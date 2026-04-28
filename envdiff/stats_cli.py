"""CLI entry-point for the diff-stats command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.differ import diff_against_base
from envdiff.differ_stats import compute_stats


def build_stats_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-stats",
        description="Print aggregate statistics for .env file comparisons.",
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
        "--no-values",
        action="store_true",
        help="Ignore value mismatches; only report missing keys",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_stats_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    if not base_path.exists():
        print(f"error: base file not found: {base_path}", file=sys.stderr)
        return 2

    base_env = parse_env_file(base_path)
    results: dict = {}

    for cmp_path_str in args.compare:
        cmp_path = Path(cmp_path_str)
        if not cmp_path.exists():
            print(f"error: compare file not found: {cmp_path}", file=sys.stderr)
            return 2
        cmp_env = parse_env_file(cmp_path)
        diff = diff_against_base(
            base_env,
            cmp_env,
            check_values=not args.no_values,
        )
        results[cmp_path_str] = diff

    from envdiff.differ import MultiDiffReport
    report = MultiDiffReport(results=results)
    stats = compute_stats(report)

    if args.format == "json":
        data = {
            "total_pairs": stats.total_pairs,
            "total_keys_checked": stats.total_keys_checked,
            "ok": stats.ok,
            "missing_in_compare": stats.missing_in_compare,
            "missing_in_base": stats.missing_in_base,
            "mismatched": stats.mismatched,
            "total_problems": stats.total_problems,
            "problem_rate": stats.problem_rate,
            "per_file": stats.per_file,
        }
        print(json.dumps(data, indent=2))
    else:
        print(stats.summary())
        for path, counts in stats.per_file.items():
            parts = ", ".join(f"{k}={v}" for k, v in counts.items())
            print(f"  {path}: {parts}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
