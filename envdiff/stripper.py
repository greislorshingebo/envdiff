"""Strip unused or empty keys from an env dict or file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class StripResult:
    original: Dict[str, Optional[str]]
    stripped: Dict[str, Optional[str]]
    removed_keys: List[str] = field(default_factory=list)

    @property
    def remove_count(self) -> int:
        return len(self.removed_keys)

    def summary(self) -> str:
        if not self.removed_keys:
            return "No keys removed."
        keys = ", ".join(sorted(self.removed_keys))
        return f"Removed {self.remove_count} key(s): {keys}"


def strip_empty(
    env: Dict[str, Optional[str]],
    strip_none: bool = True,
    strip_blank: bool = True,
) -> StripResult:
    """Remove keys whose values are None or empty/whitespace strings."""
    removed: List[str] = []
    result: Dict[str, Optional[str]] = {}

    for key, value in env.items():
        if strip_none and value is None:
            removed.append(key)
            continue
        if strip_blank and isinstance(value, str) and value.strip() == "":
            removed.append(key)
            continue
        result[key] = value

    return StripResult(original=dict(env), stripped=result, removed_keys=removed)


def strip_keys(
    env: Dict[str, Optional[str]],
    keys: List[str],
) -> StripResult:
    """Remove a specific list of keys from the env dict."""
    removed: List[str] = []
    result: Dict[str, Optional[str]] = {}

    keys_set = set(keys)
    for key, value in env.items():
        if key in keys_set:
            removed.append(key)
        else:
            result[key] = value

    return StripResult(original=dict(env), stripped=result, removed_keys=removed)


def strip_env_file(
    path: str,
    strip_none: bool = True,
    strip_blank: bool = True,
    keys: Optional[List[str]] = None,
) -> StripResult:
    """Parse a .env file and strip empty values or explicit keys."""
    env = parse_env_file(path)
    if keys:
        return strip_keys(env, keys)
    return strip_empty(env, strip_none=strip_none, strip_blank=strip_blank)
