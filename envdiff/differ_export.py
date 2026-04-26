"""Export multi-diff reports to dict, JSON, and CSV formats.

Provides serialisation helpers for MultiDiffReport so that CI pipelines
and downstream tooling can consume structured diff data without having to
parse human-readable text output.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from envdiff.differ import MultiDiffReport


# ---------------------------------------------------------------------------
# dict
# ---------------------------------------------------------------------------

def to_dict(report: MultiDiffReport) -> dict[str, Any]:
    """Serialise a MultiDiffReport to a plain Python dict.

    Structure::

        {
            "base": "path/to/base.env",
            "comparisons": [
                {
                    "compare": "path/to/other.env",
                    "has_differences": bool,
                    "entries": [
                        {
                            "key": str,
                            "status": str,
                            "base_value": str | None,
                            "compare_value": str | None,
                        },
                        ...
                    ]
                },
                ...
            ],
            "any_differences": bool
        }
    """
    comparisons: list[dict[str, Any]] = []

    for path, diff_result in zip(report.paths, report.diff_against_base):
        entries: list[dict[str, Any]] = []
        for entry in diff_result.entries:
            entries.append(
                {
                    "key": entry.key,
                    "status": entry.status,
                    "base_value": entry.base_value,
                    "compare_value": entry.compare_value,
                }
            )
        comparisons.append(
            {
                "compare": str(path),
                "has_differences": diff_result.has_differences,
                "entries": entries,
            }
        )

    return {
        "base": str(report.base),
        "comparisons": comparisons,
        "any_differences": report.any_differences,
    }


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def to_json(report: MultiDiffReport, *, indent: int = 2) -> str:
    """Return a JSON string representation of *report*."""
    return json.dumps(to_dict(report), indent=indent)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

_CSV_FIELDS = ["base", "compare", "key", "status", "base_value", "compare_value"]


def to_csv(report: MultiDiffReport) -> str:
    """Return a CSV string with one row per (compare-file, key) pair.

    Columns: base, compare, key, status, base_value, compare_value
    """
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_CSV_FIELDS, lineterminator="\n")
    writer.writeheader()

    base_str = str(report.base)
    for path, diff_result in zip(report.paths, report.diff_against_base):
        compare_str = str(path)
        for entry in diff_result.entries:
            writer.writerow(
                {
                    "base": base_str,
                    "compare": compare_str,
                    "key": entry.key,
                    "status": entry.status,
                    "base_value": entry.base_value if entry.base_value is not None else "",
                    "compare_value": entry.compare_value if entry.compare_value is not None else "",
                }
            )

    return buf.getvalue()
