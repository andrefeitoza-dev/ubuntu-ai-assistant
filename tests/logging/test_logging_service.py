import logging
from pathlib import Path

from ubuntu_ai.logging import LoggingRuntimeConfig, LoggingService


def test_service_returns_namespaced_logger(tmp_path: Path) -> None:
    service = LoggingService(
        LoggingRuntimeConfig(directory=tmp_path),
    )

    try:
        logger = service.get_logger("planner")

        assert logger.name == "ubuntu_ai.planner"
        assert logger.parent is logging.getLogger("ubuntu_ai")
    finally:
        service.shutdown()


def test_service_writes_message_to_file(tmp_path: Path) -> None:
    service = LoggingService(
        LoggingRuntimeConfig(directory=tmp_path, level="DEBUG"),
    )

    try:
        service.info("Plano criado", component="planner")

        for handler in logging.getLogger("ubuntu_ai").handlers:
            handler.flush()

        content = (tmp_path / "ubuntu-ai.log").read_text(
            encoding="utf-8"
        )

        assert "Plano criado" in content
        assert "ubuntu_ai.planner" in content
    finally:
        service.shutdown()


def test_service_configures_namespace_only_once(tmp_path: Path) -> None:
    service = LoggingService(
        LoggingRuntimeConfig(directory=tmp_path),
    )

    try:
        service.configure()
        first_handlers = tuple(logging.getLogger("ubuntu_ai").handlers)

        service.configure()
        second_handlers = tuple(logging.getLogger("ubuntu_ai").handlers)

        assert first_handlers == second_handlers
        assert len(second_handlers) == 1
    finally:
        service.shutdown()


def test_service_can_enable_console_handler(tmp_path: Path) -> None:
    service = LoggingService(
        LoggingRuntimeConfig(
            directory=tmp_path,
            console_enabled=True,
        ),
    )

    try:
        service.configure()

        handlers = logging.getLogger("ubuntu_ai").handlers

        assert len(handlers) == 2
    finally:
        service.shutdown()
