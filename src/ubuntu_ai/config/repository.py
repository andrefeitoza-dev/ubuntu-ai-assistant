from __future__ import annotations

from pathlib import Path

from ubuntu_ai.config.defaults import (
    create_default_settings,
    default_paths,
)
from ubuntu_ai.config.loader import ConfigLoader
from ubuntu_ai.config.models import AppSettings


class ConfigRepository:
    """Persiste e recupera configurações em um arquivo TOML."""

    def __init__(
        self,
        config_file: Path | None = None,
        loader: ConfigLoader | None = None,
    ) -> None:
        paths = default_paths()

        if config_file is not None:
            normalized_file = config_file.expanduser()
            paths = paths.__class__(
                config_directory=normalized_file.parent,
                data_directory=paths.data_directory,
                cache_directory=paths.cache_directory,
                state_directory=paths.state_directory,
                config_file=normalized_file,
            )

        self._paths = paths
        self._config_file = paths.config_file
        self._loader = loader or ConfigLoader()

    @property
    def config_file(self) -> Path:
        """Retorna o caminho do arquivo de configuração."""

        return self._config_file

    def exists(self) -> bool:
        """Indica se o arquivo de configuração existe."""

        return self._config_file.is_file()

    def load(self) -> AppSettings:
        """Carrega configurações ou cria o arquivo padrão."""

        if not self.exists():
            settings = create_default_settings().with_paths(self._paths)
            self.save(settings)
            return settings

        return self._loader.load_file(
            self._config_file,
            default_paths=self._paths,
        )

    def save(self, settings: AppSettings) -> None:
        """Salva as configurações no formato TOML."""

        settings_with_paths = (
            settings if settings.paths is not None else settings.with_paths(self._paths)
        )

        self._config_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = self._serialize(settings_with_paths)

        temporary_file = self._config_file.with_suffix(f"{self._config_file.suffix}.tmp")

        try:
            temporary_file.write_text(
                content,
                encoding="utf-8",
            )
            temporary_file.chmod(0o600)
            temporary_file.replace(self._config_file)
            self._config_file.chmod(0o600)
        except OSError:
            temporary_file.unlink(missing_ok=True)
            raise

    def reset(self) -> AppSettings:
        """Restaura e persiste as configurações padrão."""

        settings = create_default_settings().with_paths(self._paths)
        self.save(settings)

        return settings

    @staticmethod
    def _serialize(settings: AppSettings) -> str:
        paths = settings.paths

        if paths is None:
            raise ValueError("Os caminhos da aplicação precisam estar definidos.")

        lines = [
            "# Ubuntu AI Assistant",
            "# Arquivo gerado automaticamente.",
            "",
            "[ai]",
            f"provider = {ConfigRepository._quote(settings.ai.provider)}",
            f"model = {ConfigRepository._quote(settings.ai.model)}",
            f"base_url = {ConfigRepository._quote(settings.ai.base_url)}",
            f"timeout = {settings.ai.timeout}",
            f"max_tokens = {settings.ai.max_tokens}",
            f"temperature = {settings.ai.temperature}",
            f"keep_alive = {ConfigRepository._quote(settings.ai.keep_alive)}",
            "",
            "[memory]",
            f"enabled = {ConfigRepository._boolean(settings.memory.enabled)}",
            "",
            "[knowledge]",
            f"enabled = {ConfigRepository._boolean(settings.knowledge.enabled)}",
            "",
            "[learning]",
            f"enabled = {ConfigRepository._boolean(settings.learning.enabled)}",
            "",
            "[reflection]",
            f"enabled = {ConfigRepository._boolean(settings.reflection.enabled)}",
            "",
            "[logging]",
            f"level = {ConfigRepository._quote(settings.logging.level)}",
            (f"directory = {ConfigRepository._quote(str(settings.logging.directory))}"),
            f"max_file_size_mb = {settings.logging.max_file_size_mb}",
            f"backup_count = {settings.logging.backup_count}",
            "",
            "[ui]",
            f"language = {ConfigRepository._quote(settings.ui.language)}",
            f"theme = {ConfigRepository._quote(settings.ui.theme)}",
            (f"clear_between_tasks = {ConfigRepository._boolean(settings.ui.clear_between_tasks)}"),
            "",
            "[paths]",
            (f"config_directory = {ConfigRepository._quote(str(paths.config_directory))}"),
            (f"data_directory = {ConfigRepository._quote(str(paths.data_directory))}"),
            (f"cache_directory = {ConfigRepository._quote(str(paths.cache_directory))}"),
            (f"state_directory = {ConfigRepository._quote(str(paths.state_directory))}"),
            (f"config_file = {ConfigRepository._quote(str(paths.config_file))}"),
            "",
        ]

        return "\n".join(lines)

    @staticmethod
    def _quote(value: str) -> str:
        escaped_value = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )

        return f'"{escaped_value}"'

    @staticmethod
    def _boolean(value: bool) -> str:
        return "true" if value else "false"
