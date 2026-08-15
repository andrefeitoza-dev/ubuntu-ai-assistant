from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from ubuntu_ai.config.models import (
    AIConfig,
    AppSettings,
    FeatureConfig,
    LoggingConfig,
    PathConfig,
    UIConfig,
)


class ConfigLoadError(ValueError):
    """Indica que o arquivo de configuração não pôde ser interpretado."""


class ConfigLoader:
    """Converte arquivos e dicionários TOML em configurações da aplicação."""

    def load_file(
        self,
        config_file: Path,
        *,
        default_paths: PathConfig,
    ) -> AppSettings:
        """Carrega configurações de um arquivo TOML."""

        normalized_file = config_file.expanduser()

        try:
            with normalized_file.open("rb") as stream:
                raw_data = tomllib.load(stream)
        except FileNotFoundError:
            raise
        except (OSError, tomllib.TOMLDecodeError) as error:
            raise ConfigLoadError(f"Não foi possível carregar a configuração: {error}") from error

        return self.load_mapping(
            raw_data,
            default_paths=default_paths,
        )

    def load_mapping(
        self,
        raw_data: dict[str, Any],
        *,
        default_paths: PathConfig,
    ) -> AppSettings:
        """Converte um mapeamento em configurações validadas."""

        try:
            ai_data = self._section(raw_data, "ai")
            memory_data = self._section(raw_data, "memory")
            knowledge_data = self._section(raw_data, "knowledge")
            learning_data = self._section(raw_data, "learning")
            reflection_data = self._section(raw_data, "reflection")
            logging_data = self._section(raw_data, "logging")
            ui_data = self._section(raw_data, "ui")
            paths_data = self._section(raw_data, "paths")

            paths = self._load_paths(
                paths_data,
                default_paths=default_paths,
            )

            return AppSettings(
                ai=AIConfig(
                    provider=self._string(
                        ai_data,
                        "provider",
                        "ollama",
                    ),
                    model=self._string(
                        ai_data,
                        "model",
                        "qwen2.5:3b",
                    ),
                    base_url=self._string(
                        ai_data,
                        "base_url",
                        "http://localhost:11434",
                    ),
                    timeout=self._integer(
                        ai_data,
                        "timeout",
                        300,
                    ),
                    max_tokens=self._integer(
                        ai_data,
                        "max_tokens",
                        384,
                    ),
                    temperature=self._number(
                        ai_data,
                        "temperature",
                        0.1,
                    ),
                    keep_alive=self._string(
                        ai_data,
                        "keep_alive",
                        "10m",
                    ),
                ),
                memory=FeatureConfig(
                    enabled=self._boolean(
                        memory_data,
                        "enabled",
                        True,
                    )
                ),
                knowledge=FeatureConfig(
                    enabled=self._boolean(
                        knowledge_data,
                        "enabled",
                        True,
                    )
                ),
                learning=FeatureConfig(
                    enabled=self._boolean(
                        learning_data,
                        "enabled",
                        True,
                    )
                ),
                reflection=FeatureConfig(
                    enabled=self._boolean(
                        reflection_data,
                        "enabled",
                        True,
                    )
                ),
                logging=LoggingConfig(
                    level=self._string(
                        logging_data,
                        "level",
                        "INFO",
                    ),
                    directory=self._path(
                        logging_data,
                        "directory",
                        paths.state_directory / "logs",
                    ),
                    max_file_size_mb=self._integer(
                        logging_data,
                        "max_file_size_mb",
                        10,
                    ),
                    backup_count=self._integer(
                        logging_data,
                        "backup_count",
                        5,
                    ),
                ),
                ui=UIConfig(
                    language=self._string(
                        ui_data,
                        "language",
                        "pt_BR",
                    ),
                    theme=self._string(
                        ui_data,
                        "theme",
                        "default",
                    ),
                    clear_between_tasks=self._boolean(
                        ui_data,
                        "clear_between_tasks",
                        False,
                    ),
                ),
                paths=paths,
            )
        except (TypeError, ValueError) as error:
            raise ConfigLoadError(f"A configuração contém valores inválidos: {error}") from error

    def _load_paths(
        self,
        raw_data: dict[str, Any],
        *,
        default_paths: PathConfig,
    ) -> PathConfig:
        config_directory = self._path(
            raw_data,
            "config_directory",
            default_paths.config_directory,
        )
        data_directory = self._path(
            raw_data,
            "data_directory",
            default_paths.data_directory,
        )
        cache_directory = self._path(
            raw_data,
            "cache_directory",
            default_paths.cache_directory,
        )
        state_directory = self._path(
            raw_data,
            "state_directory",
            default_paths.state_directory,
        )
        config_file = self._path(
            raw_data,
            "config_file",
            config_directory / "config.toml",
        )

        return PathConfig(
            config_directory=config_directory,
            data_directory=data_directory,
            cache_directory=cache_directory,
            state_directory=state_directory,
            config_file=config_file,
        ).expanded()

    @staticmethod
    def _section(
        raw_data: dict[str, Any],
        section_name: str,
    ) -> dict[str, Any]:
        value = raw_data.get(section_name, {})

        if not isinstance(value, dict):
            raise TypeError(f"A seção '{section_name}' deve ser uma tabela TOML.")

        return value

    @staticmethod
    def _string(
        section: dict[str, Any],
        key: str,
        default: str,
    ) -> str:
        value = section.get(key, default)

        if not isinstance(value, str):
            raise TypeError(f"'{key}' deve ser uma string.")

        return value

    @staticmethod
    def _integer(
        section: dict[str, Any],
        key: str,
        default: int,
    ) -> int:
        value = section.get(key, default)

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{key}' deve ser um número inteiro.")

        return value

    @staticmethod
    def _number(
        section: dict[str, Any],
        key: str,
        default: float,
    ) -> float:
        value = section.get(key, default)

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"'{key}' deve ser um número.")

        return float(value)

    @staticmethod
    def _boolean(
        section: dict[str, Any],
        key: str,
        default: bool,
    ) -> bool:
        value = section.get(key, default)

        if not isinstance(value, bool):
            raise TypeError(f"'{key}' deve ser verdadeiro ou falso.")

        return value

    @staticmethod
    def _path(
        section: dict[str, Any],
        key: str,
        default: Path,
    ) -> Path:
        value = section.get(key)

        if value is None:
            return default.expanduser()

        if not isinstance(value, str):
            raise TypeError(f"'{key}' deve ser um caminho em formato texto.")

        return Path(value).expanduser()
