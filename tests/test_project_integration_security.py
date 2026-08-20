import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.project_integration import (
    BEGIN_MARKER,
    END_MARKER,
    IntegrationError,
    Operation,
    _file_action_for,
    _safe_candidate_target,
    apply_operations,
    initialize_project,
    parse_agents_section_state,
    validate_candidate_path,
)


class ProjectIntegrationSecurityTests(unittest.TestCase):
    def test_traversal_windows_unc_and_reserved_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for candidate in ["../escape", "/absolute", r"C:\escape", "C:/escape", r"\\server\share", ".git/config", ".github/workflows/x"]:
                with self.subTest(candidate=candidate):
                    with self.assertRaises(IntegrationError):
                        validate_candidate_path(root, candidate)

    @unittest.skipIf(os.name == "nt", "symlink creation requires additional Windows privileges")
    def test_external_symlink_components_and_targets_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = (base / "project").resolve()
            outside = (base / "outside").resolve()
            root.mkdir()
            outside.mkdir()
            (root / "linked-dir").symlink_to(outside, target_is_directory=True)
            (root / "linked-file").symlink_to(outside / "target.yaml")
            for candidate in ["linked-dir/state.yaml", "linked-file"]:
                with self.subTest(candidate=candidate):
                    with self.assertRaises(IntegrationError):
                        _safe_candidate_target(root, candidate)

    def test_foreign_ownership_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "config.yaml"
            target.write_text("managed_by: another-tool\n", encoding="utf-8")
            self.assertEqual(_file_action_for(target, "managed_by: ynm\n", root)[0], "CONFLICT")

    def test_malformed_agents_markers_are_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "AGENTS.md"
            for content in [BEGIN_MARKER, f"{END_MARKER}\n{BEGIN_MARKER}", f"{BEGIN_MARKER}\n{BEGIN_MARKER}\n{END_MARKER}"]:
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    self.assertEqual(parse_agents_section_state(path)[0], "CONFLICT")

    def test_failed_second_write_rolls_back_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            first = root / "first.txt"
            second = root / "second.txt"
            operations = [Operation(first, "create", "one"), Operation(second, "create", "two")]
            calls = 0

            def replace(path, content):
                nonlocal calls
                calls += 1
                if calls == 2:
                    return False, "FAILED: injected"
                path.write_text(content, encoding="utf-8")
                return True, "SUCCEEDED"

            with patch("scripts.project_integration.safe_replace", side_effect=replace):
                outcome, completed = apply_operations(root, operations, "test")
            self.assertEqual(outcome, "ROLLED_BACK")
            self.assertEqual(completed, [])
            self.assertFalse(first.exists())

    def test_unauthorized_initialization_does_not_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            receipt, status = initialize_project(root, ".ynm", apply=False, with_agents=False, dry_run=False)
            self.assertEqual(status, 0)
            self.assertFalse(receipt["writes_attempted"])
            self.assertFalse(receipt["writes_completed"])
            self.assertEqual(receipt["persistence_outcome"], "NOT_AUTHORIZED")
            self.assertFalse((root / ".ynm").exists())


if __name__ == "__main__":
    unittest.main()
