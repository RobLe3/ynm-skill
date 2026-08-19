#!/usr/bin/env python3
"""Small provider-neutral helpers for enforcing the YNM invocation lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PHASES = ("ANALYSIS", "ITERATION", "DELIVERY", "TERMINATED")
INFORMATION_DELTAS = {"EVIDENCE", "PROJECT", "DEPENDENCY", "HUMAN", "SCOPE", "METHOD", "OTHER_MATERIAL"}
TERMINAL_REASONS = {
    "CONVERGED", "ITERATION_BOUND", "BLOCKED", "PARTIAL", "ESCALATION", "USER_STOP",
    "AUTHORITY_LIMIT", "CAPABILITY_LIMIT", "EVIDENCE_LIMIT", "EVALUATOR_FAILURE", "NOT_APPLICABLE",
}


@dataclass
class InvocationLifecycle:
    max_immediate_iterations: int | None = None
    phase: str = "ANALYSIS"
    phase_history: list[str] = field(default_factory=lambda: ["ANALYSIS"])
    iteration_count: int = 0
    plan_revision: int = 1
    converged: bool = False
    stop_reason: str | None = None

    def begin_iteration(self) -> None:
        if self.phase != "ANALYSIS":
            raise ValueError("iteration may begin only after Analysis")
        self.phase = "ITERATION"
        self.phase_history.append(self.phase)

    def complete_iteration(self, *, converged: bool = False) -> None:
        if self.phase != "ITERATION":
            raise ValueError("no iteration is active")
        self.iteration_count += 1
        if converged:
            self.converged = True
            self.deliver("CONVERGED")

    def may_iterate(self, deltas: set[str]) -> bool:
        if self.phase != "ITERATION" or self.converged:
            return False
        if self.max_immediate_iterations is not None and self.iteration_count >= self.max_immediate_iterations:
            self.deliver("ITERATION_BOUND")
            return False
        return bool(deltas & INFORMATION_DELTAS)

    def reanalyze(self, reason: str) -> None:
        if self.phase != "ITERATION" or not reason.strip():
            raise ValueError("scoped reanalysis requires an active iteration and reason")
        self.plan_revision += 1
        self.phase = "ANALYSIS"
        self.phase_history.append(self.phase)

    def deliver(self, reason: str) -> None:
        if reason not in TERMINAL_REASONS:
            raise ValueError("unknown terminal reason")
        if self.phase == "TERMINATED":
            raise ValueError("invocation already terminated")
        self.stop_reason = reason
        self.phase = "DELIVERY"
        self.phase_history.append(self.phase)

    def terminate(self) -> None:
        if self.phase != "DELIVERY":
            raise ValueError("termination requires Delivery")
        self.phase = "TERMINATED"
        self.phase_history.append(self.phase)

    def receipt_fields(self, *, unresolved_findings: list[str], reviewed_scope: list[str],
                       unreviewed_scope: list[str], persistence_authorized: bool) -> dict[str, Any]:
        if "DELIVERY" not in self.phase_history:
            raise ValueError("a receipt requires Delivery")
        return {
            "schema_version": "ynm-run-receipt.v2",
            "phase_history": self.phase_history.copy(),
            "review_plan_revision": self.plan_revision,
            "iteration_count": self.iteration_count,
            "converged": self.converged,
            "stop_reason": self.stop_reason,
            "unresolved_findings": unresolved_findings,
            "material_changes": [],
            "findings_reopened": [],
            "findings_resolved": [],
            "required_human_decisions": [],
            "reviewed_scope": reviewed_scope,
            "unreviewed_scope": unreviewed_scope,
            "delivery": {
                "human_artifact": "required",
                "machine_state": "persisted" if persistence_authorized else "emitted_stateless",
                "authorization_status": "AUTHORIZED" if persistence_authorized else "NOT_REQUESTED",
            },
        }
