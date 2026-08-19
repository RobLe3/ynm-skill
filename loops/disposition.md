# Disposition Loop

**Purpose:** Preserve and reconcile the lifecycle of findings without replacing specialist analysis.

- **Scope:** proposition identity, assessment revisions, evidence accumulation and ancestry, proposed and final dispositions, authorization separation, ownership, duplicate and relationship handling, conflicts, dependencies, supersession, reopening, revalidation, negative knowledge, resolution evidence, and stale decisions.
- **Inputs and evidence:** canonical findings, lifecycle events, authority charter, prior state, contributions, and project-change records.
- **Owns:** finding lifecycle records, current disposition projections, assessment links, revalidation state, and transition integrity.
- **Observes:** specialist findings and project authority decisions.
- **May recommend:** reconciliation, more or independent evidence, ownership, escalation, merge, supersession, revalidation, reopen, or resolution.
- **May not decide:** missing specialist questions from its own general judgment, silently overwrite history, or grant project-change authority.
- **Must hand off:** domain analysis to the owning specialist and authority gaps to the appropriate human.
- **Finding types:** unresolved state, conflicting proposals or evidence, duplicate, stale or invalidated disposition, missing owner, unsupported resolution, missing provenance, or unauthorized transition.
- **Output:** append-only events, current projections, assessment and authorization links, explicit conflicts, preserved negative knowledge, escalation, and one loop result.
- **Termination:** all submitted transitions are applied, rejected with reason, or escalated.
- **Rerun:** new evidence, transition requests, revisit conditions, or material project change arrives.
- **Failure modes:** universal judging, last-reviewer-wins, closing by inactivity, merging away provenance, or treating recommendation as authority.
