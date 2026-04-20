"""Tests for envdiff.auditor and envdiff.audit_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.comparator import compare
from envdiff.auditor import (
    AuditLog, AuditEntry, record_audit, save_audit_log, load_audit_log,
)
from envdiff.audit_cli import main as audit_main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(base: dict, comp: dict, check_values: bool = True):
    return compare(base, comp, check_values=check_values)


# ---------------------------------------------------------------------------
# record_audit
# ---------------------------------------------------------------------------

def test_record_audit_no_differences():
    result = _make_result({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    entry = record_audit(result, "base.env", "prod.env")
    assert not entry.has_differences
    assert entry.total_keys == 2
    assert entry.missing_in_compare == 0
    assert entry.mismatched == 0


def test_record_audit_missing_in_compare():
    result = _make_result({"A": "1", "B": "2"}, {"A": "1"})
    entry = record_audit(result, "base.env", "prod.env")
    assert entry.has_differences
    assert entry.missing_in_compare == 1


def test_record_audit_mismatch():
    result = _make_result({"A": "1"}, {"A": "999"})
    entry = record_audit(result, "base.env", "prod.env")
    assert entry.mismatched == 1
    assert entry.has_differences


def test_record_audit_label():
    result = _make_result({"X": "1"}, {"X": "1"})
    entry = record_audit(result, "a.env", "b.env", label="release-1.0")
    assert entry.label == "release-1.0"


def test_record_audit_timestamp_is_utc_iso():
    result = _make_result({}, {})
    entry = record_audit(result, "a.env", "b.env")
    assert "+00:00" in entry.timestamp or entry.timestamp.endswith("Z")


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_round_trip(tmp_path):
    log = AuditLog()
    result = _make_result({"K": "v"}, {"K": "v"})
    log.add(record_audit(result, "a.env", "b.env", label="ci"))
    log.add(record_audit(result, "a.env", "c.env"))

    path = tmp_path / "audit.json"
    save_audit_log(log, path)
    loaded = load_audit_log(path)

    assert len(loaded.entries) == 2
    assert loaded.entries[0].label == "ci"
    assert loaded.entries[1].label is None


def test_save_produces_valid_json(tmp_path):
    log = AuditLog()
    result = _make_result({"A": "1"}, {"B": "2"})
    log.add(record_audit(result, "a.env", "b.env"))
    path = tmp_path / "audit.json"
    save_audit_log(log, path)
    data = json.loads(path.read_text())
    assert isinstance(data, list)
    assert "timestamp" in data[0]


# ---------------------------------------------------------------------------
# audit_cli
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_dir(tmp_path):
    (tmp_path / "base.env").write_text("A=1\nB=2\n")
    (tmp_path / "comp.env").write_text("A=1\n")
    return tmp_path


def test_cli_records_entry(env_dir):
    log_path = env_dir / "audit.json"
    rc = audit_main([
        str(env_dir / "base.env"),
        str(env_dir / "comp.env"),
        "--log", str(log_path),
    ])
    assert rc == 0
    log = load_audit_log(log_path)
    assert len(log.entries) == 1
    assert log.entries[0].missing_in_compare == 1


def test_cli_appends_to_existing_log(env_dir):
    log_path = env_dir / "audit.json"
    audit_main([str(env_dir / "base.env"), str(env_dir / "comp.env"), "--log", str(log_path)])
    audit_main([str(env_dir / "base.env"), str(env_dir / "comp.env"), "--log", str(log_path)])
    log = load_audit_log(log_path)
    assert len(log.entries) == 2


def test_cli_missing_file_returns_2(env_dir):
    rc = audit_main([str(env_dir / "base.env"), "nonexistent.env"])
    assert rc == 2
