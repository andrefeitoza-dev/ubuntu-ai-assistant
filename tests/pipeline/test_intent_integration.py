from ubuntu_ai.intent import IntentCategory, IntentEngine, IntentGoal
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline


def test_pipeline_interprets_request_and_exposes_intent() -> None:
    pipeline = ExecutionPipeline(intent_engine=IntentEngine())

    result = pipeline.run("Instale Docker")

    assert result.intent is not None
    assert result.intent.category is IntentCategory.INSTALLATION
    assert result.intent.goal is IntentGoal.PROVISION
    assert result.intent.request == "Instale Docker"


def test_pipeline_accepts_preclassified_intent() -> None:
    engine = IntentEngine()
    intent = engine.interpret("Instale Docker")
    pipeline = ExecutionPipeline(intent_engine=engine)

    result = pipeline.run(intent)

    assert result.intent is intent
    assert result.plan.goal
