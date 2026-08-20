# Epistemic Boundaries

YNM is a bounded evidence-backed review methodology. It produces auditable `YES`, `NO`, or `MAYBE` judgments about explicit propositions under declared scope, evidence, assessment, executor, authority, resource, and temporal conditions. A disposition is not a universal proof.

Conceptually:

```text
proposition + reviewed scope + available evidence + assessment criteria
+ executor capability + authority + resource boundary + evidence snapshot
= bounded disposition
```

## Bounded Review Profile 1

`YNM-BRP-1` is the initial supported usability profile. It applies to project or repository reviews where propositions are explicit or decomposable, evidence can be referenced, and reviewed and unreviewed scope can be stated. Execution is read-only by default and advisory. Humans retain consequential decision, mutation, certification, publication, and release authority.

Within this profile:

- `YES` requires affirmative evidence for the bounded proposition;
- `NO` requires contradicting evidence;
- material missing evidence produces `MAYBE`;
- evidence remains traceable;
- unreviewed scope remains explicit; and
- Delivery exposes the result's validity boundary.

Usable means that YNM can produce a structured, bounded, inspectable result that supports a decision while exposing its limitations. It does not mean perfect, exhaustive, model-independent, formally verified, autonomous, or error-free.

## Search and termination boundary

YNM cannot generally prove that another arbitrary review pass would discover nothing important. Convergence is operational, not proof of exhaustive knowledge. Review stops when the bounded proposition has a defensible disposition, required evidence is unavailable, no permitted operation can obtain it, further work has insufficient expected information value, an execution boundary is reached, or human escalation is required.

This limit is related in spirit to limits represented by the Halting Problem. YNM is not itself a proof or direct instance of the Halting Problem.

## Semantic decision boundary

YNM is not a universal decision procedure for arbitrary nontrivial semantic properties of arbitrary software. Unrestricted claims such as “this program is correct” or “this system is always secure” must normally be decomposed into propositions tied to concrete interfaces, snapshots, criteria, and evidence.

This boundary resembles the class of limits formalized by Rice's theorem. The theorem does not validate YNM; it helps explain why bounded claims are preferable to unrestricted semantic assurances.

## Self-validation boundary

Internal validation can establish contract consistency, schema validity, lifecycle behavior, reproducible package content, deterministic checks, benchmark performance, and observed executor behavior. Repeating internal review cannot by itself establish independent interoperability, universal methodological adequacy, or universal cross-model effectiveness.

Gödel's incompleteness theorem is an intellectual analogy for limits on sufficiently expressive formal systems proving their own completeness or consistency. It does not directly prove a limitation of YNM. `YNM-VAL-001` remains separate because independent evidence is categorically different from maintainer-operated self-evaluation.

## Open-world evidence boundary

YNM can reason only from accessible evidence. Repository evidence does not automatically establish production behavior, historical incidents, operator practice, deployment topology, undocumented dependencies, future behavior, or withheld information.

```text
unobserved != correct
unobserved != incorrect
```

When the missing evidence is material, the bounded disposition is normally `MAYBE`.

## Executor boundary

Provider-neutral design means the contracts do not require a particular provider, model, human, agent, or runtime. It does not mean every executor follows the contracts with equal quality. Methodology validity and executor effectiveness are separate propositions, and empirical claims retain the tested executor profile.

## Resource boundary

YNM operates under finite context, tokens, time, tools, evidence, memory, and compute. A valid result may therefore be `MAYBE`, `PARTIAL`, or `BLOCKED`. Resource exhaustion never becomes certainty.

## Temporal boundary

A disposition applies to an evidence snapshot. Code, configuration, dependencies, deployments, criteria, or new evidence can invalidate it. Material results identify the relevant snapshot or temporal reference.

## Validity boundary in Delivery

Every material Delivery must expose or make recoverable:

```yaml
validity_boundary:
  propositions: []
  reviewed_scope: []
  unreviewed_scope: []
  evidence_snapshot: ""
  evidence_limitations: []
  executor_profile: ""
  authority: ""
  execution_limits: []
  temporal_reference: ""
```

The boundary may be concise in user-facing output, but it must remain sufficient to interpret each material disposition.
