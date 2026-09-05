from __future__ import annotations

import hashlib
import io
import zipfile

import pytest

from ubuntu_ai.voice import VoiceModelSetup


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
