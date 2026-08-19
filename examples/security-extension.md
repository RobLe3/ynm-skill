# Security Loop Extension Example

This example tests the extension contract without changing YNM core semantics.

```yaml
name: Security Loop
purpose: Evaluate explicit propositions about resistance to identified security threats.
scope: Declared threat model, security controls, attack surfaces, and relevant operational evidence.
evidence: [threat models, source or procedure inspection, configuration, tests, incident records]
responsibilities: [security-control and threat-model findings]
non_responsibilities: [business risk acceptance, legal compliance, remediation authorization]
owns: [security propositions and specialist findings]
observes: [architecture boundaries, implementation controls, operational and incident evidence]
may_recommend: [control changes, additional evidence, threat-model clarification]
may_not_decide: [risk acceptance, compliance status outside evidence, remediation authorization]
finding_types: [missing control, ineffective control, threat-model gap, conflicting security evidence]
inputs: [review scope, threat model, available project evidence, prior YNM state]
outputs: [canonical findings, evidence contributions, handoffs, loop result]
dependencies: [Architecture for intended trust boundaries, Implementation for realized control behavior]
handoffs: [Disposition for lifecycle, Meta for orchestration, human authority for risk acceptance]
authority: advisory unless a review charter explicitly delegates disposition authority
termination_criteria: Selected security propositions are evaluated or explicitly blocked.
rerun_conditions: [material threat, control, dependency, or evidence change]
failure_modes: [invented threats, unsupported compliance claims, self-authorized remediation]
```

The loop uses canonical evidence and finding records, proposes YES/NO/MAYBE against explicit propositions, emits a standard loop result and Run Receipt, and preserves action authorization separately. Meta can select or defer it through capability metadata. No core contract needs a Security-specific field.
