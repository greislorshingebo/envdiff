"""Tests for envdiff.tag_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.tag_cli import main


@pytest.fixture()
def env_dir(tmp_path: Path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_exits_zero_basic(env_dir):
    base = _write(env_dir / ".env.base", "DB_HOST=localhost\nAPP_NAME=myapp\n")
    cmp = _write(env_dir / ".env.cmp", "DB_HOST=localhost\nAPP_NAME=myapp\n")
    rules = json.dumps({"DB_*": "database"})
    rc = main([str(base), str(cmp), "--rules", rules])
    assert rc == 0


def test_output_contains_tag(env_dir, capsys):
    base = _write(env_dir / ".env.base", "DB_HOST=localhost\n")
    cmp = _write(env_dir / ".env.cmp", "DB_HOST=remotehost\n")
    rules = json.dumps({"DB_*": "database"})
    main([str(base), str(cmp), "--rules", rules])
    out = capsys.readouterr().out
    assert "database" in out
    assert "DB_HOST" in out


def test_filter_by_tag(env_dir, capsys):
    base = _write(env_dir / ".env.base", "DB_HOST=localhost\nAPP_ENV=prod\n")
    cmp = _write(env_dir / ".env.cmp", "DB_HOST=localhost\nAPP_ENV=prod\n")
    rules = json.dumps({"DB_*": "database"})
    main([str(base), str(cmp), "--rules", rules, "--tag", "database"])
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "APP_ENV" not in out


def test_all_tags_flag(env_dir, capsys):
    base = _write(env_dir / ".env.base", "DB_HOST=localhost\nSECRET_KEY=abc\n")
    cmp = _write(env_dir / ".env.cmp", "DB_HOST=localhost\nSECRET_KEY=abc\n")
    rules = json.dumps({"DB_*": "database", "*KEY*": "secret"})
    rc = main([str(base), str(cmp), "--rules", rules, "--all-tags"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "database" in out
    assert "secret" in out


def test_invalid_rules_json_returns_2(env_dir):
    base = _write(env_dir / ".env.base", "KEY=val\n")
    cmp = _write(env_dir / ".env.cmp", "KEY=val\n")
    rc = main([str(base), str(cmp), "--rules", "not-json"])
    assert rc == 2


def test_no_tag_match_shows_dash(env_dir, capsys):
    base = _write(env_dir / ".env.base", "APP_NAME=myapp\n")
    cmp = _write(env_dir / ".env.cmp", "APP_NAME=myapp\n")
    rules = json.dumps({"DB_*": "database"})
    main([str(base), str(cmp), "--rules", rules])
    out = capsys.readouterr().out
    assert "APP_NAME" in out
    assert "[-]" in out
