# Forge Extraction

## Evidence boundary

`SOURCE_ROOT` was the read-only Forge source repository. `OUTPUT_ROOT` was a separate YNM workspace. Forge was inspected at Git revision `ac8fcbd925e2c846003f161139847a06bdaf102a`. Targeted history identified evolution but did not override current artifacts. Local paths and unrelated workspace details are intentionally omitted from this public provenance record.

Evidence references use `path:line` against that working tree. Generated and historical artifacts are identified as such rather than treated as current truth automatically.

## Reconstructed ecosystem

| Component | Status | Reconstructed responsibility | Evidence |
|---|---|---|---|
| Forge Meta Loop | OBSERVED | Selects work among scored core loops and several triggered or scheduled tracks; runs mandatory epilogues; maintains generation, cycle, mode, queue, and convergence state. | `project/FORGE_META_LOOP.md:8-40`, `:96-181`; `project/FORGE_STATE.json`; `scripts/forge_orient.py:180-307` |
| ARCS | OBSERVED | Reviews architecture, specifications, decisions, governance, and cross-document consistency, while permitting documentation and project-management changes. | `project/arcs-loop-prompt.md:1-25`, `:61-238` |
| CORC | OBSERVED | Drives code-architecture convergence through implementation work, tests, and gates. | `project/corc-loop-prompt.md:1-125` |
| GRIT | OBSERVED | Maintains issue coverage, acceptance quality, closure accuracy, milestones, and derived work; it also runs an epilogue after every iteration. | `project/FORGE_META_LOOP.md:27`, `:69-70`, `:174-177` |
| ADOPTION | OBSERVED | Reviews installation, documentation, accessibility, discoverability, dogfooding, and adoption metrics, and files issues for weak dimensions. | `project/adopt-quality-loop-prompt.md:29-58`, `:252-340` |
| WARDEN | OBSERVED | Classifies unresolved items, routes them, adjusts specialist scores within a cap, gates convergence, and records parked or deferred state. | `project/warden-loop-prompt.md:12-190`, `:309-366`; `project/WARDEN_STATE.json` |
| REPO-HEALTH | OBSERVED | Reviews repository freshness, pull-request triage, cross-repository sync, SDK health, and derived-artifact coherence without owning specialist scores. | `project/repo-health-loop-prompt.md:11-63`, `:252-434` |
| GAPS | OBSERVED | Classifies incoming work and routes it into queues before specialist work. | `LOOPS_TRIAGE.md`; `project/GAPS_STATE.json`; `project/GAPS_INBOX.md` |
| BUG, RESA, SPEC, LIVE, PM, ALIGN, validators | OBSERVED | Add adversarial, research, maintenance, outcome, planning, coherence, and external validation signals outside the four-loop composite. | `project/FORGE_META_LOOP.md:29-40`, `:44-93`, `LOOPS_PARALLEL.md`, `LOOPS_VALIDATOR.md` |
| Work selector and orientation | OBSERVED | Combine central and per-loop queues, exclude blocked work, sort ascending numeric priority, and change ACTIVE/MAINTENANCE mode from actionable queue state. | `scripts/forge_select_work.py:38-110`; `scripts/forge_orient.py:180-307`; corresponding tests |

## System reconstruction

### Inputs, outputs, state, and triggers

Forge consumes project documents, code, tests, live probes, issue trackers, generated reports, state JSON, a central work queue, and loop-specific gap queues. Core loops emit scores, work logs, findings expressed largely as queue or issue items, and state updates. Parallel tracks emit signals that can preempt or redirect core work. Explicit handoffs include inbox entries, queue entries, issue records, flags such as `arch_block`, and state-file changes (`project/FORGE_META_LOOP.md:201-218`).

The primary persistence model is distributed: `FORGE_STATE.json` carries generation, mode, scores, queues, iteration history, convergence and live references; specialist state files carry dimensions, work logs, and gap queues; `WORK_QUEUE.json` supplies actionable items; WARDEN maintains a separate state, backlog, and log. This is OBSERVED from those artifacts. A single canonical finding/event schema is UNKNOWN: no inspected source established one common contract across every loop.

