from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.domain.risk import RiskLevel


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

        risk_value = task.metadata.get("risk")
        try:
            risk = RiskLevel(risk_value) if risk_value is not None else RiskLevel.LOW
        except ValueError:
            return AgentPolicyDecision(
                allowed=False,
                reason="Classificação de risco inválida.",
            )
        if risk is RiskLevel.CRITICAL:
            return AgentPolicyDecision(
                allowed=False,
                reason="Agentes não podem despachar ações CRITICAL.",
            )
        if risk is not RiskLevel.LOW and not task.metadata.get("confirmed", False):
            return AgentPolicyDecision(
                allowed=False,
                reason="Ação sensível exige confirmação central.",
            )
        if task.metadata.get("environment") == "remote" and not task.metadata.get("target"):
            return AgentPolicyDecision(
                allowed=False,
                reason="Tarefa remota exige destino explícito.",
            )

        return AgentPolicyDecision(
            allowed=True,
            reason="Tarefa permitida.",
        )
