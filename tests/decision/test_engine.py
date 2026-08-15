from ubuntu_ai.decision.engine import DecisionEngine
from ubuntu_ai.decision.models import DecisionStrategy, ExecutionMode
from ubuntu_ai.planner.models import PlanningProfile


def test_decision_engine_builds_operational_decision() -> None:
    profile = PlanningProfile(
        profiles=("Python Project", "Docker Ready"),
        preferred_tools=("python", "pytest", "ruff", "docker"),
    )
    decision = DecisionEngine().decide(profile)
    assert decision.strategy is DecisionStrategy.AUTOMATION_FIRST
    assert decision.execution_mode is ExecutionMode.CONTAINER
    assert "docker" in decision.preferred_tools
    assert "python" in decision.preferred_skills


def test_empty_profile_defaults_to_balanced_local() -> None:
    decision = DecisionEngine().decide(PlanningProfile())
    assert decision.strategy is DecisionStrategy.BALANCED
    assert decision.execution_mode is ExecutionMode.LOCAL
