#!/usr/bin/env python3
"""Validate YNM schemas, fixtures, and repository invariants with Draft 2020-12 JSON Schema."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
import re
import subprocess
import sys
from collections.abc import Sequence
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
DEFAULT_CHECKS = [
    "schema",
    "links",
    "normative-invariants",
    "state",
    "yaml-disposition-quoting",
    "release",
    "version-consistency",
    "baseline-integrity",
    "public-sanitization",
    "runtime-boundary",
]
SECURITY_BOUNDARY_CHECKS = ["baseline-integrity", "public-sanitization", "runtime-boundary"]

AGENTS_MARKER_START = "<!-- YNM:BEGIN -->"
AGENTS_MARKER_END = "<!-- YNM:END -->"
PUBLIC_SANITIZATION_ALLOWLIST: dict[str, set[str]] = {}
PUBLIC_SANITIZATION_ALLOWLIST.update(
    {
        "PUBLICATION_COMPARISON.md": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
        "YNM_1_1_MATURITY_REPORT.md": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
        "docs/errata/1.2.0-publication.md": {"PRIVATE_REPOSITORY_REFERENCE"},
        "tests/test_validate_ynm.py": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
        "validation/validate_ynm.py": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
        "validation/validate_release_integrity.py": {"PRIVATE_ABSOLUTE_PATH"},
    }
)
TEXT_PATTERNS: dict[str, list[str]] = {
    "PRIVATE_ABSOLUTE_PATH": [
        r"(?<![A-Za-z0-9_])/[Uu]sers/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*",
        r"(?<![A-Za-z0-9_])/(?:home|private|tmp|var|opt|mnt)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+",
        r"(?<![A-Za-z0-9_])(?:[A-Za-z]:\\[Uu]sers\\[A-Za-z0-9_.-]+\\[A-Za-z0-9_.-]+(?:\\[A-Za-z0-9_.-]+)*)",
        r"(?<![A-Za-z0-9_])(\\\\[A-Za-z0-9_.-]+\\[A-Za-z0-9_.-]+(?:\\[A-Za-z0-9_.-]+)+)",
    ],
    "CREDENTIAL_PATTERN": [
        r"(?i)(?:api[_-]?key|secret|token|password|credential)\s*[:=]\s*['\"][^'\"]+['\"]",
    ],
    "PRIVATE_REPOSITORY_REFERENCE": [
        r"(?i)(?:https?://)?(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)\S*(?:private|internal|corp|secret)[^\s]*",
    ],
    "PERSONAL_DATA_PATTERN": [
        r"(?i)\b(?:john\.|jane\.)\S+",
    ],
    "PROVIDER_SPECIFIC_CORE_ASSUMPTION": [
        r"\b(?:gpt-5\.3-codex-spark|Claude|Gemini|Qwen|Llama|Spark)\b",
    ],
}


def parse_rfc3339_timestamp(raw: str) -> datetime:
    """Parse RFC3339/Zulu timestamp text.

    Returns a timezone-aware datetime in UTC.
    """

    try:
        value = str(raw)
    except Exception as exc:
        raise ValueError(f"timestamp must be a string: {raw!r}") from exc

    if not value:
        raise ValueError("timestamp is empty")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("timezone missing")
    return dt.astimezone(timezone.utc)



def _run_git(args: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)


def _run_git_bytes(args: list[str], root: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True)


def _tracked_text_files(root: Path) -> tuple[list[Path], list[Path]]:
    """Return tracked text files and tracked binary files from git.

    Using ``git ls-files`` keeps the scope aligned with repository intent and
    avoids missing ignored files that should not be part of public claims.
    """

    result = _run_git(["ls-files", "-z"], root)
    if result.returncode != 0:
        raise ValidationError(f"unable to list git files: {result.stderr.strip()}")

    text_files: list[Path] = []
    binary_files: list[Path] = []
    for raw in result.stdout.split("\x00"):
        if not raw:
            continue
        path = root / raw
        if not path.exists() or not path.is_file():
            continue
        try:
            path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            binary_files.append(path)
            continue
        except Exception:
            binary_files.append(path)
            continue
        text_files.append(path)
    return sorted(text_files), sorted(binary_files)


def _run_patterns(path: Path, data: str, *, check_id: str, patterns: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for regex in patterns:
        compiled = re.compile(regex)
        for match in compiled.finditer(data):
            start = max(match.start() - 30, 0)
            end = min(match.end() + 30, len(data))
            try:
                rel_path = str(path.relative_to(ROOT))
            except ValueError:
                rel_path = str(path)
            finding = {
                "path": rel_path.replace("\\", "/"),
                "check": check_id,
                "pattern": regex,
                "excerpt": data[start:end].replace("\n", "\\n"),
            }
            findings.append(finding)
    return findings


def _is_allowed_violation(path: Path, finding: dict[str, Any]) -> bool:
    rel_path = path.relative_to(ROOT)
    normalized_path = rel_path.as_posix()
    allowed_checks = PUBLIC_SANITIZATION_ALLOWLIST.get(normalized_path, set())
    if finding["check"] in allowed_checks:
        return True
    return False


def _public_sanitization_report_path(root: Path, version: str | None = None) -> Path:
    release = (version or CURRENT_VERSION).strip()
    return root / "state" / "releases" / release / "sanitization-report.yaml"


def _compare_sanitization_report(root: Path, report: dict[str, Any], *, findings: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    path = _public_sanitization_report_path(root)
    if not path.exists():
        return [f"missing public sanitization report: {path.relative_to(root)}"]

    data = load_yaml(path)
    if data is None:
        return [f"invalid sanitization report: {path.relative_to(root)}"]

    for key in ["scope", "files_scanned", "files_excluded_as_binary", "result", "checks"]:
        if key not in data:
            errors.append(f"sanitization report missing {key}: {path.relative_to(root)}")
    if data.get("files_scanned") != report["files_scanned"]:
        errors.append("sanitization report files_scanned mismatch")
    if data.get("files_excluded_as_binary") != report["files_excluded_as_binary"]:
        errors.append("sanitization report excluded-binary count mismatch")
    if data.get("result") not in {"PASS", "FAIL"}:
        errors.append("sanitization report result must be PASS or FAIL")
    expected_checks = {entry["id"] for entry in report["checks"]}
    actual_checks = {entry.get("id") for entry in data.get("checks", []) if isinstance(entry, dict)}
    if expected_checks != actual_checks:
        errors.append("sanitization report checks mismatch")

    report_findings = data.get("findings") or []
    if not isinstance(report_findings, list):
        errors.append("sanitization report findings must be a list")
    else:
        if len(report_findings) != len(findings):
            errors.append("sanitization report finding count mismatch")
        for observed, expected in zip(
            sorted(report_findings, key=lambda item: (item.get("path"), item.get("check"))),
            sorted(findings, key=lambda item: (item.get("path"), item.get("check"))),
        ):
            if observed.get("path") != expected.get("path") or observed.get("check") != expected.get("check"):
                errors.append("sanitization report findings differ")
                break
    return errors


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

    version_re = re.compile(r"state/releases/([0-9]+\.[0-9]+\.[0-9]+)/")

    def _hash_from_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _load_bytes_from_commit(commit: str, relpath: str) -> bytes | None:
        result = _run_git_bytes(["show", f"{commit}:{relpath}"], ROOT)
        if result.returncode != 0:
            return None
        return result.stdout

    def _load_yaml_from_commit(commit: str, relpath: str) -> Any:
        result = _run_git_bytes(["show", f"{commit}:{relpath}"], ROOT)
        if result.returncode != 0:
            return None
        return yaml.safe_load(result.stdout.decode("utf-8"))

    def _coerce_legacy_subject(label: str, subject_data: Any) -> dict[str, Any] | None:
        if isinstance(subject_data, dict):
            return dict(subject_data)
        if isinstance(subject_data, str):
            match = re.match(r"YNM\s+(\d+\.\d+\.\d+)", subject_data)
            if not match:
                errors.append(f"{label}: baseline label is not in expected form: {subject_data!r}")
                return None
            return {"version": match.group(1)}
        errors.append(f"{label}: baseline subject must be a mapping or legacy string")
        return None

    def _resolve_commit(
        tag_or_sha: str | None,
        *,
        label: str,
        expected_tag: str | None = None,
        required: bool = True,
    ) -> str | None:
        if not tag_or_sha:
            return None
        sha = tag_or_sha.strip()
        if re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            if _run_git(["cat-file", "-e", f"{sha}^{{commit}}"], ROOT).returncode != 0:
                if required:
                    errors.append(f"{label}: baseline commit {sha!r} is not a valid git commit")
                return None
            return sha
        if sha.startswith("v"):
            result = _run_git(["rev-parse", f"{sha}^{{commit}}"], ROOT)
            if result.returncode != 0:
                if required:
                    errors.append(f"{label} baseline tag not resolvable: {sha}")
                return None
            resolved_commit = result.stdout.strip()
            if expected_tag and expected_tag != sha:
                if required:
                    errors.append(f"{label} baseline tag {sha!r} != expected {expected_tag!r}")
            return resolved_commit
        errors.append(f"{label}: baseline commit/tree metadata must be full commit SHA or tag")
        return None

    def _validate_subject(
        label: str,
        subject: dict[str, Any],
        *,
        expected_version: str | None = None,
        expected_tag: str | None = None,
        strict_version_subject: bool = True,
    ) -> tuple[str | None, str | None, str | None, str | None]:
        version = str(subject.get("version", "")).strip() or None
        tag = str(subject.get("tag", "")).strip() or None
        commit = str(subject.get("commit", "")).strip() or None
        tree = str(subject.get("tree", "")).strip() or None

        if expected_version and version and version != expected_version:
            errors.append(f"{label} baseline version {version!r} != expected {expected_version!r}")
        if not version and strict_version_subject:
            errors.append(f"{label} baseline version missing")

        resolved_commit = _resolve_commit(commit, label=label, expected_tag=expected_tag, required=strict_version_subject)
        if not resolved_commit and tag:
            resolved_commit = _resolve_commit(tag, label=label, expected_tag=expected_tag, required=strict_version_subject)

        if strict_version_subject:
            if not commit:
                errors.append(f"{label} baseline subject commit must be provided as full SHA")
            elif len(commit) != 40:
                errors.append(f"{label} baseline subject commit must be a full SHA")

            if not tag:
                errors.append(f"{label} baseline tag missing")
            elif expected_tag and tag != expected_tag:
                errors.append(f"{label} baseline tag {tag!r} != expected {expected_tag!r}")

            if not tree:
                errors.append(f"{label} baseline subject tree must be provided as full SHA")
            elif len(tree) != 40:
                errors.append(f"{label} baseline subject tree must be a full SHA")

        if expected_tag and tag and tag != expected_tag:
            # already added above in strict mode, but keep the deterministic message for non-strict callers.
            pass

        if resolved_commit and tree:
            tree_result = _run_git(["rev-parse", f"{resolved_commit}^{{tree}}"], ROOT)
            if tree_result.returncode != 0:
                errors.append(f"{label} baseline commit tree not resolvable: {resolved_commit}")
            else:
                resolved_tree = tree_result.stdout.strip()
                if tree and tree != resolved_tree:
                    errors.append(f"{label} baseline subject tree does not match commit tree")

        return resolved_commit, tree, version, tag

    def _validate_hashes(record_label: str, record: dict[str, Any], *, base_commit: str) -> None:
        files = record.get("files")
        if not isinstance(files, dict):
            return

        for path_text, expected in files.items():
            if not isinstance(path_text, str):
                continue

            match = version_re.match(path_text)
            if path_text.startswith("YNM_"):
                pass
            elif path_text == f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml":
                errors.append(f"{record_label}: baseline artifact path must not reference current release artifacts: {path_text}")
                continue
            elif not match:
                errors.append(f"{record_label}: non-baseline artifact referenced in files: {path_text}")
                continue
            if match and match.group(1) == CURRENT_VERSION:
                errors.append(f"{record_label}: baseline artifact path must not reference current release artifacts: {path_text}")
                continue

            expected_str = str(expected)
            if not isinstance(expected, str) or len(expected_str) != 64:
                errors.append(f"{record_label}: invalid baseline hash format for {path_text}")
                continue

            committed_bytes = _load_bytes_from_commit(base_commit, path_text)
            if committed_bytes is None:
                errors.append(f"{record_label}: baseline artifact missing in {base_commit}: {path_text}")
                continue

            actual_hash = _hash_from_bytes(committed_bytes)
            if expected_str != actual_hash:
                errors.append(f"{record_label}: baseline hash mismatch for {path_text}")

    candidate_baseline_path = ROOT / f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml"
    if not candidate_baseline_path.exists():
        return [f"missing candidate baseline-hashes record: state/releases/{CURRENT_VERSION}/baseline-hashes.yaml"]

    try:
        candidate_record = load_yaml(candidate_baseline_path)
    except Exception as exc:  # noqa: BLE001
        return [f"candidate baseline-hashes.yaml is malformed: {exc}"]

    if not isinstance(candidate_record, dict):
        return ["candidate baseline-hashes.yaml is not a mapping"]

    captured_at = candidate_record.get("captured_at")
    if captured_at is not None:
        try:
            parse_rfc3339_timestamp(str(captured_at))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"candidate baseline-hashes.yaml captured_at invalid: {exc}")
    else:
        errors.append("candidate baseline-hashes.yaml: captured_at missing")

    candidate_subject = _coerce_legacy_subject(
        f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml",
        candidate_record.get("baseline_subject") or candidate_record.get("baseline"),
    )
    if not candidate_subject:
        errors.append(f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml missing baseline_subject")
        return errors

    candidate_subject.setdefault("version", "1.2.0")
    candidate_subject.setdefault("tag", "v1.2.0")
    candidate_subject.setdefault("commit", "")
    candidate_subject.setdefault("tree", "")

    candidate_version = str(candidate_subject.get("version", "1.2.0")).strip()
    candidate_tag = f"v{candidate_version}" if candidate_version and not str(candidate_subject.get("tag", "")).startswith("v") else str(candidate_subject.get("tag", "")).strip()

    candidate_commit, candidate_tree, candidate_subject_version, _candidate_tag = _validate_subject(
        f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml",
        candidate_subject,
        expected_version=candidate_version,
        expected_tag=candidate_tag,
        strict_version_subject=True,
    )
    if not candidate_commit:
        return errors

    historical_version = candidate_subject_version or candidate_version
    historical_release_path = f"state/releases/{historical_version}/baseline-hashes.yaml"
    historical_record = _load_yaml_from_commit(candidate_commit, historical_release_path)
    if not isinstance(historical_record, dict):
        errors.append(f"unable to load historical record {historical_release_path} from {candidate_commit}")
        return errors

    historical_subject = _coerce_legacy_subject(
        historical_release_path,
        historical_record.get("baseline_subject") or historical_record.get("baseline"),
    )
    if historical_subject:
        historical_subject.setdefault("version", historical_version)
        historical_subject.setdefault("tag", f"v{historical_subject.get('version', '')}")
        historical_subject.setdefault("commit", "")
        historical_subject.setdefault("tree", "")

        # Some historical records pre-date immutable full subject metadata.
        # Validate what is available, but do not fail solely because vX.Y.Z tagging
        # was not captured in that historical format.
        _validate_subject(
            historical_release_path,
            historical_subject,
            expected_version=historical_subject.get("version"),
            expected_tag=historical_subject.get("tag"),
            strict_version_subject=False,
        )

    _validate_hashes(
        f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml",
        candidate_record,
        base_commit=candidate_commit,
    )
    _validate_hashes(
        historical_release_path,
        historical_record,
        base_commit=candidate_commit,
    )

    if candidate_tree:
        expected_tree_result = _run_git(["rev-parse", f"{candidate_commit}^{{tree}}"], ROOT)
        if expected_tree_result.returncode == 0 and candidate_tree != expected_tree_result.stdout.strip():
            errors.append(
                f"state/releases/{CURRENT_VERSION}/baseline-hashes.yaml: baseline subject tree does not match {candidate_commit}"
            )

    return errors



def check_public_sanitization() -> list[str]:
    errors: list[str] = []
    text_files, binary_files = _tracked_text_files(ROOT)
    checks = [
        {"id": "PRIVATE_ABSOLUTE_PATH"},
        {"id": "CREDENTIAL_PATTERN"},
        {"id": "PRIVATE_REPOSITORY_REFERENCE"},
        {"id": "PERSONAL_DATA_PATTERN"},
        {"id": "PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    ]

    findings: list[dict[str, Any]] = []
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        for check in checks:
            for finding in _run_patterns(path, text, check_id=check["id"], patterns=TEXT_PATTERNS[check["id"]]):
                if not _is_allowed_violation(path, finding):
                    findings.append(finding)

    for finding in sorted(findings, key=lambda item: (item["path"], item["check"])):
        errors.append(f"{finding['path']}: {finding['check']} violation")

    report = {
        "schema_version": "ynm-public-sanitization.v1",
        "scope": "ALL_TRACKED_TEXT",
        "files_scanned": len(text_files),
        "files_excluded_as_binary": len(binary_files),
        "excluded_paths": sorted((path.relative_to(ROOT).as_posix()) for path in binary_files),
        "checks": checks,
        "result": "PASS" if not findings else "FAIL",
        "findings": sorted(findings, key=lambda item: (item["path"], item["check"], item["pattern"]),),
    }
    errors.extend(_compare_sanitization_report(ROOT, report, findings=findings))

    if findings:
        for path in sorted({finding["path"] for finding in findings}):
            errors.append(f"sanitization finding: {path}")

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


def run(requested_checks: Sequence[str] | None = None) -> list[str]:
    errors: list[str] = []

    checks = list(requested_checks) if requested_checks else DEFAULT_CHECKS
    normalized: list[str] = sorted(set(checks))

    if "schema" in normalized:
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

    if "links" in normalized:
        errors.extend(check_links())
    if "normative-invariants" in normalized:
        errors.extend(check_normative_invariants())
    if "state" in normalized:
        errors.extend(check_state())
    if "yaml-disposition-quoting" in normalized:
        errors.extend(check_yaml_disposition_quoting())
    if "release" in normalized:
        errors.extend(check_release())
    if "version-consistency" in normalized:
        errors.extend(check_version_consistency())
    if "baseline-integrity" in normalized:
        errors.extend(check_baseline_integrity())
    if "public-sanitization" in normalized:
        errors.extend(check_public_sanitization())
    if "runtime-boundary" in normalized:
        errors.extend(check_runtime_boundary())

    if "release" in normalized or "version-consistency" in normalized:
        scenarios = [line for line in (ROOT / "methodology/adversarial-validation.md").read_text(encoding="utf-8").splitlines() if line.startswith("| ")]
        if len(scenarios) != 80:
            errors.append(f"adversarial scenario count: expected 80, found {len(scenarios)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="append",
        choices=DEFAULT_CHECKS + ["security-boundary", "all"],
        help="Run a single validation check (repeatable).",
    )
    args = parser.parse_args()

    requested = args.check
    if requested:
        if "all" in requested:
            checks_to_run = DEFAULT_CHECKS
        elif "security-boundary" in requested:
            checks_to_run = SECURITY_BOUNDARY_CHECKS
        else:
            checks_to_run = sorted(set(requested))
    else:
        checks_to_run = DEFAULT_CHECKS

    errors = run(checks_to_run)
    if errors:
        print("YNM validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("YNM validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
