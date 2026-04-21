"""Tests for envdiff.summarizer."""
from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import List

from envdiff.summarizer import summarize, summarize_many, combined_report, EnvSummary


# ---------------------------------------------------------------------------
# Minimal stubs so tests don't depend on full DiffResult internals
# ---------------------------------------------------------------------------

@dataclass
class _Entry:
    key: str
    status: str
    base_value: str | None = None
    compare_value: str | None = None


@dataclass
class _Result:
    entries: List[_Entry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_result():
    return _Result(entries=[
        _Entry("A", "ok"),
        _Entry("B", "ok"),
        _Entry("C", "mismatch"),
        _Entry("D", "missing_in_compare"),
        _Entry("E", "missing_in_base"),
    ])


@pytest.fixture()
def perfect_result():
    return _Result(entries=[
        _Entry("X", "ok"),
        _Entry("Y", "ok"),
    ])


@pytest.fixture()
def empty_result():
    return _Result(entries=[])


# ---------------------------------------------------------------------------
# Tests for summarize()
# ---------------------------------------------------------------------------

def test_total_keys(mixed_result):
    s = summarize(mixed_result, "staging")
    assert s.total_keys == 5


def test_ok_count(mixed_result):
    s = summarize(mixed_result)
    assert s.ok_count == 2


def test_mismatch_count(mixed_result):
    s = summarize(mixed_result)
    assert s.mismatch_count == 1


def test_missing_in_compare(mixed_result):
    s = summarize(mixed_result)
    assert s.missing_in_compare == 1


def test_missing_in_base(mixed_result):
    s = summarize(mixed_result)
    assert s.missing_in_base == 1


def test_problem_count(mixed_result):
    s = summarize(mixed_result)
    assert s.problem_count == 3


def test_health_pct_mixed(mixed_result):
    s = summarize(mixed_result)
    assert s.health_pct == 40.0


def test_health_pct_perfect(perfect_result):
    s = summarize(perfect_result)
    assert s.health_pct == 100.0


def test_health_pct_empty(empty_result):
    s = summarize(empty_result)
    assert s.health_pct == 100.0


def test_label_stored(mixed_result):
    s = summarize(mixed_result, label="prod")
    assert s.label == "prod"


def test_as_dict_keys(mixed_result):
    d = summarize(mixed_result, "env").as_dict()
    for key in ("label", "total_keys", "ok", "missing_in_compare", "missing_in_base", "mismatch", "problems", "health_pct"):
        assert key in d


# ---------------------------------------------------------------------------
# Tests for summarize_many()
# ---------------------------------------------------------------------------

def test_summarize_many_length(mixed_result, perfect_result):
    summaries = summarize_many([mixed_result, perfect_result], ["a", "b"])
    assert len(summaries) == 2


def test_summarize_many_labels(mixed_result, perfect_result):
    summaries = summarize_many([mixed_result, perfect_result], ["staging", "prod"])
    assert summaries[0].label == "staging"
    assert summaries[1].label == "prod"


def test_summarize_many_label_mismatch_raises(mixed_result):
    with pytest.raises(ValueError):
        summarize_many([mixed_result], ["a", "b"])


def test_summarize_many_auto_labels(mixed_result, perfect_result):
    summaries = summarize_many([mixed_result, perfect_result])
    assert summaries[0].label == "0"
    assert summaries[1].label == "1"


# ---------------------------------------------------------------------------
# Tests for combined_report()
# ---------------------------------------------------------------------------

def test_combined_report_contains_label(mixed_result):
    s = summarize(mixed_result, "staging")
    report = combined_report([s])
    assert "staging" in report


def test_combined_report_contains_header(mixed_result):
    s = summarize(mixed_result)
    report = combined_report([s])
    assert "Total" in report
    assert "Health%" in report


def test_combined_report_multiple_rows(mixed_result, perfect_result):
    summaries = summarize_many([mixed_result, perfect_result], ["env1", "env2"])
    report = combined_report(summaries)
    assert "env1" in report
    assert "env2" in report
