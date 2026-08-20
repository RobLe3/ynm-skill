# Releasing YNM

The candidate pull request prepares a release; it does not authorize publication. A maintainer completes the following steps only after the candidate is merged and a human has approved the release.

1. Create a release-finalization commit on `main` that changes `CHANGELOG.md` from `Unreleased` to the actual date and changes publication state from `CANDIDATE` / `REQUIRES_HUMAN` to `READY_FOR_TAG` / `AUTHORIZED_BY_HUMAN`.
2. Run the repository, release-integrity, package, security, and Agent Skills reference checks.
3. Create the immutable annotated tag `v<version>` at the finalized commit. Never force-update a release tag.
4. Wait for tag CI to verify the exact tag, commit, tree, mainline reachability, and finalized publication state.
5. Publish a GitHub Release only after tag CI passes and a maintainer makes that separate decision.

Historical tags are immutable. A correction to release evidence is appended in a later version rather than rewriting a published tag or its files.
