"""CLI entry point for the envdiff watch sub-command."""

import argparse
import sys

from envdiff.watcher import FileWatcher
from envdiff.reporter import report


def _make_callback(fmt: str, check_values: bool):
    def _callback(path: str, result) -> None:
        if isinstance(result, Exception):
            print(f"[ERROR] {path}: {result}", file=sys.stderr)
            return
        print(f"\n--- Change detected in {path} ---")
        report(result, fmt=fmt)
    return _callback


def build_watch_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff watch",
        description="Watch .env files and print diffs on change.",
    )
    p.add_argument("base", help="Base .env file to compare against.")
    p.add_argument("targets", nargs="+", help="Target .env files to watch.")
    p.add_argument("--interval", type=float, default=1.0, help="Poll interval in seconds.")
    p.add_argument("--format", dest="fmt", choices=["plain", "rich"], default="plain")
    p.add_argument("--no-values", dest="check_values", action="store_false", default=True)
    return p


def main(argv=None) -> None:
    parser = build_watch_parser()
    args = parser.parse_args(argv)

    all_paths = [args.base] + args.targets
    callback = _make_callback(args.fmt, args.check_values)

    print(f"Watching {len(args.targets)} file(s) against base '{args.base}'. Press Ctrl+C to stop.")
    watcher = FileWatcher(all_paths, callback)
    try:
        watcher.start(args.base, interval=args.interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")
        sys.exit(0)


if __name__ == "__main__":
    main()
