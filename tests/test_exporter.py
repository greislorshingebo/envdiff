"""Tests for envdiff.exporter."""
import json
import csv
import io
import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import to_dict, to_json, to_csv


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_compare={"ONLY_BASE"},
        missing_in_base={"ONLY_COMPARE"},
        mismatched={"PORT": ("5432", "3306")},
    )


def test_to_dict_has_differences(sample_result):
    d = to_dict(sample_result, "base.env", "compare.env")
    assert d["has_differences"] is True
    assert d["base"] == "base.env"
    assert d["compare"] == "compare.env"


def test_to_dict_entries(sample_result):
    d = to_dict(sample_result)
    statuses = {e["key"]: e["status"] for e in d["entries"]}
    assert statuses["ONLY_BASE"] == "missing_in_compare"
    assert statuses["ONLY_COMPARE"] == "missing_in_base"
    assert statuses["PORT"] == "mismatch"


def test_to_json_valid(sample_result):
    raw = to_json(sample_result)
    parsed = json.loads(raw)
    assert isinstance(parsed["entries"], list)
    assert len(parsed["entries"]) == 3


def test_to_json_mismatch_values(sample_result):
    parsed = json.loads(to_json(sample_result))
    port_entry = next(e for e in parsed["entries"] if e["key"] == "PORT")
    assert port_entry["base"] == "5432"
    assert port_entry["compare"] == "3306"


def test_to_csv_headers(sample_result):
    raw = to_csv(sample_result)
    reader = csv.DictReader(io.StringIO(raw))
    assert set(reader.fieldnames) == {"key", "status", "base", "compare"}


def test_to_csv_row_count(sample_result):
    raw = to_csv(sample_result)
    rows = list(csv.DictReader(io.StringIO(raw)))
    assert len(rows) == 3


def test_empty_result_no_differences():
    result = DiffResult(missing_in_compare=set(), missing_in_base=set(), mismatched={})
    d = to_dict(result)
    assert d["has_differences"] is False
    assert d["entries"] == []
