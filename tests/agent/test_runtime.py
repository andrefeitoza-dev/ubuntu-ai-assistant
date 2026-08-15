from pathlib import Path
from typing import cast

import pytest

from ubuntu_ai.agent.context import AgentContext
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.agent.session import SessionManager
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.pipeline.models import PipelineResult


class FakeContextProvider:
    """Fornece um contexto previsível para os testes."""

    def get_context(self) -> AgentContext:
        return AgentContext(
            working_directory=Path("/tmp/ubuntu-ai"),
            operating_system="Linux",
            project_name="ubuntu-ai-assistant",
        )


class FakePipelineResult:
    """Resultado mínimo necessário para testar o runtime."""

    def __init__(self, rendered_preview: str) -> None:
        self.rendered_preview = rendered_preview


class FakeExecutionPipeline:
    """Simula o pipeline sem acessar planejadores ou serviços externos."""

    def __init__(self) -> None:
        self.received_request: str | None = None
        self.result = cast(
            PipelineResult,
            FakePipelineResult(
                rendered_preview="Preview seguro para: Analise este projeto",
            ),
        )

    def run(self, request: str) -> PipelineResult:
        self.received_request = request
        return self.result


def create_runtime(
    pipeline: FakeExecutionPipeline,
    session_manager: SessionManager | None = None,
) -> AgentRuntime:
    """Cria um runtime configurado com dependências de teste."""

    return AgentRuntime(
        execution_pipeline=cast(ExecutionPipeline, pipeline),
        session_manager=session_manager,
        context_provider=FakeContextProvider(),
    )


def test_runtime_processes_task_through_pipeline() -> None:
    pipeline = FakeExecutionPipeline()
    runtime = create_runtime(pipeline)

    result = runtime.run(
        AgentTask(request="Analise este projeto"),
    )

    assert result.success is True
    assert result.message == "Preview seguro para: Analise este projeto"
    assert result.pipeline_result is pipeline.result
    assert pipeline.received_request == "Analise este projeto"


def test_runtime_records_interaction_and_context_in_session() -> None:
    pipeline = FakeExecutionPipeline()
    session_manager = SessionManager()
    runtime = create_runtime(
        pipeline=pipeline,
        session_manager=session_manager,
    )

    runtime.run(
        AgentTask(request="Analise este projeto"),
    )

    assert session_manager.session.history == [
        "Usuário: Analise este projeto",
        ("Contexto: diretório=/tmp/ubuntu-ai; projeto=ubuntu-ai-assistant; sistema=Linux"),
        "Agente: Preview seguro para: Analise este projeto",
    ]


def test_runtime_strips_request_before_sending_to_pipeline() -> None:
    pipeline = FakeExecutionPipeline()
    runtime = create_runtime(pipeline)

    runtime.run(
        AgentTask(request="  Analise este projeto  "),
    )

    assert pipeline.received_request == "Analise este projeto"


def test_runtime_exposes_session_manager() -> None:
    pipeline = FakeExecutionPipeline()
    session_manager = SessionManager()
    runtime = create_runtime(
        pipeline=pipeline,
        session_manager=session_manager,
    )

    assert runtime.session_manager is session_manager


def test_runtime_returns_current_context() -> None:
    pipeline = FakeExecutionPipeline()
    runtime = create_runtime(pipeline)

    context = runtime.get_context()

    assert context.working_directory == Path("/tmp/ubuntu-ai")
    assert context.operating_system == "Linux"
    assert context.project_name == "ubuntu-ai-assistant"


def test_runtime_rejects_empty_task() -> None:
    pipeline = FakeExecutionPipeline()
    runtime = create_runtime(pipeline)

    with pytest.raises(
        ValueError,
        match="A solicitação não pode estar vazia",
    ):
        runtime.run(
            AgentTask(request="   "),
        )

    assert pipeline.received_request is None
