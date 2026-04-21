"""CLI entry-point for the rename sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.renamer import rename_keys


def build_rename_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Rename one or more keys in an .env file and write the result."
    if parent is not None:
        parser = parent.add_parser("rename", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-rename", description=description)

    parser.add_argument("file", help="Path to the .env file to rename keys in.")
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        dest="renames",
        required=True,
        help="Rename rule in OLD_KEY=NEW_KEY format. May be repeated.",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Write result to FILE instead of stdout.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Allow renaming even if the new key already exists.",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )
    return parser


def _parse_rename_rules(raw: list[str]) -> dict[str, str]:
    rules: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            print(f"error: invalid rename rule {item!r} (expected OLD=NEW)", file=sys.stderr)
            sys.exit(2)
        old, _, new = item.partition("=")
        rules[old.strip()] = new.strip()
    return rules


def main(argv: list[str] | None = None) -> None:
    parser = build_rename_parser()
    args = parser.parse_args(argv)

    env = parse_env_file(Path(args.file))
    rename_map = _parse_rename_rules(args.renames)
    result = rename_keys(env, rename_map, overwrite=args.overwrite)

    lines = []
    for key, value in result.env.items():
        lines.append(f"{key}={value}" if value is not None else f"{key}=")

    output = "\n".join(lines) + ("\n" if lines else "")

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output, end="")

    if not args.quiet:
        print(result.summary(), file=sys.stderr)


if __name__ == "__main__":  # pragma: no cover
    main()
