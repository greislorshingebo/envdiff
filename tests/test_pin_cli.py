"""Tests for envdiff.pin_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.pin_cli import main


@pytest.fixture()
def env_dir(tmp_path: Path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# capture sub-command
# ---------------------------------------------------------------------------

def test_capture_creates_pin_file(env_dir: Path):
    env = _write(env_dir / ".env", "FOO=bar\nBAZ=qux\n")
    out = env_dir / "pin.json"
    rc = main(["capture", str(env), "--output", str(out)])
    assert rc == 0
    assert out.exists()


def test_capture_pin_file_contents(env_dir: Path):
    env = _write(env_dir / ".env", "KEY=value\n")
    out = env_dir / "pin.json"
    main(["capture", str(env), "--output", str(out)])
    data = json.loads(out.read_text())
    assert data["KEY"] == "value"


def test_capture_missing_env_file_returns_2(env_dir: Path):
    rc = main(["capture", str(env_dir / "missing.env")])
    assert rc == 2


# ---------------------------------------------------------------------------
# check sub-command
# ---------------------------------------------------------------------------

def test_check_no_drift_exits_zero(env_dir: Path):
    env = _write(env_dir / ".env", "FOO=bar\n")
    pin = env_dir / "pin.json"
    main(["capture", str(env), "--output", str(pin)])
    rc = main(["check", str(pin), str(env)])
    assert rc == 0


def test_check_drift_exits_zero_without_flag(env_dir: Path):
    pin = env_dir / "pin.json"
    pin.write_text(json.dumps({"FOO": "old"}), encoding="utf-8")
    env = _write(env_dir / ".env", "FOO=new\n")
    rc = main(["check", str(pin), str(env)])
    assert rc == 0  # no --exit-code flag


def test_check_drift_exits_one_with_flag(env_dir: Path):
    pin = env_dir / "pin.json"
    pin.write_text(json.dumps({"FOO": "old"}), encoding="utf-8")
    env = _write(env_dir / ".env", "FOO=new\n")
    rc = main(["check", str(pin), str(env), "--exit-code"])
    assert rc == 1


def test_check_missing_pin_file_returns_2(env_dir: Path):
    env = _write(env_dir / ".env", "FOO=bar\n")
    rc = main(["check", str(env_dir / "no_pin.json"), str(env)])
    assert rc == 2


def test_check_only_drifted_flag(env_dir: Path, capsys):
    pin = env_dir / "pin.json"
    pin.write_text(json.dumps({"FOO": "old", "BAR": "same"}), encoding="utf-8")
    env = _write(env_dir / ".env", "FOO=new\nBAR=same\n")
    main(["check", str(pin), str(env), "--only-drifted"])
    out = capsys.readouterr().out
    assert "FOO" in out
    assert "BAR" not in out
