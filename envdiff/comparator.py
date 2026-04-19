"""Core comparison logic for envdiff."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple


@dataclass
class DiffResult:
    missing_in_compare: Set[str] = field(default_factory=set)
    missing_in_base: Set[str] = field(default_factory=set)
    mismatched: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_in_compare or self.missing_in_base or self.mismatched)

    def summary(self) -> str:
        parts = []
        if self.missing_in_compare:
            parts.append(f"{len(self.missing_in_compare)} missing in compare")
        if self.missing_in_base:
            parts.append(f"{len(self.missing_in_base)} missing in base")
        if self.mismatched:
            parts.append(f"{len(self.mismatched)} mismatched")
        return ", ".join(parts) if parts else "No differences"


def has_differences(result: DiffResult) -> bool:
    """Return True when the result contains any differences."""
    return result.has_differences


def summary(result: DiffResult) -> str:
    """Return a short summary string for *result*."""
    return result.summary()


def compare_envs(
    base: Dict[str, str],
    compare: Dict[str, str],
    check_values: bool = True,
) -> DiffResult:
    """Compare two env dictionaries and return a DiffResult."""
    base_keys = set(base)
    compare_keys = set(compare)

    missing_in_compare = base_keys - compare_keys
    missing_in_base = compare_keys - base_keys
    mismatched: Dict[str, Tuple[str, str]] = {}

    if check_values:
        for key in base_keys & compare_keys:
            if base[key] != compare[key]:
                mismatched[key] = (base[key], compare[key])

    return DiffResult(
        missing_in_compare=missing_in_compare,
        missing_in_base=missing_in_base,
        mismatched=mismatched,
    )
