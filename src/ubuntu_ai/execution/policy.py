from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ubuntu_ai.execution.models import ExecutionRequest


@dataclass(slots=True, frozen=True)
class PolicyDecision:
    """Resultado da avaliação de uma solicitação de execução."""

    allowed: bool
    reason: str = ""


class ExecutionPolicy(Protocol):
    """Contrato para políticas responsáveis por autorizar execuções."""

    def evaluate(self, request: ExecutionRequest) -> PolicyDecision:
        """Avalia se uma solicitação pode ser executada."""
        ...
