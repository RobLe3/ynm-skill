# Finding Contract

A finding is a longitudinal record for one proposition. Keep the core small; add detail through evidence and history events.

## Core fields

| Field | Requirement | Supply |
|---|---|---|
| `id` | Required | Generated or assigned |
| `title` | Required | Human or machine |
| `proposition` | Required | Human or machine |
| `source_loop` | Required | Machine |
| `scope` | Required | Human or machine |
| `observation` | Required; may reference typed records | Reviewer |
| `evidence` | Required, may be empty only with explanation | Reviewer |
| `interpretation` | Required | Reviewer |
| `proposed_disposition` | Required | Reviewer |
| `disposition` | Required after reconciliation | Authorized actor |
| `disposition_reason` | Required for MAYBE or overrides | Authorized actor |
| `created_at`, `updated_at` | Required | Generated |
| `history` | Required | Append-only generated events |

Optional fields are `assessment_reference`, `impact`, `confidence`, `action_recommendation`, `authorization_status`, `failure_origin`, `owner`, `related_findings`, `dependencies`, `revisit_conditions`, `reopen_reason`, and `resolution_evidence`. They exist only when useful; priority and severity may be extension fields but never alter disposition meaning.

Use `assessment_reference` instead of copying assessment criteria into every finding. Use `authorization_status` only when an action exists. Use `failure_origin` only when evaluation failed or was materially impaired. A NO preserves why the proposition was contradicted, assumptions, evidence, and reopen conditions. A MAYBE preserves the information gap, current evidence, next evidence needed, and revisit condition where knowable.

History events contain `event_id`, `event_type`, `at`, `actor`, `authority`, `payload`, and `evidence_ids`. Supported event types are `NEW_FINDING`, `EVIDENCE_CONTRIBUTION`, `RELATIONSHIP`, `PROPOSED_DISPOSITION`, `DISPOSITION_REQUEST`, `AUTHORIZATION`, `ASSESSMENT_REVISION`, `REVALIDATION`, `REOPEN_REQUEST`, `SUPERSESSION`, `DUPLICATION`, `CONFLICT`, `DEPENDENCY`, and `RESOLUTION`.

Match possible duplicates by normalized proposition, overlapping scope, and shared evidence identity. Preserve both source contributions when merging. Supersession links records without rewriting either record.

When serializing as YAML, quote `"YES"`, `"NO"`, and `"MAYBE"`. YAML 1.1-compatible parsers may otherwise coerce YES or NO into booleans. Implementations validate the parsed type, not only the visible text.
