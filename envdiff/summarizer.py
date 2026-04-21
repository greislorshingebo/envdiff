"""Summarizer: produce a concise statistics summary from a DiffResult or MultiDiffReport."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class EnvSummary:
    """Aggregated statistics for a single DiffResult."""
    label: str
    total_keys: int
    ok_count: int
    missing_in_compare: int
    missing_in_base: int
    mismatch_count: int

    @property
    def problem_count(self) -> int:
        return self.missing_in_compare + self.missing_in_base + self.mismatch_count

    @property
    def health_pct(self) -> float:
        """Percentage of keys that are OK (0-100)."""
        if self.total_keys == 0:
            return 100.0
        return round(self.ok_count / self.total_keys * 100, 1)

    def as_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "total_keys": self.total_keys,
            "ok": self.ok_count,
            "missing_in_compare": self.missing_in_compare,
            "missing_in_base": self.missing_in_base,
            "mismatch": self.mismatch_count,
            "problems": self.problem_count,
            "health_pct": self.health_pct,
        }


def summarize(result: DiffResult, label: str = "") -> EnvSummary:
    """Build an EnvSummary from a DiffResult."""
    ok = mismatch = missing_compare = missing_base = 0
    for entry in result.entries:
        status = entry.status
        if status == "ok":
            ok += 1
        elif status == "missing_in_compare":
            missing_compare += 1
        elif status == "missing_in_base":
            missing_base += 1
        elif status == "mismatch":
            mismatch += 1
    total = ok + mismatch + missing_compare + missing_base
    return EnvSummary(
        label=label,
        total_keys=total,
        ok_count=ok,
        missing_in_compare=missing_compare,
        missing_in_base=missing_base,
        mismatch_count=mismatch,
    )


def summarize_many(results: List[DiffResult], labels: List[str] | None = None) -> List[EnvSummary]:
    """Summarize a list of DiffResults, optionally with labels."""
    if labels is None:
        labels = [str(i) for i in range(len(results))]
    if len(labels) != len(results):
        raise ValueError("labels length must match results length")
    return [summarize(r, lbl) for r, lbl in zip(results, labels)]


def combined_report(summaries: List[EnvSummary]) -> str:
    """Return a human-readable combined summary table."""
    lines: List[str] = [
        f"{'Label':<20} {'Total':>6} {'OK':>6} {'Miss-C':>7} {'Miss-B':>7} {'Mismatch':>9} {'Health%':>8}",
        "-" * 70,
    ]
    for s in summaries:
        lines.append(
            f"{s.label:<20} {s.total_keys:>6} {s.ok_count:>6} "
            f"{s.missing_in_compare:>7} {s.missing_in_base:>7} "
            f"{s.mismatch_count:>9} {s.health_pct:>7}%"
        )
    return "\n".join(lines)
