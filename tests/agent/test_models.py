from ubuntu_ai.agent.models import AgentResult, AgentSession, AgentTask


def test_agent_task_preserves_request() -> None:
    task = AgentTask(request="Analise este projeto")

    assert task.request == "Analise este projeto"


def test_agent_result_preserves_data() -> None:
    result = AgentResult(
        success=True,
        message="Tarefa concluída.",
    )

    assert result.success is True
    assert result.message == "Tarefa concluída."


def test_agent_session_remembers_and_clears_history() -> None:
    session = AgentSession()

    session.remember("Usuário: Olá")
    session.remember("Agente: Olá")

    assert session.history == [
        "Usuário: Olá",
        "Agente: Olá",
    ]

    session.clear()

    assert session.history == []
