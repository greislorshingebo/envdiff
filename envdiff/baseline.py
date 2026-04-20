"""Baseline management: save a canonical .env as the reference baseline and diff against it."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envdiff.comparator import compare
from envdiff.parser import parse_env_file

_DEFAULT_BASELINE_FILE = ".envdiff_baseline.json"


@dataclass
class Baseline:
    label: str
    created_at: str
    env: dict[str, Optional[str]]

    def to_dict(self) -> dict:
        return {"label": self.label, "created_at": self.created_at, "env": self.env}

    @staticmethod
    def from_dict(data: dict) -> "Baseline":
        return Baseline(
            label=data["label"],
            created_at=data["created_at"],
            env=data["env"],
        )


def capture_baseline(env_path: Path, label: str = "baseline") -> Baseline:
    """Parse *env_path* and return a Baseline snapshot."""
    env = parse_env_file(env_path)
    return Baseline(
        label=label,
        created_at=datetime.now(timezone.utc).isoformat(),
        env=env,
    )


def save_baseline(baseline: Baseline, dest: Path = Path(_DEFAULT_BASELINE_FILE)) -> None:
    """Serialise *baseline* to JSON at *dest*."""
    dest.write_text(json.dumps(baseline.to_dict(), indent=2), encoding="utf-8")


def load_baseline(src: Path = Path(_DEFAULT_BASELINE_FILE)) -> Baseline:
    """Load a previously saved baseline from *src*."""
    data = json.loads(src.read_text(encoding="utf-8"))
    return Baseline.from_dict(data)


def diff_against_baseline(env_path: Path, baseline: Baseline, check_values: bool = True):
    """Compare *env_path* against *baseline* and return a DiffResult."""
    current = parse_env_file(env_path)
    return compare(baseline.env, current, check_values=check_values)
