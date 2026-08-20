import sys
import subprocess
import tempfile
import unittest
from pathlib import Path, PureWindowsPath
from unittest.mock import patch

import validation.validate_ynm as validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.validate_ynm import (
    _public_sanitization_report_path,
    TEXT_PATTERNS,
    check_adversarial_scenarios,
    _is_allowed_violation,
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
    write_sanitization_report,
    check_workflow_invariants,
    validate,
)
from scripts.project_integration import classify_roles
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

    def test_adversarial_scenarios_are_valid(self):
        lines = (ROOT / "methodology/adversarial-validation.md").read_text().splitlines()
        rows = [line for line in lines if line.strip().startswith("|") and "|" in line]
        self.assertGreaterEqual(len(rows), 3)
        self.assertEqual(check_adversarial_scenarios(), [])

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

    def test_sanitization_path_keys_handle_windows_style_paths(self):
        class FakePath:
            def relative_to(self, _root: Path):
                return PureWindowsPath("validation\\validate_ynm.py")

        finding = {"check": "PROVIDER_SPECIFIC_CORE_ASSUMPTION"}
        self.assertTrue(_is_allowed_violation(FakePath(), finding))

    def test_run_patterns_normalizes_finding_paths(self):
        text = 'provider = "gpt-5.3-codex-spark"\n'
        path = ROOT / "validation/validate_ynm.py"
        findings = _run_patterns(path, text, check_id="PROVIDER_SPECIFIC_CORE_ASSUMPTION", patterns=TEXT_PATTERNS["PROVIDER_SPECIFIC_CORE_ASSUMPTION"])
        self.assertTrue(findings)
        for finding in findings:
            self.assertNotEqual(finding["path"], "")
            self.assertNotIn("\\", finding["path"])
        self.assertTrue(any(finding["path"].startswith("validation/") for finding in findings))

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

    def test_workflow_invariants_are_sane(self):
        self.assertEqual(check_workflow_invariants(), [])

    def test_discovery_classification_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "README.md").write_text("# Project\n", encoding="utf-8")
            roles = classify_roles(project)
            by_role = {entry["role"]: entry for entry in roles}
            self.assertIn("project_entry", by_role)
            self.assertEqual(by_role["project_entry"]["status"], "CANDIDATE")

    def test_default_validation_is_read_only_for_sanitization_report(self):
        report_path = _public_sanitization_report_path(ROOT)
        original = report_path.read_text(encoding="utf-8")
        with patch.object(sys, "argv", ["validate_ynm.py"]):
            with patch("validation.validate_ynm.write_sanitization_report") as write_mock:
                validation_result = validator.main()
        self.assertEqual(validation_result, 0)
        write_mock.assert_not_called()
        self.assertEqual(report_path.read_text(encoding="utf-8"), original)

    def test_refresh_sanitization_flag_writes_report(self):
        with patch("validation.validate_ynm.run", return_value=[]):
            with patch.object(sys, "argv", ["validate_ynm.py", "--refresh-sanitization-report"]):
                with patch("validation.validate_ynm.generate_sanitization_report", wraps=validator.generate_sanitization_report) as generate_mock:
                    with patch("validation.validate_ynm.write_sanitization_report") as write_mock:
                        validator.main()
        generate_mock.assert_called_once_with(ROOT)
        write_mock.assert_called_once()
        called_with = write_mock.call_args.kwargs
        self.assertIn("dry_run", called_with)
        self.assertFalse(called_with["dry_run"])

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
        self.assertEqual(receipt["schema_version"], "ynm-run-receipt.v3")
        self.assertEqual(receipt["validity_boundary"]["reviewed_scope"], ["a"])
        self.assertEqual(receipt["validity_boundary"]["unreviewed_scope"], ["b"])

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

    def test_v3_receipt_requires_validity_boundary(self):
        lifecycle = InvocationLifecycle()
        lifecycle.deliver("EVIDENCE_LIMIT")
        fragment = lifecycle.lifecycle_receipt_fragment(
            unresolved_findings=["YNM-MAYBE-1"],
            reviewed_scope=["repository snapshot"],
            unreviewed_scope=["production"],
            persistence_authorized=False,
            propositions=["Reviewed behavior matches specification S"],
            evidence_snapshot="commit abc123",
            evidence_limitations=["production evidence unavailable"],
            executor_profile="example executor",
            execution_limits=["read-only repository access"],
            temporal_reference="2026-08-20",
        )
        receipt = load_yaml(ROOT / "examples/data/run-receipt.yaml")
        receipt.update(fragment)
        schema = load_json(ROOT / "schemas/run-receipt.schema.json")
        self.assertEqual(validate(receipt, schema), [])
        receipt.pop("validity_boundary")
        self.assertTrue(any("validity_boundary" in error for error in validate(receipt, schema)))


if __name__ == "__main__":
    unittest.main()
