#!/usr/bin/env python3
"""Validate YNM schemas, fixtures, and repository invariants with Draft 2020-12 JSON Schema."""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
import jsonschema
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema import exceptions as jsonschema_exceptions
from referencing import Registry
from referencing.jsonschema import Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


class ValidationError(Exception):
    """Raised for unrecoverable validation setup problems."""


@dataclass(frozen=True)
class SchemaSource:
    schema_id: str
    path: Path
    data: dict[str, Any]


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    return load_yaml(path)


def _schema_files() -> list[Path]:
    return sorted(SCHEMAS.glob("*.json"))


def _build_schema_index() -> tuple[dict[str, SchemaSource], dict[str, SchemaSource], list[str]]:
    by_id: dict[str, SchemaSource] = {}
    by_path: dict[str, SchemaSource] = {}
    errors: list[str] = []

    for path in _schema_files():
        raw = path.read_bytes()
        try:
            data = load_json(path)
        except Exception as exc:
            raise ValidationError(f"{path}: invalid YAML/JSON parse ({exc})")

        schema_id = data.get("$id")
        if not isinstance(schema_id, str) or not schema_id.strip():
            raise ValidationError(f"{path}: schema missing or invalid $id")
        schema = SchemaSource(schema_id=schema_id, path=path, data=data)

        if schema_id in by_id:
            errors.append(f"duplicate schema id {schema_id} in {path.name} and {by_id[schema_id].path.name}")
        by_id[schema_id] = schema

        by_name = path.name
        if by_name in by_path:
            errors.append(f"duplicate schema filename {by_name}: {path} and {by_path[by_name].path}")
        by_path[by_name] = schema

    if errors:
        raise ValidationError("\n".join(errors))
    return by_id, by_path, []


def _build_registry() -> Registry:
    by_id, by_path, _ = _build_schema_index()
    reg = Registry().with_resources(
        [
            (schema.schema_id, Resource.from_contents(schema.data))
            for schema in by_id.values()
        ]
    )
    # Support filename refs as fallback aliases.
    for schema in by_path.values():
        reg = reg.with_resource(schema.path.name, Resource.from_contents(schema.data))
    return reg


