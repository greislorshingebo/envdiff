"""CLI entry point for the classify command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.classifier import classify_env


def build_classify_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Classify env keys into semantic categories."
    if parent is not None:
        parser = parent.add_parser("classify", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-classify", description=description)

    parser.add_argument("file", help="Path to the .env file to classify.")
    parser.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    parser.add_argument(
        "--category",
        metavar="CATEGORY",
        default=None,
        help="Show only keys belonging to this category.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_classify_parser()
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    env = parse_env_file(path)
    result = classify_env(env)

    if args.category:
        keys = result.keys_for(args.category)
        if args.format == "json":
            print(json.dumps({args.category: keys}, indent=2))
        else:
            if keys:
                print(f"[{args.category}]")
                for k in keys:
                    print(f"  {k}")
            else:
                print(f"No keys found in category '{args.category}'.")
        return 0

    if args.format == "json":
        print(json.dumps(result.as_dict(), indent=2))
    else:
        for cat in result.categories():
            keys = result.keys_for(cat)
            print(f"[{cat}] ({len(keys)} key(s))")
            for k in keys:
                print(f"  {k}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
