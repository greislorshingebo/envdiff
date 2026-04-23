"""Pin current env values as expected values, and detect drift from pinned state."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class PinEntry:
    key: str
    pinned_value: Optional[str]
    current_value: Optional[str]

    @property
    def drifted(self) -> bool:
        return self.pinned_value != self.current_value


@dataclass
class PinReport:
    entries: List[PinEntry] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return any(e.drifted for e in self.entries)

    @property
    def drifted_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.drifted]

    def summary(self) -> str:
        total = len(self.entries)
        drift = len(self.drifted_keys)
        return f"{drift}/{total} keys drifted from pinned values."


def pin_env(env: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Return a snapshot dict suitable for saving as a pin file."""
    return dict(env)


def save_pin(pin: Dict[str, Optional[str]], path: Path) -> None:
    path.write_text(json.dumps(pin, indent=2, default=str), encoding="utf-8")


def load_pin(path: Path) -> Dict[str, Optional[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: (v if v is not None else None) for k, v in data.items()}


def check_drift(
    pin: Dict[str, Optional[str]],
    current: Dict[str, Optional[str]],
) -> PinReport:
    """Compare pinned values against current env; report any drift."""
    all_keys = sorted(set(pin) | set(current))
    entries = [
        PinEntry(
            key=k,
            pinned_value=pin.get(k),
            current_value=current.get(k),
        )
        for k in all_keys
    ]
    return PinReport(entries=entries)


def check_drift_files(pin_path: Path, env_path: Path) -> PinReport:
    pin = load_pin(pin_path)
    current = parse_env_file(env_path)
    return check_drift(pin, current)
