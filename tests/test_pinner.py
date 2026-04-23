"""Tests for envdiff.pinner."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.pinner import (
    PinEntry,
    PinReport,
    check_drift,
    check_drift_files,
    load_pin,
    pin_env,
    save_pin,
)


# ---------------------------------------------------------------------------
# PinEntry / PinReport unit tests
# ---------------------------------------------------------------------------

def test_pin_entry_no_drift():
    e = PinEntry(key="FOO", pinned_value="bar", current_value="bar")
    assert not e.drifted


def test_pin_entry_drift():
    e = PinEntry(key="FOO", pinned_value="bar", current_value="baz")
    assert e.drifted


def test_pin_entry_missing_current():
    e = PinEntry(key="FOO", pinned_value="bar", current_value=None)
    assert e.drifted


def test_report_has_drift_true():
    report = PinReport(entries=[
        PinEntry("A", "1", "1"),
        PinEntry("B", "2", "9"),
    ])
    assert report.has_drift
    assert report.drifted_keys == ["B"]


def test_report_has_drift_false():
    report = PinReport(entries=[
        PinEntry("A", "1", "1"),
        PinEntry("B", "2", "2"),
    ])
    assert not report.has_drift
    assert report.drifted_keys == []


def test_summary_message():
    report = PinReport(entries=[
        PinEntry("A", "1", "2"),
        PinEntry("B", "x", "x"),
    ])
    assert "1/2" in report.summary()


# ---------------------------------------------------------------------------
# check_drift
# ---------------------------------------------------------------------------

def test_check_drift_no_drift():
    pin = {"A": "1", "B": "2"}
    current = {"A": "1", "B": "2"}
    report = check_drift(pin, current)
    assert not report.has_drift


def test_check_drift_detects_value_change():
    pin = {"A": "1"}
    current = {"A": "99"}
    report = check_drift(pin, current)
    assert report.has_drift
    assert "A" in report.drifted_keys


def test_check_drift_detects_new_key():
    pin = {"A": "1"}
    current = {"A": "1", "B": "2"}
    report = check_drift(pin, current)
    assert "B" in report.drifted_keys


def test_check_drift_detects_removed_key():
    pin = {"A": "1", "B": "2"}
    current = {"A": "1"}
    report = check_drift(pin, current)
    assert "B" in report.drifted_keys


# ---------------------------------------------------------------------------
# save_pin / load_pin round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_pin(tmp_path: Path):
    pin_file = tmp_path / "pin.json"
    data = {"FOO": "bar", "SECRET": None}
    save_pin(data, pin_file)
    loaded = load_pin(pin_file)
    assert loaded["FOO"] == "bar"
    assert loaded["SECRET"] is None


def test_pin_env_returns_copy():
    env = {"A": "1", "B": None}
    result = pin_env(env)
    assert result == env
    assert result is not env


# ---------------------------------------------------------------------------
# check_drift_files integration
# ---------------------------------------------------------------------------

def test_check_drift_files(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=hello\nBAR=world\n", encoding="utf-8")
    pin_file = tmp_path / "pin.json"
    save_pin({"FOO": "hello", "BAR": "changed"}, pin_file)

    report = check_drift_files(pin_file, env_file)
    assert "BAR" in report.drifted_keys
    assert "FOO" not in report.drifted_keys
