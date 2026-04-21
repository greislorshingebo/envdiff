"""Truncate long values in DiffResult entries for display purposes."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from envdiff.comparator import DiffResult

DEFAULT_MAX_LENGTH = 40
_ELLIPSIS = "..."


@dataclass(frozen=True)
class TruncateOptions:
    max_length: int = DEFAULT_MAX_LENGTH
    placeholder: str = _ELLIPSIS


def _truncate_str(value: Optional[str], opts: TruncateOptions) -> Optional[str]:
    """Return *value* truncated to *opts.max_length* characters."""
    if value is None:
        return None
    if len(value) <= opts.max_length:
        return value
    keep = max(0, opts.max_length - len(opts.placeholder))
    return value[:keep] + opts.placeholder


def truncate_entry(entry, opts: TruncateOptions) -> object:
    """Return a copy of *entry* with base_value / compare_value truncated."""
    return replace(
        entry,
        base_value=_truncate_str(entry.base_value, opts),
        compare_value=_truncate_str(entry.compare_value, opts),
    )


def truncate_result(
    result: DiffResult,
    max_length: int = DEFAULT_MAX_LENGTH,
    placeholder: str = _ELLIPSIS,
) -> DiffResult:
    """Return a new DiffResult whose entry values are truncated.

    Args:
        result: The original :class:`DiffResult`.
        max_length: Maximum number of characters to keep per value.
        placeholder: String appended when a value is cut short.

    Returns:
        A new :class:`DiffResult` with truncated entry values.
    """
    opts = TruncateOptions(max_length=max_length, placeholder=placeholder)
    truncated_entries = [truncate_entry(e, opts) for e in result.entries]
    return replace(result, entries=truncated_entries)
