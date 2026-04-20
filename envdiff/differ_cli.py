"""CLI entry point for multi-file diff comparisons using differ.py.

Allows users to compare multiple .env files against a base file or
perform all-pairs comparisons, outputting results in plain or rich format.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.differ import diff_against_base, diff_all_pairs, any_differences
from envdiff.parser import parse_env_file
from envdiff.reporter import report


def build_differ_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the differ CLI."""
    parser = argparse.ArgumentParser(
        prog="envdiff-multi",
        description="Compare multiple .env files and report differences.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare. The first file is the base.",
    )
    parser.add_argument(
        "--all-pairs",
        action="store_true",
        default=False,
        help="Compare every pair of files instead of each against the base.",
    )
    parser.add_argument(
        "--no-values",
        action="store_true",
        default=False,
        help="Only check for missing keys; ignore value mismatches.",
    )
    parser.add_argument(
        "--format",
        choices=["plain", "rich"],
        default="plain",
        help="Output format (default: plain).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any differences are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:  # noqa: D401
    """Entry point for the differ CLI.

    Returns the process exit code (0 = no differences, 1 = differences found,
    2 = usage / file error).
    """
    parser = build_differ_parser()
    args = parser.parse_args(argv)

    if len(args.files) < 2:
        parser.error("At least two .env files are required.")

    # Resolve and validate all paths up front.
    paths: list[Path] = []
    for raw in args.files:
        p = Path(raw)
        if not p.is_file():
            print(f"error: file not found: {raw}", file=sys.stderr)
            return 2
        paths.append(p)

    check_values = not args.no_values

    # Build the multi-diff report.
    if args.all_pairs:
        envs = {str(p): parse_env_file(p) for p in paths}
        report_obj = diff_all_pairs(envs, check_values=check_values)
    else:
        base_path = paths[0]
        compare_paths = paths[1:]
        base_env = parse_env_file(base_path)
        compare_envs = {str(p): parse_env_file(p) for p in compare_paths}
        report_obj = diff_against_base(
            base_env,
            compare_envs,
            base_label=str(base_path),
            check_values=check_values,
        )

    # Print a section for each pairwise diff result.
    found_differences = any_differences(report_obj)
    for label, diff_result in report_obj.results.items():
        print(f"\n=== {label} ===")
        report(diff_result, fmt=args.format)

    if args.exit_code and found_differences:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
