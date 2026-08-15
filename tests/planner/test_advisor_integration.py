from pathlib import Path

from ubuntu_ai.ai import AIResponse
from ubuntu_ai.context.discovery.models import EnvironmentSnapshot
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.planner.ai_planner import AIPlanner


class FakeProvider:
    def __init__(self) -> None:
        self.request = None

    def generate(self, request):
        self.request = request

        return AIResponse(
            content=(
                "{"
                '"goal":"teste",'
                '"estimated_seconds":10,'
                '"risk":"low",'
                '"steps":['
                "{"
                '"title":"teste",'
                '"description":"teste",'
                '"command":["echo","ok"]'
                "}"
                "]"
                "}"
            )
        )


def test_ai_planner_includes_environment_advice() -> None:
    provider = FakeProvider()
    planner = AIPlanner(provider)

    context = ContextSnapshot(
        session_id="session",
        working_directory=Path("/tmp/project"),
        operating_system="Linux",
        environment=EnvironmentSnapshot(
            working_directory="/tmp/project",
            project_name="project",
            git_repository=True,
            git_branch="main",
            python_version="3.12",
            virtual_environment=".venv",
            docker_available=True,
            ollama_available=True,
            operating_system="Linux",
        ),
    )

    planner.create_plan(
        "Configure o ambiente",
        context=context,
    )

    assert provider.request is not None

    prompt = provider.request.prompt

    # Seção adicionada pelo Prompt Builder
    assert "Recomendações de planejamento:" in prompt

    # Perfis produzidos pelo PlanningAdvisor
    assert "Git Repository" in prompt
    assert "Python Project" in prompt
    assert "Docker Ready" in prompt
    assert "Local AI Ready" in prompt

    # Recomendações produzidas pelo PlanningAdvisor
    assert "histórico Git" in prompt
    assert "ambiente virtual" in prompt
    assert "Docker" in prompt
    assert "Ollama" in prompt
