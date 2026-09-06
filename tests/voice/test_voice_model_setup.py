from __future__ import annotations

import hashlib
import io
import zipfile

import pytest

from ubuntu_ai.voice import NaturalVoiceSetup, VoiceModelSetup


def model_archive(*, unsafe: bool = False) -> bytes:
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as bundle:
        name = "../escape" if unsafe else "vosk-model-small-pt-0.3/conf/model.conf"
        bundle.writestr(name, "model")
    return content.getvalue()


def test_voice_model_download_is_verified_and_installed(monkeypatch, tmp_path) -> None:
    archive = model_archive()
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.VOICE_MODEL_SHA256",
        hashlib.sha256(archive).hexdigest(),
    )
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.urllib.request.urlopen",
        lambda _request, timeout: io.BytesIO(archive),
    )
    destination = tmp_path / "voice" / "vosk-model-pt"

    installed = VoiceModelSetup(destination=destination).install()

    assert installed == destination
    assert (destination / "conf" / "model.conf").read_text() == "model"


def test_voice_model_rejects_unsafe_archive_paths(monkeypatch, tmp_path) -> None:
    archive = model_archive(unsafe=True)
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.VOICE_MODEL_SHA256",
        hashlib.sha256(archive).hexdigest(),
    )
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.urllib.request.urlopen",
        lambda _request, timeout: io.BytesIO(archive),
    )

    with pytest.raises(RuntimeError, match="caminho inseguro"):
        VoiceModelSetup(destination=tmp_path / "model").install()


def test_natural_voice_setup_recognizes_both_required_files(tmp_path) -> None:
    setup = NaturalVoiceSetup(destination=tmp_path)

    assert setup.available() is False
    setup.model_path.touch()
    assert setup.available() is False
    setup.model_path.with_suffix(".onnx.json").touch()
    assert setup.available() is True


def test_natural_voice_downloads_verifies_and_installs_files(monkeypatch, tmp_path) -> None:
    content = b"valid neural voice"
    files = {
        "pt_BR-cadu-medium.onnx": hashlib.sha256(content).hexdigest(),
        "pt_BR-cadu-medium.onnx.json": hashlib.sha256(content).hexdigest(),
    }
    monkeypatch.setattr("ubuntu_ai.voice.setup.NATURAL_VOICE_FILES", files)
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.urllib.request.urlopen",
        lambda _request, timeout: io.BytesIO(content),
    )
    setup = NaturalVoiceSetup(destination=tmp_path / "piper")

    installed = setup.install()

    assert installed == setup.model_path
    assert setup.available() is True
    assert all((tmp_path / "piper" / name).read_bytes() == content for name in files)


def test_natural_voice_rejects_invalid_download_and_removes_temporary_file(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.NATURAL_VOICE_FILES",
        {"pt_BR-cadu-medium.onnx": hashlib.sha256(b"expected").hexdigest()},
    )
    monkeypatch.setattr(
        "ubuntu_ai.voice.setup.urllib.request.urlopen",
        lambda _request, timeout: io.BytesIO(b"corrupted"),
    )
    setup = NaturalVoiceSetup(destination=tmp_path / "piper")

    with pytest.raises(RuntimeError, match="integridade"):
        setup.install()

    assert not list((tmp_path / "piper").glob("*.download"))
