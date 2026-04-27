"""CLI entry-point for the digest sub-command."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.digester import digest_files


def build_digest_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Compute SHA-256 digests of .env files and report whether they match."
    if parent is not None:
        parser = parent.add_parser("digest", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff digest", description=description)

    parser.add_argument("files", nargs="+", metavar="FILE", help=".env files to digest")
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when digests differ",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_digest_parser()
    args = parser.parse_args(argv)

    try:
        report = digest_files(*args.files)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        payload = {
            "all_match": report.all_match,
            "unique_digests": report.unique_digests,
            "entries": [{"path": e.path, "digest": e.digest} for e in report.entries],
        }
        print(json.dumps(payload, indent=2))
    else:
        for entry in report.entries:
            print(f"{entry.digest}  {entry.path}")
        print()
        print(report.summary())

    if args.exit_code and not report.all_match:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
