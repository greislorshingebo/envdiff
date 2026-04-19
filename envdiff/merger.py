"""Merge multiple .env files into a unified baseline or output."""

from __future__ import annotations

from typing import Dict, List, Optional


MergeStrategy = str  # 'first' | 'last' | 'union'


def merge_envs(
    envs: List[Dict[str, Optional[str]]],
    strategy: MergeStrategy = "last",
) -> Dict[str, Optional[str]]:
    """Merge a list of parsed env dicts into one.

    Strategies:
      first  – keep the first occurrence of each key.
      last   – later files override earlier ones (default).
      union  – include every key; conflicting values become None.
    """
    if not envs:
        return {}

    if strategy == "first":
        result: Dict[str, Optional[str]] = {}
        for env in envs:
            for key, value in env.items():
                if key not in result:
                    result[key] = value
        return result

    if strategy == "last":
        result = {}
        for env in envs:
            result.update(env)
        return result

    if strategy == "union":
        all_keys: set[str] = set()
        for env in envs:
            all_keys.update(env.keys())
        merged: Dict[str, Optional[str]] = {}
        for key in all_keys:
            values = [env[key] for env in envs if key in env]
            unique = set(values)
            merged[key] = values[0] if len(unique) == 1 else None
        return merged

    raise ValueError(f"Unknown merge strategy: {strategy!r}")


def merge_env_files(
    paths: List[str],
    strategy: MergeStrategy = "last",
) -> Dict[str, Optional[str]]:
    """Parse and merge .env files from disk."""
    from envdiff.parser import parse_env_file

    envs = [parse_env_file(p) for p in paths]
    return merge_envs(envs, strategy=strategy)
