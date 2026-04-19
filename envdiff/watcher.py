"""Watch .env files for changes and report diffs automatically."""

import time
import os
from typing import Callable, Dict, List, Optional

from envdiff.parser import parse_env_file
from envdiff.comparator import compare


class FileWatcher:
    """Watches a set of .env files and triggers a callback on change."""

    def __init__(self, paths: List[str], callback: Callable[[str, object], None]):
        self.paths = paths
        self.callback = callback
        self._mtimes: Dict[str, float] = {}

    def _get_mtime(self, path: str) -> Optional[float]:
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return None

    def _snapshot(self) -> Dict[str, Optional[float]]:
        return {p: self._get_mtime(p) for p in self.paths}

    def start(self, base_path: str, interval: float = 1.0, max_cycles: Optional[int] = None) -> None:
        """Poll files every `interval` seconds. Compare changed files against base_path."""
        self._mtimes = self._snapshot()
        cycles = 0
        while True:
            time.sleep(interval)
            current = self._snapshot()
            for path in self.paths:
                if path == base_path:
                    continue
                if current[path] != self._mtimes.get(path):
                    try:
                        base = parse_env_file(base_path)
                        changed = parse_env_file(path)
                        result = compare(base, changed)
                        self.callback(path, result)
                    except Exception as exc:  # noqa: BLE001
                        self.callback(path, exc)
                    self._mtimes[path] = current[path]
            cycles += 1
            if max_cycles is not None and cycles >= max_cycles:
                break
