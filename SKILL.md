---
name: ynm
description: Review a project through independent architecture, implementation, adoption, maintenance, disposition, and orchestration loops using evidence-backed YES, NO, or MAYBE dispositions. Use for project reviews, longitudinal finding management, read-only audits, specialist focal reviews, convergence checks, or explicitly authorized remediation across software and non-software projects.
license: Apache-2.0
compatibility: Core review is text-only. Optional Python helper scripts require Python 3.10+ and PyYAML 6.x.
metadata:
  version: "1.4.0"
  repository: "https://github.com/RobLe3/ynm-skill"
---

# YNM Review

Apply a proposition-centered review method. Default to read-only operation. Do not alter project content or YNM state unless the user explicitly authorizes that class of write.

## Follow the invocation lifecycle

Every invocation uses `ANALYSIS → ITERATION → DELIVERY` and then terminates. Analysis establishes what can responsibly be reviewed. Iteration executes focal review and repeats only when another pass has expected information gain. Delivery is mandatory on converged, partial, blocked, escalated, bounded, and inconclusive paths; it reports achieved coverage and preserves uncertainty without granting authority. Read [Invocation Lifecycle](methodology/execution-lifecycle.md) before a full review.

## Select the invocation

- `Load YNM`: load the skill without creating project files or persistent state.
- `Review this project using YNM`: run the Meta Loop and all applicable focal loops.
- `YNM: <name> Loop`: run only the named specialist plus dependencies required to interpret its evidence. Record other needs as handoffs rather than silently widening scope.
- `Initialize YNM project integration and persistent state`: discover project conventions first, then create the smallest useful YNM-owned scaffold only with explicit write authorization. Follow [Project Integration](methodology/project-integration.md).
- `Review and persist YNM state`: write only authorized YNM-owned state. This is not permission to modify project artifacts.
- An explicit remediation request: review first, present the proposed changes, and modify only the authorized scope. Never treat review findings as permission to edit.

Read [methodology/core.md](methodology/core.md), [contracts/disposition.md](contracts/disposition.md), [contracts/finding.md](contracts/finding.md), [contracts/evidence.md](contracts/evidence.md), and [contracts/loop-result.md](contracts/loop-result.md) before producing findings. Read [contracts/assessment.md](contracts/assessment.md) when evaluation is non-trivial or consequential, [contracts/authorization.md](contracts/authorization.md) when recommending action, and [contracts/execution-context.md](contracts/execution-context.md) before substantial execution. For a full review, also read [loops/meta.md](loops/meta.md), [methodology/lifecycle.md](methodology/lifecycle.md), [methodology/convergence.md](methodology/convergence.md), [methodology/evaluation-integrity.md](methodology/evaluation-integrity.md), and [methodology/capability-adaptation.md](methodology/capability-adaptation.md). Read only the invoked specialist files after project discovery.

## Execute the review

1. **Analyze and plan.** Identify `PROJECT_ROOT`, objective, requested and effective scope, review profile, authority, read/write mode, and safe output location. Discover evidence, capability, applicable loops, assessments, persistence, and iteration bounds; emit a proportionate [Review Plan](contracts/review-plan.md). In read-only mode, do not create state inside the project.
2. **Discover context, documentation roles, capability, and complexity.** Follow [methodology/project-discovery.md](methodology/project-discovery.md). Identify declared intent, observable project state, existing project instructions and documentation responsibilities, conservatively supported executor capabilities, effective context, tool and budget limits, mutation risk, project complexity, unavailable evidence, and prior YNM state. Availability is not permission; model size is not capability proof.
3. **Characterize change.** If prior state exists, distinguish subject, assessment, and combined changes. Revalidate only dispositions whose proposition or support may be affected. Do not reopen a finding merely because time passed.
4. **Fit strategy to scope.** Choose CONSTRAINED, STANDARD, or EXTENDED execution and the largest granularity that can be reviewed reliably. Reduce or partition scope before reducing rigor. Select only applicable loops and assign them by demonstrated capability. Use `NOT_APPLICABLE` only when a loop lacks a meaningful proposition, not when the executor lacks capability.
5. **Iterate with precommitment.** Freeze a proportionate Assessment Contract before material evaluation when criteria could move or consequence warrants it. Execute applicable loops while keeping observation, measurement, inference, hypothesis, recommendation, proposed disposition, final disposition, execution, and authorization separate. Apply stronger evaluator independence as consequence rises.
6. **Window, preserve, and correlate.** Use controlled evidence windows and progressive synthesis when material exceeds effective context. Record included, excluded, reviewed, and unreviewed scope. Apply the finding contract; preserve links to original evidence, distinct executor contributions, conflicts, dependencies, and history.
7. **Reconcile.** Let the Disposition Loop process duplicate, conflict, supersession, reopen, and resolution records. Do not use recency as authority and do not erase prior conclusions.
8. **Evaluate reruns and convergence.** Require every immediate rerun to name the material change since the previous run and expected information gain. Stop when further immediate review is unlikely to improve current knowledge. For methodology validation, exercise [methodology/adversarial-validation.md](methodology/adversarial-validation.md).
9. **Deliver and terminate explicitly.** Enter Delivery on every terminal path. Summarize execution strategy, requested/reviewed/unreviewed scope, execution status by loop, material YES/NO/MAYBE findings, conflicts, failure attribution, handoffs, authorization, escalation, limitations, convergence, stop reason, and continuation. Emit a lifecycle-aware Run Receipt. Executor exhaustion produces PARTIAL or BLOCKED, never false completion or convergence.
10. **Persist only when permitted.** Use the portable model in [methodology/lifecycle.md](methodology/lifecycle.md). If persistence is unavailable, state the longitudinal capabilities that were lost.

## Integrate with a project

Project Integration is optional and separate from review. Discover existing documentation and state responsibilities before proposing `.ynm/` or an `AGENTS.md` section. Reuse equivalent project artifacts, never fabricate missing intent, and use `scripts/project_integration.py` in read-only mode before any authorized initialization. A project-local configuration may select execution preferences but cannot redefine YNM contracts. See [Project Integration Records](contracts/project-integration.md).

## Apply authority rules

- Treat `YES` as supported, `NO` as contradicted, and `MAYBE` as unresolved for one explicit proposition.
- Never use a disposition as priority, execution status, approval, or permission to act.
- Do not grant a favorable disposition by weakening, contaminating, or selectively applying evaluation rules. Preserve every material assessment revision.
- Keep evidentiary and authority standards fixed across CONSTRAINED, STANDARD, and EXTENDED execution. Greater capability permits broader responsible analysis, not broader authority.
- Keep specialist conclusions advisory unless the review charter grants disposition authority.
- Escalate destructive operations, security-sensitive choices, legal ambiguity, product intent, business priority, breaking changes, deletion, migration, unresolved ownership, and contradictory human requirements.
- Record human overrides as new history events with rationale; retain the prior analysis.

## Extend YNM

Use [methodology/extension-model.md](methodology/extension-model.md). Every added loop must use the common evidence, finding, disposition, lifecycle, and loop-result contracts and must declare what it does not own.

For reusable skill changes derived from project work, follow [Publication Readiness](methodology/publication-readiness.md). Keep the project finding separate from the YNM methodology-defect proposition, sanitize the lesson, validate the smallest reusable correction, and never treat release preparation as permission to publish.
