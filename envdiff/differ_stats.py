"""Aggregate statistics across a MultiDiffReport."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.differ import MultiDiffReport


@dataclass
class DiffStats:
    """Numeric summary of a MultiDiffReport."""

    total_pairs: int = 0
    total_keys_checked: int = 0
    missing_in_compare: int = 0
    missing_in_base: int = 0
    mismatched: int = 0
    ok: int = 0
    per_file: Dict[str, Dict[str, int]] = field(default_factory=dict)

    @property
    def total_problems(self) -> int:
        return self.missing_in_compare + self.missing_in_base + self.mismatched

    @property
    def problem_rate(self) -> float:
        if self.total_keys_checked == 0:
            return 0.0
        return round(self.total_problems / self.total_keys_checked, 4)

    def summary(self) -> str:
        return (
            f"pairs={self.total_pairs} "
            f"keys={self.total_keys_checked} "
            f"ok={self.ok} "
            f"missing_in_compare={self.missing_in_compare} "
            f"missing_in_base={self.missing_in_base} "
            f"mismatched={self.mismatched} "
            f"problem_rate={self.problem_rate:.2%}"
        )


def compute_stats(report: MultiDiffReport) -> DiffStats:
    """Compute aggregate statistics from a MultiDiffReport."""
    stats = DiffStats(total_pairs=len(report.results))

    for path, diff_result in report.results.items():
        file_counts: Dict[str, int] = {
            "ok": 0,
            "missing_in_compare": 0,
            "missing_in_base": 0,
            "mismatched": 0,
        }
        for entry in diff_result.entries:
            status = entry.status
            stats.total_keys_checked += 1
            if status == "ok":
                stats.ok += 1
                file_counts["ok"] += 1
            elif status == "missing_in_compare":
                stats.missing_in_compare += 1
                file_counts["missing_in_compare"] += 1
            elif status == "missing_in_base":
                stats.missing_in_base += 1
                file_counts["missing_in_base"] += 1
            elif status == "mismatched":
                stats.mismatched += 1
                file_counts["mismatched"] += 1
        stats.per_file[path] = file_counts

    return stats
