"""Parser for .env files."""

import re
from pathlib import Path


ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)


def parse_env_file(path: str | Path) -> dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    - Ignores blank lines and comment lines (starting with #).
    - Strips optional surrounding quotes from values.
    - Raises FileNotFoundError if the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    result: dict[str, str] = {}

    with path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()

            # Skip blanks and comments
            if not line or line.startswith("#"):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                # Silently skip malformed lines (export keyword, etc.)
                continue

            key = match.group("key")
            value = match.group("value").strip()

            # Strip matching surrounding quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
                value = value[1:-1]

            result[key] = value

    return result
