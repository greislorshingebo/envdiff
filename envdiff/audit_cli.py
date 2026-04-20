"""CLI sub-command: envdiff audit — record a diff to an audit log."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.auditor import AuditLog, record_audit, save_audit_log, load_audit_log


def build_audit_parser(subparsers=None) -> argparse.ArgumentParser:
    desc = "Record a diff operation to a persistent audit log."
    if subparsers is not None:
        p = subparsers.add_parser("audit", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="envdiff audit", description=desc)
    p.add_argument("base", help="Base .env file")
    p.add_argument("compare", help="Comparison .env file")
    p.add_argument("--log", default="envdiff_audit.json",
                   help="Path to audit log file (default: envdiff_audit.json)")
    p.add_argument("--label", default=None, help="Optional label for this audit entry")
    p.add_argument("--show", action="store_true",
                   help="Print the full audit log after recording")
    p.add_argument("--no-check-values", dest="check_values",
                   action="store_false", default=True,
                   help="Ignore value mismatches")
    return p


def main(argv=None) -> int:
    parser = build_audit_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    compare_path = Path(args.compare)

    for p in (base_path, compare_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    compare_env = parse_env_file(compare_path)
    result = compare(base_env, compare_env, check_values=args.check_values)

    log_path = Path(args.log)
    if log_path.exists():
        log = load_audit_log(log_path)
    else:
        log = AuditLog()

    entry = record_audit(result, str(base_path), str(compare_path), label=args.label)
    log.add(entry)
    save_audit_log(log, log_path)

    status = "DIFF" if entry.has_differences else "OK"
    print(f"Recorded audit entry [{status}]: {entry.timestamp}")
    print(f"  keys={entry.total_keys}  missing_in_compare={entry.missing_in_compare}  "
          f"missing_in_base={entry.missing_in_base}  mismatched={entry.mismatched}")
    print(f"  log saved to: {log_path}")

    if args.show:
        print()
        print(log.summary())

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
