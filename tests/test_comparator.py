"""Tests for envdiff.comparator module."""
import pytest
from envdiff.comparator import compare_envs, DiffResult


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
COMPARE = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_missing_in_compare():
    result = compare_envs(BASE, COMPARE)
    assert "DEBUG" in result.missing_in_compare


def test_missing_in_base():
    result = compare_envs(BASE, COMPARE)
    assert "SECRET" in result.missing_in_base


def test_mismatched_values():
    result = compare_envs(BASE, COMPARE)
    assert "HOST" in result.mismatched
    assert result.mismatched["HOST"] == ("localhost", "prod.example.com")


def test_no_mismatch_when_check_values_false():
    result = compare_envs(BASE, COMPARE, check_values=False)
    assert result.mismatched == {}


def test_identical_envs_no_differences():
    result = compare_envs(BASE, BASE)
    assert not result.has_differences


def test_has_differences_true():
    result = compare_envs(BASE, COMPARE)
    assert result.has_differences


def test_summary_no_differences():
    result = compare_envs(BASE, BASE, base_file=".env", compare_file=".env.prod")
    assert "No differences found" in result.summary()


def test_summary_contains_missing_key():
    result = compare_envs(BASE, COMPARE, base_file=".env", compare_file=".env.prod")
    summary = result.summary()
    assert "DEBUG" in summary
    assert "SECRET" in summary
    assert "HOST" in summary


def test_port_not_in_mismatched():
    result = compare_envs(BASE, COMPARE)
    assert "PORT" not in result.mismatched


def test_file_labels_in_summary():
    result = compare_envs(BASE, COMPARE, base_file=".env", compare_file=".env.staging")
    summary = result.summary()
    assert ".env" in summary
    assert ".env.staging" in summary
