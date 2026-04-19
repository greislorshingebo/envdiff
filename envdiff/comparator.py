"""Core comparison logic for envdiff."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the result of comparing two .env files."""
    base_file: str
    compare_file: str
    missing_in_compare: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_compare
            or self.missing_in_base
            or self.mismatched
        )

    def summary(self) -> str:
        lines = [f"Comparing '{self.base_file}' vs '{self.compare_file}':"]
        if not self.has_differences:
            lines.append("  No differences found.")
            return "\n".join(lines)
        if self.missing_in_compare:
            lines.append(f"  Missing in '{self.compare_file}':")
            for key in sorted(self.missing_in_compare):
                lines.append(f"    - {key}")
        if self.missing_in_base:
            lines.append(f"  Missing in '{self.base_file}':")
            for key in sorted(self.missing_in_base):
                lines.append(f"    - {key}")
        if self.mismatched:
            lines.append("  Mismatched values:")
            for key in sorted(self.mismatched):
                base_val, cmp_val = self.mismatched[key]
                lines.append(f"    ~ {key}: '{base_val}' != '{cmp_val}'")
        return "\n".join(lines)


def compare_envs(
    base: Dict[str, Optional[str]],
    compare: Dict[str, Optional[str]],
    base_file: str = "base",
    compare_file: str = "compare",
    check_values: bool = True,
) -> DiffResult:
    """Compare two parsed env dicts and return a DiffResult."""
    result = DiffResult(base_file=base_file, compare_file=compare_file)
    base_keys = set(base.keys())
    compare_keys = set(compare.keys())

    result.missing_in_compare = list(base_keys - compare_keys)
    result.missing_in_base = list(compare_keys - base_keys)

    if check_values:
        for key in base_keys & compare_keys:
            if base[key] != compare[key]:
                result.mismatched[key] = (base[key], compare[key])

    return result
