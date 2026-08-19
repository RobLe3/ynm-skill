# Research Project Example

Scope: a study containing a protocol, data, analysis notebooks, and a manuscript.

- Architecture evaluates whether the research question, protocol, variables, and analysis plan form a coherent design.
- Implementation evaluates whether the recorded procedure and analysis realize that design.
- Adoption evaluates whether another researcher can understand and reproduce the study from the available package.
- Maintenance evaluates provenance, dependency longevity, dataset availability, and stale manuscript references.

Two loops evaluate related but distinct propositions. Implementation proposes YES for “The analysis notebook implements the registered exclusion rule.” Adoption proposes NO for “An independent researcher can identify and run the registered exclusion rule.” These do not conflict: one concerns realized behavior and the other reproducibility. If both instead evaluate the same proposition with opposing evidence, a `CONFLICT` event preserves both proposals and Disposition leaves MAYBE until reconciliation.

If participant data cannot be disclosed, the review records the authority and privacy limit. It does not treat inaccessible data as proof against the study. Stateless execution is allowed, but the report states that a six-month reproducibility revisit cannot be correlated automatically.

Three reports that quote the same protocol registry retain a shared evidence parent and do not count as three independent confirmations. A claim that reproducibility “improved” remains MAYBE if no stable earlier package or measurement context exists. A future reassessment of a previous NO names the new dataset, corrected method, or other material change expected to reduce uncertainty.

If a later executor has broader data tooling, it records a new execution context and appends measurements the earlier reviewer could not obtain. The earlier result remains the historical outcome of its bounded evidence window. Differences are reconciled through normal evidence and disposition events rather than treating the newer executor as automatically authoritative.