def _iter_schema_refs(schema: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "$ref" and isinstance(value, str):
                refs.append(value)
            refs.extend(_iter_schema_refs(value))
    elif isinstance(schema, list):
        for item in schema:
            refs.extend(_iter_schema_refs(item))
    return refs


def _registry() -> Registry:
    # Cached lazily for tests.
    global _REGISTRY
    if "_REGISTRY" not in globals():
        _REGISTRY = _build_registry()
    return _REGISTRY


def _schema_index() -> tuple[dict[str, SchemaSource], dict[str, SchemaSource]]:
    global _SCHEMA_INDEX
    if "_SCHEMA_INDEX" not in globals():
        by_id, by_path, _errs = _build_schema_index()
        _SCHEMA_INDEX = (by_id, by_path)
        if _errs:
            raise ValidationError("\n".join(_errs))
    return _SCHEMA_INDEX


def _resolve_ref(ref: str) -> dict[str, Any]:
    by_id, by_path = _schema_index()

    if not isinstance(ref, str):
        raise KeyError("reference must be a string")

    ref = ref.strip()
    if not ref:
        raise KeyError("empty reference")

    schema_file, frag_sep, frag = ref.partition("#")

    # Internal-only reference.
    if not schema_file:
        return {"$schema": "https://json-schema.org/draft/2020-12/schema"}

    if "://" in schema_file and not schema_file.startswith("urn:ynm:schemas:"):
        raise KeyError(f"external reference not permitted: {ref}")

    # Explicitly permitted URN namespace.
    if schema_file.startswith("urn:ynm:schemas:"):
        if schema_file not in by_id:
            raise KeyError(f"unknown urn reference: {schema_file}")
        base = by_id[schema_file].data
    else:
        # Reject absolute file paths.
        if schema_file.startswith(("/", "\\")):
            raise KeyError(f"absolute path reference not permitted: {ref}")
        if re.match(r"^[A-Za-z]:[\\/]", schema_file):
            raise KeyError(f"windows absolute reference not permitted: {ref}")
        if schema_file.startswith("\\\\") or schema_file.startswith("//"):
            raise KeyError(f"UNC reference not permitted: {ref}")

        normalized = schema_file.lstrip("./")
        # Candidate by canonical filename alias (schema definitions use filename refs).
        if normalized in by_path:
            base = by_path[normalized].data
        else:
            candidate = SCHEMAS / normalized
            if candidate.exists() and candidate.is_file():
                data = load_json(candidate)
                if not data:
                    raise KeyError(f"empty schema reference target: {candidate}")
                base = data
            else:
                raise KeyError(f"unresolved reference: {ref}")

    if not frag_sep:
        return base
    if not frag:
        return base
    if not frag.startswith("/"):
        raise KeyError(f"unsupported reference fragment: {ref}")

    target: Any = base
    for segment in frag.lstrip("/").split("/"):
        segment = segment.replace("~1", "/").replace("~0", "~")
        if not isinstance(target, dict):
            raise KeyError(f"invalid reference fragment for {ref}")
        if segment not in target:
            raise KeyError(f"missing fragment path {segment} in {ref}")
        target = target[segment]
    return target


# Public compatibility wrapper retained for existing tests and external callers.
def resolve_ref(ref: str) -> dict[str, Any]:
    return _resolve_ref(ref)


def _validator(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema, registry=_registry(), format_checker=FormatChecker())


def check_schema_files() -> list[str]:
    errors: list[str] = []
    try:
        _schema_index()
    except ValidationError as exc:
        return [str(exc)]

    for path in _schema_files():
        schema = load_json(path)
        try:
            Draft202012Validator.check_schema(schema)
        except jsonschema_exceptions.SchemaError as exc:
            errors.append(f"{path.relative_to(ROOT)}: schema error: {exc.message}")

        for ref in _iter_schema_refs(schema):
            try:
                _resolve_ref(ref)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{path.relative_to(ROOT)}: unresolved reference {ref}: {exc}")
    return errors


def check_schema_references() -> list[str]:
    return check_schema_files()


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    validator = _validator(schema)
    try:
        errors = sorted(
            validator.iter_errors(instance),
            key=lambda error: (list(error.absolute_path), list(error.absolute_schema_path)),
        )
    except jsonschema_exceptions.RefResolutionError as exc:
        return [f"{path}: schema reference resolution failed: {exc}"]

    out: list[str] = []
    for error in errors:
        location = "$" + "".join(f"[{repr(p)}]" for p in error.absolute_path)
        schema_location = "#" + "/".join(str(p) for p in error.absolute_schema_path)
        out.append(f"{path}{location} [schema {schema_location}] {error.message}")
    return out


def check_fixture(path: str, schema: str, unwrap: str | None = None) -> list[str]:
    instance = load_yaml(ROOT / path)
    if unwrap:
        instance = instance[unwrap]
    errors = validate(instance, load_json(SCHEMAS / schema), str(path))
    return [f"{path}: {error}" for error in errors]


def check_links() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            # Relative path or fragment-only local anchor.
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            if target_path.startswith("."):
                normalized = (path.parent / target_path).resolve()
            else:
                normalized = (path.parent / target_path).resolve()
            if not normalized.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link {target}")
    return errors


def check_normative_invariants() -> list[str]:
    errors: list[str] = []
    disposition = (ROOT / "contracts/disposition.md").read_text(encoding="utf-8")
    for line in ["`YES`", "`NO`", "`MAYBE`"]:
        if line not in disposition:
            errors.append(f"disposition contract missing disposition token {line}")

    for loop in (ROOT / "loops").glob("*.md"):
        content = loop.read_text(encoding="utf-8")
        for section in ["Owns", "Observes", "May recommend", "May not decide", "Must hand off"]:
            if section.lower() not in content.lower():
                errors.append(f"{loop.relative_to(ROOT)}: missing boundary field {section}")

    methodology_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in (ROOT / "methodology").glob("*.md")
    )
    for phrase in ["status is not disposition", "capability grants no authority"]:
        if phrase not in methodology_text.lower():
            errors.append(f"methodology missing invariant: {phrase}")

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

    finding_schema = load_json(SCHEMAS / "finding.schema.json")
    for item in findings:
        errors.extend(f"state/findings.yaml:{item.get('id')}: {e}" for e in validate(item, finding_schema))
        for event in item.get("history", []):
            if event not in event_ids:
                errors.append(f"{item['id']}: unknown history event {event}")

    run_schema = load_json(SCHEMAS / "run-receipt.schema.json")
    run_states = [ROOT / "state/runs.yaml", ROOT / "state/releases/1.1.0/runs.yaml", ROOT / "state/releases/1.2.0/runs.yaml", ROOT / f"state/releases/{CURRENT_VERSION}/runs.yaml"]
    for state_path in run_states:
        runs = load_yaml(state_path)["runs"]
        seen: set[str] = set()
        for item in runs:
            if item.get("run_id") in seen:
                errors.append(f"{state_path.relative_to(ROOT)}: duplicate run ID {item.get('run_id')}")
            seen.add(item.get("run_id"))
            errors.extend(f"{state_path.relative_to(ROOT)}:{item.get('run_id')}: {e}" for e in validate(item, run_schema))

    current_runs = load_yaml(ROOT / f"state/releases/{CURRENT_VERSION}/runs.yaml")["runs"] if (ROOT / f"state/releases/{CURRENT_VERSION}/runs.yaml").exists() else []
    for item in current_runs:
        if "DELIVERY" not in item.get("phase_history", []):
            errors.append(f"state/releases/{CURRENT_VERSION}/runs.yaml: Delivery missing from phase history")

    for loop_path, expected_loops in [
        (ROOT / "state/releases/1.1.0/loop-results.yaml", {"Architecture", "Implementation", "Adoption", "Maintenance", "Disposition", "Meta"}),
        (ROOT / "state/releases/1.2.0/loop-results.yaml", {"Architecture", "Implementation", "Adoption", "Maintenance", "Disposition", "Meta"}),
        (ROOT / f"state/releases/{CURRENT_VERSION}/loop-results.yaml", {"Architecture", "Implementation", "Adoption", "Maintenance", "Disposition", "Meta"}),
    ]:
        if not loop_path.exists():
            continue
        records = load_yaml(loop_path)["loop_results"]
        if {item.get("loop") for item in records} != expected_loops:
            errors.append(f"{loop_path.relative_to(ROOT)}: expected all six focal loop records")
        loop_schema = load_json(SCHEMAS / "loop-result.schema.json")
        for item in records:
            errors.extend(f"{loop_path.relative_to(ROOT)}:{item.get('loop')}: {e}" for e in validate(item, loop_schema))

    release_plan = load_yaml(ROOT / f"state/releases/{CURRENT_VERSION}/review-plan.yaml")["review_plan"]
    errors.extend(
        f"state/releases/{CURRENT_VERSION}/review-plan.yaml: {e}" for e in validate(release_plan, load_json(SCHEMAS / "review-plan.schema.json"))
    )
    return errors


