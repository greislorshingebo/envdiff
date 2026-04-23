"""Tests for envdiff.multi_diff_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.multi_diff_cli import build_multi_diff_parser, main


@pytest.fixture()
def env_dir(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


def test_exits_zero_no_differences(env_dir):
    base = _write(env_dir, "base.env", "FOO=bar\nBAZ=qux\n")
    cmp = _write(env_dir, "cmp.env", "FOO=bar\nBAZ=qux\n")
    rc = main([str(base), str(cmp)])
    assert rc == 0


def test_exits_zero_without_exit_code_flag_even_when_diffs(env_dir):
    base = _write(env_dir, "base.env", "FOO=bar\nBAZ=qux\n")
    cmp = _write(env_dir, "cmp.env", "FOO=bar\n")
    rc = main([str(base), str(cmp)])
    assert rc == 0


def test_exits_one_with_exit_code_flag_when_diffs(env_dir):
    base = _write(env_dir, "base.env", "FOO=bar\nBAZ=qux\n")
    cmp = _write(env_dir, "cmp.env", "FOO=bar\n")
    rc = main([str(base), str(cmp), "--exit-code"])
    assert rc == 1


def test_exits_zero_with_exit_code_flag_no_diffs(env_dir):
    base = _write(env_dir, "base.env", "FOO=bar\n")
    cmp = _write(env_dir, "cmp.env", "FOO=bar\n")
    rc = main([str(base), str(cmp), "--exit-code"])
    assert rc == 0


def test_missing_base_returns_2(env_dir):
    cmp = _write(env_dir, "cmp.env", "FOO=bar\n")
    rc = main([str(env_dir / "ghost.env"), str(cmp)])
    assert rc == 2


def test_missing_compare_returns_2(env_dir):
    base = _write(env_dir, "base.env", "FOO=bar\n")
    rc = main([str(base), str(env_dir / "ghost.env")])
    assert rc == 2


def test_json_output_is_valid(env_dir, capsys):
    base = _write(env_dir, "base.env", "FOO=bar\nBAZ=qux\n")
    cmp = _write(env_dir, "cmp.env", "FOO=bar\n")
    main([str(base), str(cmp), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, dict)
    assert len(data) == 1


def test_json_output_has_differences_flag(env_dir, capsys):
    base = _write(env_dir, "base.env", "FOO=bar\nBAZ=qux\n")
    cmp = _write(env_dir, "cmp.env", "FOO=bar\n")
    main([str(base), str(cmp), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    first = next(iter(data.values()))
    assert first["has_differences"] is True


def test_multiple_compare_files(env_dir, capsys):
    base = _write(env_dir, "base.env", "A=1\nB=2\n")
    c1 = _write(env_dir, "c1.env", "A=1\nB=2\n")
    c2 = _write(env_dir, "c2.env", "A=1\n")
    main([str(base), str(c1), str(c2), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 2


def test_no_values_flag_ignores_mismatches(env_dir):
    base = _write(env_dir, "base.env", "FOO=bar\n")
    cmp = _write(env_dir, "cmp.env", "FOO=different\n")
    rc = main([str(base), str(cmp), "--exit-code", "--no-values"])
    assert rc == 0
