from __future__ import annotations

import os
from pathlib import Path

from ubuntu_ai.config.models import (
    AIConfig,
    AppSettings,
    FeatureConfig,
    LoggingConfig,
    PathConfig,
    UIConfig,
)

APPLICATION_NAME = "ubuntu-ai"
CONFIG_FILE_NAME = "config.toml"


def _environment_path(
    variable_name: str,
    fallback: Path,
) -> Path:
    value = os.environ.get(variable_name)

    if value is None or not value.strip():
        return fallback.expanduser()

    return Path(value).expanduser()


def default_config_directory() -> Path:
    """Retorna o diretório XDG de configuração da aplicação."""

    xdg_directory = _environment_path(
        "XDG_CONFIG_HOME",
        Path.home() / ".config",
    )

    return xdg_directory / APPLICATION_NAME


def default_data_directory() -> Path:
    """Retorna o diretório XDG de dados persistentes."""

    xdg_directory = _environment_path(
        "XDG_DATA_HOME",
        Path.home() / ".local" / "share",
    )

    return xdg_directory / APPLICATION_NAME


def default_cache_directory() -> Path:
    """Retorna o diretório XDG de cache."""

    xdg_directory = _environment_path(
        "XDG_CACHE_HOME",
        Path.home() / ".cache",
    )

    return xdg_directory / APPLICATION_NAME


def default_state_directory() -> Path:
    """Retorna o diretório XDG de estado e logs."""

    xdg_directory = _environment_path(
        "XDG_STATE_HOME",
        Path.home() / ".local" / "state",
    )

    return xdg_directory / APPLICATION_NAME


def default_config_file() -> Path:
    """Retorna o caminho padrão do arquivo de configuração."""

    return default_config_directory() / CONFIG_FILE_NAME


def default_paths() -> PathConfig:
    """Cria a configuração padrão de diretórios."""

    return PathConfig(
        config_directory=default_config_directory(),
        data_directory=default_data_directory(),
        cache_directory=default_cache_directory(),
        state_directory=default_state_directory(),
        config_file=default_config_file(),
    )


def create_default_settings() -> AppSettings:
    """Cria as configurações padrão completas da aplicação."""

    paths = default_paths()

    return AppSettings(
        ai=AIConfig(),
        memory=FeatureConfig(enabled=True),
        knowledge=FeatureConfig(enabled=True),
        learning=FeatureConfig(enabled=True),
        reflection=FeatureConfig(enabled=True),
        logging=LoggingConfig(
            level="INFO",
            directory=paths.state_directory / "logs",
            max_file_size_mb=10,
            backup_count=5,
        ),
        ui=UIConfig(
            language="pt_BR",
            theme="default",
            clear_between_tasks=False,
        ),
        paths=paths,
    )
