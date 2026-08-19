# YNM

YNM is a project-agnostic review methodology for making evidence-backed judgments without losing disagreement, uncertainty, history, or authority boundaries. It can be followed manually, used as an agent skill, or implemented by independent tools.

Every disposition answers an explicit proposition:

- **YES**: available evidence sufficiently supports the proposition.
- **NO**: available evidence sufficiently contradicts the proposition.
- **MAYBE**: evidence is insufficient or materially conflicting, so the proposition remains unresolved with its context preserved.

Disposition is separate from execution status, recommendation, priority, confidence, and permission to act.

## Why YNM exists

Projects vary across language, technology, goal, audience, maturity, scope, architecture, operations, documentation needs, and review depth. Those dimensions do not mature at the same speed and should not collapse into one generic quality score. YNM separates focal responsibilities while allowing evidence and unresolved findings to survive across reviews.

YNM was refined through sustained use on a heterogeneous engineering effort spanning multiple languages, interfaces, audiences, goals, and levels of component complexity. One-pass review proved inadequate because architecture, implementation, adoption, maintenance, and unresolved decisions changed at different rates. The predecessor loop model helped structure review, preserve open questions, and coordinate evidence across iterations. YNM is the generalized methodology learned from that experience; it does not claim to have created or autonomously delivered the underlying project.

## Analyze, iterate, deliver

Every invocation follows one macro lifecycle:

```text
ANALYSIS → ITERATION → DELIVERY → TERMINATED
```

**Analysis** determines what can responsibly be reviewed. It discovers project context, evidence, prior state, executor capability, requested and effective scope, authority, applicable loops, assessments, persistence, and iteration safety.

**Iteration** performs focal review, gathers traceable evidence, creates and reconciles findings, and repeats only when another pass has expected information gain. Iteration count is not predetermined. Convergence normally stops review; a safety bound prevents uncontrolled looping without pretending that exhaustion is convergence.

**Delivery** produces an explicit handoff on every terminal path. Converged, partial, blocked, escalated, bounded, and inconclusive reviews all reach Delivery. MAYBE findings, unreviewed scope, limitations, authority constraints, and continuation needs remain visible.

See the [Invocation Lifecycle](methodology/execution-lifecycle.md) and [Review Plan Contract](contracts/review-plan.md).

## Quick start

1. Clone or otherwise expose this skill to a human or skill-capable runtime.
2. Invoke:

   ```text
   Review this project using YNM.
   ```

3. YNM analyzes project context and executor capability, selects applicable loops, iterates only while information gain justifies another pass, and always delivers an explicit result.
4. Project files and persistent YNM state remain unchanged unless that class of write is explicitly authorized.

Focused review uses the same contracts:

```text
YNM: Architecture Loop
YNM: Adoption Loop
```

Optional persistent integration begins with:

```text
Initialize YNM project integration and persistent state.
```

Loading or reviewing YNM does not imply initialization.

## Focal loops

- **Architecture** evaluates intended structural coherence.
- **Implementation** evaluates realized behavior against intent and contracts.
- **Adoption** evaluates whether intended users or stakeholders can succeed.
- **Maintenance** evaluates sustainability and operational upkeep.
- **Disposition** preserves and reconciles finding state without becoming a universal judge.
- **Meta** coordinates the invocation lifecycle and focal reviews without becoming a universal reviewer.

Each loop declares what it owns, observes, may recommend, may not decide, and must hand off. Extensions use the same contracts and responsibility discipline.

## Findings, evidence, and MAYBE

A finding keeps proposition, observation, typed evidence, interpretation, proposed disposition, final disposition, recommendation, authorization, history, and revisit context separate. Evidence retains provenance and ancestry so repeated summaries of one source do not masquerade as independent corroboration.

MAYBE is managed unresolved state, not neglect. It records why resolution is unavailable, current evidence, missing evidence, and a revisit condition where possible. NO preserves negative knowledge and reopen conditions. New evidence is appended; earlier reasoning is not silently overwritten.

The canonical definitions are in the [Finding](contracts/finding.md), [Evidence](contracts/evidence.md), and [Disposition](contracts/disposition.md) contracts.

## Read-only review and project integration

Review is read-only by default. Project Integration is optional and discovers existing documentation and state responsibilities before proposing files. When explicitly authorized, the default scaffold is deliberately small:

