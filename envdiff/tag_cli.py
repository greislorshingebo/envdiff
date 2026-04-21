"""CLI entry-point for the tagger feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_file
from envdiff.tagger import TagRule, tag_result


def build_tag_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    kwargs = dict(description="Tag diff entries by key patterns.")
    parser = (
        parent.add_parser("tag", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("base", help="Base .env file")
    parser.add_argument("compare", help="Compare .env file")
    parser.add_argument(
        "--rules",
        required=True,
        metavar="JSON",
        help='JSON object mapping glob patterns to tag labels, e.g. \'{"DB_*":"database"}\'',
    )
    parser.add_argument(
        "--tag",
        metavar="LABEL",
        help="Only show entries that carry this tag",
    )
    parser.add_argument(
        "--all-tags",
        action="store_true",
        help="Print all distinct tags found and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_tag_parser()
    args = parser.parse_args(argv)

    try:
        rules_map: dict = json.loads(args.rules)
    except json.JSONDecodeError as exc:
        print(f"error: --rules is not valid JSON: {exc}", file=sys.stderr)
        return 2

    base_env = parse_env_file(Path(args.base))
    cmp_env = parse_env_file(Path(args.compare))
    diff = compare_envs(base_env, cmp_env)
    rules = [TagRule(pattern=k, tag=v) for k, v in rules_map.items()]
    tagged = tag_result(diff, rules)

    if args.all_tags:
        for t in tagged.all_tags():
            print(t)
        return 0

    entries = tagged.by_tag(args.tag) if args.tag else tagged.entries
    for e in entries:
        tag_str = ",".join(e.tags) if e.tags else "-"
        print(f"{e.key}\t{e.status}\t[{tag_str}]")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
