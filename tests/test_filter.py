"""Tests for envdiff.filter module."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.filter import (
    filter_by_status,
    filter_by_key,
    filter_only_problems,
    apply_filters,
)


@pytest.fixture()
def mixed_result() -> DiffResult:
    return DiffResult(
        entries=[
            {"key": "DB_HOST", "status": "ok", "base": "localhost", "compare": "localhost"},
            {"key": "DB_PASS", "status": "mismatch", "base": "secret", "compare": "other"},
            {"key": "API_KEY", "status": "missing_in_compare", "base": "abc", "compare": None},
            {"key": "NEW_VAR", "status": "missing_in_base", "base": None, "compare": "xyz"},
            {"key": "LOG_LEVEL", "status": "ok", "base": "info", "compare": "info"},
        ]
    )


def test_filter_by_status_ok(mixed_result):
    result = filter_by_status(mixed_result, ["ok"])
    assert len(result.entries) == 2
    assert all(e["status"] == "ok" for e in result.entries)


def test_filter_by_status_multiple(mixed_result):
    result = filter_by_status(mixed_result, ["mismatch", "missing_in_compare"])
    assert len(result.entries) == 2


def test_filter_by_status_empty_match(mixed_result):
    result = filter_by_status(mixed_result, ["nonexistent"])
    assert result.entries == []


def test_filter_by_key_exact(mixed_result):
    result = filter_by_key(mixed_result, "DB")
    assert len(result.entries) == 2
    assert all("DB" in e["key"] for e in result.entries)


def test_filter_by_key_case_insensitive(mixed_result):
    result = filter_by_key(mixed_result, "db")
    assert len(result.entries) == 2


def test_filter_by_key_no_match(mixed_result):
    result = filter_by_key(mixed_result, "ZZZNOPE")
    assert result.entries == []


def test_filter_only_problems(mixed_result):
    result = filter_only_problems(mixed_result)
    assert len(result.entries) == 3
    assert all(e["status"] != "ok" for e in result.entries)


def test_apply_filters_only_problems(mixed_result):
    result = apply_filters(mixed_result, only_problems=True)
    assert len(result.entries) == 3


def test_apply_filters_combined(mixed_result):
    result = apply_filters(mixed_result, only_problems=True, key_pattern="DB")
    assert len(result.entries) == 1
    assert result.entries[0]["key"] == "DB_PASS"


def test_apply_filters_no_filters(mixed_result):
    result = apply_filters(mixed_result)
    assert len(result.entries) == 5
