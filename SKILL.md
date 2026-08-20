---
name: ynm
description: Evidence-backed project and repository review for implementation correctness, architecture, specification-versus-code conflicts, tests-versus-documentation, release or production readiness, adoption, maintenance, security claims, and conflicting project evidence. Enter through lightweight YNM-0 routing, preserve unresolved evidence as MAYBE, and escalate only when additional work can materially improve the disposition.
license: Apache-2.0
compatibility: Core review is text-only. Optional Python helper scripts require Python 3.10+ and PyYAML 6.x.
metadata:
  version: "1.4.0"
  repository: "https://github.com/RobLe3/ynm-skill"
---

# YNM Review

Apply a proposition-centered review method. Default to read-only operation. Do not alter project content or YNM state unless the user explicitly authorizes that class of write.

## Start with the cheapest defensible path

Every eligible request enters through [Adaptive Execution](methodology/adaptive-execution.md): `YNM-0 ROUTE`, `YNM-1 EVALUATE`, `YNM-2 SPECIALIZE`, or `YNM-3 ASSURE`. Execution levels measure justified work, not result quality. Most ordinary reviews should stop at YNM-1. Use YNM-2 only for a relevant additional perspective and reserve YNM-3 for consequential assurance or an explicit comprehensive audit.

Prefer deterministic exact lookup, verified cached evidence, and targeted structural analysis before semantic retrieval or model reasoning. Optional accelerators may reduce evidence-acquisition cost but never change evidence sufficiency, authority, or disposition semantics. Continue in PORTABLE mode when acceleration is absent or fails.

## Follow the invocation lifecycle

Every invocation uses `ANALYSIS → ITERATION → DELIVERY` and then terminates. Analysis establishes what can responsibly be reviewed. Iteration executes focal review and repeats only when another pass has expected information gain. Delivery is mandatory on converged, partial, blocked, escalated, bounded, and inconclusive paths; it reports achieved coverage and preserves uncertainty without granting authority. Read [Invocation Lifecycle](methodology/execution-lifecycle.md) before a full review.

## Select the invocation

- `Load YNM`: load the skill without creating project files or persistent state.
- `Review this project using YNM`: enter YNM-0, bound the propositions, and invoke only the focal loops justified by expected information gain.
- `YNM: <name> Loop`: run only the named specialist plus dependencies required to interpret its evidence. Record other needs as handoffs rather than silently widening scope.
- `Initialize YNM project integration and persistent state`: discover project conventions first, then create the smallest useful YNM-owned scaffold only with explicit write authorization. Follow [Project Integration](methodology/project-integration.md).
- `Review and persist YNM state`: write only authorized YNM-owned state. This is not permission to modify project artifacts.
- An explicit remediation request: review first, present the proposed changes, and modify only the authorized scope. Never treat review findings as permission to edit.

At YNM-0, read only this file and the [Adaptive Execution Contract](contracts/adaptive-execution.md). At YNM-1, add [contracts/disposition.md](contracts/disposition.md), [contracts/evidence.md](contracts/evidence.md), and the minimum finding contract needed for Delivery. Load assessment, authorization, lifecycle, specialist, meta, adversarial, and convergence material only when the proposition or escalation level requires it. Read only invoked specialist files after targeted project discovery.

## Execute the review

