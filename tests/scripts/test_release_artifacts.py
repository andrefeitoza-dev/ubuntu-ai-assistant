from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/release_artifacts.py"
SPEC = importlib.util.spec_from_file_location("release_artifacts", SCRIPT)
assert SPEC and SPEC.loader
release_artifacts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_artifacts)


def test_checksums_are_deterministic_and_verifiable(tmp_path: Path) -> None:
    first = tmp_path / "first.whl"
    second = tmp_path / "second.tar.gz"
    first.write_bytes(b"wheel")
    second.write_bytes(b"source")
    output = tmp_path / "SHA256SUMS"

    release_artifacts.write_checksums((second, first), output)
    release_artifacts.verify_checksums(output, tmp_path)

    expected = hashlib.sha256(b"wheel").hexdigest()
    assert output.read_text(encoding="utf-8").splitlines()[0] == f"{expected}  first.whl"


def test_checksum_verification_detects_modification(tmp_path: Path) -> None:
    artifact = tmp_path / "package.whl"
    artifact.write_bytes(b"original")
    output = tmp_path / "SHA256SUMS"
    release_artifacts.write_checksums((artifact,), output)
    artifact.write_bytes(b"modified")

    with pytest.raises(ValueError, match="Checksum inválido"):
        release_artifacts.verify_checksums(output, tmp_path)


@pytest.mark.parametrize(
    "name",
    (
        "../secret",
        "/absolute",
        "src/file.py.bak",
        "ubuntu-ai-source.zip",
        "ubuntu-ai-current.zip",
        "projeto.txt",
        "src_files.txt",
        "test_files.txt",
    ),
)
def test_unsafe_archive_members_are_rejected(name: str) -> None:
    assert not release_artifacts._safe_member(name) or release_artifacts._forbidden(name)
