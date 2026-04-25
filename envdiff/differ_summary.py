"""Aggregate summary statistics across a MultiDiffReport."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envdiff.differ import MultiDiffReport


@dataclass
class DiffSummaryEntry:
    path: str
    missing_in_compare: int
    missing_in_base: int
    mismatched: int
    total_issues: int

    @property
    def is_clean(self) -> bool:
        return self.total_issues == 0


@dataclass
class MultiDiffSummary:
    entries: List[DiffSummaryEntry]

    @property
    def total_files(self) -> int:
        return len(self.entries)

    @property
    def clean_files(self) -> int:
        return sum(1 for e in self.entries if e.is_clean)

    @property
    def dirty_files(self) -> int:
        return self.total_files - self.clean_files

    @property
    def total_issues(self) -> int:
        return sum(e.total_issues for e in self.entries)

    def summary(self) -> str:
        return (
            f"{self.total_files} file(s) compared: "
            f"{self.clean_files} clean, {self.dirty_files} with issues "
            f"({self.total_issues} total issue(s))"
        )


def summarize_multi_diff(report: MultiDiffReport) -> MultiDiffSummary:
    """Build a MultiDiffSummary from a MultiDiffReport."""
    entries: List[DiffSummaryEntry] = []
    for path, diff in zip(report.paths, report.diff_against_base()):
        mic = len(diff.missing_in_compare)
        mib = len(diff.missing_in_base)
        mm = len(diff.mismatched)
        entries.append(
            DiffSummaryEntry(
                path=path,
                missing_in_compare=mic,
                missing_in_base=mib,
                mismatched=mm,
                total_issues=mic + mib + mm,
            )
        )
    return MultiDiffSummary(entries=entries)
