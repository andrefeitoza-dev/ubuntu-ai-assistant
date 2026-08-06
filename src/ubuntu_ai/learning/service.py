from __future__ import annotations

import re
from collections.abc import Iterable

from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.intent.context import IntentContextBuilder
from ubuntu_ai.intent.models import Intent
from ubuntu_ai.learning.models import (
    LearningOutcome,
    LearningPattern,
    LearningRecommendation,
)
from ubuntu_ai.learning.repository import LearningRepository

_TOKEN_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9_./-]+")


class LearningService:
    def __init__(self, repository: LearningRepository) -> None:
        self._repository = repository

    def learn_from_execution(
        self,
        *,
        user_request: str,
        project_name: str | None,
        result: ExecutionResult,
    ) -> LearningPattern:
        if result.command is None:
            raise ValueError("O resultado precisa conter o comando executado.")
        outcome = self._outcome_for(result.status)
        pattern = LearningPattern.create(
            request_pattern=self.normalize_request(user_request),
            command=result.command,
            project_name=project_name,
        )
        return self._repository.record_outcome(pattern, outcome)

    def recommend(
        self,
        request: str,
        *,
        project_name: str | None = None,
        limit: int = 5,
    ) -> tuple[LearningRecommendation, ...]:
        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")
        normalized = self.normalize_request(request)
        request_tokens = self._tokens(normalized)
        recommendations: list[LearningRecommendation] = []
        for pattern in self._repository.list_patterns(project_name=project_name, limit=200):
            relevance = self._similarity(request_tokens, self._tokens(pattern.request_pattern))
            if relevance == 0:
                continue
            recommendations.append(LearningRecommendation(pattern, relevance))
        recommendations.sort(key=lambda item: item.score, reverse=True)
        return tuple(recommendations[:limit])

    def recommend_for_intent(
        self,
        intent: Intent,
        *,
        project_name: str | None = None,
        limit: int = 5,
        context_builder: IntentContextBuilder | None = None,
    ) -> tuple[LearningRecommendation, ...]:
        """Recomenda padrões usando a representação estruturada da intenção."""

        builder = context_builder or IntentContextBuilder()
        return self.recommend(
            builder.search_query(intent),
            project_name=project_name,
            limit=limit,
        )

    def context_for_intent(
        self,
        intent: Intent,
        *,
        project_name: str | None = None,
        limit: int = 5,
        context_builder: IntentContextBuilder | None = None,
    ) -> str | None:
        """Monta contexto de aprendizado orientado pela intenção."""

        builder = context_builder or IntentContextBuilder()
        return self.context_for_prompt(
            builder.search_query(intent),
            project_name=project_name,
            limit=limit,
        )

    def context_for_prompt(
        self,
        request: str,
        *,
        project_name: str | None = None,
        limit: int = 5,
    ) -> str | None:
        recommendations = self.recommend(request, project_name=project_name, limit=limit)
        if not recommendations:
            return None
        lines: list[str] = []
        for item in recommendations:
            pattern = item.pattern
            if pattern.success_count > pattern.failure_count + pattern.blocked_count:
                label = "funcionou anteriormente"
            else:
                label = "teve falhas ou bloqueios; valide antes de reutilizar"
            lines.append(
                f"- Pedido semelhante: {pattern.request_pattern}; comando: {pattern.command}; "
                f"{label}; sucesso={pattern.success_count}, falha={pattern.failure_count}, "
                f"bloqueio={pattern.blocked_count}, confiança={pattern.confidence:.2f}"
            )
        return "\n".join(lines)

    def record_feedback(self, pattern_id: str, *, helpful: bool) -> LearningPattern:
        return self._repository.record_feedback(pattern_id, helpful=helpful)

    @staticmethod
    def normalize_request(request: str) -> str:
        normalized = " ".join(request.strip().lower().split())
        if not normalized:
            raise ValueError("A solicitação não pode estar vazia.")
        return normalized

    @staticmethod
    def _outcome_for(status: ExecutionStatus) -> LearningOutcome:
        if status is ExecutionStatus.EXECUTED:
            return LearningOutcome.SUCCESS
        if status is ExecutionStatus.BLOCKED:
            return LearningOutcome.BLOCKED
        return LearningOutcome.FAILURE

    @staticmethod
    def _tokens(value: str) -> frozenset[str]:
        return frozenset(token.lower() for token in _TOKEN_PATTERN.findall(value))

    @staticmethod
    def _similarity(left: Iterable[str], right: Iterable[str]) -> float:
        left_set = set(left)
        right_set = set(right)
        union = left_set | right_set
        if not union:
            return 0.0
        return len(left_set & right_set) / len(union)
