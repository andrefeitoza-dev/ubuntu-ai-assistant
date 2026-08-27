from __future__ import annotations

import platform
import re
import shutil
import subprocess
import unicodedata
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, distribution

from ubuntu_ai.version import PACKAGE_NAME, get_version


class RuntimeStatusResponder:
    """Consulta versões e disponibilidade sem executar alterações."""

    _TOPICS = {
        "o servico ssh esta ativo": "ssh",
        "o docker esta instalado": "docker",
        "qual a versao do python": "python",
        "mostre a versao do assistente": "assistant",
        "verifique a instalacao": "installation",
    }

    def __init__(
        self,
        *,
        ssh_provider: Callable[[], str | None] | None = None,
        docker_provider: Callable[[], str | None] | None = None,
        python_provider: Callable[[], str] | None = None,
        version_provider: Callable[[], str] | None = None,
        installation_provider: Callable[[], str | None] | None = None,
    ) -> None:
        self._ssh_provider = ssh_provider or self._ssh_status
        self._docker_provider = docker_provider or self._docker_version
        self._python_provider = python_provider or platform.python_version
        self._version_provider = version_provider or get_version
        self._installation_provider = installation_provider or self._installed_version

    def respond(self, request: str) -> str | None:
        topic = self._TOPICS.get(self._normalize(request))
        if topic is None:
            return None

        if topic == "ssh":
            status = self._safe_optional(self._ssh_provider)
            if status is None:
                return "Não foi possível consultar o estado do serviço SSH."
            translated = {
                "active": "ativo",
                "inactive": "inativo",
                "failed": "com falha",
                "activating": "iniciando",
                "deactivating": "parando",
            }.get(status.casefold(), status)
            return f"Serviço SSH deste computador: {translated}."

        if topic == "docker":
            version = self._safe_optional(self._docker_provider)
            if version is None:
                return "Docker não está instalado ou não está disponível no PATH."
            return f"Docker instalado: {version}."

        if topic == "python":
            return f"Python deste ambiente: {self._python_provider()}."

        if topic == "assistant":
            return f"Ubuntu AI Assistant: versão {self._version_provider()}."

        installed = self._safe_optional(self._installation_provider)
        if installed is None:
            return (
                "A instalação do Ubuntu AI Assistant não foi encontrada "
                "nos metadados do ambiente atual."
            )
        return f"Instalação do Ubuntu AI Assistant disponível e legível: versão {installed}."

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return " ".join(normalized.split())

    @staticmethod
    def _safe_optional(
        provider: Callable[[], str | None],
    ) -> str | None:
        try:
            return provider()
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError):
            return None

    @staticmethod
    def _ssh_status() -> str | None:
        if shutil.which("systemctl") is None:
            return None

        result = subprocess.run(
            ("systemctl", "is-active", "ssh"),
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
            shell=False,
        )
        status = result.stdout.strip()
        if status:
            return status
        return "inativo" if result.returncode else "ativo"

    @staticmethod
    def _docker_version() -> str | None:
        executable = shutil.which("docker")
        if executable is None:
            return None

        result = subprocess.run(
            (executable, "--version"),
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
            shell=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    @staticmethod
    def _installed_version() -> str | None:
        try:
            return distribution(PACKAGE_NAME).version
        except PackageNotFoundError:
            return None
