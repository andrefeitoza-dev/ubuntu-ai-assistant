from pathlib import Path

from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.intent import (
    Intent,
    IntentCategory,
    IntentEntity,
    IntentGoal,
)
from ubuntu_ai.learning.service import LearningService
from ubuntu_ai.learning.sqlite_repository import SQLiteLearningRepository


def test_learning_recommends_by_intent(tmp_path: Path) -> None:
    service = LearningService(SQLiteLearningRepository(tmp_path / "learning.db"))
    service.learn_from_execution(
        user_request="instale docker",
        project_name=None,
        result=ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="ok",
            command="sudo apt install docker.io",
            return_code=0,
        ),
    )
    intent = Intent(
        request="instale docker",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.95,
        entities=(IntentEntity("docker"),),
    )

    recommendations = service.recommend_for_intent(intent)

    assert recommendations[0].pattern.command == "sudo apt install docker.io"
