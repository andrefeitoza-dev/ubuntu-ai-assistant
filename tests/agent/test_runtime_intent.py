from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.intent import IntentCategory, IntentEngine
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline


def test_runtime_exposes_last_interpreted_intent() -> None:
    runtime = AgentRuntime(execution_pipeline=ExecutionPipeline(intent_engine=IntentEngine()))

    runtime.run(AgentTask(request="Instale Docker"))

    assert runtime.last_intent is not None
    assert runtime.last_intent.category is IntentCategory.INSTALLATION
