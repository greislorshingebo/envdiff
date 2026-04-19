"""Filtering utilities for DiffResult entries."""

from typing import List, Optional
from envdiff.comparator import DiffResult


def filter_by_status(
    result: DiffResult,
    statuses: List[str],
) -> DiffResult:
    """Return a new DiffResult containing only entries matching given statuses.

    Valid statuses: 'missing_in_compare', 'missing_in_base', 'mismatch', 'ok'
    """
    filtered = [e for e in result.entries if e["status"] in statuses]
    return DiffResult(entries=filtered)


def filter_by_key(
    result: DiffResult,
    pattern: str,
) -> DiffResult:
    """Return a new DiffResult containing only entries whose key contains pattern."""
    filtered = [e for e in result.entries if pattern.lower() in e["key"].lower()]
    return DiffResult(entries=filtered)


def filter_only_problems(result: DiffResult) -> DiffResult:
    """Convenience: keep only entries that represent a difference."""
    return filter_by_status(
        result,
        statuses=["missing_in_compare", "missing_in_base", "mismatch"],
    )


def apply_filters(
    result: DiffResult,
    statuses: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
    only_problems: bool = False,
) -> DiffResult:
    """Apply multiple filters in sequence."""
    if only_problems:
        result = filter_only_problems(result)
    if statuses:
        result = filter_by_status(result, statuses)
    if key_pattern:
        result = filter_by_key(result, key_pattern)
    return result
