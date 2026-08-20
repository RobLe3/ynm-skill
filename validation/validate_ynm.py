#!/usr/bin/env python3
"""Validate YNM schemas, fixtures, and repository invariants with Draft 2020-12 JSON Schema."""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import argparse
import hashlib
from datetime import datetime, timezone

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
    "package-links",
    "adversarial-scenarios",
    "normative-invariants",
    "state",
    "yaml-disposition-quoting",
    "release",
    "version-consistency",
    "baseline-integrity",
    "public-sanitization",
    "runtime-boundary",
    "workflow-invariants",
    "current-evidence-references",
    "evaluation-artifacts",
]
PREFLIGHT_CHECKS = [
    "schema",
    "links",
    "adversarial-scenarios",
    "normative-invariants",
    "state",
    "yaml-disposition-quoting",
    "release",
    "version-consistency",
    "baseline-integrity",
    "public-sanitization",
    "runtime-boundary",
    "workflow-invariants",
    "current-evidence-references",
    "evaluation-artifacts",
]
CROSS_PLATFORM_CHECKS = [
    "schema",
    "links",
    "adversarial-scenarios",
    "normative-invariants",
    "state",
    "yaml-disposition-quoting",
    "runtime-boundary",
]
SECURITY_BOUNDARY_CHECKS = [
    "repository-security-boundary",
    "project-integration-security",
]
REPOSITORY_SECURITY_BOUNDARY_CHECKS = ["baseline-integrity", "public-sanitization", "runtime-boundary"]
PROJECT_INTEGRATION_SECURITY_CHECKS = ["project-integration-security"]
REPOSITORY_LINK_CHECK_FORBIDDEN_PREFIXES = {
    "state",
    "tests",
    "validation",
    "dist",
    ".tmp",
    ".venv",
    ".github",
}

AGENTS_MARKER_START = "<!-- YNM:BEGIN -->"
AGENTS_MARKER_END = "<!-- YNM:END -->"
PUBLIC_SANITIZATION_ALLOWLIST: dict[str, set[str]] = {
    "docs/errata/1.2.0-publication.md": {"PRIVATE_REPOSITORY_REFERENCE"},
    "tests/test_validate_ynm.py": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    "validation/validate_ynm.py": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION", "PRIVATE_ABSOLUTE_PATH"},
    "validation/validate_release_integrity.py": {"PRIVATE_ABSOLUTE_PATH"},
    "VALIDATION.md": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    "evaluations/README.md": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    "evaluations/results/model-availability.yaml": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    "scripts/run_evaluations.py": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    "state/releases/1.3.0/review-plan.yaml": {"PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
}
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "ynm-ci.yml"
ALLOWED_CAPABILITY_LABELS = {
    "VALIDATED",
    "SUPPORTED_BY_DESIGN",
    "PARTIALLY_VALIDATED",
    "NOT_VALIDATED",
    "KNOWN_LIMITATION",
    "MAINTAINER_VALIDATED",
}
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
    "PROVIDER_SPECIFIC_CORE_ASSUMPTION": [
        r"\b(?:gpt-5\.3-codex-spark|Claude|Gemini|Qwen|Llama|Spark)\b",
    ],
}


_INLINE_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_REFERENCE_USAGE_RE = re.compile(r"\[[^\]]+\]\[([^\]]+)\]")
_REFERENCE_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)


def _parse_markdown_links(text: str) -> list[tuple[str, str]]:
    """Return ``(link_text, target)`` pairs from inline and reference-style links."""

    links: list[tuple[str, str]] = []
    for match in _INLINE_LINK_RE.finditer(text):
        links.append((match.group(0), match.group(1).strip()))

    refs: dict[str, str] = {}
    for match in _REFERENCE_DEF_RE.finditer(text):
        refs[match.group(1).strip().lower()] = match.group(2).strip()

    for match in _REFERENCE_USAGE_RE.finditer(text):
        target_label = match.group(1).strip().lower()
        if target_label in refs:
            links.append((match.group(0), refs[target_label]))
    return links


def _is_control_or_empty(path: str) -> bool:
    return not path or "\x00" in path or any(ord(ch) < 0x20 for ch in path if ch not in "\t\n\r")


