"""CLI sub-command: envdiff group — display diff entries grouped by prefix or status."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare
from envdiff.grouper import group_by_prefix, group_by_status
from envdiff.parser import parse_env_file


def build_group_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Group diff entries by prefix or status.")
    if parent is not None:
        p = parent.add_parser("group", **kwargs)
    else:
        p = argparse.ArgumentParser(prog="envdiff-group", **kwargs)

    p.add_argument("base", help="Base .env file")
    p.add_argument("compare", help="Comparison .env file")
    p.add_argument(
        "--by",
        choices=["prefix", "status"],
        default="prefix",
        help="Grouping strategy (default: prefix)",
    )
    p.add_argument(
        "--sep",
        default="_",
        help="Key separator used for prefix grouping (default: _)",
    )
    p.add_argument(
        "--no-values",
        action="store_true",
        help="Hide values in output",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_group_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    cmp_path = Path(args.compare)

    for p in (base_path, cmp_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    cmp_env = parse_env_file(cmp_path)
    result = compare(base_env, cmp_env)

    grouped = (
        group_by_prefix(result, sep=args.sep)
        if args.by == "prefix"
        else group_by_status(result)
    )

    for label in grouped.labels():
        entries = grouped.get(label)
        print(f"[{label}]  ({len(entries)} key(s))")
        for entry in entries:
            key = entry["key"]
            status = entry["status"]
            if args.no_values:
                print(f"  {key}  [{status}]")
            else:
                base_val = entry.get("base_value", "")
                cmp_val = entry.get("compare_value", "")
                print(f"  {key}={base_val!r} -> {cmp_val!r}  [{status}]")
        print()

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
