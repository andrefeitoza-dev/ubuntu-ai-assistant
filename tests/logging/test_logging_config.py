import logging
from pathlib import Path

import pytest

from ubuntu_ai.logging import (
    LoggingRuntimeConfig,
    build_file_handler,
    build_formatter,
)


def test_logging_runtime_config_builds_file_path(
    tmp_path: Path,
) -> None:
    config = LoggingRuntimeConfig(directory=tmp_path)

    assert config.file_path == tmp_path / "ubuntu-ai.log"
    assert config.numeric_level == logging.INFO


def test_logging_runtime_config_rejects_invalid_values(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="Nível de log inválido"):
        LoggingRuntimeConfig(directory=tmp_path, level="INVALID")

    with pytest.raises(ValueError, match="maior que zero"):
        LoggingRuntimeConfig(directory=tmp_path, max_file_size_mb=0)


def test_build_formatter_uses_standard_fields() -> None:
    formatter = build_formatter()
    record = logging.LogRecord(
        name="ubuntu_ai.planner",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Plano criado",
        args=(),
        exc_info=None,
    )

    rendered = formatter.format(record)

    assert "INFO" in rendered
    assert "ubuntu_ai.planner" in rendered
    assert "Plano criado" in rendered


def test_build_file_handler_creates_log_directory(
    tmp_path: Path,
) -> None:
    config = LoggingRuntimeConfig(directory=tmp_path / "logs")

    handler = build_file_handler(config)

    try:
        assert config.directory.is_dir()
        assert handler.baseFilename == str(config.file_path)
    finally:
        handler.close()
