from pathlib import Path

from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.context.engine import ContextEngine
from ubuntu_ai.conversation.engine import ConversationEngine
from ubuntu_ai.conversation.service import ConversationService
from ubuntu_ai.conversation.sqlite_repository import SQLiteConversationRepository


class PipelineDouble:
    def __init__(self) -> None:
        self.context = None

    def run(self, request, context=None):
        from ubuntu_ai.domain.plan import Plan
        from ubuntu_ai.domain.risk import RiskLevel
        from ubuntu_ai.executor.preview import PreviewBuilder
        from ubuntu_ai.pipeline.models import PipelineResult
        from ubuntu_ai.renderer.preview_renderer import PreviewRenderer

        self.context = context
        plan = Plan(goal=request, estimated_seconds=1, risk=RiskLevel.LOW)
        preview = PreviewBuilder().build(plan)
        return PipelineResult(
            plan=plan,
            preview=preview,
            rendered_preview=PreviewRenderer().render(preview),
        )


def test_runtime_persists_conversation_and_enriches_context(tmp_path: Path) -> None:
    pipeline = PipelineDouble()
    conversation = ConversationEngine(
        ConversationService(
            SQLiteConversationRepository(tmp_path / "memory.db")
        )
    )
    runtime = AgentRuntime(
        execution_pipeline=pipeline,
        context_engine=ContextEngine(),
        conversation_engine=conversation,
    )

    runtime.run(AgentTask(request="install docker"))

    assert pipeline.context is not None
    assert pipeline.context.conversation_history[0] == "user: install docker"
    assert pipeline.context.conversation_history[-1].startswith("user:")
