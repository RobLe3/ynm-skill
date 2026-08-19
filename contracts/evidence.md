# Evidence Contract

Evidence is a traceable representation of something observed or measured for evaluating a proposition. Inferences and hypotheses may refer to evidence but are not silently promoted into direct evidence. Store references and bounded excerpts rather than unsupported conclusions.

## Evidence record

Required: `id`, `epistemic_type`, `kind`, `locator`, `content`, `captured_at`, `availability`, and `provenance`. Generated identifiers and fingerprints are allowed. Optional: `revision`, `section`, `symbol`, `collector`, `method`, `scope`, `quality`, `directness`, `corroboration`, `reproducible`, `replayable`, `independence`, `observed_at`, `project_revision`, `integrity_reference`, `parent_evidence`, `valid_from`, `valid_until`, and `related_evidence`.

`kind` may describe source code, specification, test, decision record, documentation, configuration, automated check, release metadata, issue history, runtime observation, generated report, dependency state, project instruction, user-visible behavior, or external decision. Implementations may extend this vocabulary without changing disposition semantics.

## Epistemic types

- `OBSERVATION`: something directly encountered in available project evidence.
- `MEASUREMENT`: a value produced through a defined method; retain method, conditions, sample, and units where relevant.
- `INFERENCE`: a conclusion derived from identified observations or measurements; retain the inference rule and inputs.
- `HYPOTHESIS`: a proposition introduced for investigation but not sufficiently established.

Unknown, unavailable, contradictory, obsolete, or insufficient knowledge is represented through availability, limitations, MAYBE reasons, and lifecycle events rather than as a fifth epistemic type. `OBSERVATION`, `MEASUREMENT`, `INFERENCE`, and `HYPOTHESIS` are not interchangeable; none is a disposition or authorization.

Evidence quality is multi-dimensional. Confidence may summarize uncertainty, but it does not replace provenance, directness, reproducibility, ancestry, or suitability. Distinguish evidence existence from sufficiency for a particular proposition and from sufficiency to authorize an action.

Evidence that descends from one source is not independent corroboration. Preserve ancestry where practical: a report quoting a document and a summary quoting that report remain one underlying source lineage. Conflicting records remain present and linked by a `CONFLICT` event. An unavailable or deleted source changes availability; it does not erase the old observation or prove the opposite.
