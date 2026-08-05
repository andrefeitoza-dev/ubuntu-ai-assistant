from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from ubuntu_ai.logging.config import (
    LoggingRuntimeConfig,
    build_console_handler,
    build_file_handler,
)


class LoggingService:
    """Configura e fornece loggers padronizados da aplicação."""

    def __init__(
        self,
        config: LoggingRuntimeConfig,
        *,
        namespace: str = "ubuntu_ai",
    ) -> None:
        self._config = config
        self._namespace = namespace.strip() or "ubuntu_ai"
        self._configured = False

    @property
    def config(self) -> LoggingRuntimeConfig:
        """Retorna a configuração usada pelo serviço."""

        return self._config

    def configure(self) -> None:
        """Configura o logger raiz do namespace uma única vez."""

        if self._configured:
            return

        logger = logging.getLogger(self._namespace)
        logger.setLevel(self._config.numeric_level)
        logger.propagate = False

        self._remove_managed_handlers(logger)
        logger.addHandler(build_file_handler(self._config))

        if self._config.console_enabled:
            logger.addHandler(build_console_handler(self._config))

        self._configured = True

    def get_logger(self, component: str | None = None) -> logging.Logger:
        """Retorna um logger filho para um componente da aplicação."""

        self.configure()

        if component is None or not component.strip():
            return logging.getLogger(self._namespace)

        normalized_component = component.strip().replace(" ", "_")
        return logging.getLogger(
            f"{self._namespace}.{normalized_component}"
        )

    def info(
        self,
        message: str,
        *,
        component: str | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        """Registra um evento informativo."""

        self.get_logger(component).info(
            message,
            extra=dict(extra or {}),
        )

    def warning(
        self,
        message: str,
        *,
        component: str | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        """Registra um aviso."""

        self.get_logger(component).warning(
            message,
            extra=dict(extra or {}),
        )

    def error(
        self,
        message: str,
        *,
        component: str | None = None,
        extra: Mapping[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Registra um erro, opcionalmente com traceback."""

        self.get_logger(component).error(
            message,
            extra=dict(extra or {}),
            exc_info=exc_info,
        )

    def shutdown(self) -> None:
        """Fecha handlers gerenciados e libera arquivos de log."""

        logger = logging.getLogger(self._namespace)
        self._remove_managed_handlers(logger)
        self._configured = False

    @staticmethod
    def _remove_managed_handlers(logger: logging.Logger) -> None:
        for handler in tuple(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