Triggers combine threshold gates, queue contents, modular schedules, elapsed iterations, changed files, live-system values, and maintainer authorization. Selection is mainly sequential for the active unit of work, while validators can operate independently and multiple epilogues run after an iteration. “Parallel track” therefore denotes composite and scheduling position more clearly than simultaneous execution; actual broad concurrent execution is UNKNOWN.

### Authority

Specialist prompts grant their agents permission to change artifacts within domain-specific boundaries. WARDEN has explicit score-adjustment authority, routing authority, and a convergence-gate role, but its own hard rules limit implementation and require routing (`project/warden-loop-prompt.md:12-37`, `:117-190`, `:309-366`). Production deployment and several external or irreversible operations require maintainer authorization (`project/FORGE_META_LOOP.md:40`; generated work guardrails in `scripts/forge_detect_gaps.py:267-297`).

Forge therefore does not use a purely advisory review model. Review, remediation, scoring, issue management, and orchestration are often combined. This is a project-specific operating choice rather than a necessary review principle.

### Meta Loop behavior

- **Selection:** LIVE thresholds can preempt ordinary work; BUG, GAPS, and repository health have triggered positions; ADOPTION and GRIT have floors and fixed cadence; remaining slots use largest score gap (`project/FORGE_META_LOOP.md:96-147`). Newer queue tooling also selects the lowest numeric unblocked priority from central and specialist queues (`scripts/forge_select_work.py:46-110`).
- **Ordering:** one primary loop is selected, followed by mandatory or conditional epilogues for issue hygiene, state refresh, live verification, project management, and specification maintenance.
- **State passage:** files and issue records carry signals between iterations; current and historical data coexist unevenly across work logs, cycle logs, mode history, WARDEN logs, and queue status.
- **Convergence:** current documentation requires all four scored loops to meet targets, a recent WARDEN pass without unaddressed important items, and LIVE at or above 80 (`project/FORGE_META_LOOP.md:389-406`).
- **Reruns:** score reductions, new queue items, scheduled cadence, failed live gates, or specialist handoffs can cause another pass. A universal record of `expected_information_gain` is UNKNOWN.
- **Endless-loop controls:** finite queue selection, blocked-item exclusion, convergence targets, ACTIVE/MAINTENANCE mode, bounded Meta-Ralph gates, and tests for no-progress stopping all provide controls. Repeated cadence can still execute without proposition-level new evidence.
- **Conflict handling:** WARDEN can reconcile unresolved items and adjust scores; explicit handoffs preserve some disagreement. A general contract that retains concurrent YES/NO proposals is UNKNOWN.
- **Closure and reopening:** queues, issues, WARDEN backlog, score adjustments, and state histories support forms of closure and reactivation. A single authority-neutral reopen protocol tied to material evidence change is UNKNOWN.

## Findings, evidence, and epistemic behavior

Forge uses direct repository checks, tests, issue metadata, live probes, reports, state comparisons, and independent fact-checking. The documented reality-check vocabulary distinguishes supported, partially supported, contradicted, and unverifiable claims with confidence (`LOOPS_VALIDATOR.md`, “Reality Audit”). This directly supports evidence-sensitive review.

Forge also uses scores as compressed state. The process composite once remained high while live operation was poor, leading to the separate LIVE gate (`project/FORGE_META_LOOP.md:341-381`). This is evidence that a single aggregate can hide domain failure and that declared convergence needs reality checks.

No common proposition-first finding model was observed across all loops. Issues, queue items, score dimensions, WARDEN entries, and reports each encode different subsets of proposition, evidence, owner, status, and history. The inference is that unresolved information survives better than in a one-shot review, but not under one uniform lifecycle.

## Responsibility collisions and contradictions

