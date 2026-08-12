from __future__ import annotations

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.planner.builtin.registry import (
    BUILTIN_COMMANDS,
    BuiltinCommand,
)


class BuiltinPlanner:
    """Cria planos determinísticos simples sem utilizar IA."""

    def try_create_plan(self, request: str) -> Plan | None:
        """Retorna um plano builtin ou None quando não houver correspondência."""

        normalized_request = self._normalize(request)

        if not normalized_request:
            return None

        command = self._match(normalized_request)

        if command is None:
            return None

        return self._build_plan(command)

    def _match(self, normalized_request: str) -> BuiltinCommand | None:
        for command in BUILTIN_COMMANDS:
            if any(
                keyword in normalized_request
                for keyword in command.keywords
            ):
                return command

        return None

    @staticmethod
    def _build_plan(command: BuiltinCommand) -> Plan:
        plan = Plan(
            goal=command.goal,
            estimated_seconds=command.estimated_seconds,
            risk=command.risk,
        )

        plan.add_step(
            PlanStep(
                title=command.title,
                description=command.description,
                command=list(command.command),
            )
        )

        return plan

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.strip().lower().split())