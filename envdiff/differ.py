"""High-level differ: compare N env files pairwise against a base."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import compare, DiffResult
from envdiff.parser import parse_env_file


@dataclass
class MultiDiffReport:
    """Comparison of multiple env files against a single base."""

    base_path: str
    results: Dict[str, DiffResult] = field(default_factory=dict)

    def any_differences(self) -> bool:
        from envdiff.comparator import has_differences
        return any(has_differences(r) for r in self.results.values())

    def paths(self) -> List[str]:
        return list(self.results.keys())


def diff_against_base(
    base_path: str,
    compare_paths: List[str],
    check_values: bool = True,
) -> MultiDiffReport:
    """Parse *base_path* and compare every path in *compare_paths* against it."""
    base_env = parse_env_file(base_path)
    report = MultiDiffReport(base_path=base_path)
    for path in compare_paths:
        other_env = parse_env_file(path)
        report.results[path] = compare(base_env, other_env, check_values=check_values)
    return report


def diff_all_pairs(
    paths: List[str],
    check_values: bool = True,
) -> Dict[str, MultiDiffReport]:
    """Compare every file against every other file (all ordered pairs)."""
    reports: Dict[str, MultiDiffReport] = {}
    for i, base in enumerate(paths):
        others = [p for j, p in enumerate(paths) if j != i]
        reports[base] = diff_against_base(base, others, check_values=check_values)
    return reports
