# YNM — YES / NO / MAYBE

YNM is a bounded evidence-backed review methodology for projects and agent-assisted engineering. Instead of reducing a review to “looks good,” “probably ready,” or one overall score, YNM turns important conclusions into explicit propositions, connects them to traceable evidence, and returns one of three bounded dispositions:

- **YES** — sufficient evidence supports the proposition within the reviewed boundary.
- **NO** — sufficient evidence contradicts the proposition.
- **MAYBE** — available evidence cannot responsibly decide the proposition.

YNM separates what is known, what is contradicted, what remains unresolved, what was not reviewed, and what authority exists to act on the result.

> **Current version: 1.4.0 — Research Release**
>
> YNM 1.4.0 is usable for bounded, advisory project review. It is experimental, can be substantially more expensive than ordinary review, and has not demonstrated equal effectiveness across all models or runtimes.

| Item | State |
| --- | --- |
| Current version | 1.4.0 |
| Release class | Research / Experimental |
| Development state | Paused |
| Latest release | [`v1.4.0`](https://github.com/RobLe3/ynm-skill/releases/tag/v1.4.0) |
| Previous release | [`v1.2.0`](https://github.com/RobLe3/ynm-skill/releases/tag/v1.2.0) |
| License | Apache-2.0 |

![YNM bounded review workflow](https://raw.githubusercontent.com/RobLe3/ynm-skill/main/docs/assets/ynm-overview.svg)

## What YNM helps you do

YNM helps a reviewer:

- check whether implementation matches architecture, documentation, or a specification;
- distinguish confirmed behavior from unsupported assumptions;
- review release readiness without treating passing tests as production proof;
- retain unresolved questions instead of forcing premature conclusions;
- identify the evidence behind each material conclusion;
- separate architecture, implementation, adoption, and maintenance concerns;
- expose reviewed and unreviewed scope;
- preserve findings and disposition changes across review cycles;
- separate analysis from authority to modify, merge, deploy, or publish; and
- stop honestly when required evidence is unavailable.

## A 30-second example

A conventional review may conclude:

> The release looks ready.

YNM separates that judgment:

| Proposition | Result | Why |
| --- | --- | --- |
| Implementation matches the declared API | **YES** | Code and tests match the reviewed specification |
| Required recovery procedure exists | **NO** | Required operator documentation is absent |
| Production failover preserves security behavior | **MAYBE** | Production failover evidence was unavailable |
| Publication is authorized | **NO / NOT AUTHORIZED** | Review authority does not grant publication authority |

The result preserves what is supported, what failed, what remains unknown, and what the review did not authorize.

## What YNM gives you

- **Traceable evidence:** findings attach to explicit propositions and source references.
- **First-class uncertainty:** `MAYBE` records why a material question remains unresolved.
- **Visible scope:** reviewed and unreviewed areas remain distinct.
- **Authority containment:** review, recommendation, authorization, execution, persistence, and publication are separate.
- **Longitudinal findings:** provenance, prior dispositions, conflicts, reopenings, supersessions, and resolution history can be retained.
- **Honest completion:** convergence is distinct from exhaustion, missing evidence, and blocked execution.
- **Provider-neutral contracts:** humans, agents, and tools can follow the method without requiring one provider or runtime.

## Why YNM exists

Tests and linters answer bounded mechanical questions. Checklists improve repeatability. Human and model-assisted reviews provide interpretation. YNM adds explicit propositions, evidence provenance, scope boundaries, uncertainty, and terminal Delivery records so later decisions can be made with a visible basis.

YNM complements rather than replaces tests, domain checks, formal verification where appropriate, operational evidence, and domain expertise.

## Should I use YNM?

YNM is a good fit when the cost of an ambiguous review is higher than the cost of additional analysis. Use it when you need traceable evidence, explicit uncertainty, reviewed and unreviewed scope, repeatable findings, or separation between review and authority.

A simpler review is often preferable when the question is deterministic, the task is small, auditability is unnecessary, or token and tool cost matter more than added review structure. YNM 1.4 trades substantially more computation for stronger review structure. That tradeoff should be intentional.

## When to use YNM

Use YNM experimentally, with a human retaining consequential authority, for:

- architecture-versus-implementation or specification-versus-code review;
- bounded release-readiness and audit-oriented analysis;
- recurring project reviews across releases;
- incomplete, conflicting, or evolving evidence;
- explicit scope definition and rerun justification;
- controlled agent workflows where write authority must remain explicit;
- adoption and maintenance reviews; and
- comparative research into model-assisted review.

For consequential work, YNM should complement tests, expert review, formal verification where applicable, security analysis, operational evidence, and human release authority. It is not an autonomous production release gate.

## When not to use YNM

Use a simpler method for syntax checks, formatting, trivial edits, general summaries, deterministic questions, or reviews where the extra process cost is unjustified. Do not use YNM as the sole basis for security, safety, legal, production, migration, deployment, or publication decisions, particularly where the executor has not been evaluated for the consequence involved.

## Quick start

Ask for a bounded project review:

```text
Review this project using YNM. Evaluate whether the implementation matches the documented API, cite the evidence, state unreviewed scope, and retain unresolved production behavior as MAYBE.
```

YNM follows one macro lifecycle:

```text
ANALYSIS → ITERATION → DELIVERY → TERMINATED
```

Review is read-only by default. Persistence and project mutation require explicit authorization.

## YES / NO / MAYBE

- **YES:** sufficient affirmative evidence supports an explicit proposition under the stated scope and assessment conditions. It is not universal proof.
- **NO:** sufficient evidence contradicts an explicit proposition under those conditions. It does not invalidate the entire project.
- **MAYBE:** available evidence cannot responsibly decide the proposition because evidence is missing, conflicting, inaccessible, ambiguous, or outside the execution boundary.

`MAYBE` is an expected terminal result, not low confidence disguised as a conclusion.

## Analysis, Iteration, and Delivery

- **ANALYSIS:** define objective, proposition, scope, evidence needs, authority, capability, and limits.
- **ITERATION:** gather relevant evidence and continue only while another pass has credible information value.
- **DELIVERY:** return dispositions, evidence, reviewed and unreviewed scope, limits, authority, and revisit conditions.

Delivery is mandatory. It records how the review ended; it does not imply approval or authorization. See [Invocation Lifecycle](methodology/execution-lifecycle.md) and [Review Plan](contracts/review-plan.md).

## Bounded validity

Every YNM disposition applies only to its proposition, reviewed scope, available evidence, assessment criteria, executor capability, authority, resource limits, and evidence snapshot.

YNM cannot guarantee exhaustive discovery, decide arbitrary semantic properties of arbitrary software, or create independent validation through self-review. Therefore:

- convergence does not prove that nothing else could be discovered;
- absence of contradictory evidence is not automatically affirmative evidence;
- missing material evidence remains `MAYBE`;
- unreviewed scope remains unreviewed;
- repository evidence does not automatically establish production behavior; and
- provider-neutral design does not imply equal effectiveness across models or runtimes.

The normative boundaries are defined in [Epistemic Boundaries](methodology/epistemic-boundaries.md). `YNM-BRP-1` covers experimental, read-only, advisory project review with explicit or decomposable propositions and traceable evidence.

## Validation and empirical evidence

Repository, package, Agent Skills, and deterministic security-boundary checks pass. These establish structural consistency, not universal review effectiveness.

On the controlled 1.4 fresh holdout, the primary tested executor (`gpt-5.6-sol`) produced:

| Measure | YNM 1.4 PORTABLE |
| --- | ---: |
| Material finding recall | 1.0000 |
| Material finding precision | 0.9722 |
| Unsupported-claim rate | 0.0000 |
| Required-MAYBE recall | 1.0000 |
| Evidence traceability | 2.0000 / 2 |
| Authority violations | 0 |

These are benchmark-specific executor-profile results, not guarantees. The replication executor did not satisfy the frozen non-inferiority criteria.

### Execution cost

In the same primary-executor evaluation, PORTABLE YNM used approximately:

- **2.34×** the input tokens;
- **2.82×** the output tokens;
- **2.40×** the elapsed time; and
- **2.90×** the tool calls

relative to control. These measurements are not universal cost estimates, but they show that the current implementation can be substantially more expensive than ordinary review. YNM is not currently an efficiency optimization.

### YNM-BRP-1

The bounded-usability assessment did not satisfy its complete frozen contract. It showed strong usefulness, traceability, inspectability, and authority containment, but both tested executors missed one frozen required-`MAYBE` condition. A plausible post-hoc alternative interpretation was documented, but the frozen ground truth was not changed after execution. The adverse result remains authoritative and is one reason this release is Research/Experimental.

The evidence supports a bounded claim: YNM demonstrated meaningful benefits under tested conditions, with substantial computational overhead and executor-dependent behavior.

## Known limitations

YNM has not demonstrated universal improvement, equal cross-model effectiveness, zero false findings, exhaustive issue discovery, perfect uncertainty preservation, reliable automatic activation, cost reduction, independent interoperability, or measured Ruflo/RuVector acceleration savings. It provides advisory review structure, not production, security, safety, legal, or compliance certification.

## What YNM is not

YNM is not a correctness oracle, universal project score, exhaustive verifier, proof of arbitrary program semantics, guarantee of zero false findings, proof that another review pass could discover nothing, proof that unreviewed scope is correct, production-readiness or security certification, proof of independent interoperability, guarantee of model-independent behavior, automatic authorization to act, or a cost-saving mechanism in its current implementation.

Provider-neutral means that YNM contracts do not require a specific provider, model, or runtime. It is a design property, not empirical evidence that all executors behave equally well.

## Installation and verification

YNM 1.4.0 is the current Research / Experimental release. For a reproducible source checkout:

```text
git clone https://github.com/RobLe3/ynm-skill.git
cd ynm-skill
git checkout v1.4.0
```

For an Agent Skills location, the containing directory must be named `ynm`. A source checkout can build the focused runtime package with:

```text
python scripts/build_skill_package.py --output-dir dist --overwrite
skills-ref validate dist/ynm
skills-ref read-properties dist/ynm
```

The last two commands require the Agent Skills reference validator. CI pins it to an exact revision. Format conformance is not independent interoperability evidence.

Core methodology is text-only. Optional bundled helpers require Python 3.10 or later and `PyYAML >=6,<7`:

```text
python -m pip install "PyYAML>=6,<7"
```

Repository development and validation use the broader dependencies in `pyproject.toml`.

## Repository structure

| Class | Locations | Role |
| --- | --- | --- |
| Runtime and normative | `SKILL.md`, `contracts/`, `loops/`, `methodology/` | Defines YNM behavior |
| Runtime support | `schemas/`, selected `scripts/`, `examples/`, `agents/` | Portable schemas, helpers, examples, and adapter metadata |
| Research and validation | `evaluations/`, `validation/`, `tests/`, `state/`, `docs/` | Reproducible evidence and research history |
| Packaging and policy | `manifest.yaml`, `VERSION`, `CHANGELOG.md`, `VERSIONING.md`, `CONTRIBUTING.md`, `SECURITY.md` | Distribution and repository policy |
| Historical provenance | Git history and immutable tags | Published snapshots and prior evidence |

Evaluation fixtures, adjudication results, and research-only tooling are excluded from the generated runtime package.

## Research and validation

- [Research status](https://github.com/RobLe3/ynm-skill/blob/main/docs/RESEARCH_STATUS.md)
- [Validation evidence](https://github.com/RobLe3/ynm-skill/blob/main/VALIDATION.md)
- [Evaluation evidence](https://github.com/RobLe3/ynm-skill/blob/main/evaluations/README.md)
- [Epistemic boundaries](methodology/epistemic-boundaries.md)
- [Release policy](https://github.com/RobLe3/ynm-skill/blob/main/RELEASING.md)
- [Changelog](https://github.com/RobLe3/ynm-skill/blob/main/CHANGELOG.md)

Active methodology development is paused after the 1.4 and YNM-BRP-1 cycles. The repository remains open for use, independent evaluation, and future work when new evidence offers credible information value.

## Contributing, security, and license

YNM is licensed under the [Apache License 2.0](LICENSE). Read [CONTRIBUTING.md](https://github.com/RobLe3/ynm-skill/blob/main/CONTRIBUTING.md) before proposing behavioral work. Report security issues through the process in [SECURITY.md](https://github.com/RobLe3/ynm-skill/blob/main/SECURITY.md).
