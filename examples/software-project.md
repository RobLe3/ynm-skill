# Software Project Example

Scope: a persistence feature after an implementation change.

Because the conformance decision may authorize a migration, the reviewer freezes an assessment revision before testing:

```yaml
id: ASSESS-PERSIST-1
revision: 1
proposition: The implementation conforms to the declared single-path persistence architecture.
scope: persistence subsystem at project revision abc123
assessment_mode: conformance
reference_state: ADR-12 at revision 7
evaluation_method: Trace every production persistence entry point and compare it with ADR-12.
acceptance_conditions:
  - No production path bypasses the declared adapter.
  - Migration-only paths are explicitly gated.
required_evidence: [architecture record, entry-point inventory, configuration, focused tests]
evaluator: architecture-review role
independence_requirement: SEPARATE_ROLE
frozen_at: 2026-08-19T09:50:00Z
```

```yaml
id: YNM-ARCH-0042
title: Second persistence path may contradict the declared architecture
proposition: The implementation conforms to the declared single-path persistence architecture.
source_loop: Architecture
scope: persistence subsystem at review generation 18
observation: The architecture record declares one persistence path; implementation inspection reveals two.
evidence: [EV-ADR-12, EV-CODE-77]
interpretation: The additional path may be architectural drift or a bounded migration path.
proposed_disposition: "MAYBE"
disposition: "MAYBE"
disposition_reason: CONFLICTING_EVIDENCE
authorization_status: NOT_REQUESTED
revisit_conditions: [Determine whether the second path is migration-only.]
created_at: 2026-08-19T10:00:00Z
updated_at: 2026-08-19T10:00:00Z
status: OPEN
history: [EVENT-1]
```

The Implementation Loop contributes evidence that the second path runs only when a migration flag is active. The contribution does not overwrite the finding. The Architecture Loop confirms that the decision record explicitly permits the migration exception, and the Disposition Loop appends a transition to YES under the review charter. If a later change removes the flag guard, material-change detection opens a `REOPEN_REQUEST`; the previous YES remains in history.

An independent Adoption finding may still be NO if operators cannot understand the migration. Technical and architectural support does not force an adoption disposition. A recommendation to delete the previous store remains `REQUIRES_HUMAN` even when conformance is YES.

If tests fail because the test runner cannot access its temporary directory, the run records `execution_status: BLOCKED`, `failure_origin: ENVIRONMENT` only when filesystem evidence supports that attribution, and `disposition: MAYBE`. Changing the acceptance condition after seeing the failure creates assessment revision 2; it does not revise the meaning of revision 1.

For a repository larger than effective context, the Meta Loop chooses CONSTRAINED execution and creates separate persistence-subsystem and migration-tool windows. Each window records included and excluded paths. Findings are synthesized only after both windows complete; deployment remains explicitly unreviewed. If context ends after the first window, its findings survive and the Run Receipt reports `execution_status: PARTIAL`, `halt_reason: EXECUTOR_LIMIT`, and continuation scope for the second window. It does not claim convergence.
