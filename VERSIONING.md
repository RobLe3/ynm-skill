# Versioning

YNM uses Semantic Versioning for its public contracts and operational behavior.

- **Major:** incompatible changes to disposition meaning, required records, lifecycle transitions, loop ownership, authority, or invocation behavior.
- **Minor:** backward-compatible methods, optional contracts, focal-loop extensions, or operational capabilities.
- **Patch:** corrections and clarifications that do not add behavior or alter compatible records.

## Current candidate

`1.3.0` is a backwards-compatible release-candidate set of hardening and packaging work. It adds explicit iteration-stop reasons, stricter project-integration security boundaries, release-integrity evidence, and package-construction determinism.

The existing core semantics, run-receipt contract shape, and focal-loop ownership model are preserved.

## Historical baseline

`1.0.0` is the immutable historical maintainer-assessed baseline. Its frozen assessment,
findings, receipts, gates, and final disposition are not retroactively evaluated against
`1.1.0` or later revision criteria.

`1.1.0` is the immutable Project Integration and publication-readiness baseline. Its report and release state are preserved in immutable release evidence.
