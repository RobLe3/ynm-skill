import os
import tempfile
import unittest
from pathlib import Path

from scripts import build_skill_package as builder
from validation.validate_ynm import _check_markdown_links_for_root


class PackageSecurityTests(unittest.TestCase):
    def test_manifest_paths_cannot_escape(self):
        for candidate in ["../escape", "/absolute", r"C:\escape", "C:/escape", r"\\server\share"]:
            with self.subTest(candidate=candidate):
                with self.assertRaises(builder.PackageError):
                    builder._validate_candidate_component(candidate, builder.ROOT)

    @unittest.skipIf(os.name == "nt", "symlink creation requires additional Windows privileges")
    def test_external_source_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            outside = Path(tmp) / "outside"
            source.mkdir()
            outside.mkdir()
            (outside / "secret").write_text("secret", encoding="utf-8")
            (source / "file-link").symlink_to(outside / "secret")
            (source / "dir-link").symlink_to(outside, target_is_directory=True)
            for candidate in ["file-link", "dir-link"]:
                with self.subTest(candidate=candidate):
                    with self.assertRaises(builder.PackageError):
                        builder._normalize_candidate(candidate, source)

    def test_built_package_has_contained_links_and_runtime_only_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = builder.build_package(Path(tmp), builder.ROOT / "manifest.yaml", overwrite=True)
            errors = []
            for path in package.rglob("*.md"):
                errors.extend(_check_markdown_links_for_root(path, expected_root=package))
            self.assertEqual(errors, [])
            for forbidden in ["state", "tests", "validation", ".github", "RELEASING.md"]:
                self.assertFalse((package / forbidden).exists())


if __name__ == "__main__":
    unittest.main()
