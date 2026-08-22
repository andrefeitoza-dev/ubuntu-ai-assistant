from __future__ import annotations

from pathlib import Path

from ubuntu_ai.gui import launcher_installer


def test_user_paths_are_scoped_to_local_home(tmp_path: Path) -> None:
    launcher, desktop, icon = launcher_installer.user_paths(tmp_path)

    assert launcher == tmp_path / ".local/bin/ubuntu-ai-assistant"
    assert desktop == (tmp_path / ".local/share/applications/ubuntu-ai-assistant.desktop")
    assert icon == (tmp_path / ".local/share/icons/hicolor/512x512/apps/ubuntu-ai-assistant.png")


def test_write_launcher_creates_portable_executable(
    tmp_path: Path,
) -> None:
    launcher = tmp_path / ".local/bin/ubuntu-ai-assistant"
    executable = tmp_path / "venv/bin/ubuntu-ai-gui"

    launcher_installer.write_launcher(launcher, executable)

    content = launcher.read_text(encoding="utf-8")
    assert content.startswith("#!/usr/bin/env bash")
    assert 'exec "$GUI" "$@"' in content
    assert 'kill -USR1 "$PID"' in content
    assert "ubuntu-ai-assistant.lock" in content
    assert str(executable) in content
    assert "PROJECT=" not in content
    assert launcher.stat().st_mode & 0o111


def test_write_desktop_creates_valid_entry(tmp_path: Path) -> None:
    desktop = tmp_path / "ubuntu-ai-assistant.desktop"
    launcher = tmp_path / ".local/bin/ubuntu-ai-assistant"

    launcher_installer.write_desktop(desktop, launcher)

    content = desktop.read_text(encoding="utf-8")
    assert content.startswith("[Desktop Entry]")
    assert "Name=Ubuntu AI Assistant" in content
    assert "Icon=ubuntu-ai-assistant" in content
    assert f"Exec={launcher}" in content
    assert "Terminal=false" in content
    assert "StartupWMClass=UbuntuAIAssistant" in content
    assert "StartupNotify=false" in content


def test_install_creates_all_launcher_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    executable = tmp_path / "venv/bin/ubuntu-ai-gui"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\n", encoding="utf-8")

    monkeypatch.setattr(
        launcher_installer,
        "gui_executable",
        lambda: executable,
    )
    monkeypatch.setattr(
        launcher_installer,
        "refresh_desktop",
        lambda _home: None,
    )

    launcher_installer.install(tmp_path)

    launcher, desktop, icon = launcher_installer.user_paths(tmp_path)
    assert launcher.is_file()
    assert desktop.is_file()
    assert icon.is_file()
    assert str(executable) in launcher.read_text(encoding="utf-8")


def test_uninstall_removes_only_launcher_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    paths = launcher_installer.user_paths(tmp_path)

    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test", encoding="utf-8")

    untouched = tmp_path / "keep.txt"
    untouched.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(
        launcher_installer,
        "refresh_desktop",
        lambda _home: None,
    )

    launcher_installer.uninstall(tmp_path)

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
    assert launcher_installer.ICON_SOURCE == icon
