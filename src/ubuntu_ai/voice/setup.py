from __future__ import annotations

import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from ubuntu_ai.config.defaults import default_data_directory

VOICE_MODEL_NAME = "vosk-model-small-pt-0.3"
VOICE_MODEL_URL = f"https://alphacephei.com/vosk/models/{VOICE_MODEL_NAME}.zip"
VOICE_MODEL_SHA256 = "6e1ce909032e1afa7a88e68a3d628ecafff302bdf195befab308826c395e93b7"


@dataclass(frozen=True, slots=True)
class VoiceSetupStatus:
    model_available: bool
    model_path: Path


class VoiceModelSetup:
    """Baixa e instala o modelo oficial de voz em diretório privado do usuário."""

    def __init__(self, *, destination: Path | None = None) -> None:
        self._destination = destination or default_data_directory() / "voice" / "vosk-model-pt"

    def status(self) -> VoiceSetupStatus:
        return VoiceSetupStatus(self._destination.is_dir(), self._destination)

    def install(self) -> Path:
        if self._destination.exists():
            if self._destination.is_dir():
                return self._destination
            raise RuntimeError("O destino do modelo de voz existe e não é um diretório.")

        parent = self._destination.parent
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with tempfile.TemporaryDirectory(prefix="voice-model-", dir=parent) as temporary:
            workspace = Path(temporary)
            archive = workspace / "model.zip"
            self._download(archive)
            self._verify(archive)
            extracted = workspace / "extracted"
            extracted.mkdir()
            self._safe_extract(archive, extracted)
            source = extracted / VOICE_MODEL_NAME
            if not source.is_dir():
                raise RuntimeError("O arquivo baixado não contém o modelo de voz esperado.")
            shutil.move(str(source), self._destination)
        return self._destination

    @staticmethod
    def _download(destination: Path) -> None:
        request = urllib.request.Request(
            VOICE_MODEL_URL,
            headers={"User-Agent": "Ubuntu-AI-Assistant/voice-setup"},
        )
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            destination.open("wb") as file,
        ):
            shutil.copyfileobj(response, file, length=1024 * 1024)

    @staticmethod
    def _verify(archive: Path) -> None:
        digest = hashlib.sha256()
        with archive.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != VOICE_MODEL_SHA256:
            raise RuntimeError("O modelo de voz falhou na verificação de integridade SHA-256.")

    @staticmethod
    def _safe_extract(archive: Path, destination: Path) -> None:
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                path = PurePosixPath(member.filename)
                if path.is_absolute() or ".." in path.parts or path.parts[0] != VOICE_MODEL_NAME:
                    raise RuntimeError("O modelo de voz contém um caminho inseguro.")
            bundle.extractall(destination)
