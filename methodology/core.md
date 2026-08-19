# YNM Core Architecture

YNM evaluates explicit propositions through evidence and preserves the result as longitudinal knowledge. Its minimum complete form contains:

1. an explicit proposition and bounded scope;
2. typed, traceable evidence and interpretation;
3. a finding with YES, NO, or MAYBE disposition;
4. an applicable focal responsibility with explicit non-authority;
5. separation among disposition, execution, recommendation, and authorization;
6. append-only lifecycle history that preserves unresolved and negative knowledge;
7. justified rerun, revisit, and convergence behavior; and
8. an explicit terminal result for every started review.

These elements operate through the canonical [Invocation Lifecycle](execution-lifecycle.md): Analysis establishes the responsible review basis, Iteration performs focal work while information gain justifies it, and Delivery creates the mandatory terminal handoff. The macro lifecycle does not own specialist judgment or disposition reconciliation.

The canonical disposition meaning lives in [Disposition Contract](../contracts/disposition.md). Record shapes live in `contracts/`. Lifecycle transitions live in [Finding Lifecycle](lifecycle.md). Loop ownership lives in [Responsibility Model](responsibility-model.md). These locations are normative; summaries and examples must reference rather than redefine them.

## Built-in responsibilities

Architecture evaluates intended structural coherence. Implementation evaluates realized behavior against intent and contracts. Adoption evaluates successful understanding and use. Maintenance evaluates sustainability and operational upkeep. Disposition preserves and reconciles finding state. Meta discovers, scopes, coordinates, and stops review. A loop may observe another domain but must hand off decisions it does not own.

## Conditional core controls

Some controls become mandatory only when their condition applies:

- Freeze an Assessment Contract for non-trivial, comparative, consequential, or manipulation-sensitive evaluation.
- Create an Authorization record when an action is requested or recommended.
- Create an Execution Context for substantial or capability-sensitive review.
- Record a reference state for comparative propositions when one is reliably available.
- Increase evaluator independence with consequence.

These controls are part of core correctness when triggered, but trivial findings need no empty records.

## Optional capabilities

Persistent storage, integrity witnesses, multiple executors, parallel execution, automated orchestration, model routing, external connectors, cryptography, and provider-specific tools are optional. BASIC, PERSISTENT, and AUDITABLE describe assurance features. CONSTRAINED, STANDARD, and EXTENDED describe workload strategy. None changes truth standards or grants authority.

[Project Integration](project-integration.md) is also optional. It connects persistent YNM state to project conventions but is not a focal loop and does not change the minimum review method. Publication metadata and runtime adapters package implementations; they are not methodology semantics.

An implementation may use files, a database, forms, conversation, or manual notes. It remains YNM only if it preserves the core semantics and can reconstruct material evidence, dispositions, authority, transitions, and terminal outcomes.
