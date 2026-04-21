"""Tests for envdiff.masker."""
from __future__ import annotations

import pytest

from envdiff.masker import (
    MaskOptions,
    MASK_PLACEHOLDER,
    mask_env,
    masked_keys,
    should_mask,
)


# ---------------------------------------------------------------------------
# should_mask
# ---------------------------------------------------------------------------

class TestShouldMask:
    def test_password_key_masked(self):
        assert should_mask("PASSWORD") is True

    def test_token_key_masked(self):
        assert should_mask("AUTH_TOKEN") is True

    def test_api_key_masked(self):
        assert should_mask("API_KEY") is True

    def test_plain_key_not_masked(self):
        assert should_mask("APP_ENV") is False

    def test_explicit_key_masked(self):
        opts = MaskOptions(explicit_keys=["MY_CUSTOM_SECRET_FIELD"])
        assert should_mask("MY_CUSTOM_SECRET_FIELD", opts) is True

    def test_explicit_key_not_in_defaults(self):
        opts = MaskOptions(patterns=[], explicit_keys=["SPECIAL"])
        assert should_mask("SPECIAL", opts) is True
        assert should_mask("OTHER", opts) is False

    def test_case_insensitive_by_default(self):
        assert should_mask("db_password") is True

    def test_case_sensitive_no_match(self):
        opts = MaskOptions(case_sensitive=True)
        # default patterns use lowercase literals; uppercase key should NOT match
        assert should_mask("PASSWORD", opts) is False

    def test_custom_pattern(self):
        opts = MaskOptions(patterns=[r"internal.*"])
        assert should_mask("INTERNAL_KEY", opts) is True
        assert should_mask("PUBLIC_KEY", opts) is False


# ---------------------------------------------------------------------------
# mask_env
# ---------------------------------------------------------------------------

class TestMaskEnv:
    def test_sensitive_values_replaced(self):
        env = {"DB_PASSWORD": "s3cr3t", "APP_ENV": "production"}
        result = mask_env(env)
        assert result["DB_PASSWORD"] == MASK_PLACEHOLDER
        assert result["APP_ENV"] == "production"

    def test_original_dict_unchanged(self):
        env = {"SECRET": "abc"}
        mask_env(env)
        assert env["SECRET"] == "abc"

    def test_custom_placeholder(self):
        opts = MaskOptions(placeholder="[HIDDEN]")
        result = mask_env({"API_KEY": "xyz"}, opts)
        assert result["API_KEY"] == "[HIDDEN]"

    def test_none_value_stays_none_when_not_sensitive(self):
        result = mask_env({"APP_NAME": None})
        assert result["APP_NAME"] is None

    def test_none_value_masked_when_sensitive(self):
        result = mask_env({"DB_PASSWORD": None})
        assert result["DB_PASSWORD"] == MASK_PLACEHOLDER

    def test_empty_env(self):
        assert mask_env({}) == {}


# ---------------------------------------------------------------------------
# masked_keys
# ---------------------------------------------------------------------------

class TestMaskedKeys:
    def test_returns_sorted_list(self):
        env = {"TOKEN": "t", "APP": "a", "SECRET": "s"}
        keys = masked_keys(env)
        assert keys == sorted(keys)
        assert "TOKEN" in keys
        assert "SECRET" in keys
        assert "APP" not in keys

    def test_empty_when_no_sensitive(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        assert masked_keys(env) == []
