# Extension Model

An extension loop declares:

```yaml
name:
purpose:
scope:
evidence:
responsibilities:
non_responsibilities:
owns:
observes:
may_recommend:
may_not_decide:
finding_types:
inputs:
outputs:
dependencies:
handoffs:
authority:
termination_criteria:
rerun_conditions:
failure_modes:
```

It uses the canonical execution-context, evidence, finding, assessment, disposition, authorization, loop-result, lifecycle, and event contracts unchanged across every executor.

Extensions register with discovery and Meta Loop selection through capability metadata rather than hard-coded branches. Dependencies identify required information, not permission to execute another loop silently. Security, privacy, performance, compliance, research, documentation, operations, accessibility, and governance are possible extensions, not privileged built-ins.

Reject an extension that merely renames an existing responsibility, changes YES/NO/MAYBE semantics, makes its recommendation authoritative by default, or requires every project to adopt its tooling.