def _contains_windows_drive(path: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", path))


def _contains_unc(path: str) -> bool:
    return path.startswith("\\\\") or path.startswith("//")


def _extract_pyproject_version(root: Path) -> str:
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"(?P<version>\d+\.\d+\.\d+)"', pyproject)
    if not match:
        return ""
    return match.group("version")


def _resolve_markdown_link_target(
    source_path: Path,
    raw_target: str,
    *,
    expected_root: Path,
) -> Path:
    if _is_control_or_empty(raw_target):
        raise ValueError("empty markdown link target")
    target = raw_target.split("#", 1)[0].strip()
    if not target or target.startswith("#"):
        raise ValueError("anchor-only target")
    if target.startswith("mailto:") or target.startswith("http://") or target.startswith("https://"):
        raise ValueError("external target")
    if _contains_windows_drive(target) or _contains_unc(target):
        raise ValueError(f"disallowed absolute or UNC target: {target}")
    if target.startswith("/"):
        raise ValueError(f"absolute filesystem target: {target}")

    candidate = (source_path.parent / target).resolve()
    if _is_control_or_empty(str(candidate)):
        raise ValueError("target resolved to invalid path")
    return candidate


def _check_markdown_links_for_root(
    path: Path,
    *,
    expected_root: Path,
    forbidden_prefixes: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    canonical_root = expected_root.resolve()

    def display(candidate: Path) -> str:
        canonical_candidate = candidate.resolve()
        for base in (canonical_root, ROOT.resolve()):
            try:
                return canonical_candidate.relative_to(base).as_posix()
            except ValueError:
                continue
        return candidate.name

    if not path.exists():
        return [f"{path}: link source file missing"]

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"{path}: cannot read markdown file: {exc}"]

    forbidden_prefixes = set(forbidden_prefixes or set())
    for _, raw_target in _parse_markdown_links(text):
        if raw_target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_part = raw_target.split("#", 1)[0]
        if not target_part:
            continue
        try:
            resolved = _resolve_markdown_link_target(path, raw_target, expected_root=expected_root)
        except ValueError as exc:
            if str(exc).endswith("anchor-only target") or str(exc).startswith("external target"):
                continue
            errors.append(
                f"{display(path)}: link target '{raw_target}' invalid ({exc})"
            )
            continue
        if not resolved.exists():
            errors.append(f"{display(path)}: broken link target '{raw_target}'")
            continue
        try:
            resolved.relative_to(canonical_root)
        except ValueError as exc:
            errors.append(
                f"{display(path)}: link target '{raw_target}' escapes expected root "
                f"(resolved={resolved})"
            )
            continue
        if forbidden_prefixes:
            rel = resolved.relative_to(canonical_root)
            if rel.parts and rel.parts[0] in forbidden_prefixes:
                errors.append(
                    f"{display(path)}: runtime depends on non-runtime artifact '{raw_target}'"
                )
    return errors


def _parse_markdown_table_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return rows

    header_found = False
    separator_seen = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.count("|") < 2:
            continue

        columns = [col.strip() for col in stripped.strip("|").split("|")]
        if len(columns) < 3:
            continue

        if not header_found:
            if columns[0].lower() in {"scenario id", "scenario_id", "id"}:
                header_found = True
            continue

        if not separator_seen:
            if all(set(col.strip()) <= {"-", ":"} for col in columns):
                separator_seen = True
            continue

        if all(not col.strip() for col in columns[:3]):
            continue
        rows.append({"id": columns[0].strip(), "scenario": columns[1].strip(), "behavior": columns[2].strip()})
    return rows


def check_adversarial_scenarios() -> list[str]:
    path = ROOT / "methodology" / "adversarial-validation.md"
    rows = _parse_markdown_table_rows(path)
    if not rows:
        return ["adversarial scenario table missing or malformed"]

    errors: list[str] = []
    ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        scenario_id = row.get("id", "").strip()
        scenario = row.get("scenario", "").strip()
        behavior = row.get("behavior", "").strip()

        if not scenario_id:
            errors.append(f"adversarial scenario row {index} missing Scenario ID")
        if not scenario:
            errors.append(f"adversarial scenario {scenario_id or index} missing required scenario text")
        if not behavior:
            errors.append(f"adversarial scenario {scenario_id or index} missing required behavior text")

        if scenario_id:
            if scenario_id in ids:
                errors.append(f"duplicate adversarial Scenario ID: {scenario_id}")
            ids.add(scenario_id)

    if not errors:
        return []
    return errors


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
        errors.append(
            "sanitization report files_scanned mismatch: "
            f"recorded={data.get('files_scanned')} actual={report['files_scanned']}\n"
            "Refresh intentionally with:\n"
            "python validation/validate_ynm.py --refresh-sanitization-report"
        )
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


def generate_sanitization_report(root: Path = ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    text_files, binary_files = _tracked_text_files(root)
    checks = [
        {"id": "PRIVATE_ABSOLUTE_PATH"},
        {"id": "CREDENTIAL_PATTERN"},
        {"id": "PRIVATE_REPOSITORY_REFERENCE"},
        {"id": "PROVIDER_SPECIFIC_CORE_ASSUMPTION"},
    ]

    findings: list[dict[str, Any]] = []
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        for check in checks:
            for finding in _run_patterns(path, text, check_id=check["id"], patterns=TEXT_PATTERNS[check["id"]]):
                if not _is_allowed_violation(path, finding):
                    findings.append(finding)

    findings = sorted(findings, key=lambda item: (item["path"], item["check"], item["pattern"]))
    return (
        {
            "schema_version": "ynm-public-sanitization.v1",
            "scope": "ALL_TRACKED_TEXT",
            "files_scanned": len(text_files),
            "files_excluded_as_binary": len(binary_files),
            "excluded_paths": sorted((path.relative_to(root).as_posix()) for path in binary_files),
            "checks": checks,
            "result": "PASS" if not findings else "FAIL",
            "findings": findings,
        },
        findings,
    )


def write_sanitization_report(root: Path, version: str, report: dict[str, Any], *, dry_run: bool = False) -> Path:
    path = _public_sanitization_report_path(root, version)
    if dry_run:
        print(f"NOT_WRITING: {path}")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(report, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return path


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
    excluded_prefixes = {"dist", "dist-cli", ".tmp", ".venv", ".github", ".devcontainer"}
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT).as_posix()
        if not relative:
            continue
        if relative.split("/", maxsplit=1)[0] in excluded_prefixes:
            continue
        errors.extend(_check_markdown_links_for_root(path, expected_root=ROOT, forbidden_prefixes=None))
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
    release_state = ROOT / f"state/releases/{CURRENT_VERSION}"
    required = {
        "findings.yaml",
        "events.yaml",
        "loop-results.yaml",
        "runs.yaml",
        "review-plan.yaml",
    }

    if not release_state.exists():
        errors.append(f"{release_state.relative_to(ROOT)}: missing")
        return errors

    for required_file in sorted(required):
        path = release_state / required_file
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing")

    if errors:
        return errors

    release_findings = load_yaml(release_state / "findings.yaml")
    release_events = load_yaml(release_state / "events.yaml")
    release_runs = load_yaml(release_state / "runs.yaml")
    release_plan = load_yaml(release_state / "review-plan.yaml")
    loop_records = load_yaml(release_state / "loop-results.yaml")

    findings = release_findings.get("findings", [])
    events = release_events.get("events", [])
    runs = release_runs.get("runs", [])
    records = loop_records.get("loop_results", [])
    plan = release_plan.get("review_plan", {})

    if not isinstance(findings, list):
        errors.append("state/releases/" + CURRENT_VERSION + "/findings.yaml: findings must be a list")
        findings = []
    if not isinstance(events, list):
        errors.append("state/releases/" + CURRENT_VERSION + "/events.yaml: events must be a list")
        events = []
    if not isinstance(runs, list):
        errors.append("state/releases/" + CURRENT_VERSION + "/runs.yaml: runs must be a list")
        runs = []
    if not isinstance(records, list):
        errors.append("state/releases/" + CURRENT_VERSION + "/loop-results.yaml: loop_results must be a list")
        records = []
    if not isinstance(plan, dict):
        errors.append("state/releases/" + CURRENT_VERSION + "/review-plan.yaml: review_plan must be a mapping")
        plan = {}

    finding_ids = {item.get("id") for item in findings if isinstance(item, dict) and isinstance(item.get("id"), str)}
    event_ids = {item.get("event_id") for item in events if isinstance(item, dict) and isinstance(item.get("event_id"), str)}
    if len(finding_ids) != len([item for item in findings if isinstance(item, dict) and isinstance(item.get("id"), str)]):
        errors.append(f"state/releases/{CURRENT_VERSION}/findings.yaml: duplicate finding ID")
    if len(event_ids) != len([item for item in events if isinstance(item, dict) and isinstance(item.get("event_id"), str)]):
        errors.append(f"state/releases/{CURRENT_VERSION}/events.yaml: duplicate event ID")

    finding_schema = load_json(SCHEMAS / "finding.schema.json")
    for item in findings:
        if isinstance(item, dict):
            errors.extend(
                f"state/releases/{CURRENT_VERSION}/findings.yaml:{item.get('id')}: {e}"
                for e in validate(item, finding_schema)
            )
            for event in item.get("history", []):
                if event not in event_ids:
                    errors.append(f"findings.yaml:{item.get('id')}: unknown history event {event}")

    run_schema = load_json(SCHEMAS / "run-receipt.schema.json")
    seen: set[str] = set()
    for item in runs:
        if not isinstance(item, dict):
            errors.append("state/releases/" + CURRENT_VERSION + "/runs.yaml: run entry must be a mapping")
            continue
        run_id = str(item.get("run_id", ""))
        if not run_id:
            errors.append("state/releases/" + CURRENT_VERSION + "/runs.yaml: run_id missing")
        if run_id in seen:
            errors.append(f"state/releases/{CURRENT_VERSION}/runs.yaml: duplicate run ID {run_id}")
        seen.add(run_id)
        errors.extend(f"state/releases/{CURRENT_VERSION}/runs.yaml:{run_id}: {e}" for e in validate(item, run_schema))
        if "DELIVERY" not in item.get("phase_history", []):
            errors.append(f"state/releases/{CURRENT_VERSION}/runs.yaml:{run_id}: DELIVERY missing from phase history")

    expected_loops = {"Architecture", "Implementation", "Adoption", "Maintenance", "Disposition", "Meta"}
    observed_loops = {item.get("loop") for item in records if isinstance(item, dict) and isinstance(item.get("loop"), str)}
    if observed_loops != expected_loops:
        errors.append(f"state/releases/{CURRENT_VERSION}/loop-results.yaml: expected all six focal loop records")

    loop_schema = load_json(SCHEMAS / "loop-result.schema.json")
    for item in records:
        if isinstance(item, dict):
            errors.extend(
                f"state/releases/{CURRENT_VERSION}/loop-results.yaml:{item.get('loop')}: {e}"
                for e in validate(item, loop_schema)
            )

    errors.extend(
        f"state/releases/{CURRENT_VERSION}/review-plan.yaml: {e}"
        for e in validate(plan, load_json(SCHEMAS / "review-plan.schema.json"))
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

    release_dir = ROOT / f"state/releases/{version}"
    release_assessment = load_yaml(release_dir / "final-assessment.yaml") if (release_dir / "final-assessment.yaml").exists() else None
    final_disposition = release_assessment.get("final_assessment", {}).get("disposition", "").strip() if isinstance(release_assessment, dict) else ""
    if final_disposition not in {"YES", "NO", "MAYBE"}:
        errors.append(f"state/releases/{version}/final-assessment.yaml: missing or invalid final_disposition")

    manifest = load_yaml(ROOT / "manifest.yaml")
    if manifest.get("version") != version:
        errors.append("manifest.yaml: version does not match VERSION")

    if version not in (ROOT / "README.md").read_text(encoding="utf-8"):
        errors.append("README.md: current version is not stated")

    if f"## [{version}]" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        errors.append("CHANGELOG.md: current version entry is missing")

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
            "events.yaml",
        ]:
            if not (release_dir / required).exists():
                errors.append(f"state/releases/{version}: missing {required}")

    # Candidate final assessment remains the only current-blocking source for maturity.
    if not (release_dir / "final-assessment.yaml").exists():
        errors.append("release final-assessment.yaml missing")
    else:
        latest = load_yaml(release_dir / "findings.yaml")
        if isinstance(latest, dict):
            finding_blocks = latest.get("findings", [])
            blockers = [
                item.get("id")
                for item in finding_blocks
                if isinstance(item, dict)
                and item.get("maturity_impact") == "MATURITY_BLOCKING"
                and item.get("status") not in {"RESOLVED", "CLOSED"}
            ]
            if blockers:
                errors.append(f"state/releases/{version}/findings.yaml: unresolved maturity blockers {blockers}")

    release_assessment = load_yaml(release_dir / "assessment.yaml")
    if isinstance(release_assessment, dict):
        assessment_block = release_assessment.get("assessment", {})
        reference_state = assessment_block.get("reference_state") or assessment_block.get("baseline_subject")
        if isinstance(reference_state, dict) and reference_state.get("version") != "1.2.0":
            errors.append(f"state/releases/{version}/assessment.yaml: reference state must remain 1.2.0 baseline")

    package_component = manifest.get("package", {})
    package_entries = package_component.get("include") if isinstance(package_component, dict) else None
    if isinstance(package_entries, list):
        for item_path in package_entries:
            if not isinstance(item_path, str) or not item_path.strip():
                errors.append("manifest.yaml: package.include must be a list of paths")
                break
            if not (ROOT / item_path).exists():
                errors.append(f"manifest.yaml: missing path {item_path}")
    else:
        errors.append("manifest.yaml: package.include must be a non-empty list")

    for item_path in _flatten_manifest_values(manifest.get("optional_adapters", {})):
        if not (ROOT / item_path).exists():
            errors.append(f"manifest.yaml: missing optional adapter path {item_path}")

    for item_path in _flatten_manifest_values(manifest.get("package", {})):
        if item_path == "include":
            continue
        if not (ROOT / item_path).exists():
            errors.append(f"manifest.yaml: missing manifest package metadata path {item_path}")

    labels = ALLOWED_CAPABILITY_LABELS
    for name, label in manifest.get("compatibility", {}).items():
        if label not in labels:
            errors.append(f"manifest.yaml: invalid capability label for {name}: {label}")

    return errors


def load_yaml_frontmatter(path: Path) -> dict[str, Any] | None:
    """Load YAML frontmatter from markdown-like files.

    Non-Markdown files are not expected here, so return None if the file does not
    contain a parseable frontmatter block.
    """

    try:
        raw = path.read_text(encoding="utf-8")
    except Exception:
        return None

    if not raw.lstrip().startswith("---"):
        return None

    # locate the second frontmatter marker. Use direct search to avoid relying
    # on third-party helpers and to preserve deterministic behavior.
    terminator = raw.find("\n---", 3)
    if terminator == -1:
        return None

    block = raw[3:terminator]
    if not block.strip():
        return None

    try:
        data = yaml.safe_load(block)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


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
    report, findings = generate_sanitization_report(ROOT)

    for finding in sorted(findings, key=lambda item: (item["path"], item["check"])):
        errors.append(f"{finding['path']}: {finding['check']} violation")
    errors.extend(_compare_sanitization_report(ROOT, report, findings=findings))

    if findings:
        for path in sorted({finding["path"] for finding in findings}):
            errors.append(f"sanitization finding: {path}")

    return errors


def check_workflow_invariants() -> list[str]:
    errors: list[str] = []

    if not WORKFLOW_PATH.exists():
        return ["workflow invariant check: workflow file missing"]

    try:
        workflow = load_yaml(WORKFLOW_PATH)
    except Exception as exc:  # noqa: BLE001
        return [f"workflow invariant check: failed to parse workflow: {exc}"]

    if not isinstance(workflow, dict):
        return ["workflow invariant check: workflow is not a mapping"]

    on_entry = workflow.get("on")
    if on_entry is None and True in workflow:
        on_entry = workflow.get(True)
    if not isinstance(on_entry, dict):
        errors.append("workflow invariant: on block missing")
        return errors

    push = on_entry.get("push")
    if not isinstance(push, dict):
        errors.append("workflow invariant: push event missing")
    else:
        branches = push.get("branches")
        tags = push.get("tags")
        if branches != ["main"]:
            errors.append(f"workflow invariant: push.branches must be ['main'], found {branches}")
        if tags != ["v*"]:
            errors.append(f"workflow invariant: push.tags must be ['v*'], found {tags}")

    if "pull_request" not in on_entry:
        errors.append("workflow invariant: pull_request trigger missing")
    if "workflow_dispatch" not in on_entry:
        errors.append("workflow invariant: workflow_dispatch trigger missing")

    concurrency = workflow.get("concurrency")
    if not isinstance(concurrency, dict):
        errors.append("workflow invariant: concurrency block missing")
    else:
        group = str(concurrency.get("group", ""))
        if "github.event.pull_request.number" not in group or "github.ref" not in group:
            errors.append("workflow invariant: concurrency group must isolate pull requests and refs")
        if not concurrency.get("cancel-in-progress"):
            errors.append("workflow invariant: concurrency.cancel-in-progress must be true")

    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        errors.append("workflow invariant: jobs block missing")
        return errors

    if "release-integrity-tag" not in jobs:
        errors.append("workflow invariant: release-integrity-tag job missing")
    if "preflight" not in jobs:
        errors.append("workflow invariant: preflight job missing")

    validate_job = jobs.get("validate")
    if not isinstance(validate_job, dict) or validate_job.get("needs") != "preflight":
        errors.append("workflow invariant: validate matrix must depend on preflight")
    for downstream in ["package", "security"]:
        job = jobs.get(downstream)
        if not isinstance(job, dict) or job.get("needs") != "validate":
            errors.append(f"workflow invariant: {downstream} job must depend on validate")

    actions = [line for line in WORKFLOW_PATH.read_text(encoding="utf-8").splitlines() if "uses:" in line]
    if "@" not in "".join(actions):
        errors.append("workflow invariant: unable to detect action references")

    for line in actions:
        if "actions/checkout@" in line and not re.search(r"@([0-9a-f]{40})", line):
            errors.append("workflow invariant: checkout action must use full commit SHA")
        if "actions/setup-python@" in line and not re.search(r"@([0-9a-f]{40})", line):
            errors.append("workflow invariant: setup-python action must use full commit SHA")

    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps", []) or []:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "")
            if isinstance(uses, str) and uses.startswith("actions/checkout@"):
                with_credentials = False
                for key, value in step.items():
                    if (
                        key == "with"
                        and isinstance(value, dict)
                        and value.get("persist-credentials") in {False, "false", 0}
                    ):
                        with_credentials = True
                if not with_credentials:
                    errors.append("workflow invariant: checkout steps must set persist-credentials: false")

    if isinstance(jobs.get("release-integrity-tag"), dict):
        if "if" not in jobs["release-integrity-tag"]:
            errors.append("workflow invariant: release-integrity-tag job missing tag-condition guard")
        elif str(jobs["release-integrity-tag"]["if"]) != "github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')":
            errors.append("workflow invariant: release-integrity-tag job condition is not tag-guarded correctly")
        needs = jobs["release-integrity-tag"].get("needs")
        if not isinstance(needs, list):
            errors.append("workflow invariant: release-integrity-tag job requires explicit needs")
        else:
            missing_needs = sorted(set(["preflight", "validate", "package", "security"]) - set(needs))
            if missing_needs:
                errors.append(f"workflow invariant: release-integrity-tag job missing needs {missing_needs}")
        workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
        if "--require-tagged-subject" not in workflow_text or '--tag-ref "$GITHUB_REF_NAME"' not in workflow_text:
            errors.append("workflow invariant: tag job must validate the exact tagged subject")
        if "main:refs/remotes/origin/main" not in workflow_text:
            errors.append("workflow invariant: tag job must fetch an exact origin/main tracking ref")
        tag_steps = jobs["release-integrity-tag"].get("steps", [])
        checkout_steps = [step for step in tag_steps if isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/checkout@")]
        if not checkout_steps or checkout_steps[0].get("with", {}).get("fetch-depth") != 0:
            errors.append("workflow invariant: tag checkout must use full history")
        if re.search(r"\b(?:gh release create|softprops/action-gh-release|actions/create-release)\b", workflow_text):
            errors.append("workflow invariant: validation workflow must not publish a release")

    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "--refresh-sanitization-report" in workflow_text:
        errors.append("workflow invariant: CI must not refresh candidate evidence")
    if "pip install --upgrade pip" in workflow_text:
        errors.append("workflow invariant: CI must not upgrade pip implicitly")
    if "git config --global core.autocrlf" in workflow_text or "git config --global core.eol" in workflow_text:
        errors.append("workflow invariant: checkout normalization must rely on .gitattributes")

    return errors


def check_runtime_boundary() -> list[str]:
    errors: list[str] = []
    normative = [
        ROOT / "SKILL.md",
        ROOT / "README.md",
        *(ROOT / "contracts").glob("*.md"),
        *(ROOT / "loops").glob("*.md"),
        *(ROOT / "methodology").glob("*.md"),
        ROOT / "schemas" / "run-receipt.schema.json",
        ROOT / "schemas" / "finding.schema.json",
    ]
    for path in normative:
        if not path.exists():
            continue
        errors.extend(
            _check_markdown_links_for_root(
                path,
                expected_root=ROOT,
                forbidden_prefixes=REPOSITORY_LINK_CHECK_FORBIDDEN_PREFIXES | {"manifest.yaml", "AGENTS.md"},
            )
        )
    return errors


def check_package_links() -> list[str]:
    errors: list[str] = []
    package_path = ROOT / "dist" / "ynm"
    if not package_path.exists():
        return errors

    package_yaml = package_path / "package-manifest.yaml"
    if not package_yaml.exists():
        errors.append("package-manifest.yaml missing from dist/ynm")
        return errors

    for path in package_path.rglob("*.md"):
        errors.extend(
            _check_markdown_links_for_root(
                path,
                expected_root=package_path,
                forbidden_prefixes=set(),
            )
        )
    return errors


def check_project_integration_security() -> list[str]:
    """Run focused project-integration boundary tests.

    Security-boundary mode must cover repository checks and project-integration
    controls separately so failures are attributable to the right domain.
    """

    tests = [
        "tests.test_validate_ynm.YNMValidationTests.test_discovery_and_unapproved_initialize_are_read_only",
        "tests.test_validate_ynm.YNMValidationTests.test_bootstrap_is_idempotent",
        "tests.test_validate_ynm.YNMValidationTests.test_agents_integration_preserves_human_content",
        "tests.test_validate_ynm.YNMValidationTests.test_malformed_agents_markers_block_all_writes",
        "tests.test_validate_ynm.YNMValidationTests.test_discovery_classification_requires_confirmation",
    ]

    command = [sys.executable, "-m", "unittest", *tests]
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return [f"project integration security tests failed: {result.stdout} {result.stderr}".strip()]
    return []


def check_version_consistency() -> list[str]:
    expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    errors: list[str] = []

    manifest = load_yaml(ROOT / "manifest.yaml")
    if manifest.get("version") != expected:
        errors.append(f"manifest.yaml: version field mismatch: expected {expected}, found {manifest.get('version')}")
    manifest_metadata_version = manifest.get("metadata", {}).get("version") if isinstance(manifest.get("metadata"), dict) else None
    if manifest_metadata_version != expected:
        errors.append(
            f"manifest.yaml: metadata.version mismatch: expected {expected}, found {manifest_metadata_version}"
        )

    skill = load_yaml_frontmatter(ROOT / "SKILL.md")
    if not isinstance(skill, dict):
        errors.append("SKILL.md: frontmatter is not parseable metadata")
    else:
        skill_version = skill.get("metadata", {}).get("version")
        if skill_version != expected:
            errors.append(f"SKILL.md metadata.version mismatch: expected {expected}, found {skill_version}")
        if not isinstance(skill.get("compatibility"), str) or not skill.get("compatibility", "").strip():
            errors.append("SKILL.md: top-level Agent Skills compatibility field missing")
        if isinstance(skill.get("metadata"), dict) and "compatibility" in skill["metadata"]:
            errors.append("SKILL.md: compatibility must be top-level, not nested under metadata")

    pyproject_version = _extract_pyproject_version(ROOT)
    if not pyproject_version:
        errors.append("pyproject.toml: project version missing")
    elif pyproject_version != expected:
        errors.append(f"pyproject.toml: version mismatch: expected {expected}, found {pyproject_version}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{expected}]" not in changelog:
        errors.append(f"CHANGELOG.md: missing current version heading for {expected} unreleased section")

    publication = load_yaml(ROOT / f"state/releases/{expected}/publication.yaml")
    if not isinstance(publication, dict):
        errors.append(f"state/releases/{expected}/publication.yaml missing or malformed")
    else:
        publication_version = str(publication.get("publication", {}).get("version", "")).strip() if isinstance(publication.get("publication"), dict) else str(publication.get("version", "")).strip()
        if publication_version and publication_version != expected:
            errors.append(f"state/releases/{expected}/publication.yaml version mismatch: expected {expected}, found {publication_version}")

    final_assessment = load_yaml(ROOT / f"state/releases/{expected}/final-assessment.yaml")
    if not isinstance(final_assessment, dict):
        errors.append(f"state/releases/{expected}/final-assessment.yaml missing or malformed")
    else:
        decision = final_assessment.get("final_assessment", {}).get("version_decision", "")
        if decision and str(decision) != expected:
            errors.append(
                f"state/releases/{expected}/final-assessment.yaml version_decision mismatch: expected {expected}, found {decision}"
            )

    return errors


def check_current_evidence_references(root: Path = ROOT, version: str = CURRENT_VERSION) -> list[str]:
    """Require path-like evidence in current findings to resolve inside the repository."""

    findings_path = root / f"state/releases/{version}/findings.yaml"
    if not findings_path.exists():
        return [f"{findings_path}: current findings file missing"]
    payload = load_yaml(findings_path)
    findings = payload.get("findings", []) if isinstance(payload, dict) else []
    errors: list[str] = []
    canonical_root = root.resolve()
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        finding_id = finding.get("id", "<unknown>")
        for locator in finding.get("evidence", []):
            if not isinstance(locator, str) or "/" not in locator:
                continue
            if re.match(r"^[a-z][a-z0-9+.-]*://", locator, re.IGNORECASE):
                continue
            candidate = (root / locator).resolve()
            try:
                candidate.relative_to(canonical_root)
            except ValueError:
                errors.append(f"{finding_id}: evidence path escapes repository: {locator}")
                continue
            if not candidate.exists():
                errors.append(f"{finding_id}: evidence path does not exist: {locator}")
    return errors


def check_evaluation_artifacts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    schema_root = root / "evaluations/schemas"
    scenario_schema_path = schema_root / "evaluation-scenario.schema.json"
    result_schema_path = schema_root / "evaluation-result.schema.json"
    score_schema_path = schema_root / "evaluation-score.schema.json"
    for path in (scenario_schema_path, result_schema_path, score_schema_path):
        if not path.exists():
            errors.append(f"{path.relative_to(root)}: evaluation schema missing")
            continue
        schema = load_json(path)
        try:
            Draft202012Validator.check_schema(schema)
        except jsonschema_exceptions.SchemaError as exc:
            errors.append(f"{path.relative_to(root)}: schema error: {exc.message}")
    if errors:
        return errors
    scenarios = load_yaml(root / "evaluations/scenarios.yaml")
    scenario_errors = sorted(Draft202012Validator(load_json(scenario_schema_path), format_checker=FormatChecker()).iter_errors(scenarios), key=lambda item: list(item.absolute_path))
    for error in scenario_errors:
        errors.append(f"evaluations/scenarios.yaml: {error.json_path}: {error.message}")
    scenario_ids = [item.get("id") for item in scenarios.get("scenarios", []) if isinstance(item, dict)]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("evaluations/scenarios.yaml: duplicate scenario IDs")
    protocol = load_yaml(root / "evaluations/protocol.yaml")
    if protocol.get("revision") != 2:
        errors.append("evaluations/protocol.yaml: revision must be 2 for the frozen empirical cycle")
    if protocol.get("primary_executor") != "gpt-5.6-sol":
        errors.append("evaluations/protocol.yaml: primary executor drift")
    expected_candidates = ["gpt-5.4-mini-2026-03-17", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.4"]
    if protocol.get("replication_candidates") != expected_candidates:
        errors.append("evaluations/protocol.yaml: replication candidate order drift")
    findings = load_yaml(root / "state/releases/1.3.0/findings.yaml").get("findings", [])
    finding_ids = [item.get("id") for item in findings if isinstance(item, dict)]
    collisions = set(finding_ids) & set(scenario_ids)
    allowed_historical_collisions = {"YNM-EVAL-001"}
    unexpected = sorted(collisions - allowed_historical_collisions)
    if unexpected:
        errors.append(f"evaluation identifier collision across finding and scenario types: {', '.join(unexpected)}")
    result_paths = sorted((root / "evaluations/results/records").glob("*.yaml")) if (root / "evaluations/results/records").exists() else []
    result_records: list[dict] = []
    for result_path in result_paths:
        result = load_yaml(result_path)
        result_records.append(result)
        result_errors = sorted(Draft202012Validator(load_json(result_schema_path), format_checker=FormatChecker()).iter_errors(result), key=lambda item: list(item.absolute_path))
        for error in result_errors:
            errors.append(f"{result_path.relative_to(root)}: {error.json_path}: {error.message}")
    for score_path in sorted((root / "evaluations/results/blinded/scores").glob("*.yaml")) if (root / "evaluations/results/blinded/scores").exists() else []:
        score = load_yaml(score_path)
        score_errors = sorted(Draft202012Validator(load_json(score_schema_path), format_checker=FormatChecker()).iter_errors(score), key=lambda item: list(item.absolute_path))
        for error in score_errors:
            errors.append(f"{score_path.relative_to(root)}: {error.json_path}: {error.message}")
    benchmark_summary = root / "evaluations/results/benchmark-summary.yaml"
    if benchmark_summary.exists():
        availability = load_yaml(root / "evaluations/results/model-availability.yaml").get("models", [])
        selected_count = 1 + int(any(item.get("status") == "AVAILABLE" and item.get("model") != "gpt-5.6-sol" for item in availability[1:]))
        benchmark_records = [item for item in result_records if str(item.get("scenario_id", "")).startswith("YNM-EVAL-")]
        trigger_records = [item for item in result_records if str(item.get("scenario_id", "")).startswith("TRIG-")]
        expected_benchmarks = len(scenario_ids) * 2 * selected_count
        trigger_cases = load_yaml(root / "tests/data/trigger-cases.yaml").get("cases", [])
        expected_triggers = len(trigger_cases) * 5 * selected_count
        if len(benchmark_records) != expected_benchmarks:
            errors.append(f"evaluation results: expected {expected_benchmarks} benchmark records, found {len(benchmark_records)}")
        if len(trigger_records) != expected_triggers:
            errors.append(f"evaluation results: expected {expected_triggers} trigger records, found {len(trigger_records)}")
        score_count = len(list((root / "evaluations/results/blinded/scores").glob("*.yaml")))
        if score_count != expected_benchmarks:
            errors.append(f"evaluation results: expected {expected_benchmarks} blinded scores, found {score_count}")
        run_ids = [item.get("run_id") for item in result_records]
        if len(run_ids) != len(set(run_ids)):
            errors.append("evaluation results: duplicate run IDs")
    return errors


def run(requested_checks: Sequence[str] | None = None) -> list[str]:
    errors: list[str] = []

    checks = list(requested_checks) if requested_checks else DEFAULT_CHECKS
    expanded: set[str] = set(checks)
    if "repository-security-boundary" in expanded:
        expanded.update(REPOSITORY_SECURITY_BOUNDARY_CHECKS)
    normalized: list[str] = sorted(expanded)

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
            ("state/releases/1.3.0/assessment.yaml", "assessment.schema.json", "assessment"),
            ("state/releases/1.3.0/bootstrap.yaml", "bootstrap-receipt.schema.json", None),
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
    if "adversarial-scenarios" in normalized:
        errors.extend(check_adversarial_scenarios())
    if "package-links" in normalized:
        errors.extend(check_package_links())
    if "baseline-integrity" in normalized:
        errors.extend(check_baseline_integrity())
    if "public-sanitization" in normalized:
        errors.extend(check_public_sanitization())
    if "runtime-boundary" in normalized:
        errors.extend(check_runtime_boundary())
    if "workflow-invariants" in normalized:
        errors.extend(check_workflow_invariants())
    if "project-integration-security" in normalized:
        errors.extend(check_project_integration_security())
    if "current-evidence-references" in normalized:
        errors.extend(check_current_evidence_references())
    if "evaluation-artifacts" in normalized:
        errors.extend(check_evaluation_artifacts())

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="append",
        choices=DEFAULT_CHECKS + ["preflight", "cross-platform", "security-boundary", "all", "workflow-invariants"],
        help="Run a single validation check (repeatable).",
    )
    parser.add_argument(
        "--refresh-sanitization-report",
        action="store_true",
        help="Refresh state/releases/<VERSION>/sanitization-report.yaml from tracked text files",
    )
    args = parser.parse_args()

    requested = args.check
    if requested:
        if "all" in requested:
            checks_to_run = DEFAULT_CHECKS
        elif "preflight" in requested:
            checks_to_run = PREFLIGHT_CHECKS
        elif "cross-platform" in requested:
            checks_to_run = CROSS_PLATFORM_CHECKS
        elif "security-boundary" in requested:
            checks_to_run = SECURITY_BOUNDARY_CHECKS
        else:
            checks_to_run = sorted(set(requested))
    else:
        checks_to_run = DEFAULT_CHECKS
    if "workflow-invariants" not in checks_to_run and args.refresh_sanitization_report:
        if "public-sanitization" not in checks_to_run:
            checks_to_run.append("public-sanitization")

    refresh_report = None
    refresh_findings = None
    if args.refresh_sanitization_report:
        refresh_report, refresh_findings = generate_sanitization_report(ROOT)
        write_sanitization_report(ROOT, CURRENT_VERSION, refresh_report, dry_run=False)
        if "public-sanitization" not in checks_to_run:
            checks_to_run = sorted(set(checks_to_run) | {"public-sanitization"})
        if args.check is None:
            print("Refreshed public sanitization report")

    errors = run(checks_to_run)
    if args.refresh_sanitization_report and refresh_report is not None:
        if refresh_findings is not None:
            errors.extend(_compare_sanitization_report(ROOT, refresh_report, findings=refresh_findings))
    if errors:
        print("YNM validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("YNM validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
