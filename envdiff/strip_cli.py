"""CLI entry point for the strip subcommand."""
from __future__ import annotations

import argparse
import sys

from envdiff.stripper import strip_env_file


def build_strip_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    description = "Strip empty or unwanted keys from a .env file."
    if parent is not None:
        parser = parent.add_parser("strip", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-strip", description=description)

    parser.add_argument("file", help="Path to the .env file to process.")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Explicit key names to remove.",
    )
    parser.add_argument(
        "--keep-empty",
        action="store_true",
        default=False,
        help="Do not strip keys with empty or blank values.",
    )
    parser.add_argument(
        "--keep-none",
        action="store_true",
        default=False,
        help="Do not strip keys with no value (bare keys).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any keys were removed.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_strip_parser()
    args = parser.parse_args(argv)

    try:
        result = strip_env_file(
            args.file,
            strip_none=not args.keep_none,
            strip_blank=not args.keep_empty,
            keys=args.keys,
        )
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    print(result.summary())

    if result.removed_keys:
        for key in sorted(result.removed_keys):
            print(f"  - {key}")

    if args.exit_code and result.remove_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
