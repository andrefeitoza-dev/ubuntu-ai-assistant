from pathlib import Path

from ubuntu_ai.memory.database import default_app_directory, prepare_database_path

DATABASE_FILE_NAME = "learning.db"


def default_database_path() -> Path:
    return default_app_directory() / DATABASE_FILE_NAME


__all__ = ["default_database_path", "prepare_database_path"]
