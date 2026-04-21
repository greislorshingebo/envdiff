"""Render a GroupedResult as plain text or a rich table."""
from __future__ import annotations

from typing import Optional

from envdiff.grouper import GroupedResult

_STATUS_SYMBOL = {
    "ok": "✓",
    "mismatch": "≠",
    "missing_in_compare": "−",
    "missing_in_base": "+",
}


def report_grouped_plain(
    grouped: GroupedResult,
    *,
    show_values: bool = True,
) -> str:
    """Return a plain-text string representation of *grouped*."""
    lines: list[str] = []
    for label in grouped.labels():
        entries = grouped.get(label)
        lines.append(f"[{label}]  {len(entries)} key(s)")
        for entry in entries:
            symbol = _STATUS_SYMBOL.get(entry["status"], "?")
            key = entry["key"]
            if show_values:
                bv = entry.get("base_value") or ""
                cv = entry.get("compare_value") or ""
                lines.append(f"  {symbol} {key}  base={bv!r}  compare={cv!r}")
            else:
                lines.append(f"  {symbol} {key}  [{entry['status']}]")
        lines.append("")
    return "\n".join(lines)


def report_grouped_summary(grouped: GroupedResult) -> str:
    """Return a one-line-per-group summary."""
    lines: list[str] = []
    for label in grouped.labels():
        entries = grouped.get(label)
        status_counts: dict[str, int] = {}
        for e in entries:
            status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1
        parts = ", ".join(f"{s}={c}" for s, c in sorted(status_counts.items()))
        lines.append(f"{label}: {parts}")
    return "\n".join(lines)


def report_grouped(
    grouped: GroupedResult,
    *,
    fmt: str = "plain",
    show_values: bool = True,
) -> str:
    """Dispatch to the appropriate renderer."""
    if fmt == "summary":
        return report_grouped_summary(grouped)
    return report_grouped_plain(grouped, show_values=show_values)
