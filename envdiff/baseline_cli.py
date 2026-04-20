"""CLI sub-commands for baseline management: capture, show, diff."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.baseline import (
    capture_baseline,
    diff_against_baseline,
    load_baseline,
    save_baseline,
)
from envdiff.reporter import report


def build_baseline_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff baseline",
        description="Manage a canonical .env baseline for drift detection.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # capture
    cap = sub.add_parser("capture", help="Save current .env as the baseline.")
    cap.add_argument("env_file", type=Path, help="Path to the .env file.")
    cap.add_argument("-o", "--output", type=Path, default=Path(".envdiff_baseline.json"))
    cap.add_argument("--label", default="baseline", help="Human-readable label.")

    # show
    shw = sub.add_parser("show", help="Print the saved baseline.")
    shw.add_argument("-b", "--baseline", type=Path, default=Path(".envdiff_baseline.json"))

    # diff
    dif = sub.add_parser("diff", help="Diff an env file against the saved baseline.")
    dif.add_argument("env_file", type=Path)
    dif.add_argument("-b", "--baseline", type=Path, default=Path(".envdiff_baseline.json"))
    dif.add_argument("--no-values", action="store_true", help="Skip value comparison.")
    dif.add_argument("--format", choices=["plain", "rich"], default="plain")
    dif.add_argument("--exit-code", action="store_true")

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_baseline_parser()
    args = parser.parse_args(argv)

    if args.command == "capture":
        bl = capture_baseline(args.env_file, label=args.label)
        save_baseline(bl, dest=args.output)
        print(f"Baseline '{bl.label}' saved to {args.output} ({len(bl.env)} keys).")

    elif args.command == "show":
        bl = load_baseline(args.baseline)
        print(f"Label   : {bl.label}")
        print(f"Created : {bl.created_at}")
        print(f"Keys    : {len(bl.env)}")
        for k, v in sorted(bl.env.items()):
            print(f"  {k}={v}")

    elif args.command == "diff":
        bl = load_baseline(args.baseline)
        result = diff_against_baseline(
            args.env_file, bl, check_values=not args.no_values
        )
        report(result, fmt=args.format)
        if args.exit_code and result.has_differences():
            sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
