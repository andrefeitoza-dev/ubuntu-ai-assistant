from ubuntu_ai.ai.models import AIResponse
from ubuntu_ai.planner.ai_planner import AIPlanner


class FakeProvider:
    def __init__(self) -> None:
        self.prompt = ""

    def generate(self, request: object) -> AIResponse:
        self.prompt = getattr(request, "prompt")
        return AIResponse(
            content='{"goal":"g","estimated_seconds":1,"risk":"low",'
            '"steps":[{"title":"t","description":"d","command":["ls"]}]}'
        )


class FakeLearningService:
    def context_for_prompt(self, request: str, **kwargs: object) -> str:
        return "- ls funcionou anteriormente"


def test_ai_planner_injects_learning_context() -> None:
    provider = FakeProvider()
    planner = AIPlanner(
        provider=provider,  # type: ignore[arg-type]
        learning_service=FakeLearningService(),  # type: ignore[arg-type]
    )

    planner.create_plan("listar arquivos")

    assert "Aprendizado de execuções anteriores" in provider.prompt
    assert "ls funcionou anteriormente" in provider.prompt
