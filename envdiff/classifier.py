"""Classify env entries into semantic categories based on key naming conventions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

# Category patterns: (category_name, compiled_regex)
_CATEGORY_PATTERNS: List[tuple[str, re.Pattern]] = [
    ("database",  re.compile(r"(DB|DATABASE|POSTGRES|MYSQL|MONGO|REDIS|SQLITE)", re.I)),
    ("auth",      re.compile(r"(AUTH|JWT|OAUTH|SECRET|PASSWORD|PASSWD|TOKEN|API_KEY)", re.I)),
    ("network",   re.compile(r"(HOST|PORT|URL|URI|ENDPOINT|DOMAIN|ADDR)", re.I)),
    ("logging",   re.compile(r"(LOG|LOGGING|SENTRY|DATADOG|NEWRELIC)", re.I)),
    ("feature",   re.compile(r"(FEATURE|FLAG|TOGGLE|ENABLE|DISABLE)", re.I)),
    ("storage",   re.compile(r"(S3|BUCKET|STORAGE|GCS|BLOB|MINIO)", re.I)),
    ("email",     re.compile(r"(MAIL|EMAIL|SMTP|SENDGRID|MAILGUN)", re.I)),
    ("app",       re.compile(r"(APP|ENV|ENVIRONMENT|DEBUG|VERSION|RELEASE|SERVICE)", re.I)),
]

UNCATEGORIZED = "uncategorized"


def classify_key(key: str) -> str:
    """Return the category name for a single env key."""
    for category, pattern in _CATEGORY_PATTERNS:
        if pattern.search(key):
            return category
    return UNCATEGORIZED


@dataclass
class ClassifiedResult:
    """Mapping of category -> list of keys belonging to that category."""
    _data: Dict[str, List[str]] = field(default_factory=dict)

    def add(self, key: str, category: str) -> None:
        self._data.setdefault(category, []).append(key)

    def categories(self) -> List[str]:
        return sorted(self._data.keys())

    def keys_for(self, category: str) -> List[str]:
        return sorted(self._data.get(category, []))

    def as_dict(self) -> Dict[str, List[str]]:
        return {cat: self.keys_for(cat) for cat in self.categories()}

    def summary(self) -> str:
        lines = []
        for cat in self.categories():
            keys = self.keys_for(cat)
            lines.append(f"{cat}: {len(keys)} key(s)")
        return "\n".join(lines) if lines else "No keys classified."


def classify_env(env: Dict[str, Optional[str]]) -> ClassifiedResult:
    """Classify all keys in an env dict and return a ClassifiedResult."""
    result = ClassifiedResult()
    for key in env:
        category = classify_key(key)
        result.add(key, category)
    return result
