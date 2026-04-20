"""Tests for envdiff.snapshotter."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envdiff.snapshotter import diff_snapshot, load_snapshot, save_snapshot, take_snapshot


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# take_snapshot
# ---------------------------------------------------------------------------

def test_take_snapshot_keys(env_dir):
    f = _write(env_dir / ".env", "FOO=bar\nBAZ=qux\n")
    snap = take_snapshot(f)
    assert snap["keys"] == {"FOO": "bar", "BAZ": "qux"}


def test_take_snapshot_default_label(env_dir):
    f = _write(env_dir / "prod.env", "X=1\n")
    snap = take_snapshot(f)
    assert snap["label"] == "prod.env"


def test_take_snapshot_custom_label(env_dir):
    f = _write(env_dir / ".env", "X=1\n")
    snap = take_snapshot(f, label="production")
    assert snap["label"] == "production"


def test_take_snapshot_has_timestamp(env_dir):
    f = _write(env_dir / ".env", "X=1\n")
    before = time.time()
    snap = take_snapshot(f)
    assert snap["timestamp"] >= before


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_roundtrip(env_dir):
    f = _write(env_dir / ".env", "A=1\nB=2\n")
    snap = take_snapshot(f, label="test")
    out = env_dir / "snap.json"
    save_snapshot(snap, out)
    loaded = load_snapshot(out)
    assert loaded["keys"] == {"A": "1", "B": "2"}
    assert loaded["label"] == "test"


def test_load_invalid_snapshot_raises(env_dir):
    bad = env_dir / "bad.json"
    bad.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid snapshot"):
        load_snapshot(bad)


# ---------------------------------------------------------------------------
# diff_snapshot
# ---------------------------------------------------------------------------

def test_diff_no_changes(env_dir):
    f = _write(env_dir / ".env", "A=1\nB=2\n")
    snap = take_snapshot(f)
    result = diff_snapshot(snap, f)
    assert result["has_differences"] is False
    assert result["added"] == []
    assert result["removed"] == []
    assert result["changed"] == []


def test_diff_detects_added_key(env_dir):
    old = _write(env_dir / "old.env", "A=1\n")
    snap = take_snapshot(old)
    new = _write(env_dir / "new.env", "A=1\nB=2\n")
    result = diff_snapshot(snap, new)
    assert "B" in result["added"]
    assert result["has_differences"] is True


def test_diff_detects_removed_key(env_dir):
    old = _write(env_dir / "old.env", "A=1\nB=2\n")
    snap = take_snapshot(old)
    new = _write(env_dir / "new.env", "A=1\n")
    result = diff_snapshot(snap, new)
    assert "B" in result["removed"]


def test_diff_detects_changed_value(env_dir):
    old = _write(env_dir / "old.env", "A=original\n")
    snap = take_snapshot(old)
    new = _write(env_dir / "new.env", "A=changed\n")
    result = diff_snapshot(snap, new)
    assert result["changed"][0] == {"key": "A", "old": "original", "new": "changed"}


def test_diff_no_value_check_ignores_changes(env_dir):
    old = _write(env_dir / "old.env", "A=1\n")
    snap = take_snapshot(old)
    new = _write(env_dir / "new.env", "A=999\n")
    result = diff_snapshot(snap, new, check_values=False)
    assert result["changed"] == []
    assert result["has_differences"] is False
