from __future__ import annotations

from collections import deque
from typing import Any

from ubuntu_ai.reflection.v2 import ReflectionEngineV2, ReflectionV2Report


class ReflectionV2Service:
    """Serviço de alto nível com histórico limitado de reflexões."""

    def __init__(
        self,
        engine: ReflectionEngineV2 | None = None,
        history_limit: int = 20,
    ) -> None:
        if history_limit < 1:
            raise ValueError("history_limit deve ser maior que zero.")

        self._engine = engine or ReflectionEngineV2()
        self._history: deque[ReflectionV2Report] = deque(maxlen=history_limit)

    def reflect_execution(self, result: Any) -> ReflectionV2Report:
        report = self._engine.reflect_execution_result(result)
        self._history.append(report)
        return report

    def history(self) -> tuple[ReflectionV2Report, ...]:
        return tuple(self._history)
