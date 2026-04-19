"""Tests for envdiff.sorter module."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.sorter import sort_by_key, sort_by_status, sort_entries


@pytest.fixture()
def unsorted_result() -> DiffResult:
    return DiffResult(
        entries=[
            {"key": "Z_VAR", "status": "ok", "base": "1", "compare": "1"},
            {"key": "A_VAR", "status": "mismatch", "base": "x", "compare": "y"},
            {"key": "M_VAR", "status": "missing_in_compare", "base": "v", "compare": None},
            {"key": "B_VAR", "status": "missing_in_base", "base": None, "compare": "w"},
        ]
    )


def test_sort_by_key_ascending(unsorted_result):
    result = sort_by_key(unsorted_result)
    keys = [e["key"] for e in result.entries]
    assert keys == ["A_VAR", "B_VAR", "M_VAR", "Z_VAR"]


def test_sort_by_key_descending(unsorted_result):
    result = sort_by_key(unsorted_result, reverse=True)
    keys = [e["key"] for e in result.entries]
    assert keys == ["Z_VAR", "M_VAR", "B_VAR", "A_VAR"]


def test_sort_by_status_order(unsorted_result):
    result = sort_by_status(unsorted_result)
    statuses = [e["status"] for e in result.entries]
    assert statuses[0] == "missing_in_compare"
    assert statuses[1] == "missing_in_base"
    assert statuses[2] == "mismatch"
    assert statuses[3] == "ok"


def test_sort_by_status_secondary_key():
    result = DiffResult(
        entries=[
            {"key": "Z_MISS", "status": "missing_in_compare", "base": "a", "compare": None},
            {"key": "A_MISS", "status": "missing_in_compare", "base": "b", "compare": None},
        ]
    )
    sorted_result = sort_by_status(result)
    assert sorted_result.entries[0]["key"] == "A_MISS"


def test_sort_entries_by_key(unsorted_result):
    result = sort_entries(unsorted_result, by="key")
    assert result.entries[0]["key"] == "A_VAR"


def test_sort_entries_by_status(unsorted_result):
    result = sort_entries(unsorted_result, by="status")
    assert result.entries[0]["status"] == "missing_in_compare"


def test_sort_entries_default_is_key(unsorted_result):
    result = sort_entries(unsorted_result)
    assert result.entries[0]["key"] == "A_VAR"


def test_sort_does_not_mutate_original(unsorted_result):
    original_first = unsorted_result.entries[0]["key"]
    sort_by_key(unsorted_result)
    assert unsorted_result.entries[0]["key"] == original_first
