"""Tests for envdiff.inverter."""
from __future__ import annotations

import pytest

from envdiff.inverter import InvertResult, invert_env


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _invert(pairs: dict) -> InvertResult:
    return invert_env(pairs)


# ---------------------------------------------------------------------------
# basic inversion
# ---------------------------------------------------------------------------

def test_simple_inversion():
    result = _invert({"HOST": "localhost", "PORT": "5432"})
    assert result.inverted["localhost"] == "HOST"
    assert result.inverted["5432"] == "PORT"


def test_lookup_existing_value():
    result = _invert({"DB_NAME": "mydb"})
    assert result.lookup("mydb") == "DB_NAME"


def test_lookup_missing_value_returns_none():
    result = _invert({"KEY": "val"})
    assert result.lookup("not_there") is None


def test_empty_env_produces_empty_result():
    result = _invert({})
    assert result.inverted == {}
    assert result.collisions == {}
    assert not result.has_collisions


# ---------------------------------------------------------------------------
# None / missing values
# ---------------------------------------------------------------------------

def test_none_value_is_skipped():
    result = _invert({"KEY": None, "OTHER": "val"})
    assert None not in result.inverted
    assert "val" in result.inverted


def test_all_none_values_gives_empty_inverted():
    result = _invert({"A": None, "B": None})
    assert result.inverted == {}


# ---------------------------------------------------------------------------
# collision handling
# ---------------------------------------------------------------------------

def test_collision_detected():
    result = _invert({"A": "same", "B": "same"})
    assert result.has_collisions
    assert "same" in result.collisions
    assert set(result.collisions["same"]) == {"A", "B"}


def test_collision_last_write_wins():
    # dict ordering is preserved in Python 3.7+
    result = _invert({"FIRST": "dup", "SECOND": "dup"})
    assert result.inverted["dup"] == "SECOND"


def test_no_collision_when_values_differ():
    result = _invert({"X": "alpha", "Y": "beta"})
    assert not result.has_collisions
    assert result.collisions == {}


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_collisions():
    result = _invert({"A": "1", "B": "2"})
    s = result.summary()
    assert "2 unique" in s
    assert "no collisions" in s


def test_summary_with_collisions():
    result = _invert({"A": "v", "B": "v", "C": "other"})
    s = result.summary()
    assert "collision" in s
