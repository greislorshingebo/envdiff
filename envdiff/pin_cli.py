"""CLI entry-point for the pin / drift-check feature."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.pinner import check_drift_files, load_pin, save_pin, pin_env


def build_pin_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-pin",
        description="Pin .env values and detect drift from the pinned state.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # envdiff-pin capture <env_file> --output pin.json
    capture = sub.add_parser("capture", help="Capture current values as a pin file.")
    capture.add_argument("env_file", type=Path, help=".env file to pin.")
    capture.add_argument(
        "--output", "-o", type=Path, default=Path("pin.json"),
        help="Destination pin file (default: pin.json).",
    )

    # envdiff-pin check <pin_file> <env_file>
    check = sub.add_parser("check", help="Check an .env file for drift against a pin.")
    check.add_argument("pin_file", type=Path, help="Previously saved pin file.")
    check.add_argument("env_file", type=Path, help="Current .env file to check.")
    check.add_argument(
        "--exit-code", action="store_true",
        help="Exit with code 1 when drift is detected.",
    )
    check.add_argument(
        "--only-drifted", action="store_true",
        help="Print only keys that have drifted.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_pin_parser()
    args = parser.parse_args(argv)

    if args.command == "capture":
        if not args.env_file.exists():
            print(f"Error: {args.env_file} not found.", file=sys.stderr)
            return 2
        env = parse_env_file(args.env_file)
        pinned = pin_env(env)
        save_pin(pinned, args.output)
        print(f"Pinned {len(pinned)} keys to {args.output}")
        return 0

    # command == "check"
    for p in (args.pin_file, args.env_file):
        if not p.exists():
            print(f"Error: {p} not found.", file=sys.stderr)
            return 2

    report = check_drift_files(args.pin_file, args.env_file)

    entries = report.entries if not args.only_drifted else [
        e for e in report.entries if e.drifted
    ]
    for entry in entries:
        status = "DRIFT" if entry.drifted else "OK"
        print(f"  [{status}] {entry.key}  pinned={entry.pinned_value!r}  current={entry.current_value!r}")

    print(report.summary())
    if args.exit_code and report.has_drift:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
