#!/usr/bin/env python3
"""Validate release-candidate and published release evidence integrity."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _run_git(args: list[str], cwd: Path, *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, check=check
    )


def _run_git_bytes(args: list[str], cwd: Path, *, check: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, check=check
    )


def _read_version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


@dataclass
class IntegrityCheck:
    errors: list[str]
    warnings: list[str]
    info: list[str] = field(default_factory=list)


def parse_rfc3339_timestamp(raw: str) -> datetime:
    try:
        value = str(raw)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"timestamp must be a string: {raw!r}") from exc

    if not value:
        raise ValueError("timestamp is empty")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("timezone missing")
    return dt.astimezone(timezone.utc)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_resolve_commit(root: Path, ref: str) -> str | None:
    if not ref:
        return None
    value = ref.strip()
    if re.fullmatch(r"[0-9a-fA-F]{40}", value):
        if _run_git(["cat-file", "-e", f"{value}^{{commit}}"], root).returncode != 0:
            return None
        return value.lower()

    if value.startswith("v"):
        result = _run_git(["rev-parse", f"{value}^{{commit}}"], root)
        return result.stdout.strip() if result.returncode == 0 else None

    return None


def _git_show_bytes(root: Path, commit: str, relpath: str) -> bytes:
    result = _run_git_bytes(["show", f"{commit}:{relpath}"], root)
    if result.returncode != 0:
        raise FileNotFoundError(f"{commit}:{relpath}")
    return result.stdout


def _git_show_yaml(root: Path, commit: str, relpath: str) -> dict[str, Any]:
    data = _git_show_bytes(root, commit, relpath)
    return yaml.safe_load(data.decode("utf-8")) or {}


def _validate_file_hashes(
    root: Path,
    commit: str,
    record: dict[str, Any],
    checks: IntegrityCheck,
    *,
    forbidden_release_versions: set[str],
) -> None:
    files = record.get("files")
    if not isinstance(files, dict):
        checks.errors.append("baseline-hashes.yaml: `files` must be a mapping")
        return

    for candidate, expected in files.items():
        if not isinstance(candidate, str):
            checks.errors.append(f"baseline-hashes.yaml: non-string file path {candidate!r}")
            continue

        if not isinstance(expected, str) or len(expected.strip()) != 64:
            checks.errors.append(f"baseline-hashes.yaml: invalid hash for {candidate}")
            continue

        is_forbidden = False
        for forbidden_version in forbidden_release_versions:
            prefix = f"state/releases/{forbidden_version}"
            if candidate == prefix or candidate.startswith(f"{prefix}/"):
                is_forbidden = True
                break
        if is_forbidden:
            checks.errors.append(
                f"baseline-hashes.yaml: candidate-record references forbidden release path {candidate}"
            )
            continue

        try:
            payload = _git_show_bytes(root, commit, candidate)
        except FileNotFoundError:
            checks.errors.append(f"baseline file missing in {commit}: {candidate}")
            continue

        if _hash_bytes(payload) != expected:
            checks.errors.append(f"baseline hash mismatch for {candidate}")


def _check_timestamp_order(
    path: str,
    earlier: datetime | None,
    later: datetime | None,
    checks: IntegrityCheck,
    *,
    now_tolerance: int = 300,
) -> None:
    if earlier and later and later < earlier:
        checks.errors.append(
            f"{path}: timestamp order invalid ({later.isoformat()} before {earlier.isoformat()})"
        )

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
    require_tagged_subject: bool = False,
    tag_ref: str | None = None,
    main_ref: str = "origin/main",
) -> IntegrityCheck:
    root = root or ROOT
    checks = IntegrityCheck(errors=[], warnings=[])

    release_dir = root / "state" / "releases" / version
    if not release_dir.exists():
        checks.errors.append(f"release directory missing: {release_dir.relative_to(root)}")
        return checks

    baseline_path = release_dir / "baseline-hashes.yaml"
    if not baseline_path.exists():
        checks.errors.append(f"missing baseline-hashes.yaml in {release_dir.relative_to(root)}")
        baseline_record: dict[str, Any] = {}
    else:
        try:
            baseline_record = _load_yaml(baseline_path)
        except Exception as exc:  # noqa: BLE001
            checks.errors.append(f"baseline-hashes.yaml malformed: {exc}")
            baseline_record = {}

    captured_raw = baseline_record.get("captured_at") if isinstance(baseline_record, dict) else None
    captured_at: datetime | None = None
    if captured_raw:
        try:
            captured_at = parse_rfc3339_timestamp(captured_raw)
        except Exception as exc:
            checks.errors.append(f"baseline-hashes.yaml captured_at invalid: {exc}")
    else:
        checks.errors.append("baseline-hashes.yaml missing captured_at")

    subject = None
    if isinstance(baseline_record, dict):
        subject = baseline_record.get("baseline_subject") or baseline_record.get("baseline")

    if not isinstance(subject, dict):
        checks.errors.append("baseline-hashes.yaml missing baseline_subject mapping")
        return checks

    baseline_subject = subject
    baseline_version = str(baseline_subject.get("version", "")).strip()
    baseline_tag = str(baseline_subject.get("tag", "")).strip()
    baseline_commit = str(baseline_subject.get("commit", "")).strip()

    if not baseline_version:
        checks.errors.append("baseline-hashes.yaml baseline version missing")
    if not baseline_tag:
        checks.errors.append("baseline-hashes.yaml baseline tag missing")

    baseline_commit = _git_resolve_commit(root, baseline_commit or baseline_tag)
    if not baseline_commit:
        checks.errors.append("baseline-hashes.yaml baseline commit/tag not resolvable")
        return checks

    if baseline_tag:
        if _git_resolve_commit(root, baseline_tag) != baseline_commit:
            checks.errors.append("baseline-hashes.yaml baseline tag does not resolve to subject commit")

    baseline_tree = str(baseline_subject.get("tree", "")).strip()
    if baseline_tree:
        if len(baseline_tree) != 40:
            checks.errors.append("baseline-hashes.yaml baseline tree is not full SHA")
        else:
            tree_result = _run_git(["rev-parse", f"{baseline_commit}^{{tree}}"], root)
            if tree_result.returncode != 0:
                checks.errors.append("unable to resolve baseline commit tree")
            elif tree_result.stdout.strip() != baseline_tree:
                checks.errors.append("baseline-hashes.yaml tree does not match baseline commit tree")

    # Ensure current release evidence exists in the working tree.
    required_current = [
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
    ]
    for required in required_current:
        if not (release_dir / required).exists():
            checks.errors.append(f"missing required release evidence: state/releases/{version}/{required}")

    # Candidate baseline-hash records should describe historical artifacts only.
    _validate_file_hashes(
        root,
        baseline_commit,
        baseline_record,
        checks,
        forbidden_release_versions={version},
    )

    if baseline_version:
        historical_path = f"state/releases/{baseline_version}/baseline-hashes.yaml"
        try:
            historical_record = _git_show_yaml(root, baseline_commit, historical_path)
        except FileNotFoundError:
            checks.errors.append(f"unable to load historical baseline record from {baseline_commit}:{historical_path}")
        else:
            _validate_file_hashes(
                root,
                baseline_commit,
                historical_record,
                checks,
                forbidden_release_versions={version},
            )

    # Release evidence content checks.
    final_assessment_path = release_dir / "final-assessment.yaml"
    if final_assessment_path.exists():
        final_assessment = _load_yaml(final_assessment_path)
        block = final_assessment.get("final_assessment", {}) if isinstance(final_assessment, dict) else {}
        if not isinstance(block, dict):
            checks.errors.append("final-assessment.yaml: final_assessment root object malformed")
        else:
            version_decision = str(block.get("version_decision", "")).strip()
            if version_decision and version_decision != version:
                checks.errors.append(
                    f"final-assessment.yaml: version_decision ({version_decision}) does not match release version ({version})"
                )
            evaluated_at_raw = block.get("evaluated_at")
            if not evaluated_at_raw:
                checks.errors.append("final-assessment.yaml: evaluated_at missing")
            else:
                try:
                    evaluated_at = parse_rfc3339_timestamp(evaluated_at_raw)
                    _check_timestamp_order(
                        "final-assessment.yaml",
                        captured_at,
                        evaluated_at,
                        checks,
                        now_tolerance= future_tolerance_seconds,
                    )
                except Exception as exc:
                    checks.errors.append(f"final-assessment.yaml evaluated_at invalid: {exc}")

            disposition = str(block.get("final_disposition") or block.get("disposition", "")).strip()
            if disposition not in {"YES", "NO", "MAYBE"}:
                checks.errors.append("final-assessment.yaml: final_disposition must be YES/NO/MAYBE")

            for ref in block.get("evidence", []) if isinstance(block.get("evidence"), list) else []:
                evidence_path = root / str(ref)
                if not evidence_path.exists():
                    checks.errors.append(f"final-assessment.yaml evidence missing: {ref}")

    assessment_path = release_dir / "assessment.yaml"
    if assessment_path.exists():
        assessment = _load_yaml(assessment_path)
        if not isinstance(assessment, dict) or "assessment" not in assessment:
            checks.errors.append("assessment.yaml: missing `assessment`")
        else:
            assessment_block = assessment.get("assessment", {})
            publication = assessment_block.get("publication", {}) if isinstance(assessment_block, dict) else {}
            if isinstance(publication, dict):
                publication_version = str(publication.get("version", "")).strip()
                if publication_version and publication_version != version:
                    checks.errors.append(
                        f"assessment.yaml: publication.version {publication_version} does not match {version}"
                    )

                status = publication.get("status")
                tag = publication.get("tag")
                verification_basis = str(publication.get("verification_basis_commit", "")).strip()
                verified_at_raw = publication.get("verified_at")
                if status == "VERIFIED_PUBLIC":
                    if not tag:
                        checks.errors.append("assessment.yaml: VERIFIED_PUBLIC without tag")
                    if require_publication_commit_tree and tag:
                        resolved_tag = _git_resolve_commit(root, tag)
                        if not resolved_tag:
                            checks.errors.append(f"assessment.yaml: tag {tag} not resolvable")

                if verification_basis:
                    if _git_resolve_commit(root, verification_basis) is None:
                        checks.errors.append(f"assessment.yaml: basis commit missing: {verification_basis}")
                    if tag:
                        tag_commit = _git_resolve_commit(root, tag)
                        if tag_commit:
                            ancestry = _run_git(["merge-base", "--is-ancestor", verification_basis, tag_commit], root)
                            if ancestry.returncode == 1:
                                checks.errors.append(
                                    f"assessment.yaml: basis {verification_basis} is not ancestor of {tag_commit}"
                                )
                            elif ancestry.returncode not in (0, 1):
                                checks.warnings.append(
                                    f"assessment.yaml: unable to verify ancestry for {verification_basis} -> {tag_commit}"
                                )

                if verified_at_raw:
                    try:
                        verified_at = parse_rfc3339_timestamp(verified_at_raw)
                        _check_timestamp_order(
                            "assessment.yaml",
                            captured_at,
                            verified_at,
                            checks,
                            now_tolerance=future_tolerance_seconds,
                        )
                    except Exception as exc:
                        checks.errors.append(f"assessment.yaml: verified_at invalid: {exc}")

    gates_path = release_dir / "gates.yaml"
    if gates_path.exists():
        gates = _load_yaml(gates_path)
        for index, gate in enumerate(gates.get("gates", []) if isinstance(gates, dict) else [], start=1):
            if not isinstance(gate, dict):
                checks.errors.append(f"gates.yaml gate #{index} malformed")
                continue
            if gate.get("disposition") not in {"YES", "NO", "MAYBE"}:
                checks.errors.append(f"gates.yaml gate {gate.get('name', index)} has invalid disposition")

    review_plan_path = release_dir / "review-plan.yaml"
    runs_path = release_dir / "runs.yaml"
    if review_plan_path.exists() and runs_path.exists():
        plan_doc = _load_yaml(review_plan_path)
        runs_doc = _load_yaml(runs_path)
        mode = (plan_doc.get("review_plan") or {}).get("persistence_mode")
        runs = runs_doc.get("runs", []) if isinstance(runs_doc, dict) else []
        successful_persistent = any(
            isinstance(item, dict)
            and item.get("persistence_status") == "PERSISTENT"
            and isinstance(item.get("delivery"), dict)
            and item["delivery"].get("persistence_attempted") is True
            and item["delivery"].get("persistence_outcome") == "SUCCEEDED"
            for item in runs
        )
        if mode == "STATELESS" and successful_persistent:
            checks.errors.append("review-plan.yaml is STATELESS but runs.yaml records successful persistent state")

    corrections_dir = release_dir / "corrections"
    if corrections_dir.exists():
        for path in sorted(corrections_dir.glob("*.yaml")):
            correction = _load_yaml(path)
            for required in ["subject", "original_record", "evidence", "disposition"]:
                if required not in correction:
                    checks.errors.append(f"correction {path.relative_to(root)} missing required field {required}")
            disposition = str(correction.get("disposition", "")).strip()
            if disposition not in {"YES", "NO", "MAYBE"}:
                checks.errors.append(f"correction {path.relative_to(root)} has invalid disposition")

    if require_tagged_subject:
        expected_tag = f"v{version}"
        selected_tag = tag_ref or expected_tag
        if selected_tag != expected_tag:
            checks.errors.append(f"tag ref {selected_tag} does not match expected {expected_tag}")
        tag_commit = _git_resolve_commit(root, selected_tag)
        if not tag_commit:
            checks.errors.append(f"tag {selected_tag} does not resolve to a commit")
        else:
            tree_result = _run_git(["rev-parse", f"{tag_commit}^{{tree}}"], root)
            if tree_result.returncode != 0:
                checks.errors.append(f"unable to resolve tree for tag {selected_tag}")
            ancestry = _run_git(["merge-base", "--is-ancestor", tag_commit, main_ref], root)
            if ancestry.returncode == 1:
                checks.errors.append(f"tagged commit {tag_commit} is not reachable from {main_ref}")
            elif ancestry.returncode not in (0, 1):
                checks.errors.append(f"unable to verify tagged commit reachability from {main_ref}")
            if tree_result.returncode == 0:
                checks.info.append(
                    f"tagged subject: tag={selected_tag} commit={tag_commit} tree={tree_result.stdout.strip()}"
                )

        publication_path = release_dir / "publication.yaml"
        if not publication_path.exists():
            checks.errors.append("publication.yaml missing for tagged-subject validation")
        else:
            publication_doc = _load_yaml(publication_path)
            publication = publication_doc.get("publication", {})
            if not isinstance(publication, dict):
                checks.errors.append("publication.yaml: publication object malformed")
            else:
                if str(publication.get("version", "")) != version:
                    checks.errors.append("publication.yaml version does not match tagged release")
                if publication.get("publication_readiness") != "YES":
                    checks.errors.append("publication.yaml is not ready for publication")
                if publication.get("status") not in {"READY_FOR_TAG", "PUBLISHED"}:
                    checks.errors.append("publication.yaml status must be READY_FOR_TAG or PUBLISHED")
                if publication.get("publication_authorization") != "AUTHORIZED_BY_HUMAN":
                    checks.errors.append("publication.yaml requires explicit human publication authorization")

    return checks


def run(
    version: str,
    root: Path | None = None,
    future_tolerance_seconds: int = 300,
    require_publication_commit_tree: bool = False,
    require_tagged_subject: bool = False,
    tag_ref: str | None = None,
    main_ref: str = "origin/main",
) -> list[str]:
    result = validate_release_integrity(
        version,
        root=root,
        future_tolerance_seconds=future_tolerance_seconds,
        require_publication_commit_tree=require_publication_commit_tree,
        require_tagged_subject=require_tagged_subject,
        tag_ref=tag_ref,
        main_ref=main_ref,
    )
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
    parser.add_argument("--require-tagged-subject", action="store_true", help="require a human-finalized tag subject")
    parser.add_argument("--tag-ref", default=None, help="tag ref to validate (defaults to v<release>)")
    parser.add_argument("--main-ref", default="origin/main", help="mainline ref that must contain the tagged commit")
    args = parser.parse_args()

    release = args.release or _read_version(Path(args.root))
    messages = run(
        release,
        root=Path(args.root),
        future_tolerance_seconds=args.tolerance,
        require_publication_commit_tree=args.require_publication_tree,
        require_tagged_subject=args.require_tagged_subject,
        tag_ref=args.tag_ref,
        main_ref=args.main_ref,
    )

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
