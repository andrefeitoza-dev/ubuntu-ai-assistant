from __future__ import annotations

import argparse
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = {
    "./usr/bin/ubuntu-ai",
    "./usr/bin/ubuntu-ai-gui",
    "./usr/bin/ubuntu-ai-setup",
    "./usr/share/applications/ubuntu-ai-assistant.desktop",
    "./usr/share/icons/hicolor/512x512/apps/ubuntu-ai-assistant.png",
}


def project_version() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(project["project"]["version"])


def field(package: Path, name: str) -> str:
    result = subprocess.run(
        ("dpkg-deb", "--field", str(package), name),
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    )
    return result.stdout.strip()


def contents(package: Path) -> set[str]:
    result = subprocess.run(
        ("dpkg-deb", "--contents", str(package)),
        check=True,
        capture_output=True,
        text=True,
        shell=False,
    )
    return {line.split(maxsplit=5)[-1] for line in result.stdout.splitlines() if line.strip()}


def validate(package: Path) -> None:
    if not package.is_file():
        raise ValueError(f"Pacote ausente: {package}")
    if field(package, "Package") != "ubuntu-ai-assistant":
        raise ValueError("Nome de pacote Debian inválido.")
    if field(package, "Version") != project_version():
        raise ValueError("Versão do pacote Debian não corresponde ao projeto.")
    dependencies = field(package, "Depends")
    if "libc6" not in dependencies or "libx11-6" not in dependencies:
        raise ValueError("Dependências do sistema incompletas.")
    packaged_paths = contents(package)
    missing = sorted(REQUIRED_PATHS - packaged_paths)
    if missing:
        raise ValueError("Pacote Debian incompleto: " + ", ".join(missing))
    if not any(path.endswith("/bin/python3.12") for path in packaged_paths):
        raise ValueError("Runtime Python 3.12 incorporado não encontrado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita o pacote Debian da distribuição.")
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    validate(args.package.resolve())
    print(f"Pacote Debian {args.package.name} aprovado.")


if __name__ == "__main__":
    main()
