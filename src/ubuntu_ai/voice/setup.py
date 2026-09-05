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
NATURAL_VOICE_BASE_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/cadu/medium"
)
NATURAL_VOICE_FILES = {
    "pt_BR-cadu-medium.onnx": "765f0809a6ea9035d4a6d0d008dbf8876e68b2dd32029312672fa8f405bdb535",
    "pt_BR-cadu-medium.onnx.json": (
        "5fe03aa3d4901880554905b12075713cd552598c8a350455a1ec73f8b4e6be19"
    ),
}


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


class NaturalVoiceSetup:
    """Instala a voz neural brasileira Piper com verificação de integridade."""

    def __init__(self, *, destination: Path | None = None) -> None:
        self._destination = destination or default_data_directory() / "voice" / "piper"

    @property
    def model_path(self) -> Path:
        return self._destination / "pt_BR-cadu-medium.onnx"

    def available(self) -> bool:
        return all((self._destination / name).is_file() for name in NATURAL_VOICE_FILES)

    def install(self) -> Path:
        self._destination.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name, expected_digest in NATURAL_VOICE_FILES.items():
            destination = self._destination / name
            if destination.is_file() and self._digest(destination) == expected_digest:
                continue
            temporary = destination.with_suffix(destination.suffix + ".download")
            try:
                request = urllib.request.Request(
                    f"{NATURAL_VOICE_BASE_URL}/{name}?download=true",
                    headers={"User-Agent": "Ubuntu-AI-Assistant/voice-setup"},
                )
                with (
                    urllib.request.urlopen(request, timeout=90) as response,
                    temporary.open("wb") as file,
                ):
                    shutil.copyfileobj(response, file, length=1024 * 1024)
                if self._digest(temporary) != expected_digest:
                    raise RuntimeError("A voz natural falhou na verificação de integridade.")
                temporary.replace(destination)
            finally:
                temporary.unlink(missing_ok=True)
        return self.model_path

    @staticmethod
    def _digest(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
