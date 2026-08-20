# YNM Evaluation

This repository-only harness compares bounded project reviews with and without the generated YNM skill. It is not included in `dist/ynm`.

The rubric in `rubric.yaml` is frozen before execution. Agent-visible fixtures do not contain the ground-truth annotations in `scenarios.yaml`. Treatment and control runs use the same model, tools, prompt, read-only sandbox, and fixture; only YNM availability differs.

Probe the exact configured models before running the suites:

```bash
python scripts/run_evaluations.py --probe
```

Run trigger and benchmark evaluations only when every required model is available:

```bash
python scripts/run_evaluations.py --run-triggers --repetitions 5
python scripts/run_evaluations.py --run-benchmark
```

Raw model output is evidence, not a disposition. Maintainer-operated runs do not resolve `YNM-VAL-001` or constitute independent third-party implementation.

The trigger expectations are frozen in `tests/data/trigger-cases.yaml`. Generic isolated code review, isolated cleanup advice, and weak future references to YNM are non-activating near misses; explicit YNM reviews and specialist invocations remain positive cases.
