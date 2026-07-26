from __future__ import annotations

from pathlib import Path

from ubuntu_ai.memory.database import default_app_directory

DATABASE_FILE_NAME = "knowledge.db"


def default_knowledge_database_path() -> Path:
    """Retorna o caminho padrão do banco de conhecimento."""

    return default_app_directory() / DATABASE_FILE_NAME


def prepare_knowledge_database_path(database_path: Path) -> Path:
    """Expande o caminho e cria seu diretório pai."""

    resolved_path = database_path.expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path
