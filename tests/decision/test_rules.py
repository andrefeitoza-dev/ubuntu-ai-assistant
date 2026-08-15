from ubuntu_ai.decision.models import DecisionStrategy, ExecutionMode
from ubuntu_ai.decision.rules import choose_execution_mode, choose_strategy, preferred_skills
from ubuntu_ai.planner.models import PlanningProfile


def test_risk_prefers_conservative_review() -> None:
    profile = PlanningProfile(risk_hints=("falha recente",), preferred_tools=("docker",))
    assert choose_strategy(profile) is DecisionStrategy.CONSERVATIVE
    assert choose_execution_mode(profile) is ExecutionMode.REVIEW


def test_docker_profile_prefers_automation_container() -> None:
    profile = PlanningProfile(profiles=("Docker Ready",), preferred_tools=("docker",))
    assert choose_strategy(profile) is DecisionStrategy.AUTOMATION_FIRST
    assert choose_execution_mode(profile) is ExecutionMode.CONTAINER


def test_preferred_skills_are_derived_from_tools() -> None:
    profile = PlanningProfile(
        preferred_tools=("git", "python", "pytest", "ruff", "docker", "ollama")
    )
    assert preferred_skills(profile) == ("git", "python", "docker", "ai")
