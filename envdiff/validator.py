"""Validate .env files against a schema of required and optional keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    type_errors: Dict[str, str] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not (self.missing_required or self.type_errors)

    def summary(self) -> str:
        parts = []
        if self.missing_required:
            parts.append(f"{len(self.missing_required)} missing required key(s)")
        if self.type_errors:
            parts.append(f"{len(self.type_errors)} type error(s)")
        if self.unknown_keys:
            parts.append(f"{len(self.unknown_keys)} unknown key(s)")
        return ", ".join(parts) if parts else "valid"


@dataclass
class KeySchema:
    required: bool = True
    expected_type: Optional[str] = None  # "int", "bool", "url", or None


SCHEMA = Dict[str, KeySchema]

_TYPE_CHECKS = {
    "int": lambda v: v.lstrip("-").isdigit(),
    "bool": lambda v: v.lower() in ("true", "false", "1", "0", "yes", "no"),
    "url": lambda v: v.startswith(("http://", "https://")),
}


def validate_env(env: Dict[str, str], schema: SCHEMA) -> ValidationResult:
    result = ValidationResult()
    required_keys: Set[str] = {k for k, s in schema.items() if s.required}
    present = set(env.keys())

    result.missing_required = sorted(required_keys - present)
    result.unknown_keys = sorted(present - set(schema.keys()))

    for key, value in env.items():
        spec = schema.get(key)
        if spec and spec.expected_type:
            checker = _TYPE_CHECKS.get(spec.expected_type)
            if checker and not checker(value):
                result.type_errors[key] = (
                    f"expected {spec.expected_type}, got {value!r}"
                )

    return result
