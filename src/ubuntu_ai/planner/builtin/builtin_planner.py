from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.planner.builtin.file_search import SafeFileSearchPlanner
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
    "favor",
}


@dataclass(frozen=True, slots=True)
class BuiltinMatch:
    command: BuiltinCommand
    keyword: str
    confidence: float


class BuiltinPlanner:
    """Cria planos determinísticos simples sem utilizar IA."""

    def __init__(self, file_search: SafeFileSearchPlanner | None = None) -> None:
        self._file_search = file_search or SafeFileSearchPlanner()

    def try_create_plan(self, request: str) -> Plan | None:
        """Retorna um plano builtin ou None quando não houver correspondência."""

        file_search_plan = self._file_search.try_create_plan(request)
        if file_search_plan is not None:
            return file_search_plan
        if self._file_search.has_search_intent(request):
            return None

        normalized_request = self._normalize(request)

        if not normalized_request:
            return None

        match = self._match(normalized_request)

        if match is None:
            return None

        return self._build_plan(match.command)

    def rejection_reason(self, request: str) -> str | None:
        """Explica por que uma consulta builtin foi recusada antes do fallback."""

        return self._file_search.rejection_reason(request)

    def find_match(self, request: str) -> BuiltinMatch | None:
        """Retorna a melhor correspondência e sua confiança, sem criar plano."""

        normalized = self._normalize(request)
        return self._match(normalized) if normalized else None

    def _match(
        self,
        normalized_request: str,
    ) -> BuiltinMatch | None:
        matches: list[BuiltinMatch] = []
        for command in BUILTIN_COMMANDS:
            for keyword in command.keywords:
                normalized_keyword = self._normalize(keyword)
                confidence = self._confidence(normalized_request, normalized_keyword)
                if confidence >= 0.78:
                    matches.append(BuiltinMatch(command, keyword, confidence))

        if not matches:
            return None

        return max(
            matches,
            key=lambda match: (
                match.confidence,
                len(self._normalize(match.keyword).split()),
                len(match.keyword),
            ),
        )

    @staticmethod
    def _confidence(request: str, keyword: str) -> float:
        if not keyword:
            return 0.0
        if request == keyword:
            return 1.0

        request_tokens = set(request.split())
        keyword_tokens = set(keyword.split())
        if keyword_tokens and keyword_tokens <= request_tokens:
            specificity = min(len(keyword_tokens), 4) * 0.015
            return min(0.98, 0.90 + specificity)

        if min(len(request), len(keyword)) < 5:
            return 0.0

        sequence = SequenceMatcher(None, request, keyword).ratio()
        union = request_tokens | keyword_tokens
        token_similarity = len(request_tokens & keyword_tokens) / len(union) if union else 0.0
        return max(sequence, token_similarity)

    @staticmethod
    def _build_plan(command: BuiltinCommand) -> Plan:
        plan = Plan(
            goal=command.goal,
            estimated_seconds=command.estimated_seconds,
            risk=command.risk,
            planner="builtin",
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

        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()

        words = [word for word in value.split() if word not in _STOP_WORDS]

        return " ".join(words)
