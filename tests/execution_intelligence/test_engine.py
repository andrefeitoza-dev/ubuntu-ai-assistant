from ubuntu_ai.domain.plan import PlanStep
from ubuntu_ai.execution_intelligence.engine import ExecutionIntelligence
from ubuntu_ai.tools.capability_registry import CapabilityRegistry
from ubuntu_ai.tools.default_capabilities import default_capabilities


def test_inspects_selected_tool() -> None:
    engine = ExecutionIntelligence(CapabilityRegistry(default_capabilities()))
    report = engine.inspect_step(
        PlanStep(
            title="Python",
            description="Check Python",
            command=["python", "--version"],
            tool_name="python",
        )
    )
    assert report.tool_name == "python"
    assert report.ready is True
