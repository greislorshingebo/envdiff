"""CLI entry point for scoring .env file health."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.scorer import score_result


def build_score_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-score",
        description="Score the health of a .env file against a base.",
    )
    p.add_argument("base", help="Base .env file (source of truth)")
    p.add_argument("compare", help=".env file to score")
    p.add_argument(
        "--no-values",
        action="store_true",
        default=False,
        help="Ignore value mismatches; only check key presence",
    )
    p.add_argument(
        "--min-score",
        type=float,
        default=None,
        metavar="SCORE",
        help="Exit with code 1 if score is below this threshold (0-100)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_score_parser()
    args = parser.parse_args(argv)

    try:
        base_env = parse_env_file(args.base)
    except FileNotFoundError:
        print(f"Error: base file not found: {args.base}", file=sys.stderr)
        return 2

    try:
        comp_env = parse_env_file(args.compare)
    except FileNotFoundError:
        print(f"Error: compare file not found: {args.compare}", file=sys.stderr)
        return 2

    check_values = not args.no_values
    result = compare(base_env, comp_env, check_values=check_values)
    sr = score_result(result)

    print(sr.summary())

    if args.min_score is not None and sr.score < args.min_score:
        print(
            f"Score {sr.score} is below minimum threshold {args.min_score}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
