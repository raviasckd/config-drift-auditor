"""Create and compare SHA-256 snapshots of configuration directories."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scan(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    files: dict[str, str] = {}
    for current, directories, filenames in os.walk(root, followlinks=False):
        base = Path(current)
        directories[:] = sorted(name for name in directories if not (base / name).is_symlink())
        for filename in sorted(filenames):
            path = base / filename
            if path.is_symlink() or not path.is_file():
                continue
            files[path.relative_to(root).as_posix()] = _file_hash(path)
    return dict(sorted(files.items()))


def build_snapshot(root: str | Path) -> dict[str, Any]:
    """Return relative paths and SHA-256 hashes for regular files below root."""
    return {"format_version": 1, "algorithm": "sha256", "files": _scan(Path(root))}


def compare_snapshot(root: str | Path, baseline: dict[str, Any]) -> dict[str, Any]:
    """Classify added, removed, modified, and unchanged files."""
    if baseline.get("format_version") != 1 or baseline.get("algorithm") != "sha256":
        raise ValueError("unsupported baseline format or hash algorithm")
    expected = baseline.get("files")
    if not isinstance(expected, dict) or not all(
        isinstance(path, str) and isinstance(value, str) for path, value in expected.items()
    ):
        raise ValueError("baseline files must be a mapping of paths to hashes")

    actual = _scan(Path(root))
    expected_paths, actual_paths = set(expected), set(actual)
    added = sorted(actual_paths - expected_paths)
    removed = sorted(expected_paths - actual_paths)
    modified = sorted(
        path for path in expected_paths & actual_paths if expected[path] != actual[path]
    )
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": len(expected_paths & actual_paths) - len(modified),
        "has_drift": bool(added or removed or modified),
    }
