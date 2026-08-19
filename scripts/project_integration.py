#!/usr/bin/env python3
"""Project discovery and bounded initialization helpers for YNM project integration."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

BEGIN_MARKER = "<!-- YNM:BEGIN -->"
END_MARKER = "<!-- YNM:END -->"
FORBIDDEN_PATH_SEGMENTS = {".git", ".github"}
MANAGED_BY_KEY = "ynm"
ALLOWED_ROOT_SEGMENTS = {".ynm"}
PERSISTENCE_OUTCOMES = {"NOT_AUTHORIZED", "NOT_ATTEMPTED", "SUCCEEDED", "FAILED", "ROLLED_BACK", "PARTIALLY_ROLLED_BACK"}

ROLE_DEFINITION = {
    "project_entry": ["README.md"],
    "agent_guidance": ["AGENTS.md", "MEMORY.md"],
    "project_context": ["CONTRIBUTING.md", "VERSIONING.md", "ROADMAP.md", "ARCHITECTURE.md", "DESIGN.md", "spec"],
    "implementation_contracts": ["spec", "contracts", "docs/spec", "specification"],
    "adoption_guidance": ["INSTALL.md", "USAGE.md", "docs", "getting-started", "README.md"],
    "operational_guidance": ["OPERATIONS.md", "operations.md", "docs/operations"],
    "security_guidance": ["SECURITY.md", "SECURITY", "docs/security"],
    "release_history": ["CHANGELOG.md", "RELEASES.md", "RELEASE.md", "docs/changelog"],
    "version_policy": ["VERSIONING.md", "RELEASES.md", "VERSION"],
    "decision_history": ["adr", "adrs", "docs/adr", "docs/adrs", "decisions"],
    "ynm_configuration": [".ynm/config.yaml", ".ynm/config.yml", "ynm.config.yaml"],
    "ynm_state": [".ynm/state", ".ynm"],
}


class IntegrationError(ValueError):
    """Raised for unsafe integration operations or unresolved ownership conflicts."""

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message)
        self.message = message
        self.path = path


@dataclass(frozen=True)
class Operation:
    path: Path
    kind: str
    content: str
    reason: str = ""


def now_iso8601() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def has_control_chars(value: str) -> bool:
    return "\0" in value or any(ord(ch) < 32 and ch not in "\t\n\r" for ch in value)


def is_windows_drive_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", value))


def is_unc_path(value: str) -> bool:
    return value.startswith("\\\\") or value.startswith("//")


def normalize_root_path(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise IntegrationError("state root cannot be empty")
    if has_control_chars(candidate):
        raise IntegrationError("state root contains control characters")
    if candidate in {".", ".."}:
        raise IntegrationError("state root cannot be '.' or '..'")
    if candidate.startswith(("/", "\\")) or is_windows_drive_path(candidate) or is_unc_path(candidate):
        raise IntegrationError("state root must be project-relative")
    parts = candidate.replace("\\", "/").split("/")
    if any(part in {".", ".."} for part in parts):
        raise IntegrationError("state root must not include path traversal")
    return "/".join(parts).rstrip("/")


def _rel(project_root: Path, path: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ensure_root(path: Path, root: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise IntegrationError(f"path outside project root: {path}", str(path)) from exc


def _path_contains_forbidden_segments(relative_candidate: Path) -> bool:
    return any(part in FORBIDDEN_PATH_SEGMENTS for part in relative_candidate.parts)


def validate_candidate_path(root: Path, candidate: str) -> Path:
    candidate = candidate.strip()
    if not candidate:
        raise IntegrationError("target path cannot be empty")
    if has_control_chars(candidate):
        raise IntegrationError("target path contains control characters", candidate)
    if candidate in {".", ".."}:
        raise IntegrationError("target path cannot be '.' or '..'", candidate)
    if Path(candidate).is_absolute() or is_windows_drive_path(candidate) or is_unc_path(candidate):
        raise IntegrationError("absolute and UNC paths are not allowed", candidate)
    normalized = candidate.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    if any(part in {".", ".."} for part in parts):
        raise IntegrationError("target path contains path traversal", candidate)
    relative = Path(*parts)
    if _path_contains_forbidden_segments(relative):
        raise IntegrationError("target path contains reserved project directory", candidate)
    if relative == Path("."):
        raise IntegrationError("target path cannot be project root", candidate)
    return (root / relative).resolve()


def _resolve_if_present(path: Path) -> Path:
    if path.exists() and path.is_symlink():
        return path.resolve()
    return path


def _component_targets_within_root(root: Path, target: Path) -> None:
    # Check every resolved component to avoid parent traversal through symlinks.
    target_relative = target.relative_to(root)
    cursor = root
    for part in target_relative.parts:
        cursor = cursor / part
        if cursor.exists() and cursor.is_symlink():
            resolved = cursor.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise IntegrationError(f"symlink component escapes project: {cursor}", str(cursor)) from exc
    if target.exists() and target.is_symlink():
        resolved = target.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise IntegrationError(f"final target symlink escapes project: {target}", str(target)) from exc


def _safe_candidate_target(root: Path, candidate: str) -> Path:
    target = validate_candidate_path(root, candidate)
    _ensure_root(target, root)
    _component_targets_within_root(root, target)
    return target


def load_structured_text(path: Path) -> Any | None:
    text = _read_text(path).strip()
    if not text:
        return None
    try:
        return yaml.safe_load(text)
    except Exception:
        return None


def is_ynm_owned_document(document: Any) -> bool:
    return isinstance(document, dict) and document.get("managed_by") == MANAGED_BY_KEY


def parse_ynm_owned_yaml(path: Path) -> bool:
    return is_ynm_owned_document(load_structured_text(path))


def parse_marked_agents_section(text: str) -> str:
    return f"{BEGIN_MARKER}\n{text.rstrip()}\n{END_MARKER}"


def parse_agents_section_state(path: Path) -> tuple[str, str | None]:
    try:
        original = _read_text(path)
    except FileNotFoundError:
        return "ABSENT", None
    if not original:
        return "UNKNOWN", "empty agent file"
    if path.is_dir():
        return "CONFLICT", "AGENTS path is a directory"

    begin_count = original.count(BEGIN_MARKER)
    end_count = original.count(END_MARKER)
    if begin_count == 0 and end_count == 0:
        if original.strip():
            return "UNKNOWN", "file exists without YNM section"
        return "ABSENT", None
    if begin_count != 1 or end_count != 1:
        return "CONFLICT", "malformed YNM markers"
    if original.find(BEGIN_MARKER) > original.find(END_MARKER):
        return "CONFLICT", "reversed markers"
    if original.count(BEGIN_MARKER + "\n") != 1:
        return "CONFLICT", "duplicate marker formatting"

    start = original.index(BEGIN_MARKER)
    end = original.index(END_MARKER, start) + len(END_MARKER)
    managed = original[start:end]
    if BEGIN_MARKER not in managed or END_MARKER not in managed:
        return "CONFLICT", "missing managed boundary"

    return "OWNED", None


def agents_section_body(state_root: str) -> str:
    return "\n".join(
        [
            BEGIN_MARKER,
            "## YNM Project Review",
            "",
            "- Load YNM: `YNM`",
            "- Read-only review is the default invocation mode.",
            f"- YNM state is recorded in `{state_root}/` when explicitly authorized.",
            "- Project files are read for review evidence; mutation requires explicit scope authorization.",
            "- See project integration records for current review constraints.",
            END_MARKER,
            "",
        ]
    )


def merge_agents_update(path: Path, state_root: str) -> Operation:
    existing = _read_text(path).rstrip("\n")
    body = agents_section_body(state_root).rstrip("\n")
    if not existing:
        content = body + "\n"
    else:
        content = f"{existing}\n\n{body}\n"
    return Operation(path=path, kind="update", content=content, reason="append bounded YNM AGENTS section")


def classify_roles(project_root: Path) -> list[dict[str, Any]]:
    roles: list[dict[str, Any]] = []
    for role, candidates in ROLE_DEFINITION.items():
        artifacts = []
        role_status = "UNKNOWN"
        for candidate in candidates:
            path = project_root / candidate
            if not path.exists():
                continue
            if path.is_dir():
                evidence = ["candidate directory match"]
                status = "CANDIDATE"
            else:
                evidence = ["candidate file match"]
                status = "CONFIRMED"
            artifacts.append({"path": candidate, "status": status, "evidence": evidence})
            role_status = "CONFIRMED" if status == "CONFIRMED" else "CANDIDATE"

        roles.append({
            "role": role,
            "status": role_status,
            "artifacts": artifacts,
            "evidence": artifacts,
        })
    return roles


def discover_context(project_root: Path, state_root: str) -> dict[str, Any]:
    return {
        "schema_version": "ynm-project-context.v1",
        "project": {
            "name": project_root.name,
            "root": ".",
        },
        "documentation_roles": classify_roles(project_root),
        "ynm_state_location": state_root,
        "persistence_mode": "PERSISTENT" if (project_root / state_root).exists() else "STATELESS",
        "discovered_at": now_iso8601(),
    }


def desired_state_payload(context: dict[str, Any], state_root: str) -> dict[str, str]:
    project_context = {
        **context,
        "managed_by": "ynm",
    }
    project_config = {
        "managed_by": "ynm",
        "schema_version": "ynm-project-config.v1",
        "ynm": {
            "persistence": True,
            "state_location": state_root,
        },
        "review": {"default_mode": "read_only"},
        "loops": {
            "architecture": "auto",
            "implementation": "auto",
            "adoption": "auto",
            "maintenance": "auto",
            "disposition": "auto",
        },
        "scope": {"include": [], "exclude": []},
        "authority": {
            "mutation_requires_explicit_authorization": True,
        },
    }
    readme = """# YNM project state\n\nThis directory contains YNM-owned review configuration and longitudinal state for this project.\nLoading or reviewing with YNM remains read-only by default.\nProject artifacts may be changed only under separate, explicit authorization.\n\n- `project.yaml` records discovered context and documentation-role mappings.\n- `config.yaml` controls project-local execution preferences; it cannot redefine YNM semantics.\n- `state/findings.yaml` is the current finding projection.\n- `state/events.jsonl` preserves append-oriented history.\n- `state/receipts/` records bootstrap and review outcomes.\n\nRemoving this directory detaches persistent YNM state and loses review continuity.\n"""

    return {
        f"{state_root}/README.md": readme,
        f"{state_root}/project.yaml": yaml.safe_dump(project_context, sort_keys=False).strip() + "\n",
        f"{state_root}/config.yaml": yaml.safe_dump(project_config, sort_keys=False).strip() + "\n",
        f"{state_root}/state/findings.yaml": "schema_version: ynm-findings.v1\nfindings: []\n",
        f"{state_root}/state/events.jsonl": "",
        f"{state_root}/state/receipts/.keep": "",
    }


