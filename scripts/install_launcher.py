#!/usr/bin/env python3
"""Instala ou remove o launcher desktop do Ubuntu AI Assistant."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ID = "ubuntu-ai-assistant"
ICON_SOURCE = PROJECT_ROOT / "src" / "ubuntu_ai" / "gui" / "assets" / f"{APP_ID}.png"


def user_paths(home: Path) -> tuple[Path, Path, Path]:
    launcher = home / ".local" / "bin" / APP_ID
    desktop = home / ".local" / "share" / "applications" / f"{APP_ID}.desktop"
    icon = home / ".local" / "share" / "icons" / "hicolor" / "512x512" / "apps" / f"{APP_ID}.png"
    return launcher, desktop, icon


def gui_executable() -> Path:
    candidate = Path(sys.executable).resolve().parent / "ubuntu-ai-gui"
    if candidate.is_file():
        return candidate

    discovered = shutil.which("ubuntu-ai-gui")
    if discovered:
        return Path(discovered).resolve()

    raise SystemExit(
        "Entry point ubuntu-ai-gui não encontrado. "
        "Execute o instalador com: uv run python scripts/install_launcher.py"
    )


def write_launcher(path: Path, executable: Path) -> None:
    project = shlex.quote(str(PROJECT_ROOT))
    gui = shlex.quote(str(executable))

    content = f"""#!/usr/bin/env bash
set -euo pipefail

PROJECT={project}
GUI={gui}

cd "$PROJECT"
exec "$GUI" "$@"
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def write_desktop(path: Path, launcher: Path) -> None:
    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Ubuntu AI Assistant
Icon={APP_ID}
Comment=Assistente inteligente para Ubuntu
Exec={launcher}
Terminal=false
Categories=Utility;System;
StartupNotify=true
StartupWMClass=Ubuntu AI Assistant
Keywords=Ubuntu;AI;Assistant;Linux;
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def refresh_desktop(home: Path) -> None:
    commands = (
        (
            "update-desktop-database",
            str(home / ".local" / "share" / "applications"),
        ),
        (
            "gtk-update-icon-cache",
            "-f",
            "-t",
            str(home / ".local" / "share" / "icons" / "hicolor"),
        ),
    )

    for command in commands:
        if shutil.which(command[0]):
            subprocess.run(
                command,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def install(home: Path) -> None:
    if not ICON_SOURCE.is_file():
        raise SystemExit(f"Ícone não encontrado: {ICON_SOURCE}")

    launcher, desktop, icon = user_paths(home)
    executable = gui_executable()

    icon.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ICON_SOURCE, icon)
    write_launcher(launcher, executable)
    write_desktop(desktop, launcher)
    refresh_desktop(home)

    print("Launcher instalado com sucesso.")
    print(f"Aplicativo: {desktop}")
    print(f"Executável: {launcher}")
    print(f"Ícone: {icon}")


def uninstall(home: Path) -> None:
    launcher, desktop, icon = user_paths(home)

    for path in (desktop, launcher, icon):
        path.unlink(missing_ok=True)

    refresh_desktop(home)
    print("Launcher removido com sucesso.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Instala o launcher desktop do Ubuntu AI Assistant."
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove o launcher e o ícone instalados.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    home = Path.home()

    if args.uninstall:
        uninstall(home)
    else:
        install(home)


if __name__ == "__main__":
    main()
