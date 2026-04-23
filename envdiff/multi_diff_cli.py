"""CLI entry-point: compare one base .env file against multiple compare files."""
from __future__ import annotations

import argparse
import sys

from envdiff.differ import diff_against_base
from envdiff.differ_report import report_multi
from envdiff.parser import parse_env_file


def build_multi_diff_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-multi",
        description="Compare a base .env file against one or more compare files.",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("compare", nargs="+", help="One or more .env files to compare against base")
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        dest="fmt",
        help="Output format (default: plain)",
    )
    p.add_argument(
        "--show-all",
        action="store_true",
        help="Show pairs with no differences too",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if any differences are found",
    )
    p.add_argument(
        "--no-values",
        action="store_true",
        help="Ignore value mismatches; only flag missing keys",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_multi_diff_parser()
    args = parser.parse_args(argv)

    try:
        base_env = parse_env_file(args.base)
    except FileNotFoundError:
        print(f"error: base file not found: {args.base}", file=sys.stderr)
        return 2

    compare_envs: dict = {}
    for path in args.compare:
        try:
            compare_envs[path] = parse_env_file(path)
        except FileNotFoundError:
            print(f"error: compare file not found: {path}", file=sys.stderr)
            return 2

    check_values = not args.no_values
    report = diff_against_base(
        args.base, base_env, compare_envs, check_values=check_values
    )

    output = report_multi(report, fmt=args.fmt, show_all=args.show_all)
    print(output)

    if args.exit_code and report.any_differences():
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
