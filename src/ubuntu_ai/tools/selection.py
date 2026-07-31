from __future__ import annotations

import re
from dataclasses import dataclass, replace
from shlex import split

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.learning.service import LearningService
from ubuntu_ai.tools.capability import ToolCapability
from ubuntu_ai.tools.capability_registry import CapabilityRegistry

_TOKEN_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9_.-]+")
_WRAPPERS = {"sudo", "env", "command", "nohup"}


@dataclass(slots=True, frozen=True)
class ToolSelection:
    capability: ToolCapability
    score: float
    reasons: tuple[str, ...]


class ToolSelectionEngine:
    """Seleciona capacidades com base no comando, intenção e histórico."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        learning_service: LearningService | None = None,
    ) -> None:
        self._registry = registry
        self._learning_service = learning_service

    def select(
        self,
        step: PlanStep,
        *,
        request: str,
        project_name: str | None = None,
    ) -> ToolSelection:
        executable = self._executable(step.command)
        context_tokens = self._tokens(
            " ".join((request, step.title, step.description, executable))
        )
        learned = self._learned_scores(request, project_name)

        ranked: list[ToolSelection] = []
        for capability in self._registry.all():
            score = 0.0
            reasons: list[str] = []

            if capability.supports_executable(executable):
                score += 0.65
                reasons.append(f"executável compatível: {executable}")

            intent_tokens = self._tokens(" ".join(capability.intents))
            if intent_tokens:
                overlap = len(context_tokens & intent_tokens) / len(intent_tokens)
                if overlap:
                    score += min(0.2, overlap * 0.2)
                    reasons.append("intenção compatível")

            score += (capability.priority / 100) * 0.05

            learned_score = learned.get(capability.name, 0.0)
            if learned_score:
                score += learned_score * 0.1
                reasons.append("histórico favorável")

            ranked.append(
                ToolSelection(
                    capability=capability,
                    score=round(score, 4),
                    reasons=tuple(reasons),
                )
            )

        ranked.sort(
            key=lambda item: (item.score, item.capability.priority),
            reverse=True,
        )
        best = ranked[0]
        if best.score < 0.15:
            shell = self._registry.get("shell")
            return ToolSelection(shell, 0.1, ("fallback de shell",))
        return best

    def select_plan(
        self,
        plan: Plan,
        *,
        request: str,
        project_name: str | None = None,
    ) -> Plan:
        selected_steps = [
            replace(
                step,
                tool_name=self.select(
                    step,
                    request=request,
                    project_name=project_name,
                ).capability.name,
            )
            for step in plan.steps
        ]
        return replace(plan, steps=selected_steps)

    def _learned_scores(
        self,
        request: str,
        project_name: str | None,
    ) -> dict[str, float]:
        if self._learning_service is None:
            return {}

        scores: dict[str, float] = {}
        for recommendation in self._learning_service.recommend(
            request,
            project_name=project_name,
            limit=20,
        ):
            command = split(recommendation.pattern.command)
            if not command:
                continue
            executable = self._executable(command)
            for capability in self._registry.for_executable(executable):
                scores[capability.name] = max(
                    scores.get(capability.name, 0.0),
                    recommendation.score,
                )
        return scores

    @staticmethod
    def _executable(command: list[str]) -> str:
        if not command:
            raise ValueError("A etapa precisa conter um comando.")
        index = 0
        while index < len(command) - 1 and command[index] in _WRAPPERS:
            index += 1
        return command[index].lower()

    @staticmethod
    def _tokens(value: str) -> frozenset[str]:
        return frozenset(token.lower() for token in _TOKEN_PATTERN.findall(value))
