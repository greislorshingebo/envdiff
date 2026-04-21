"""Tests for envdiff.tagger."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.tagger import (
    TagRule,
    TaggedResult,
    rules_from_dict,
    tag_result,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Entry:  # minimal stand-in for a comparator Entry
    def __init__(self, key, status="ok", base=None, cmp=None):
        self.key = key
        self.status = status
        self.base_value = base
        self.compare_value = cmp


def _make_result(*keys_statuses) -> DiffResult:
    entries = [_Entry(k, s) for k, s in keys_statuses]
    result = object.__new__(DiffResult)
    object.__setattr__(result, "entries", entries)
    return result


# ---------------------------------------------------------------------------
# tag_result
# ---------------------------------------------------------------------------

def test_no_rules_produces_empty_tags():
    result = _make_result(("DB_HOST", "ok"), ("API_KEY", "mismatch"))
    tagged = tag_result(result, [])
    assert all(e.tags == [] for e in tagged.entries)


def test_glob_pattern_matches_prefix():
    result = _make_result(("DB_HOST", "ok"), ("DB_PORT", "ok"), ("APP_NAME", "ok"))
    rules = [TagRule(pattern="DB_*", tag="database")]
    tagged = tag_result(result, rules)
    db_entries = {e.key: e.tags for e in tagged.entries}
    assert db_entries["DB_HOST"] == ["database"]
    assert db_entries["DB_PORT"] == ["database"]
    assert db_entries["APP_NAME"] == []


def test_multiple_rules_can_match_same_key():
    result = _make_result(("DB_PASSWORD", "ok"))
    rules = [TagRule("DB_*", "database"), TagRule("*PASSWORD*", "secret")]
    tagged = tag_result(result, rules)
    assert set(tagged.entries[0].tags) == {"database", "secret"}


def test_by_tag_filters_correctly():
    result = _make_result(("DB_HOST", "ok"), ("APP_NAME", "ok"))
    rules = [TagRule("DB_*", "database")]
    tagged = tag_result(result, rules)
    db_only = tagged.by_tag("database")
    assert len(db_only) == 1
    assert db_only[0].key == "DB_HOST"


def test_by_tag_unknown_returns_empty():
    result = _make_result(("FOO", "ok"))
    tagged = tag_result(result, [])
    assert tagged.by_tag("nonexistent") == []


def test_all_tags_sorted_and_unique():
    result = _make_result(("DB_HOST", "ok"), ("DB_PASS", "ok"), ("APP_NAME", "ok"))
    rules = [TagRule("DB_*", "database"), TagRule("*PASS*", "secret")]
    tagged = tag_result(result, rules)
    assert tagged.all_tags() == ["database", "secret"]


def test_rules_from_dict():
    mapping = {"DB_*": "database", "*KEY*": "secret"}
    rules = rules_from_dict(mapping)
    assert len(rules) == 2
    patterns = {r.pattern for r in rules}
    tags = {r.tag for r in rules}
    assert patterns == {"DB_*", "*KEY*"}
    assert tags == {"database", "secret"}


def test_tagged_result_preserves_status():
    result = _make_result(("MISSING_KEY", "missing_in_compare"))
    tagged = tag_result(result, [TagRule("MISSING_*", "absent")])
    assert tagged.entries[0].status == "missing_in_compare"
    assert "absent" in tagged.entries[0].tags
