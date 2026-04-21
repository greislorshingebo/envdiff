"""Rename keys across one or more parsed env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameResult:
    """Outcome of applying a rename map to an env dict."""

    env: Dict[str, Optional[str]]
    renamed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def rename_count(self) -> int:
        return len(self.renamed)

    @property
    def skip_count(self) -> int:
        return len(self.skipped)

    def summary(self) -> str:
        parts = [f"{self.rename_count} key(s) renamed"]
        if self.skipped:
            parts.append(f"{self.skip_count} key(s) not found (skipped)")
        return ", ".join(parts) + "."


def rename_keys(
    env: Dict[str, Optional[str]],
    rename_map: Dict[str, str],
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Return a new env dict with keys renamed according to *rename_map*.

    Args:
        env:        Source env mapping (key -> value).
        rename_map: Mapping of old_key -> new_key.
        overwrite:  When *True*, replace an existing new_key if present.
                    When *False* (default), skip the rename if new_key already
                    exists in *env*.

    Returns:
        A :class:`RenameResult` containing the updated env and bookkeeping.
    """
    result: Dict[str, Optional[str]] = dict(env)
    renamed: List[str] = []
    skipped: List[str] = []

    for old_key, new_key in rename_map.items():
        if old_key not in result:
            skipped.append(old_key)
            continue
        if new_key in result and not overwrite:
            skipped.append(old_key)
            continue
        result[new_key] = result.pop(old_key)
        renamed.append(old_key)

    return RenameResult(env=result, renamed=renamed, skipped=skipped)


def rename_env_files(
    envs: Dict[str, Dict[str, Optional[str]]],
    rename_map: Dict[str, str],
    *,
    overwrite: bool = False,
) -> Dict[str, RenameResult]:
    """Apply *rename_keys* to each env in a label -> env mapping."""
    return {
        label: rename_keys(env, rename_map, overwrite=overwrite)
        for label, env in envs.items()
    }
