"""Snapshot .env files to JSON for later diffing against current state."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Optional

from envdiff.parser import parse_env_file


def take_snapshot(env_path: str | Path, label: Optional[str] = None) -> dict:
    """Parse *env_path* and return a snapshot dict with metadata."""
    path = Path(env_path)
    values = parse_env_file(path)
    return {
        "label": label or path.name,
        "source": str(path.resolve()),
        "timestamp": time.time(),
        "keys": values,
    }


def save_snapshot(snapshot: dict, output_path: str | Path) -> None:
    """Persist *snapshot* as JSON to *output_path*."""
    Path(output_path).write_text(json.dumps(snapshot, indent=2), encoding="utf-8")


def load_snapshot(snapshot_path: str | Path) -> dict:
    """Load a previously saved snapshot from *snapshot_path*."""
    data = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    if "keys" not in data or "label" not in data:
        raise ValueError(f"Invalid snapshot file: {snapshot_path}")
    return data


def diff_snapshot(
    snapshot: dict,
    current_path: str | Path,
    check_values: bool = True,
) -> Dict[str, object]:
    """Compare a saved *snapshot* against the current state of *current_path*.

    Returns a plain dict describing added, removed, and changed keys.
    """
    old: Dict[str, Optional[str]] = snapshot["keys"]
    new: Dict[str, Optional[str]] = parse_env_file(Path(current_path))

    old_keys = set(old)
    new_keys = set(new)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = []
    if check_values:
        for key in sorted(old_keys & new_keys):
            if old[key] != new[key]:
                changed.append({"key": key, "old": old[key], "new": new[key]})

    return {
        "snapshot_label": snapshot["label"],
        "snapshot_timestamp": snapshot["timestamp"],
        "current_source": str(Path(current_path).resolve()),
        "added": added,
        "removed": removed,
        "changed": changed,
        "has_differences": bool(added or removed or changed),
    }
