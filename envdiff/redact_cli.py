"""CLI extension: --redact flag support wired into the main report pipeline."""

from __future__ import annotations

import argparse
from typing import Sequence

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.redactor import redact_result
from envdiff.reporter import report


def build_redact_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-redact",
        description="Compare .env files and redact sensitive values in output.",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("compare", help="Comparison .env file")
    p.add_argument(
        "--format",
        choices=["plain", "rich"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.add_argument(
        "--extra-redact",
        metavar="PATTERN",
        nargs="*",
        default=[],
        help="Additional regex patterns for keys to redact",
    )
    p.add_argument(
        "--no-redact",
        action="store_true",
        help="Disable redaction entirely",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_redact_parser()
    args = parser.parse_args(argv)

    base_env = parse_env_file(args.base)
    cmp_env = parse_env_file(args.compare)
    result = compare(base_env, cmp_env)

    if not args.no_redact:
        result = redact_result(result, extra_patterns=args.extra_redact or None)

    report(result, fmt=args.format)

    if args.exit_code and result.has_differences():
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
