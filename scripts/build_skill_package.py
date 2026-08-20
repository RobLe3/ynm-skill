#!/usr/bin/env python3
"""Build a deterministic YNM skill package under a top-level `ynm` directory."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PackageError(Exception):
    """Raised when package assembly cannot be performed deterministically."""


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        raise PackageError(f"manifest not found: {manifest_path}")
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def _is_control_or_empty(path: str) -> bool:
    if not path or path.strip() == "":
        return True
    return "\x00" in path or any(ord(ch) < 0x20 for ch in path if ch not in "\t\n\r")


def _contains_windows_drive(path: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", path))


def _contains_unc(path: str) -> bool:
    return path.startswith("\\\\") or path.startswith("//")


def _validate_candidate_component(candidate: str, candidate_root: Path) -> Path:
    candidate = candidate.strip()
    if _is_control_or_empty(candidate):
        raise PackageError("manifest package include entry cannot be empty")

    if candidate in {".", ".."}:
        raise PackageError(f"manifest package include cannot target root traversal target: {candidate}")

    if candidate.startswith(("/", "\\")):
        raise PackageError(f"absolute manifest path not allowed: {candidate}")

    if _contains_windows_drive(candidate):
        raise PackageError(f"windows drive path not allowed: {candidate}")

    if _contains_unc(candidate):
        raise PackageError(f"UNC path not allowed: {candidate}")

    if PureWindowsPath(candidate).is_absolute():
        raise PackageError(f"invalid windows-rooted manifest path: {candidate}")

    normalized = candidate.replace("\\", "/")
    if normalized.startswith("/"):
        raise PackageError(f"manifest path escapes repository root: {candidate}")

    parts = [part for part in normalized.split("/") if part]
    if not parts:
        raise PackageError(f"manifest path resolves to empty include: {candidate}")

    if any(part in {".", ".."} for part in parts):
        raise PackageError(f"path traversal is not allowed: {candidate}")

    path = candidate_root / Path(*parts)
    try:
        path.relative_to(candidate_root)
    except ValueError as exc:
        raise PackageError(f"manifest path escapes repository root: {candidate}") from exc

    if path.exists() and path.is_symlink():
        raise PackageError(f"manifest include path is a symlink: {candidate}")

    return path


def _component_is_forbidden(candidate_root: Path, target: Path) -> None:
    target_relative = target.relative_to(candidate_root)
    cursor = candidate_root
    for part in target_relative.parts:
        cursor = cursor / part
        if cursor.exists() and cursor.is_symlink():
            resolved = cursor.resolve()
            try:
                resolved.relative_to(candidate_root)
            except ValueError as exc:
                raise PackageError(
                    f"symlink component escapes repository root: {cursor.relative_to(candidate_root)}"
                ) from exc

    if target.exists() and target.is_symlink():
        resolved = target.resolve()
        try:
            resolved.relative_to(candidate_root)
        except ValueError as exc:
            raise PackageError(f"symlink target escapes repository root: {target.relative_to(candidate_root)}") from exc


def _ensure_recursive_path_safety(candidate_root: Path, source: Path) -> None:
    if source.is_dir():
        for path in source.rglob("*"):
            if path.is_symlink():
                raise PackageError(f"manifest includes symlinked path: {path.relative_to(candidate_root)}")
            if path.is_file():
                _component_is_forbidden(candidate_root, path)


def _normalize_candidate(candidate: str, manifest_root: Path) -> Path:
    source = _validate_candidate_component(candidate, manifest_root)
    try:
        source.relative_to(manifest_root)
    except ValueError as exc:
        raise PackageError(f"manifest path escapes repository root: {candidate}") from exc

    if source.is_file() or source.is_dir():
        _component_is_forbidden(manifest_root, source)
        if source.is_dir():
            _ensure_recursive_path_safety(manifest_root, source)
    else:
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
            continue

        for path in sorted(source.rglob("*")):
            if path.is_file():
                paths.append(path)

    # Always include manifest itself if it is not already included.
    manifest_file = root / "manifest.yaml"
    if manifest_file not in seen and manifest_file.exists():
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
        for item in sorted(package_root.rglob("*"), reverse=True):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    package_root.mkdir(parents=True, exist_ok=True)
    # macOS may expose temporary directories through both /var and /private/var.
    # Resolve the boundary once so containment comparisons use one representation.
    package_root = package_root.resolve()

    entries = _collect_package_paths(manifest, source_root)

    copied: list[str] = []
    for source in entries:
        rel = source.relative_to(source_root)
        target = package_root / rel
        target = target.resolve()
        try:
            target.relative_to(package_root)
        except ValueError as exc:
            raise PackageError(f"package target escapes root: {source}") from exc

        _component_is_forbidden(source_root, source)
        if target.exists() and target.is_symlink():
            raise PackageError(f"target path resolves to forbidden symlink: {target.relative_to(package_root)}")
        if target.parent.is_symlink():
            raise PackageError(f"package target parent escapes allowed path: {target.parent.relative_to(package_root)}")

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(relative_posix(source, source_root))

    copy_report = {
        "manifest_version": manifest.get("version"),
        "name": manifest.get("name"),
        "copied_files": sorted(copied),
        "package_fields": sorted(relative_posix(path, source_root) for path in entries),
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
