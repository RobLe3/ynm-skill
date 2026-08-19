# Architecture Loop

**Purpose:** Evaluate whether intended structure is internally coherent and consistent with declared architecture.

- **Scope:** boundaries, decomposition, dependencies, interfaces, data and control flow, constraints, decisions, cross-cutting concerns, and architectural drift.
- **Inputs and evidence:** declared intent, decision records, specifications, dependency or structure views, configuration, and implementation evidence needed to test architectural claims.
- **Owns:** findings whose proposition concerns architectural coherence or conformance.
- **Observes:** implementation and operations where they reveal architecture.
- **May recommend:** implementation changes, decision clarification, or explicit architecture changes.
- **May not decide:** that undocumented implementation automatically becomes intended architecture, or that a code defect is resolved.
- **Must hand off:** implementation correctness defects to Implementation; user-facing consequences to Adoption; stale architecture artifacts to Maintenance.
- **Finding types:** contradiction, boundary violation, undeclared dependency, incoherent decision, drift, or unresolved intent.
- **Output:** canonical findings, evidence contributions, handoffs, and one loop result.
- **Termination:** all selected architectural propositions were evaluated or explicitly blocked.
- **Rerun:** architecture, relevant implementation, or an authoritative decision materially changes.
- **Failure modes:** generic code review, treating diagrams as truth, silently inventing architecture, or widening scope without risk justification.

