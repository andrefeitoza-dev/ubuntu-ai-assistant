from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AgentKind(StrEnum):
    """Tipos de agentes especializados suportados pelo runtime."""

    PLANNER = "planner"
    EXECUTION = "execution"
    MEMORY = "memory"
    REFLECTION = "reflection"


@dataclass(frozen=True, slots=True)
class AgentMessage:
    """Mensagem trocada entre agentes."""

    sender: AgentKind
    recipient: AgentKind
    content: str


@dataclass(frozen=True, slots=True)
class AgentTask:
    """Tarefa roteável pelo coordenador."""

    kind: AgentKind
    payload: Any
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Resultado padronizado de uma tarefa de agente."""

    kind: AgentKind
    output: Any
    messages: tuple[AgentMessage, ...] = ()
