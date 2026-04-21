"""Tests for envdiff.duplicate_cli."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.duplicate_cli import main


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content, encoding="utf-8")
    return p


def test_exits_zero_no_duplicates(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "FOO=bar\nBAZ=qux\n")
    main([str(p)])


def test_exits_zero_without_flag_even_when_duplicates(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "FOO=1\nFOO=2\n")
    main([str(p)])  # should not raise SystemExit


def test_exits_one_with_exit_code_flag(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "KEY=1\nKEY=2\n")
    with pytest.raises(SystemExit) as exc_info:
        main(["--exit-code", str(p)])
    assert exc_info.value.code == 1


def test_exits_zero_exit_code_flag_no_duplicates(env_dir: Path) -> None:
    p = _write(env_dir, ".env", "ONLY=once\n")
    main(["--exit-code", str(p)])  # should not raise


def test_missing_file_exits_two(env_dir: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main([str(env_dir / "missing.env")])
    assert exc_info.value.code == 2


def test_multiple_files_one_clean_one_dirty(env_dir: Path) -> None:
    clean = _write(env_dir, "clean.env", "A=1\n")
    dirty = _write(env_dir, "dirty.env", "B=1\nB=2\n")
    with pytest.raises(SystemExit) as exc_info:
        main(["--exit-code", str(clean), str(dirty)])
    assert exc_info.value.code == 1


def test_quiet_flag_accepted(env_dir: Path, capsys: pytest.CaptureFixture) -> None:
    p = _write(env_dir, ".env", "DUP=a\nDUP=b\n")
    main(["--quiet", str(p)])
    captured = capsys.readouterr()
    # summary line should still appear
    assert "DUP" in captured.out
    # but per-key detail lines should not
    lines = [ln for ln in captured.out.splitlines() if ln.startswith("  ")]
    assert lines == []
