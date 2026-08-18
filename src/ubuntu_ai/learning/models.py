from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class LearningOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"


@dataclass(slots=True, frozen=True)
class LearningPattern:
    id: str
    created_at: datetime
    updated_at: datetime
    request_pattern: str
    command: str
    project_name: str | None = None
    success_count: int = 0
    failure_count: int = 0
    blocked_count: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0

    @classmethod
    def create(
        cls,
        *,
        request_pattern: str,
        command: str,
        project_name: str | None = None,
    ) -> LearningPattern:
        now = datetime.now(UTC)
        return cls(
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
            request_pattern=request_pattern,
            command=command,
            project_name=project_name,
        )

    @property
    def attempts(self) -> int:
        return self.success_count + self.failure_count + self.blocked_count

    @property
    def confidence(self) -> float:
        weighted_success = self.success_count + (0.5 * self.positive_feedback)
        weighted_total = self.attempts + self.positive_feedback + self.negative_feedback
        if weighted_total == 0:
            return 0.0
        return max(0.0, min(1.0, weighted_success / weighted_total))

    @property
    def approved_for_reuse(self) -> bool:
        """Exige sucesso e aprovação explícita sem histórico negativo."""

        return (
            self.success_count > 0
            and self.positive_feedback > 0
            and self.failure_count == 0
            and self.blocked_count == 0
            and self.negative_feedback == 0
        )

    def with_outcome(self, outcome: LearningOutcome) -> LearningPattern:
        changes = {"updated_at": datetime.now(UTC)}
        if outcome is LearningOutcome.SUCCESS:
            changes["success_count"] = self.success_count + 1
        elif outcome is LearningOutcome.FAILURE:
            changes["failure_count"] = self.failure_count + 1
        else:
            changes["blocked_count"] = self.blocked_count + 1
        return replace(self, **changes)

    def with_feedback(self, *, helpful: bool) -> LearningPattern:
        changes: dict[str, object] = {"updated_at": datetime.now(UTC)}
        field = "positive_feedback" if helpful else "negative_feedback"
        changes[field] = getattr(self, field) + 1
        return replace(self, **changes)


@dataclass(slots=True, frozen=True)
class LearningRecommendation:
    pattern: LearningPattern
    relevance: float

    @property
    def score(self) -> float:
        return round((0.65 * self.relevance) + (0.35 * self.pattern.confidence), 4)
