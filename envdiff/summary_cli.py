"""CLI entry-point: envdiff-summary — aggregate diff summary across files."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.differ import MultiDiffReport
from envdiff.differ_summary import summarize_multi_diff
from envdiff.summary_reporter import report_summary


def build_summary_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-summary",
        description="Show an aggregate diff summary across multiple .env files.",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("compare", nargs="+", help="One or more .env files to compare")
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if any issues are found",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_summary_parser()
    args = parser.parse_args(argv)

    try:
        base_env = parse_env_file(args.base)
    except FileNotFoundError:
        print(f"error: base file not found: {args.base}", file=sys.stderr)
        return 2

    compare_envs = {}
    for path in args.compare:
        try:
            compare_envs[path] = parse_env_file(path)
        except FileNotFoundError:
            print(f"error: compare file not found: {path}", file=sys.stderr)
            return 2

    report_obj = MultiDiffReport(
        base=base_env,
        others=compare_envs,
    )
    summary = summarize_multi_diff(report_obj)
    print(report_summary(summary, fmt=args.format))

    if args.exit_code and summary.dirty_files > 0:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
