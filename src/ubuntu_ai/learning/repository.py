from __future__ import annotations

from typing import Protocol

from ubuntu_ai.learning.models import LearningOutcome, LearningPattern


class LearningRepository(Protocol):
    def record_outcome(
        self,
        pattern: LearningPattern,
        outcome: LearningOutcome,
    ) -> LearningPattern: ...

    def get_pattern(self, pattern_id: str) -> LearningPattern | None: ...

    def list_patterns(
        self,
        *,
        project_name: str | None = None,
        limit: int = 100,
    ) -> tuple[LearningPattern, ...]: ...

    def record_feedback(self, pattern_id: str, *, helpful: bool) -> LearningPattern: ...
