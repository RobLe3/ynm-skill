# Contract Dependency Map

This map identifies canonical ownership and required compatibility. It does not create new semantics.

| Concept | Canonical home | Required compatibility |
|---|---|---|
| YES, NO, MAYBE | `contracts/disposition.md` | Finding values, examples, lifecycle events, reports |
| Typed evidence and provenance | `contracts/evidence.md` | Findings, assessments, synthesis, persistence |
| Finding fields and history events | `contracts/finding.md` | Disposition, evidence, lifecycle, schemas |
| Execution status and terminal receipts | `contracts/loop-result.md` | Meta control flow, convergence, persistence |
| Assessment precommitment and revision | `contracts/assessment.md` | Evaluation integrity, findings, Meta |
| Action permission | `contracts/authorization.md` | Findings, human authority, remediation workflows |
| Capability and coverage | `contracts/execution-context.md` | Discovery, Meta, partial results, receipts |
| Lifecycle status and transitions | `methodology/lifecycle.md` | Finding events, persistence, reopening, supersession |
| Loop ownership | `methodology/responsibility-model.md` | All loop definitions and extension declarations |
| Reruns and convergence | `methodology/convergence.md` | Meta control flow and receipts |
| Minimal versus optional architecture | `methodology/core.md` | Skill loading, implementations, extensions |
| Project context, configuration, bootstrap receipts, and ownership | `contracts/project-integration.md` | Project Integration, Meta selection, schemas, helper script |
| Installable/public artifact classes and capability claims | `methodology/publication-readiness.md` | Manifest, README, release validation, contributions |
| Invocation phases and mandatory Delivery | `methodology/execution-lifecycle.md` | Skill, Meta orchestration, convergence, receipts, project integration |
| Objective, requested/effective scope, and iteration policy | `contracts/review-plan.md` | Analysis, execution context, assessments, receipt plan revision |

Normative dependency direction is core architecture → contracts and responsibility model → lifecycle and methodology → loops → executable skill → examples. Downstream material may summarize upstream behavior but cannot redefine it. Examples are never normative.

Change canonical definitions first, then update dependent schemas, methodology, loops, skill instructions, examples, validation, and persisted state in that order. A detected mismatch becomes a finding; do not resolve it by choosing the most recent text automatically.