def _file_action_for(path: Path, expected: str, root: Path) -> tuple[str, str] | None:
    if path.exists():
        if path.is_dir():
            return "CONFLICT", f"expected file but found directory at {_rel(root, path)}"
        existing_text = _read_text(path)
        if parse_ynm_owned_yaml(path) and path.name != "AGENTS.md":
            return "REUSE", "managed and retained"
        if existing_text == expected:
            return "REUSE", "content already current"
        if path.name == "AGENTS.md":
            status, reason = parse_agents_section_state(path)
            if status == "OWNED":
                return "REUSE", "managed section already present"
            if reason:
                return "UPDATE", "append bounded section"
            return "UPDATE", "append bounded section"
        if "managed_by:" in existing_text:
            return "CONFLICT", "foreign ownership marker present"
        return "CONFLICT", "ownership unknown"
    return "CREATE", "missing"


def _plan_for(root: Path, desired: dict[str, str]) -> tuple[list[Operation], list[Operation], list[str], list[str]]:
    planned: list[Operation] = []
    unchanged: list[Operation] = []
    created: list[str] = []
    updated: list[str] = []
    conflicts: list[str] = []

    for relative, content in desired.items():
        try:
            target = _safe_candidate_target(root, relative)
            target_parent = target.parent
            if target_parent.exists() and target_parent.is_file():
                conflicts.append(relative)
                continue
            if target.exists() and target.is_symlink():
                resolved = target.resolve()
                try:
                    resolved.relative_to(root)
                except ValueError:
                    conflicts.append(relative)
                    continue
        except IntegrationError as exc:
            conflicts.append(str(exc.path or relative))
            continue

        action, _ = _file_action_for(target, content, root)
        if action == "CONFLICT":
            conflicts.append(relative)
            continue
        if action == "REUSE":
            unchanged.append(Operation(path=target, kind="reuse", content=content, reason="existing managed file unchanged"))
        elif action in {"CREATE", "UPDATE"}:
            op = Operation(path=target, kind=action.lower(), content=content, reason="YNM scaffold")
            planned.append(op)
            if action == "CREATE":
                created.append(relative)
            else:
                updated.append(relative)

    return planned, unchanged, created, updated, conflicts


