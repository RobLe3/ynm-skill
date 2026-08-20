# Releasing YNM

There is currently no authorized YNM 1.4.0 release. The project is paused after the 1.4 and YNM-BRP-1 evaluations, and the current candidate is not recommended for release. Green repository CI is necessary but not sufficient publication evidence.

The candidate pull request prepares a release; it does not authorize publication. A maintainer completes the following steps only after the candidate is merged and a human has approved the release.

1. Create a release-finalization commit on `main` that changes `CHANGELOG.md` from `Unreleased` to the actual date and changes publication state from `CANDIDATE` / `REQUIRES_HUMAN` to `READY_FOR_TAG` / `AUTHORIZED_BY_HUMAN`.
2. Run the repository, release-integrity, package, security, and Agent Skills reference checks.
3. Create the immutable annotated tag `v<version>` at the finalized commit. Never force-update a release tag.
4. Wait for tag CI to verify the exact tag, commit, tree, mainline reachability, and finalized publication state.
5. Publish a GitHub Release only after tag CI passes and a maintainer makes that separate decision.

Historical tags are immutable. A correction to release evidence is appended in a later version rather than rewriting a published tag or its files.

## Claims required for a bounded release

Release decisions distinguish methodology usability, general effectiveness, and certification. A release may support a declared bounded profile without claiming universal effectiveness or certification.

For `YNM-BRP-1`, require repository and package integrity, security-boundary tests, Agent Skills conformance, read-only authority behavior, bounded `YES` semantics, clean-project restraint, bounded-negative behavior, explicit `MAYBE` preservation, visible Delivery limitations, and honest documentation of empirical limits. Do not require or claim exhaustive review, universal semantic correctness, zero possible future findings, self-proof of independent validity, or model-independent parity.

Release readiness does not grant publication authorization. YNM-BRP-1 remains advisory and cannot independently authorize security or safety certification, legal compliance, production release, destructive migration, publication, or autonomous mutation.

## Restarting release work

Before proposing a future release, read [Research Status](docs/RESEARCH_STATUS.md), identify the existing `NO` or `MAYBE` finding addressed by the new hypothesis, explain its expected information gain, and freeze a new Assessment Contract. Behavioral changes require fresh holdout evidence; known 1.3, 1.4, and BRP-1 fixtures remain regression evidence rather than independent proof.

Preserve all historical assessments and dispositions. Do not treat a green deterministic suite, provider-neutral contracts, or improved performance on known fixtures as release authorization.
