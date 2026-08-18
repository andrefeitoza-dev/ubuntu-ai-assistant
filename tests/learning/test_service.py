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


def test_service_only_promotes_explicitly_approved_pattern(tmp_path: Path) -> None:
    service = LearningService(SQLiteLearningRepository(tmp_path / "learning.db"))
    pattern = service.learn_from_execution(
        user_request="exibir os itens deste local",
        project_name=None,
        result=ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="ok",
            command="ls",
            return_code=0,
        ),
    )

    assert service.approved_recommendations("exibir itens deste local") == ()

    service.record_feedback(pattern.id, helpful=True)
    approved = service.approved_recommendations("exibir os itens deste local")

    assert approved
    assert approved[0].pattern.command == "ls"
