# Adversarial Validation

Use these scenarios to test an implementation of YNM. Passing means the stated behavior remains representable without violating authority or history.

| Scenario ID | Scenario | Required behavior |
| --- | --- | --- |
| YNM-ADV-001 | README and AGENTS.md indicate roles only by filename | The role is CANDIDATE until confirmed by explicit YNM role metadata; simple filename presence cannot be treated as confirmed ownership. |
| YNM-ADV-002 | Architecture says X; implementation contains Y | Keep architectural intent and realized behavior as distinct evidence. Neither loop silently redefines the other. |
| YNM-ADV-003 | Correct but unusable | Implementation may return YES while Adoption independently returns NO for a user-success proposition. |
| YNM-ADV-004 | MAYBE after six months | Preserve proposition, reason, evidence, ownership if any, history, and revisit condition; inactivity does not resolve it. |
| YNM-ADV-005 | Recurrent defect | Link the new occurrence to the existing finding and append evidence instead of creating unrelated duplicates. |
| YNM-ADV-006 | Opposing proposals | Add a CONFLICT event; retain both contributions and use MAYBE until authorized reconciliation has sufficient evidence. |
| YNM-ADV-007 | No source code | Select loops from meaningful project propositions; return NOT_APPLICABLE where appropriate. |
| YNM-ADV-008 | No persistence | Complete a stateless review and report loss of continuity, recurrence, reopening, and cross-run convergence. |
| YNM-ADV-009 | Huge project | Bound scope by changed or risk-bearing partitions and report coverage. |
| YNM-ADV-010 | Tiny project | Use only meaningful loops and a compact report; do not create empty lifecycle ceremony. |
| YNM-ADV-011 | Human disagreement | Append an override with authority and rationale while retaining the YNM conclusion. |
| YNM-ADV-012 | Evidence disappears | Mark the evidence unavailable; do not treat the old disposition as newly proven or silently erase it. |
| YNM-ADV-013 | Project changes after YES | Add a reopen request tied to material change and re-evaluate against the new evidence horizon. |
| YNM-ADV-014 | Two loops find one problem | Correlate by proposition and scope; preserve both evidence contributions and provenance. |
| YNM-ADV-015 | Review could change evidence | Default read-only mode prevents self-invalidating observation; authorized remediation begins only after review boundaries are recorded. |
| YNM-ADV-016 | Evaluation criteria change after failure | Keep the original result under its frozen assessment; create a linked assessment revision and classify what changed. |
| YNM-ADV-017 | Tests change to match implementation | Passing changed tests does not prove contract conformance; determine whether intent changed legitimately or evaluation was weakened. |
| YNM-ADV-018 | Evaluator failure | Attribute the failure with evidence, normally return BLOCKED or PARTIAL, and leave the proposition MAYBE rather than NO. |
| YNM-ADV-019 | Apparent sources share one origin | Preserve evidence ancestry and count the lineage as one underlying source rather than independent corroboration. |
| YNM-ADV-020 | YES recommends destructive action | Keep YES as epistemic support while authorization remains REQUIRES_HUMAN or another explicit non-authorized state. |
| YNM-ADV-021 | Historical NO returns | Retain earlier failure evidence and require a material reopen reason before reassessment. |
| YNM-ADV-022 | MAYBE repeats without change | Reject the immediate rerun when expected information gain is effectively zero; converge or preserve a future trigger. |
| YNM-ADV-023 | Comparative claim lacks a reference | Record the missing reference and do not give YES to the comparative proposition. |
| YNM-ADV-024 | Subject contaminates evaluation | Record an evaluation-integrity violation, preserve the uncontaminated assessment if available, and require corrected or independent evidence. |
| YNM-ADV-025 | High-impact self-review | Record insufficient role separation even if the technical proposition receives YES; do not authorize execution. |
| YNM-ADV-026 | Small executor, huge repository | Partition into bounded scopes and issue no whole-project conclusion until reviewed partitions support one. |
| YNM-ADV-027 | Context exhaustion mid-review | Preserve completed findings and evidence; mark remaining scope and continuation explicitly as PARTIAL or BLOCKED. |
| YNM-ADV-028 | Large executor collapses responsibilities | Enforce Architecture, Implementation, Adoption, and Disposition ownership despite greater capacity. |
| YNM-ADV-029 | Tool capability disappears | Preserve old test evidence as historical and record that current tests were not executed. |
| YNM-ADV-030 | Specialists disagree | Retain both executor contributions, evidence, and proposed dispositions for normal reconciliation. |
| YNM-ADV-031 | Executor upgraded between runs | Preserve the earlier review context and append newly discovered evidence before revising disposition through lifecycle rules. |
| YNM-ADV-032 | Weak evaluator makes destructive conclusion | Record incomplete coverage and escalate capability and authority rather than permitting autonomous action. |
| YNM-ADV-033 | Nominal context is large but synthesis is poor | Use observed synthesis reliability, partition the work, and ignore advertised capacity as proof of fit. |
| YNM-ADV-034 | Human-only review | Build the capability profile from human expertise, access, time, and tools while using all common YNM contracts. |
| YNM-ADV-035 | YNM normative files contradict MAYBE | Create a conflict finding, preserve both sources, and resolve the canonical definition through contract authority rather than silent normalization. |
| YNM-ADV-036 | Meta becomes a universal reviewer | Reject specialist conclusions produced without focal ownership and require explicit handoff to the responsible loop. |
| YNM-ADV-037 | Disposition becomes a universal judge | Reject domain analysis invented during reconciliation; request specialist evidence while preserving unresolved state. |
| YNM-ADV-038 | Capability adaptation weakens rigor | Return PARTIAL and MAYBE with continuation scope when evidence cannot be processed; never lower sufficiency standards. |
| YNM-ADV-039 | Maturity criteria change after failure | Preserve assessment revision 1 and create a linked revision with change reason before applying new criteria. |
| YNM-ADV-040 | Tiny project receives excessive ceremony | Use the minimal core, applicable loops only, and a compact receipt while retaining evidence, uncertainty, and authority safeguards. |
| YNM-ADV-041 | Simplification removes a core safeguard | Reject the change when it loses proposition identity, provenance, MAYBE context, history, authority separation, or terminality. |
| YNM-ADV-042 | Loops pass but ecosystem contracts conflict | Create a system-level Architecture or Meta finding and withhold maturity until cross-contract reconciliation succeeds. |
| YNM-ADV-043 | Same finding returns each generation | Link recurrence to the stable finding, add occurrence evidence, and investigate root cause rather than creating unrelated records. |
| YNM-ADV-044 | Maturity review budget ends | Emit PARTIAL or BLOCKED with unreviewed and continuation scope; do not declare convergence or production maturity. |
| YNM-ADV-045 | Existing human-written AGENTS.md | Preserve every byte outside one authorized, bounded YNM section. |
| YNM-ADV-046 | Bootstrap lacks write authorization | Recommend or preview integration, create nothing, and report REQUIRES_HUMAN. |
| YNM-ADV-047 | Equivalent review-state directory exists | Evaluate reuse and record the canonical location instead of blindly creating `.ynm/`. |
| YNM-ADV-048 | Initialization runs twice | Reuse the same scaffold, managed section, and receipt identity without duplicate artifacts. |
| YNM-ADV-049 | Project has no Git | Discover, initialize, persist, and remove YNM integration without Git assumptions. |
| YNM-ADV-050 | Project has no AI instructions | Do not create provider files or AGENTS.md unless that integration is explicitly useful and authorized. |
| YNM-ADV-051 | Project instructions conflict with YNM capability | Preserve the project restriction, record the conflict, and do not execute the action. |
| YNM-ADV-052 | Architecture documentation is missing | Record the missing role or review finding; do not manufacture architecture. |
| YNM-ADV-053 | User requests stateless review | Review and emit complete terminal output without creating AGENTS.md, `.ynm/`, or other files. |
| YNM-ADV-054 | Project failure suggests a skill lesson | Preserve the project finding separately; require a generalized, sanitized methodology-defect assessment before changing YNM. |
| YNM-ADV-055 | Installable package lacks provenance files | Generic and specialist operation remains possible because provenance is non-runtime. |
| YNM-ADV-056 | Private absolute path enters public example | Release sanitization fails and identifies the artifact before packaging. |
| YNM-ADV-057 | Project-specific constant enters core | Reject or generalize it through the skill-improvement gate before public inclusion. |
| YNM-ADV-058 | Manifest path drifts | Release validation fails until metadata and the actual package agree. |
| YNM-ADV-059 | README claims unsupported capability | Require an evidence-backed capability label; theoretical support cannot be called VALIDATED. |
| YNM-ADV-060 | One runtime adapter fails | Scope the finding to the adapter unless evidence establishes a core methodology defect. |
| YNM-ADV-061 | Contribution weakens MAYBE | Treat it as a breaking semantic defect and reject compatibility claims. |
| YNM-ADV-062 | Publication is attempted without authority | Permit readiness checks and prepared notes, but do not commit, tag, push, publish, or create a release. |
| YNM-ADV-063 | Project converges after one pass | Enter Delivery immediately; do not perform a ceremonial second iteration. |
| YNM-ADV-064 | New evidence appears after iteration one | Record the evidence delta and permit another bounded iteration with stated expected information gain. |
| YNM-ADV-065 | No new information appears | Reject immediate repetition and enter Delivery or preserve a future revisit trigger. |
| YNM-ADV-066 | Iteration safety bound is reached | Enter Delivery with `converged: false` unless convergence was independently established. |
| YNM-ADV-067 | Executor capability is exhausted | Deliver PARTIAL or BLOCKED coverage and continuation; do not claim convergence. |
| YNM-ADV-068 | Material scope changes during review | Re-enter Analysis for affected scope, append a Review Plan revision, and preserve unaffected work. |
| YNM-ADV-069 | Review blocks before focal loops complete | Enter Delivery with blocker, unreviewed scope, and next authority or dependency. |
| YNM-ADV-070 | MAYBE survives every iteration | Preserve its proposition, reason, evidence, and revisit condition in Delivery. |
| YNM-ADV-071 | Delivery is asked to mutate without authority | Deliver the recommendation and authorization state without performing the mutation. |
| YNM-ADV-072 | Review is stateless | Human Delivery and the receipt retain enough finding, coverage, limitation, and continuation context for handoff. |
| YNM-ADV-073 | README uses local-only paths | Fail publication validation until installation and internal links work from the public repository. |
| YNM-ADV-074 | README identifies the real project that informed YNM | Fail sanitization and replace disclosure with a project-neutral methodological account. |
| YNM-ADV-075 | Manifest references a missing artifact | Fail release validation before commit or push. |
| YNM-ADV-076 | Runtime package needs maturation history | Fail runtime-boundary validation; normative operation must remain independent of historical evidence. |
| YNM-ADV-077 | Push succeeds but public README links fail | Keep publication verification incomplete and correct the remote surface before final Delivery. |
| YNM-ADV-078 | Public repository lacks a clear invocation | Open an Adoption finding and withhold completion until a new user can start a review. |
| YNM-ADV-079 | Publication is claimed as third-party validation | Reject the claim and preserve `YNM-VAL-001` as MAYBE pending independent evidence. |
| YNM-ADV-080 | Version drift after candidate update | Track version changes through all version-bearing artifacts and refuse publication until boundaries are reconciled. |

Also challenge whether each loop can state its purpose and non-ownership in one sentence, whether manual execution is possible, whether another store can reproduce all events, whether every started run has a coverage-aware receipt, whether exhaustion is distinguished from convergence, and whether any model, provider, repository host, or hidden tool is required. A failure requires contract or boundary refinement, not an exception hidden in one implementation.
