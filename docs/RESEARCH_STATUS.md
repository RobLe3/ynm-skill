# YNM Research Status

## Current state

**Project state:** PAUSED RESEARCH PROJECT

**Research cycle:** CONCLUDED

**Current version:** 1.4.0

**Publication state:** PUBLISHED RESEARCH RELEASE

**Release class:** EXPERIMENTAL / RESEARCH PRE-RELEASE

**Current profile:** YNM-BRP-1, experimental

YNM 1.4.0 is published as an auditable research checkpoint. It contains an implemented evidence-backed review methodology, deterministic validation, controlled empirical evaluations, and both favorable and adverse results. It is not abandoned or deprecated, but another development cycle is not currently justified by expected information gain.

## Publication interpretation

`v1.4.0` makes the evaluated implementation publicly obtainable as a bounded Research/Experimental Pre-release. Publication does not mean that the frozen 1.4 or BRP-1 contracts passed. It means that the implemented method, reproducible evidence, demonstrated strengths, and measured limitations are useful enough to publish under an explicitly narrower claim. `v1.2.0` remains the previous stable release.

## Purpose

YNM investigated whether explicit propositions, evidence provenance, bounded `YES` / `NO` / `MAYBE` judgments, review lifecycle records, and authority separation could make model-assisted project review more useful and auditable. It also examined whether those benefits could be obtained consistently across executors and at acceptable cost.

The central result is mixed. YNM improved several aspects of bounded review, but methodology instructions alone did not guarantee reliable executor behavior, low execution cost, complete uncertainty preservation, or cross-model equivalence. The current implementation is published as a bounded Research Release while active methodology development remains paused.

## Research progression

### 1.0–1.2: methodology and deterministic foundations

