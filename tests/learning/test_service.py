from pathlib import Path

from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.learning.service import LearningService
from ubuntu_ai.learning.sqlite_repository import SQLiteLearningRepository


def test_service_learns_and_recommends_similar_execution(tmp_path: Path) -> None:
    service = LearningService(SQLiteLearningRepository(tmp_path / "learning.db"))
    service.learn_from_execution(
        user_request="Listar arquivos do projeto",
        project_name="ubuntu-ai",
        result=ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="ok",
            command="ls -la",
            return_code=0,
        ),
    )

    recommendations = service.recommend("listar arquivos", project_name="ubuntu-ai")

    assert recommendations[0].pattern.command == "ls -la"
    assert "funcionou anteriormente" in (service.context_for_prompt("listar arquivos") or "")
