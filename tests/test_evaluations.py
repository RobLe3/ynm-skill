import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from scripts import run_evaluations
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
            self.assertEqual(status, 2)
            self.assertEqual([item["status"] for item in payload["models"]], ["AVAILABLE", "UNAVAILABLE"])
            self.assertEqual(payload["models"][1]["error"], "unsupported model")

    def test_near_miss_trigger_policy_is_non_activating(self):
        cases = yaml.safe_load((run_evaluations.ROOT / "tests/data/trigger-cases.yaml").read_text(encoding="utf-8"))["cases"]
        by_id = {item["id"]: item for item in cases}
        for case_id in ("TRIG-018", "TRIG-019", "TRIG-020"):
            self.assertFalse(by_id[case_id]["expectation"]["expected_activation"])

    def test_execution_stops_when_precommitted_model_is_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            run_evaluations, "probe", return_value=2
        ), patch.object(run_evaluations, "run_trigger_suite") as trigger_run, patch(
            "sys.argv", ["run_evaluations.py", "--run-triggers", "--output-dir", tmp]
        ):
            self.assertEqual(run_evaluations.main(), 2)
            trigger_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
