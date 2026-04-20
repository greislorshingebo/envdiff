"""Audit trail: record and replay diff operations with timestamps."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envdiff.comparator import DiffResult
from envdiff.exporter import to_dict


@dataclass
class AuditEntry:
    timestamp: str
    base_file: str
    compare_file: str
    total_keys: int
    missing_in_compare: int
    missing_in_base: int
    mismatched: int
    has_differences: bool
    label: Optional[str] = None


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def summary(self) -> str:
        lines = [f"Audit log: {len(self.entries)} record(s)"]
        for e in self.entries:
            tag = f" [{e.label}]" if e.label else ""
            diff_flag = "DIFF" if e.has_differences else "OK"
            lines.append(
                f"  {e.timestamp}{tag}  {e.base_file} vs {e.compare_file}  "
                f"keys={e.total_keys}  status={diff_flag}"
            )
        return "\n".join(lines)


def record_audit(result: DiffResult, base_file: str, compare_file: str,
                 label: Optional[str] = None) -> AuditEntry:
    data = to_dict(result)
    counts: dict = {s: 0 for s in ("ok", "missing_in_compare", "missing_in_base", "mismatch")}
    for e in data["entries"]:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        base_file=str(base_file),
        compare_file=str(compare_file),
        total_keys=len(data["entries"]),
        missing_in_compare=counts["missing_in_compare"],
        missing_in_base=counts["missing_in_base"],
        mismatched=counts["mismatch"],
        has_differences=data["has_differences"],
        label=label,
    )


def save_audit_log(log: AuditLog, path: os.PathLike) -> None:
    Path(path).write_text(
        json.dumps([asdict(e) for e in log.entries], indent=2), encoding="utf-8"
    )


def load_audit_log(path: os.PathLike) -> AuditLog:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return AuditLog(entries=[AuditEntry(**r) for r in raw])
