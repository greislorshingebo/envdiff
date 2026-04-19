"""Annotate DiffResult entries with human-readable explanations."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
from envdiff.comparator import DiffResult


@dataclass
class AnnotatedEntry:
    key: str
    status: str
    base_value: str | None
    compare_value: str | None
    annotation: str


def _annotate(key: str, status: str, base: str | None, compare: str | None) -> str:
    if status == "ok":
        return f"'{key}' is present and identical in both files."
    if status == "missing_in_compare":
        return f"'{key}' exists in base but is absent from the compare file."
    if status == "missing_in_base":
        return f"'{key}' exists in compare but is absent from the base file."
    if status == "mismatch":
        return (
            f"'{key}' differs: base has {base!r}, compare has {compare!r}."
        )
    return f"'{key}' has unknown status '{status}'."


def annotate_result(result: DiffResult) -> List[AnnotatedEntry]:
    """Return a list of AnnotatedEntry for every entry in *result*."""
    annotated: List[AnnotatedEntry] = []
    for entry in result.entries:
        annotation = _annotate(
            entry.key, entry.status, entry.base_value, entry.compare_value
        )
        annotated.append(
            AnnotatedEntry(
                key=entry.key,
                status=entry.status,
                base_value=entry.base_value,
                compare_value=entry.compare_value,
                annotation=annotation,
            )
        )
    return annotated


def annotation_report(result: DiffResult) -> str:
    """Return a plain-text annotation report for *result*."""
    entries = annotate_result(result)
    if not entries:
        return "No entries to annotate."
    lines = [f"  [{e.status.upper()}] {e.annotation}" for e in entries]
    return "\n".join(lines)
