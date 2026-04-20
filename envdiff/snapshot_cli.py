"""CLI entry-point for snapshot sub-commands: take, diff."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.snapshotter import diff_snapshot, load_snapshot, save_snapshot, take_snapshot


def build_snapshot_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-snapshot",
        description="Snapshot .env files and diff against saved snapshots.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- take ---
    take_p = sub.add_parser("take", help="Capture a snapshot of an .env file.")
    take_p.add_argument("env_file", help="Path to the .env file.")
    take_p.add_argument("-o", "--output", required=True, help="Where to write the snapshot JSON.")
    take_p.add_argument("--label", default=None, help="Human-readable label for the snapshot.")

    # --- diff ---
    diff_p = sub.add_parser("diff", help="Diff a snapshot against the current .env file.")
    diff_p.add_argument("snapshot", help="Path to the snapshot JSON file.")
    diff_p.add_argument("env_file", help="Path to the current .env file.")
    diff_p.add_argument(
        "--no-values",
        dest="check_values",
        action="store_false",
        default=True,
        help="Only compare keys, ignore value changes.",
    )
    diff_p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found.",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_snapshot_parser()
    args = parser.parse_args(argv)

    if args.command == "take":
        snap = take_snapshot(args.env_file, label=args.label)
        save_snapshot(snap, args.output)
        print(f"Snapshot saved to {args.output}  ({len(snap['keys'])} keys)")

    elif args.command == "diff":
        snap = load_snapshot(args.snapshot)
        result = diff_snapshot(snap, args.env_file, check_values=args.check_values)
        print(json.dumps(result, indent=2))
        if args.exit_code and result["has_differences"]:
            sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
