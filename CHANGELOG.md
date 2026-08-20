# Changelog

All notable YNM changes are recorded here. Historical release and maturity evidence remains available through immutable Git history and release tags.

## [1.3.0] - Unreleased

### Added

- Canonical `ANALYSIS → ITERATION → DELIVERY` invocation lifecycle and mandatory terminal Delivery behavior.
- Lifecycle-aware Review Plan and v2 run-receipt fields.
- Scoped reanalysis, bounded iteration policy, and explicit continuation-stop reasons.
- Security-boundary hardening for project integration, including path normalization, symlink checks, ownership parsing, and rollback reporting.
- Deterministic packaging workflow, manifest-driven packaging tests, and release-integrity checks.
- Release-candidate correction record for unresolved 1.2 publication timestamp causality.
- Frozen trigger and ten-task A/B evaluation fixtures for measuring review effectiveness without changing the runtime package.
- Decomposed the unexecuted empirical gate into primary effectiveness, trigger selectivity, and non-blocking cross-model replication before observing outcomes.
- Current-candidate evidence-locator validation and a project-native self-bootstrap receipt.

### Changed

- Clarified public candidate status and publication readiness versus publication authority.
- Tightened near-miss trigger expectations for isolated code review, cleanup advice, and weak contextual references.
- Marked empirical two-model effectiveness evaluation as blocked rather than inferring results from internal consistency tests.

### Preserved

- YES/NO/MAYBE semantics, focal-loop ownership, read-only defaults, capability and authority separation.
- Project integration behavior and complete 1.0.0–1.2.0 maturity history.

### Removed

- Historical development and self-review artifacts from current HEAD; historical evidence remains available via Git history and immutable tags.

### [1.2.0] - 2026-08-19

- Canonical `ANALYSIS → ITERATION → DELIVERY` invocation lifecycle was introduced and documented.
- Portable Review Plan and lifecycle-aware Run Receipt fields were added.
- Scoped reanalysis and public-publication validation guidance were added.
- Repository onboarding and independent-evaluation guidance was formalized.

### [1.1.0] - 2026-08-19

- Authorization-gated, idempotent Project Integration with documentation-role discovery and optional persistent state.
- Project context, configuration, and bootstrap receipt contracts and schemas.
- Provider-neutral publication manifest, installation verification, sanitization, contribution, and release-readiness guidance.
- Bootstrap and publication adversarial validation and deterministic integration tests.

### [1.0.0] - 2026-08-19

- First maintainer-assessed YNM maturity milestone. Historical maturity evidence remains
  available through the 1.0.0 release artifacts and immutable Git tags.
