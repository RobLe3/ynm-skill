# Responsibility Model

Multiple focal loops exist because technical structure, realized behavior, user success, and sustainability can disagree. Independence preserves those disagreements long enough to examine them.

Every loop declares `owns`, `observes`, `may_recommend`, `may_not_decide`, and `must_hand_off`. Ownership means responsibility for framing and maintaining findings in that focal domain. It does not grant project-change authority. Observation permits use of another domain's evidence without taking over that domain.

Specialists propose dispositions. The Disposition Loop applies transitions only under the review charter's authority rules. The Meta Loop selects, orders, and stops work; it neither substitutes for specialist evidence nor becomes an appeals court. Human project authority remains outside YNM unless explicitly delegated. Disposition and action authorization use separate records.

Separate advocacy from adjudication in proportion to consequence. Low-impact work may use one actor in several explicitly named roles. High-impact, irreversible, security, privacy, legal, or destructive recommendations require stronger logical or actor separation. Independence is a relationship among roles, not a requirement for multiple tools or AI agents.

When boundaries overlap, keep the same underlying evidence but frame separate propositions if the domains ask different questions. If two loops ask the same proposition, correlate their records and preserve both contributions rather than letting the latest result win.

## Canonical ownership matrix

| Loop | Owns | Observes | May recommend | May not decide | Must hand off |
|---|---|---|---|---|---|
| Architecture | Intended structural coherence and architectural conformance findings | Realized behavior and user or maintenance evidence affecting structure | Implementation or decision-record changes | That undocumented behavior becomes intended architecture | Behavioral defects, usability barriers, and maintenance debt |
| Implementation | Realized behavior and contract-fulfillment findings | Intent, structure, user evidence, and operational signals | Fixes, tests, safeguards, or clarification | Architecture or product intent | Structural ambiguity, adoption barriers, and sustainability debt |
| Adoption | Successful understanding, access, operation, and integration findings | Implementation and maintenance evidence affecting users | Documentation, defaults, interfaces, examples, or validation | Technical correctness, architecture, or business priority | Behavioral, structural, and freshness causes |
| Maintenance | Sustainability, freshness, recurrence, and operational-upkeep findings | All project surfaces for drift and recurring cost | Retirement, consolidation, automation, ownership, or debt tracking | Product semantics, destructive cleanup, or aesthetic refactoring | Behavioral, architectural, adoption, and lifecycle findings |
| Disposition | Finding identity, event history, reconciliation, and lifecycle projections | Specialist findings, evidence contributions, and authority decisions | Evidence, ownership, reconciliation, revalidation, or escalation | Specialist analysis or project action authority | Domain questions and authority gaps |
| Meta | Scope, capability, orchestration, generation, coverage, receipt, and convergence records | All loop results and cross-loop records | Strategy, assignment, sequencing, reruns, partitioning, or escalation | Specialist propositions, lifecycle adjudication, or remediation | Focal analysis, reconciliation, and human authority |

The detailed loop files apply this matrix to their domain. If a loop file conflicts with this table, this table controls until a recorded architecture revision resolves the conflict.
