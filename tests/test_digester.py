"""Tests for envdiff.digester and envdiff.digest_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.digester import DigestEntry, DigestReport, digest_file, digest_files, _hash_env
from envdiff.digest_cli import main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Unit tests: _hash_env
# ---------------------------------------------------------------------------

def test_hash_env_deterministic():
    env = {"A": "1", "B": "2"}
    assert _hash_env(env) == _hash_env(env)


def test_hash_env_order_independent():
    assert _hash_env({"A": "1", "B": "2"}) == _hash_env({"B": "2", "A": "1"})


def test_hash_env_different_values_differ():
    assert _hash_env({"A": "1"}) != _hash_env({"A": "2"})


def test_hash_env_none_value_stable():
    h = _hash_env({"KEY": None})
    assert isinstance(h, str) and len(h) == 64


# ---------------------------------------------------------------------------
# Unit tests: digest_file / digest_files
# ---------------------------------------------------------------------------

def test_digest_file_returns_entry(env_dir: Path):
    f = _write(env_dir, ".env", "FOO=bar\nBAZ=qux\n")
    entry = digest_file(f)
    assert isinstance(entry, DigestEntry)
    assert entry.path == str(f)
    assert len(entry.digest) == 64


def test_identical_content_same_digest(env_dir: Path):
    f1 = _write(env_dir, "a.env", "KEY=value\n")
    f2 = _write(env_dir, "b.env", "KEY=value\n")
    r = digest_files(f1, f2)
    assert r.all_match
    assert r.unique_digests == 1


def test_different_content_differs(env_dir: Path):
    f1 = _write(env_dir, "a.env", "KEY=value\n")
    f2 = _write(env_dir, "b.env", "KEY=other\n")
    r = digest_files(f1, f2)
    assert not r.all_match
    assert r.unique_digests == 2


def test_summary_all_match(env_dir: Path):
    f1 = _write(env_dir, "a.env", "X=1\n")
    f2 = _write(env_dir, "b.env", "X=1\n")
    r = digest_files(f1, f2)
    assert "identical" in r.summary()


def test_summary_differ(env_dir: Path):
    f1 = _write(env_dir, "a.env", "X=1\n")
    f2 = _write(env_dir, "b.env", "X=2\n")
    r = digest_files(f1, f2)
    assert "differ" in r.summary()


def test_empty_report_summary():
    r = DigestReport()
    assert "No files" in r.summary()


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_exits_zero_identical(env_dir: Path):
    f1 = _write(env_dir, "a.env", "KEY=val\n")
    f2 = _write(env_dir, "b.env", "KEY=val\n")
    assert main([str(f1), str(f2)]) == 0


def test_cli_exits_zero_without_flag_when_differ(env_dir: Path):
    f1 = _write(env_dir, "a.env", "KEY=val\n")
    f2 = _write(env_dir, "b.env", "KEY=other\n")
    assert main([str(f1), str(f2)]) == 0


def test_cli_exits_one_with_flag_when_differ(env_dir: Path):
    f1 = _write(env_dir, "a.env", "KEY=val\n")
    f2 = _write(env_dir, "b.env", "KEY=other\n")
    assert main(["--exit-code", str(f1), str(f2)]) == 1


def test_cli_json_output(env_dir: Path, capsys):
    f1 = _write(env_dir, "a.env", "KEY=val\n")
    f2 = _write(env_dir, "b.env", "KEY=val\n")
    main(["--json", str(f1), str(f2)])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["all_match"] is True
    assert len(data["entries"]) == 2


def test_cli_missing_file_returns_2(env_dir: Path):
    assert main([str(env_dir / "ghost.env")]) == 2
