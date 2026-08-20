# YNM Evaluation

YNM's completed empirical cycles are preserved as frozen research evidence:

- **1.3 controlled A/B and trigger evaluation:** [`protocol.yaml`](protocol.yaml), [`scenarios.yaml`](scenarios.yaml), [`rubric.yaml`](rubric.yaml), and [`results/summary.md`](results/summary.md)
- **1.4 adaptive-execution holdout:** [`1.4/protocol.yaml`](1.4/protocol.yaml), [`1.4/holdout.yaml`](1.4/holdout.yaml), [`1.4/rubric.yaml`](1.4/rubric.yaml), and [`1.4/results/summary.md`](1.4/results/summary.md)
- **YNM-BRP-1 bounded usability:** [`brp-1/protocol.yaml`](brp-1/protocol.yaml), [`brp-1/scenarios.yaml`](brp-1/scenarios.yaml), [`brp-1/rubric.yaml`](brp-1/rubric.yaml), and [`brp-1/results/summary.md`](brp-1/results/summary.md)

These fixtures are now known evidence. Future effectiveness claims require a newly frozen holdout rather than tuning against them.

This repository-only harness compares bounded project reviews with and without the generated YNM skill. It is not included in `dist/ynm`.

Protocol revision 2 and the rubric are frozen before execution. Revision 1 did not execute a trigger or benchmark task. Agent-visible fixtures do not contain the ground-truth annotations in `scenarios.yaml`. Treatment and control runs use the same model, tools, prompt, read-only sandbox, and fixture; only YNM availability differs.

Probe the frozen primary and ordered replication candidates before running the suites:

```bash
python scripts/run_evaluations.py --probe
```

The primary experiment proceeds when `gpt-5.6-sol` is available. The first available replication candidate in the frozen order is selected mechanically; unavailable replication does not block the primary experiment.

Run the suites without editing fixtures, expectations, or ground truth:

```bash
python scripts/run_evaluations.py --run-triggers --repetitions 5
python scripts/run_evaluations.py --run-benchmark
python scripts/score_evaluations.py --prepare --score --aggregate
```

Scoring uses deterministic anonymous sample identifiers and a frozen 0/1/2 rubric. The adjudicator is `gpt-5.6-sol` and is labeled `MAINTAINER_OPERATED_BLINDED_MODEL_ADJUDICATION`; this is not independent validation. Raw model output is evidence, not a disposition. Maintainer-operated runs do not resolve `YNM-VAL-001`.

The trigger expectations are frozen in `tests/data/trigger-cases.yaml`. Generic isolated code review, isolated cleanup advice, and weak future references to YNM are non-activating near misses; explicit YNM reviews and specialist invocations remain positive cases.
