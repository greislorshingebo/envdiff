"""Score an environment's health based on diff results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from envdiff.comparator import DiffResult


@dataclass
class ScoreResult:
    total: int
    ok: int
    missing_in_compare: int
    missing_in_base: int
    mismatched: int

    @property
    def score(self) -> float:
        """Return a 0.0-100.0 health score."""
        if self.total == 0:
            return 100.0
        return round((self.ok / self.total) * 100, 2)

    @property
    def grade(self) -> str:
        s = self.score
        if s == 100.0:
            return "A"
        if s >= 80.0:
            return "B"
        if s >= 60.0:
            return "C"
        if s >= 40.0:
            return "D"
        return "F"

    def summary(self) -> str:
        return (
            f"Score: {self.score}/100 ({self.grade}) — "
            f"{self.ok}/{self.total} keys OK, "
            f"{self.missing_in_compare} missing in compare, "
            f"{self.missing_in_base} missing in base, "
            f"{self.mismatched} mismatched"
        )


def score_result(result: DiffResult) -> ScoreResult:
    """Compute a ScoreResult from a DiffResult."""
    counts = {"ok": 0, "missing_in_compare": 0, "missing_in_base": 0, "mismatched": 0}
    for entry in result.entries:
        status = entry.status
        if status in counts:
            counts[status] += 1
        else:
            counts["ok"] += 1
    total = len(result.entries)
    return ScoreResult(
        total=total,
        ok=counts["ok"],
        missing_in_compare=counts["missing_in_compare"],
        missing_in_base=counts["missing_in_base"],
        mismatched=counts["mismatched"],
    )
