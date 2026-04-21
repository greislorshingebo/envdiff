"""Group DiffResult entries by prefix, status, or custom pattern."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class GroupedResult:
    """Mapping of group label -> list of entry dicts."""
    groups: Dict[str, List[dict]] = field(default_factory=dict)

    def labels(self) -> List[str]:
        return sorted(self.groups.keys())

    def get(self, label: str) -> List[dict]:
        return self.groups.get(label, [])

    def total(self) -> int:
        return sum(len(v) for v in self.groups.values())


def _entry_prefix(key: str, sep: str = "_") -> str:
    """Return the first segment of a key split by *sep*, or the key itself."""
    parts = key.split(sep, 1)
    return parts[0] if len(parts) > 1 else key


def group_by_prefix(
    result: DiffResult,
    sep: str = "_",
) -> GroupedResult:
    """Group entries by the prefix of each key (e.g. DB_HOST -> DB)."""
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for entry in result.entries:
        prefix = _entry_prefix(entry["key"], sep)
        buckets[prefix].append(entry)
    return GroupedResult(groups=dict(buckets))


def group_by_status(result: DiffResult) -> GroupedResult:
    """Group entries by their status string (ok / missing_in_compare / etc.)."""
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for entry in result.entries:
        buckets[entry["status"]].append(entry)
    return GroupedResult(groups=dict(buckets))


def group_by_custom(
    result: DiffResult,
    key_fn: Callable[[str], str],
) -> GroupedResult:
    """Group entries using an arbitrary callable that maps key -> group label."""
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for entry in result.entries:
        label = key_fn(entry["key"])
        buckets[label].append(entry)
    return GroupedResult(groups=dict(buckets))
