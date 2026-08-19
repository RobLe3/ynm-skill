import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.validate_ynm import (
    TEXT_PATTERNS,
    _run_patterns,
    _tracked_text_files,
    check_baseline_integrity,
    check_public_sanitization,
    check_release,
    check_runtime_boundary,
    check_schema_references,
    check_yaml_disposition_quoting,
    load_json,
    load_yaml,
    resolve_ref,
    run,
    validate,
)
from scripts.execution_lifecycle import InvocationLifecycle, TERMINAL_REASONS


class YNMValidationTests(unittest.TestCase):
    def test_repository_is_consistent(self):
        self.assertEqual(run(), [])

    def test_maybe_requires_reason(self):
        finding = load_yaml(ROOT / "examples/data/finding.yaml")
        finding.pop("disposition_reason")
        errors = validate(finding, load_json(ROOT / "schemas/finding.schema.json"))
        self.assertTrue(any("disposition_reason" in error for error in errors))

    def test_partial_requires_coverage(self):
        result = load_yaml(ROOT / "examples/data/loop-result.yaml")
        result.pop("unreviewed_scope")
        errors = validate(result, load_json(ROOT / "schemas/loop-result.schema.json"))
        self.assertTrue(any("unreviewed_scope" in error for error in errors))

    def test_common_disposition_enum(self):
        self.assertEqual(resolve_ref("ynm-defs.schema.json#/$defs/disposition")["enum"], ["YES", "NO", "MAYBE"])

    def test_yaml_dispositions_are_quoted(self):
        self.assertEqual(check_yaml_disposition_quoting(), [])

    def test_adversarial_scenario_count(self):
        lines = (ROOT / "methodology/adversarial-validation.md").read_text().splitlines()
        self.assertEqual(len([line for line in lines if line.startswith("| ")]) - 1, 80 - 1)

    def test_schema_references_resolve(self):
        self.assertEqual(check_schema_references(), [])

    def test_release_gates_and_version(self):
        self.assertEqual(check_release(), [])

    def test_historical_baseline_is_immutable(self):
        self.assertEqual(check_baseline_integrity(), [])

    def test_public_runtime_is_sanitized(self):
        self.assertEqual(check_public_sanitization(), [])

    def test_sanitization_patterns_detect_private_data(self):
        sample = ROOT / "tmp" / "ynm-sanitization-sample.md"
        try:
            sample.parent.mkdir(parents=True, exist_ok=True)
            sample.write_text(
                "\n".join(
                    [
                        "path = " + '"' + "/" + "Users" + "/example/" + "private" + "/doc.md" + '"',
                        "window = " + '"' + "C:" + "\\" + "Users" + "\\" + "example" + "\\" + "private" + "\\" + "secret.txt" + '"',
                        "unc = " + '"' + "\\" + "\\" + "fileserver" + "\\" + "secret" + "\\" + "share" + "\\" + "artifact.txt" + '"',
                        "ap" + "i" + "_" + "key" + '="' + "secret" + '-value"',
                        "to" + "ken" + '="' + "secret" + '-value"',
                        "pas" + "sword" + '="' + "secret" + '-value"',
                        'repo = "https://github.com/' + "private" + '/example/repo"',
                    ],
                ),
                encoding="utf-8",
            )
            text = sample.read_text(encoding="utf-8")
            all_findings = []
            for check_id, patterns in TEXT_PATTERNS.items():
                all_findings.extend(_run_patterns(sample, text, check_id=check_id, patterns=patterns))

            checks = {check["check"] for check in all_findings}
            self.assertIn("PRIVATE_ABSOLUTE_PATH", checks)
            self.assertIn("CREDENTIAL_PATTERN", checks)
            self.assertIn("PRIVATE_REPOSITORY_REFERENCE", checks)
            self.assertGreaterEqual(len(all_findings), 4)
        finally:
            if sample.exists():
                sample.unlink()
            if sample.parent.exists():
                sample.parent.rmdir()

    def test_tracked_text_scanning_tolerates_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "-C", tmp, "init", "-q"], check=True)
            text_file = repo / "readable.txt"
            binary_file = repo / "binary.bin"
            text_file.write_text("hello", encoding="utf-8")
            binary_file.write_bytes(b"\xff\x00\x7f")
            subprocess.run(["git", "-C", tmp, "add", "readable.txt", "binary.bin"], check=True)

            with patch("validation.validate_ynm.ROOT", repo):
                text_files, binary_files = _tracked_text_files(repo)

            self.assertIn(repo / "readable.txt", text_files)
            self.assertIn(repo / "binary.bin", binary_files)

    def test_runtime_does_not_depend_on_provenance(self):
        self.assertEqual(check_runtime_boundary(), [])

    def run_bootstrap(self, project: Path, *args: str):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/project_integration.py"), str(project), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_discovery_and_unapproved_initialize_are_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "README.md").write_text("# Project\n")
            self.assertEqual(self.run_bootstrap(project).returncode, 0)
            self.assertFalse((project / ".ynm").exists())
            result = self.run_bootstrap(project, "--initialize")
            self.assertEqual(result.returncode, 0)
            self.assertFalse((project / ".ynm").exists())

    def test_bootstrap_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "README.md").write_text("# Project\n")
            first = self.run_bootstrap(project, "--initialize", "--apply")
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
            second = self.run_bootstrap(project, "--initialize", "--apply")
            self.assertEqual(second.returncode, 0, second.stderr)
            after = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_agents_integration_preserves_human_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            original = "# Instructions\n\nNever deploy automatically.\n"
            (project / "AGENTS.md").write_text(original)
            result = self.run_bootstrap(project, "--initialize", "--agents-section", "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            updated = (project / "AGENTS.md").read_text()
            self.assertTrue(updated.startswith(original.rstrip()))
            self.assertEqual(updated.count("<!-- YNM:BEGIN -->"), 1)
            self.assertEqual(updated.count("<!-- YNM:END -->"), 1)

    def test_malformed_agents_markers_block_all_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "AGENTS.md").write_text("<!-- YNM:BEGIN -->\n")
            result = self.run_bootstrap(project, "--initialize", "--agents-section", "--apply")
            self.assertEqual(result.returncode, 1)
            self.assertFalse((project / ".ynm").exists())

    def test_analysis_reaches_iteration(self):
        lifecycle = InvocationLifecycle()
        lifecycle.begin_iteration()
        self.assertEqual(lifecycle.phase, "ITERATION")

    def test_one_pass_convergence_reaches_delivery(self):
        lifecycle = InvocationLifecycle()
        lifecycle.begin_iteration()
        lifecycle.complete_iteration(converged=True)
        self.assertEqual(lifecycle.phase, "DELIVERY")
        self.assertTrue(lifecycle.converged)

    def test_material_information_gain_permits_iteration(self):
        lifecycle = InvocationLifecycle()
        lifecycle.begin_iteration()
        lifecycle.complete_iteration()
        self.assertTrue(lifecycle.may_iterate({"EVIDENCE"}))

    def test_no_information_gain_stops_repetition(self):
        lifecycle = InvocationLifecycle()
        lifecycle.begin_iteration()
        lifecycle.complete_iteration()
        self.assertFalse(lifecycle.may_iterate(set()))

    def test_scoped_reanalysis_revises_plan(self):
        lifecycle = InvocationLifecycle()
        lifecycle.begin_iteration()
        lifecycle.reanalyze("effective scope changed")
        self.assertEqual(lifecycle.phase, "ANALYSIS")
        self.assertEqual(lifecycle.plan_revision, 2)

    def test_iteration_bound_delivers_without_convergence(self):
        lifecycle = InvocationLifecycle(max_immediate_iterations=1)
        lifecycle.begin_iteration()
        lifecycle.complete_iteration()
        self.assertFalse(lifecycle.may_iterate({"EVIDENCE"}))
        self.assertEqual(lifecycle.phase, "DELIVERY")
        self.assertFalse(lifecycle.converged)

    def test_blocked_and_partial_paths_reach_delivery(self):
        for reason in ["BLOCKED", "PARTIAL", "CAPABILITY_LIMIT", "EVIDENCE_LIMIT"]:
            lifecycle = InvocationLifecycle()
            lifecycle.deliver(reason)
            self.assertEqual(lifecycle.phase, "DELIVERY")
            self.assertFalse(lifecycle.converged)

    def test_maybe_and_unreviewed_scope_survive_delivery(self):
        lifecycle = InvocationLifecycle()
        lifecycle.begin_iteration()
        lifecycle.complete_iteration()
        lifecycle.deliver("PARTIAL")
        receipt = lifecycle.receipt_fields(unresolved_findings=["YNM-MAYBE-1"], reviewed_scope=["a"], unreviewed_scope=["b"], persistence_authorized=False)
        self.assertEqual(receipt["unresolved_findings"], ["YNM-MAYBE-1"])
        self.assertEqual(receipt["unreviewed_scope"], ["b"])

    def test_delivery_does_not_grant_authorization(self):
        lifecycle = InvocationLifecycle()
        lifecycle.deliver("USER_STOP")
        receipt = lifecycle.receipt_fields(unresolved_findings=[], reviewed_scope=[], unreviewed_scope=[], persistence_authorized=False)
        self.assertEqual(receipt["delivery"]["authorization_status"], "NOT_REQUESTED")
        self.assertEqual(receipt["delivery"]["machine_state"], "emitted_stateless")

    def test_termination_requires_delivery(self):
        lifecycle = InvocationLifecycle()
        with self.assertRaises(ValueError):
            lifecycle.terminate()
        lifecycle.deliver("USER_STOP")
        lifecycle.terminate()
        self.assertEqual(lifecycle.phase, "TERMINATED")

    def test_every_terminal_reason_reaches_delivery(self):
        for reason in TERMINAL_REASONS:
            lifecycle = InvocationLifecycle()
            lifecycle.deliver(reason)
            self.assertIn("DELIVERY", lifecycle.phase_history)

    def test_v2_receipt_requires_lifecycle_delivery_fields(self):
        receipt = load_yaml(ROOT / "examples/data/run-receipt.yaml")
        schema = load_json(ROOT / "schemas/run-receipt.schema.json")
        self.assertEqual(validate(receipt, schema), [])
        receipt.pop("delivery")
        self.assertTrue(any("delivery" in error for error in validate(receipt, schema)))


if __name__ == "__main__":
    unittest.main()
