# Loop Result Contract

Every invocation returns one execution result independent of finding dispositions.

| Status | Meaning |
|---|---|
| `COMPLETED` | The selected scope was reviewed with the evidence reasonably available. |
| `PARTIAL` | Some selected scope was reviewed; omitted scope and consequences are recorded. |
| `NOT_APPLICABLE` | The loop has no meaningful proposition in the selected project scope. |
| `BLOCKED` | The loop could not perform required review work; the blocker and next authority are recorded. |

Required loop-result fields are `loop`, `execution_status`, `scope`, `started_at`, `completed_at`, `finding_ids`, `evidence_summary`, and `limitations`. For PARTIAL, also require `reviewed_scope`, `unreviewed_scope`, and `continuation_scope`. Optional fields are `execution_context`, `strategy`, `failure_origin`, `failure_origin_evidence`, `capability_exhausted`, `dependencies`, `handoffs`, `escalation`, `rerun_request`, and `metrics`. Timestamps and run identifiers may be generated.

A rerun request contains `reason`, `affected_scope`, `change_since_previous_run`, and `expected_information_gain`. The change may be new evidence, relevant project state, dependency state, a human decision, review scope, or a legitimately corrected method. A blocked run may produce MAYBE findings, but no automatic mapping exists between execution status and disposition.

## Failure origin

When evaluation fails, use `SUBJECT`, `PREEXISTING`, `ENVIRONMENT`, `EVALUATOR`, `DEPENDENCY`, `AUTHORITY`, `EVIDENCE`, `BUDGET`, or `UNKNOWN`. Attribution is itself an inference and requires supporting evidence. Use `UNKNOWN` rather than calling an unexplained failure environmental. A subject-attributed failure may support NO; evaluator or environment failure normally leaves the proposition unresolved.

## Run Receipt

Every started YNM review emits one terminal Run Receipt, including in stateless mode. Required fields are `run_id`, `generation`, `project_state`, `execution_context`, `execution_strategy`, `loops_requested`, `loops_executed`, `stage_reached`, `execution_status`, `terminal_outcome`, `halt_reason`, `reviewed_scope`, `unreviewed_scope`, `evidence_added`, `findings_created`, `findings_updated`, `dispositions_changed`, `unresolved_dependencies`, `continuation_scope`, `next_revisit_condition`, and `persistence_status`. Add `capability_exhausted` and `escalation` when applicable.

`terminal_outcome` is one of `COMPLETED_REVIEW`, `PARTIAL_REVIEW`, `BLOCKED_REVIEW`, `ESCALATED_REVIEW`, `NOT_APPLICABLE_REVIEW`, or `CONVERGED_REVIEW`. This does not expand loop execution status or disposition. Silence is not a terminal outcome. A receipt explains what happened even when no finding changed, evidence was missing, budget ended, or authority was unavailable.

Executor exhaustion uses PARTIAL or BLOCKED with a specific halt reason such as `EXECUTOR_LIMIT`; it never sets convergence. A completed receipt cannot imply coverage beyond `reviewed_scope`.

Receipts created under the explicit invocation lifecycle use `schema_version: ynm-run-receipt.v2` and additionally record `phase_history`, `review_plan_revision`, `iteration_count`, `converged`, `stop_reason`, unresolved findings, material changes, reopened and resolved findings, required human decisions, and a `delivery` summary for human output and machine state. Existing receipts remain valid historical records.

Every v2 receipt includes Delivery in its phase history. Delivery may report any execution status and does not grant project or persistence authorization. A safety-bound, capability-limited, or blocked receipt normally has `converged: false`.
