"""Tests for envdiff.profiler."""
import pytest
from pathlib import Path

from envdiff.profiler import profile_env_file, _detect_type


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def test_total_keys(env_dir):
    path = _write(env_dir / ".env", "A=1\nB=2\nC=3\n")
    result = profile_env_file(path)
    assert result.total_keys == 3


def test_empty_value_keys(env_dir):
    path = _write(env_dir / ".env", "A=\nB=hello\n")
    result = profile_env_file(path)
    assert "A" in result.empty_value_keys
    assert "B" not in result.empty_value_keys


def test_duplicate_keys(env_dir):
    path = _write(env_dir / ".env", "A=1\nA=2\nB=3\n")
    result = profile_env_file(path)
    assert "A" in result.duplicate_keys
    assert "B" not in result.duplicate_keys


def test_no_issues_clean_file(env_dir):
    path = _write(env_dir / ".env", "HOST=localhost\nPORT=5432\n")
    result = profile_env_file(path)
    assert not result.has_issues


def test_has_issues_with_empty(env_dir):
    path = _write(env_dir / ".env", "SECRET=\n")
    result = profile_env_file(path)
    assert result.has_issues


def test_type_hints_bool(env_dir):
    path = _write(env_dir / ".env", "DEBUG=true\n")
    result = profile_env_file(path)
    assert result.type_hints["DEBUG"] == "bool"


def test_type_hints_int(env_dir):
    path = _write(env_dir / ".env", "PORT=8080\n")
    result = profile_env_file(path)
    assert result.type_hints["PORT"] == "int"


def test_type_hints_float(env_dir):
    path = _write(env_dir / ".env", "RATIO=0.5\n")
    result = profile_env_file(path)
    assert result.type_hints["RATIO"] == "float"


def test_type_hints_str(env_dir):
    path = _write(env_dir / ".env", "NAME=alice\n")
    result = profile_env_file(path)
    assert result.type_hints["NAME"] == "str"


def test_summary_contains_path(env_dir):
    path = _write(env_dir / ".env", "X=1\n")
    result = profile_env_file(path)
    assert path in result.summary()


def test_ignores_comments(env_dir):
    path = _write(env_dir / ".env", "# comment\nA=1\n")
    result = profile_env_file(path)
    assert result.total_keys == 1


@pytest.mark.parametrize("value,expected", [
    ("true", "bool"), ("False", "bool"),
    ("42", "int"), ("3.14", "float"), ("hello", "str"),
])
def test_detect_type(value, expected):
    assert _detect_type(value) == expected
