# Assessment Contract

An Assessment Contract precommits how a non-trivial proposition will be evaluated before material results are interpreted. Use one when criteria could be changed after results become visible, when a comparative claim needs reproducibility, or when the consequence warrants stronger review. Do not require one for a simple, directly observed finding.

## Record

Required fields are `id`, `revision`, `proposition`, `scope`, `assessment_mode`, `evaluation_method`, `acceptance_conditions`, `required_evidence`, `evaluator`, and `frozen_at`. Add `reference_state`, `invariants`, `independence_requirement`, and `comparison_policy` when relevant.

The contract identifies the subject being assessed separately from the evaluation mechanism. A comparative proposition using words such as improved, regressed, restored, better, or worse identifies a reference artifact, revision or other stable identity, observation time, and evaluation context. If no reliable reference exists, record that limitation and do not invent one.

## Revision integrity

After material evaluation begins, do not silently change the proposition, relevant scope, reference state, method, acceptance conditions, critical invariants, or comparison policy. A legitimate material change creates a new assessment revision linked to the previous revision with a reason and one change class:

- `SUBJECT_CHANGE`: the evaluated subject changed under the same assessment.
- `ASSESSMENT_CHANGE`: evaluation rules changed while the subject did not.
- `BOTH_CHANGED`: both changed; results are not directly comparable without qualification.

Preserve the earlier assessment and result. A subject must not gain a more favorable disposition merely because thresholds, tests, data, preprocessing, warnings, reporting, or intended architecture were weakened or selectively changed after results appeared.

Evaluator independence is `SAME_ACTOR`, `SEPARATE_ROLE`, or `INDEPENDENT_ACTOR`. Required independence rises with impact, uncertainty, irreversibility, destructive potential, security, privacy, legal consequence, conflicting evidence, architectural reach, and requested authority. Logical role separation is sufficient when proportionate; YNM never requires multiple AI agents.

