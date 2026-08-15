from __future__ import annotations

from ubuntu_ai.decision.models import DecisionStrategy, ExecutionMode
from ubuntu_ai.planner.models import PlanningProfile


def choose_strategy(profile: PlanningProfile) -> DecisionStrategy:
    if profile.risk_hints:
        return DecisionStrategy.CONSERVATIVE
    if "Docker Ready" in profile.profiles:
        return DecisionStrategy.AUTOMATION_FIRST
    return DecisionStrategy.BALANCED


def choose_execution_mode(profile: PlanningProfile) -> ExecutionMode:
    if profile.risk_hints:
        return ExecutionMode.REVIEW
    if "docker" in profile.preferred_tools:
        return ExecutionMode.CONTAINER
    return ExecutionMode.LOCAL


def preferred_skills(profile: PlanningProfile) -> tuple[str, ...]:
    mapping = {
        "git": "git",
        "python": "python",
        "pytest": "python",
        "ruff": "python",
        "docker": "docker",
        "ollama": "ai",
    }
    skills: list[str] = []
    for tool in profile.preferred_tools:
        skill = mapping.get(tool)
        if skill is not None and skill not in skills:
            skills.append(skill)
    return tuple(skills)
