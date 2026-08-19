# Project Discovery

Discover before judging. Declare the review root, requested scope, read/write authority, time boundary, safe output location, and review profile. Do not assume a repository, source code, Git, GitHub, CI, tests, deployment, APIs, users, AI, or persistent state.

Inventory available evidence and capabilities by function: source inspection, history, validation, runtime access, user feedback, issue history, dependency metadata, benchmarks, architecture records, external specifications, prior YNM state, and mutation. For each material capability record availability, evidence basis, interface or version where relevant, evidence scope, mutation behavior, required authorization, and known reliability. Prefer declared interfaces and observed successful use over executor self-description. Mark uncertainty instead of assuming availability. Note excluded, inaccessible, generated, stale, and contradictory sources. Filenames and documentation are clues, not automatic truth.

Before proposing project integration, map documentation by responsibility rather than filename. Inspect project entry, agent guidance, project context, architecture, contracts, adoption and operations guidance, contribution and security guidance, release and version history, decisions, existing review state, and project-specific instructions. Record confirmed, candidate, and unknown mappings. Existing artifacts and explicit project restrictions take precedence over a default YNM scaffold. Follow [Project Integration](project-integration.md) only when integration is requested or materially useful.

Capability existence is not permission. Mark mutating capabilities and keep them unused in default read-only review. Select evaluation methods only from capabilities actually available and suitable for the proposition.

Characterize complexity and capability-to-scope fit before selecting granularity. Consider artifact and history volume, subsystems, dependencies, coupling, applicable loops, external evidence, effective rather than nominal context capacity, retrieval quality, active findings, tools, and execution budgets. Ask whether this executor can review the requested scope as one coherent unit.

Bound effort proportionally:

- Small: review the complete relevant surface with minimal ceremony.
- Medium: review changed and risk-bearing areas, then sample stable areas.
- Large: partition hierarchically by explicit scope, dependencies, material changes, and risk; report reviewed, unreviewed, and deferred segments.

Determine applicable loops from meaningful propositions, not artifact presence. Assess whether the current executor is suitable for each loop and assign a different specialist, reduced scope, or explicit limitation when needed. Adoption may apply to a policy or research project; Implementation may be `NOT_APPLICABLE` when no realized artifact or procedure exists. Record why a loop was excluded.

If prior state exists, verify its format and provenance before loading it. Compare review scope, relevant project state, assessment revisions, and evidence fingerprints. Classify material differences as subject, assessment, or combined changes and determine whether each old disposition remains valid, requires revalidation, or should reopen. Treat missing old evidence as unavailable historical evidence, not as proof that the previous conclusion was false.
