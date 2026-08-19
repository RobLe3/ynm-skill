#!/usr/bin/env python3
"""Validate YNM schemas, fixtures, state, links, and canonical semantics."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


class ValidationError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text())


def resolve_ref(ref: str) -> dict[str, Any]:
    filename, _, fragment = ref.partition("#")
    node: Any = load_json(SCHEMAS / filename)
    if fragment:
        for part in fragment.removeprefix("/").split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def matches_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }[expected]


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    if "$ref" in schema:
        return validate(instance, resolve_ref(schema["$ref"]), path)
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        types = [expected] if isinstance(expected, str) else expected
        if not any(matches_type(instance, item) for item in types):
            return [f"{path}: expected {types}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if isinstance(instance, str) and len(instance) < schema.get("minLength", 0):
        errors.append(f"{path}: string is too short")
    if isinstance(instance, int) and instance < schema.get("minimum", instance):
        errors.append(f"{path}: value is below minimum")
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: array has too few items")
        if "items" in schema:
            for index, value in enumerate(instance):
                errors.extend(validate(value, schema["items"], f"{path}[{index}]"))
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required field {key!r}")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate(instance[key], subschema, f"{path}.{key}"))
        for clause in schema.get("allOf", []):
            condition_errors = validate(instance, clause.get("if", {}), path)
            branch = clause.get("then") if not condition_errors else clause.get("else")
            if branch:
                errors.extend(validate(instance, branch, path))
    return errors


def check_fixture(path: str, schema: str, unwrap: str | None = None) -> list[str]:
    instance = load_yaml(ROOT / path)
    if unwrap:
        instance = instance[unwrap]
    return [f"{path}: {error}" for error in validate(instance, load_json(SCHEMAS / schema))]


def check_links() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            if not (path.parent / target.split("#", 1)[0]).exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link {target}")
    return errors


def check_normative_invariants() -> list[str]:
    errors: list[str] = []
    disposition = (ROOT / "contracts/disposition.md").read_text()
    for line in ["`YES` | `SUPPORTED`", "`NO` | `CONTRADICTED`", "`MAYBE` | `UNRESOLVED`"]:
        if line not in disposition:
            errors.append(f"disposition contract missing canonical mapping {line}")
    core = (ROOT / "methodology/core.md").read_text()
    for phrase in ["Status is not disposition", "Capability grants no authority"]:
        corpus = "\n".join(p.read_text() for p in (ROOT / "methodology").glob("*.md"))
        if phrase.lower() not in corpus.lower():
            errors.append(f"methodology missing invariant: {phrase}")
    meta = (ROOT / "loops/meta.md").read_text()
    if "terminal_outcome = null" not in meta or "emit_terminal_run_receipt" not in meta:
        errors.append("Meta Loop lacks explicit initialized terminal control and receipt emission")
    required_boundaries = ["Owns", "Observes", "May recommend", "May not decide", "Must hand off"]
    for path in (ROOT / "loops").glob("*.md"):
        for label in required_boundaries:
            if label.lower() not in path.read_text().lower():
                errors.append(f"{path.relative_to(ROOT)}: missing responsibility boundary {label}")
    public = [ROOT / "SKILL.md", ROOT / "README.md", *(ROOT / "contracts").glob("*.md"), *(ROOT / "loops").glob("*.md"), *(ROOT / "methodology").glob("*.md")]
    for path in public:
        if re.search(r"\b(ARCS|CORC|WARDEN|FORGE Meta Loop)\b", path.read_text(), re.I):
            errors.append(f"{path.relative_to(ROOT)}: unexplained Forge terminology in operational material")
    return errors


def check_state() -> list[str]:
    errors: list[str] = []
    findings = load_yaml(ROOT / "state/findings.yaml")["findings"]
    events = load_yaml(ROOT / "state/events.yaml")["events"]
    finding_ids = {item["id"] for item in findings}
    event_ids = {item["event_id"] for item in events}
    if len(finding_ids) != len(findings):
        errors.append("state/findings.yaml: duplicate finding ID")
    if len(event_ids) != len(events):
        errors.append("state/events.yaml: duplicate event ID")
    schema = load_json(SCHEMAS / "finding.schema.json")
    for item in findings:
        errors.extend(f"state/findings.yaml:{item.get('id')}: {e}" for e in validate(item, schema))
        for event in item.get("history", []):
            if event not in event_ids:
                errors.append(f"{item['id']}: unknown history event {event}")
    receipt_schema = load_json(SCHEMAS / "run-receipt.schema.json")
    runs = load_yaml(ROOT / "state/runs.yaml")["runs"]
    run_ids: set[str] = set()
    for item in runs:
        if item.get("run_id") in run_ids:
            errors.append(f"state/runs.yaml: duplicate run ID {item.get('run_id')}")
        run_ids.add(item.get("run_id"))
        errors.extend(f"state/runs.yaml:{item.get('run_id')}: {e}" for e in validate(item, receipt_schema))
    release_runs = load_yaml(ROOT / "state/releases/1.1.0/runs.yaml")["runs"]
    for item in release_runs:
        errors.extend(f"state/releases/1.1.0/runs.yaml:{item.get('run_id')}: {e}" for e in validate(item, receipt_schema))
    loop_schema = load_json(SCHEMAS / "loop-result.schema.json")
    release_loops = load_yaml(ROOT / "state/releases/1.1.0/loop-results.yaml")["loop_results"]
    if {item.get("loop") for item in release_loops} != {"Architecture", "Implementation", "Adoption", "Maintenance", "Disposition", "Meta"}:
        errors.append("state/releases/1.1.0/loop-results.yaml: expected all six focal results")
    for item in release_loops:
        errors.extend(f"state/releases/1.1.0/loop-results.yaml:{item.get('loop')}: {e}" for e in validate(item, loop_schema))
    current_runs = load_yaml(ROOT / "state/releases/1.2.0/runs.yaml")["runs"]
    for item in current_runs:
        errors.extend(f"state/releases/1.2.0/runs.yaml:{item.get('run_id')}: {e}" for e in validate(item, receipt_schema))
        if "DELIVERY" not in item.get("phase_history", []):
            errors.append(f"state/releases/1.2.0/runs.yaml:{item.get('run_id')}: Delivery missing from phase history")
    current_loops = load_yaml(ROOT / "state/releases/1.2.0/loop-results.yaml")["loop_results"]
    if {item.get("loop") for item in current_loops} != {"Architecture", "Implementation", "Adoption", "Maintenance", "Disposition", "Meta"}:
        errors.append("state/releases/1.2.0/loop-results.yaml: expected all six focal results")
    for item in current_loops:
        errors.extend(f"state/releases/1.2.0/loop-results.yaml:{item.get('loop')}: {e}" for e in validate(item, loop_schema))
    plan = load_yaml(ROOT / "state/releases/1.2.0/review-plan.yaml")["review_plan"]
    errors.extend(f"state/releases/1.2.0/review-plan.yaml: {e}" for e in validate(plan, load_json(SCHEMAS / "review-plan.schema.json")))
    return errors


def check_yaml_disposition_quoting() -> list[str]:
    errors: list[str] = []
    pattern = re.compile(r"^\s*(?:proposed_disposition|disposition):\s*(YES|NO|MAYBE)\s*$", re.M)
    for path in [*ROOT.rglob("*.yaml"), *ROOT.rglob("*.md")]:
        for match in pattern.finditer(path.read_text()):
            errors.append(f"{path.relative_to(ROOT)}: YAML disposition {match.group(1)} must be quoted")
    return errors


def check_release() -> list[str]:
    errors: list[str] = []
    version = (ROOT / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"VERSION: expected semantic version, found {version!r}")
    findings = load_yaml(ROOT / "state/findings.yaml")["findings"]
    blockers = [item["id"] for item in findings if item.get("maturity_impact") == "MATURITY_BLOCKING" and item.get("status") != "RESOLVED"]
    if version.startswith("1.") and blockers:
        errors.append(f"VERSION: production version with unresolved blockers {blockers}")
    gates = load_yaml(ROOT / "state/maturity-gates.yaml")["maturity_gates"]["gates"]
    if len(gates) != 15 or [gate.get("id") for gate in gates] != list(range(1, 16)):
        errors.append("state/maturity-gates.yaml: expected gates 1 through 15")
    for gate in gates:
        if not isinstance(gate.get("disposition"), str) or gate.get("disposition") not in {"YES", "NO", "MAYBE"}:
            errors.append(f"maturity gate {gate.get('id')}: invalid disposition")
    if not (ROOT / "YNM_MATURITY_REPORT.md").exists():
        errors.append("missing YNM_MATURITY_REPORT.md")
    manifest = load_yaml(ROOT / "manifest.yaml")
    if manifest.get("version") != version:
        errors.append("manifest.yaml: version does not match VERSION")
    if version not in (ROOT / "README.md").read_text():
        errors.append("README.md: current version is not stated")
    if f"## [{version}]" not in (ROOT / "CHANGELOG.md").read_text():
        errors.append("CHANGELOG.md: current version entry is missing")
    for group in ["components", "optional_adapters", "packaging", "provenance", "validation"]:
        value = manifest.get(group, {})
        paths = value.values() if isinstance(value, dict) else [value]
        for collection in paths:
            collection = collection if isinstance(collection, list) else [collection]
            for item in collection:
                if not (ROOT / item).exists():
                    errors.append(f"manifest.yaml: missing path {item}")
    labels = {"VALIDATED", "SUPPORTED_BY_DESIGN", "PARTIALLY_VALIDATED", "NOT_VALIDATED", "KNOWN_LIMITATION"}
    for name, label in manifest.get("compatibility", {}).items():
        if label not in labels:
            errors.append(f"manifest.yaml: invalid capability label for {name}: {label}")
    return errors


def check_baseline_integrity() -> list[str]:
    errors: list[str] = []
    baseline = load_yaml(ROOT / "state/releases/1.1.0/baseline-hashes.yaml")
    entries = {**baseline["files"], **baseline["report"]}
    for name, expected in entries.items():
        path = ROOT / name
        if not path.exists():
            errors.append(f"1.0.0 baseline artifact missing: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"1.0.0 baseline artifact changed: {name}")
    release_baseline = load_yaml(ROOT / "state/releases/1.2.0/baseline-hashes.yaml")
    for name, expected in release_baseline["files"].items():
        path = ROOT / name
        if not path.exists():
            errors.append(f"1.1.0 baseline artifact missing: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"1.1.0 baseline artifact changed: {name}")
    return errors


def check_public_sanitization() -> list[str]:
    errors: list[str] = []
    runtime = [ROOT / "SKILL.md", *(ROOT / "contracts").glob("*.md"), *(ROOT / "loops").glob("*.md"), *(ROOT / "methodology").glob("*.md"), *(ROOT / "schemas").glob("*.json"), *(ROOT / "examples").glob("*.md"), *(ROOT / "scripts").glob("*.py")]
    absolute = re.compile(r"/(?:Users|home)/[^\s`'\"]+")
    secret = re.compile(r"(?i)(?:api[_-]?key|token|password)\s*[:=]\s*['\"][^'\"]+['\"]")
    for path in runtime:
        text = path.read_text()
        if absolute.search(text):
            errors.append(f"{path.relative_to(ROOT)}: private absolute path in public runtime surface")
        if secret.search(text):
            errors.append(f"{path.relative_to(ROOT)}: possible secret in public runtime surface")
        if path.name != "publication-readiness.md" and re.search(r"\bBlender\b|\bClaude Code\b", text):
            errors.append(f"{path.relative_to(ROOT)}: project/provider-specific assumption in runtime surface")
    readme = (ROOT / "README.md").read_text()
    if re.search(r"/Users/|iicp\.network|roble/development", readme, re.I):
        errors.append("README.md: private or real-project identifier in public onboarding")
    return errors


def check_runtime_boundary() -> list[str]:
    """Ensure normative Markdown does not depend on provenance or validation artifacts."""
    errors: list[str] = []
    normative = [ROOT / "SKILL.md", *(ROOT / "contracts").glob("*.md"), *(ROOT / "loops").glob("*.md"), *(ROOT / "methodology").glob("*.md")]
    forbidden = {"FORGE_EXTRACTION.md", "GENERALIZATION.md", "PUBLICATION_COMPARISON.md", "YNM_MATURITY_REPORT.md", "YNM_1_1_MATURITY_REPORT.md", "state", "tests", "validation"}
    for path in normative:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            relative = resolved.relative_to(ROOT).parts
            if relative and relative[0] in forbidden:
                errors.append(f"{path.relative_to(ROOT)}: runtime depends on non-runtime artifact {target}")
    return errors


def check_schema_references() -> list[str]:
    errors: list[str] = []
    for path in SCHEMAS.glob("*.json"):
        text = path.read_text()
        for ref in re.findall(r'"\$ref"\s*:\s*"([^"]+)"', text):
            try:
                resolve_ref(ref)
            except Exception as exc:
                errors.append(f"{path.relative_to(ROOT)}: unresolved reference {ref}: {exc}")
    return errors


def run() -> list[str]:
    errors: list[str] = []
    for path in SCHEMAS.glob("*.json"):
        try:
            load_json(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
    fixtures = [
        ("examples/data/evidence.yaml", "evidence.schema.json", None),
        ("examples/data/assessment.yaml", "assessment.schema.json", None),
        ("examples/data/finding.yaml", "finding.schema.json", None),
        ("examples/data/loop-result.yaml", "loop-result.schema.json", None),
        ("examples/data/run-receipt.yaml", "run-receipt.schema.json", None),
        ("examples/data/execution-context.yaml", "execution-context.schema.json", None),
        ("examples/data/security-extension.yaml", "extension.schema.json", None),
        ("examples/data/project-context.yaml", "project-context.schema.json", None),
        ("examples/data/project-config.yaml", "project-config.schema.json", None),
        ("examples/data/bootstrap-receipt.yaml", "bootstrap-receipt.schema.json", None),
        ("examples/data/review-plan.yaml", "review-plan.schema.json", None),
        ("state/maturity-assessment.yaml", "assessment.schema.json", "assessment"),
    ]
    for fixture in fixtures:
        errors.extend(check_fixture(*fixture))
    errors.extend(check_links())
    errors.extend(check_normative_invariants())
    errors.extend(check_state())
    errors.extend(check_yaml_disposition_quoting())
    errors.extend(check_schema_references())
    errors.extend(check_release())
    errors.extend(check_baseline_integrity())
    errors.extend(check_public_sanitization())
    errors.extend(check_runtime_boundary())
    scenarios = [line for line in (ROOT / "methodology/adversarial-validation.md").read_text().splitlines() if line.startswith("| ")][1:]
    if len(scenarios) != 78:
        errors.append(f"adversarial scenario count: expected 78, found {len(scenarios)}")
    return errors


def main() -> int:
    errors = run()
    if errors:
        print("YNM validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("YNM validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
