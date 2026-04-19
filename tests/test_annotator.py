"""Tests for envdiff.annotator."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.annotator import annotate_result, annotation_report, AnnotatedEntry


def _make_result(entries_data):
    """Build a DiffResult from a list of (key, status, base, compare) tuples."""
    from dataclasses import dataclass

    @dataclass
    class _Entry:
        key: str
        status: str
        base_value: str | None
        compare_value: str | None

    entries = [_Entry(*d) for d in entries_data]
    result = object.__new__(DiffResult)
    result.__dict__["entries"] = entries
    return result


def test_annotate_ok():
    result = _make_result([("HOST", "ok", "localhost", "localhost")])
    annotated = annotate_result(result)
    assert len(annotated) == 1
    assert annotated[0].status == "ok"
    assert "identical" in annotated[0].annotation


def test_annotate_missing_in_compare():
    result = _make_result([("SECRET", "missing_in_compare", "abc", None)])
    annotated = annotate_result(result)
    assert "absent from the compare" in annotated[0].annotation


def test_annotate_missing_in_base():
    result = _make_result([("NEW_KEY", "missing_in_base", None, "val")])
    annotated = annotate_result(result)
    assert "absent from the base" in annotated[0].annotation


def test_annotate_mismatch():
    result = _make_result([("PORT", "mismatch", "8080", "9090")])
    annotated = annotate_result(result)
    ann = annotated[0].annotation
    assert "8080" in ann
    assert "9090" in ann
    assert "differs" in ann


def test_annotate_unknown_status():
    result = _make_result([("X", "weird", None, None)])
    annotated = annotate_result(result)
    assert "unknown status" in annotated[0].annotation


def test_annotation_report_empty():
    result = _make_result([])
    report = annotation_report(result)
    assert report == "No entries to annotate."


def test_annotation_report_contains_status_labels():
    result = _make_result([
        ("A", "ok", "1", "1"),
        ("B", "mismatch", "x", "y"),
    ])
    report = annotation_report(result)
    assert "[OK]" in report
    assert "[MISMATCH]" in report


def test_annotated_entry_fields():
    result = _make_result([("DB", "missing_in_compare", "pg", None)])
    entry: AnnotatedEntry = annotate_result(result)[0]
    assert entry.key == "DB"
    assert entry.base_value == "pg"
    assert entry.compare_value is None
