"""Integration tests for envdiff.summary_cli."""
from __future__ import annotations

import json
import os
import pytest

from envdiff.summary_cli import main


@pytest.fixture()
def env_dir(tmp_path):
    return tmp_path


def _write(directory, name, content):
    p = directory / name
    p.write_text(content)
    return str(p)


@pytest.fixture()
def base_file(env_dir):
    return _write(env_dir, "base.env", "A=1\nB=2\nC=3\n")


@pytest.fixture()
def identical_file(env_dir):
    return _write(env_dir, "identical.env", "A=1\nB=2\nC=3\n")


@pytest.fixture()
def diff_file(env_dir):
    return _write(env_dir, "diff.env", "A=1\nB=changed\n")


def test_exits_zero_no_differences(base_file, identical_file):
    assert main([base_file, identical_file]) == 0


def test_exits_zero_without_flag_even_when_diffs(base_file, diff_file):
    assert main([base_file, diff_file]) == 0


def test_exits_one_with_exit_code_flag_when_diffs(base_file, diff_file):
    assert main([base_file, diff_file, "--exit-code"]) == 1


def test_exits_zero_with_exit_code_flag_when_clean(base_file, identical_file):
    assert main([base_file, identical_file, "--exit-code"]) == 0


def test_missing_base_returns_2(env_dir, identical_file):
    assert main([str(env_dir / "ghost.env"), identical_file]) == 2


def test_missing_compare_returns_2(base_file, env_dir):
    assert main([base_file, str(env_dir / "ghost.env")]) == 2


def test_json_output_is_valid(base_file, diff_file, capsys):
    main([base_file, diff_file, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "files" in data
    assert data["total_files"] == 1
