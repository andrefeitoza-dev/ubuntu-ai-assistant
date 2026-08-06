from __future__ import annotations

from abc import ABC, abstractmethod

from ubuntu_ai.intent.models import Intent


class IntentRepository(ABC):
    """Contrato de persistência do histórico de intenções."""

    @abstractmethod
    def save(self, intent: Intent) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_recent(self, limit: int = 20) -> tuple[Intent, ...]:
        raise NotImplementedError


class InMemoryIntentRepository(IntentRepository):
    """Repositório em memória adequado para testes e composição inicial."""

    def __init__(self) -> None:
        self._items: list[Intent] = []

    def save(self, intent: Intent) -> None:
        self._items.append(intent)

    def list_recent(self, limit: int = 20) -> tuple[Intent, ...]:
        if limit <= 0:
            raise ValueError("O limite deve ser maior que zero.")
        return tuple(reversed(self._items[-limit:]))
