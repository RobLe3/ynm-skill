# Contributing to YNM

Contributions should solve a demonstrated methodology, usability, compatibility, or validation problem.
Describe the proposition, evidence, affected contracts, compatibility effect, and validation performed.

Preserve YES/NO/MAYBE semantics, evidence provenance, execution/disposition/authorization separation, focal responsibility boundaries, history, project neutrality, provider neutrality, and manual execution. A change to core semantics must be declared as breaking; examples cannot redefine contracts.

Project-derived lessons must be abstracted and sanitized. Do not submit private paths,
credentials, personal data, proprietary project evidence, organization-specific policy,
or constants that do not generalize. Update affected examples, schemas, tests, manifest
entries, capability claims, and changelog entries.

Reports should include the YNM version, executor or runtime capabilities relevant to the issue, project type, invocation, focal loop, expected and observed behavior, available evidence, and whether persistence was enabled. Redact project content that is not necessary to reproduce the problem.

## Research contributions

YNM is a published Research Release with active methodology development paused. Useful future contributions include independent implementations or evaluations, new executor-profile evidence, mechanically enforced execution kernels, reliable activation telemetry, project-scoped retrieval, measured cost reduction, real-world case studies, and stronger evaluation methods.

Do not submit benchmark-only prompt tuning, remove adverse evidence, expand methodology without a demonstrated unresolved proposition, or add loops merely for completeness. A behavioral proposal must answer:

1. Which existing unresolved finding does this address?
2. What new information would success provide?
3. How will it be tested without treating known fixtures as fresh independent evidence?

A behavioral change after 1.4.0 must use a new version or candidate; it must not be presented as the evaluated 1.4.0 artifact. Begin a new behavioral cycle with an observed limitation, a new proposition, expected information gain, and a frozen assessment. Preserve historical thresholds, model-selection rules, findings, and provenance.

## Common commands

```text
python -m pip install -e ".[dev]"
python validation/validate_ynm.py
python validation/validate_release_integrity.py
python -m unittest discover -s tests -v
python scripts/build_skill_package.py --output-dir dist --overwrite
```

For Agent Skills format checks:

```text
skills-ref validate dist/ynm
skills-ref read-properties dist/ynm
```