1. **Architecture versus implementation:** CORC is named “Code-Architecture Convergence,” while ARCS owns architecture and specification. Both necessarily inspect the other domain, creating a boundary that relies on prompt prohibitions rather than a shared handoff contract.
2. **Adoption versus repository maintenance:** README and deprecated-document freshness moved from ad hoc ADOPTION review into REPO-HEALTH, while REPO-HEALTH still sends evidence back for ADOPTION scoring (`project/FORGE_META_LOOP.md:80-87`; `project/repo-health-loop-prompt.md:408-418`). This is useful evolution and evidence that original boundaries were incomplete.
3. **Disposition versus judgment:** WARDEN is described as a disposition steward but can lower specialist scores and gate convergence. It is both custodian and second-order evaluator, which risks turning state management into cross-domain authority.
4. **Orchestration versus work:** the Meta Loop includes mandatory state rewriting, issue operations, live checks, and maintenance epilogues. It coordinates but also prescribes project-specific operational work.
5. **Scheduling models:** narrative scheduling uses composite gaps and modular cadence, while current scripts emphasize actionable queue priority. Both may be active at different layers, but their exact precedence is not expressed as one executable specification.
6. **Convergence history:** an earlier convergence was not retroactively revoked after LIVE exposed a measurement failure (`project/FORGE_META_LOOP.md:397-400`). Historical truth is preserved, but applicability and current validity are separate and only partly formalized.

## Classification

| Concept | Primary classification | Reason |
|---|---|---|
| Separate architecture, implementation, adoption, and maintenance perspectives | CORE PRINCIPLE | Distinct evidence domains catch failures hidden by another domain's success. |
| Persistent unresolved work and cross-loop handoffs | CORE PRINCIPLE | Queues, issues, WARDEN state, and loop signals prevent one-pass loss. |
| Evidence and reality checks before closure | CORE PRINCIPLE | Live and fact-checking mechanisms corrected misleading process confidence. |
| Explicit convergence and bounded stopping | CORE PRINCIPLE | Generations, gates, modes, and bounded controllers define stopping behavior. |
| Triggered and incremental review | USEFUL DEFAULT | Proportional scheduling avoids running every concern every time. |
| Human authorization for irreversible actions | CORE PRINCIPLE | Review evidence does not supply project authority. |
| Scores and weighted composite | FORGE IMPLEMENTATION DETAIL | Useful for Forge scheduling but capable of hiding failure and unnecessary for YNM. |
| GitHub issues, Git commits, JSON filenames, modular iteration cadence | FORGE IMPLEMENTATION DETAIL | Portable behavior does not require these technologies. |
| IICP protocol, SDK matrix, live-node and deployment assumptions | PROJECT-SPECIFIC ASSUMPTION | They describe the host project rather than review methodology. |
| Multiple overlapping state stores and old generation terminology | HISTORICAL ACCIDENT | Evolution left distributed representations and renamed descendants. |
| One universal current finding authority | OPEN QUESTION | Evidence shows several authorities but no single interoperable rule. |
| Actual concurrency of “parallel tracks” | OPEN QUESTION | Scheduling independence is documented; broad concurrent execution is not established. |

## Extracted lessons

Extracted from Forge: independent focal review, repeated evidence-driven passes, persistent unresolved work, explicit handoffs, reality checks, triggered review, separate human authority, convergence gates, and stopping when actionable work is exhausted.

Not extracted as requirements: scoring, metaphors, specific loop acronyms, GitHub, Git, state filenames, issue formats, live probes, AI agents, repository structure, or the Forge scheduler.

Open questions retained for YNM design were resolved deliberately rather than attributed to Forge: a proposition-first finding contract, append-only contribution events, YES/NO/MAYBE semantics, execution-status separation, authority-neutral reconciliation, material-change reopening, and a portable optional state model.

The later formal-rigor addendum extends YNM with assessment precommitment, epistemic typing, authorization status, failure attribution, Run Receipts, evidence ancestry, and optional integrity witnesses. Those additions are independent YNM refinements and are not retroactively classified as Forge observations.

The capability-adaptive execution layer is also an independent YNM refinement. Executor profiles, effective-context estimates, workload strategies, evidence windows, specialist assignment, and capability exhaustion are not attributed to Forge and do not alter this extraction.
