# Validation

Current candidate: **YNM 1.4.0 (unreleased candidate; empirical release gate failed)**

## Deterministic validation status

| Area | Status |
|---|---|
| Repository and schema validation | PASS |
| Release integrity validation | PASS |
| Unit tests | PASS |
| Package build and deterministic signature | PASS |
| Package reference-form validation | PASS |
| Security-boundary checks | PASS |
| Public tracked-text sanitization | PASS |

## What these results mean

Validation confirms that current 1.4.0 candidate files, schemas, lifecycle invariants, and package metadata are internally consistent.
The package checks confirm runtime-conformant files for `dist/ynm` from the manifest, including deterministic file inventory and content. They do not claim deterministic filesystem metadata or archive bytes.

Agent Skills reference validation is a format conformance check; it does not prove independent implementation compatibility.

Automated sanitization checks tracked text for private-path patterns, credential-like assignments, private/internal repository markers, and provider-specific assumptions in normative core files. These checks are heuristic. Broader review for personal data, proprietary material, and licensing suitability remains a manual publication responsibility.

## Known limits

- `YNM-VAL-001` remains **MAYBE**: no independent third-party implementation report has yet demonstrated compatible YNM record exchange.
- Independent interoperability across additional runtimes remains pending.

## Empirical evaluation status

The 1.4 cycle completed 200 frozen trigger runs, 40 historical regression executions, and 72 fresh holdout executions across `gpt-5.6-sol` and `gpt-5.6-terra`. All holdout outputs received blinded maintainer-operated adjudication. An initial 72-score adjudication attempt used an incorrect scenario-ID constraint; the complete invalid attempt is retained and a complete replacement adjudication was performed after correcting the evaluation-only schema.

PORTABLE execution improved primary precision, unsupported-claim rate, required-MAYBE recall, and evidence traceability. It nevertheless produced a non-zero false-finding rate, regressed on replication, and exceeded every frozen cost target. Activation was not observable under the frozen instrumentation rule. ACCELERATED execution was not run because project-scoped semantic retrieval and isolated memory did not pass smoke validation. The 1.4 effectiveness, cost, and replication gates are therefore NO; activation and acceleration remain MAYBE. See [the 1.4 empirical summary](evaluations/1.4/results/summary.md).

This availability probe and any later maintainer-operated runs do not constitute independent interoperability evidence.

## Validation evidence snapshot

- `python validation/validate_ynm.py`
- `python validation/validate_release_integrity.py`
- `python -m unittest discover -s tests -v`
- `python scripts/build_skill_package.py --output-dir dist --overwrite`
- `skills-ref validate dist/ynm`
- `skills-ref read-properties dist/ynm`
- `python scripts/run_evaluations.py --probe`
