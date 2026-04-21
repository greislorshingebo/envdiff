"""Tests for envdiff.renamer."""
from __future__ import annotations

import pytest

from envdiff.renamer import RenameResult, rename_env_files, rename_keys


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_env() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_basic_rename(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_value_preserved_after_rename(base_env):
    result = rename_keys(base_env, {"DB_PORT": "DATABASE_PORT"})
    assert result.env["DATABASE_PORT"] == "5432"


def test_missing_key_is_skipped(base_env):
    result = rename_keys(base_env, {"MISSING_KEY": "NEW_KEY"})
    assert "NEW_KEY" not in result.env
    assert "MISSING_KEY" in result.skipped
    assert result.rename_count == 0
    assert result.skip_count == 1


def test_no_overwrite_by_default(base_env):
    """If new_key already exists, skip rename when overwrite=False."""
    env = {"OLD": "old_val", "NEW": "existing"}
    result = rename_keys(env, {"OLD": "NEW"})
    assert result.env["NEW"] == "existing"
    assert result.env["OLD"] == "old_val"
    assert "OLD" in result.skipped


def test_overwrite_replaces_existing():
    env = {"OLD": "old_val", "NEW": "existing"}
    result = rename_keys(env, {"OLD": "NEW"}, overwrite=True)
    assert result.env["NEW"] == "old_val"
    assert "OLD" not in result.env
    assert "OLD" in result.renamed


def test_multiple_renames(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert result.rename_count == 2
    assert result.skip_count == 0
    assert "DB_HOST" not in result.env
    assert "DB_PORT" not in result.env


def test_empty_rename_map(base_env):
    result = rename_keys(base_env, {})
    assert result.env == base_env
    assert result.rename_count == 0


def test_none_value_preserved():
    env = {"KEY": None}
    result = rename_keys(env, {"KEY": "NEW_KEY"})
    assert result.env["NEW_KEY"] is None


# ---------------------------------------------------------------------------
# RenameResult.summary
# ---------------------------------------------------------------------------

def test_summary_renames_only():
    r = RenameResult(env={}, renamed=["A", "B"], skipped=[])
    assert "2 key(s) renamed" in r.summary()
    assert "skipped" not in r.summary()


def test_summary_with_skipped():
    r = RenameResult(env={}, renamed=["A"], skipped=["B"])
    assert "1 key(s) renamed" in r.summary()
    assert "1 key(s) not found" in r.summary()


# ---------------------------------------------------------------------------
# rename_env_files
# ---------------------------------------------------------------------------

def test_rename_env_files_applies_to_all():
    envs = {
        "dev": {"DB_HOST": "dev-host"},
        "prod": {"DB_HOST": "prod-host"},
    }
    results = rename_env_files(envs, {"DB_HOST": "DATABASE_HOST"})
    assert results["dev"].env["DATABASE_HOST"] == "dev-host"
    assert results["prod"].env["DATABASE_HOST"] == "prod-host"
    assert results["dev"].rename_count == 1
