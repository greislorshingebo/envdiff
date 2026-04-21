"""Tests for envdiff.stripper."""
from __future__ import annotations

import pytest

from envdiff.stripper import StripResult, strip_empty, strip_env_file, strip_keys


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_dir(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


# ---------------------------------------------------------------------------
# strip_empty
# ---------------------------------------------------------------------------

def test_strip_empty_removes_none():
    env = {"A": "hello", "B": None, "C": "world"}
    result = strip_empty(env)
    assert "B" not in result.stripped
    assert result.removed_keys == ["B"]


def test_strip_empty_removes_blank_string():
    env = {"A": "ok", "B": "   ", "C": ""}
    result = strip_empty(env)
    assert "B" not in result.stripped
    assert "C" not in result.stripped
    assert set(result.removed_keys) == {"B", "C"}


def test_strip_empty_keeps_none_when_flag_off():
    env = {"A": None, "B": "value"}
    result = strip_empty(env, strip_none=False)
    assert "A" in result.stripped
    assert result.removed_keys == []


def test_strip_empty_keeps_blank_when_flag_off():
    env = {"A": "", "B": "value"}
    result = strip_empty(env, strip_blank=False)
    assert "A" in result.stripped
    assert result.removed_keys == []


def test_strip_empty_preserves_original():
    env = {"A": None, "B": "keep"}
    result = strip_empty(env)
    assert result.original == env
    assert result.original is not result.stripped


# ---------------------------------------------------------------------------
# strip_keys
# ---------------------------------------------------------------------------

def test_strip_keys_removes_listed():
    env = {"A": "1", "B": "2", "C": "3"}
    result = strip_keys(env, ["A", "C"])
    assert result.stripped == {"B": "2"}
    assert set(result.removed_keys) == {"A", "C"}


def test_strip_keys_ignores_missing():
    env = {"A": "1"}
    result = strip_keys(env, ["MISSING"])
    assert result.stripped == {"A": "1"}
    assert result.removed_keys == []


# ---------------------------------------------------------------------------
# StripResult helpers
# ---------------------------------------------------------------------------

def test_remove_count():
    result = StripResult(original={}, stripped={}, removed_keys=["X", "Y"])
    assert result.remove_count == 2


def test_summary_no_removal():
    result = StripResult(original={}, stripped={}, removed_keys=[])
    assert result.summary() == "No keys removed."


def test_summary_with_removals():
    result = StripResult(original={}, stripped={}, removed_keys=["FOO", "BAR"])
    assert "2" in result.summary()
    assert "BAR" in result.summary()


# ---------------------------------------------------------------------------
# strip_env_file
# ---------------------------------------------------------------------------

def test_strip_env_file_empty_values(env_dir):
    p = _write(env_dir / ".env", "A=hello\nB=\nC=world\n")
    result = strip_env_file(p)
    assert "B" not in result.stripped
    assert "A" in result.stripped


def test_strip_env_file_explicit_keys(env_dir):
    p = _write(env_dir / ".env", "A=1\nB=2\nC=3\n")
    result = strip_env_file(p, keys=["B"])
    assert "B" not in result.stripped
    assert result.removed_keys == ["B"]


def test_strip_env_file_not_found():
    with pytest.raises(FileNotFoundError):
        strip_env_file("/nonexistent/.env")
