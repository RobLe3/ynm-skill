# Disposition Contract

A disposition evaluates exactly one explicit, falsifiable proposition within a stated scope and evidence horizon.

| Value | Canonical meaning | Use when |
|---|---|---|
| `YES` | `SUPPORTED` | Sufficient affirmative evidence supports the explicitly bounded proposition under the declared conditions. |
| `NO` | `CONTRADICTED` | Sufficient evidence contradicts the explicitly bounded proposition under the declared conditions. |
| `MAYBE` | `UNRESOLVED` | Available evidence cannot responsibly decide the proposition within the current boundary. |

Absence of evidence is not negative evidence. `MAYBE` requires a reason and retained context. Recommended reason codes are `EVIDENCE_REQUIRED`, `DEPENDENCY_PENDING`, `EXTERNAL_DECISION`, `CONFLICTING_EVIDENCE`, `INSUFFICIENT_CONTEXT`, `IMPLEMENTATION_PENDING`, `ARCHITECTURE_PENDING`, `USER_VALIDATION_REQUIRED`, `TIME_DEPENDENT`, and `REPRODUCTION_REQUIRED`.

A finding whose proposition remains materially ambiguous does not receive final YES or NO. Use MAYBE with `INSUFFICIENT_CONTEXT` or another accurate reason until the proposition is clarified. Significant evidence supporting both YES and NO normally remains MAYBE with `CONFLICTING_EVIDENCE`; later reconciliation preserves the conflict history.

A disposition is not an epistemic type, execution status, severity, priority, confidence, approval, or action authority. `BLOCKED` and `NOT_APPLICABLE` are loop execution statuses, never dispositions.

`YES` is not universal proof, and `NO` is not a judgment that an entire project is invalid. Missing evidence, inaccessible evidence, conflicting evidence, semantic ambiguity, insufficient coverage, executor or resource limits, and unresolved authority or intent may all require `MAYBE`. Every disposition is interpreted within the validity boundary defined in [Epistemic Boundaries](../methodology/epistemic-boundaries.md).

Changing a disposition requires a lifecycle event that identifies actor authority, previous and new values, evidence considered, rationale, and time. Recency alone has no authority. A human override remains explicit and does not delete the previous evaluation.
