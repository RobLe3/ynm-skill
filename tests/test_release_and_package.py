import sys
import tempfile
import unittest
import subprocess
from pathlib import Path
import importlib.util
import os
import shutil
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.validate_release_integrity import validate_release_integrity  # noqa: E402


def _load_builder():
    path = ROOT / "scripts" / "build_skill_package.py"
    spec = importlib.util.spec_from_file_location("ynm_build_skill_package", path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError("build package loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseIntegrityTests(unittest.TestCase):
    def test_release_integrity_candidate_current_version(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        checks = validate_release_integrity(version, root=ROOT)
        self.assertFalse(checks.errors)
        self.assertIsInstance(checks, object)

    def test_release_integrity_default_uses_repo_version(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "validation/validate_release_integrity.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_release_integrity_flags_missing_directory(self):
        result = validate_release_integrity("9.9.9", root=ROOT)
        self.assertTrue(result.errors)

    def test_current_release_is_human_authorized_and_tag_ready(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        checks = validate_release_integrity(
            version,
            root=ROOT,
            require_tagged_subject=True,
            tag_ref=f"v{version}",
        )
        self.assertFalse(any("READY_FOR_TAG" in item for item in checks.errors))
        self.assertFalse(any("human publication authorization" in item for item in checks.errors))
        self.assertTrue(any("does not resolve to a commit" in item for item in checks.errors))

    def test_simulated_human_finalized_tag_subject_passes(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        with tempfile.TemporaryDirectory() as tmp:
            clone = Path(tmp) / "repo"
            subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone)], check=True)
            subprocess.run(["git", "-C", str(clone), "config", "user.name", "YNM Test"], check=True)
            subprocess.run(["git", "-C", str(clone), "config", "user.email", "ynm-test@example.invalid"], check=True)
            publication_path = clone / f"state/releases/{version}/publication.yaml"
            document = yaml.safe_load(publication_path.read_text(encoding="utf-8"))
            document["publication"]["status"] = "READY_FOR_TAG"
            document["publication"]["publication_readiness"] = "YES"
            document["publication"]["publication_authorization"] = "AUTHORIZED_BY_HUMAN"
            publication_path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            review_plan_path = clone / f"state/releases/{version}/review-plan.yaml"
            review_plan = yaml.safe_load(review_plan_path.read_text(encoding="utf-8"))
            review_plan["review_plan"]["persistence_mode"] = "PERSISTENT"
            review_plan_path.write_text(yaml.safe_dump(review_plan, sort_keys=False), encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(clone), "add", str(publication_path.relative_to(clone)), str(review_plan_path.relative_to(clone))],
                check=True,
            )
            subprocess.run(["git", "-C", str(clone), "commit", "--quiet", "-m", "test: finalize release"], check=True)
            subprocess.run(["git", "-C", str(clone), "tag", f"v{version}"], check=True)
            head = subprocess.run(
                ["git", "-C", str(clone), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
            ).stdout.strip()
            subprocess.run(["git", "-C", str(clone), "update-ref", "refs/remotes/origin/main", head], check=True)

            checks = validate_release_integrity(
                version,
                root=clone,
                require_tagged_subject=True,
                tag_ref=f"v{version}",
            )
            self.assertFalse(checks.errors, checks.errors)
            self.assertTrue(any("tagged subject:" in item for item in checks.info))

            wrong = validate_release_integrity(
                version,
                root=clone,
                require_tagged_subject=True,
                tag_ref="v9.9.9",
            )
            self.assertTrue(any("does not match expected" in item for item in wrong.errors))


class PackageBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_skill_package = _load_builder()

    def test_build_creates_ynm_directory_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.build_skill_package.build_package(
                Path(tmp),
                ROOT / "manifest.yaml",
                overwrite=True,
            )
            self.assertTrue((package / "manifest.yaml").exists())
            self.assertTrue((package / "SKILL.md").exists())

    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.build_skill_package.build_package(Path(tmp) / "first", ROOT / "manifest.yaml", overwrite=True)
            first_sig = self.build_skill_package.deterministic_signature(first)

            second = self.build_skill_package.build_package(Path(tmp) / "second", ROOT / "manifest.yaml", overwrite=True)
            second_sig = self.build_skill_package.deterministic_signature(second)

            first_inventory = sorted(
                f.relative_to(first).as_posix()
                for f in first.rglob("*")
                if f.is_file()
            )
            second_inventory = sorted(
                f.relative_to(second).as_posix()
                for f in second.rglob("*")
                if f.is_file()
            )
            self.assertEqual(first_inventory, second_inventory)

            for relative in first_inventory:
                self.assertEqual(
                    (first / relative).read_bytes(),
                    (second / relative).read_bytes(),
                )
            self.assertEqual(first_sig, second_sig)

    def test_skills_ref_validate_references_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.build_skill_package.build_package(Path(tmp), ROOT / "manifest.yaml", overwrite=True)
            skill_manifest = (package / "manifest.yaml").read_text(encoding="utf-8")
            self.assertIn("name: ynm", skill_manifest)


    def test_packaged_tree_excludes_development_and_historical_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.build_skill_package.build_package(Path(tmp), ROOT / "manifest.yaml", overwrite=True)
            forbidden_paths = [
                package / "AGENTS.md",
                package / ".github",
                package / "CHANGELOG.md",
                package / "CONTRIBUTING.md",
                package / "SECURITY.md",
                package / "VALIDATION.md",
                package / "VERSIONING.md",
                package / "build_skill_package.py",
                package / "state",
                package / "tests",
                package / "validation",
                package / "state/events.yaml",
                package / "state/runs.yaml",
                package / "state/maturity-assessment.yaml",
                package / "FORGE_EXTRACTION.md",
                package / "GENERALIZATION.md",
                package / "PUBLICATION_COMPARISON.md",
                package / "YNM_MATURITY_REPORT.md",
                package / "YNM_1_1_MATURITY_REPORT.md",
                package / "YNM_1_2_MATURITY_REPORT.md",
                package / "state/final-assessment.yaml",
            ]
            for item in forbidden_paths:
                self.assertFalse(item.exists(), f"forbidden item present in package: {item.relative_to(package)}")
            self.assertFalse((package / "evaluations").exists())
            self.assertFalse((package / "scripts/run_evaluations.py").exists())

    def test_cli_build_runs(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_skill_package.py"), "--output-dir", "dist-cli", "--overwrite"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)

    def test_manifest_include_rejects_platform_independent_escapes(self):
        for candidate in ["../escape", "/absolute", r"C:\escape", "C:/escape", r"\\server\share"]:
            with self.subTest(candidate=candidate):
                with self.assertRaises(self.build_skill_package.PackageError):
                    self.build_skill_package._validate_candidate_component(candidate, ROOT)

    @unittest.skipIf(os.name == "nt", "symlink creation policy differs on Windows test hosts")
    def test_manifest_rejects_external_symlink_file_and_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            outside = Path(tmp) / "outside"
            source.mkdir()
            outside.mkdir()
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            (source / "file-link").symlink_to(outside / "secret.txt")
            (source / "dir-link").symlink_to(outside, target_is_directory=True)
            for candidate in ["file-link", "dir-link"]:
                with self.subTest(candidate=candidate):
                    with self.assertRaises(self.build_skill_package.PackageError):
                        self.build_skill_package._normalize_candidate(candidate, source)

    def test_installed_package_is_self_contained_and_helpers_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            package = self.build_skill_package.build_package(skills_root, ROOT / "manifest.yaml", overwrite=True)
            self.assertEqual(package.name, "ynm")
            self.assertFalse((package / "state").exists())
            result = subprocess.run(
                [sys.executable, str(package / "scripts/project_integration.py"), "--help"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            spec = importlib.util.spec_from_file_location(
                "installed_execution_lifecycle", package / "scripts/execution_lifecycle.py"
            )
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)

    def test_package_markdown_links_are_local_or_external_and_resolve(self):
        from validation.validate_ynm import _check_markdown_links_for_root

        with tempfile.TemporaryDirectory() as tmp:
            package = self.build_skill_package.build_package(Path(tmp), ROOT / "manifest.yaml", overwrite=True)
            errors = []
            for path in package.rglob("*.md"):
                errors.extend(_check_markdown_links_for_root(path, expected_root=package))
            self.assertEqual(errors, [])

    def test_markdown_link_cannot_escape_expected_root(self):
        from validation.validate_ynm import _check_markdown_links_for_root

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_root = base / "package"
            expected_root.mkdir()
            outside = base / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            source = expected_root / "README.md"
            source.write_text("[escape](../outside.md)\n", encoding="utf-8")
            errors = _check_markdown_links_for_root(source, expected_root=expected_root)
            self.assertTrue(any("escapes expected root" in item for item in errors), errors)

    @unittest.skipIf(os.name == "nt", "directory symlinks require additional Windows privileges")
    def test_markdown_link_root_is_canonicalized_before_containment_check(self):
        from validation.validate_ynm import _check_markdown_links_for_root

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            package = base / "package"
            package.mkdir()
            (package / "target.md").write_text("target\n", encoding="utf-8")
            (package / "README.md").write_text("[target](target.md)\n", encoding="utf-8")
            alias = base / "package-alias"
            alias.symlink_to(package, target_is_directory=True)

            errors = _check_markdown_links_for_root(
                alias / "README.md",
                expected_root=alias,
            )
            self.assertEqual(errors, [])
