"""Tests for envdiff.deduplicator."""
import pytest

from envdiff.deduplicator import DeduplicateResult, deduplicate


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc"}
C = {"HOST": "staging.example.com", "SECRET": "xyz", "EXTRA": "1"}


# ---------------------------------------------------------------------------
# strategy: first
# ---------------------------------------------------------------------------


def test_first_strategy_keeps_first_value():
    result = deduplicate([A, B], strategy="first")
    assert result.deduped["HOST"] == "localhost"


def test_first_strategy_key_only_in_second_env():
    result = deduplicate([A, B], strategy="first")
    assert result.deduped["SECRET"] == "abc"


def test_first_strategy_identical_values_no_conflict():
    result = deduplicate([A, B], strategy="first")
    assert "PORT" not in result.conflicts


# ---------------------------------------------------------------------------
# strategy: last
# ---------------------------------------------------------------------------


def test_last_strategy_keeps_last_value():
    result = deduplicate([A, B, C], strategy="last")
    assert result.deduped["HOST"] == "staging.example.com"


def test_last_strategy_secret_overridden():
    result = deduplicate([B, C], strategy="last")
    assert result.deduped["SECRET"] == "xyz"


# ---------------------------------------------------------------------------
# strategy: longest
# ---------------------------------------------------------------------------


def test_longest_strategy_picks_longer_string():
    env1 = {"URL": "http://a.io"}
    env2 = {"URL": "http://much-longer-hostname.example.com"}
    result = deduplicate([env1, env2], strategy="longest")
    assert result.deduped["URL"] == "http://much-longer-hostname.example.com"


def test_longest_strategy_skips_none_values():
    env1 = {"KEY": None}
    env2 = {"KEY": "value"}
    result = deduplicate([env1, env2], strategy="longest")
    assert result.deduped["KEY"] == "value"


# ---------------------------------------------------------------------------
# conflicts
# ---------------------------------------------------------------------------


def test_conflict_detected_for_differing_values():
    result = deduplicate([A, B], strategy="first")
    assert "HOST" in result.conflicts
    assert "localhost" in result.conflicts["HOST"]
    assert "prod.example.com" in result.conflicts["HOST"]


def test_no_conflict_for_same_value():
    result = deduplicate([A, B], strategy="first")
    assert "PORT" not in result.conflicts


def test_has_conflicts_true():
    result = deduplicate([A, B], strategy="first")
    assert result.has_conflicts is True


def test_has_conflicts_false():
    result = deduplicate([{"K": "v"}, {"K": "v"}], strategy="first")
    assert result.has_conflicts is False


# ---------------------------------------------------------------------------
# summary / metadata
# ---------------------------------------------------------------------------


def test_summary_contains_key_count():
    result = deduplicate([A, B], strategy="first")
    assert str(len(result.deduped)) in result.summary()


def test_original_preserves_all_values():
    result = deduplicate([A, B], strategy="first")
    assert len(result.original["HOST"]) == 2


def test_empty_envs_returns_empty_result():
    result = deduplicate([], strategy="first")
    assert result.deduped == {}
    assert result.has_conflicts is False


def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate([A], strategy="bogus")
