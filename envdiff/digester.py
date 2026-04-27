"""Compute and compare cryptographic digests of .env files for change detection."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from envdiff.parser import parse_env_file


def _hash_env(env: Dict[str, Optional[str]]) -> str:
    """Return a stable SHA-256 hex digest of a parsed env dict."""
    # Sort keys for determinism; encode both key and value
    canonical = json.dumps(
        {k: (v if v is not None else "") for k, v in sorted(env.items())},
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class DigestEntry:
    path: str
    digest: str


@dataclass
class DigestReport:
    entries: list[DigestEntry] = field(default_factory=list)

    @property
    def all_match(self) -> bool:
        """True when every file shares the same digest."""
        digests = {e.digest for e in self.entries}
        return len(digests) <= 1

    @property
    def unique_digests(self) -> int:
        return len({e.digest for e in self.entries})

    def summary(self) -> str:
        if not self.entries:
            return "No files digested."
        if self.all_match:
            return f"All {len(self.entries)} file(s) are identical (digest: {self.entries[0].digest[:12]}…)."
        return (
            f"{len(self.entries)} file(s) checked; "
            f"{self.unique_digests} unique digest(s) — files differ."
        )


def digest_file(path: str | Path) -> DigestEntry:
    """Parse a single .env file and return its DigestEntry."""
    env = parse_env_file(str(path))
    return DigestEntry(path=str(path), digest=_hash_env(env))


def digest_files(*paths: str | Path) -> DigestReport:
    """Digest multiple .env files and return a DigestReport."""
    entries = [digest_file(p) for p in paths]
    return DigestReport(entries=entries)
