# Execution Context Contract

Execution context records the capabilities and limits that materially shaped a review. It is provider-neutral and applies to people, models, tools, and mixed teams. Record only fields that affect strategy, coverage, reliability, continuation, or interpretation.

## Capability profile

Required for substantial reviews: `id`, `observed_at`, `capability_basis`, `effective_context_capacity`, `state_access`, `tools`, `limits`, and `unknowns`. Add relevant analytical capabilities, modalities, orchestration support, reliable structured output, or executor family when known without relying on vendor identity.

Resolve capability in this order: environment declarations, available interfaces, runtime metadata, observed successful use, conservative probes, then conservative fallback assumptions. Mark each material capability `AVAILABLE`, `UNAVAILABLE`, or `UNKNOWN`. UNKNOWN never silently becomes AVAILABLE. Advertised context, parameter count, product tier, and model family are weak secondary evidence only.

## Complexity and fit

A project-complexity record may include artifact volume, approximate size, languages or formats, subsystem count, dependency depth, documentation and history volume, active findings, coupling, applicable loops, and external evidence. Exact scores are unnecessary. Record `capability_scope_fit` as `FITS`, `REQUIRES_PARTITION`, or `EXCEEDS_CAPABILITY`, with rationale.

Execution strategy is `CONSTRAINED`, `STANDARD`, or `EXTENDED`. These values describe workload strategy, not review quality. They do not change evidence sufficiency, disposition semantics, authority, or assessment integrity.

## Supporting records

`review_window` records `scope`, `evidence_included`, `evidence_excluded`, `reason`, and `related_windows`. `loop_assignment` records `loop`, `executor`, `capability_basis`, `scope`, and `independence_requirement`. `capability_escalation` records `reason`, `required_capability`, `remaining_scope`, and `continuation_artifacts`.

When execution is partial, record `reviewed_scope`, `unreviewed_scope`, and `continuation_scope`. When capability changed materially between runs, record the new capability and tool profile so later reconciliation can distinguish new evidence from changed evaluation reach.
