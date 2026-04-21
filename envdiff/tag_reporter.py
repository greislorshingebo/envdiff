"""Plain-text and summary reporters for TaggedResult."""
from __future__ import annotations

from typing import List

from envdiff.tagger import TaggedEntry, TaggedResult

_STATUS_SYMBOL = {
    "ok": "✔",
    "mismatch": "≠",
    "missing_in_compare": "→",
    "missing_in_base": "←",
}


def _fmt_entry(entry: TaggedEntry) -> str:
    symbol = _STATUS_SYMBOL.get(entry.status, "?")
    tag_str = ",".join(sorted(entry.tags)) if entry.tags else "-"
    return f"  {symbol} {entry.key:<30} [{tag_str}]"


def report_tagged_plain(tagged: TaggedResult) -> str:
    """Return a plain multi-line string listing every entry with its tags."""
    lines: List[str] = ["Tagged diff entries:", ""]
    if not tagged.entries:
        lines.append("  (no entries)")
    else:
        for entry in tagged.entries:
            lines.append(_fmt_entry(entry))
    return "\n".join(lines)


def report_tagged_by_tag(tagged: TaggedResult) -> str:
    """Group entries by tag and return a section-per-tag plain report."""
    lines: List[str] = []
    all_tags = tagged.all_tags()
    if not all_tags:
        lines.append("No tags defined.")
        return "\n".join(lines)

    for tag in all_tags:
        lines.append(f"[{tag}]")
        for entry in tagged.by_tag(tag):
            lines.append(_fmt_entry(entry))
        lines.append("")

    untagged = [e for e in tagged.entries if not e.tags]
    if untagged:
        lines.append("[untagged]")
        for entry in untagged:
            lines.append(_fmt_entry(entry))

    return "\n".join(lines)


def report_tagged_summary(tagged: TaggedResult) -> str:
    """One-line summary: total entries, distinct tags, untagged count."""
    total = len(tagged.entries)
    n_tags = len(tagged.all_tags())
    untagged = sum(1 for e in tagged.entries if not e.tags)
    return (
        f"Total entries: {total} | "
        f"Distinct tags: {n_tags} | "
        f"Untagged: {untagged}"
    )
