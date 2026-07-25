from __future__ import annotations

from pathlib import Path

APP_DIRECTORY_NAME = ".ubuntu_ai"
DATABASE_FILE_NAME = "memory.db"


def default_app_directory() -> Path:
    """Retorna o diretório padrão de dados locais do UbuntuAI."""

    return Path.home() / APP_DIRECTORY_NAME


def default_database_path() -> Path:
    """Retorna o caminho padrão do banco de memória."""

    return default_app_directory() / DATABASE_FILE_NAME


def prepare_database_path(database_path: Path) -> Path:
    """Cria o diretório pai do banco quando necessário."""

    resolved_path = database_path.expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path
