from ubuntu_ai.agent_loop import AgentReplanner
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus


def test_replanner_preserves_goal_and_failure_evidence() -> None:
    request = AgentReplanner().build_request(
        goal="instalar docker",
        iteration=1,
        results=(
            ExecutionResult(
                status=ExecutionStatus.FAILED,
                message="falhou",
                command="apt install docker",
                return_code=1,
                stderr="pacote inexistente",
            ),
        ),
    )

    assert "instalar docker" in request
    assert "pacote inexistente" in request
    assert "abordagem diferente" in request
