"""Integration tests for the CLI entry point."""
import pytest
from pathlib import Path
from envdiff.cli import main


@pytest.fixture
def env_files(tmp_path):
    base = tmp_path / ".env"
    prod = tmp_path / ".env.prod"
    base.write_text("HOST=localhost\nPORT=5432\nDEBUG=true\n")
    prod.write_text("HOST=prod.example.com\nPORT=5432\nSECRET=abc\n")
    return base, prod


def test_cli_exits_zero_no_exit_code_flag(env_files, capsys):
    base, prod = env_files
    rc = main([str(base), str(prod)])
    assert rc == 0


def test_cli_exits_one_with_exit_code_flag(env_files):
    base, prod = env_files
    rc = main([str(base), str(prod), "--exit-code"])
    assert rc == 1


def test_cli_exits_zero_identical(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    rc = main([str(f), str(f), "--exit-code"])
    assert rc == 0


def test_cli_missing_file_returns_2(tmp_path):
    real = tmp_path / ".env"
    real.write_text("KEY=val\n")
    rc = main([str(real), str(tmp_path / "nonexistent")])
    assert rc == 2


def test_cli_plain_output_contains_key(env_files, capsys):
    base, prod = env_files
    main([str(base), str(prod)])
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "SECRET" in captured.out


def test_cli_no_values_flag(env_files, capsys):
    base, prod = env_files
    main([str(base), str(prod), "--no-values"])
    captured = capsys.readouterr()
    assert "HOST" not in captured.out or "mismatch" not in captured.out
