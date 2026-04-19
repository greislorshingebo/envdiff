"""Command-line interface for envdiff."""
import sys
import argparse
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.comparator import compare_envs
from envdiff.reporter import report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and flag missing or mismatched keys.",
    )
    p.add_argument("base", help="Base .env file path")
    p.add_argument("compare", help="Comparison .env file path")
    p.add_argument(
        "--no-values",
        action="store_true",
        default=False,
        help="Only check for missing keys; ignore value differences.",
    )
    p.add_argument(
        "--format",
        choices=["plain", "rich"],
        default="plain",
        dest="fmt",
        help="Output format (default: plain).",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found.",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    cmp_path = Path(args.compare)

    for p in (base_path, cmp_path):
        if not p.exists():
            print(f"envdiff: error: file not found: {p}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    cmp_env = parse_env_file(cmp_path)

    result = compare_envs(
        base_env,
        cmp_env,
        base_file=str(base_path),
        compare_file=str(cmp_path),
        check_values=not args.no_values,
    )

    report(result, fmt=args.fmt)

    if args.exit_code and result.has_differences:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
