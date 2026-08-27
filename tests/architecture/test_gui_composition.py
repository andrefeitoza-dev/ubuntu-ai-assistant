from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_gui_architecture_guard_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_gui_architecture.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "GUI architecture checks passed" in result.stdout


def test_gui_app_remains_within_size_budget() -> None:
    source = Path("src/ubuntu_ai/gui/app.py").read_text(encoding="utf-8")

    assert len(source.splitlines()) <= 1400
