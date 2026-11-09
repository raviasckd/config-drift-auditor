"""CLI for creating and comparing configuration snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from config_drift.auditor import build_snapshot, compare_snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit configuration directory drift.")
    commands = parser.add_subparsers(dest="command", required=True)

    snapshot = commands.add_parser("snapshot", help="Create a baseline manifest")
    snapshot.add_argument("directory", type=Path)
    snapshot.add_argument("--output", type=Path, required=True)

    compare = commands.add_parser("compare", help="Compare a directory with a baseline")
    compare.add_argument("directory", type=Path)
    compare.add_argument("baseline", type=Path)
    compare.add_argument("--json", dest="json_path", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            report = build_snapshot(args.directory)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(f"Baseline written to {args.output} ({len(report['files'])} files)")
            return 0

        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        report = compare_snapshot(args.directory, baseline)
        rendered = json.dumps(report, indent=2)
        print(rendered)
        if args.json_path:
            args.json_path.write_text(rendered + "\n", encoding="utf-8")
        return 1 if report["has_drift"] else 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"config-drift: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
