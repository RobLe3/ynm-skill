#!/usr/bin/env python3
"""Discover or initialize a minimal YNM project integration.

Discovery is always read-only. Initialization writes only with --apply.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

BEGIN = "<!-- YNM:BEGIN -->"
END = "<!-- YNM:END -->"

ROLE_CANDIDATES = {
    "project_entry": ["README.md"],
    "agent_guidance": ["AGENTS.md", "CLAUDE.md"],
    "architecture_source": ["ARCHITECTURE.md", "DESIGN.md", "docs/architecture", "architecture"],
    "adoption_guidance": ["README.md", "docs", "INSTALL.md"],
    "contribution_guidance": ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"],
    "security_guidance": ["SECURITY.md"],
    "release_history": ["CHANGELOG.md", "RELEASES.md"],
    "version_policy": ["VERSIONING.md", "RELEASES.md"],
    "decision_history": ["adr", "adrs", "docs/adr", "docs/adrs"],
    "ynm_configuration": [".ynm/config.yaml"],
    "ynm_state": [".ynm/state"],
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def discover(root: Path, state_root: str) -> dict[str, Any]:
    roles = []
    discovered: set[str] = set()
    for role, candidates in ROLE_CANDIDATES.items():
        artifacts = []
        for candidate in candidates:
            path = root / candidate
            if path.exists():
                artifacts.append(candidate)
                discovered.add(candidate)
        roles.append({"role": role, "artifacts": artifacts, "status": "CONFIRMED" if artifacts else "UNKNOWN"})

    # Common project instructions that may use unfamiliar names remain candidates.
    for path in sorted(root.glob("*INSTRUCTIONS*.md")):
        discovered.add(rel(path, root))
        role = next(item for item in roles if item["role"] == "agent_guidance")
        role["artifacts"].append(rel(path, root))
        role["status"] = "CANDIDATE"

    return {
        "schema_version": "ynm-project-context.v1",
        "project": {"name": root.name, "root": "."},
        "documentation_roles": roles,
        "ynm_state_location": state_root,
        "persistence_mode": "PERSISTENT" if (root / state_root).exists() else "STATELESS",
        "discovered_at": now(),
        "discovered_artifacts": sorted(discovered),
    }


def dump_yaml(data: Any) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def desired_files(context: dict[str, Any], state_root: str) -> dict[str, str]:
    project_context = {k: v for k, v in context.items() if k != "discovered_artifacts"}
    project_context["managed_by"] = "ynm"
    project_context["persistence_mode"] = "PERSISTENT"
    config = {
        "managed_by": "ynm",
        "schema_version": "ynm-project-config.v1",
        "ynm": {"persistence": True, "state_location": state_root},
        "review": {"default_mode": "read_only"},
        "loops": {name: "auto" for name in ["architecture", "implementation", "adoption", "maintenance", "disposition"]},
        "scope": {"include": [], "exclude": []},
        "authority": {"mutation_requires_explicit_authorization": True},
    }
    readme = """# YNM project state

This directory contains YNM-owned review configuration and longitudinal state for this project. Loading or reviewing with YNM remains read-only by default. Project artifacts may be changed only under separate, explicit authorization.

- `project.yaml` records discovered context and documentation-role mappings.
- `config.yaml` controls project-local execution preferences; it cannot redefine YNM semantics.
- `state/findings.yaml` is the current finding projection.
- `state/events.jsonl` preserves append-oriented history.
- `state/receipts/` records terminal bootstrap and review results.

Removing this directory detaches persistent YNM state but loses longitudinal history. Remove a bounded YNM section in `AGENTS.md` separately; do not alter surrounding project instructions.
"""
    return {
        f"{state_root}/README.md": readme,
        f"{state_root}/project.yaml": dump_yaml(project_context),
        f"{state_root}/config.yaml": dump_yaml(config),
        f"{state_root}/state/findings.yaml": "schema_version: ynm-findings.v1\nfindings: []\n",
        f"{state_root}/state/events.jsonl": "",
    }


def agents_section(state_root: str) -> str:
    return f"""{BEGIN}
## YNM Project Review

