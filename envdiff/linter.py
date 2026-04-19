"""Lint .env files for common style and correctness issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line: int
    key: str | None
    code: str
    message: str


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.is_clean:
            return f"{self.path}: no issues found"
        lines = [f"{self.path}: {len(self.issues)} issue(s)"]
        for iss in self.issues:
            loc = f"line {iss.line}" if iss.line else "—"
            lines.append(f"  [{iss.code}] {loc}: {iss.message}")
        return "\n".join(lines)


def lint_env(path: str | Path) -> LintResult:
    p = Path(path)
    result = LintResult(path=str(p))
    seen_keys: dict[str, int] = {}

    with p.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if "=" not in line:
                result.issues.append(LintIssue(lineno, None, "E001", f"no '=' found: {line!r}"))
                continue

            key, _, value = line.partition("=")
            key = key.strip()

            if not key:
                result.issues.append(LintIssue(lineno, key, "E002", "empty key"))
                continue

            if key != key.upper():
                result.issues.append(LintIssue(lineno, key, "W001", f"key '{key}' is not uppercase"))

            if " " in key:
                result.issues.append(LintIssue(lineno, key, "E003", f"key '{key}' contains spaces"))

            if key in seen_keys:
                result.issues.append(LintIssue(lineno, key, "W002",
                    f"duplicate key '{key}' (first seen on line {seen_keys[key]})"))
            else:
                seen_keys[key] = lineno

            if value != value.strip():
                result.issues.append(LintIssue(lineno, key, "W003",
                    f"value for '{key}' has leading/trailing whitespace"))

    return result