def build_bootstrap_receipt(
    *,
    project: Path,
    planned: list[Operation],
    unchanged: list[Operation],
    conflicts: list[str],
    state_root: str,
    apply: bool,
    writes_attempted: bool,
    writes_completed: bool,
    persistence_outcome: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    planned_entries = []
    for op in unchanged:
        planned_entries.append({
            "path": _rel(project, op.path),
            "action": op.kind,
            "status": "REUSED",
            "reason": op.reason,
        })
    for op in planned:
        planned_entries.append({
            "path": _rel(project, op.path),
            "action": op.kind,
            "status": "COMPLETED" if writes_completed and apply else "PLANNED",
            "reason": op.reason,
        })

    for item in sorted(set(conflicts)):
        if not any(entry["path"] == item for entry in planned_entries):
            planned_entries.append({"path": item, "action": "BLOCK", "status": "CONFLICT", "reason": "ownership or path safety"})

    return {
        "schema_version": "ynm-bootstrap-receipt.v1",
        "execution_id": plan_id(project, state_root),
        "project": project.name,
        "mode": "INITIALIZE",
        "execution_status": "SUCCEEDED" if writes_completed else ("FAILED" if writes_attempted else ("BLOCKED" if conflicts else "COMPLETED")),
        "discovered_artifacts": sorted(context.get("documentation_roles", []), key=lambda item: item.get("role", "")),
        "reused_artifacts": [entry["path"] for entry in planned_entries if entry.get("status") == "REUSED"],
        "created_artifacts": sorted({entry["path"] for entry in planned_entries if entry.get("action") == "create"}),
        "updated_artifacts": sorted({entry["path"] for entry in planned_entries if entry.get("action") == "update"}),
        "untouched_conflicting_artifacts": sorted(set(conflicts)),
        "ynm_state_location": state_root,
        "persistence_mode": "PERSISTENT" if apply and writes_completed else "STATELESS",
        "mutation_authorization": "AUTHORIZED" if apply else "REQUIRES_HUMAN",
        "unresolved_questions": ["Resolve ownership or marker conflicts before initialization"] if conflicts else [],
        "planned_operations": planned_entries,
        "writes_attempted": writes_attempted,
        "writes_completed": writes_completed,
        "persistence_outcome": persistence_outcome,
        "created_at": now_iso8601(),
    }


def plan_id(project: Path, state_root: str) -> str:
    seed = f"{project.resolve()}\0{state_root}\0ynm-bootstrap".encode()
    return "YNM-BOOT-" + hashlib.sha256(seed).hexdigest()[:12].upper()


def _flush_handle(handle) -> None:
    handle.flush()
    os.fsync(handle.fileno())


def safe_replace(path: Path, content: str) -> tuple[bool, str]:
    temp_suffix = ".ynm-tmp"
    temp_path = path.with_suffix(path.suffix + temp_suffix)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.write(content)
            _flush_handle(handle)
        os.replace(str(temp_path), str(path))
        return True, "SUCCEEDED"
    except Exception as exc:  # pragma: no cover - exercised indirectly
        return False, f"FAILED: {exc}"


def apply_operations(project_root: Path, operations: list[Operation], context: str) -> tuple[str, list[dict[str, Any]]]:
    backups: dict[Path, Path] = {}
    completed: list[Path] = []
    outcome = "SUCCEEDED"
    for op in operations:
        target = op.path
        try:
            _ensure_root(target, project_root)
            _component_targets_within_root(project_root, target)
            if target.exists():
                backup = target.with_suffix(f"{target.suffix}.ynm-backup")
                if target.is_file():
                    if target.is_symlink() and not target.resolve().is_relative_to(project_root):
                        raise IntegrationError("cannot replace symlink outside project", str(target))
                    target.replace(backup)
                    backups[target] = backup
            ok, message = safe_replace(target, op.content)
            if not ok:
                raise IntegrationError(message, str(target))
            completed.append(target)
        except Exception as exc:
            outcome = "FAILED"
            rollback_ok = True
            for written in reversed(completed):
                try:
                    backup = backups.get(written)
                    if backup and backup.exists():
                        backup.replace(written)
                    else:
                        if written.exists():
                            written.unlink()
                except Exception:
                    rollback_ok = False
            if rollback_ok:
                outcome = "ROLLED_BACK"
            else:
                outcome = "PARTIALLY_ROLLED_BACK"
            return outcome, []

    return outcome, [{"path": _rel(project_root, op.path), "status": "COMPLETED", "reason": op.reason} for op in operations]


def initialize_project(project_root: Path, state_root: str, apply: bool, with_agents: bool, dry_run: bool) -> tuple[dict[str, Any], int]:
    context = discover_context(project_root, state_root)
    desired = desired_state_payload(context, state_root)
    try:
        planned, unchanged, created, updated, conflicts = _plan_for(project_root, desired)
    except IntegrationError as exc:
        return {
            "schema_version": "ynm-bootstrap-receipt.v1",
            "execution_id": plan_id(project_root, state_root),
            "project": project_root.name,
            "execution_status": "FAILED",
            "writes_attempted": False,
            "writes_completed": False,
            "persistence_outcome": "FAILED",
            "unresolved_questions": [exc.message],
            "created_at": now_iso8601(),
            "execution_error": exc.message,
        }, 1

    if with_agents:
        agents_path = project_root / "AGENTS.md"
        try:
            agents_status, agents_reason = parse_agents_section_state(agents_path)
            if agents_status == "OWNED":
                # Reuse existing section (idempotent behavior).
                pass
            elif agents_status == "ABSENT":
                planned.append(Operation(path=agents_path, kind="create", content=agents_section_body(state_root), reason="add bounded AGENTS section"))
                created.append("AGENTS.md")
            elif agents_status == "CONFLICT":
                conflicts.append("AGENTS.md")
            else:
                planned.append(merge_agents_update(agents_path, state_root))
                if agents_status == "UNKNOWN":
                    updated.append("AGENTS.md")
        except IntegrationError as exc:
            conflicts.append(f"AGENTS.md:{exc.message}")

    if not apply:
        persistence_outcome = "NOT_AUTHORIZED"
        writes_attempted = False
        writes_completed = False
        if dry_run:
            persistence_outcome = "NOT_ATTEMPTED"
        receipt = build_bootstrap_receipt(
            project=project_root,
            planned=planned,
            unchanged=unchanged,
            conflicts=sorted(set(conflicts)),
            state_root=state_root,
            apply=False,
            writes_attempted=writes_attempted,
            writes_completed=writes_completed,
            persistence_outcome=persistence_outcome,
            context=context,
        )
        return receipt, 0

    if conflicts:
        return build_bootstrap_receipt(
            project=project_root,
            planned=planned,
            unchanged=unchanged,
            conflicts=sorted(set(conflicts)),
            state_root=state_root,
            apply=True,
            writes_attempted=False,
            writes_completed=False,
            persistence_outcome="FAILED",
            context=context,
        ), 1

    if dry_run:
        return build_bootstrap_receipt(
            project_root,
            planned,
            unchanged,
            sorted(set(conflicts)),
            state_root,
            apply=False,
            writes_attempted=False,
            writes_completed=False,
            persistence_outcome="NOT_ATTEMPTED",
            context=context,
        ), 0

    outcome, completed_receipt = apply_operations(project_root, planned, state_root)
    writes_completed = outcome == "SUCCEEDED"
    receipt = build_bootstrap_receipt(
        project=project_root,
        planned=planned,
        unchanged=unchanged,
        conflicts=sorted(set(conflicts)),
        state_root=state_root,
        apply=True,
        writes_attempted=True,
        writes_completed=writes_completed,
        persistence_outcome=outcome,
        context=context,
    )

    # Persisting execution receipts is a separate maintenance concern and may be added by callers
    # intentionally omit write-by-default for deterministic initialization behavior.

    if outcome in {"FAILED", "PARTIALLY_ROLLED_BACK"}:
        return receipt, 1
    return receipt, 0


def discover_project(project_root: Path, state_root: str) -> dict[str, Any]:
    return discover_context(project_root, state_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--initialize", action="store_true", help="plan or apply initialization")
    parser.add_argument("--apply", action="store_true", help="authorize writes")
    parser.add_argument("--dry-run", action="store_true", help="show plan without writes")
    parser.add_argument("--agents-section", action="store_true", help="manage the bounded AGENTS.md section")
    parser.add_argument("--state-root", default=".ynm", help="project-relative state directory")
    args = parser.parse_args()

    project_root = Path(args.project).resolve()
    if not project_root.is_dir():
        parser.error("project must be an existing directory")

    try:
        state_root = normalize_root_path(args.state_root)
    except IntegrationError as exc:
        parser.error(str(exc))

    if args.apply and not args.initialize:
        parser.error("--apply requires --initialize")

    if args.initialize:
        result, code = initialize_project(
            project_root,
            state_root,
            apply=args.apply and not args.dry_run,
            with_agents=args.agents_section,
            dry_run=args.dry_run,
        )
        print(yaml.safe_dump(result, sort_keys=False, default_flow_style=False))
        return code

    result = discover_project(project_root, state_root)
    print(yaml.safe_dump(result, sort_keys=False, default_flow_style=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