- Invoke a read-only review with: `Review this project using YNM.`
- Persistent YNM state: `{state_root}/state/`
- Loading and review do not authorize project mutation.
- Modify project artifacts only within explicitly authorized scope.
- See `{state_root}/README.md` for project-local state details.
{END}"""


def integrate_agents(path: Path, state_root: str) -> tuple[str | None, str | None]:
    original = path.read_text() if path.exists() else ""
    begins, ends = original.count(BEGIN), original.count(END)
    section = agents_section(state_root)
    if begins != ends or begins > 1:
        return None, "AGENTS.md has malformed or duplicate YNM ownership markers"
    if begins == 1:
        start = original.index(BEGIN)
        finish = original.index(END, start) + len(END)
        return original[:start] + section + original[finish:], None
    if not original:
        return section + "\n", None
    return original.rstrip() + "\n\n" + section + "\n", None


def bootstrap_id(root: Path, state_root: str) -> str:
    value = f"{root.resolve()}\0{state_root}\0ynm-bootstrap.v1"
    return "YNM-BOOT-" + hashlib.sha256(value.encode()).hexdigest()[:12].upper()


def initialize(root: Path, state_root: str, apply: bool, with_agents: bool) -> dict[str, Any]:
    context = discover(root, state_root)
    desired = desired_files(context, state_root)
    created, updated, reused, conflicts = [], [], [], []
    plan: list[tuple[Path, str]] = []

    for name, content in desired.items():
        path = root / name
        if not path.exists():
            created.append(name)
            plan.append((path, content))
        elif path.read_text() == content or name.endswith("project.yaml"):
            # Existing context is retained rather than replacing its discovery timestamp.
            reused.append(name)
        elif name.endswith(("findings.yaml", "events.jsonl")):
            reused.append(name)
        elif name.endswith("config.yaml") and "managed_by:" not in path.read_text():
            conflicts.append(name)
        elif name.endswith("README.md"):
            reused.append(name)
        else:
            updated.append(name)
            plan.append((path, content))

    if with_agents:
        agents = root / "AGENTS.md"
        content, error = integrate_agents(agents, state_root)
        if error:
            conflicts.append("AGENTS.md")
        elif content is not None and (not agents.exists() or agents.read_text() != content):
            (created if not agents.exists() else updated).append("AGENTS.md")
            plan.append((agents, content))
        else:
            reused.append("AGENTS.md")

    status = "BLOCKED" if conflicts else "COMPLETED"
    receipt = {
        "schema_version": "ynm-bootstrap-receipt.v1",
        "bootstrap_id": bootstrap_id(root, state_root),
        "project": root.name,
        "mode": "INITIALIZE",
        "execution_status": status,
        "discovered_artifacts": context["discovered_artifacts"],
        "reused_artifacts": sorted(set(reused)),
        "created_artifacts": sorted(set(created)) if apply and not conflicts else [],
        "updated_artifacts": sorted(set(updated)) if apply and not conflicts else [],
        "untouched_conflicting_artifacts": sorted(set(conflicts)),
        "ynm_state_location": state_root,
        "persistence_mode": "PERSISTENT" if apply and not conflicts else context["persistence_mode"],
        "mutation_authorization": "AUTHORIZED" if apply else "REQUIRES_HUMAN",
        "unresolved_questions": ["Resolve ownership conflicts before initialization"] if conflicts else [],
        "created_at": now(),
    }

    if apply and not conflicts:
        for path, content in plan:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        receipt_path = root / state_root / "state" / "receipts" / f"{receipt['bootstrap_id']}.yaml"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        if receipt_path.exists():
            previous = yaml.safe_load(receipt_path.read_text())
            receipt["created_at"] = previous.get("created_at", receipt["created_at"])
        if not receipt_path.exists() or plan:
            receipt_path.write_text(dump_yaml(receipt))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--initialize", action="store_true", help="plan persistent initialization")
    parser.add_argument("--apply", action="store_true", help="authorize and apply initialization writes")
    parser.add_argument("--agents-section", action="store_true", help="manage the bounded YNM AGENTS.md section")
    parser.add_argument("--state-root", default=".ynm")
    args = parser.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        parser.error("project must be an existing directory")
    if args.apply and not args.initialize:
        parser.error("--apply requires --initialize")
    if args.initialize:
        result = initialize(root, args.state_root.strip("/"), args.apply, args.agents_section)
    else:
        result = discover(root, args.state_root.strip("/"))
    print(json.dumps(result, indent=2))
    return 1 if result.get("execution_status") == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
