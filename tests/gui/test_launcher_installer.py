from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "install_launcher.py"
SPEC = importlib.util.spec_from_file_location("install_launcher", SCRIPT)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Não foi possível carregar scripts/install_launcher.py")

install_launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = install_launcher
SPEC.loader.exec_module(install_launcher)


def test_user_paths_are_scoped_to_local_home(tmp_path: Path) -> None:
    launcher, desktop, icon = install_launcher.user_paths(tmp_path)

    assert launcher == tmp_path / ".local/bin/ubuntu-ai-assistant"
    assert desktop == (tmp_path / ".local/share/applications/ubuntu-ai-assistant.desktop")
    assert icon == (tmp_path / ".local/share/icons/hicolor/512x512/apps/ubuntu-ai-assistant.png")


def test_write_launcher_creates_executable_script(tmp_path: Path) -> None:
    launcher = tmp_path / ".local/bin/ubuntu-ai-assistant"
    executable = tmp_path / "venv/bin/ubuntu-ai-gui"

    install_launcher.write_launcher(launcher, executable)

    content = launcher.read_text(encoding="utf-8")
    assert content.startswith("#!/usr/bin/env bash")
    assert 'cd "$PROJECT"' in content
    assert 'exec "$GUI" "$@"' in content
    assert str(executable) in content
    assert launcher.stat().st_mode & 0o111


def test_write_desktop_creates_valid_entry(tmp_path: Path) -> None:
    desktop = tmp_path / "ubuntu-ai-assistant.desktop"
    launcher = tmp_path / ".local/bin/ubuntu-ai-assistant"

    install_launcher.write_desktop(desktop, launcher)

    content = desktop.read_text(encoding="utf-8")
    assert content.startswith("[Desktop Entry]")
    assert "Name=Ubuntu AI Assistant" in content
    assert "Icon=ubuntu-ai-assistant" in content
    assert f"Exec={launcher}" in content
    assert "Terminal=false" in content
    assert "StartupWMClass=Ubuntu AI Assistant" in content


def test_uninstall_removes_only_launcher_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    paths = install_launcher.user_paths(tmp_path)

    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test", encoding="utf-8")

    untouched = tmp_path / "keep.txt"
    untouched.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(install_launcher, "refresh_desktop", lambda _home: None)

    install_launcher.uninstall(tmp_path)

    assert all(not path.exists() for path in paths)
    assert untouched.read_text(encoding="utf-8") == "keep"


def test_gui_icon_is_packaged_and_valid_png() -> None:
    icon = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "ubuntu_ai"
        / "gui"
        / "assets"
        / "ubuntu-ai-assistant.png"
    )

    assert icon.is_file()
    assert icon.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert install_launcher.ICON_SOURCE == icon
