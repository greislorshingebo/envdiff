"""Tests for envdiff.differ_stats."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ import MultiDiffReport
from envdiff.differ_stats import DiffStats, compute_stats


def _make_entry(key: str, status: str):
    """Minimal stand-in for a DiffResult entry."""
    class _E:
        pass
    e = _E()
    e.key = key
    e.status = status
    return e


def _make_diff_result(*entries):
    class _DR:
        pass
    dr = _DR()
    dr.entries = list(entries)
    return dr


@pytest.fixture()
def simple_report():
    entries_a = [
        _make_entry("KEY1", "ok"),
        _make_entry("KEY2", "missing_in_compare"),
        _make_entry("KEY3", "mismatched"),
    ]
    entries_b = [
        _make_entry("KEY1", "ok"),
        _make_entry("KEY4", "missing_in_base"),
    ]
    return MultiDiffReport(
        results={
            "a.env": _make_diff_result(*entries_a),
            "b.env": _make_diff_result(*entries_b),
        }
    )


def test_total_pairs(simple_report):
    stats = compute_stats(simple_report)
    assert stats.total_pairs == 2


def test_total_keys_checked(simple_report):
    stats = compute_stats(simple_report)
    assert stats.total_keys_checked == 5


def test_ok_count(simple_report):
    stats = compute_stats(simple_report)
    assert stats.ok == 2


def test_missing_in_compare_count(simple_report):
    stats = compute_stats(simple_report)
    assert stats.missing_in_compare == 1


def test_missing_in_base_count(simple_report):
    stats = compute_stats(simple_report)
    assert stats.missing_in_base == 1


def test_mismatched_count(simple_report):
    stats = compute_stats(simple_report)
    assert stats.mismatched == 1


def test_total_problems(simple_report):
    stats = compute_stats(simple_report)
    assert stats.total_problems == 3


def test_problem_rate(simple_report):
    stats = compute_stats(simple_report)
    assert stats.problem_rate == round(3 / 5, 4)


def test_per_file_keys(simple_report):
    stats = compute_stats(simple_report)
    assert set(stats.per_file.keys()) == {"a.env", "b.env"}


def test_per_file_counts_a(simple_report):
    stats = compute_stats(simple_report)
    assert stats.per_file["a.env"]["ok"] == 1
    assert stats.per_file["a.env"]["missing_in_compare"] == 1
    assert stats.per_file["a.env"]["mismatched"] == 1


def test_empty_report_zero_stats():
    report = MultiDiffReport(results={})
    stats = compute_stats(report)
    assert stats.total_pairs == 0
    assert stats.total_keys_checked == 0
    assert stats.problem_rate == 0.0


def test_summary_string(simple_report):
    stats = compute_stats(simple_report)
    s = stats.summary()
    assert "pairs=2" in s
    assert "problem_rate=" in s
