import sys
import tempfile
import unittest
import subprocess
from pathlib import Path
import importlib.util

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

            self.assertEqual(first_sig, second_sig)

    def test_skills_ref_validate_references_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.build_skill_package.build_package(Path(tmp), ROOT / "manifest.yaml", overwrite=True)
            skill_manifest = (package / "manifest.yaml").read_text(encoding="utf-8")
            self.assertIn("name: ynm", skill_manifest)

    def test_cli_build_runs(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_skill_package.py"), "--output-dir", "dist-cli", "--overwrite"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
