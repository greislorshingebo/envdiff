"""Tests for envdiff.baseline module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.baseline import (
    Baseline,
    capture_baseline,
    diff_against_baseline,
    load_baseline,
    save_baseline,
)


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# --- Baseline dataclass ---

def test_baseline_round_trip():
    bl = Baseline(label="test", created_at="2024-01-01T00:00:00+00:00", env={"A": "1"})
    restored = Baseline.from_dict(bl.to_dict())
    assert restored.label == bl.label
    assert restored.env == bl.env


# --- capture_baseline ---

def test_capture_baseline_keys(env_dir):
    env = _write(env_dir / ".env", "FOO=bar\nBAZ=qux\n")
    bl = capture_baseline(env)
    assert bl.env == {"FOO": "bar", "BAZ": "qux"}


def test_capture_baseline_default_label(env_dir):
    env = _write(env_dir / ".env", "X=1\n")
    bl = capture_baseline(env)
    assert bl.label == "baseline"


def test_capture_baseline_custom_label(env_dir):
    env = _write(env_dir / ".env", "X=1\n")
    bl = capture_baseline(env, label="production")
    assert bl.label == "production"


def test_capture_baseline_created_at_set(env_dir):
    env = _write(env_dir / ".env", "X=1\n")
    bl = capture_baseline(env)
    assert bl.created_at  # non-empty string


# --- save / load ---

def test_save_and_load_baseline(env_dir):
    env = _write(env_dir / ".env", "KEY=value\n")
    bl = capture_baseline(env, label="staging")
    dest = env_dir / "baseline.json"
    save_baseline(bl, dest=dest)
    assert dest.exists()
    loaded = load_baseline(dest)
    assert loaded.label == "staging"
    assert loaded.env == {"KEY": "value"}


def test_save_baseline_valid_json(env_dir):
    env = _write(env_dir / ".env", "A=1\n")
    bl = capture_baseline(env)
    dest = env_dir / "bl.json"
    save_baseline(bl, dest=dest)
    data = json.loads(dest.read_text())
    assert "env" in data and "label" in data and "created_at" in data


# --- diff_against_baseline ---

def test_diff_identical_no_differences(env_dir):
    env_file = _write(env_dir / ".env", "A=1\nB=2\n")
    bl = capture_baseline(env_file)
    result = diff_against_baseline(env_file, bl)
    assert not result.has_differences()


def test_diff_detects_missing_key(env_dir):
    base_file = _write(env_dir / "base.env", "A=1\nB=2\n")
    bl = capture_baseline(base_file)
    current = _write(env_dir / "current.env", "A=1\n")
    result = diff_against_baseline(current, bl)
    missing = [e.key for e in result.entries if e.status == "missing_in_compare"]
    assert "B" in missing


def test_diff_detects_extra_key(env_dir):
    base_file = _write(env_dir / "base.env", "A=1\n")
    bl = capture_baseline(base_file)
    current = _write(env_dir / "current.env", "A=1\nC=3\n")
    result = diff_against_baseline(current, bl)
    extra = [e.key for e in result.entries if e.status == "missing_in_base"]
    assert "C" in extra


def test_diff_no_values_ignores_mismatch(env_dir):
    base_file = _write(env_dir / "base.env", "A=old\n")
    bl = capture_baseline(base_file)
    current = _write(env_dir / "current.env", "A=new\n")
    result = diff_against_baseline(current, bl, check_values=False)
    assert not result.has_differences()
