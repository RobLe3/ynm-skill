# Finding Lifecycle and Persistence

The review flow is:

`DISCOVERY → PROPOSITION → REVIEW → EVIDENCE → INTERPRETATION → FINDING → PROPOSED DISPOSITION → RECONCILIATION → DISPOSITION → PERSISTENCE → REVISIT → RESOLUTION, REOPEN, DUPLICATION, or SUPERSESSION`

A finding projection has one lifecycle status: `OPEN`, `RESOLVED`, `DUPLICATE`, or `SUPERSEDED`. Status is not disposition. A new or reopened finding is OPEN. YES, NO, and MAYBE may all remain OPEN while action, monitoring, or a decision is outstanding.

## Transition rules

- `NEW_FINDING` creates an OPEN finding with a stable proposition and scope. A proposed disposition may precede the reconciled disposition.
- `EVIDENCE_CONTRIBUTION`, `RELATIONSHIP`, `CONFLICT`, and `DEPENDENCY` add knowledge without changing disposition or status automatically.
- `PROPOSED_DISPOSITION` and `DISPOSITION_REQUEST` never overwrite the current disposition. An authorized reconciliation event records old value, new value, evidence, and rationale.
- `RESOLUTION` changes OPEN to RESOLVED and identifies resolution evidence or an explicit authority decision. Inactivity and age are not resolution.
- `REOPEN_REQUEST` identifies new evidence, material subject or dependency change, changed assumption, corrected assessment, or a satisfied revisit condition. Accepted reopening changes RESOLVED to OPEN and preserves the prior disposition.
- `DUPLICATION` changes the duplicate record to DUPLICATE and links the canonical finding. Contributions and provenance remain accessible.
- `SUPERSESSION` changes a finding to SUPERSEDED and links the replacement proposition. It does not rewrite the historical meaning of either finding.
- `ASSESSMENT_REVISION`, `AUTHORIZATION`, and `REVALIDATION` update their own projections and affect a finding only through an explicit linked event.

Every transition appends an event containing actor, authority, time, payload, and evidence references. Corrections append corrective events. Current records are projections derived from history; history remains reconstructable.

Assessment revisions preserve earlier criteria and results. Repeating an assessment with identical evidence and conditions is not reopening. A changed proposition normally requires supersession rather than silently editing identity.

Preserve negative knowledge. NO records why the proposition was contradicted, evidence and assumptions, and reopen conditions. MAYBE records the unresolved information gap, current evidence, next evidence needed, and revisit trigger where possible. BLOCKED records what prevented execution. Each run ends with a Run Receipt, whether or not persistent state is available.

## Portable state

Persistence may use a human-readable directory containing:

```text
ynm-state/
├── manifest.yaml          # format version and project identity
├── project-snapshots.yaml # bounded state fingerprints by review generation
├── execution-contexts.yaml # capability, complexity, strategy, and coverage
├── assessments.yaml       # frozen assessment revisions and references
├── findings.yaml          # current projections plus stable IDs
├── events.yaml            # append-only lifecycle and contribution events
└── runs.yaml              # loop results, receipts, limitations, and convergence
```

The files are a portable representation, not a required database schema. An implementation may use another store if it can export and import equivalent records without losing provenance or history. Write state atomically and only with permission.

Stateless execution remains valid. It loses reliable recurrence detection, historical comparison, unresolved-state continuity, previous dispositions, reopen detection, and convergence across runs. The report must name those limitations.
