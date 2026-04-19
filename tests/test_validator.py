import pytest
from envdiff.validator import validate_env, KeySchema, ValidationResult


@pytest.fixture
def schema():
    return {
        "DATABASE_URL": KeySchema(required=True, expected_type="url"),
        "PORT": KeySchema(required=True, expected_type="int"),
        "DEBUG": KeySchema(required=False, expected_type="bool"),
        "APP_NAME": KeySchema(required=True, expected_type=None),
    }


def test_valid_env(schema):
    env = {"DATABASE_URL": "https://db.example.com", "PORT": "5432", "APP_NAME": "myapp"}
    result = validate_env(env, schema)
    assert result.is_valid
    assert result.summary() == "valid"


def test_missing_required(schema):
    env = {"DATABASE_URL": "https://db.example.com"}
    result = validate_env(env, schema)
    assert not result.is_valid
    assert "PORT" in result.missing_required
    assert "APP_NAME" in result.missing_required


def test_optional_key_absent_is_valid(schema):
    env = {"DATABASE_URL": "https://db.example.com", "PORT": "8080", "APP_NAME": "x"}
    result = validate_env(env, schema)
    assert result.is_valid
    assert "DEBUG" not in result.missing_required


def test_type_error_int(schema):
    env = {"DATABASE_URL": "https://db.example.com", "PORT": "not-a-port", "APP_NAME": "x"}
    result = validate_env(env, schema)
    assert not result.is_valid
    assert "PORT" in result.type_errors


def test_type_error_bool(schema):
    env = {
        "DATABASE_URL": "https://db.example.com",
        "PORT": "5432",
        "APP_NAME": "x",
        "DEBUG": "maybe",
    }
    result = validate_env(env, schema)
    assert "DEBUG" in result.type_errors


def test_type_error_url(schema):
    env = {"DATABASE_URL": "ftp://bad", "PORT": "5432", "APP_NAME": "x"}
    result = validate_env(env, schema)
    assert "DATABASE_URL" in result.type_errors


def test_unknown_keys_detected(schema):
    env = {
        "DATABASE_URL": "https://db.example.com",
        "PORT": "5432",
        "APP_NAME": "x",
        "UNKNOWN_VAR": "something",
    }
    result = validate_env(env, schema)
    assert "UNKNOWN_VAR" in result.unknown_keys
    assert result.is_valid  # unknown keys don't fail validation


def test_summary_lists_problems(schema):
    env = {"DATABASE_URL": "ftp://bad"}  # missing PORT, APP_NAME; bad URL
    result = validate_env(env, schema)
    s = result.summary()
    assert "missing required" in s
    assert "type error" in s
