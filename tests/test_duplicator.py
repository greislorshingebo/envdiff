"""Tests for envdiff.duplicator."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.duplicator import DuplicateResult, find_duplicates


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content, encoding="utf-8")
    return p


def test_no_duplicates_clean_file(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "FOO=bar\nBAZ=qux\n")
    result = find_duplicates(p)
    assert not result.has_duplicates
    assert result.duplicate_keys == []


def test_single_duplicate_key(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "FOO=first\nFOO=second\n")
    result = find_duplicates(p)
    assert result.has_duplicates
    assert "FOO" in result.duplicate_keys
    assert len(result.duplicates["FOO"]) == 2


def test_multiple_duplicate_keys(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "A=1\nB=2\nA=3\nB=4\nC=5\n")
    result = find_duplicates(p)
    assert set(result.duplicate_keys) == {"A", "B"}
    assert "C" not in result.duplicates


def test_comments_and_blanks_ignored(env_dir: Path) -> None:
    content = "# comment\n\nFOO=bar\n# another\nFOO=baz\n"
    p = _write(env_dir, ".env", content)
    result = find_duplicates(p)
    assert result.has_duplicates
    assert result.duplicate_keys == ["FOO"]


def test_lines_without_equals_ignored(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "NOEQUALS\nFOO=bar\n")
    result = find_duplicates(p)
    assert not result.has_duplicates


def test_summary_no_duplicates(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "KEY=val\n")
    result = find_duplicates(p)
    assert "no duplicate" in result.summary()


def test_summary_with_duplicates(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "KEY=1\nKEY=2\n")
    result = find_duplicates(p)
    assert "KEY" in result.summary()
    assert "1 duplicate" in result.summary()


def test_result_path_matches_input(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "X=1\n")
    result = find_duplicates(p)
    assert result.path == p


def test_triplicate_recorded_three_times(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "K=a\nK=b\nK=c\n")
    result = find_duplicates(p)
    assert len(result.duplicates["K"]) == 3
