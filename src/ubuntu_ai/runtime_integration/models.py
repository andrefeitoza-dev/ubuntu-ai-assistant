from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ubuntu_ai.agents.models import AgentMessage


class RuntimeStage(StrEnum):
    """Etapas do ciclo multiagente."""

    CONTEXT = "context"
    MEMORY = "memory"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class RuntimeRequest:
    """Entrada normalizada para o runtime multiagente."""

    request: object
    session_id: str
    context: object | None = None
    memory_candidates: tuple[object, ...] = ()
    execute: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RuntimeCycleResult:
    """Resultado consolidado de um ciclo multiagente."""

    stage: RuntimeStage
    plan: object | None = None
    execution: object | None = None
    reflection: object | None = None
    memory: object | None = None
    messages: tuple[AgentMessage, ...] = ()
