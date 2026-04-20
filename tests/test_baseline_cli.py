"""Tests for envdiff.baseline_cli module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.baseline_cli import main


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_capture_creates_file(env_dir, capsys):
    env = _write(env_dir / ".env", "FOO=bar\n")
    out = env_dir / "bl.json"
    main(["capture", str(env), "-o", str(out)])
    assert out.exists()


def test_capture_output_message(env_dir, capsys):
    env = _write(env_dir / ".env", "A=1\nB=2\n")
    out = env_dir / "bl.json"
    main(["capture", str(env), "-o", str(out)])
    captured = capsys.readouterr()
    assert "2 keys" in captured.out


def test_capture_custom_label(env_dir):
    env = _write(env_dir / ".env", "X=1\n")
    out = env_dir / "bl.json"
    main(["capture", str(env), "-o", str(out), "--label", "prod"])
    data = json.loads(out.read_text())
    assert data["label"] == "prod"


def test_show_prints_keys(env_dir, capsys):
    env = _write(env_dir / ".env", "ALPHA=1\nBETA=2\n")
    out = env_dir / "bl.json"
    main(["capture", str(env), "-o", str(out)])
    main(["show", "-b", str(out)])
    captured = capsys.readouterr()
    assert "ALPHA" in captured.out
    assert "BETA" in captured.out


def test_diff_exits_zero_when_identical(env_dir):
    env = _write(env_dir / ".env", "K=v\n")
    out = env_dir / "bl.json"
    main(["capture", str(env), "-o", str(out)])
    # Should not raise SystemExit
    main(["diff", str(env), "-b", str(out), "--exit-code"])


def test_diff_exits_one_when_different(env_dir):
    base = _write(env_dir / "base.env", "A=1\nB=2\n")
    out = env_dir / "bl.json"
    main(["capture", str(base), "-o", str(out)])
    current = _write(env_dir / "current.env", "A=1\n")
    with pytest.raises(SystemExit) as exc_info:
        main(["diff", str(current), "-b", str(out), "--exit-code"])
    assert exc_info.value.code == 1


def test_diff_no_exit_code_flag_no_exit(env_dir):
    base = _write(env_dir / "base.env", "A=1\n")
    out = env_dir / "bl.json"
    main(["capture", str(base), "-o", str(out)])
    current = _write(env_dir / "current.env", "A=changed\n")
    # Without --exit-code, should not raise even with differences
    main(["diff", str(current), "-b", str(out)])
