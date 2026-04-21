"""Tag entries in a DiffResult with arbitrary string labels."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, Iterable, List

from envdiff.comparator import DiffResult


@dataclass
class TagRule:
    """A glob pattern and the tag to apply when a key matches."""
    pattern: str
    tag: str


@dataclass
class TaggedEntry:
    key: str
    status: str          # ok | missing_in_compare | missing_in_base | mismatch
    base_value: object
    compare_value: object
    tags: List[str] = field(default_factory=list)


@dataclass
class TaggedResult:
    entries: List[TaggedEntry] = field(default_factory=list)

    def by_tag(self, tag: str) -> List[TaggedEntry]:
        """Return entries that carry *tag*."""
        return [e for e in self.entries if tag in e.tags]

    def all_tags(self) -> List[str]:
        """Sorted list of distinct tags present in the result."""
        tags: set[str] = set()
        for e in self.entries:
            tags.update(e.tags)
        return sorted(tags)


def _match_tags(key: str, rules: Iterable[TagRule]) -> List[str]:
    return [r.tag for r in rules if fnmatch(key, r.pattern)]


def tag_result(result: DiffResult, rules: Iterable[TagRule]) -> TaggedResult:
    """Apply *rules* to every entry in *result* and return a TaggedResult."""
    rules = list(rules)
    tagged: List[TaggedEntry] = []
    for entry in result.entries:
        tags = _match_tags(entry.key, rules)
        tagged.append(
            TaggedEntry(
                key=entry.key,
                status=entry.status,
                base_value=entry.base_value,
                compare_value=entry.compare_value,
                tags=tags,
            )
        )
    return TaggedResult(entries=tagged)


def rules_from_dict(mapping: Dict[str, str]) -> List[TagRule]:
    """Build rules from ``{pattern: tag}`` mapping (e.g. loaded from JSON)."""
    return [TagRule(pattern=k, tag=v) for k, v in mapping.items()]
