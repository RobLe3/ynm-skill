# Publication Readiness

Publication packages YNM; it does not define YNM semantics or authorize release actions.

## Artifact classes

- **Normative:** `SKILL.md`, contracts, loops, and methodology. These define behavior.
- **Optional:** schemas, scripts, examples, adapters, persistence, and audit mechanisms.
- **Packaging:** manifest, README, license, version, changelog, and contribution guidance.
- **Provenance:** extraction, generalization, comparison, and historical reports. Runtime use must not depend on them.
- **Validation:** tests, fixtures, assessment state, receipts, and failure evidence. They support claims but do not redefine contracts.

The installable package contains the entrypoint and its normative dependencies plus any scripts or schemas required by the selected operation. Removing provenance and historical validation must not change runtime semantics.

## Capability claims

Public claims use these labels:

- `VALIDATED`: directly exercised by recorded evidence.
- `SUPPORTED_BY_DESIGN`: specified and internally checked but not independently exercised in the claimed environment.
- `PARTIALLY_VALIDATED`: some material paths were exercised and limits are named.
- `NOT_VALIDATED`: no sufficient validation evidence exists.
- `KNOWN_LIMITATION`: evidence identifies a bounded deficiency.

Theoretical support is not reported as validated. A runtime-adapter failure is scoped to that adapter unless it reveals a methodology defect.

## Project-derived improvements

Keep project findings separate from methodology defects. A reusable YNM change requires:

1. evidence of a methodology deficiency;
2. a generalized proposition;
3. the smallest reusable correction;
4. removal of project names, private paths, credentials, personal data, proprietary evidence, and task-specific constants;
5. contract-impact analysis;
6. targeted validation;
7. regression review.

Project lessons cross an abstraction, sanitization, generalization, and validation boundary before entering public YNM. A project receiving NO or MAYBE is not by itself evidence that YNM must change.

## Release readiness

Before preparing a candidate, verify manifest paths, version agreement, schemas and examples, internal links, public-path sanitization, provider neutrality, licenses, known limitations, and installation instructions. Preserve useful failure → finding → correction → regression-test records when they contain no private material.

YNM may validate readiness, recommend a version, prepare notes, and build a temporary package. Commit, tag, push, publication, and release creation require separate explicit authorization.
