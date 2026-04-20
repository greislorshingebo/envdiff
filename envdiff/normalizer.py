"""normalizer.py — Normalize .env values for consistent comparison.

Provides utilities to strip quotes, normalize whitespace, expand common
boolean aliases, and case-fold keys so that comparisons are not tripped
up by superficial formatting differences between environments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional

# Canonical truthy / falsy aliases
_BOOL_TRUE = frozenset({"1", "true", "yes", "on"})
_BOOL_FALSE = frozenset({"0", "false", "no", "off"})


@dataclass
class NormalizedEnv:
    """Holds a normalized copy of a parsed .env mapping.

    Attributes:
        original: The raw key→value mapping before normalization.
        normalized: The key→value mapping after normalization.
        changed_keys: Keys whose value changed during normalization.
    """

    original: Dict[str, Optional[str]]
    normalized: Dict[str, Optional[str]]
    changed_keys: list[str] = field(default_factory=list)

    def __len__(self) -> int:  # pragma: no cover
        return len(self.normalized)


def normalize_key(key: str) -> str:
    """Return *key* uppercased and with surrounding whitespace stripped.

    >>> normalize_key("  db_host  ")
    'DB_HOST'
    """
    return key.strip().upper()


def normalize_value(value: Optional[str]) -> Optional[str]:
    """Return a canonical form of *value*.

    Steps applied in order:
    1. ``None`` is returned as-is (key present but no value).
    2. Strip surrounding whitespace.
    3. Remove matching outer single or double quotes.
    4. Collapse internal runs of whitespace to a single space.
    5. Normalise boolean-like strings to lowercase ``"true"`` / ``"false"``.

    >>> normalize_value('  "Hello  World"  ')
    'Hello World'
    >>> normalize_value('YES')
    'true'
    """
    if value is None:
        return None

    v = value.strip()

    # Remove matching outer quotes
    if (v.startswith('"') and v.endswith('"')) or (
        v.startswith("'") and v.endswith("'")
    ):
        v = v[1:-1]

    # Collapse internal whitespace
    v = re.sub(r"\s+", " ", v).strip()

    # Normalise boolean aliases
    lower = v.lower()
    if lower in _BOOL_TRUE:
        return "true"
    if lower in _BOOL_FALSE:
        return "false"

    return v


def normalize_env(
    env: Dict[str, Optional[str]],
    *,
    fold_keys: bool = True,
) -> NormalizedEnv:
    """Normalize an entire parsed env mapping.

    Args:
        env: Raw key→value mapping, typically from ``parse_env_file``.
        fold_keys: When *True* (default) keys are uppercased.  Set to
            *False* to preserve original casing while still normalizing
            values.

    Returns:
        A :class:`NormalizedEnv` with the original and normalized views
        plus a list of keys whose values were altered.
    """
    normalized: Dict[str, Optional[str]] = {}
    changed: list[str] = []

    for raw_key, raw_value in env.items():
        key = normalize_key(raw_key) if fold_keys else raw_key.strip()
        norm_value = normalize_value(raw_value)

        normalized[key] = norm_value

        if norm_value != raw_value:
            changed.append(key)

    return NormalizedEnv(
        original=dict(env),
        normalized=normalized,
        changed_keys=changed,
    )


def normalize_env_files(
    envs: Dict[str, Dict[str, Optional[str]]],
    *,
    fold_keys: bool = True,
) -> Dict[str, NormalizedEnv]:
    """Normalize multiple named env mappings at once.

    Args:
        envs: Mapping of label → raw env dict (e.g. ``{"prod": {...}, "staging": {...}}``).
        fold_keys: Forwarded to :func:`normalize_env`.

    Returns:
        Mapping of label → :class:`NormalizedEnv`.
    """
    return {
        label: normalize_env(env, fold_keys=fold_keys)
        for label, env in envs.items()
    }