1. **Route cheaply.** Normalize and, when needed, decompose the proposition. Bound scope, consequence, authority, minimum execution level, relevant perspectives, retrieval strategy, optional capabilities, and budget. Do not perform comprehensive discovery at YNM-0.
2. **Discover context, documentation roles, capability, and complexity.** Follow [methodology/project-discovery.md](methodology/project-discovery.md). Identify declared intent, observable project state, existing project instructions and documentation responsibilities, conservatively supported executor capabilities, effective context, tool and budget limits, mutation risk, project complexity, unavailable evidence, and prior YNM state. Availability is not permission; model size is not capability proof.
3. **Characterize change.** If prior state exists, distinguish subject, assessment, and combined changes. Revalidate only dispositions whose proposition or support may be affected. Do not reopen a finding merely because time passed.
4. **Fit strategy to scope.** Choose LIGHT, NORMAL, or THOROUGH execution and the largest granularity that can be reviewed reliably. Reduce or partition scope before reducing rigor. Select only loops with a credible chance of changing a disposition.
5. **Iterate with precommitment.** Freeze a proportionate Assessment Contract before material evaluation when criteria could move or consequence warrants it. Execute applicable loops while keeping observation, measurement, inference, hypothesis, recommendation, proposed disposition, final disposition, execution, and authorization separate. Apply stronger evaluator independence as consequence rises.
6. **Window, preserve, and correlate.** Use controlled evidence windows and progressive synthesis when material exceeds effective context. Record included, excluded, reviewed, and unreviewed scope. Apply the finding contract; preserve links to original evidence, distinct executor contributions, conflicts, dependencies, and history.
7. **Reconcile.** Let the Disposition Loop process duplicate, conflict, supersession, reopen, and resolution records. Do not use recency as authority and do not erase prior conclusions.
8. **Evaluate escalation and convergence.** Record a supported reason, expected information gain, and expected cost before optional escalation. Stop when a bounded disposition is defensible or further work is unlikely to improve current knowledge. Use adversarial review conditionally for consequential affirmative assurance, conflicts, contamination, or authority risk.
9. **Deliver and terminate explicitly.** Enter Delivery on every terminal path. Summarize execution strategy, requested/reviewed/unreviewed scope, execution status by loop, material YES/NO/MAYBE findings, conflicts, failure attribution, handoffs, authorization, escalation, limitations, convergence, stop reason, and continuation. Emit a lifecycle-aware Run Receipt. Executor exhaustion produces PARTIAL or BLOCKED, never false completion or convergence.
10. **Persist only when permitted.** Use the portable model in [methodology/lifecycle.md](methodology/lifecycle.md). If persistence is unavailable, state the longitudinal capabilities that were lost.

## Integrate with a project

Project Integration is optional and separate from review. Discover existing documentation and state responsibilities before proposing `.ynm/` or an `AGENTS.md` section. Reuse equivalent project artifacts, never fabricate missing intent, and use `scripts/project_integration.py` in read-only mode before any authorized initialization. A project-local configuration may select execution preferences but cannot redefine YNM contracts. See [Project Integration Records](contracts/project-integration.md).

## Apply authority rules

- Treat `YES` as supported, `NO` as contradicted, and `MAYBE` as unresolved for one explicit proposition.
- Absence of contradictory evidence is not affirmative evidence. A normal YES requires affirmative support, sufficient coverage, and bounded scope. A complete search of an explicit bounded set may affirm a correspondingly bounded absence proposition.
- Never use a disposition as priority, execution status, approval, or permission to act.
- Do not grant a favorable disposition by weakening, contaminating, or selectively applying evaluation rules. Preserve every material assessment revision.
- Keep evidentiary and authority standards fixed across CONSTRAINED, STANDARD, and EXTENDED execution. Greater capability permits broader responsible analysis, not broader authority.
- Keep specialist conclusions advisory unless the review charter grants disposition authority.
- Escalate destructive operations, security-sensitive choices, legal ambiguity, product intent, business priority, breaking changes, deletion, migration, unresolved ownership, and contradictory human requirements.
- Record human overrides as new history events with rationale; retain the prior analysis.

## Extend YNM

Use [methodology/extension-model.md](methodology/extension-model.md). Every added loop must use the common evidence, finding, disposition, lifecycle, and loop-result contracts and must declare what it does not own.

For reusable skill changes derived from project work, follow [Publication Readiness](methodology/publication-readiness.md). Keep the project finding separate from the YNM methodology-defect proposition, sanitize the lesson, validate the smallest reusable correction, and never treat release preparation as permission to publish.
