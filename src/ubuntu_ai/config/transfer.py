from __future__ import annotations

import os
import re
import tomllib
from dataclasses import replace
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from ubuntu_ai.config.loader import ConfigLoader, ConfigLoadError
from ubuntu_ai.config.models import AppSettings
from ubuntu_ai.config.repository import ConfigRepository

_SECRET_KEY = re.compile(
    r"(?:^|_)(?:api_?key|token|secret|password|credential|private_?key)(?:$|_)",
    re.IGNORECASE,
)
MAX_CONFIG_SIZE = 1024 * 1024


class ConfigTransferError(ValueError):
    """Indica exportação ou importação insegura/inválida."""


class ConfigTransferService:
    """Transfere apenas opções públicas e mantém caminhos locais."""

    def __init__(self, repository: ConfigRepository | None = None) -> None:
        self._repository = repository or ConfigRepository()

    def export_file(self, destination: Path) -> Path:
        target = self._safe_target(destination)
        settings = self._repository.load()
        self._reject_url_credentials(settings.ai.base_url)
        content = self._portable_toml(settings)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        try:
            temporary.write_text(content, encoding="utf-8")
            temporary.chmod(0o600)
            temporary.replace(target)
            target.chmod(0o600)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
        return target

    def import_file(self, source: Path) -> AppSettings:
        path = source.expanduser()
        if path.is_symlink() or not path.is_file():
            raise ConfigTransferError("A origem precisa ser um arquivo regular.")
        if path.stat().st_size > MAX_CONFIG_SIZE:
            raise ConfigTransferError("A configuração excede o limite de 1 MiB.")
        try:
            with path.open("rb") as stream:
                raw = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigTransferError("Não foi possível interpretar a configuração.") from exc
        self._reject_secrets(raw)
        ai_section = raw.get("ai", {})
        if isinstance(ai_section, dict) and isinstance(ai_section.get("base_url"), str):
            self._reject_url_credentials(ai_section["base_url"])
        current = self._repository.load()
        current_paths = current.paths
        if current_paths is None:
            raise ConfigTransferError("Os caminhos locais não estão disponíveis.")
        try:
            settings = ConfigLoader().load_mapping(
                raw,
                default_paths=current_paths,
            )
        except (ConfigLoadError, TypeError, ValueError) as exc:
            raise ConfigTransferError(str(exc)) from exc
        imported = replace(
            settings.with_paths(current_paths),
            logging=replace(settings.logging, directory=current.logging.directory),
        )
        self._repository.save(imported)
        return imported

    @staticmethod
    def _safe_target(destination: Path) -> Path:
        target = destination.expanduser()
        if not target.is_absolute():
            raise ConfigTransferError("O destino deve usar caminho absoluto.")
        if target.exists() and (target.is_symlink() or not target.is_file()):
            raise ConfigTransferError("O destino precisa ser um arquivo regular.")
        if target.parent.exists() and target.parent.is_symlink():
            raise ConfigTransferError("O diretório de destino não pode ser um link simbólico.")
        return target

    @staticmethod
    def _reject_url_credentials(value: str) -> None:
        parsed = urlsplit(value)
        if parsed.username is not None or parsed.password is not None:
            raise ConfigTransferError("A URL do provedor não pode conter credenciais.")

    @classmethod
    def _reject_secrets(cls, value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                name = str(key)
                location = f"{path}.{name}" if path else name
                if _SECRET_KEY.search(name):
                    raise ConfigTransferError(
                        f"A configuração contém campo potencialmente secreto: {location}."
                    )
                cls._reject_secrets(nested, location)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                cls._reject_secrets(nested, f"{path}[{index}]")

    @staticmethod
    def _portable_toml(settings: AppSettings) -> str:
        quote = ConfigRepository._quote
        boolean = ConfigRepository._boolean
        lines = [
            "# Ubuntu AI Assistant — configuração portátil",
            "# Segredos e caminhos locais não são exportados.",
            "",
            "[ai]",
            f"provider = {quote(settings.ai.provider)}",
            f"model = {quote(settings.ai.model)}",
            f"base_url = {quote(settings.ai.base_url)}",
            f"timeout = {settings.ai.timeout}",
            f"max_tokens = {settings.ai.max_tokens}",
            f"temperature = {settings.ai.temperature}",
            f"keep_alive = {quote(settings.ai.keep_alive)}",
            "",
            "[memory]",
            f"enabled = {boolean(settings.memory.enabled)}",
            "",
            "[knowledge]",
            f"enabled = {boolean(settings.knowledge.enabled)}",
            "",
            "[learning]",
            f"enabled = {boolean(settings.learning.enabled)}",
            "",
            "[reflection]",
            f"enabled = {boolean(settings.reflection.enabled)}",
            "",
            "[logging]",
            f"level = {quote(settings.logging.level)}",
            f"max_file_size_mb = {settings.logging.max_file_size_mb}",
            f"backup_count = {settings.logging.backup_count}",
            "",
            "[ui]",
            f"language = {quote(settings.ui.language)}",
            f"theme = {quote(settings.ui.theme)}",
            f"clear_between_tasks = {boolean(settings.ui.clear_between_tasks)}",
            "",
        ]
        return os.linesep.join(lines)
