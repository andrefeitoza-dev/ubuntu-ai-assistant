from ubuntu_ai.ai import AIProvider, AIRequest, AIResponse
from ubuntu_ai.intent import (
    Intent,
    IntentCategory,
    IntentEntity,
    IntentGoal,
)
from ubuntu_ai.planner.ai_planner import AIPlanner


class FakeProvider(AIProvider):
    def __init__(self) -> None:
        self.request: AIRequest | None = None

    def generate(self, request: AIRequest) -> AIResponse:
        self.request = request
        return AIResponse(
            content=(
                '{"goal":"Instalar Docker","estimated_seconds":60,'
                '"risk":"medium","steps":[{"title":"Instalar",'
                '"description":"Instala Docker","command":["apt","install",'
                '"docker.io"]}]}'
            )
        )


def test_ai_planner_includes_intent_in_prompt() -> None:
    provider = FakeProvider()
    planner = AIPlanner(provider)
    intent = Intent(
        request="Instale Docker",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.98,
        entities=(IntentEntity("docker"),),
        requires_confirmation=True,
    )

    planner.create_plan(intent)

    assert provider.request is not None
    assert "Intenção estruturada" in provider.request.prompt
    assert "Categoria: installation" in provider.request.prompt
