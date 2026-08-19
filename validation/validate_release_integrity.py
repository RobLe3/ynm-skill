#!/usr/bin/env python3
"""Validate release-candidate and published release evidence integrity."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read_version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


@dataclass
class IntegrityCheck:
    errors: list[str]
    warnings: list[str]


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_rfc3339_timestamp(raw: str) -> datetime:
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


def check_file_hash_set(base: Path, base_record: dict[str, Any], checks: IntegrityCheck) -> None:
    files = base_record.get("files")
    if not isinstance(files, dict):
        checks.errors.append("baseline-hashes.yaml: `files` must be a mapping")
        return
    for candidate, expected in files.items():
        path = base / candidate
        if not path.exists():
            checks.errors.append(f"baseline file missing: {candidate}")
            continue
        if not isinstance(expected, str):
            checks.errors.append(f"baseline hash not a string for {candidate}")
            continue
        if _hash(path) != expected:
            checks.errors.append(f"baseline hash mismatch for {candidate}")


def check_timestamp_order(path: str, earlier: datetime | None, later: datetime | None, checks: IntegrityCheck, *, now_tolerance: int = 300) -> None:
    if earlier and later and later < earlier:
        checks.errors.append(f"{path}: timestamp order invalid ({later.isoformat()} before {earlier.isoformat()})")

    if later:
        now = datetime.now(timezone.utc)
        delta = later - now
        if delta.total_seconds() > now_tolerance:
            checks.warnings.append(f"{path}: timestamp appears in the future ({later.isoformat()})")


def validate_release_integrity(
    version: str,
    *,
    root: Path | None = None,
    future_tolerance_seconds: int = 300,
    require_publication_commit_tree: bool = False,
) -> IntegrityCheck:
    root = root or ROOT
    checks = IntegrityCheck(errors=[], warnings=[])

    release_dir = root / "state" / "releases" / version
    if not release_dir.exists():
        checks.errors.append(f"release directory missing: {release_dir.relative_to(root)}")
        return checks

    # 1) Baseline evidence.
    try:
        baseline = _load_yaml(release_dir / "baseline-hashes.yaml")
    except FileNotFoundError:
        checks.errors.append(f"missing baseline-hashes.yaml in {release_dir.relative_to(root)}")
        baseline = {}

    captured_at_raw = baseline.get("captured_at") if isinstance(baseline, dict) else None
    captured_at: datetime | None = None
    if captured_at_raw:
        try:
            captured_at = parse_rfc3339_timestamp(captured_at_raw)
        except Exception as exc:
            checks.errors.append(f"baseline-hashes.yaml captured_at invalid: {exc}")
    else:
        checks.errors.append("baseline-hashes.yaml missing captured_at")

    if baseline:
        if (
            not isinstance(baseline.get("baseline"), str)
            or not baseline["baseline"]
        ) and (
            not isinstance(baseline.get("baseline_subject"), dict)
            or not baseline["baseline_subject"].get("version")
        ):
            checks.warnings.append("baseline-hashes.yaml baseline label missing or empty")

    check_file_hash_set(root, baseline if isinstance(baseline, dict) else {}, checks)

    # 2) Mandatory release evidence files.
    final_assessment_path = release_dir / "final-assessment.yaml"
    assessment_path = release_dir / "assessment.yaml"
    review_plan_path = release_dir / "review-plan.yaml"
    gates_path = release_dir / "gates.yaml"
    for required in [final_assessment_path, assessment_path, review_plan_path, gates_path]:
        if not required.exists():
            checks.errors.append(f"missing required release evidence: {required.relative_to(root)}")

    # 3) Final-assessment and publication metadata checks.
    final_assessment = {}
    if final_assessment_path.exists():
        final_assessment = _load_yaml(final_assessment_path)
        if not isinstance(final_assessment.get("final_assessment"), dict):
            checks.errors.append("final-assessment.yaml: final_assessment root object missing")
        else:
            block = final_assessment["final_assessment"]
            if block.get("version"):
                if block.get("version") != version:
                    checks.errors.append(
                        f"final-assessment.yaml: version ({block.get('version')}) does not match release version ({version})"
                    )
            elif block.get("version_decision") not in (None, version):
                checks.errors.append(
                    f"final-assessment.yaml: version_decision ({block.get('version_decision')}) does not match release version ({version})"
                )
            evaluated_at_raw = block.get("evaluated_at")
            if not evaluated_at_raw:
                checks.errors.append("final-assessment.yaml: evaluated_at missing")
            else:
                try:
                    evaluated_at = parse_rfc3339_timestamp(evaluated_at_raw)
                    check_timestamp_order("final-assessment.yaml", captured_at, evaluated_at, checks, now_tolerance=future_tolerance_seconds)
                except Exception as exc:
                    checks.errors.append(f"final-assessment.yaml evaluated_at invalid: {exc}")
            disposition = block.get("final_disposition") or block.get("disposition")
            if disposition not in {"YES", "NO", "MAYBE"}:
                checks.errors.append("final-assessment.yaml: final_disposition must be YES/NO/MAYBE")
            evidence_refs = block.get("evidence", []) if isinstance(block.get("evidence"), list) else []
            for ref in evidence_refs:
                candidate = root / str(ref)
                if not candidate.exists():
                    checks.errors.append(f"final-assessment.yaml evidence missing: {ref}")

    # 4) Assessment claims and publication integrity.
    assessment_record = {}
    if assessment_path.exists():
        assessment_record = _load_yaml(assessment_path)
        if not isinstance(assessment_record, dict):
            checks.errors.append("assessment.yaml malformed")
        else:
            if "assessment" not in assessment_record:
                checks.errors.append("assessment.yaml: missing `assessment`")
            elif not isinstance(assessment_record.get("assessment"), dict):
                checks.errors.append("assessment.yaml: `assessment` must be a mapping")

            publication = assessment_record.get("assessment", {}).get("publication") if isinstance(assessment_record.get("assessment"), dict) else None
            if isinstance(publication, dict):
                publication_version = str(publication.get("version", "")).strip()
                if publication_version and publication_version != version:
                    checks.errors.append(
                        f"assessment.yaml: publication.version {publication_version} does not match {version}"
                    )

                status = publication.get("status")
                tag = publication.get("tag")
                basis = publication.get("verification_basis_commit")
                verified_at_raw = publication.get("verified_at")
                if status == "VERIFIED_PUBLIC":
                    if not tag:
                        checks.errors.append("assessment.yaml: VERIFIED_PUBLIC without tag")
                if tag:
                    tag_result = _run_git(["rev-parse", f"{tag}^{{commit}}"], root)
                    if tag_result.returncode != 0:
                        checks.errors.append(f"assessment.yaml: tag '{tag}' cannot be resolved")
                    else:
                        tag_commit = tag_result.stdout.strip()
                        if not _run_git(["cat-file", "-e", f"{tag_commit}^{{commit}}"], root).returncode == 0:
                            checks.errors.append(f"assessment.yaml: resolved tag commit invalid: {tag_commit}")
                elif status == "VERIFIED_PUBLIC":
                    checks.errors.append("assessment.yaml: VERIFIED_PUBLIC requires tag")

                if basis:
                    if _run_git(["cat-file", "-e", f"{basis}^{{commit}}"], root).returncode != 0:
                        checks.errors.append(f"assessment.yaml: basis commit missing: {basis}")
                    if tag:
                        tag_result = _run_git(["rev-parse", f"{tag}^{{commit}}"], root)
                        if tag_result.returncode == 0:
                            tag_commit = tag_result.stdout.strip()
                            ancestry = _run_git(["merge-base", "--is-ancestor", basis, tag_commit], root)
                            if ancestry.returncode == 0:
                                pass
                            elif ancestry.returncode == 1:
                                checks.errors.append(f"assessment.yaml: basis {basis} is not ancestor of {tag_commit}")
                            else:
                                checks.warnings.append(f"assessment.yaml: unable to verify ancestry for {basis} -> {tag_commit}")

                if status == "VERIFIED_PUBLIC" and require_publication_commit_tree and basis:
                    tag_result = _run_git(["rev-parse", f"{tag}^{{commit}}"], root)
                    if tag_result.returncode == 0:
                        tree_result = _run_git(["rev-parse", f"{tag_result.stdout.strip()}^{{tree}}"], root)
                        if tree_result.returncode != 0:
                            checks.errors.append(f"assessment.yaml: unable to resolve tree for tag commit {tag}")

                try:
                    if verified_at_raw:
                        verified_at = parse_rfc3339_timestamp(verified_at_raw)
                        check_timestamp_order("assessment.yaml", captured_at, verified_at, checks, now_tolerance=future_tolerance_seconds)
                except Exception as exc:
                    checks.errors.append(f"assessment.yaml: verified_at invalid: {exc}")

    # 5) Gates evidence references
    if gates_path.exists():
        gates = _load_yaml(gates_path)
        for idx, gate in enumerate(gates.get("gates", []) if isinstance(gates, dict) else [], start=1):
            if not isinstance(gate, dict):
                checks.errors.append(f"gates.yaml gate #{idx} malformed")
                continue
            if gate.get("disposition") not in {"YES", "NO", "MAYBE"}:
                checks.errors.append(f"gates.yaml gate {gate.get('name', idx)} has invalid disposition")

    # 6) Appended-only correction evidence.
    corrections_dir = release_dir / "corrections"
    if corrections_dir.exists():
        for path in sorted(corrections_dir.glob("*.yaml")):
            try:
                correction = _load_yaml(path)
            except Exception:
                checks.errors.append(f"unreadable correction file {path.relative_to(root)}")
                continue
            for required in ["subject", "original_record", "evidence", "disposition"]:
                if required not in correction:
                    checks.errors.append(f"correction {path.relative_to(root)} missing required field {required}")
            disposition = correction.get("disposition")
            if disposition and disposition not in {"YES", "NO", "MAYBE"}:
                checks.errors.append(f"correction {path.relative_to(root)} has invalid disposition")

    if final_assessment.get("final_assessment", {}).get("proposition") and assessment_record.get("assessment", {}).get("proposition"):
        if isinstance(final_assessment["final_assessment"].get("proposition"), str) and isinstance(assessment_record["assessment"].get("proposition"), str):
            if final_assessment["final_assessment"].get("proposition") == "":
                checks.errors.append("final-assessment.yaml: empty proposition")

    return checks


def run(version: str, root: Path | None = None, future_tolerance_seconds: int = 300) -> list[str]:
    result = validate_release_integrity(version, root=root, future_tolerance_seconds=future_tolerance_seconds)
    messages: list[str] = []
    messages.extend(f"{issue}" for issue in result.errors)
    messages.extend(f"warning: {issue}" for issue in result.warnings)
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", default=None, help="release version directory under state/releases")
    parser.add_argument("--root", default=str(ROOT), help="repository root")
    parser.add_argument("--tolerance", type=int, default=300, help="future-timestamp tolerance seconds")
    parser.add_argument("--strict", action="store_true", help="fail on warnings")
    parser.add_argument(
        "--require-publication-tree",
        action="store_true",
        help="require publication tag to resolve a commit tree",
    )
    args = parser.parse_args()

    release = args.release or _read_version(Path(args.root))
    messages = run(release, root=Path(args.root), future_tolerance_seconds=args.tolerance)

    if messages:
        print("YNM release-integrity validation issues:")
        for item in messages:
            print(f"- {item}")

    errors_only = [item for item in messages if not item.startswith("warning:")]
    if args.strict and any(item.startswith("warning:") for item in messages):
        return 1
    return 0 if not errors_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
