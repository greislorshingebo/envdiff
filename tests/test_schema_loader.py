"""Tests for envdiff.schema_loader — JSON and TOML schema loading."""

import json
import pytest

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

from envdiff.schema_loader import load_schema_json, load_schema_toml, load_schema
from envdiff.validator import KeySchema


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def schema_dir(tmp_path):
    """Return a temporary directory for schema files."""
    return tmp_path


def _write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_toml(path, content: str):
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# JSON loading
# ---------------------------------------------------------------------------

class TestLoadSchemaJson:
    def test_required_key_parsed(self, schema_dir):
        f = schema_dir / "schema.json"
        _write_json(f, {"DATABASE_URL": {"required": True, "type": "str"}})
        schema = load_schema_json(f)
        assert "DATABASE_URL" in schema
        assert schema["DATABASE_URL"].required is True
        assert schema["DATABASE_URL"].type == "str"

    def test_optional_key_defaults(self, schema_dir):
        f = schema_dir / "schema.json"
        _write_json(f, {"DEBUG": {"required": False}})
        schema = load_schema_json(f)
        entry = schema["DEBUG"]
        assert entry.required is False
        # type defaults to str when omitted
        assert entry.type == "str"

    def test_multiple_keys(self, schema_dir):
        f = schema_dir / "schema.json"
        _write_json(f, {
            "HOST": {"required": True, "type": "str"},
            "PORT": {"required": True, "type": "int"},
            "VERBOSE": {"required": False, "type": "bool"},
        })
        schema = load_schema_json(f)
        assert len(schema) == 3
        assert schema["PORT"].type == "int"
        assert schema["VERBOSE"].type == "bool"

    def test_empty_schema(self, schema_dir):
        f = schema_dir / "schema.json"
        _write_json(f, {})
        schema = load_schema_json(f)
        assert schema == {}

    def test_missing_file_raises(self, schema_dir):
        with pytest.raises(FileNotFoundError):
            load_schema_json(schema_dir / "nonexistent.json")


# ---------------------------------------------------------------------------
# TOML loading
# ---------------------------------------------------------------------------

@pytest.mark.skipif(tomllib is None, reason="tomllib/tomli not available")
class TestLoadSchemaToml:
    def test_required_key_parsed(self, schema_dir):
        f = schema_dir / "schema.toml"
        _write_toml(f, '[DATABASE_URL]\nrequired = true\ntype = "str"\n')
        schema = load_schema_toml(f)
        assert "DATABASE_URL" in schema
        assert schema["DATABASE_URL"].required is True
        assert schema["DATABASE_URL"].type == "str"

    def test_optional_key(self, schema_dir):
        f = schema_dir / "schema.toml"
        _write_toml(f, '[CACHE_TTL]\nrequired = false\ntype = "int"\n')
        schema = load_schema_toml(f)
        assert schema["CACHE_TTL"].required is False
        assert schema["CACHE_TTL"].type == "int"

    def test_missing_file_raises(self, schema_dir):
        with pytest.raises(FileNotFoundError):
            load_schema_toml(schema_dir / "no.toml")


# ---------------------------------------------------------------------------
# Generic load_schema dispatcher
# ---------------------------------------------------------------------------

class TestLoadSchema:
    def test_dispatches_json_by_extension(self, schema_dir):
        f = schema_dir / "s.json"
        _write_json(f, {"KEY": {"required": True, "type": "str"}})
        schema = load_schema(f)
        assert "KEY" in schema

    @pytest.mark.skipif(tomllib is None, reason="tomllib/tomli not available")
    def test_dispatches_toml_by_extension(self, schema_dir):
        f = schema_dir / "s.toml"
        _write_toml(f, '[KEY]\nrequired = true\ntype = "str"\n')
        schema = load_schema(f)
        assert "KEY" in schema

    def test_unsupported_extension_raises(self, schema_dir):
        f = schema_dir / "schema.yaml"
        f.write_text("KEY: {required: true}")
        with pytest.raises(ValueError, match="Unsupported schema format"):
            load_schema(f)
