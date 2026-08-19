# Invocation Lifecycle

Every YNM invocation follows one macro lifecycle:

```text
ANALYSIS → ITERATION → DELIVERY → TERMINATED
```

This lifecycle coordinates existing methods and contracts. It is not a focal loop, a finding lifecycle, or an additional source of disposition authority.

## Analysis

Analysis establishes what can responsibly be reviewed before material project-wide judgment. It identifies the objective; requested and effective scope; project context and documentation; available and unavailable evidence; prior YNM state; executor capability; complexity and capability-to-scope fit; authority and mutation limits; applicable and excluded loops; dependencies; Assessment Contracts and reference states; persistence mode; and iteration safety policy.

Its output is a proportionate Review Plan. Requested scope records what the user asked for. Effective scope records what available evidence, capability, authority, tools, and budget permit. A difference between them is explicit and appears again in Delivery.

Analysis normally occurs once. A material change to scope, capability, authority, evidence availability, dependencies, reference state, or assessment conditions may re-enter Analysis for the affected scope. Reanalysis creates a linked Review Plan revision; it does not erase earlier assumptions or restart unaffected review work.

## Iteration

Iteration performs applicable focal reviews, gathers typed evidence, creates or updates findings, correlates duplicates and relationships, preserves provenance, identifies conflicts and dependencies, proposes dispositions, and reconciles them under declared authority.

An immediate additional iteration requires a stated source of expected information gain: material new evidence (`ΔE`), project change (`ΔP`), dependency change (`ΔD`), newly available human decision (`ΔH`), legitimate scope change (`ΔS`), corrected evaluation method (`ΔM`), or another explicit material change. No change means no immediate repetition.

`max_immediate_iterations` is an optional safety ceiling. It never requires that many passes and never substitutes for convergence. Reaching it moves the invocation to Delivery with `converged: false` unless convergence was independently established.

## Delivery

Delivery converts the state actually achieved into an explicit handoff on every terminal path. It occurs after convergence, a safety bound, blocking, partial execution, escalation, user stop, authority or capability limits, evidence limits, or unrecoverable evaluator failure.

Delivery finalizes current finding projections without inventing evidence; preserves MAYBE reasons and negative knowledge; identifies blockers, accepted limitations, unresolved dependencies and human decisions; reports requested, reviewed, and unreviewed scope; records material changes, reopened and resolved findings, convergence, and the stop reason; persists only when enabled and authorized; emits a terminal Run Receipt; and produces a concise human-facing result.

Human Delivery summarizes decisions, coverage, limitations, uncertainty, authority, and next steps. Machine state preserves complete continuation records. Neither may conceal a material limitation present in the other. Delivery is mandatory but does not imply success, completion, convergence, or authorization.

## Phase and status separation

Invocation phase is one of `ANALYSIS`, `ITERATION`, `DELIVERY`, or `TERMINATED`. Loop execution status remains `COMPLETED`, `PARTIAL`, `BLOCKED`, or `NOT_APPLICABLE`. Disposition remains `YES`, `NO`, or `MAYBE`. Authorization remains separate.

```yaml
phase: DELIVERY
execution_status: PARTIAL
converged: false
authorization_status: REQUIRES_HUMAN
```

## Invariants

- **Analysis before judgment:** establish enough context, scope, capability, evidence, and authority before material project-wide dispositions.
- **Iteration with information gain:** repeat only when another pass can reasonably improve knowledge.
- **Delivery is mandatory:** every started invocation reaches Delivery, including blocked and inconclusive reviews.
- **Delivery does not invent completion:** report only achieved coverage and state.
- **Exhaustion is not convergence:** capability, context, budget, tool, evidence, or authority limits do not prove that review converged.
