#!/usr/bin/env python3
"""Provider-neutral helpers for enforcing the YNM invocation lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PHASES = ("ANALYSIS", "ITERATION", "DELIVERY", "TERMINATED")
INFORMATION_DELTAS = {"EVIDENCE", "PROJECT", "DEPENDENCY", "HUMAN", "SCOPE", "METHOD", "OTHER_MATERIAL"}
TERMINAL_REASONS = {
    "CONVERGED",
    "ITERATION_BOUND",
    "BLOCKED",
    "PARTIAL",
    "ESCALATION",
    "USER_STOP",
    "CAPABILITY_LIMIT",
    "CAPABILITY_BOUNDARY",
    "AUTHORITY_BOUNDARY",
    "NO_INFORMATION_GAIN",
    "EVIDENCE_LIMIT",
    "UNSAFE_CONTINUATION",
    "EVALUATOR_FAILURE",
    "TERMINATOR",
    "NOT_APPLICABLE",
}
LEGACY_TERMINAL_ALIASES = {
    "CAPABILITY_LIMIT": "CAPABILITY_BOUNDARY",
}


@dataclass(frozen=True)
class IterationDecision:
    """Decision for one post-iteration continuation check."""

    continue_iteration: bool
    reason: str
    transitioned_to_delivery: bool
    expected_information_gain: list[str] = field(default_factory=list)


class InvocationLifecycle:
    def __init__(
        self,
        max_immediate_iterations: int | None = None,
        phase: str = "ANALYSIS",
    ) -> None:
        if max_immediate_iterations is not None and max_immediate_iterations < 1:
            raise ValueError("max_immediate_iterations must be >= 1 when set")
        if phase not in PHASES:
            raise ValueError(f"unknown phase: {phase}")
        self.max_immediate_iterations = max_immediate_iterations
        self.phase = phase
        self.phase_history: list[str] = [phase]
        self.iteration_count = 0
        self.plan_revision = 1
        self.converged = False
        self.stop_reason: str | None = None

    @property
    def active(self) -> bool:
        return self.phase not in {"TERMINATED"}

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

    def reanalyze(self, reason: str) -> None:
        if self.phase != "ITERATION" or not reason.strip():
            raise ValueError("scoped reanalysis requires an active iteration and reason")
        self.plan_revision += 1
        self.phase = "ANALYSIS"
        self.phase_history.append(self.phase)

    def _transition_to_delivery(self, reason: str) -> IterationDecision:
        reason = self.normalize_terminal_reason(reason)
        if reason not in TERMINAL_REASONS:
            raise ValueError(f"unknown terminal reason: {reason}")
        if self.phase == "TERMINATED":
            raise ValueError("invocation already terminated")
        if self.phase == "DELIVERY":
            raise ValueError("invocation already in Delivery")
        self.stop_reason = reason
        self.phase = "DELIVERY"
        self.phase_history.append(self.phase)
        return IterationDecision(False, reason, True)

    def deliver(self, reason: str) -> IterationDecision:
        """Force an explicit delivery transition."""
        return self._transition_to_delivery(reason)

    def terminate(self) -> None:
        if self.phase != "DELIVERY":
            raise ValueError("termination requires Delivery")
        self.phase = "TERMINATED"
        self.phase_history.append(self.phase)

    def decide_next_iteration(
        self,
        deltas: set[str],
        *,
        other_material_evidence: list[str] | None = None,
        authority_exhausted: bool = False,
        capability_exhausted: bool = False,
        unsafe_reason: str | None = None,
        additional_evidence_gain: list[str] | None = None,
    ) -> IterationDecision:
        if self.phase != "ITERATION":
            raise ValueError("analysis and delivery phases do not decide iteration")
        unknown = set(deltas) - INFORMATION_DELTAS
        if unknown:
            raise ValueError(f"unknown deltas: {sorted(unknown)}")
        if authority_exhausted:
            return self._transition_to_delivery("AUTHORITY_BOUNDARY")
        if capability_exhausted:
            return self._transition_to_delivery("CAPABILITY_BOUNDARY")
        if unsafe_reason:
            return self._transition_to_delivery("UNSAFE_CONTINUATION")
        if self.max_immediate_iterations is not None and self.iteration_count >= self.max_immediate_iterations:
            return self._transition_to_delivery("ITERATION_BOUND")
        if "OTHER_MATERIAL" in deltas and not other_material_evidence:
            raise ValueError("OTHER_MATERIAL requires supporting evidence")
        if not deltas:
            return self._transition_to_delivery("NO_INFORMATION_GAIN")
        if self.converged:
            return self._transition_to_delivery("CONVERGED")
        decision = IterationDecision(True, "MATERIAL_GAIN", False, sorted(deltas | set(additional_evidence_gain or [])))
        return decision

    def may_iterate(self, deltas: set[str]) -> bool:
        """Compatibility wrapper for existing callers."""
        return self.decide_next_iteration(deltas).continue_iteration

    def decision_for_legacy_convergence(self) -> IterationDecision:
        if self.converged:
            return IterationDecision(False, "CONVERGED", True)
        if self.phase != "ITERATION":
            raise ValueError("iteration required for convergence check")
        return IterationDecision(False, "NOT_APPLICABLE", False)

    def lifecycle_receipt_fragment(
        self,
        *,
        unresolved_findings: list[str],
        reviewed_scope: list[str],
        unreviewed_scope: list[str],
        persistence_authorized: bool,
        persistence_attempted: bool = False,
        persistence_outcome: str = "NOT_ATTEMPTED",
        propositions: list[str] | None = None,
        evidence_snapshot: str = "current review inputs",
        evidence_limitations: list[str] | None = None,
        executor_profile: str = "unspecified executor",
        authority: str = "review only",
        execution_limits: list[str] | None = None,
        temporal_reference: str = "receipt creation time",
    ) -> dict[str, Any]:
        if self.phase != "DELIVERY":
            raise ValueError("a receipt requires Delivery")
        return {
            "schema_version": "ynm-run-receipt.v3",
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
                "machine_state": "persisted" if persistence_outcome == "SUCCEEDED" and persistence_attempted else "emitted_stateless",
                "authorization_status": "AUTHORIZED" if persistence_authorized else "NOT_REQUESTED",
                "persistence_attempted": persistence_attempted,
                "persistence_outcome": persistence_outcome,
            },
            "validity_boundary": {
                "propositions": propositions or ["bounded review proposition"],
                "reviewed_scope": reviewed_scope,
                "unreviewed_scope": unreviewed_scope,
                "evidence_snapshot": evidence_snapshot,
                "evidence_limitations": evidence_limitations or [],
                "executor_profile": executor_profile,
                "authority": authority,
                "execution_limits": execution_limits or [],
                "temporal_reference": temporal_reference,
            },
        }

    def normalize_terminal_reason(self, reason: str) -> str:
        """Return a canonical terminal reason while preserving legacy aliases."""
        return LEGACY_TERMINAL_ALIASES.get(reason, reason)

    def receipt_fields(self, *, unresolved_findings: list[str], reviewed_scope: list[str], unreviewed_scope: list[str], persistence_authorized: bool) -> dict[str, Any]:
        # Backward-compatible wrapper.
        return self.lifecycle_receipt_fragment(
            unresolved_findings=unresolved_findings,
            reviewed_scope=reviewed_scope,
            unreviewed_scope=unreviewed_scope,
            persistence_authorized=persistence_authorized,
            persistence_attempted=False,
            persistence_outcome="NOT_ATTEMPTED",
        )
