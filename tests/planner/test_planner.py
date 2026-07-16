import pytest

from ubuntu_ai.ai import AIProvider, AIRequest, AIResponse
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.ai_planner import AIPlanner
from ubuntu_ai.planner.planner import Planner


class FakeAIProvider(AIProvider):
    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content="""
            {
              "goal": "Instalar PostgreSQL",
              "estimated_seconds": 180,
              "risk": "high",
              "steps": [
                {
                  "title": "Instalar PostgreSQL",
                  "description": "Instala o servidor PostgreSQL.",
                  "command": [
                    "sudo",
                    "apt",
                    "install",
                    "-y",
                    "postgresql"
                  ]
                }
              ]
            }
            """
        )


def test_create_docker_plan() -> None:
    planner = Planner(
        ai_planner=AIPlanner(FakeAIProvider()),
    )

    plan = planner.create_plan("Instale Docker")

    assert plan.goal == "Instalar e configurar o Docker"
    assert plan.risk == RiskLevel.HIGH
    assert plan.estimated_seconds == 240
    assert len(plan.steps) == 4

    assert plan.steps[0].command == ["sudo", "apt", "update"]
    assert plan.steps[-1].command == ["docker", "--version"]


def test_uses_ai_planner_for_unknown_request() -> None:
    planner = Planner(
        ai_planner=AIPlanner(FakeAIProvider()),
    )

    plan = planner.create_plan("Instale PostgreSQL")

    assert plan.goal == "Instalar PostgreSQL"
    assert plan.risk == RiskLevel.HIGH
    assert plan.steps[0].command == [
        "sudo",
        "apt",
        "install",
        "-y",
        "postgresql",
    ]


def test_reject_empty_request() -> None:
    planner = Planner(
        ai_planner=AIPlanner(FakeAIProvider()),
    )

    with pytest.raises(
        ValueError,
        match="A solicitação não pode estar vazia",
    ):
        planner.create_plan("   ")


def test_reject_unsupported_request_without_ai_planner() -> None:
    planner = Planner()

    with pytest.raises(
        ValueError,
        match="Ainda não sei criar um plano",
    ):
        planner.create_plan("Configure o servidor de e-mail")