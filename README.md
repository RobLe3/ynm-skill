# YNM

YNM is a structured project review methodology for cases where “looks good” is not sufficient evidence for judgment. It turns conclusions into explicit propositions, binds each proposition to traceable evidence, preserves uncertainty where evidence is missing or conflicting, and records what was reviewed versus what was not.

YNM is useful when teams need a reliable handoff between review, recommendation, and action, especially under changing scope, partial evidence, and multiple stakeholders.

## What YNM gives you

YNM gives practical, review-oriented behavior instead of generic quality rhetoric:

- **Evidence instead of impressions:** findings are attached to explicit propositions, so conclusions are auditable.
- **First-class uncertainty:** `MAYBE` is a managed state, not a failure mode.
- **Safe agentic control:** review, recommendation, authorization, execution, persistence, and outcome are tracked separately.
- **Honest completion:** convergence is separate from exhaustion or limit-driven stopping.
- **Longitudinal knowledge:** findings preserve provenance, prior dispositions, conflicts, reopenings, supersessions, and resolution history.
- **Specialist agreement without a universal score:** architecture, implementation, adoption, and maintenance can legitimately differ.
- **Capability-aware operation:** scoped, constrained execution is preferred over lowering rigor.
- **Provider-neutral execution:** humans, agents, and tooling can follow the same contracts.

## Why YNM exists

Ordinary approaches help in different ways, but they typically leave gaps:

- **Tests/linters** validate specific mechanics.
- **Checklists** provide repeatability.
- **Code review / LLM reviews** provide interpretation.

YNM adds the missing layer: explicit propositions, preserved uncertainty, and explicit terminal outcomes.

YNM was refined through practical engineering work across multiple technologies, audiences, and maturity levels. That experience showed one-pass judgments are often insufficient and that architecture, implementation, adoption, and maintenance can progress at different speeds.

YNM does not replace tests, domain checks, or domain expertise. It coordinates review, evidence, and uncertainty so subsequent decisions can be made intentionally.

## What a YNM result looks like

A conventional review might conclude:

> Authentication is mostly good, but recovery documentation and failover testing are weak.

YNM instead keeps each statement explicit:

| Proposition | Disposition | Evidence / reason |
|---|---|---|
| Authentication enforces the declared access model | **YES** | Access-control implementation, tests, and config match the declared contract. |
| Recovery behavior is sufficiently documented for operators | **NO** | The required operator procedure is not present in reviewed evidence. |
| Multi-region failover preserves declared security properties | **MAYBE** | Failover evidence is outside reviewed scope and was not available for this run. |

Execution status: **PARTIAL**
Reviewed scope:
- authentication implementation
- authentication tests
- recovery documentation

Unreviewed scope:
- production failover topology
- incident post-mortem records

Authorization:
- review only
- no project mutation authorized

Continuation:
- revisit MAYBE finding when failover evidence becomes available.

This is what you can expect to receive as a terminal, auditable artifact, including explicit uncertainty.

## What YNM adds beyond common approaches

| Approach | Primary strength | What YNM adds |
| --- | --- | --- |
| Tests / linters | Deterministic checks | Proposition-focused interpretation, evidence context, explicit uncertainty, and scope boundaries |
| Code review | Human judgment | Shared review contracts, lifecycle, and persistent, auditable findings |
| Checklist | Repeatability | Evidence provenance, explicit `MAYBE`, history and reopening conditions |
| One-shot LLM review | Fast synthesis | Scope control, convergence discipline, Delivery handoff, authorization separation |
| YNM | Structured evidence-backed review | Keeps propositions, evidence, and authority distinct across repeatable iterations |

YNM complements, rather than replaces, tests, linters, domain verification, and implementation-specific quality gates.

## When to use YNM

Use YNM when you need structured, auditable review for:

- architecture vs implementation alignment
- release-readiness or audit-oriented reviews
- recurring project audits across releases
- multi-agent or multi-reviewer review coordination
- incomplete, conflicting, or evolving evidence
- explicit scope definition and rerun justification
- controlled agentic workflows where write authority must remain explicit
- adoption and maintenance reviews that differ from technical correctness

## When not to use YNM

YNM is not the right tool for:

- simple syntax/style checks
- trivial one-off edits
- questions fully answered by deterministic tests
- general summaries or explanations
- isolated formatting or wording requests
- quick informal opinions where project-level context is unnecessary

## Analysis, Iteration, and Delivery

YNM follows one macro lifecycle:

```text
ANALYSIS → ITERATION → DELIVERY → TERMINATED
```

- **ANALYSIS:** determine objective, requested/effective scope, evidence availability, authority, capability, applicable loops, and safety limits.
- **ITERATION:** execute relevant loops, gather evidence, build and reconcile findings, and iterate only when the next pass has justified information gain.
- **DELIVERY:** provide an explicit terminal handoff on every outcome (converged, partial, blocked, bounded, or escalated).

Delivery is mandatory. It means the review ended with traceable results; it does not imply approval, completion, or automatic safety.

Read the full lifecycle definition in [Invocation Lifecycle](methodology/execution-lifecycle.md) and [Review Plan](contracts/review-plan.md).

## YES / NO / MAYBE

YNM is proposition-centered:

- **YES:** sufficient evidence supports the proposition under the established evaluation conditions.
- **NO:** sufficient evidence contradicts the proposition.
- **MAYBE:** evidence is insufficient, conflicting, or currently unavailable to decide.

`MAYBE` is not “low confidence.” It is a managed unresolved state that preserves why a decision is still pending.

## Delivery and scope visibility

