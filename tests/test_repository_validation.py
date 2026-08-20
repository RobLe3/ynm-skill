import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from validation import validate_ynm as validator


class RepositoryValidationTests(unittest.TestCase):
    def test_current_path_like_evidence_must_resolve(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "state/releases/1.3.0/findings.yaml"
            target.parent.mkdir(parents=True)
            target.write_text(
                yaml.safe_dump({"findings": [{"id": "F-1", "evidence": ["contracts/missing.md", "urn:evidence:external"]}]}),
                encoding="utf-8",
            )
            errors = validator.check_current_evidence_references(root, "1.3.0")
            self.assertEqual(errors, ["F-1: evidence path does not exist: contracts/missing.md"])

    def test_evaluation_scenarios_and_schemas_are_valid(self):
        self.assertEqual(validator.check_evaluation_artifacts(), [])

    def test_sanitization_count_drift_is_actionable_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_path = root / "state/releases/1.3.0/sanitization-report.yaml"
            report_path.parent.mkdir(parents=True)
            stored = {
                "scope": "ALL_TRACKED_TEXT",
                "files_scanned": 107,
                "files_excluded_as_binary": 0,
                "result": "PASS",
                "checks": [],
                "findings": [],
            }
            report_path.write_text(yaml.safe_dump(stored), encoding="utf-8")
            before = report_path.read_bytes()
            actual = {**stored, "files_scanned": 108}

            with patch("validation.validate_ynm.CURRENT_VERSION", "1.3.0"):
                errors = validator._compare_sanitization_report(root, actual, findings=[])

            self.assertTrue(any("recorded=107 actual=108" in error for error in errors), errors)
            self.assertTrue(any("--refresh-sanitization-report" in error for error in errors), errors)
            self.assertEqual(report_path.read_bytes(), before)

            validator.write_sanitization_report(root, "1.3.0", actual, dry_run=False)
            refreshed = yaml.safe_load(report_path.read_text(encoding="utf-8"))
            self.assertEqual(refreshed["files_scanned"], 108)

    def test_workflow_dependency_graph_is_valid(self):
        self.assertEqual(validator.check_workflow_invariants(), [])


if __name__ == "__main__":
    unittest.main()
