# Implementation Loop

**Purpose:** Determine whether realized behavior correctly implements declared intent and contracts.

- **Scope:** correctness, contract adherence, tests, errors, edges, state, APIs, concurrency, resources, consistency, and dead or contradictory realization. “Implementation” includes procedures and realized artifacts, not only code.
- **Inputs and evidence:** requirements, specifications, examples, executable artifacts, tests, observations, configurations, and failure records.
- **Owns:** findings whose proposition concerns realized behavior or contract fulfillment.
- **Observes:** architecture to understand intent and user evidence to identify behavioral consequences.
- **May recommend:** fixes, tests, safeguards, or contract clarification.
- **May not decide:** that observed behavior redefines architecture or product intent.
- **Must hand off:** incoherent intent to Architecture; usability barriers to Adoption; sustainability debt to Maintenance.
- **Finding types:** incorrect behavior, missing realization, contract mismatch, unhandled condition, inadequate validation, or contradictory paths.
- **Output:** canonical findings, contributions, handoffs, and one loop result.
- **Termination:** selected contracts and behaviors were evaluated to the declared depth.
- **Rerun:** relevant implementation, contract, or reproducibility evidence changes.
- **Failure modes:** equating passing tests with correctness, aesthetic refactoring, assuming code exists, or resolving ambiguity through invention.

