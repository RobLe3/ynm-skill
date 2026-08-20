# Releasing YNM

YNM 1.4.0 is authorized for publication as a bounded Research/Experimental Pre-release. Green repository CI is necessary but does not establish universal effectiveness, certification, or publication authority.

## Release classes

- **Stable Release:** the conventional publication channel.
- **Research Release:** a reproducible experimental implementation published with measured strengths, adverse results, and explicit operating boundaries.
- **Development Candidate:** an unpublished work item.

A Research Release may publish a useful bounded artifact while broader empirical findings remain `NO` or `MAYBE`, provided its claims do not contradict the evidence. This distinction does not rewrite historical assessments.

## Research Release requirements

A maintainer may publish a Research Release only when repository, package, security, authority, sanitization, and Agent Skills checks pass; the public documentation discloses known empirical failures and cost; no known mutation defect is hidden; and a human explicitly authorizes publication. Research Release status does not authorize certification, autonomous mutation, deployment, or publication by downstream users.

## Procedure

1. Merge the approved candidate.
2. Create a release-finalization commit on `main` that dates the changelog and changes publication state from `CANDIDATE` / `REQUIRES_HUMAN` to `READY_FOR_TAG` / `AUTHORIZED_BY_HUMAN`.
3. Run repository, release-integrity, package, security, sanitization, and Agent Skills checks.
4. Create immutable annotated tag `v<version>` at the finalized commit. Never force-update a release tag.
5. Wait for tag CI to verify the exact tag, commit, tree, mainline reachability, package, security gates, and finalized publication state.
6. Publish the GitHub release only after tag CI passes. Mark an experimental Research Release as a pre-release.
7. Record publication afterward without rewriting the tag.

Historical tags are immutable. Corrections are appended in a later commit or version.

## Claims and evidence

YNM 1.4.0 is released as bounded advisory review, not universal review superiority. Its frozen effectiveness, cost, replication, activation, acceleration, and BRP-1 results remain unchanged. A release may support a declared bounded use without claiming exhaustive review, arbitrary semantic correctness, zero false findings, model-independent parity, independent interoperability, or certification.

## Future release work

Before changing behavior after 1.4.0, read [Research Status](docs/RESEARCH_STATUS.md), identify the existing `NO` or `MAYBE` finding addressed, explain expected information gain, choose a new version, and freeze a new Assessment Contract. Known fixtures remain regression evidence rather than independent proof.
