import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts import run_evaluations
from scripts import score_evaluations
from validation import validate_ynm


class EvaluationHarnessTests(unittest.TestCase):
    def test_repository_evaluation_artifacts_validate(self):
        self.assertEqual(validate_ynm.check_evaluation_artifacts(), [])

    def test_probe_preserves_unavailable_model_as_evidence(self):
        available = {
            "returncode": 0,
            "started_at": "2026-08-20T00:00:00Z",
            "elapsed_seconds": 1.0,
            "input_tokens": 1,
            "output_tokens": 1,
            "raw_output": "MODEL_AVAILABLE",
            "raw_events": "",
            "stderr": "",
            "error": "",
            "activation_evidence": "NOT_OBSERVED",
        }
        unavailable = {**available, "returncode": 1, "raw_output": "", "error": "unsupported model"}
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            run_evaluations, "invoke", side_effect=[available, unavailable]
        ), patch.object(run_evaluations, "client_version", return_value="codex-cli test"):
            output = Path(tmp) / "availability.yaml"
            status = run_evaluations.probe(["large", "small"], output)
            payload = yaml.safe_load(output.read_text(encoding="utf-8"))
            self.assertEqual(status, 0)
            self.assertEqual([item["status"] for item in payload["models"]], ["AVAILABLE", "UNAVAILABLE"])
            self.assertEqual(payload["models"][1]["error"], "unsupported model")

    def test_near_miss_trigger_policy_is_non_activating(self):
        cases = yaml.safe_load((run_evaluations.ROOT / "tests/data/trigger-cases.yaml").read_text(encoding="utf-8"))["cases"]
        by_id = {item["id"]: item for item in cases}
        for case_id in ("TRIG-018", "TRIG-019", "TRIG-020"):
            self.assertFalse(by_id[case_id]["expectation"]["expected_activation"])

    def test_execution_stops_when_primary_model_is_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            run_evaluations, "probe", return_value=2
        ), patch.object(run_evaluations, "run_trigger_suite") as trigger_run, patch(
            "sys.argv", ["run_evaluations.py", "--run-triggers", "--output-dir", tmp]
        ):
            self.assertEqual(run_evaluations.main(), 2)
            trigger_run.assert_not_called()

    def test_replication_selection_uses_first_available_frozen_candidate(self):
        payload = {"models": [
            {"model": "gpt-5.6-sol", "status": "AVAILABLE"},
            {"model": "gpt-5.4-mini-2026-03-17", "status": "UNAVAILABLE"},
            {"model": "gpt-5.6-terra", "status": "AVAILABLE"},
            {"model": "gpt-5.6-luna", "status": "AVAILABLE"},
            {"model": "gpt-5.4", "status": "AVAILABLE"},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "availability.yaml"
            path.write_text(yaml.safe_dump(payload), encoding="utf-8")
            self.assertEqual(run_evaluations.selected_models(path), ["gpt-5.6-sol", "gpt-5.6-terra"])

    def test_replication_unavailability_does_not_block_primary(self):
        payload = {"models": [
            {"model": "gpt-5.6-sol", "status": "AVAILABLE"},
            *({"model": model, "status": "UNAVAILABLE"} for model in run_evaluations.REPLICATION_CANDIDATES),
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "availability.yaml"
            path.write_text(yaml.safe_dump(payload), encoding="utf-8")
            self.assertEqual(run_evaluations.selected_models(path), ["gpt-5.6-sol"])

    def test_behavioral_activation_rule_is_conservative(self):
        self.assertTrue(run_evaluations.behavioral_activation("Using YNM for this review."))
        self.assertTrue(run_evaluations.behavioral_activation("YES NO MAYBE\nReviewed scope\nUnreviewed scope\nDelivery"))
        self.assertIsNone(run_evaluations.behavioral_activation("Maybe this is fine."))

    def test_blinded_sample_ids_do_not_expose_condition(self):
        control = score_evaluations.sample_id("YNM-EVAL-001-CONTROL-model-1")
        treatment = score_evaluations.sample_id("YNM-EVAL-001-YNM-model-1")
        self.assertRegex(control, r"^S-[a-f0-9]{12}$")
        self.assertNotEqual(control, treatment)

    def test_identifier_namespaces_are_distinct_for_new_findings(self):
        scenarios = yaml.safe_load((run_evaluations.ROOT / "evaluations/scenarios.yaml").read_text(encoding="utf-8"))["scenarios"]
        findings = yaml.safe_load((run_evaluations.ROOT / "state/releases/1.3.0/findings.yaml").read_text(encoding="utf-8"))["findings"]
        scenario_ids = {item["id"] for item in scenarios}
        finding_ids = {item["id"] for item in findings if item["id"].startswith("YNM-EMP-")}
        self.assertFalse(scenario_ids & finding_ids)

    def test_core_effect_decision_does_not_trade_safety_for_quality(self):
        control = {"material_recall": 0.5, "material_precision": 0.5, "unsupported_claim_rate": 0.2, "false_finding_rate": 0.1, "required_maybe_recall": 0.5, "unjustified_maybe": 1, "evidence_traceability": 1, "lifecycle_quality": 1, "completion_quality": 1, "authority_violations": 0}
        improved = {**control, "material_recall": 1.0, "evidence_traceability": 2, "authority_violations": 1}
        self.assertEqual(score_evaluations.decide_core_effect(control, improved)["disposition"], "NO")

    def test_core_effect_requires_improvement_or_control_ceiling(self):
        tied = {"material_recall": 0.5, "material_precision": 0.5, "unsupported_claim_rate": 0.0, "false_finding_rate": 0.0, "required_maybe_recall": 0.5, "unjustified_maybe": 0, "evidence_traceability": 1, "lifecycle_quality": 1, "completion_quality": 1, "authority_violations": 0}
        self.assertEqual(score_evaluations.decide_core_effect(tied, tied)["disposition"], "MAYBE")
        improved = {**tied, "material_recall": 1.0}
        self.assertEqual(score_evaluations.decide_core_effect(tied, improved)["disposition"], "YES")


if __name__ == "__main__":
    unittest.main()
