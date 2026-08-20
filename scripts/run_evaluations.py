#!/usr/bin/env python3
"""Run isolated YNM trigger and A/B evaluations through the Codex CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_MODEL = "gpt-5.6-sol"
REPLICATION_CANDIDATES = (
    "gpt-5.4-mini-2026-03-17",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
    "gpt-5.4",
)
DEFAULT_MODELS = (PRIMARY_MODEL, *REPLICATION_CANDIDATES)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def client_version() -> str:
    result = subprocess.run(["codex", "--version"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def filesystem_inventory(root: Path) -> dict[str, str]:
    inventory: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            inventory[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return inventory


def isolated_home(*, with_skill: bool) -> tempfile.TemporaryDirectory[str]:
    holder = tempfile.TemporaryDirectory(prefix="ynm-eval-home-")
    home = Path(holder.name)
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    if not auth.exists():
        holder.cleanup()
        raise RuntimeError("Codex authentication is unavailable")
    (home / "auth.json").symlink_to(auth)
    if with_skill:
        package_root = home / "skills"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_skill_package.py"), "--output-dir", str(package_root), "--overwrite"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    return holder


def invoke(model: str, prompt: str, cwd: Path, *, with_skill: bool, timeout_seconds: int = 300, output_schema: Path | None = None) -> dict:
    started_at = utc_now()
    started = time.monotonic()
    holder = isolated_home(with_skill=with_skill)
    env = os.environ.copy()
    env["CODEX_HOME"] = holder.name
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--skip-git-repo-check",
        "--sandbox", "read-only", "--model", model, "--config", 'model_reasoning_effort="medium"', "--json", prompt,
    ]
    if output_schema is not None:
        command[2:2] = ["--output-schema", str(output_schema)]
    before_inventory = filesystem_inventory(cwd)
    try:
        try:
            result = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(command, 124, stdout=exc.stdout or "", stderr=f"invocation timed out after {timeout_seconds} seconds")
    finally:
        holder.cleanup()
    events = []
    for line in result.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    messages = [
        event["item"]["text"]
        for event in events
        if event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") == "agent_message"
    ]
    normalized_messages = []
    path_forms = {str(cwd), str(cwd.resolve())}
    for message in messages:
        for path_form in sorted(path_forms, key=len, reverse=True):
            message = message.replace(path_form, "<EVALUATION_PROJECT>")
        normalized_messages.append(message)
    usage = next((event.get("usage", {}) for event in reversed(events) if event.get("type") == "turn.completed"), {})
    error = next((event.get("message", "") for event in events if event.get("type") == "error"), "")
    skill_event = any("skill" in str(event.get("type", "")).lower() for event in events)
    tool_calls = sum(
        1 for event in events
        if isinstance(event.get("item"), dict)
        and event["item"].get("type") in {"command_execution", "mcp_tool_call", "tool_call"}
    )
    after_inventory = filesystem_inventory(cwd)
    return {
        "returncode": result.returncode,
        "started_at": started_at,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "tool_calls": tool_calls,
        "filesystem_changed": before_inventory != after_inventory,
        "raw_output": normalized_messages[-1] if normalized_messages else "",
        "raw_events": result.stdout,
        "stderr": result.stderr,
        "error": error,
        "activation_evidence": "RUNTIME_EVENT" if skill_event else "NOT_OBSERVED",
    }


def probe(models: list[str], output: Path) -> int:
    records = []
    for model in models:
        result = invoke(model, "Reply with exactly MODEL_AVAILABLE.", ROOT, with_skill=False)
        available = result["returncode"] == 0 and result["raw_output"].strip() == "MODEL_AVAILABLE"
        records.append({
            "provider": "OpenAI",
            "model": model,
            "role": "evaluated_executor",
            "status": "AVAILABLE" if available else "UNAVAILABLE",
            "checked_at": result["started_at"],
            "client": client_version(),
            "error": "" if available else (result["error"] or result["stderr"].strip()),
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump({"models": records}, sort_keys=False), encoding="utf-8")
    primary = next((item for item in records if item["model"] == models[0]), None)
    return 0 if primary and primary["status"] == "AVAILABLE" else 2


def selected_models(availability_path: Path) -> list[str]:
    records = yaml.safe_load(availability_path.read_text(encoding="utf-8"))["models"]
    by_model = {item["model"]: item["status"] for item in records}
    if by_model.get(PRIMARY_MODEL) != "AVAILABLE":
        return []
    selected = [PRIMARY_MODEL]
    replication = next((model for model in REPLICATION_CANDIDATES if by_model.get(model) == "AVAILABLE"), None)
    if replication:
        selected.append(replication)
    return selected


def behavioral_activation(output: str) -> bool | None:
    normalized = output.lower()
    if "used ynm" in normalized or "using ynm" in normalized or "ynm review" in normalized:
        return True
    has_dispositions = all(token in output.upper() for token in ("YES", "NO", "MAYBE"))
    has_scope = "reviewed scope" in normalized and "unreviewed scope" in normalized
    has_delivery = "delivery" in normalized
    if has_dispositions and has_scope and has_delivery:
        return True
    return None


def smoke_observability(model: str, output: Path) -> str:
    prompt = "Perform a brief read-only YNM review of the empty working directory and clearly identify the method used."
    with tempfile.TemporaryDirectory(prefix="ynm-observability-") as tmp:
        result = invoke(model, prompt, Path(tmp), with_skill=True)
    if result["activation_evidence"] == "RUNTIME_EVENT":
        mode = "RUNTIME_EVENT"
    elif behavioral_activation(result["raw_output"]):
        mode = "BEHAVIORAL_INFERENCE"
    else:
        mode = "NOT_OBSERVED"
    payload = {
        "schema_version": "ynm-activation-observability.v1",
        "model": model,
        "checked_at": result["started_at"],
        "mode": mode,
        "inference_rule": "Explicit YNM-use statement, or YES/NO/MAYBE plus reviewed/unreviewed scope plus Delivery.",
        "raw_output": result["raw_output"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return mode


def write_result(output_root: Path, scenario_id: str, condition: str, repetition: int, model: str, result: dict) -> None:
    run_id = f"{scenario_id}-{condition}-{model}-{repetition}".replace("/", "-")
    raw_dir = output_root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{run_id}.jsonl").write_text(result.pop("raw_events"), encoding="utf-8")
    record = {
        "schema_version": "ynm-evaluation-result.v1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "condition": condition,
        "repetition": repetition,
        "status": "EXECUTED" if result["returncode"] == 0 else "FAILED",
        "provider": "OpenAI",
        "model": model,
        "client": client_version(),
        "started_at": result["started_at"],
        "elapsed_seconds": result["elapsed_seconds"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "tool_calls": result["tool_calls"],
        "filesystem_changed": result["filesystem_changed"],
        "activation_evidence": result["activation_evidence"] if condition == "YNM" else "NOT_APPLICABLE",
        "raw_output": result["raw_output"],
    }
    if result["error"] or result["stderr"]:
        record["error"] = result["error"] or result["stderr"].strip()
    target = output_root / "records" / f"{run_id}.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")


def run_trigger_suite(models: list[str], repetitions: int, output_root: Path, observability_mode: str, workers: int = 6) -> None:
    cases = yaml.safe_load((ROOT / "tests/data/trigger-cases.yaml").read_text(encoding="utf-8"))["cases"]
    with tempfile.TemporaryDirectory(prefix="ynm-trigger-project-") as tmp:
        cwd = Path(tmp)
        jobs = [(model, case, repetition) for model in models for case in cases for repetition in range(1, repetitions + 1)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(invoke, model, case["prompt"], cwd, with_skill=True): (model, case, repetition) for model, case, repetition in jobs}
            for future in as_completed(futures):
                model, case, repetition = futures[future]
                result = future.result()
                if result["activation_evidence"] != "RUNTIME_EVENT":
                    inferred = behavioral_activation(result["raw_output"])
                    result["activation_evidence"] = "BEHAVIORAL_INFERENCE" if observability_mode == "BEHAVIORAL_INFERENCE" and inferred else "NOT_OBSERVED"
                write_result(output_root, case["id"], "YNM", repetition, model, result)


def run_benchmark(
    models: list[str], output_root: Path, workers: int = 6, *,
    scenarios_path: Path | None = None, treatment_label: str = "YNM",
) -> None:
    scenario_source = scenarios_path or (ROOT / "evaluations/scenarios.yaml")
    scenarios = yaml.safe_load(scenario_source.read_text(encoding="utf-8"))["scenarios"]
    jobs = [(model, scenario, condition, with_skill) for model in models for scenario in scenarios for condition, with_skill in (("CONTROL", False), (treatment_label, True))]
    def execute(job: tuple) -> tuple:
        model, scenario, condition, with_skill = job
        fixture = ROOT / scenario["fixture"]
        with tempfile.TemporaryDirectory(prefix="ynm-benchmark-project-") as tmp:
            isolated_fixture = Path(tmp) / "project"
            shutil.copytree(fixture, isolated_fixture)
            result = invoke(model, scenario["prompt"], isolated_fixture, with_skill=with_skill)
            return model, scenario, condition, result
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(execute, job) for job in jobs]
        for future in as_completed(futures):
            model, scenario, condition, result = future.result()
            write_result(output_root, scenario["id"], condition, 1, model, result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--run-triggers", action="store_true")
    parser.add_argument("--run-benchmark", action="store_true")
    parser.add_argument("--smoke-observability", action="store_true")
    parser.add_argument("--model", action="append", dest="models")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evaluations/results")
    parser.add_argument("--scenarios", type=Path, default=ROOT / "evaluations/scenarios.yaml")
    parser.add_argument("--treatment-label", default="YNM")
    args = parser.parse_args()
    models = args.models or list(DEFAULT_MODELS)
    if args.repetitions < 1:
        parser.error("--repetitions must be >= 1")
    if args.probe:
        return probe(models, args.output_dir / "model-availability.yaml")
    availability_path = args.output_dir / "model-availability.yaml"
    availability_status = probe(models, availability_path)
    if availability_status != 0:
        print("Evaluation not executed: the frozen primary model is unavailable.", file=sys.stderr)
        return availability_status
    models = selected_models(availability_path)
    observability_mode = smoke_observability(models[0], args.output_dir / "activation-observability.yaml")
    if args.smoke_observability and not args.run_triggers and not args.run_benchmark:
        return 0
    if args.run_triggers:
        run_trigger_suite(models, args.repetitions, args.output_dir, observability_mode, args.workers)
    if args.run_benchmark:
        run_benchmark(
            models, args.output_dir, args.workers,
            scenarios_path=args.scenarios, treatment_label=args.treatment_label,
        )
    if not args.run_triggers and not args.run_benchmark and not args.smoke_observability:
        parser.error("select --probe, --smoke-observability, --run-triggers, or --run-benchmark")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
