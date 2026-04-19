"""Tests for envdiff.formatter."""
import pytest
from envdiff.formatter import (
    format_key_status,
    format_section_header,
    format_summary_line,
)


def test_missing_in_compare():
    line = format_key_status("DB_HOST", "missing_in_compare")
    assert "DB_HOST" in line
    assert "only in base" in line
    assert line.startswith("  -")


def test_missing_in_base():
    line = format_key_status("SECRET_KEY", "missing_in_base")
    assert "SECRET_KEY" in line
    assert "only in compare" in line
    assert line.startswith("  +")


def test_mismatch_shows_both_values():
    line = format_key_status("PORT", "mismatch", base_value="5432", compare_value="3306")
    assert "PORT" in line
    assert '"5432"' in line
    assert '"3306"' in line
    assert line.startswith("  ~")


def test_ok_status():
    line = format_key_status("API_URL", "ok")
    assert "API_URL" in line
    assert "[ok]" in line


def test_section_header():
    header = format_section_header(".env.base", ".env.prod")
    assert ".env.base" in header
    assert ".env.prod" in header
    assert "<>" in header


def test_summary_no_differences():
    line = format_summary_line(0, 0, 0)
    assert "No differences" in line


def test_summary_with_issues():
    line = format_summary_line(2, 1, 3)
    assert "2 missing in compare" in line
    assert "1 missing in base" in line
    assert "3 mismatched" in line


def test_summary_partial():
    line = format_summary_line(0, 0, 1)
    assert "1 mismatched" in line
    assert "missing" not in line
