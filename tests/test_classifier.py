"""Tests for envdiff.classifier."""
from __future__ import annotations

import pytest
from envdiff.classifier import (
    classify_key,
    classify_env,
    ClassifiedResult,
    UNCATEGORIZED,
)


# ---------------------------------------------------------------------------
# classify_key
# ---------------------------------------------------------------------------

def test_database_key():
    assert classify_key("DATABASE_URL") == "database"

def test_db_prefix():
    assert classify_key("DB_HOST") == "database"

def test_auth_password():
    assert classify_key("PASSWORD") == "auth"

def test_auth_token():
    assert classify_key("GITHUB_TOKEN") == "auth"

def test_auth_api_key():
    assert classify_key("STRIPE_API_KEY") == "auth"

def test_network_port():
    assert classify_key("PORT") == "network"

def test_network_host():
    assert classify_key("APP_HOST") == "network"

def test_logging_key():
    assert classify_key("LOG_LEVEL") == "logging"

def test_feature_flag():
    assert classify_key("FEATURE_DARK_MODE") == "feature"

def test_storage_s3():
    assert classify_key("S3_BUCKET") == "storage"

def test_email_smtp():
    assert classify_key("SMTP_HOST") == "email"

def test_app_debug():
    assert classify_key("DEBUG") == "app"

def test_uncategorized():
    assert classify_key("SOME_RANDOM_KEY") == UNCATEGORIZED

def test_case_insensitive():
    assert classify_key("db_password") == "database"


# ---------------------------------------------------------------------------
# classify_env
# ---------------------------------------------------------------------------

def test_classify_env_groups_correctly():
    env = {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "abc123",
        "PORT": "8080",
        "SOME_FLAG": "true",
    }
    result = classify_env(env)
    assert "database" in result.categories()
    assert "auth" in result.categories()
    assert "network" in result.categories()
    assert "DATABASE_URL" in result.keys_for("database")
    assert "SECRET_KEY" in result.keys_for("auth")
    assert "PORT" in result.keys_for("network")

def test_classify_empty_env():
    result = classify_env({})
    assert result.categories() == []
    assert result.summary() == "No keys classified."

def test_as_dict_returns_sorted_keys():
    env = {"DB_NAME": "mydb", "DB_HOST": "localhost"}
    result = classify_env(env)
    d = result.as_dict()
    assert d["database"] == sorted(["DB_NAME", "DB_HOST"])

def test_summary_contains_category_and_count():
    env = {"LOG_LEVEL": "info", "LOG_FORMAT": "json"}
    result = classify_env(env)
    summary = result.summary()
    assert "logging" in summary
    assert "2" in summary

def test_keys_for_missing_category_returns_empty():
    result = ClassifiedResult()
    assert result.keys_for("nonexistent") == []
