"""Filter utilities for MultiDiffReport results.

Allows callers to narrow down a multi-file diff by status, key pattern,
or whether any differences exist — useful for large environment sets.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from envdiff.differ import MultiDiffReport
from envdiff.comparator import DiffResult
from envdiff.filter import filter_by_status, filter_by_key, filter_only_problems


@dataclass
class FilteredMultiReport:
    """Holds a subset of a MultiDiffReport after applying filters."""

    reports: List[DiffResult] = field(default_factory=list)

    # ---------- convenience helpers ----------

    @property
    def paths(self) -> List[str]:
        """Return the compare-file paths present in this filtered report."""
        return [r.compare_label for r in self.reports if r.compare_label]

    @property
    def any_differences(self) -> bool:
        """True if at least one contained report has differences."""
        from envdiff.comparator import has_differences

        return any(has_differences(r) for r in self.reports)

    def __len__(self) -> int:  # noqa: D105
        return len(self.reports)


# ---------------------------------------------------------------------------
# Per-report entry filters
# ---------------------------------------------------------------------------


def filter_report_by_status(
    report: DiffResult, statuses: Iterable[str]
) -> DiffResult:
    """Return a copy of *report* containing only entries matching *statuses*."""
    return filter_by_status(report, list(statuses))


def filter_report_by_key(
    report: DiffResult, pattern: str
) -> DiffResult:
    """Return a copy of *report* containing only entries whose key matches *pattern*.

    *pattern* supports Unix shell-style wildcards via :func:`fnmatch.fnmatch`.
    """
    return filter_by_key(report, pattern)


def filter_report_problems_only(report: DiffResult) -> DiffResult:
    """Return a copy of *report* with only non-OK entries."""
    return filter_only_problems(report)


# ---------------------------------------------------------------------------
# Multi-report filters
# ---------------------------------------------------------------------------


def filter_multi_by_status(
    multi: MultiDiffReport, statuses: Iterable[str]
) -> FilteredMultiReport:
    """Filter every report in *multi* to the given *statuses*."""
    status_list = list(statuses)
    filtered = [
        filter_by_status(r, status_list) for r in multi.reports
    ]
    return FilteredMultiReport(reports=filtered)


def filter_multi_by_key(
    multi: MultiDiffReport, pattern: str
) -> FilteredMultiReport:
    """Filter every report in *multi* to keys matching *pattern*."""
    filtered = [filter_by_key(r, pattern) for r in multi.reports]
    return FilteredMultiReport(reports=filtered)


def filter_multi_problems_only(
    multi: MultiDiffReport,
) -> FilteredMultiReport:
    """Keep only non-OK entries across all reports in *multi*."""
    filtered = [filter_only_problems(r) for r in multi.reports]
    return FilteredMultiReport(reports=filtered)


def filter_multi_with_differences(
    multi: MultiDiffReport,
) -> FilteredMultiReport:
    """Return only those reports that actually contain differences."""
    from envdiff.comparator import has_differences

    return FilteredMultiReport(
        reports=[r for r in multi.reports if has_differences(r)]
    )


def apply_multi_filters(
    multi: MultiDiffReport,
    *,
    statuses: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
    problems_only: bool = False,
    with_differences_only: bool = False,
) -> FilteredMultiReport:
    """Convenience wrapper that applies multiple filters in sequence.

    Parameters
    ----------
    multi:
        The source :class:`~envdiff.differ.MultiDiffReport` to filter.
    statuses:
        If provided, keep only entries whose status is in this list.
    key_pattern:
        If provided, keep only entries whose key matches this glob pattern.
    problems_only:
        If ``True``, drop all OK entries.
    with_differences_only:
        If ``True``, drop reports that have no differences at all.
    """
    result: MultiDiffReport | FilteredMultiReport = multi

    if with_differences_only:
        result = filter_multi_with_differences(result)  # type: ignore[arg-type]
        # Wrap back into a temporary MultiDiffReport-like for further filters
        _reports = result.reports
    else:
        _reports = list(multi.reports)

    from envdiff.comparator import has_differences as _hd  # local import avoids cycle

    # Build a throw-away MultiDiffReport for chained helpers
    class _Proxy:
        def __init__(self, reports):
            self.reports = reports

    proxy = _Proxy(_reports)

    if statuses:
        proxy = _Proxy(  # type: ignore[assignment]
            [filter_by_status(r, statuses) for r in proxy.reports]
        )
    if key_pattern:
        proxy = _Proxy(  # type: ignore[assignment]
            [filter_by_key(r, key_pattern) for r in proxy.reports]
        )
    if problems_only:
        proxy = _Proxy(  # type: ignore[assignment]
            [filter_only_problems(r) for r in proxy.reports]
        )

    return FilteredMultiReport(reports=proxy.reports)
