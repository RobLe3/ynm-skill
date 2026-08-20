# Validation

Current candidate: **YNM 1.3.0 (release candidate)**

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

Validation confirms that current 1.3.0 candidate files, schemas, lifecycle invariants, and package metadata are internally consistent.
The package checks confirm runtime-conformant files for `dist/ynm` from the manifest, including deterministic file inventory and content. They do not claim deterministic filesystem metadata or archive bytes.

Agent Skills reference validation is a format conformance check; it does not prove independent implementation compatibility.

Automated sanitization checks tracked text for private-path patterns, credential-like assignments, private/internal repository markers, and provider-specific assumptions in normative core files. These checks are heuristic. Broader review for personal data, proprietary material, and licensing suitability remains a manual publication responsibility.

## Known limits

- `YNM-VAL-001` remains **MAYBE**: no independent third-party implementation report has yet demonstrated compatible YNM record exchange.
- Independent interoperability across additional runtimes remains pending.

## Empirical evaluation status

The repository contains protocol revision 2, a frozen rubric, and ten controlled A/B fixtures under `evaluations/`. The primary experiment compares the same project, model, tools, task, and read-only authority with and without YNM. It measures finding precision and recall, unsupported conclusions, evidence quality, MAYBE calibration, authority violations, lifecycle behavior, completion quality, tokens, tool calls, and elapsed time.

Revision 1 stopped at a capability boundary and executed no trigger or benchmark task. Revision 2 completed 200 trigger executions and 40 paired benchmark executions on `gpt-5.6-sol` and the mechanically selected replication model, `gpt-5.6-terra`.

The primary aggregate showed modest precision and unsupported-claim improvements, but YNM failed the frozen hard-safety rule on the clean-project fixture by asserting correctness while failing to preserve explicitly unreviewed production evidence. Trigger activation also had material false negatives under the precommitted behavioral-inference rule. Core effectiveness and trigger selectivity are therefore NO for this candidate. See [the empirical summary](evaluations/results/summary.md).

This availability probe and any later maintainer-operated runs do not constitute independent interoperability evidence.

## Validation evidence snapshot

- `python validation/validate_ynm.py`
- `python validation/validate_release_integrity.py`
- `python -m unittest discover -s tests -v`
- `python scripts/build_skill_package.py --output-dir dist --overwrite`
- `skills-ref validate dist/ynm`
- `skills-ref read-properties dist/ynm`
- `python scripts/run_evaluations.py --probe`
