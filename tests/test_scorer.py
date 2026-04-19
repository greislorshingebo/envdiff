"""Tests for envdiff.scorer."""
import pytest
from envdiff.comparator import DiffResult, compare
from envdiff.scorer import ScoreResult, score_result


@pytest.fixture
def perfect() -> DiffResult:
    base = {"A": "1", "B": "2"}
    comp = {"A": "1", "B": "2"}
    return compare(base, comp)


@pytest.fixture
def mixed() -> DiffResult:
    base = {"A": "1", "B": "2", "C": "3", "D": "4"}
    comp = {"A": "1", "C": "changed", "E": "5"}
    return compare(base, comp)


def test_perfect_score(perfect):
    sr = score_result(perfect)
    assert sr.score == 100.0
    assert sr.grade == "A"
    assert sr.ok == 2
    assert sr.total == 2


def test_mixed_score(mixed):
    sr = score_result(mixed)
    assert sr.total == 5
    assert sr.ok == 1
    assert sr.missing_in_compare == 2
    assert sr.missing_in_base == 1
    assert sr.mismatched == 1
    assert sr.score == 20.0
    assert sr.grade == "F"


def test_empty_env():
    result = compare({}, {})
    sr = score_result(result)
    assert sr.score == 100.0
    assert sr.total == 0
    assert sr.grade == "A"


def test_grade_boundaries():
    def _make(ok, total):
        sr = ScoreResult(
            total=total, ok=ok,
            missing_in_compare=0, missing_in_base=0,
            mismatched=total - ok,
        )
        return sr

    assert _make(8, 10).grade == "B"
    assert _make(6, 10).grade == "C"
    assert _make(4, 10).grade == "D"
    assert _make(2, 10).grade == "F"


def test_summary_contains_score(mixed):
    sr = score_result(mixed)
    s = sr.summary()
    assert "20.0/100" in s
    assert "(F)" in s
    assert "5" in s
