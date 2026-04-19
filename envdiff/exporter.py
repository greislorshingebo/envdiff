"""Export diff results to structured formats (JSON, CSV)."""
from __future__ import annotations
import csv
import io
import json
from typing import Any, Dict, List

from envdiff.comparator import DiffResult


def to_dict(result: DiffResult, base_path: str = "", compare_path: str = "") -> Dict[str, Any]:
    """Serialise a DiffResult to a plain dictionary."""
    rows: List[Dict[str, Any]] = []
    for key in sorted(result.missing_in_compare):
        rows.append({"key": key, "status": "missing_in_compare", "base": None, "compare": None})
    for key in sorted(result.missing_in_base):
        rows.append({"key": key, "status": "missing_in_base", "base": None, "compare": None})
    for key, (bv, cv) in sorted(result.mismatched.items()):
        rows.append({"key": key, "status": "mismatch", "base": bv, "compare": cv})
    return {
        "base": base_path,
        "compare": compare_path,
        "has_differences": result.has_differences,
        "entries": rows,
    }


def to_json(result: DiffResult, base_path: str = "", compare_path: str = "", indent: int = 2) -> str:
    """Return a JSON string representation of the diff result."""
    return json.dumps(to_dict(result, base_path, compare_path), indent=indent)


def to_csv(result: DiffResult, base_path: str = "", compare_path: str = "") -> str:
    """Return a CSV string representation of the diff result."""
    data = to_dict(result, base_path, compare_path)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["key", "status", "base", "compare"])
    writer.writeheader()
    for entry in data["entries"]:
        writer.writerow(entry)
    return output.getvalue()
