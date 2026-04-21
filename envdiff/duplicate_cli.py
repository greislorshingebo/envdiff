"""CLI entry-point for the duplicate-key detector."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.duplicator import find_duplicates


def build_duplicate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-duplicates",
        description="Detect duplicate keys inside .env files.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to inspect.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when duplicates are found.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-key output; only print the summary line.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_duplicate_parser()
    args = parser.parse_args(argv)

    any_found = False

    for file_arg in args.files:
        path = Path(file_arg)
        if not path.exists():
            print(f"error: {path} does not exist.", file=sys.stderr)
            sys.exit(2)

        result = find_duplicates(path)
        print(result.summary())

        if result.has_duplicates and not args.quiet:
            for key, lines in result.duplicates.items():
                print(f"  {key}:")
                for ln in lines:
                    print(f"    {ln}")

        if result.has_duplicates:
            any_found = True

    if args.exit_code and any_found:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
