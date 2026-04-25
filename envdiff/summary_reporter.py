"""Plain-text and JSON reporters for MultiDiffSummary."""
from __future__ import annotations

import json
from typing import Literal

from envdiff.differ_summary import MultiDiffSummary


def report_summary_plain(summary: MultiDiffSummary) -> str:
    lines = [summary.summary(), ""]
    for entry in summary.entries:
        status = "OK" if entry.is_clean else "ISSUES"
        lines.append(f"  [{status}] {entry.path}")
        if not entry.is_clean:
            if entry.missing_in_compare:
                lines.append(f"         missing in compare : {entry.missing_in_compare}")
            if entry.missing_in_base:
                lines.append(f"         missing in base    : {entry.missing_in_base}")
            if entry.mismatched:
                lines.append(f"         mismatched values  : {entry.mismatched}")
    return "\n".join(lines)


def report_summary_json(summary: MultiDiffSummary) -> str:
    data = {
        "total_files": summary.total_files,
        "clean_files": summary.clean_files,
        "dirty_files": summary.dirty_files,
        "total_issues": summary.total_issues,
        "files": [
            {
                "path": e.path,
                "missing_in_compare": e.missing_in_compare,
                "missing_in_base": e.missing_in_base,
                "mismatched": e.mismatched,
                "total_issues": e.total_issues,
                "clean": e.is_clean,
            }
            for e in summary.entries
        ],
    }
    return json.dumps(data, indent=2)


def report_summary(
    summary: MultiDiffSummary,
    fmt: Literal["plain", "json"] = "plain",
) -> str:
    if fmt == "json":
        return report_summary_json(summary)
    return report_summary_plain(summary)
