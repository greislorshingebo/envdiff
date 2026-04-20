"""Tests for the differ CLI (multi-file diff against a base)."""

import json
import sys
from pathlib import Path

import pytest

from envdiff.differ_cli import build_differ_parser, main


@pytest.fixture()
def env_dir(tmp_path: Path):
    """Create a small set of .env files for CLI tests."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return tmp_path, _write


# ---------------------------------------------------------------------------
# build_differ_parser
# ---------------------------------------------------------------------------


def test_parser_requires_base(env_dir):
    """Calling the parser with no arguments should raise SystemExit."""
    parser = build_differ_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_accepts_base_and_compare(env_dir):
    tmp, _write = env_dir
    base = _write("base.env", "KEY=1\n")
    cmp1 = _write("cmp1.env", "KEY=1\n")
    parser = build_differ_parser()
    args = parser.parse_args([str(base), str(cmp1)])
    assert args.base == str(base)
    assert args.compare == [str(cmp1)]


def test_parser_accepts_multiple_compare_files(env_dir):
    tmp, _write = env_dir
    base = _write("base.env", "KEY=1\n")
    cmp1 = _write("c1.env", "KEY=1\n")
    cmp2 = _write("c2.env", "KEY=2\n")
    parser = build_differ_parser()
    args = parser.parse_args([str(base), str(cmp1), str(cmp2)])
    assert len(args.compare) == 2


# ---------------------------------------------------------------------------
# main — exit codes
# ---------------------------------------------------------------------------


def test_main_exits_zero_no_differences(env_dir, capsys):
    """Identical envs should exit 0 by default."""
    tmp, _write = env_dir
    base = _write("base.env", "KEY=value\n")
    cmp = _write("cmp.env", "KEY=value\n")
    sys.argv = ["envdiff-differ", str(base), str(cmp)]
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_main_exits_zero_with_differences_no_flag(env_dir, capsys):
    """Without --exit-code flag, differences should still exit 0."""
    tmp, _write = env_dir
    base = _write("base.env", "KEY=a\n")
    cmp = _write("cmp.env", "KEY=b\n")
    sys.argv = ["envdiff-differ", str(base), str(cmp)]
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_main_exits_one_with_differences_and_flag(env_dir, capsys):
    """With --exit-code, any differences should cause exit 1."""
    tmp, _write = env_dir
    base = _write("base.env", "KEY=a\nONLY_BASE=x\n")
    cmp = _write("cmp.env", "KEY=b\n")
    sys.argv = ["envdiff-differ", "--exit-code", str(base), str(cmp)]
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_main_exits_zero_identical_with_flag(env_dir, capsys):
    """With --exit-code but no differences, exit code should be 0."""
    tmp, _write = env_dir
    base = _write("base.env", "KEY=same\n")
    cmp = _write("cmp.env", "KEY=same\n")
    sys.argv = ["envdiff-differ", "--exit-code", str(base), str(cmp)]
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


# ---------------------------------------------------------------------------
# main — output format
# ---------------------------------------------------------------------------


def test_main_json_output(env_dir, capsys):
    """--format json should produce valid JSON on stdout."""
    tmp, _write = env_dir
    base = _write("base.env", "KEY=a\n")
    cmp = _write("cmp.env", "KEY=b\n")
    sys.argv = ["envdiff-differ", "--format", "json", str(base), str(cmp)]
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, (dict, list))


def test_main_plain_output_contains_key(env_dir, capsys):
    """Plain output should mention the differing key."""
    tmp, _write = env_dir
    base = _write("base.env", "MISSING_KEY=val\n")
    cmp = _write("cmp.env", "OTHER=val\n")
    sys.argv = ["envdiff-differ", "--format", "plain", str(base), str(cmp)]
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "MISSING_KEY" in captured.out or "OTHER" in captured.out


def test_main_missing_file_exits_2(env_dir, capsys):
    """A non-existent file path should cause exit 2 (usage error)."""
    tmp, _write = env_dir
    base = _write("base.env", "KEY=1\n")
    sys.argv = ["envdiff-differ", str(base), str(tmp / "ghost.env")]
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
