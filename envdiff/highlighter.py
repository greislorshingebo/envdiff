"""Highlight changed keys between two env snapshots or diffs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class HighlightedEntry:
    key: str
    base_value: Optional[str]
    compare_value: Optional[str]
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    highlight: bool = False


@dataclass
class HighlightResult:
    entries: List[HighlightedEntry] = field(default_factory=list)

    @property
    def highlighted(self) -> List[HighlightedEntry]:
        return [e for e in self.entries if e.highlight]

    @property
    def added(self) -> List[HighlightedEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[HighlightedEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[HighlightedEntry]:
        return [e for e in self.entries if e.status == "changed"]

    def summary(self) -> str:
        return (
            f"{len(self.added)} added, "
            f"{len(self.removed)} removed, "
            f"{len(self.changed)} changed"
        )


def highlight_diff(
    result: DiffResult,
    highlight_statuses: Optional[List[str]] = None,
) -> HighlightResult:
    """Convert a DiffResult into a HighlightResult, flagging notable entries."""
    if highlight_statuses is None:
        highlight_statuses = ["added", "removed", "changed"]

    entries: List[HighlightedEntry] = []
    for entry in result.entries:
        status_map = {
            "missing_in_compare": "removed",
            "missing_in_base": "added",
            "mismatch": "changed",
            "ok": "unchanged",
        }
        status = status_map.get(entry.status, "unchanged")
        highlighted = status in highlight_statuses
        entries.append(
            HighlightedEntry(
                key=entry.key,
                base_value=entry.base_value,
                compare_value=entry.compare_value,
                status=status,
                highlight=highlighted,
            )
        )
    return HighlightResult(entries=entries)


def highlight_report(result: HighlightResult, only_highlighted: bool = True) -> str:
    """Render a plain-text highlight report."""
    lines: List[str] = []
    source = result.highlighted if only_highlighted else result.entries
    for entry in source:
        marker = "*" if entry.highlight else " "
        base = entry.base_value if entry.base_value is not None else "<missing>"
        cmp = entry.compare_value if entry.compare_value is not None else "<missing>"
        if entry.status == "unchanged":
            lines.append(f"{marker} [{entry.status.upper():9}] {entry.key}")
        else:
            lines.append(
                f"{marker} [{entry.status.upper():9}] {entry.key}: {base!r} -> {cmp!r}"
            )
    if not lines:
        lines.append("(no highlighted entries)")
    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)
