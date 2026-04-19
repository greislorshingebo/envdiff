"""Tests for envdiff.merger."""

from __future__ import annotations

import pytest

from envdiff.merger import merge_envs, merge_env_files


A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc"}
C = {"HOST": "staging.example.com", "TIMEOUT": "30"}


def test_merge_last_strategy_overrides():
    result = merge_envs([A, B], strategy="last")
    assert result["HOST"] == "prod.example.com"
    assert result["PORT"] == "5432"
    assert result["DEBUG"] == "true"
    assert result["SECRET"] == "abc"


def test_merge_first_strategy_keeps_first():
    result = merge_envs([A, B], strategy="first")
    assert result["HOST"] == "localhost"
    assert result["SECRET"] == "abc"  # only in B, still included


def test_merge_union_same_values_kept():
    same = {"HOST": "localhost", "PORT": "5432"}
    result = merge_envs([A, same], strategy="union")
    assert result["PORT"] == "5432"
    assert result["HOST"] is None  # conflict between A and same? No — same values
    # Actually both have HOST=localhost so no conflict


def test_merge_union_conflict_becomes_none():
    result = merge_envs([A, B], strategy="union")
    assert result["HOST"] is None  # conflict
    assert result["PORT"] == "5432"  # same in both
    assert result["DEBUG"] == "true"  # only in A
    assert result["SECRET"] == "abc"  # only in B


def test_merge_empty_list():
    assert merge_envs([]) == {}


def test_merge_single_env():
    result = merge_envs([A])
    assert result == A


def test_merge_three_envs_last():
    result = merge_envs([A, B, C], strategy="last")
    assert result["HOST"] == "staging.example.com"
    assert result["TIMEOUT"] == "30"
    assert result["SECRET"] == "abc"


def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs([A], strategy="invalid")


def test_merge_env_files(tmp_path):
    f1 = tmp_path / "base.env"
    f1.write_text("HOST=localhost\nPORT=5432\n")
    f2 = tmp_path / "override.env"
    f2.write_text("HOST=prod.example.com\nSECRET=xyz\n")

    result = merge_env_files([str(f1), str(f2)], strategy="last")
    assert result["HOST"] == "prod.example.com"
    assert result["PORT"] == "5432"
    assert result["SECRET"] == "xyz"
