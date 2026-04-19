"""Tests for envdiff.linter."""
import pytest
from pathlib import Path
from envdiff.linter import lint_env, LintResult


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_clean_file(env_dir):
    f = _write(env_dir / ".env", "APP_NAME=myapp\nDEBUG=true\n")
    result = lint_env(f)
    assert result.is_clean


def test_ignores_comments_and_blanks(env_dir):
    f = _write(env_dir / ".env", "# comment\n\nAPP=1\n")
    result = lint_env(f)
    assert result.is_clean


def test_no_equals_sign(env_dir):
    f = _write(env_dir / ".env", "BADLINE\n")
    result = lint_env(f)
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_empty_key(env_dir):
    f = _write(env_dir / ".env", "=value\n")
    result = lint_env(f)
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_lowercase_key_warning(env_dir):
    f = _write(env_dir / ".env", "myKey=value\n")
    result = lint_env(f)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_key_with_spaces(env_dir):
    f = _write(env_dir / ".env", "MY KEY=value\n")
    result = lint_env(f)
    codes = [i.code for i in result.issues]
    assert "E003" in codes


def test_duplicate_key(env_dir):
    f = _write(env_dir / ".env", "FOO=1\nFOO=2\n")
    result = lint_env(f)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_trailing_whitespace_in_value(env_dir):
    f = _write(env_dir / ".env", "FOO=bar   \n")
    result = lint_env(f)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_summary_clean(env_dir):
    f = _write(env_dir / ".env", "X=1\n")
    result = lint_env(f)
    assert "no issues" in result.summary()


def test_summary_with_issues(env_dir):
    f = _write(env_dir / ".env", "bad line\n")
    result = lint_env(f)
    summary = result.summary()
    assert "E001" in summary
    assert "1 issue" in summary
