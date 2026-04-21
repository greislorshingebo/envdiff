"""Tests for envdiff.patcher."""
from pathlib import Path

import pytest

from envdiff.patcher import PatchResult, patch_env, patch_env_file


# ---------------------------------------------------------------------------
# patch_env (in-memory)
# ---------------------------------------------------------------------------

BASE_ENV = "HOST=localhost\nPORT=5432\nDEBUG=false\n"


def test_update_existing_key():
    out, result = patch_env(BASE_ENV, {"PORT": "9999"})
    assert "PORT=9999" in out
    assert "PORT=5432" not in out
    assert result.updated == ["PORT"]
    assert result.added == []


def test_add_missing_key_by_default():
    out, result = patch_env(BASE_ENV, {"NEW_KEY": "hello"})
    assert "NEW_KEY=hello" in out
    assert result.added == ["NEW_KEY"]


def test_add_missing_disabled():
    out, result = patch_env(BASE_ENV, {"NEW_KEY": "hello"}, add_missing=False)
    assert "NEW_KEY" not in out
    assert "NEW_KEY" in result.skipped


def test_overwrite_false_skips_existing():
    out, result = patch_env(BASE_ENV, {"HOST": "remotehost"}, overwrite=False)
    assert "HOST=localhost" in out
    assert "HOST" in result.skipped
    assert result.updated == []


def test_none_value_becomes_empty_string():
    out, result = patch_env(BASE_ENV, {"PORT": None})
    assert "PORT=\n" in out
    assert result.updated == ["PORT"]


def test_preserves_comments_and_blank_lines():
    src = "# comment\n\nHOST=localhost\n"
    out, _ = patch_env(src, {"HOST": "remotehost"})
    assert "# comment" in out
    assert "\n\n" in out


def test_multiple_patches_applied():
    out, result = patch_env(BASE_ENV, {"HOST": "db", "PORT": "3306"})
    assert "HOST=db" in out
    assert "PORT=3306" in out
    assert len(result.updated) == 2


def test_change_count():
    _, result = patch_env(BASE_ENV, {"HOST": "x", "EXTRA": "y"})
    assert result.change_count == 2  # 1 updated + 1 added


def test_summary_no_changes():
    _, result = patch_env(BASE_ENV, {}, add_missing=False)
    assert result.summary() == "no changes"


def test_summary_with_changes():
    _, result = patch_env(BASE_ENV, {"HOST": "x", "NEW": "y"})
    assert "updated" in result.summary()
    assert "added" in result.summary()


# ---------------------------------------------------------------------------
# patch_env_file (file I/O)
# ---------------------------------------------------------------------------


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(BASE_ENV, encoding="utf-8")
    return p


def test_patch_env_file_updates_disk(env_file: Path):
    result = patch_env_file(env_file, {"DEBUG": "true"})
    assert "DEBUG=true" in env_file.read_text()
    assert result.updated == ["DEBUG"]


def test_patch_env_file_adds_key(env_file: Path):
    patch_env_file(env_file, {"LOG_LEVEL": "info"})
    assert "LOG_LEVEL=info" in env_file.read_text()


def test_patch_env_file_no_overwrite(env_file: Path):
    result = patch_env_file(env_file, {"HOST": "other"}, overwrite=False)
    assert "HOST=localhost" in env_file.read_text()
    assert "HOST" in result.skipped
