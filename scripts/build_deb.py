from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ID = "ubuntu-ai-assistant"
INSTALL_ROOT = Path("opt") / APP_ID / "lib"
RUNTIME_ROOT = Path("opt") / APP_ID / "runtime"
REQUIRED_COMMANDS = ("dpkg-deb", "uv")


def project_version() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(project["project"]["version"])


def detect_architecture() -> str:
    result = subprocess.run(
        ("dpkg", "--print-architecture"),
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    )
    architecture = result.stdout.strip()
    if not architecture:
        raise RuntimeError("Não foi possível detectar a arquitetura Debian.")
    return architecture


def control_text(version: str, architecture: str) -> str:
    return f"""Package: {APP_ID}
Version: {version}
Section: utils
Priority: optional
Architecture: {architecture}
Depends: libc6 (>= 2.35), libx11-6, libxext6, libxrender1, libxft2, libfontconfig1
Maintainer: Andre Anderson Feitoza
Homepage: https://github.com/andrefeitoza-dev/ubuntu-ai-assistant
Description: Assistente local e seguro para administração do Ubuntu
 Plataforma multiagente com interface gráfica, contexto local e suporte SSH.
"""


def pre_install_text() -> str:
    return f"""#!/usr/bin/env bash
set -e
if [ "${{1:-}}" = "upgrade" ] && [ -d "/opt/{APP_ID}" ]; then
    rm -rf -- "/opt/{APP_ID}"
fi
"""


def wrapper(command: str, interpreter: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="/opt/{APP_ID}/lib${{PYTHONPATH:+:$PYTHONPATH}}"
exec "{interpreter}" "/opt/{APP_ID}/lib/bin/{command}" "$@"
"""


def rewrite_entrypoint_shebangs(directory: Path, interpreter: str) -> None:
    """Substitui caminhos temporários pelos caminhos finais do pacote."""

    if not directory.is_dir():
        raise RuntimeError("Diretório de entry points Python não encontrado.")
    for entrypoint in directory.iterdir():
        if not entrypoint.is_file():
            continue
        try:
            text = entrypoint.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not text.startswith("#!"):
            continue
        _first_line, separator, remainder = text.partition("\n")
        entrypoint.write_text(
            f"#!{interpreter}{separator}{remainder}",
            encoding="utf-8",
        )


def desktop_text() -> str:
    return f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Ubuntu AI Assistant
Comment=Assistente inteligente para Ubuntu
Exec=/usr/bin/ubuntu-ai-gui
Icon={APP_ID}
Terminal=false
Categories=Utility;System;
StartupNotify=false
StartupWMClass=UbuntuAIAssistant
Keywords=Ubuntu;AI;Assistant;Linux;
"""


def write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def build_package(wheel: Path, output: Path, architecture: str) -> Path:
    version = project_version()
    expected_wheel = f"ubuntu_ai_assistant-{version}-py3-none-any.whl"
    if wheel.name != expected_wheel or not wheel.is_file():
        raise ValueError(f"Wheel obrigatório: {expected_wheel}")
    for command in REQUIRED_COMMANDS:
        if not shutil.which(command):
            raise RuntimeError(f"Comando necessário não encontrado: {command}")

    output.mkdir(parents=True, exist_ok=True)
    destination = output / f"{APP_ID}_{version}_{architecture}.deb"

    with tempfile.TemporaryDirectory(prefix="ubuntu-ai-deb-") as temporary:
        staging = Path(temporary) / "package"
        library = staging / INSTALL_ROOT
        library.mkdir(parents=True)

        runtime_install = staging / RUNTIME_ROOT
        subprocess.run(
            (
                "uv",
                "python",
                "install",
                "3.12",
                "--managed-python",
                "--no-bin",
                "--install-dir",
                str(runtime_install),
            ),
            check=True,
            shell=False,
        )
        runtimes = sorted(runtime_install.glob("cpython-3.12.*-linux-x86_64-gnu"))
        if len(runtimes) != 1:
            raise RuntimeError("Runtime Python 3.12 gerenciado não foi encontrado.")
        runtime_python = runtimes[0] / "bin" / "python3.12"
        installed_python = "/" + str(runtime_python.relative_to(staging))

        subprocess.run(
            (
                "uv",
                "pip",
                "install",
                "--python",
                str(runtime_python),
                "--target",
                str(library),
                "--no-cache",
                str(wheel.resolve()),
            ),
            check=True,
            shell=False,
        )
        rewrite_entrypoint_shebangs(library / "bin", installed_python)

        control = staging / "DEBIAN" / "control"
        control.parent.mkdir(parents=True)
        control.write_text(control_text(version, architecture), encoding="utf-8")

        preinst = staging / "DEBIAN" / "preinst"
        write_executable(preinst, pre_install_text())

        postinst = staging / "DEBIAN" / "postinst"
        post_install_script = """#!/usr/bin/env bash
set -e
if command -v update-desktop-database >/dev/null; then
    update-desktop-database /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi
printf '%s\n' 'Ubuntu AI Assistant instalado.'
printf '%s\n' 'Execute ubuntu-ai-setup para configurar o modelo local.'
"""
        write_executable(
            postinst,
            post_install_script,
        )

        commands = (
            "ubuntu-ai",
            "ubuntu-ai-gui",
            "ubuntu-ai-setup",
            "ubuntu-ai-install-launcher",
        )
        for name in commands:
            if not (library / "bin" / name).is_file():
                raise RuntimeError(f"Entry point empacotado não encontrado: {name}")
            write_executable(
                staging / "usr" / "bin" / name,
                wrapper(name, installed_python),
            )

        desktop = staging / "usr" / "share" / "applications" / f"{APP_ID}.desktop"
        desktop.parent.mkdir(parents=True)
        desktop.write_text(desktop_text(), encoding="utf-8")

        source_icon = ROOT / "src" / "ubuntu_ai" / "gui" / "assets" / f"{APP_ID}.png"
        target_icon = (
            staging / "usr" / "share" / "icons" / "hicolor" / "512x512" / "apps" / source_icon.name
        )
        target_icon.parent.mkdir(parents=True)
        shutil.copy2(source_icon, target_icon)

        subprocess.run(
            ("dpkg-deb", "--build", "--root-owner-group", str(staging), str(destination)),
            check=True,
            shell=False,
        )
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói o pacote Debian do Ubuntu AI Assistant.")
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--architecture", default=None)
    args = parser.parse_args()

    architecture = args.architecture or detect_architecture()
    package = build_package(args.wheel, args.output.resolve(), architecture)
    print(f"Pacote Debian criado: {package}")


if __name__ == "__main__":
    main()
