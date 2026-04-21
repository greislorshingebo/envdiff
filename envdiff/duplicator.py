"""Detect and report duplicate keys within a single .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class DuplicateResult:
    path: Path
    duplicates: Dict[str, List[str]] = field(default_factory=dict)
    # maps key -> list of raw lines where it appeared

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    @property
    def duplicate_keys(self) -> List[str]:
        return sorted(self.duplicates.keys())

    def summary(self) -> str:
        if not self.has_duplicates:
            return f"{self.path}: no duplicate keys found."
        keys = ", ".join(self.duplicate_keys)
        return (
            f"{self.path}: {len(self.duplicates)} duplicate key(s) found: {keys}"
        )


def find_duplicates(path: Path) -> DuplicateResult:
    """Parse *path* line-by-line and collect keys that appear more than once."""
    seen: Dict[str, List[str]] = {}

    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, _ = line.partition("=")
            key = key.strip()
            if not key:
                continue
            seen.setdefault(key, []).append(raw_line.rstrip("\n"))

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    return DuplicateResult(path=path, duplicates=duplicates)
