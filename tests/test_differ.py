"""Tests for envdiff.differ."""

from __future__ import annotations

import pytest

from envdiff.differ import diff_against_base, diff_all_pairs, MultiDiffReport


@pytest.fixture()
def env_trio(tmp_path):
    base = tmp_path / "base.env"
    base.write_text("HOST=localhost\nPORT=5432\nDEBUG=true\n")

    prod = tmp_path / "prod.env"
    prod.write_text("HOST=prod.example.com\nPORT=5432\n")

    staging = tmp_path / "staging.env"
    staging.write_text("HOST=staging.example.com\nPORT=5432\nDEBUG=true\nTIMEOUT=30\n")

    return str(base), str(prod), str(staging)


def test_diff_against_base_returns_report(env_trio):
    base, prod, staging = env_trio
    report = diff_against_base(base, [prod, staging])
    assert isinstance(report, MultiDiffReport)
    assert report.base_path == base
    assert prod in report.paths()
    assert staging in report.paths()


def test_diff_against_base_detects_missing(env_trio):
    base, prod, staging = env_trio
    report = diff_against_base(base, [prod])
    result = report.results[prod]
    # DEBUG is in base but not in prod
    missing_keys = [e.key for e in result.entries if e.status == "missing_in_compare"]
    assert "DEBUG" in missing_keys


def test_diff_against_base_detects_extra(env_trio):
    base, prod, staging = env_trio
    report = diff_against_base(base, [staging])
    result = report.results[staging]
    extra_keys = [e.key for e in result.entries if e.status == "missing_in_base"]
    assert "TIMEOUT" in extra_keys


def test_any_differences_true(env_trio):
    base, prod, _ = env_trio
    report = diff_against_base(base, [prod])
    assert report.any_differences() is True


def test_any_differences_false(tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    content = "HOST=localhost\nPORT=5432\n"
    f1.write_text(content)
    f2.write_text(content)
    report = diff_against_base(str(f1), [str(f2)])
    assert report.any_differences() is False


def test_diff_all_pairs(env_trio):
    base, prod, staging = env_trio
    reports = diff_all_pairs([base, prod, staging])
    assert base in reports
    assert prod in reports
    assert staging in reports
    # base report should compare against prod and staging
    assert prod in reports[base].paths()
    assert staging in reports[base].paths()


def test_diff_all_pairs_no_self_compare(env_trio):
    base, prod, staging = env_trio
    reports = diff_all_pairs([base, prod, staging])
    assert base not in reports[base].paths()