A delivery output always includes:

- current dispositions
- executed and requested scope
- reviewed and unreviewed scope
- evidence boundaries and failures
- execution status and stop reason
- continuation/revisit conditions
- remaining `MAYBE` items and unresolved dependencies

Exhaustion (capability, context, budget, evidence, authorization, or failure) is recorded distinctly from convergence. A review may stop for limits and still produce a valid partial delivery.

## Stateless and persistent use

YNM can be used in two operating modes:

### Stateless

- no project writes
- one-shot review and Delivery
- no persistent finding history in-project
- suitable for bounded ad-hoc reviews

### Persistent (authorized)

- optional and explicit authorization required
- stores findings, plans, receipts, events, and resolution state
- improves recurrence, reopening, and longitudinal context

Persistence is optional and authorization-gated, not required.

See [Project Integration](methodology/project-integration.md).

## Quick start

1. Open this methodology:

   ```text
   Review this project using YNM.
   ```

2. The invocation follows one lifecycle:

   ```text
   ANALYSIS → ITERATION → DELIVERY
   ```

3. Use source checkout for inspection and development, or install as an Agent Skill for runtime execution.

4. Validation starts with:

   ```text
   python validation/validate_ynm.py
   python -m unittest discover -s tests -v
   ```

This remains read-only by default. Persistent integration requires explicit authorization.

## Installation and verification

The installable entrypoint is [`SKILL.md`](SKILL.md). The package and repository are separated by intended use.

### Source checkout (development / audit)

```text
git clone https://github.com/RobLe3/ynm-skill.git
cd ynm-skill
```

### Installed Agent Skill

For agent-capable runtimes, the containing directory must be named `ynm`:

```text
git clone https://github.com/RobLe3/ynm-skill.git /path/to/skills/ynm
```

Or install from the built package:

```text
python scripts/build_skill_package.py --output-dir dist --overwrite
ls dist/ynm
```

Validate package format and metadata:

```text
python scripts/build_skill_package.py --output-dir dist --overwrite
skills-ref validate dist/ynm
skills-ref read-properties dist/ynm
```

The CI checks `skills-ref` against a pinned reference revision so format and reference
conformance are reproducible. It confirms Agent Skills format conformance only; it is
**not** independent interoperability validation.

## Repository structure

| Class | Locations | Role |
|---|---|---|
| Runtime / normative | `SKILL.md`, `contracts/`, `loops/`, `methodology/` | Defines YNM behavior |
| Optional runtime support | `schemas/`, `scripts/`, `examples/`, `agents/` | Validation, tooling, examples, adapters |
| Validation and history | `validation/`, `tests/`, `state/` | Evidence for current candidate claims and reproducible checks |
| Packaging and contribution | `README.md`, `manifest.yaml`, `VERSION`, `CHANGELOG.md`, `VERSIONING.md`, `CONTRIBUTING.md`, `SECURITY.md` | Distribution and project policy |
| Provenance | Git history and tags | Historical evidence retained in immutable tags, not copied into HEAD |

## What YNM is not

YNM is not:

- a universal project score
- automatic permission to modify a repository
- proof that unreviewed scope is correct
- a replacement for tests, linters, domain checks, or product requirements
- a guarantee to eliminate uncertainty
- evidence of production-readiness certification by itself
- independent interoperability proof
- tied to one provider, model, or runtime

## Extend YNM

Use [Extension Model](methodology/extension-model.md) for additional loops. Extensions must use the same evidence, finding, disposition, lifecycle, and delivery contracts and explicit ownership boundaries.

## Validation status and limits

**Current version:** `1.3.0`
**Candidate status:** release candidate

- Candidate release evidence is in `state/releases/1.3.0`.
- Deterministic local tests: **PASS**.
- Workflow includes schema, lifecycle, security-boundary, package, and release-integrity validations.
- Historical 1.0.0 through 1.2.0 maturity evidence is integrity-checked.
- Manifested package validation uses the pinned Agent Skills reference implementation.
- `YNM-VAL-001` remains **MAYBE**: no independent third-party implementation has yet demonstrated compatible YNM records.

YNM uses the Python `jsonschema` Draft 2020-12 validator for its declared schemas, together with YNM-specific checks for cross-file lifecycle consistency, release integrity, sanitization, and runtime boundaries.

Passing these checks means the repository and candidate evidence are internally consistent. It is not proof of independent implementation compatibility.

## Core method vs optional tooling

YNM can be used without a Python runtime for manual interpretation:

- Core methodology: read and follow `SKILL.md`, contracts, and methodology.

Optional helpers are available when you want local validation:

- Python >= 3.10
- `PyYAML >= 6,<7`
- Validation dependencies listed in `pyproject.toml`

If you are only using the method and runtime package, these helper dependencies are optional.

## Evaluate YNM independently

1. Read `SKILL.md`.
2. Inspect `contracts/` and `methodology/`.
3. Run the local validation and tests.
4. Review findings and candidate evidence under `state/releases/1.3.0`.
5. Run a bounded review or independent implementation.
6. Report incompatible or ambiguous behavior with evidence.

Useful external evidence includes: alternate runtimes/models, manual execution, independent implementation of contracts, and reviews on different project types.

## License, contributing, and security

YNM is licensed under the [Apache License 2.0](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) for semantic and sanitization requirements and [SECURITY.md](SECURITY.md) for private reporting of ownership-boundary, mutation, secret-exposure, or validation issues.

Historical development notes were not removed from Git history and remain discoverable through tags, while current HEAD stays focused on the active public methodology and candidate evidence.
