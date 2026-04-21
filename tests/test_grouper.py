"""Tests for envdiff.grouper."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.grouper import (
    GroupedResult,
    group_by_custom,
    group_by_prefix,
    group_by_status,
)


@pytest.fixture()
def mixed_result() -> DiffResult:
    entries = [
        {"key": "DB_HOST", "status": "ok", "base_value": "localhost", "compare_value": "localhost"},
        {"key": "DB_PORT", "status": "mismatch", "base_value": "5432", "compare_value": "5433"},
        {"key": "APP_ENV", "status": "ok", "base_value": "prod", "compare_value": "prod"},
        {"key": "APP_DEBUG", "status": "missing_in_compare", "base_value": "true", "compare_value": None},
        {"key": "SECRET", "status": "missing_in_base", "base_value": None, "compare_value": "xyz"},
    ]
    return DiffResult(entries=entries)


def test_group_by_prefix_labels(mixed_result):
    grouped = group_by_prefix(mixed_result)
    assert set(grouped.labels()) == {"DB", "APP", "SECRET"}


def test_group_by_prefix_counts(mixed_result):
    grouped = group_by_prefix(mixed_result)
    assert len(grouped.get("DB")) == 2
    assert len(grouped.get("APP")) == 2
    assert len(grouped.get("SECRET")) == 1


def test_group_by_prefix_custom_sep(mixed_result):
    # Using '-' as separator — no key has '-', so each key is its own group
    grouped = group_by_prefix(mixed_result, sep="-")
    assert grouped.total() == len(mixed_result.entries)
    assert len(grouped.labels()) == len(mixed_result.entries)


def test_group_by_status_labels(mixed_result):
    grouped = group_by_status(mixed_result)
    assert set(grouped.labels()) == {"ok", "mismatch", "missing_in_compare", "missing_in_base"}


def test_group_by_status_ok_count(mixed_result):
    grouped = group_by_status(mixed_result)
    assert len(grouped.get("ok")) == 2


def test_group_by_status_mismatch_count(mixed_result):
    grouped = group_by_status(mixed_result)
    assert len(grouped.get("mismatch")) == 1


def test_group_by_custom(mixed_result):
    grouped = group_by_custom(mixed_result, lambda k: "long" if len(k) > 6 else "short")
    assert "long" in grouped.labels()
    assert "short" in grouped.labels()


def test_grouped_result_total(mixed_result):
    grouped = group_by_prefix(mixed_result)
    assert grouped.total() == len(mixed_result.entries)


def test_grouped_result_get_missing_label(mixed_result):
    grouped = group_by_prefix(mixed_result)
    assert grouped.get("NONEXISTENT") == []


def test_empty_result():
    result = DiffResult(entries=[])
    grouped = group_by_prefix(result)
    assert grouped.labels() == []
    assert grouped.total() == 0


def test_group_by_custom_all_same_label(mixed_result):
    """All entries mapped to the same label should produce a single group."""
    grouped = group_by_custom(mixed_result, lambda k: "all")
    assert grouped.labels() == ["all"]
    assert grouped.total() == len(mixed_result.entries)
    assert len(grouped.get("all")) == len(mixed_result.entries)


def test_group_by_status_missing_counts(mixed_result):
    """Verify counts for missing_in_compare and missing_in_base statuses."""
    grouped = group_by_status(mixed_result)
    assert len(grouped.get("missing_in_compare")) == 1
    assert len(grouped.get("missing_in_base")) == 1
