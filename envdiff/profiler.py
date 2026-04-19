"""Profile .env files: count keys, detect duplicates, and summarize value types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class ProfileResult:
    path: str
    total_keys: int
    duplicate_keys: List[str]
    empty_value_keys: List[str]
    type_hints: Dict[str, str]  # key -> 'bool' | 'int' | 'float' | 'str'
    has_issues: bool = field(init=False)

    def __post_init__(self) -> None:
        self.has_issues = bool(self.duplicate_keys or self.empty_value_keys)

    def summary(self) -> str:
        lines = [
            f"Profile: {self.path}",
            f"  Total keys : {self.total_keys}",
            f"  Duplicates : {', '.join(self.duplicate_keys) or 'none'}",
            f"  Empty vals : {', '.join(self.empty_value_keys) or 'none'}",
        ]
        return "\n".join(lines)


def _detect_type(value: str) -> str:
    if value.lower() in ("true", "false"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def _find_duplicates(path: str) -> List[str]:
    seen: Dict[str, int] = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                seen[key] = seen.get(key, 0) + 1
    return [k for k, count in seen.items() if count > 1]


def profile_env_file(path: str) -> ProfileResult:
    parsed = parse_env_file(path)
    duplicates = _find_duplicates(path)
    empty_keys = [k for k, v in parsed.items() if v == ""]
    type_hints = {k: _detect_type(v) for k, v in parsed.items() if v != ""}
    return ProfileResult(
        path=path,
        total_keys=len(parsed),
        duplicate_keys=duplicates,
        empty_value_keys=empty_keys,
        type_hints=type_hints,
    )
