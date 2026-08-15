from typing import cast

import pytest

from ubuntu_ai import UbuntuAI
from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.pipeline.models import PipelineResult


class FakeAgentRuntime:
    """Runtime controlado utilizado pelos testes do SDK."""

    def __init__(
        self,
        pipeline_result: PipelineResult | None,
    ) -> None:
        self.pipeline_result = pipeline_result
        self.received_task: AgentTask | None = None

    def run(self, task: AgentTask) -> AgentResult:
        self.received_task = task

        return AgentResult(
            success=True,
            message="Planejamento concluído.",
            pipeline_result=self.pipeline_result,
        )


def test_sdk_delegates_request_to_agent_runtime() -> None:
    expected_result = cast(PipelineResult, object())
    runtime = FakeAgentRuntime(
        pipeline_result=expected_result,
    )
    assistant = UbuntuAI(
        agent_runtime=cast(AgentRuntime, runtime),
    )

    result = assistant.plan("Instale Docker")

    assert result is expected_result
    assert runtime.received_task == AgentTask(
        request="Instale Docker",
    )


def test_sdk_plans_request_with_default_runtime() -> None:
    assistant = UbuntuAI()

    result = assistant.plan("Instale Docker")

    assert isinstance(result, PipelineResult)
    assert result.plan.goal == "Instalar e configurar o Docker"
    assert result.preview.dry_run is True
    assert "Execution Preview (DRY RUN)" in result.rendered_preview


def test_sdk_rejects_empty_request() -> None:
    assistant = UbuntuAI()

    with pytest.raises(
        ValueError,
        match="A solicitação não pode estar vazia",
    ):
        assistant.plan("   ")


def test_sdk_raises_error_when_runtime_returns_no_pipeline_result() -> None:
    runtime = FakeAgentRuntime(
        pipeline_result=None,
    )
    assistant = UbuntuAI(
        agent_runtime=cast(AgentRuntime, runtime),
    )

    with pytest.raises(
        RuntimeError,
        match=("O Agent Runtime não retornou um resultado de planejamento"),
    ):
        assistant.plan("Instale Docker")
