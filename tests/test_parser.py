"""Tests for envdiff.parser."""

import textwrap
from pathlib import Path

import pytest

from envdiff.parser import parse_env_file


@pytest.fixture()
def env_file(tmp_path: Path):
    """Factory that writes content to a temp .env file and returns its path."""

    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p

    return _write


def test_basic_key_value(env_file):
    path = env_file("""
        APP_ENV=production
        PORT=8080
    """)
    result = parse_env_file(path)
    assert result == {"APP_ENV": "production", "PORT": "8080"}


def test_ignores_comments_and_blanks(env_file):
    path = env_file("""
        # This is a comment
        DEBUG=true

        # Another comment
        SECRET=abc123
    """)
    result = parse_env_file(path)
    assert result == {"DEBUG": "true", "SECRET": "abc123"}


def test_strips_double_quotes(env_file):
    path = env_file('DATABASE_URL="postgres://localhost/db"\n')
    result = parse_env_file(path)
    assert result["DATABASE_URL"] == "postgres://localhost/db"


def test_strips_single_quotes(env_file):
    path = env_file("API_KEY='my-secret-key'\n")
    result = parse_env_file(path)
    assert result["API_KEY"] == "my-secret-key"


def test_value_with_spaces(env_file):
    path = env_file("GREETING=hello world\n")
    result = parse_env_file(path)
    assert result["GREETING"] == "hello world"


def test_empty_value(env_file):
    path = env_file("EMPTY=\n")
    result = parse_env_file(path)
    assert result["EMPTY"] == ""


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "missing.env")


def test_malformed_lines_skipped(env_file):
    path = env_file("""
        VALID=yes
        this is not valid
        =nokey
    """)
    result = parse_env_file(path)
    assert result == {"VALID": "yes"}
