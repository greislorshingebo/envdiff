"""Tests for envdiff.templater."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.templater import generate_template, save_template, _sorted_keys


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}
ENV_B = {"DB_HOST": "prod.example.com", "API_KEY": "xyz", "SECRET": "supersecret"}


# ---------------------------------------------------------------------------
# _sorted_keys
# ---------------------------------------------------------------------------

def test_sorted_keys_union():
    keys = _sorted_keys([ENV_A, ENV_B])
    assert keys == sorted({"DB_HOST", "DB_PORT", "SECRET", "API_KEY"})


def test_sorted_keys_single_env():
    keys = _sorted_keys([ENV_A])
    assert keys == sorted(ENV_A.keys())


def test_sorted_keys_empty():
    assert _sorted_keys([]) == []


# ---------------------------------------------------------------------------
# generate_template — values stripped
# ---------------------------------------------------------------------------

def test_template_strips_values():
    content = generate_template([ENV_A])
    assert "DB_HOST=" in content
    assert "localhost" not in content


def test_template_contains_all_keys():
    content = generate_template([ENV_A, ENV_B])
    for key in ("DB_HOST", "DB_PORT", "SECRET", "API_KEY"):
        assert f"{key}=" in content


def test_template_has_header_comment():
    content = generate_template([ENV_A])
    assert "envdiff" in content.lower()


def test_template_keys_sorted():
    content = generate_template([ENV_A, ENV_B])
    lines = [l for l in content.splitlines() if "=" in l]
    keys_in_output = [l.split("=")[0] for l in lines]
    assert keys_in_output == sorted(keys_in_output)


# ---------------------------------------------------------------------------
# generate_template — include_example_values
# ---------------------------------------------------------------------------

def test_example_values_from_first_env():
    content = generate_template([ENV_A, ENV_B], include_example_values=True)
    # DB_HOST is in ENV_A first
    assert "DB_HOST=localhost" in content


def test_example_values_fallback_to_second_env():
    content = generate_template([ENV_A, ENV_B], include_example_values=True)
    # API_KEY only in ENV_B
    assert "API_KEY=xyz" in content


def test_no_example_values_by_default():
    content = generate_template([ENV_A])
    assert "localhost" not in content
    assert "5432" not in content


# ---------------------------------------------------------------------------
# save_template
# ---------------------------------------------------------------------------

def test_save_template_creates_file(tmp_path: Path):
    out = tmp_path / ".env.template"
    result = save_template([ENV_A], out)
    assert result == out
    assert out.exists()


def test_save_template_content_correct(tmp_path: Path):
    out = tmp_path / ".env.template"
    save_template([ENV_A, ENV_B], out)
    content = out.read_text(encoding="utf-8")
    assert "DB_HOST=" in content
    assert "API_KEY=" in content
    assert "localhost" not in content
