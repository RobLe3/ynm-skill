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

## A. Structural validation

Validation confirms that current 1.4.0 candidate files, schemas, lifecycle invariants, and package metadata are internally consistent.
The package checks confirm runtime-conformant files for `dist/ynm` from the manifest, including deterministic file inventory and content. They do not claim deterministic filesystem metadata or archive bytes.

Agent Skills reference validation is a format conformance check; it does not prove independent implementation compatibility.

Automated sanitization checks tracked text for private-path patterns, credential-like assignments, private/internal repository markers, and provider-specific assumptions in normative core files. These checks are heuristic. Broader review for personal data, proprietary material, and licensing suitability remains a manual publication responsibility.

## B. Methodology evaluation

Controlled methodology evaluation asks whether making YNM available changes review behavior. It is separate from structural validity and does not certify universal effectiveness.

## C. Executor-profile evidence

Empirical results apply to the tested model, client, task, fixture, authority, tool, and resource conditions. Provider-neutral contracts do not imply empirically equal behavior across executors.

## D. Independent validation

- `YNM-VAL-001` remains **MAYBE**: no independent third-party implementation report has yet demonstrated compatible YNM record exchange.
- Independent interoperability across additional runtimes remains pending.

Validation evidence is scoped. Passing one category does not imply passing another.

## Empirical evaluation status

The 1.4 cycle completed 200 frozen trigger runs, 40 historical regression executions, and 72 fresh holdout executions across `gpt-5.6-sol` and `gpt-5.6-terra`. All holdout outputs received blinded maintainer-operated adjudication. An initial 72-score adjudication attempt used an incorrect scenario-ID constraint; the complete invalid attempt is retained and a complete replacement adjudication was performed after correcting the evaluation-only schema.

PORTABLE execution improved primary precision, unsupported-claim rate, required-MAYBE recall, and evidence traceability. It nevertheless produced a non-zero false-finding rate, regressed on replication, and exceeded every frozen cost target. Activation was not observable under the frozen instrumentation rule. ACCELERATED execution was not run because project-scoped semantic retrieval and isolated memory did not pass smoke validation. The 1.4 effectiveness, cost, and replication gates are therefore NO; activation and acceleration remain MAYBE. See [the 1.4 empirical summary](evaluations/1.4/results/summary.md).

This is evidence that YNM can improve review quality under some tested conditions, together with evidence that those improvements are not universal across the tested executors. Several known 1.3 regressions were corrected, but zero-error behavior, acceptable execution overhead, safe cross-model non-inferiority, observable activation, and acceleration effectiveness were not established. The historical dispositions remain unchanged.

This availability probe and any later maintainer-operated runs do not constitute independent interoperability evidence.

## Bounded usability assessment

`YNM-BRP-1` was evaluated on 12 fresh frozen fixtures using `gpt-5.6-sol`, with `gpt-5.6-terra` reported separately as non-gating executor-profile evidence. Both completed all fixtures without authority violations or escaped containment failures. The primary missed the frozen required-MAYBE criterion on the semantic-limit fixture, so bounded usability is **NO** and 1.4.0 remains a release candidate. The frozen fixture interpretation and its post-execution limitation are retained in [the BRP-1 result](evaluations/brp-1/results/summary.md).

## Validation evidence snapshot

- `python validation/validate_ynm.py`
- `python validation/validate_release_integrity.py`
- `python -m unittest discover -s tests -v`
- `python scripts/build_skill_package.py --output-dir dist --overwrite`
- `skills-ref validate dist/ynm`
- `skills-ref read-properties dist/ynm`
- `python scripts/run_evaluations.py --probe`
