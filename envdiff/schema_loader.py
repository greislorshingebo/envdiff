"""Load a validation schema from a TOML or JSON file."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict

from envdiff.validator import KeySchema, SCHEMA


def _parse_entry(data: dict) -> KeySchema:
    return KeySchema(
        required=bool(data.get("required", True)),
        expected_type=data.get("type"),
    )


def load_schema_json(path: str | Path) -> SCHEMA:
    """Load schema from a JSON file.

    Expected format::

        {
          "DATABASE_URL": {"required": true, "type": "url"},
          "PORT":         {"required": true, "type": "int"},
          "DEBUG":        {"required": false, "type": "bool"}
        }
    """
    text = Path(path).read_text(encoding="utf-8")
    raw: Dict[str, dict] = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("Schema JSON must be a top-level object")
    return {key: _parse_entry(entry) for key, entry in raw.items()}


def load_schema_toml(path: str | Path) -> SCHEMA:
    """Load schema from a TOML file (requires Python 3.11+ or tomli)."""
    try:
        import tomllib  # type: ignore
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "tomllib/tomli is required to load TOML schemas. "
                "Install tomli: pip install tomli"
            ) from exc

    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return {key: _parse_entry(entry) for key, entry in data.items()}


def load_schema(path: str | Path) -> SCHEMA:
    """Auto-detect format from file extension and load schema."""
    p = Path(path)
    if p.suffix == ".json":
        return load_schema_json(p)
    if p.suffix == ".toml":
        return load_schema_toml(p)
    raise ValueError(f"Unsupported schema format: {p.suffix!r} (use .json or .toml)")
