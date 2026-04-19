"""Redact sensitive values in env diffs before display or export."""

from __future__ import annotations

import re
from typing import Iterable

from envdiff.comparator import DiffResult, DiffEntry

_DEFAULT_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api_key|private_key|auth)", re.I),
]

REDACTED = "***REDACTED***"


def _is_sensitive(key: str, patterns: list[re.Pattern]) -> bool:
    return any(p.search(key) for p in patterns)


def redact_entry(entry: DiffEntry, patterns: list[re.Pattern]) -> DiffEntry:
    """Return a copy of *entry* with values masked if the key is sensitive."""
    if not _is_sensitive(entry.key, patterns):
        return entry
    return DiffEntry(
        key=entry.key,
        status=entry.status,
        base_value=REDACTED if entry.base_value is not None else None,
        compare_value=REDACTED if entry.compare_value is not None else None,
    )


def redact_result(
    result: DiffResult,
    extra_patterns: Iterable[str] | None = None,
) -> DiffResult:
    """Return a new DiffResult with sensitive values redacted."""
    patterns = list(_DEFAULT_PATTERNS)
    if extra_patterns:
        patterns.extend(re.compile(p, re.I) for p in extra_patterns)

    redacted_entries = [redact_entry(e, patterns) for e in result.entries]
    return DiffResult(entries=redacted_entries)
