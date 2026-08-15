from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.tools.capability_registry import CapabilityRegistry
from ubuntu_ai.tools.default_capabilities import default_capabilities
from ubuntu_ai.tools.selection import ToolSelectionEngine


def test_planner_enriches_rule_plan_with_selected_tools() -> None:
    planner = Planner(tool_selector=ToolSelectionEngine(CapabilityRegistry(default_capabilities())))

    plan = planner.create_plan("Instale Docker")

    assert [step.tool_name for step in plan.steps] == [
        "apt",
        "apt",
        "systemctl",
        "docker",
    ]
