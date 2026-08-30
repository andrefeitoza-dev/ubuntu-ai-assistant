from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.planner.builtin.capability_actions import CapabilityActionPlanner
from ubuntu_ai.planner.builtin.desktop_action import SafeDesktopActionPlanner
from ubuntu_ai.planner.builtin.file_operations import SafeFileOperationPlanner
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

    def __init__(
        self,
        file_search: SafeFileSearchPlanner | None = None,
        desktop_action: SafeDesktopActionPlanner | None = None,
        capability_actions: CapabilityActionPlanner | None = None,
        file_operations: SafeFileOperationPlanner | None = None,
    ) -> None:
        self._file_search = file_search or SafeFileSearchPlanner()
        self._desktop_action = desktop_action or SafeDesktopActionPlanner()
        self._capability_actions = capability_actions or CapabilityActionPlanner()
        self._file_operations = file_operations or SafeFileOperationPlanner()

    def try_create_plan(self, request: str) -> Plan | None:
        """Retorna um plano builtin ou None quando não houver correspondência."""

        capability_plan = self._capability_actions.try_create_plan(request)
        if capability_plan is not None:
            return capability_plan

        file_operation_plan = self._file_operations.try_create_plan(request)
        if file_operation_plan is not None:
            return file_operation_plan
        if self._file_operations.has_file_operation_intent(request):
            return None

        desktop_plan = self._desktop_action.try_create_plan(request)
        if desktop_plan is not None:
            return desktop_plan
        if self._desktop_action.has_desktop_intent(request):
            return None

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

        return (
            self._file_operations.rejection_reason(request)
            or self._desktop_action.rejection_reason(request)
            or self._file_search.rejection_reason(request)
        )

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

        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode().lower()
        value = re.sub(r"[^a-z0-9_./\s-]", " ", value)

        words = [word for word in value.split() if word not in _STOP_WORDS]

        return " ".join(words)
