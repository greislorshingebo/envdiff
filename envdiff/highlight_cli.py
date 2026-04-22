"""CLI entry point for the highlight command."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.highlighter import highlight_diff, highlight_report


def build_highlight_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-highlight",
        description="Highlight added, removed, and changed keys between two .env files.",
    )
    parser.add_argument("base", help="Base .env file")
    parser.add_argument("compare", help="Compare .env file")
    parser.add_argument(
        "--all",
        action="store_true",
        dest="show_all",
        help="Show all keys, not just highlighted ones",
    )
    parser.add_argument(
        "--status",
        nargs="+",
        choices=["added", "removed", "changed", "unchanged"],
        default=["added", "removed", "changed"],
        metavar="STATUS",
        help="Statuses to highlight (default: added removed changed)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if any highlighted entries exist",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_highlight_parser()
    args = parser.parse_args(argv)

    try:
        base_env = parse_env_file(args.base)
        cmp_env = parse_env_file(args.compare)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    diff = compare(base_env, cmp_env)
    highlight = highlight_diff(diff, highlight_statuses=args.status)
    report = highlight_report(highlight, only_highlighted=not args.show_all)
    print(report)

    if args.exit_code and highlight.highlighted:
        sys.exit(1)


if __name__ == "__main__":
    main()
