"""Patch an .env file by applying a dict of key->value updates."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PatchResult:
    updated: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.updated) + len(self.added)

    def summary(self) -> str:
        parts = []
        if self.updated:
            parts.append(f"{len(self.updated)} updated")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts) if parts else "no changes"


_KEY_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=')


def patch_env(
    source: str,
    patches: Dict[str, Optional[str]],
    *,
    add_missing: bool = True,
    overwrite: bool = True,
) -> tuple[str, PatchResult]:
    """Apply *patches* to the text of an .env file.

    Returns the patched text and a PatchResult describing what changed.
    """
    result = PatchResult()
    remaining = dict(patches)
    lines: List[str] = []

    for line in source.splitlines(keepends=True):
        m = _KEY_RE.match(line.lstrip())
        if m:
            key = m.group(1)
            if key in remaining:
                if overwrite:
                    val = remaining.pop(key)
                    new_val = "" if val is None else val
                    lines.append(f"{key}={new_val}\n")
                    result.updated.append(key)
                else:
                    remaining.pop(key)
                    result.skipped.append(key)
                    lines.append(line)
                continue
        lines.append(line)

    if add_missing:
        for key, val in remaining.items():
            new_val = "" if val is None else val
            lines.append(f"{key}={new_val}\n")
            result.added.append(key)
    else:
        result.skipped.extend(remaining.keys())

    return "".join(lines), result


def patch_env_file(
    path: Path,
    patches: Dict[str, Optional[str]],
    *,
    add_missing: bool = True,
    overwrite: bool = True,
) -> PatchResult:
    """Patch an .env file in-place and return a PatchResult."""
    source = path.read_text(encoding="utf-8")
    patched, result = patch_env(
        source, patches, add_missing=add_missing, overwrite=overwrite
    )
    path.write_text(patched, encoding="utf-8")
    return result
