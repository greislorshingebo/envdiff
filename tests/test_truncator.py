"""Tests for envdiff.truncator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pytest

from envdiff.truncator import (
    DEFAULT_MAX_LENGTH,
    TruncateOptions,
    _truncate_str,
    truncate_entry,
    truncate_result,
)


# ---------------------------------------------------------------------------
# Minimal stubs so we don't need the full comparator machinery
# ---------------------------------------------------------------------------

@dataclass
class _Entry:
    key: str
    status: str
    base_value: Optional[str] = None
    compare_value: Optional[str] = None


@dataclass
class _Result:
    entries: list


# ---------------------------------------------------------------------------
# _truncate_str
# ---------------------------------------------------------------------------

def test_short_value_unchanged():
    assert _truncate_str("hello", TruncateOptions(max_length=10)) == "hello"


def test_exact_length_unchanged():
    assert _truncate_str("hello", TruncateOptions(max_length=5)) == "hello"


def test_long_value_truncated():
    result = _truncate_str("abcdefghij", TruncateOptions(max_length=7))
    assert result == "abcd..."
    assert len(result) == 7


def test_none_value_returns_none():
    assert _truncate_str(None, TruncateOptions()) is None


def test_custom_placeholder():
    result = _truncate_str("abcdefgh", TruncateOptions(max_length=6, placeholder="--"))
    assert result == "abcd--"


def test_max_length_shorter_than_placeholder():
    # Edge case: keep at least 0 chars
    result = _truncate_str("hello", TruncateOptions(max_length=2, placeholder="..."))
    assert result == "..."


# ---------------------------------------------------------------------------
# truncate_entry
# ---------------------------------------------------------------------------

def test_entry_values_truncated():
    entry = _Entry(key="DB_URL", status="mismatch",
                   base_value="postgres://localhost/db",
                   compare_value="postgres://prod-host/db")
    opts = TruncateOptions(max_length=10)
    result = truncate_entry(entry, opts)
    assert len(result.base_value) <= 10
    assert len(result.compare_value) <= 10


def test_entry_key_and_status_preserved():
    entry = _Entry(key="SECRET", status="ok", base_value="x" * 50, compare_value=None)
    opts = TruncateOptions(max_length=20)
    result = truncate_entry(entry, opts)
    assert result.key == "SECRET"
    assert result.status == "ok"
    assert result.compare_value is None


# ---------------------------------------------------------------------------
# truncate_result
# ---------------------------------------------------------------------------

def test_truncate_result_all_entries():
    entries = [
        _Entry("A", "ok", "a" * 60, "a" * 60),
        _Entry("B", "missing", "b" * 80, None),
    ]
    result = _Result(entries=entries)
    truncated = truncate_result(result, max_length=20)  # type: ignore[arg-type]
    for entry in truncated.entries:
        if entry.base_value is not None:
            assert len(entry.base_value) <= 20
        if entry.compare_value is not None:
            assert len(entry.compare_value) <= 20


def test_truncate_result_original_unchanged():
    long_val = "x" * 100
    entries = [_Entry("K", "ok", long_val, long_val)]
    result = _Result(entries=entries)
    truncate_result(result, max_length=10)  # type: ignore[arg-type]
    # Original entries must not be mutated
    assert result.entries[0].base_value == long_val


def test_default_max_length_constant():
    assert DEFAULT_MAX_LENGTH == 40
