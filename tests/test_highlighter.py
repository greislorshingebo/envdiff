"""Tests for envdiff.highlighter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from envdiff.highlighter import (
    HighlightedEntry,
    HighlightResult,
    highlight_diff,
    highlight_report,
)


# ---------------------------------------------------------------------------
# Minimal stubs so tests don't depend on comparator internals
# ---------------------------------------------------------------------------

@dataclass
class _Entry:
    key: str
    base_value: Optional[str]
    compare_value: Optional[str]
    status: str


@dataclass
class _Result:
    entries: List[_Entry] = field(default_factory=list)


def _make_result(*entries: _Entry) -> _Result:
    return _Result(entries=list(entries))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_added_entry_status():
    result = _make_result(_Entry("NEW_KEY", None, "value", "missing_in_base"))
    hr = highlight_diff(result)
    assert hr.entries[0].status == "added"


def test_removed_entry_status():
    result = _make_result(_Entry("OLD_KEY", "value", None, "missing_in_compare"))
    hr = highlight_diff(result)
    assert hr.entries[0].status == "removed"


def test_changed_entry_status():
    result = _make_result(_Entry("KEY", "old", "new", "mismatch"))
    hr = highlight_diff(result)
    assert hr.entries[0].status == "changed"


def test_ok_entry_status():
    result = _make_result(_Entry("KEY", "val", "val", "ok"))
    hr = highlight_diff(result)
    assert hr.entries[0].status == "unchanged"


def test_ok_entry_not_highlighted_by_default():
    result = _make_result(_Entry("KEY", "val", "val", "ok"))
    hr = highlight_diff(result)
    assert not hr.entries[0].highlight


def test_changed_entry_highlighted_by_default():
    result = _make_result(_Entry("KEY", "old", "new", "mismatch"))
    hr = highlight_diff(result)
    assert hr.entries[0].highlight


def test_custom_highlight_statuses():
    result = _make_result(
        _Entry("A", None, "v", "missing_in_base"),
        _Entry("B", "v", None, "missing_in_compare"),
    )
    hr = highlight_diff(result, highlight_statuses=["added"])
    highlighted_keys = {e.key for e in hr.highlighted}
    assert "A" in highlighted_keys
    assert "B" not in highlighted_keys


def test_highlight_result_properties():
    result = _make_result(
        _Entry("A", None, "v", "missing_in_base"),
        _Entry("B", "v", None, "missing_in_compare"),
        _Entry("C", "old", "new", "mismatch"),
        _Entry("D", "x", "x", "ok"),
    )
    hr = highlight_diff(result)
    assert len(hr.added) == 1
    assert len(hr.removed) == 1
    assert len(hr.changed) == 1


def test_summary_string():
    result = _make_result(
        _Entry("A", None, "v", "missing_in_base"),
        _Entry("B", "v", None, "missing_in_compare"),
        _Entry("C", "old", "new", "mismatch"),
    )
    hr = highlight_diff(result)
    summary = hr.summary()
    assert "1 added" in summary
    assert "1 removed" in summary
    assert "1 changed" in summary


def test_report_only_highlighted():
    result = _make_result(
        _Entry("CHANGED", "old", "new", "mismatch"),
        _Entry("SAME", "x", "x", "ok"),
    )
    hr = highlight_diff(result)
    report = highlight_report(hr, only_highlighted=True)
    assert "CHANGED" in report
    assert "SAME" not in report


def test_report_all_entries():
    result = _make_result(
        _Entry("CHANGED", "old", "new", "mismatch"),
        _Entry("SAME", "x", "x", "ok"),
    )
    hr = highlight_diff(result)
    report = highlight_report(hr, only_highlighted=False)
    assert "CHANGED" in report
    assert "SAME" in report


def test_report_no_highlights_message():
    result = _make_result(_Entry("KEY", "v", "v", "ok"))
    hr = highlight_diff(result)
    report = highlight_report(hr, only_highlighted=True)
    assert "no highlighted entries" in report
