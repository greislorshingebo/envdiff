"""CLI entry point for the env linter."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from envdiff.linter import lint_env


def build_lint_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-lint",
        description="Lint .env files for style and correctness issues.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to lint")
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="exit with code 1 if any issues are found",
    )
    p.add_argument(
        "--codes",
        metavar="CODES",
        help="comma-separated list of codes to report (e.g. E001,W001)",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_lint_parser()
    args = parser.parse_args(argv)

    filter_codes = (
        {c.strip() for c in args.codes.split(",")} if args.codes else None
    )

    any_issues = False
    for file in args.files:
        path = Path(file)
        if not path.exists():
            print(f"error: file not found: {file}", file=sys.stderr)
            sys.exit(2)

        result = lint_env(path)

        if filter_codes:
            result.issues = [i for i in result.issues if i.code in filter_codes]

        print(result.summary())
        if not result.is_clean:
            any_issues = True

    if args.exit_code and any_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
