"""inverter.py – swap keys and values in a parsed env mapping.

Useful for reverse-lookup workflows: given a value, find which key holds it.
Duplicate values are tracked so callers can detect ambiguity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InvertResult:
    """Holds the inverted mapping and any collision metadata."""
    inverted: Dict[str, str]          # value -> key (last-write wins on collision)
    collisions: Dict[str, List[str]]  # value -> all keys that shared it

    @property
    def has_collisions(self) -> bool:
        return bool(self.collisions)

    def lookup(self, value: str) -> Optional[str]:
        """Return the key for *value*, or None if not present."""
        return self.inverted.get(value)

    def summary(self) -> str:
        total = len(self.inverted)
        col = len(self.collisions)
        if col:
            return f"{total} unique value(s), {col} collision(s)"
        return f"{total} unique value(s), no collisions"


def invert_env(env: Dict[str, Optional[str]]) -> InvertResult:
    """Invert *env* so values become keys.

    Keys whose value is ``None`` (missing/empty) are skipped.
    When multiple keys share the same value, all are recorded in
    ``collisions`` and the *last* key encountered wins in ``inverted``.
    """
    inverted: Dict[str, str] = {}
    seen: Dict[str, List[str]] = {}

    for key, value in env.items():
        if value is None:
            continue
        seen.setdefault(value, []).append(key)
        inverted[value] = key  # last-write wins

    collisions = {v: keys for v, keys in seen.items() if len(keys) > 1}
    return InvertResult(inverted=inverted, collisions=collisions)
