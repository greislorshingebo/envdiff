"""Render a multi-environment diff report as plain text or JSON."""
from __future__ import annotations

import json
from typing import Literal

from envdiff.differ import MultiDiffReport
from envdiff.formatter import format_key_status, format_section_header, format_summary_line


OutputFormat = Literal["plain", "json"]


def _plain_block(label: str, result) -> list[str]:
    lines: list[str] = [format_section_header(label)]
    for entry in result.entries:
        lines.append("  " + format_key_status(entry))
    lines.append("  " + format_summary_line(result.summary()))
    return lines


def report_multi_plain(report: MultiDiffReport, *, show_all: bool = False) -> str:
    """Return a plain-text string for every base→compare pair in *report*."""
    blocks: list[str] = []
    for (base_path, cmp_path), result in report.results.items():
        if not show_all and not result.has_differences():
            label = f"{base_path} ↔ {cmp_path}  (no differences)"
            blocks.append(format_section_header(label))
        else:
            label = f"{base_path} ↔ {cmp_path}"
            blocks.extend(_plain_block(label, result))
    return "\n".join(blocks)


def report_multi_json(report: MultiDiffReport) -> str:
    """Return a JSON string summarising every pair in *report*."""
    data: dict = {}
    for (base_path, cmp_path), result in report.results.items():
        key = f"{base_path}::{cmp_path}"
        data[key] = {
            "has_differences": result.has_differences(),
            "summary": result.summary(),
            "entries": [
                {
                    "key": e.key,
                    "status": e.status,
                    "base_value": e.base_value,
                    "compare_value": e.compare_value,
                }
                for e in result.entries
            ],
        }
    return json.dumps(data, indent=2)


def report_multi(
    report: MultiDiffReport,
    fmt: OutputFormat = "plain",
    *,
    show_all: bool = False,
) -> str:
    """Dispatch to the correct renderer based on *fmt*."""
    if fmt == "json":
        return report_multi_json(report)
    return report_multi_plain(report, show_all=show_all)
