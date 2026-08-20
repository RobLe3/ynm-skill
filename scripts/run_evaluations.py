#!/usr/bin/env python3
"""Run isolated YNM trigger and A/B evaluations through the Codex CLI."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS = ("gpt-5.6-sol", "gpt-5.4-mini-2026-03-17")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def client_version() -> str:
    result = subprocess.run(["codex", "--version"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


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


def invoke(model: str, prompt: str, cwd: Path, *, with_skill: bool) -> dict:
    started_at = utc_now()
    started = time.monotonic()
    holder = isolated_home(with_skill=with_skill)
    env = os.environ.copy()
    env["CODEX_HOME"] = holder.name
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--skip-git-repo-check",
        "--sandbox", "read-only", "--model", model, "--config", 'model_reasoning_effort="medium"', "--json", prompt,
    ]
    try:
        result = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
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
    usage = next((event.get("usage", {}) for event in reversed(events) if event.get("type") == "turn.completed"), {})
    error = next((event.get("message", "") for event in events if event.get("type") == "error"), "")
    skill_event = any("skill" in str(event.get("type", "")).lower() for event in events)
    return {
        "returncode": result.returncode,
        "started_at": started_at,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "raw_output": messages[-1] if messages else "",
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
    return 0 if all(item["status"] == "AVAILABLE" for item in records) else 2


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
        "activation_evidence": result["activation_evidence"] if condition == "YNM" else "NOT_APPLICABLE",
        "raw_output": result["raw_output"],
    }
    if result["error"] or result["stderr"]:
        record["error"] = result["error"] or result["stderr"].strip()
    target = output_root / "records" / f"{run_id}.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")


def run_trigger_suite(models: list[str], repetitions: int, output_root: Path) -> None:
    cases = yaml.safe_load((ROOT / "tests/data/trigger-cases.yaml").read_text(encoding="utf-8"))["cases"]
    with tempfile.TemporaryDirectory(prefix="ynm-trigger-project-") as tmp:
        cwd = Path(tmp)
        for model in models:
            for case in cases:
                for repetition in range(1, repetitions + 1):
                    result = invoke(model, case["prompt"], cwd, with_skill=True)
                    write_result(output_root, case["id"], "YNM", repetition, model, result)


def run_benchmark(models: list[str], output_root: Path) -> None:
    scenarios = yaml.safe_load((ROOT / "evaluations/scenarios.yaml").read_text(encoding="utf-8"))["scenarios"]
    for model in models:
        for scenario in scenarios:
            fixture = ROOT / scenario["fixture"]
            for condition, with_skill in (("CONTROL", False), ("YNM", True)):
                with tempfile.TemporaryDirectory(prefix="ynm-benchmark-project-") as tmp:
                    isolated_fixture = Path(tmp) / "project"
                    shutil.copytree(fixture, isolated_fixture)
                    result = invoke(model, scenario["prompt"], isolated_fixture, with_skill=with_skill)
                    write_result(output_root, scenario["id"], condition, 1, model, result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--run-triggers", action="store_true")
    parser.add_argument("--run-benchmark", action="store_true")
    parser.add_argument("--model", action="append", dest="models")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evaluations/results")
    args = parser.parse_args()
    models = args.models or list(DEFAULT_MODELS)
    if args.repetitions < 1:
        parser.error("--repetitions must be >= 1")
    if args.probe:
        return probe(models, args.output_dir / "model-availability.yaml")
    availability_status = probe(models, args.output_dir / "model-availability.yaml")
    if availability_status != 0:
        print("Evaluation not executed: one or more precommitted models are unavailable.", file=sys.stderr)
        return availability_status
    if args.run_triggers:
        run_trigger_suite(models, args.repetitions, args.output_dir)
    if args.run_benchmark:
        run_benchmark(models, args.output_dir)
    if not args.run_triggers and not args.run_benchmark:
        parser.error("select --probe, --run-triggers, or --run-benchmark")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
