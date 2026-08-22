from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.agents.specialists import SpecialistPayload
from ubuntu_ai.domain.risk import RiskLevel

SPECIALIST_KINDS = frozenset(
    {AgentKind.SYSTEM, AgentKind.NETWORK, AgentKind.STORAGE, AgentKind.SERVICES}
)


class OrchestrationStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class OrchestrationTask:
    task_id: str
    specialist: AgentKind
    payload: SpecialistPayload
    dependencies: tuple[str, ...] = ()
    context_keys: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task_id não pode estar vazio.")
        if self.specialist not in SPECIALIST_KINDS:
            raise ValueError("A tarefa deve usar um agente especializado.")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError(f"Dependência duplicada na tarefa {self.task_id}.")
        if self.task_id in self.dependencies:
            raise ValueError(f"A tarefa {self.task_id} não pode depender de si mesma.")


@dataclass(frozen=True, slots=True)
class OrchestrationGoal:
    goal_id: str
    description: str
    tasks: tuple[OrchestrationTask, ...]
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("goal_id não pode estar vazio.")
        if not self.description.strip():
            raise ValueError("A descrição do objetivo não pode estar vazia.")
        if not self.tasks:
            raise ValueError("O objetivo exige ao menos uma tarefa.")
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))
        self._validate_graph()

    def _validate_graph(self) -> None:
        identifiers = [task.task_id for task in self.tasks]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("O objetivo contém identificadores de tarefa duplicados.")

        known = set(identifiers)
        for task in self.tasks:
            missing = set(task.dependencies) - known
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(f"Dependência inexistente em {task.task_id}: {names}.")
            unavailable = task.context_keys - self.context.keys()
            if unavailable:
                names = ", ".join(sorted(unavailable))
                raise ValueError(f"Contexto inexistente em {task.task_id}: {names}.")

        dependencies = {task.task_id: set(task.dependencies) for task in self.tasks}
        ready = [task_id for task_id, values in dependencies.items() if not values]
        visited = 0
        while ready:
            completed = ready.pop()
            visited += 1
            for task_id, values in dependencies.items():
                if completed in values:
                    values.remove(completed)
                    if not values:
                        ready.append(task_id)
        if visited != len(self.tasks):
            raise ValueError("O objetivo contém um ciclo de dependências.")


@dataclass(frozen=True, slots=True)
class OrchestrationTaskResult:
    task_id: str
    specialist: AgentKind
    status: OrchestrationStatus
    result: AgentResult | None = None
    shared_context: Mapping[str, Any] = field(default_factory=dict)
    reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "shared_context", MappingProxyType(dict(self.shared_context)))


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    goal_id: str
    status: OrchestrationStatus
    tasks: tuple[OrchestrationTaskResult, ...]
    total_tasks: int

    def __post_init__(self) -> None:
        if self.total_tasks < len(self.tasks):
            raise ValueError("total_tasks não pode ser menor que os resultados.")

    @property
    def progress(self) -> float:
        finished = sum(
            task.status in {OrchestrationStatus.COMPLETED, OrchestrationStatus.FAILED}
            for task in self.tasks
        )
        return finished / self.total_tasks if self.total_tasks else 0.0


class MultiAgentOrchestrator:
    """Coordena planos especializados sem executar comandos diretamente."""

    def __init__(self, coordinator: AgentCoordinator) -> None:
        self._coordinator = coordinator

    def run(self, goal: OrchestrationGoal) -> OrchestrationResult:
        pending = {task.task_id: task for task in goal.tasks}
        completed: set[str] = set()
        results: list[OrchestrationTaskResult] = []

        while pending:
            ready = [
                task
                for task in goal.tasks
                if task.task_id in pending and set(task.dependencies) <= completed
            ]
            if not ready:
                raise RuntimeError("Não foi possível avançar o plano de orquestração.")

            for task in ready:
                shared_context = {key: goal.context[key] for key in sorted(task.context_keys)}
                try:
                    agent_result = self._dispatch(task, shared_context)
                except (PermissionError, TypeError, ValueError, KeyError) as exc:
                    results.append(
                        OrchestrationTaskResult(
                            task_id=task.task_id,
                            specialist=task.specialist,
                            status=OrchestrationStatus.FAILED,
                            shared_context=shared_context,
                            reason=str(exc),
                        )
                    )
                    return OrchestrationResult(
                        goal_id=goal.goal_id,
                        status=OrchestrationStatus.BLOCKED,
                        tasks=tuple(results),
                        total_tasks=len(goal.tasks),
                    )

                results.append(
                    OrchestrationTaskResult(
                        task_id=task.task_id,
                        specialist=task.specialist,
                        status=OrchestrationStatus.COMPLETED,
                        result=agent_result,
                        shared_context=shared_context,
                    )
                )
                completed.add(task.task_id)
                del pending[task.task_id]

        return OrchestrationResult(
            goal_id=goal.goal_id,
            status=OrchestrationStatus.COMPLETED,
            tasks=tuple(results),
            total_tasks=len(goal.tasks),
        )

    def _dispatch(
        self,
        task: OrchestrationTask,
        context: Mapping[str, Any],
    ) -> AgentResult:
        payload = task.payload
        risks = [action.risk for action in payload.actions]
        risk = max(risks, key=_risk_order) if risks else RiskLevel.LOW
        metadata = {
            "risk": risk.value,
            "confirmed": payload.confirmed,
            "environment": payload.environment.value,
            "target": payload.target,
            "context": dict(context),
            "orchestration_task_id": task.task_id,
        }
        return self._coordinator.dispatch(
            AgentTask(kind=task.specialist, payload=payload, metadata=metadata)
        )


def _risk_order(risk: RiskLevel) -> int:
    return {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2,
        RiskLevel.CRITICAL: 3,
    }[risk]