The project developed its review contracts, project integration, packaging, lifecycle, schemas, and deterministic validation. Historical published evidence remains available through the immutable [`v1.2.0` tag](https://github.com/RobLe3/ynm-skill/tree/v1.2.0).

### 1.3: first controlled empirical evaluation

The first controlled A/B work evaluated whether making YNM available changed model-assisted review. It found modest quality improvements, along with false-certainty and authority-boundary regressions, poor observed activation, and roughly 2.5-times execution overhead in the primary measurements.

Canonical evidence:

- [Frozen protocol](../evaluations/protocol.yaml)
- [Frozen scenarios](../evaluations/scenarios.yaml)
- [Rubric](../evaluations/rubric.yaml)
- [Results](../evaluations/results/summary.md)
- [Release state](../state/releases/1.3.0/)

### 1.4: adaptive execution and stronger evidence discipline

YNM added progressive execution, stricter affirmative-evidence requirements, selective escalation, evidence caching, and optional acceleration interfaces. The primary executor improved on several review-quality measures and corrected known failures. The frozen assessment still failed because false findings remained, the replication executor regressed, every cost target was missed, activation was not observable, and acceleration could not be evaluated safely.

Canonical evidence:

- [Assessment protocol](../evaluations/1.4/protocol.yaml)
- [Holdout definition](../evaluations/1.4/holdout.yaml)
- [Rubric](../evaluations/1.4/rubric.yaml)
- [Results](../evaluations/1.4/results/summary.md)
- [Capability discovery](../evaluations/1.4/capability-discovery.yaml)
- [Release state](../state/releases/1.4.0/)

### YNM-BRP-1: bounded-validity formalization

The product claim was narrowed to experimental bounded evidential review. The frozen evaluation found high material usefulness recall, evidence traceability, conclusion inspectability, and authority containment. It failed one required-`MAYBE` criterion, so bounded usability remained `NO` under the frozen contract.

Canonical evidence:

- [Protocol](../evaluations/brp-1/protocol.yaml)
- [Frozen scenarios and ground truth](../evaluations/brp-1/scenarios.yaml)
- [Rubric](../evaluations/brp-1/rubric.yaml)
- [Scoring schema](../evaluations/brp-1/schemas/score.schema.json)
- [Results](../evaluations/brp-1/results/summary.md)
- [Machine-readable assessment](../state/releases/1.4.0/bounded-final-assessment.yaml)

### Current checkpoint

Development is paused. The candidate and all evaluation evidence are retained so future work can begin from the observed limitations rather than reconstructing the research history.

## Main findings

### Demonstrated strengths

The tested implementation provided evidence for:

- proposition-centered review;
- traceable evidence and source ancestry;
- explicit reviewed and unreviewed scope;
- separation of review, recommendation, authorization, execution, persistence, and publication;
- bounded affirmative-evidence requirements and negative claims;
- append-only findings and frozen Assessment Contracts;
- useful uncertainty records through `MAYBE`;
- validity boundaries and information-gain-based stopping;
- strong primary-executor material usefulness recall and inspectability; and
- deterministic repository, package, and security-boundary validation.

These concepts form a reusable integrated research artifact. This document does not claim that they originated uniquely in YNM.

### Demonstrated failures

The frozen assessments recorded:

- false certainty and false findings in tested scenarios;
- incomplete uncertainty preservation;
- executor-dependent behavior and failed cross-model non-inferiority;
- substantial execution overhead;
- poor or unobservable activation behavior;
- no demonstrated acceleration savings; and
- failure of the frozen 1.4 general-effectiveness and BRP-1 usability contracts. These results remain unchanged by the narrower Research Release classification.

The authoritative dispositions remain in [`state/releases/1.4.0/findings.yaml`](../state/releases/1.4.0/findings.yaml). They must not be reclassified by summary prose.

### Unresolved questions

`YNM-140-ACT-001`, `YNM-140-ACC-001`, and `YNM-VAL-001` remain `MAYBE`. Reliable activation telemetry, isolated acceleration evidence, and independent interoperability have not been established.

## BRP-007 interpretation

The frozen BRP-007 fixture required a bounded `MAYBE` for a universal termination proposition. Both tested executors returned `NO`. Post-execution analysis identified a plausible interpretation in which a concrete counterexample can refute that universal proposition.

Changing ground truth after observing execution would violate the frozen evaluation protocol. The adverse result therefore remains authoritative for that assessment. At the same time, the interpretive issue is retained as a limitation of the fixture and evaluation design. This does not make the BRP-1 assessment a pass.

## Why development paused

Further prompt and methodology iterations were producing diminishing information gain. The research established useful bounded-review behavior, but it also demonstrated executor dependence, high execution cost, and remaining uncertainty-preservation errors. Continuing to tune against known fixtures would risk benchmark-specific optimization without resolving execution control or generalization.

Improvement is not assumed to be impossible. Another cycle is deferred until a new capability or evidence source creates a credible chance of answering a materially different proposition.

## Conditions that could justify restarting development

A restart assessment may be worthwhile if one or more of these conditions appears:

- **Better execution control:** a runtime can mechanically enforce execution levels, evidence gates, budgets, specialist routing, and activation telemetry.
- **Lower-cost bounded execution:** deterministic mechanisms can enforce more of YNM without repeatedly supplying the full method as model context.
- **Reliable scoped retrieval:** Ruflo, RuVector, AgentDB, or an equivalent system provides demonstrable project isolation, provenance preservation, contamination control, and measurable net savings.
- **New executor generations:** a model or runtime materially improves instruction adherence, uncertainty calibration, structured output, or low-cost context handling.
- **Independent implementation:** an external implementation or evaluation supplies qualitatively different evidence and can begin addressing `YNM-VAL-001`.
- **Better evaluation methods:** activation, execution depth, hidden cost, model effect, and methodology effect can be separated more reliably.
- **A practical use case:** a real project demonstrates longitudinal or evidentiary value not represented by the synthetic fixtures.

No condition automatically restarts development. It justifies a new expected-information-gain assessment.

## Where future work should start

1. Read the repository [README](../README.md).
2. Read this checkpoint and [Epistemic Boundaries](../methodology/epistemic-boundaries.md).
3. Read [Validation](../VALIDATION.md).
4. Inspect the frozen [1.3 results](../evaluations/results/summary.md).
5. Inspect the frozen [1.4 results](../evaluations/1.4/results/summary.md).
6. Inspect the frozen [YNM-BRP-1 results](../evaluations/brp-1/results/summary.md).
7. Read [SKILL.md](../SKILL.md) and the current runtime contracts.
8. Review all open `NO` and `MAYBE` findings before proposing a change.
9. State which observed limitation a new hypothesis addresses and what information success would add.
10. Freeze a new Assessment Contract and fresh holdout before changing behavior.

## If development resumes

Treat the 1.3, 1.4, and BRP-1 fixtures as known regression evidence, not independent proof of a later candidate. Do not begin by tuning YNM until old benchmarks pass.

Do not:

- erase or rewrite previous `NO` or `MAYBE` findings;
- move acceptance thresholds after seeing results;
- optimize exclusively against historical fixtures;
- select models based on benchmark performance;
- treat repository validation as empirical effectiveness;
- treat provider-neutral design as provider-independent evidence; or
- claim acceleration savings without controlled ablation.

Use this continuation discipline:

```text
OBSERVED LIMITATION
        ↓
NEW PROPOSITION
        ↓
EXPECTED INFORMATION GAIN
        ↓
FROZEN ASSESSMENT
        ↓
IMPLEMENTATION
        ↓
FRESH HOLDOUT
        ↓
EVIDENCE
```
