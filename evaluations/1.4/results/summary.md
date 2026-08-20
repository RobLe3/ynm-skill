# YNM 1.4 empirical evaluation

The frozen 1.4 holdout does not support release. PORTABLE execution improved several quality dimensions but failed the frozen false-finding/non-inferiority rules and missed every frozen cost target. ACCELERATED execution was not run because project-scoped semantic retrieval and isolated memory did not pass capability validation.

## Holdout aggregates

### gpt-5.6-sol

| Metric | CONTROL | YNM 1.4 PORTABLE |
|---|---:|---:|
| material_recall | 0.9444 | 1.0 |
| material_precision | 0.8056 | 0.9722 |
| unsupported_claim_rate | 0.1111 | 0.0 |
| false_finding_rate | 0.0833 | 0.0278 |
| required_maybe_recall | 0.8333 | 1.0 |
| evidence_traceability | 1.8333 | 2.0 |
| lifecycle_quality | 2.0 | 2.0 |
| completion_quality | 1.6111 | 1.8333 |
| authority_violations | 0 | 0 |

Decision: **NO** — At least one frozen non-inferiority condition failed.

Cost ratios: input 2.3404x; output 2.8158x; elapsed 2.4044x; tools 2.8966x.

### gpt-5.6-terra

| Metric | CONTROL | YNM 1.4 PORTABLE |
|---|---:|---:|
| material_recall | 0.9444 | 0.8889 |
| material_precision | 0.8796 | 0.8241 |
| unsupported_claim_rate | 0.0648 | 0.0463 |
| false_finding_rate | 0.0556 | 0.1296 |
| required_maybe_recall | 0.8333 | 0.8889 |
| evidence_traceability | 1.9444 | 2.0 |
| lifecycle_quality | 2.0 | 1.9444 |
| completion_quality | 1.7222 | 1.5 |
| authority_violations | 0 | 0 |

Decision: **NO** — YNM-140-HOLD-003 increased false material findings relative to its paired control.

Cost ratios: input 1.7173x; output 2.2945x; elapsed 1.8289x; tools 1.6383x.

## Activation

The instrumentation smoke test selected `NOT_OBSERVED`. All 200 trigger executions completed, but activation accuracy and selectivity cannot be claimed from unavailable telemetry. `YNM-140-ACT-001` therefore remains MAYBE.

## Acceleration

Ruflo and RuVector responded, and AST/diff/coverage helpers returned structured results. Project-scoped semantic retrieval did not return a plausible known YNM item, AgentDB lacked an established isolated ephemeral namespace, and local inference failed authentication. ACCELERATED benchmark execution was therefore not attempted.

## Adaptive execution observability

Maximum execution level was textually observable in only 29 of 56 treatment outputs. Among those, 24 reported YNM-1, three YNM-2, and two YNM-3. These partial observations are not a complete execution-distribution estimate. Source-byte, repeated-read, and accelerator-cost metrics were unavailable.

## Dispositions

- `YNM-140-EPI-001`: NO
- `YNM-140-EFF-001`: NO
- `YNM-140-COST-001`: NO
- `YNM-140-ACT-001`: MAYBE
- `YNM-140-ACC-001`: MAYBE
- `YNM-140-REP-001`: NO
- `YNM-VAL-001`: MAYBE

The candidate remains unreleased. Publication authorization remains `REQUIRES_HUMAN`.
