"""masker.py – selectively mask env values based on key patterns or explicit lists."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Optional

# Default patterns treated as sensitive (case-insensitive match on key name)
_DEFAULT_PATTERNS: list[str] = [
    r"pass(word)?",
    r"secret",
    r"token",
    r"api[_\-]?key",
    r"private[_\-]?key",
    r"auth",
    r"credential",
    r"cert",
    r"salt",
]

MASK_PLACEHOLDER = "***"


@dataclass
class MaskOptions:
    """Configuration for the masking pass."""
    patterns: list[str] = field(default_factory=lambda: list(_DEFAULT_PATTERNS))
    explicit_keys: list[str] = field(default_factory=list)
    placeholder: str = MASK_PLACEHOLDER
    case_sensitive: bool = False


def _compile_patterns(patterns: Iterable[str], case_sensitive: bool) -> list[re.Pattern]:
    flags = 0 if case_sensitive else re.IGNORECASE
    return [re.compile(rf"^{p}$", flags) for p in patterns]


def should_mask(key: str, options: Optional[MaskOptions] = None) -> bool:
    """Return True if *key* should be masked according to *options*."""
    opts = options or MaskOptions()
    if key in opts.explicit_keys:
        return True
    compiled = _compile_patterns(opts.patterns, opts.case_sensitive)
    return any(pat.search(key) for pat in compiled)


def mask_env(
    env: dict[str, Optional[str]],
    options: Optional[MaskOptions] = None,
) -> dict[str, Optional[str]]:
    """Return a copy of *env* with sensitive values replaced by the placeholder."""
    opts = options or MaskOptions()
    return {
        k: (opts.placeholder if should_mask(k, opts) else v)
        for k, v in env.items()
    }


def masked_keys(env: dict[str, Optional[str]], options: Optional[MaskOptions] = None) -> list[str]:
    """Return sorted list of keys that would be masked."""
    opts = options or MaskOptions()
    return sorted(k for k in env if should_mask(k, opts))
