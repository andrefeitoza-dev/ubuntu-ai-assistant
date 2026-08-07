from pathlib import Path

from ubuntu_ai.context.discovery.models import EnvironmentSnapshot
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.planner.advisor import PlanningAdvisor


def test_planning_advisor_generates_structured_profile() -> None:
    context = ContextSnapshot(
        session_id="session",
        working_directory=Path("/tmp"),
        operating_system="Linux",
        last_commands=("git status",),
        last_errors=("docker: failed",),
        environment=EnvironmentSnapshot(
            working_directory="/tmp",
            project_name="ubuntu-ai",
            git_repository=True,
            git_branch="main",
            python_version="3.12",
            virtual_environment=".venv",
            docker_available=True,
            ollama_available=True,
            operating_system="Linux",
        ),
    )

    profile = PlanningAdvisor().build(context)

    assert "Git Repository" in profile.profiles
    assert "Python Project" in profile.profiles
    assert "Docker Ready" in profile.profiles
    assert "Local AI Ready" in profile.profiles

    assert "git" in profile.preferred_tools
    assert "python" in profile.preferred_tools
    assert "pytest" in profile.preferred_tools
    assert "ruff" in profile.preferred_tools
    assert "docker" in profile.preferred_tools
    assert "ollama" in profile.preferred_tools

    assert profile.risk_hints


def test_planning_advisor_without_context() -> None:
    profile = PlanningAdvisor().build(None)

    assert profile.is_empty()
    assert profile.to_prompt() == ""