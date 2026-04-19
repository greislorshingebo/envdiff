"""Formatting utilities for envdiff output."""
from __future__ import annotations
from typing import Dict, List, Optional


KEY_WIDTH = 32


def format_key_status(
    key: str,
    status: str,
    base_value: Optional[str] = None,
    compare_value: Optional[str] = None,
) -> str:
    """Return a single formatted line describing a key's diff status."""
    padded = key.ljust(KEY_WIDTH)
    if status == "missing_in_compare":
        return f"  - {padded} [only in base]"
    if status == "missing_in_base":
        return f"  + {padded} [only in compare]"
    if status == "mismatch":
        return (
            f"  ~ {padded} "
            f"base={_quote(base_value)}  compare={_quote(compare_value)}"
        )
    return f"    {padded} [ok]"


def format_section_header(base_path: str, compare_path: str) -> str:
    """Return a header line for a diff section."""
    return f"Comparing: {base_path}  <>  {compare_path}"


def format_summary_line(missing_in_compare: int, missing_in_base: int, mismatched: int) -> str:
    """Return a human-readable summary line."""
    parts: List[str] = []
    if missing_in_compare:
        parts.append(f"{missing_in_compare} missing in compare")
    if missing_in_base:
        parts.append(f"{missing_in_base} missing in base")
    if mismatched:
        parts.append(f"{mismatched} mismatched")
    if not parts:
        return "No differences found."
    return "Issues: " + ", ".join(parts) + "."


def _quote(value: Optional[str]) -> str:
    if value is None:
        return "<missing>"
    return f'"{value}"'