```text
.ynm/
├── README.md
├── project.yaml
├── config.yaml
└── state/
```

An optional bounded section may be added to `AGENTS.md`; existing content outside the managed markers is preserved. Projects without `AGENTS.md`, Git, GitHub, AI tooling, or persistent storage remain supported.

Read-only discovery:

```text
python3 scripts/project_integration.py /path/to/project
```

Authorized initialization:

```text
python3 scripts/project_integration.py /path/to/project --initialize --apply
```

See [Project Integration](methodology/project-integration.md) for ownership, idempotence, removal, and project-native placement rules.

## Stateless, persistent, and capability-adaptive use

Stateless YNM emits findings, coverage, unresolved context, continuation information, and a Run Receipt without creating project files. It cannot reliably preserve recurrence, historical comparison, reopening, or cross-run convergence.

Persistent YNM stores portable snapshots, plans, assessments, findings, events, and receipts when enabled and authorized. A database is optional.

Execution adapts to demonstrated capability rather than provider or model size. Constrained execution narrows and partitions scope before reducing rigor. More capable execution may broaden synthesis but receives no greater authority. Humans are executors too.

## Installation and verification

The installable entrypoint is [`SKILL.md`](SKILL.md). A minimal runtime installation contains the entrypoint and the contracts, loops, and methodology it references. Schemas, scripts, examples, and runtime adapters provide optional capabilities. The [manifest](manifest.yaml) classifies each component.

Provider-neutral installation:

```text
git clone https://github.com/RobLe3/ynm-skill.git
cd ynm-skill
```

Expose the repository or `SKILL.md` to the chosen runtime according to that runtime's skill-loading instructions. `agents/openai.yaml` is an optional adapter, not a core dependency.

Verify the repository:

```text
python3 validation/validate_ynm.py
python3 -m unittest discover -s tests -v
```

## Repository structure

| Class | Locations | Role |
|---|---|---|
| Runtime / normative | `SKILL.md`, `contracts/`, `loops/`, `methodology/` | Defines YNM behavior |
| Optional | `schemas/`, `scripts/`, `examples/`, `agents/` | Validation, automation, examples, adapters |
| Packaging | README, manifest, version, license, contribution files | Distribution and discoverability |
| Provenance | extraction, generalization, and comparison reports | Historical analysis; not required at runtime |
| Validation | `tests/`, `validation/`, maturity reports, `state/` | Evidence for claims and longitudinal history |

README and manifest describe YNM but cannot override normative contracts.

## Extend YNM

An additional focal loop declares purpose, scope, evidence, responsibilities, non-responsibilities, finding types, dependencies, handoffs, and rerun conditions. It uses the common finding, evidence, disposition, authorization, lifecycle, execution-result, and Delivery contracts. See the [Extension Model](methodology/extension-model.md).

## Validation status and limitations

**Current version:** 1.2.0

- Production-maturity disposition: recorded in `YNM_1_2_MATURITY_REPORT.md`.
- Final local validation: 27 unit tests passed and 78 adversarial scenarios have explicit expected outcomes.
- Historical 1.0.0 and 1.1.0 maturity evidence is integrity-checked.
- Generic, specialist, stateless, persistent, project-bootstrap, lifecycle, and repository validation paths are locally exercised.
- The bundled validator implements the JSON Schema features used by YNM fixtures, not every Draft 2020-12 feature.
- `YNM-VAL-001` remains MAYBE: no independent third-party implementation has yet exchanged compatible YNM records. Public availability does not resolve that finding.

## Evaluate YNM independently

1. Read `SKILL.md`.
2. Inspect `contracts/` and `methodology/`.
3. Run the validation suite.
4. Review the examples and maturity evidence.
5. Attempt a bounded review or independent implementation.
6. Report ambiguous semantics or incompatible records through the compatibility issue template.

Useful external evidence includes independent contract implementations, another runtime or model, manual human execution, different project types, and reports of incompatible lifecycle interpretations. Publication enables this evaluation; it is not itself third-party validation.

## License, contributing, and security

YNM is licensed under the [Apache License 2.0](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md) for semantic and sanitization requirements and [SECURITY.md](SECURITY.md) for private reporting of unintended mutation, ownership-boundary, secret-exposure, or validation issues.

Forge research is retained only as analytical provenance. Runtime YNM is independently expressed and requires no knowledge of Forge or any project that informed its development.
