"""Tests for envdiff.differ_summary and envdiff.summary_reporter."""
from __future__ import annotations

import json
import pytest

from envdiff.differ import MultiDiffReport
from envdiff.differ_summary import DiffSummaryEntry, MultiDiffSummary, summarize_multi_diff
from envdiff.summary_reporter import report_summary_plain, report_summary_json, report_summary


@pytest.fixture()
def base_env():
    return {"A": "1", "B": "2", "C": "3"}


@pytest.fixture()
def compare_envs(base_env):
    return {
        "dev.env": {"A": "1", "B": "changed"},   # missing C, mismatch B
        "prod.env": {"A": "1", "B": "2", "C": "3"},  # identical
    }


@pytest.fixture()
def report(base_env, compare_envs):
    return MultiDiffReport(base=base_env, others=compare_envs)


@pytest.fixture()
def summary(report):
    return summarize_multi_diff(report)


def test_total_files(summary):
    assert summary.total_files == 2


def test_clean_files(summary):
    assert summary.clean_files == 1


def test_dirty_files(summary):
    assert summary.dirty_files == 1


def test_total_issues(summary):
    # dev.env: 1 missing_in_compare + 1 mismatch = 2
    assert summary.total_issues == 2


def test_summary_string_contains_counts(summary):
    s = summary.summary()
    assert "2 file(s)" in s
    assert "1 clean" in s
    assert "1 with issues" in s


def test_entry_is_clean_for_identical(summary):
    prod = next(e for e in summary.entries if e.path == "prod.env")
    assert prod.is_clean is True


def test_entry_issues_for_dev(summary):
    dev = next(e for e in summary.entries if e.path == "dev.env")
    assert dev.is_clean is False
    assert dev.missing_in_compare >= 1


def test_report_plain_contains_ok(summary):
    out = report_summary_plain(summary)
    assert "[OK]" in out
    assert "[ISSUES]" in out


def test_report_json_valid(summary):
    out = report_summary_json(summary)
    data = json.loads(out)
    assert "files" in data
    assert data["total_files"] == 2


def test_report_json_entry_fields(summary):
    data = json.loads(report_summary_json(summary))
    for entry in data["files"]:
        assert "path" in entry
        assert "total_issues" in entry
        assert "clean" in entry


def test_report_dispatch_plain(summary):
    assert report_summary(summary, fmt="plain") == report_summary_plain(summary)


def test_report_dispatch_json(summary):
    assert report_summary(summary, fmt="json") == report_summary_json(summary)
