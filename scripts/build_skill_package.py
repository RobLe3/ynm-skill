#!/usr/bin/env python3
"""Build a deterministic YNM skill package under a top-level `ynm` directory."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
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


def _normalize_candidate(candidate: str, manifest_root: Path, seen: set[str]) -> list[Path]:
    if ".." in candidate or candidate.startswith(("/", "\\")):
        raise PackageError(f"manifest path escapes repository: {candidate}")

    base = Path(candidate)
    if base.is_absolute():
        raise PackageError(f"absolute manifest path not allowed: {candidate}")

    source = (manifest_root / base).resolve()
    try:
        source.relative_to(manifest_root)
    except ValueError as exc:
        raise PackageError(f"manifest path outside repo: {candidate}") from exc

    if candidate in seen:
        return []
    seen.add(candidate)

    if not source.exists():
        raise PackageError(f"required manifest path not found: {candidate}")

    if source.is_file():
        return [source]
    return sorted(path for path in source.rglob("*") if path.is_file())


def collect_manifest_paths(manifest: dict[str, Any], root: Path) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for group in ["components", "optional_adapters", "packaging", "provenance", "validation", "runtime"]:
        group_value = manifest.get(group)
        if group_value is None:
            continue
        if isinstance(group_value, dict):
            candidates = [value for value in group_value.values()]
        elif isinstance(group_value, list):
            candidates = group_value
        else:
            continue
        for candidate in candidates:
            if isinstance(candidate, str):
                paths.extend(_normalize_candidate(candidate, root, seen))
            elif isinstance(candidate, list):
                for nested in candidate:
                    if isinstance(nested, str):
                        paths.extend(_normalize_candidate(nested, root, seen))
            else:
                raise PackageError(f"unsupported manifest path entry type: {candidate!r}")

    # Always include the manifest itself for reproducibility and discovery.
    manifest_file = root / "manifest.yaml"
    if manifest_file not in paths:
        paths.append(manifest_file)
    return paths


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

    entries = collect_manifest_paths(manifest, source_root)

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
