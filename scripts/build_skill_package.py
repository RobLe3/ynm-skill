#!/usr/bin/env python3
"""Build a deterministic YNM skill package under a top-level `ynm` directory."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PackageError(Exception):
    """Raised when package assembly cannot be performed deterministically."""


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        raise PackageError(f"manifest not found: {manifest_path}")
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def _normalize_candidate(candidate: str, manifest_root: Path) -> Path:
    if not isinstance(candidate, str) or not candidate.strip():
        raise PackageError("manifest package include entries must be non-empty strings")

    candidate = candidate.strip()
    if candidate.startswith(("/", "\\")):
        raise PackageError(f"absolute manifest path not allowed: {candidate}")
    if ".." in Path(candidate).parts:
        raise PackageError(f"path traversal is not allowed: {candidate}")

    source = (manifest_root / candidate).resolve()
    try:
        source.relative_to(manifest_root)
    except ValueError as exc:
        raise PackageError(f"manifest path outside repository: {candidate}") from exc

    if not source.exists():
        raise PackageError(f"required manifest path not found: {candidate}")
    return source


def _collect_package_paths(manifest: dict[str, Any], root: Path) -> list[Path]:
    package = manifest.get("package", {})
    if not isinstance(package, dict):
        raise PackageError("manifest.package is required for package inclusion")

    includes = package.get("include")
    if not isinstance(includes, list) or not includes:
        raise PackageError("manifest.package.include must be a non-empty list")

    paths: list[Path] = []
    seen: set[Path] = set()
    for candidate in includes:
        if not isinstance(candidate, str):
            raise PackageError(f"manifest.package.include entry must be a string: {candidate!r}")
        source = _normalize_candidate(candidate, root)
        if source in seen:
            continue
        seen.add(source)

        if source.is_file():
            paths.append(source)
        else:
            for path in sorted(source.rglob("*")):
                if path.is_file():
                    paths.append(path)

    # Always include manifest itself if it is not already included.
    manifest_file = root / "manifest.yaml"
    if manifest_file not in seen:
        paths.append(manifest_file)
    return sorted(set(paths), key=lambda path: str(path))


def relative_posix(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def build_package(output_dir: Path, manifest_path: Path, *, overwrite: bool = False) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(manifest_path)
    source_root = manifest_path.parent
    package_root = output_dir / "ynm"

    if package_root.exists():
        if not overwrite:
            raise PackageError(f"package directory already exists: {package_root}")
        for item in sorted(package_root.iterdir(), reverse=True):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    package_root.mkdir(parents=True, exist_ok=True)

    entries = _collect_package_paths(manifest, source_root)

    copied: list[str] = []
    for source in entries:
        rel = source.relative_to(source_root)
        target = package_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(relative_posix(source, source_root))

    copy_report = {
        "manifest_version": manifest.get("version"),
        "name": manifest.get("name"),
        "copied_files": sorted(copied),
        "package_fields": sorted(relative_posix(path, source_root) for path in _collect_package_paths(manifest, source_root)),
    }
    (package_root / "package-manifest.yaml").write_text(
        yaml.safe_dump(copy_report, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )

    return package_root


def deterministic_signature(path: Path) -> str:
    hasher = hashlib.sha256()
    for file_path in sorted(path.rglob("*")):
        if file_path.is_file():
            relative = file_path.relative_to(path).as_posix()
            hasher.update(relative.encode("utf-8"))
            hasher.update(file_path.read_bytes())
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="dist", help="directory for package output")
    parser.add_argument("--manifest", default=str(ROOT / "manifest.yaml"), help="manifest path")
    parser.add_argument("--overwrite", action="store_true", help="allow overwriting existing package")
    args = parser.parse_args()

    try:
        package = build_package(Path(args.output_dir), Path(args.manifest), overwrite=args.overwrite)
    except PackageError as exc:
        print(f"YNM package build failed: {exc}")
        return 1

    signature = deterministic_signature(package)
    print(f"Built package at: {package}")
    print(f"Package signature: {signature}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
