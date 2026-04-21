"""Tests for envdiff.group_cli."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.group_cli import main


@pytest.fixture()
def env_dir(tmp_path: Path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_group_by_prefix_exits_zero(env_dir, capsys):
    base = _write(env_dir / ".env.base", "DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=prod\n")
    cmp = _write(env_dir / ".env.cmp", "DB_HOST=localhost\nDB_PORT=5433\nAPP_ENV=prod\n")
    rc = main([str(base), str(cmp), "--by", "prefix"])
    assert rc == 0


def test_group_by_status_exits_zero(env_dir, capsys):
    base = _write(env_dir / ".env.base", "KEY=val\n")
    cmp = _write(env_dir / ".env.cmp", "KEY=val\n")
    rc = main([str(base), str(cmp), "--by", "status"])
    assert rc == 0


def test_output_contains_group_label(env_dir, capsys):
    base = _write(env_dir / ".env.base", "DB_HOST=localhost\n")
    cmp = _write(env_dir / ".env.cmp", "DB_HOST=remotehost\n")
    main([str(base), str(cmp), "--by", "prefix"])
    out = capsys.readouterr().out
    assert "[DB]" in out


def test_no_values_flag_hides_values(env_dir, capsys):
    base = _write(env_dir / ".env.base", "SECRET_KEY=abc123\n")
    cmp = _write(env_dir / ".env.cmp", "SECRET_KEY=xyz789\n")
    main([str(base), str(cmp), "--no-values"])
    out = capsys.readouterr().out
    assert "abc123" not in out
    assert "xyz789" not in out


def test_missing_base_file_returns_2(env_dir):
    cmp = _write(env_dir / ".env.cmp", "KEY=val\n")
    rc = main([str(env_dir / "nonexistent"), str(cmp)])
    assert rc == 2


def test_missing_compare_file_returns_2(env_dir):
    base = _write(env_dir / ".env.base", "KEY=val\n")
    rc = main([str(base), str(env_dir / "nonexistent")])
    assert rc == 2


def test_custom_sep(env_dir, capsys):
    base = _write(env_dir / ".env.base", "DB-HOST=localhost\nDB-PORT=5432\n")
    cmp = _write(env_dir / ".env.cmp", "DB-HOST=localhost\nDB-PORT=5432\n")
    rc = main([str(base), str(cmp), "--by", "prefix", "--sep", "-"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[DB]" in out
