# Review Plan Contract

A Review Plan records the execution basis established during Analysis. It complements the Execution Context: the context describes executor capability, while the plan applies that capability to one requested objective.

Required fields are `id`, `revision`, `objective`, `requested_scope`, `effective_scope`, `project_context`, `execution_context`, `available_evidence`, `unavailable_evidence`, `applicable_loops`, `excluded_loops`, `dependencies`, `authority_constraints`, `persistence_mode`, `assessments`, `iteration_policy`, `created_at`, and `change_reason` for revisions after 1.

`iteration_policy.max_immediate_iterations` is optional and, when present, must be a positive integer. It is a safety ceiling, not a required pass count. The plan may reference existing project-context, execution-context, and assessment records rather than duplicating them.

When material conditions change, append a new revision with the affected scope and reason. Prior revisions remain reconstructable. Changing the Review Plan does not automatically change a finding, assessment, disposition, or authorization.
