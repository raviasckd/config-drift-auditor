"""Tests for directory snapshots and drift classification."""

from pathlib import Path
import tempfile
import unittest

from config_drift.auditor import build_snapshot, compare_snapshot


class DriftAuditorTests(unittest.TestCase):
    def test_detects_added_removed_and_modified_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "keep.conf").write_text("one", encoding="utf-8")
            (root / "change.conf").write_text("before", encoding="utf-8")
            (root / "remove.conf").write_text("old", encoding="utf-8")
            baseline = build_snapshot(root)
            (root / "change.conf").write_text("after", encoding="utf-8")
            (root / "remove.conf").unlink()
            (root / "new.conf").write_text("new", encoding="utf-8")
            result = compare_snapshot(root, baseline)
        self.assertEqual(result["added"], ["new.conf"])
        self.assertEqual(result["removed"], ["remove.conf"])
        self.assertEqual(result["modified"], ["change.conf"])
        self.assertTrue(result["has_drift"])

    def test_unchanged_directory_has_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.ini").write_text("mode=production", encoding="utf-8")
            result = compare_snapshot(root, build_snapshot(root))
        self.assertFalse(result["has_drift"])
        self.assertEqual(result["unchanged"], 1)

    def test_rejects_unknown_baseline_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                compare_snapshot(directory, {
                    "format_version": 9, "algorithm": "sha256", "files": {}
                })


if __name__ == "__main__":
    unittest.main()
