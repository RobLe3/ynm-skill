# Generalization from Forge to YNM

YNM was written from extracted principles, not by renaming Forge artifacts. “Refinement” below identifies deliberate YNM design rather than a claim about Forge.

| Forge concept | Observed purpose | Classification | Extracted principle | Removed | YNM equivalent | Refinement and rationale |
|---|---|---|---|---|---|---|
| ARCS | Align architecture, decisions, specifications, and governance | Core principle plus project detail | Review intended structure independently | IICP dimensions, scoring, GitHub actions | Architecture Loop | Narrows ownership to coherence; implementation defects become handoffs. |
| CORC | Align implementation with architecture and quality gates | Core principle plus project detail | Review realized behavior against declared intent | language, test, security, and release specifics | Implementation Loop | Treats procedures and non-code artifacts as possible implementation. |
| ADOPTION | Test installation, documentation, usability, and real use | Core principle | Technical correctness does not prove successful use | SDK, website, node, and score assumptions | Adoption Loop | Applies to any intended audience, including non-software work. |
| REPO-HEALTH and maintenance tracks | Detect stale, duplicated, unhealthy, or unsynchronized artifacts | Core principle plus useful defaults | Sustainability deserves an independent review | repositories, pull requests, dependency tools, fixed cadence | Maintenance Loop | Prohibits semantic change and aesthetic cleanup under maintenance authority. |
| WARDEN | Preserve deferred work, route findings, adjust scores, and gate convergence | Core principle mixed with implementation authority | Unresolved state must persist and be reconciled | score adjustment, severity bands, project-specific cadence | Disposition Loop | Separates lifecycle custody from specialist judgment and project authority. |
| Forge Meta Loop | Select, sequence, repeat, gate, and stop focal work | Core principle plus implementation detail | Orchestration needs explicit selection and convergence | composites, modular schedules, epilogues, mode names | Meta Loop | Selects by applicability and material change; cannot perform specialist review. |
| Gap queues and issue handoffs | Carry work between loops and iterations | Core principle | Communication must use explicit durable records | JSON locations and GitHub issue shape | Finding events and relationships | Contributions append evidence without silently changing ownership or disposition. |
| Fact checking and LIVE gate | Compare claims and process scores with observable reality | Core principle | Evidence can invalidate confident process conclusions | production probes and numeric thresholds | Evidence contract and change-aware reopening | Distinguishes observation, inference, conflict, and unavailable evidence. |
| Weighted scores | Rank gaps and express phase targets | Forge implementation detail | Scheduling needs a comparable reason, not necessarily a score | formula and target ratchets | Applicability, risk, dependency, and rerun records | Avoids compressing incompatible propositions into one truth value. |
| Generations, queue modes, bounded Meta-Ralph | Bound work and prevent unattended continuation | Useful default | Iteration must stop without new information or authority | Forge phase names and gate sequence | Review generation and rerun budget | Requires new evidence and expected information gain for immediate reruns. |
| Maintainer deployment gates | Reserve irreversible decisions for humans | Core principle | Analysis and recommendation do not create authority | project-specific deploy rules | Escalation and override history | Human overrides append history rather than rewriting analysis. |

## Deliberate YNM semantics

YNM introduces a common proposition-first finding contract because Forge's issues, queues, scores, reports, and WARDEN records do not supply one uniform lifecycle. `YES`, `NO`, and `MAYBE` mean supported, contradicted, and unresolved. They do not encode priority, completion, applicability, or permission.

YNM also introduces append-only lifecycle events, explicit current projections, evidence availability, material-change reopening, a default one-rerun limit, and a portable optional state format. These choices address observed information-loss and authority risks while remaining implementation-neutral. They are refinements, not reconstructed Forge behavior.

## Formal-rigor addendum refinements

The formal-rigor addendum further introduces typed observations, measurements, inferences and hypotheses; proportionate Assessment Contracts; precommitment and evaluation-integrity rules; reference-state discipline; evidence ancestry; evidence-supported failure attribution; explicit action authorization; consequence-proportional evaluator independence; terminal Run Receipts; persistent negative knowledge; and information-gain reruns. These controls are YNM refinements supplied by the addendum. They are not presented as behavior observed in Forge.

Optional BASIC, PERSISTENT, and AUDITABLE profiles describe implementation capability without changing YES/NO/MAYBE. Integrity witnesses remain optional. No benchmark system, optimization engine, provider tooling, automated promotion workflow, model mutation, scoring system, or scheduling machinery is imported.

## Capability-adaptive execution refinement

The capability-adaptive addendum introduces conservative executor discovery, effective-context reasoning, project-complexity characterization, capability-to-scope fit, neutral CONSTRAINED/STANDARD/EXTENDED strategies, hierarchical partitioning, evidence windows, progressive synthesis, loop assignment, capability exhaustion, continuation coverage, and capability escalation. These are execution refinements, not Forge observations and not separate truth models.

Capability adaptation applies equally to humans and machines. It uses observed interfaces and successful operation before self-description or model size, marks uncertainty conservatively, reduces scope before rigor, preserves provenance through summaries, and never converts exhaustion into convergence. BASIC/PERSISTENT/AUDITABLE remain a separate assurance dimension.

## Critical challenge results

- **Copied accidents removed:** scores, cadence arithmetic, branded names, GitHub workflows, phase generations, and production probes are not foundational.
- **Overlap reduced:** each focal loop owns one question family; cross-domain observations produce handoffs or linked propositions.
- **Contracts kept small:** the finding core has sixteen required concepts; impact, confidence, action, owner, relationships, dependencies, revisit conditions, and resolution evidence appear only when useful.
- **Software assumptions removed:** “implementation” includes realized procedures and artifacts; loops may be not applicable.
- **MAYBE persists:** reason, evidence, history, and optional revisit conditions survive; inactivity cannot close it.
- **Provider independence:** no AI, model, agent runtime, repository host, database, or automation engine is required.
- **Proportionality:** discovery selects meaningful loops and bounds scope; tiny projects need no empty ceremony.
- **Authority preserved:** specialists propose; declared authority reconciles; humans may override through an explicit event.
- **Evaluation meaning preserved:** material criteria are frozen before interpretation; later rule changes create assessment revisions rather than retroactive success.
- **Terminality preserved:** completed, partial, blocked, escalated, not-applicable, converged, and no-change runs emit receipts.
- **Capability fit preserved:** execution uses the largest reliably reviewable granularity; omitted scope remains explicit and standards remain fixed.
