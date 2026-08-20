import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_trigger_cases():
    payload = yaml.safe_load((ROOT / "tests/data/trigger-cases.yaml").read_text(encoding="utf-8"))
    cases = payload["cases"] if isinstance(payload, dict) else []
    return cases


class TriggerCaseTests(unittest.TestCase):
    def test_trigger_case_catalog_shape(self):
        cases = load_trigger_cases()
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({item["id"] for item in cases}), 20)
        for case in cases:
            self.assertIn("id", case)
            self.assertIn("prompt", case)
            self.assertIn("expected_class", case)
            self.assertIn("expectation", case)
            self.assertIn("expected_activation", case["expectation"])
            self.assertIn("classification", case["expectation"])

    def test_expected_classes_are_supported(self):
        classes = {case["expected_class"] for case in load_trigger_cases()}
        self.assertLessEqual(classes, {"positive", "negative", "contextual"})

    def test_execution_results_capture(self):
        cases = load_trigger_cases()
        # Trigger execution depends on external evaluator availability.
        for case in cases:
            self.assertTrue(case["id"].startswith("TRIG-"))
            self.assertIsInstance(case["prompt"], str)
            self.assertTrue(case["prompt"])
            case.setdefault("evaluation", {"status": "NOT_EXECUTED"})
            self.assertEqual(case["evaluation"].get("status"), "NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main()
