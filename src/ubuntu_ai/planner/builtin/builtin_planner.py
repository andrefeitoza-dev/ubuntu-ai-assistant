from __future__ import annotations

import unicodedata

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.planner.builtin.registry import (
    BUILTIN_COMMANDS,
    BuiltinCommand,
)


_STOP_WORDS = {
    "o",
    "a",
    "os",
    "as",
    "um",
    "uma",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "para",
    "por",
    "com",
    "no",
    "na",
    "nos",
    "nas",
    "me",
    "meu",
    "minha",
    "mostrar",
    "mostre",
    "mostrar-me",
    "ver",
    "veja",
    "quero",
    "por",
    "favor",
}


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

    def _match(
        self,
        normalized_request: str,
    ) -> BuiltinCommand | None:

        for command in BUILTIN_COMMANDS:
            for keyword in command.keywords:
                normalized_keyword = self._normalize(keyword)

                if normalized_keyword in normalized_request:
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

    @classmethod
    def _normalize(cls, value: str) -> str:

        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode()
            .lower()
        )

        words = [
            word
            for word in value.split()
            if word not in _STOP_WORDS
        ]

        return " ".join(words)