def check_yaml_disposition_quoting() -> list[str]:
    errors: list[str] = []
    pattern = re.compile(r"^\s*(?:proposed_disposition|disposition):\s*(YES|NO|MAYBE)\s*$", re.M)
    for path in [*ROOT.rglob("*.yaml"), *ROOT.rglob("*.yml")]:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in pattern.finditer(text):
            errors.append(f"{path.relative_to(ROOT)}: YAML disposition {match.group(1)} must be quoted")
    return errors



def _flatten_manifest_values(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _flatten_manifest_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _flatten_manifest_values(nested)
    elif value:
        yield str(value)


def check_release() -> list[str]:
    errors: list[str] = []
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"VERSION: expected semantic version, found {version!r}")

    findings = load_yaml(ROOT / "state/findings.yaml")["findings"]
    blockers = [item["id"] for item in findings if item.get("maturity_impact") == "MATURITY_BLOCKING" and item.get("status") != "RESOLVED"]
    if blockers:
        errors.append(f"VERSION: unresolved maturity blockers {blockers}")

    gates = load_yaml(ROOT / "state/maturity-gates.yaml")["maturity_gates"]["gates"]
    if len(gates) != 15 or [gate.get("id") for gate in gates] != list(range(1, 16)):
        errors.append("state/maturity-gates.yaml: expected gates 1 through 15")

    for gate in gates:
        if gate.get("disposition") not in {"YES", "NO", "MAYBE"}:
            errors.append(f"maturity gate {gate.get('id')}: invalid disposition")

    if not (ROOT / "YNM_MATURITY_REPORT.md").exists():
        errors.append("missing YNM_MATURITY_REPORT.md")

    manifest = load_yaml(ROOT / "manifest.yaml")
    if manifest.get("version") != version:
        errors.append("manifest.yaml: version does not match VERSION")

    if version not in (ROOT / "README.md").read_text(encoding="utf-8"):
        errors.append("README.md: current version is not stated")

    if f"## [{version}]" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        errors.append("CHANGELOG.md: current version entry is missing")

    release_dir = ROOT / f"state/releases/{version}"
    if not release_dir.exists():
        errors.append(f"state/releases/{version}: directory missing")
    else:
        for required in [
            "assessment.yaml",
            "baseline-hashes.yaml",
            "final-assessment.yaml",
            "findings.yaml",
            "gates.yaml",
            "iterations.yaml",
            "loop-results.yaml",
            "publication.yaml",
            "runs.yaml",
            "review-plan.yaml",
            "sanitization-report.yaml",
            "stability.yaml",
            "adversarial-results.yaml",
            "events.yaml",
            "execution-context.yaml",
        ]:
            if not (release_dir / required).exists():
                errors.append(f"state/releases/{version}: missing {required}")

    for group in ["components", "optional_adapters", "packaging", "provenance", "validation", "runtime"]:
        for item_path in _flatten_manifest_values(manifest.get(group, {})):
            if not (ROOT / item_path).exists():
                errors.append(f"manifest.yaml: missing path {item_path}")

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
            errors.append(f"1.1.0 baseline artifact missing: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"1.1.0 baseline artifact changed: {name}")

    release_baseline_path = ROOT / f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml"
    if release_baseline_path.exists():
        release_baseline = load_yaml(release_baseline_path)
        for name, expected in release_baseline.get("files", {}).items():
            path = ROOT / name
            if not path.exists():
                errors.append(f"{CURRENT_VERSION} baseline artifact missing: {name}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                errors.append(f"{CURRENT_VERSION} baseline artifact changed: {name}")
    return errors


def check_public_sanitization() -> list[str]:
    errors: list[str] = []
    runtime = [
        ROOT / "SKILL.md",
        *(ROOT / "contracts").glob("*.md"),
        *(ROOT / "loops").glob("*.md"),
        *(ROOT / "methodology").glob("*.md"),
        *(ROOT / "schemas").glob("*.json"),
        *(ROOT / "examples").glob("*.md"),
        *(ROOT / "scripts").glob("*.py"),
        ROOT / "README.md",
    ]
    absolute = re.compile(r"/Users/[^\s`'\"]+")
    secret = re.compile(r"(?i)(?:api[_-]?key|token|password)\s*[:=]\s*['\"][^'\"]+['\"]")
    for path in runtime:
        text = path.read_text(encoding="utf-8")
        if absolute.search(text):
            errors.append(f"{path.relative_to(ROOT)}: private absolute path in runtime surface")
        if secret.search(text):
            errors.append(f"{path.relative_to(ROOT)}: possible secret in runtime surface")
        if path != ROOT / "validation" / "validate_ynm.py" and re.search(r"\bBlender\b|\bClaude\b|iicp\.network", text, re.I):
            errors.append(f"{path.relative_to(ROOT)}: project/provider-specific assumption in runtime surface")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if re.search(r"/Users/|roble/development", readme, re.I):
        errors.append("README.md: private or personal reference in public onboarding")

    return errors


def check_runtime_boundary() -> list[str]:
    errors: list[str] = []
    normative = [ROOT / "SKILL.md", *(ROOT / "contracts").glob("*.md"), *(ROOT / "loops").glob("*.md"), *(ROOT / "methodology").glob("*.md")]
    forbidden_prefixes = {"FORGE_EXTRACTION.md", "GENERALIZATION.md", "PUBLICATION_COMPARISON.md", "YNM_1_1_MATURITY_REPORT.md", "YNM_1_2_MATURITY_REPORT.md", "state", "tests", "validation", "AGENTS.md", "manifest.yaml"}

    for path in normative:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (path.parent / target_path).resolve()
            try:
                relative = resolved.relative_to(ROOT)
            except ValueError:
                continue
            if relative.parts and relative.parts[0] in forbidden_prefixes:
                errors.append(f"{path.relative_to(ROOT)}: runtime depends on non-runtime artifact {target}")

    return errors


def check_version_consistency() -> list[str]:
    expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    manifest = load_yaml(ROOT / "manifest.yaml").get("version")
    if manifest != expected:
        return [f"manifest version mismatch: {expected} != {manifest}"]

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{expected}]" not in changelog:
        return ["changelog missing current version heading"]

    return []


def run() -> list[str]:
    errors: list[str] = []
    errors.extend(check_schema_files())
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
    errors.extend(check_release())
    errors.extend(check_version_consistency())
    errors.extend(check_baseline_integrity())
    errors.extend(check_public_sanitization())
    errors.extend(check_runtime_boundary())

    scenarios = [line for line in (ROOT / "methodology/adversarial-validation.md").read_text(encoding="utf-8").splitlines() if line.startswith("| ")]
    if len(scenarios) != 80:
        errors.append(f"adversarial scenario count: expected 80, found {len(scenarios)}")

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
    raise SystemExit(main())
