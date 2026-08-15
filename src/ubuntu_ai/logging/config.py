from __future__ import annotations

import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path

DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True, slots=True)
class LoggingRuntimeConfig:
    """Parâmetros usados para configurar o logging da aplicação."""

    directory: Path
    level: str = "INFO"
    max_file_size_mb: int = 10
    backup_count: int = 5
    console_enabled: bool = False
    file_name: str = "ubuntu-ai.log"

    def __post_init__(self) -> None:
        normalized_level = self.level.strip().upper()

        if normalized_level not in logging.getLevelNamesMapping():
            raise ValueError(f"Nível de log inválido: {self.level}")

        if self.max_file_size_mb <= 0:
            raise ValueError("O tamanho máximo do arquivo de log deve ser maior que zero.")

        if self.backup_count < 0:
            raise ValueError("A quantidade de backups de log não pode ser negativa.")

        if not self.file_name.strip():
            raise ValueError("O nome do arquivo de log não pode estar vazio.")

    @property
    def numeric_level(self) -> int:
        """Retorna o nível numérico aceito pela biblioteca logging."""

        return logging.getLevelNamesMapping()[self.level.strip().upper()]

    @property
    def file_path(self) -> Path:
        """Retorna o caminho completo do arquivo principal de log."""

        return self.directory.expanduser() / self.file_name


def build_formatter() -> logging.Formatter:
    """Cria o formatter padrão do Ubuntu AI Assistant."""

    return logging.Formatter(
        fmt=DEFAULT_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
    )


def build_file_handler(
    config: LoggingRuntimeConfig,
) -> RotatingFileHandler:
    """Cria um handler de arquivo com rotação por tamanho."""

    file_path = config.file_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=config.max_file_size_mb * 1024 * 1024,
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    handler.setLevel(config.numeric_level)
    handler.setFormatter(build_formatter())
    return handler


def build_console_handler(
    config: LoggingRuntimeConfig,
) -> logging.StreamHandler:
    """Cria um handler opcional para saída no terminal."""

    handler = logging.StreamHandler()
    handler.setLevel(config.numeric_level)
    handler.setFormatter(build_formatter())
    return handler
