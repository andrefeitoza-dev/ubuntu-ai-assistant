from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.agents.models import AgentKind, AgentTask


@dataclass(frozen=True, slots=True)
class AgentPolicyDecision:
    allowed: bool
    reason: str


class AgentPolicy:
    """Política simples para validar despacho de tarefas."""

    def evaluate(self, task: AgentTask) -> AgentPolicyDecision:
        if task.kind is AgentKind.EXECUTION and task.payload is None:
            return AgentPolicyDecision(
                allowed=False,
                reason="Execução sem payload não é permitida.",
            )

        return AgentPolicyDecision(
            allowed=True,
            reason="Tarefa permitida.",
        )
