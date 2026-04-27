"""Deduplicator: merge duplicate keys across multiple env dicts using a chosen strategy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass over a merged env mapping."""

    original: Dict[str, List[Optional[str]]]
    """Key -> all values seen (in order)."""
    deduped: Dict[str, Optional[str]]
    """Key -> single resolved value."""
    conflicts: Dict[str, List[Optional[str]]] = field(default_factory=dict)
    """Keys where more than one *distinct* value was found."""

    # ------------------------------------------------------------------ #
    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)

    @property
    def has_conflicts(self) -> bool:
        return self.conflict_count > 0

    def summary(self) -> str:
        total = len(self.deduped)
        return (
            f"{total} key(s) after dedup; "
            f"{self.conflict_count} conflict(s) resolved."
        )


def _collect(envs: List[Dict[str, Optional[str]]]) -> Dict[str, List[Optional[str]]]:
    """Gather all values for every key across *envs*."""
    collected: Dict[str, List[Optional[str]]] = {}
    for env in envs:
        for k, v in env.items():
            collected.setdefault(k, []).append(v)
    return collected


def deduplicate(
    envs: List[Dict[str, Optional[str]]],
    strategy: str = "first",
) -> DeduplicateResult:
    """Deduplicate keys across *envs*.

    Parameters
    ----------
    envs:
        Ordered list of env dicts (e.g. from ``parse_env_file``).
    strategy:
        ``"first"``  – keep the first value encountered.
        ``"last"``   – keep the last value encountered.
        ``"longest"``– keep the longest string value; falls back to first.
    """
    if strategy not in {"first", "last", "longest"}:
        raise ValueError(f"Unknown strategy {strategy!r}; choose first/last/longest.")

    original = _collect(envs)
    deduped: Dict[str, Optional[str]] = {}
    conflicts: Dict[str, List[Optional[str]]] = {}

    for key, values in original.items():
        distinct = list(dict.fromkeys(values))  # stable-unique
        if len(distinct) > 1:
            conflicts[key] = distinct

        if strategy == "first":
            deduped[key] = values[0]
        elif strategy == "last":
            deduped[key] = values[-1]
        else:  # longest
            deduped[key] = max(
                (v for v in values if v is not None),
                key=len,
                default=values[0],
            )

    return DeduplicateResult(original=original, deduped=deduped, conflicts=conflicts)
