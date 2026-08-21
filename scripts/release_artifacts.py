from __future__ import annotations

import argparse
import hashlib
import re
import tarfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = (".bak", ".backup", ".orig", ".rej", ".pyc")
REQUIRED_WHEEL_FILES = {
    "ubuntu_ai/cli/app.py",
    "ubuntu_ai/gui/assets/ubuntu-ai-assistant.png",
    "ubuntu_ai/gui/launcher_installer.py",
    "ubuntu_ai/distribution/lifecycle.py",
    "ubuntu_ai/plugins/catalog.py",
}


def project_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def _safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def _forbidden(name: str) -> bool:
    lowered = name.lower()
    return lowered.endswith(FORBIDDEN_SUFFIXES) or "/__pycache__/" in lowered


def validate_wheel(path: Path, version: str) -> None:
    expected = f"ubuntu_ai_assistant-{version}-py3-none-any.whl"
    if path.name != expected:
        raise ValueError(f"Wheel inesperado: {path.name}; esperado {expected}.")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        unsafe = sorted(name for name in names if not _safe_member(name) or _forbidden(name))
        if unsafe:
            raise ValueError("Wheel contém arquivos inseguros: " + ", ".join(unsafe))
        missing = sorted(REQUIRED_WHEEL_FILES - names)
        if missing:
            raise ValueError("Wheel incompleto: " + ", ".join(missing))

        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("Wheel deve conter exatamente um arquivo METADATA.")
        metadata = archive.read(metadata_names[0]).decode("utf-8")
        if f"Version: {version}\n" not in metadata:
            raise ValueError("Versão do METADATA não corresponde ao projeto.")


def validate_sdist(path: Path, version: str) -> None:
    expected = f"ubuntu_ai_assistant-{version}.tar.gz"
    if path.name != expected:
        raise ValueError(f"Source archive inesperado: {path.name}; esperado {expected}.")

    prefix = f"ubuntu_ai_assistant-{version}/"
    with tarfile.open(path, "r:gz") as archive:
        names = [member.name for member in archive.getmembers()]
        unsafe = sorted(name for name in names if not _safe_member(name) or _forbidden(name))
        if unsafe:
            raise ValueError("Source archive contém arquivos inseguros: " + ", ".join(unsafe))
        required = {prefix + "pyproject.toml", prefix + "README.md", prefix + "LICENSE"}
        missing = sorted(required - set(names))
        if missing:
            raise ValueError("Source archive incompleto: " + ", ".join(missing))


def release_artifacts(directory: Path) -> tuple[Path, Path]:
    version = project_version()
    wheel = directory / f"ubuntu_ai_assistant-{version}-py3-none-any.whl"
    sdist = directory / f"ubuntu_ai_assistant-{version}.tar.gz"
    if not wheel.is_file() or not sdist.is_file():
        raise ValueError("Wheel e source archive da versão atual são obrigatórios.")
    validate_wheel(wheel, version)
    validate_sdist(sdist, version)
    return wheel, sdist


def write_checksums(paths: tuple[Path, ...], output: Path) -> None:
    lines = []
    for path in sorted(paths, key=lambda item: item.name):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_checksums(checksum_file: Path, directory: Path) -> None:
    pattern = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9_.+-]+)$")
    entries = checksum_file.read_text(encoding="utf-8").splitlines()
    if not entries:
        raise ValueError("Arquivo de checksums vazio.")
    for line in entries:
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError(f"Linha de checksum inválida: {line}")
        expected, name = match.groups()
        artifact = directory / name
        if not artifact.is_file():
            raise ValueError(f"Artefato ausente: {name}")
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Checksum inválido: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita artefatos da release.")
    parser.add_argument("operation", choices=("validate", "checksums", "verify"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()

    directory = args.directory.resolve()
    checksum_file = directory / "SHA256SUMS"
    if args.operation == "verify":
        verify_checksums(checksum_file, directory)
        print("Checksums aprovados.")
        return

    artifacts = release_artifacts(directory)
    if args.operation == "checksums":
        write_checksums(artifacts, checksum_file)
        verify_checksums(checksum_file, directory)
        print(f"Checksums gerados: {checksum_file}")
        return
    print(f"Artefatos da versão {project_version()} aprovados.")


if __name__ == "__main__":
    main()
