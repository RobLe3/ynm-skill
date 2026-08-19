# Meta Loop

**Purpose:** Coordinate Analysis, applicable focal reviews during Iteration, and mandatory Delivery, stopping when further immediate iteration is unjustified.

- **Scope:** executor capability and drift, project complexity, capability-to-scope fit, project-integration need, documentation-role discovery, granularity, evidence windows, mutation awareness, assessment need, reference state, evaluator independence, loop assignment, dependencies, ordering, safe parallelism, generations, material change, reruns, cross-scope synthesis, exhaustion, coverage, convergence, terminal receipts, and escalation.
- **Inputs and evidence:** project characterization, prior state, change summary, loop capabilities, loop results, and authority boundaries.
- **Owns:** review scope and partitions, execution-context and coverage records, generation and Run Receipt records, orchestration decisions, assessment-control selection, and convergence evaluation.
- **Observes:** all loop results and cross-loop records.
- **May recommend:** strategy, granularity, partitioning, stateless or persistent operation, Project Integration, loop assignment, sequencing, bounded reruns, scope adjustment, or capability escalation.
- **May not decide:** specialist propositions, project intent, or remediation authority.
- **Must hand off:** focal analysis to specialists and unresolved authority to humans.
- **Finding types:** capability mismatch, false coverage, provenance loss, executor exhaustion, orchestration conflict, assessment-integrity violation, evidence contamination, unjustified rerun, unresolved dependency, authority gap, missing terminal result, or non-convergence.
- **Output:** selected-loop plan, run records, review report, convergence decision, and optional state request.
- **Termination:** convergence, explicit escalation, or a blocker that prevents useful coordination.
- **Rerun:** justified by material change or a conforming rerun request.
- **Failure modes:** doing specialist work, running every loop ceremonially, infinite iteration, or hiding conflicts to declare success.

## Implementation-neutral algorithm

```text
declare_boundaries_authority_and_review_profile()
project = discover_project()
integration = discover_existing_project_instructions_documentation_roles_and_ynm_state()
capabilities = discover_executor_capabilities_conservatively()
complexity = characterize_project_complexity(project, requested_scope)
fit = determine_capability_scope_fit(capabilities, complexity)
strategy = select_execution_strategy(fit)
select_project_integration_if_useful_without_mutating(integration, authority)
scopes = partition_scope_if_needed(requested_scope, fit)
previous = load_previous_state_if_available_and_permitted()
current = characterize_project_state(project)
changes = compare_subject_assessment_and_evidence_horizons(previous, current)
revalidate_prior_dispositions_affected_by_material_change(changes)
loops = select_applicable_loops(current, changes, requested_scope)
assignments = assign_strategy_scope_and_executor_per_loop(loops, capabilities)
generation = begin_review_generation(requested_scope, scopes, evidence_fingerprint)
review_plan = record_analysis_output_and_requested_effective_scope()

terminal_outcome = null
immediate_reruns = 0

while terminal_outcome is null:
    for bounded_scope in pending_scopes:
        windows = define_controlled_evidence_windows(bounded_scope, capabilities)
        assessments = require_and_freeze_proportionate_assessment_contracts(assignments)
        identify_reference_states_and_independence_requirements(assessments)
        results = execute_assigned_loops(assignments, bounded_scope, windows)
        persist_or_emit_intermediate_results()

        if capability_exhausted():
            remaining = preserve_and_repartition_remaining_scope()
            if responsible_continuation_unavailable():
                record_partial_or_blocked_coverage_and_escalation(remaining)
                terminal_outcome = "PARTIAL_REVIEW" or "BLOCKED_REVIEW"
                break

        detect_assessment_rule_changes_and_evidence_contamination()
        findings = normalize_to_contract(results)
        correlate_with_existing_findings(findings, previous)
        append_evidence_and_events_without_rewriting_history()
        identify_duplicates_relationships_dependencies_and_conflicts()

    if terminal_outcome is not null:
        break

    if cross_scope_synthesis_is_supported(capabilities, completed_scopes):
        synthesize_progressively_with_provenance()
    else:
        record_synthesis_dependency_or_escalation()

    process_proposed_dispositions_under_declared_authority()
    evaluate_resolution_reopen_and_supersession_requests()
    reruns = validate_rerun_requests_for_material_delta_and_information_gain()

    if authority_safety_or_capability_escalation_required():
        terminal_outcome = "ESCALATED_REVIEW"
    elif executor_exhausted_with_remaining_scope():
        terminal_outcome = "PARTIAL_REVIEW"
    elif convergence_criteria_hold_independently_of_executor_limits():
        terminal_outcome = "CONVERGED_REVIEW"
    elif justified_immediate_reruns_exist(reruns) and immediate_reruns < rerun_limit:
        pending_scopes = select_bounded_rerun_scopes(reruns)
        immediate_reruns += 1
    else:
        preserve_future_revisit_conditions(reruns)
        terminal_outcome = derive_completed_partial_or_blocked_outcome()

enter_delivery_for_every_terminal_outcome()
persist_state_only_if_permitted()
emit_terminal_run_receipt_with_lifecycle(terminal_outcome, limitations, persistence_status)
produce_human_delivery_and_machine_continuation_state()
```

Loops with no meaningful scope return `NOT_APPLICABLE`. Independent loops may run in parallel only when capability and dependencies permit it; reconciliation follows completion. Default to one immediate rerun per loop per generation. Capability is rediscovered when tools, executor, access, or budgets materially change. Exceptions, blockers, exhausted budgets, and unavailable authority still flow through receipt emission; no started run may disappear silently.
