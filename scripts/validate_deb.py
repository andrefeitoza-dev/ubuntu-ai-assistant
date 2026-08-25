from __future__ import annotations

import argparse
import subprocess
import tempfile
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
PUBLIC_COMMANDS = (
    "ubuntu-ai",
    "ubuntu-ai-gui",
    "ubuntu-ai-setup",
    "ubuntu-ai-install-launcher",
)


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


def validate_launcher_tree(root: Path) -> None:
    for command in PUBLIC_COMMANDS:
        public = root / "usr" / "bin" / command
        internal = root / "opt" / "ubuntu-ai-assistant" / "lib" / "bin" / command
        if not public.is_file() or not internal.is_file():
            raise ValueError(f"Lançador ausente: {command}")

        public_text = public.read_text(encoding="utf-8")
        if " -c " in public_text or f"/lib/bin/{command}" not in public_text:
            raise ValueError(f"Lançador público inválido: {command}")

        first_line = internal.read_text(encoding="utf-8").splitlines()[0]
        if "/tmp/ubuntu-ai-deb-" in first_line:
            raise ValueError(f"Entry point contém caminho temporário: {command}")
        if not first_line.startswith("#!/opt/ubuntu-ai-assistant/runtime/"):
            raise ValueError(f"Shebang final inválido: {command}")


def validate_preinstall_tree(root: Path) -> None:
    preinst = root / "preinst"
    if not preinst.is_file():
        raise ValueError("Script Debian preinst ausente.")

    source = preinst.read_text(encoding="utf-8")
    required = (
        '"${1:-}" = "upgrade"',
        '[ -d "/opt/ubuntu-ai-assistant" ]',
        'rm -rf -- "/opt/ubuntu-ai-assistant"',
    )
    if not all(item in source for item in required):
        raise ValueError("Script Debian preinst inválido.")
    if "$HOME" in source or ".config" in source:
        raise ValueError("Script Debian preinst alcança dados do usuário.")


def validate_preinstall(package: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="ubuntu-ai-deb-control-") as temporary:
        root = Path(temporary)
        subprocess.run(
            ("dpkg-deb", "--control", str(package), str(root)),
            check=True,
            shell=False,
        )
        validate_preinstall_tree(root)


def validate_launchers(package: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="ubuntu-ai-deb-audit-") as temporary:
        root = Path(temporary)
        subprocess.run(
            ("dpkg-deb", "--extract", str(package), str(root)),
            check=True,
            shell=False,
        )
        validate_launcher_tree(root)


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
    validate_preinstall(package)
    validate_launchers(package)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita o pacote Debian da distribuição.")
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    validate(args.package.resolve())
    print(f"Pacote Debian {args.package.name} aprovado.")


if __name__ == "__main__":
    main()
