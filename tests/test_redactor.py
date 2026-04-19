"""Tests for envdiff.redactor."""

import pytest
from envdiff.comparator import DiffEntry, DiffResult
from envdiff.redactor import REDACTED, redact_entry, redact_result, _DEFAULT_PATTERNS


def _entry(key, base=None, compare=None, status="ok"):
    return DiffEntry(key=key, status=status, base_value=base, compare_value=compare)


def test_non_sensitive_key_unchanged():
    e = _entry("APP_NAME", base="myapp", compare="myapp")
    result = redact_entry(e, _DEFAULT_PATTERNS)
    assert result.base_value == "myapp"
    assert result.compare_value == "myapp"


def test_password_key_redacted():
    e = _entry("DB_PASSWORD", base="s3cr3t", compare="other")
    result = redact_entry(e, _DEFAULT_PATTERNS)
    assert result.base_value == REDACTED
    assert result.compare_value == REDACTED


def test_token_key_redacted():
    e = _entry("GITHUB_TOKEN", base="ghp_abc", compare=None, status="missing_in_compare")
    result = redact_entry(e, _DEFAULT_PATTERNS)
    assert result.base_value == REDACTED
    assert result.compare_value is None


def test_api_key_redacted():
    e = _entry("STRIPE_API_KEY", base="sk_live", compare="sk_test", status="mismatch")
    result = redact_entry(e, _DEFAULT_PATTERNS)
    assert result.base_value == REDACTED
    assert result.compare_value == REDACTED
    assert result.status == "mismatch"


def test_redact_result_mixed_entries():
    dr = DiffResult(entries=[
        _entry("APP_ENV", base="prod", compare="dev", status="mismatch"),
        _entry("SECRET_KEY", base="abc", compare="xyz", status="mismatch"),
        _entry("PORT", base="8080", compare="8080"),
    ])
    redacted = redact_result(dr)
    by_key = {e.key: e for e in redacted.entries}
    assert by_key["APP_ENV"].base_value == "prod"
    assert by_key["SECRET_KEY"].base_value == REDACTED
    assert by_key["PORT"].base_value == "8080"


def test_extra_patterns_applied():
    e = _entry("INTERNAL_CERT", base="cert_data", compare="cert_data")
    result = redact_entry(e, _DEFAULT_PATTERNS + [__import__('re').compile(r"cert", __import__('re').I)])
    assert result.base_value == REDACTED


def test_redact_result_with_extra_patterns():
    dr = DiffResult(entries=[_entry("MY_CERT", base="data", compare="data")])
    redacted = redact_result(dr, extra_patterns=[r"cert"])
    assert redacted.entries[0].base_value == REDACTED


def test_none_values_stay_none_after_redact():
    e = _entry("DB_PASSWORD", base=None, compare=None, status="missing_in_base")
    result = redact_entry(e, _DEFAULT_PATTERNS)
    assert result.base_value is None
    assert result.compare_value is None
