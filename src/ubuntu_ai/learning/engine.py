from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.learning.models import LearningPattern, LearningRecommendation
from ubuntu_ai.learning.service import LearningService


class LearningEngine:
    """Fachada de alto nível para aprendizado e recomendações."""

    def __init__(self, service: LearningService) -> None:
        self._service = service

    def observe_execution(
        self,
        *,
        user_request: str,
        project_name: str | None,
        result: ExecutionResult,
    ) -> LearningPattern:
        return self._service.learn_from_execution(
            user_request=user_request,
            project_name=project_name,
            result=result,
        )

    def recommendations(
        self,
        request: str,
        *,
        project_name: str | None = None,
        limit: int = 5,
    ) -> tuple[LearningRecommendation, ...]:
        return self._service.recommend(request, project_name=project_name, limit=limit)
