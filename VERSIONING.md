# Versioning

YNM uses Semantic Versioning for its public contracts and operational behavior.

- **Major:** incompatible changes to disposition meaning, required records, lifecycle transitions, loop ownership, authority, or invocation behavior.
- **Minor:** backward-compatible methods, optional contracts, focal-loop extensions, or operational capabilities.
- **Patch:** corrections and clarifications that do not add behavior or alter compatible records.

## Current candidate

`1.2.0` adds a backward-compatible invocation lifecycle and lifecycle-aware records without changing core review semantics. Existing receipts remain valid; new v2 receipts make Analysis, Iteration, mandatory Delivery, scope, convergence, and stop reasons explicit.

## Historical baseline

`1.0.0` is the immutable production-maturity baseline. Its frozen assessment, findings, receipts, gates, and final disposition are not retroactively evaluated against 1.1.0 requirements.

`1.1.0` is the immutable Project Integration and publication-readiness baseline. Its report and release state are protected by the 1.2.0 baseline hashes.
