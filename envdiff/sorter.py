"""Sorting utilities for DiffResult entries."""

from envdiff.comparator import DiffResult

_STATUS_ORDER = {
    "missing_in_compare": 0,
    "missing_in_base": 1,
    "mismatch": 2,
    "ok": 3,
}


def sort_by_key(result: DiffResult, reverse: bool = False) -> DiffResult:
    """Return a new DiffResult sorted alphabetically by key."""
    sorted_entries = sorted(result.entries, key=lambda e: e["key"], reverse=reverse)
    return DiffResult(entries=sorted_entries)


def sort_by_status(result: DiffResult) -> DiffResult:
    """Return a new DiffResult sorted by status severity (problems first)."""
    sorted_entries = sorted(
        result.entries,
        key=lambda e: (_STATUS_ORDER.get(e["status"], 99), e["key"]),
    )
    return DiffResult(entries=sorted_entries)


def sort_entries(
    result: DiffResult,
    by: str = "key",
    reverse: bool = False,
) -> DiffResult:
    """Sort entries by 'key' or 'status'.

    Args:
        result: The DiffResult to sort.
        by: Sort field — 'key' or 'status'.
        reverse: Reverse the sort order (only applies to key sort).
    """
    if by == "status":
        return sort_by_status(result)
    return sort_by_key(result, reverse=reverse)
