import pytest

from ubuntu_ai.ai import AIProvider, AIRequest, AIResponse
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.ai_planner import AIPlanner


class FakeAIProvider(AIProvider):
    def __init__(self, content: str) -> None:
        self.content = content
        self.last_request: AIRequest | None = None

    def generate(self, request: AIRequest) -> AIResponse:
        self.last_request = request
        return AIResponse(content=self.content)


def test_ai_planner_creates_structured_plan() -> None:
    provider = FakeAIProvider(
        """
        {
          "goal": "Instalar PostgreSQL",
          "estimated_seconds": 180,
          "risk": "high",
          "steps": [
            {
              "title": "Atualizar repositórios",
              "description": "Atualiza os índices de pacotes.",
              "command": ["sudo", "apt", "update"]
            },
            {
              "title": "Instalar PostgreSQL",
              "description": "Instala o servidor PostgreSQL.",
              "command": ["sudo", "apt", "install", "-y", "postgresql"]
            }
          ]
        }
        """
    )
    planner = AIPlanner(provider)

    plan = planner.create_plan("Instale PostgreSQL")

    assert plan.goal == "Instalar PostgreSQL"
    assert plan.estimated_seconds == 180
    assert plan.risk == RiskLevel.HIGH
    assert len(plan.steps) == 2
    assert plan.steps[0].command == ["sudo", "apt", "update"]


def test_ai_planner_sends_request_to_provider() -> None:
    provider = FakeAIProvider(
        """
        {
          "goal": "Verificar sistema",
          "estimated_seconds": 30,
          "risk": "low",
          "steps": [
            {
              "title": "Verificar kernel",
              "description": "Exibe a versão do kernel.",
              "command": ["uname", "-r"]
            }
          ]
        }
        """
    )
    planner = AIPlanner(provider)

    planner.create_plan("Verifique o kernel")

    assert provider.last_request is not None
    assert "Verifique o kernel" in provider.last_request.prompt
    assert "JSON válido" in provider.last_request.prompt


def test_ai_planner_rejects_empty_request() -> None:
    planner = AIPlanner(FakeAIProvider("{}"))

    with pytest.raises(ValueError, match="solicitação não pode estar vazia"):
        planner.create_plan("   ")


def test_ai_planner_rejects_invalid_json() -> None:
    planner = AIPlanner(FakeAIProvider("resposta inválida"))

    with pytest.raises(ValueError, match="JSON inválido"):
        planner.create_plan("Instale PostgreSQL")


def test_ai_planner_rejects_invalid_command() -> None:
    provider = FakeAIProvider(
        """
        {
          "goal": "Instalar PostgreSQL",
          "estimated_seconds": 180,
          "risk": "high",
          "steps": [
            {
              "title": "Instalar",
              "description": "Instala o pacote.",
              "command": "sudo apt install postgresql"
            }
          ]
        }
        """
    )
    planner = AIPlanner(provider)

    with pytest.raises(ValueError, match="comando de etapa inválido"):
        planner.create_plan("Instale PostgreSQL")