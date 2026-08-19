# Evaluation Integrity

YNM applies seven invariants proportionally. The controls exist to protect meaning, not to create procedural ceremony.

1. **Precommitment:** establish material evaluation criteria before interpreting results.
2. **Evaluation integrity:** a subject cannot obtain a favorable disposition by weakening, bypassing, contaminating, or selectively applying its evaluation.
3. **Epistemic honesty:** observation, measurement, inference, hypothesis, disposition, execution, and authorization remain distinct.
4. **Durable terminality:** every started review emits an explicit terminal Run Receipt.
5. **Independence proportional to consequence:** stronger consequences require stronger separation among proposal, evaluation, disposition, and authority.
6. **Information-gain reruns:** another immediate review requires a justified expectation of new information.
7. **Negative knowledge persists:** rejected, failed, and unresolved paths remain available for later review.

## Applying the invariants

Use an [Assessment Contract](../contracts/assessment.md) when criteria could otherwise move after results, when a comparison needs a stable reference, or when consequence warrants it. Freeze the assessment before material evaluation. The subject may change and the assessment may legitimately change, but changing the rules does not retroactively improve the earlier result.

Treat the following as possible integrity violations: weakening tests after failure, changing thresholds or expected output after results, excluding adverse evidence without reason, suppressing errors or warnings, redefining architecture solely to erase drift, removing failed user paths from scope, changing evaluation data or preprocessing after inspection, hiding costs, selecting only favorable runs, altering provenance, or treating missing evidence as positive.

When a subject controls its own tests, evidence generation, or reporting, record that dependence. Require a separate role or independent actor when consequence justifies it. The producer, evaluator, disposition authority, and action authority may be one person for low-consequence work, but the role combination remains explicit.

## Optional review profiles

- `BASIC`: read-only review, canonical findings, and a terminal receipt.
- `PERSISTENT`: BASIC plus longitudinal events, findings, assessments, and receipts.
- `AUDITABLE`: PERSISTENT plus stronger provenance and optional integrity witnesses.

Profiles describe capabilities; they never change YES/NO/MAYBE. Optional integrity fields include `project_snapshot`, `report_digest`, `evidence_bundle_digest`, and `previous_receipt_digest`. Manual, stateless, non-Git, and non-cryptographic execution remains valid.

These assurance profiles are separate from CONSTRAINED, STANDARD, and EXTENDED execution strategies. A review may be constrained and auditable, or extended and basic. Strategy changes workload shape; assurance profiles describe retained controls.

## Review value test

A valid cycle reduces uncertainty, reduces the future search space, or preserves why neither was possible. YES preserves why support was sufficient. NO preserves the contradiction and assumptions. MAYBE preserves the information gap. BLOCKED preserves the execution barrier. A rerun preserves the material change and expected information gain. No cycle terminates by forgetting what happened.
