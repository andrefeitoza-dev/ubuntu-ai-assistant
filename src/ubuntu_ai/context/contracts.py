from __future__ import annotations

from typing import Protocol


class SessionState(Protocol):
    """Visão mínima de uma sessão necessária ao contexto."""

    history: list[str]


class SessionHistoryReader(Protocol):
    """Contrato somente leitura para consultar o histórico da sessão."""

    @property
    def session(self) -> SessionState:
        """Retorna a sessão disponível para leitura."""
        ...
