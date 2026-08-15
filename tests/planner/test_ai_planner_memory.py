from ubuntu_ai.ai import AIResponse
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemorySelection,
    RankedMemory,
)
from ubuntu_ai.planner.ai_planner import AIPlanner


class FakeProvider:
    def __init__(self) -> None:
        self.last_request = None

    def generate(self, request):
        self.last_request = request
        return AIResponse(
            content=(
                '{"goal":"teste","estimated_seconds":1,'
                '"risk":"low","steps":['
                '{"title":"teste","description":"teste",'
                '"command":["echo","ok"]}]}'
            )
        )


def test_ai_planner_includes_selected_memory_in_prompt() -> None:
    provider = FakeProvider()

    memory = MemorySelection(
        items=(
            RankedMemory(
                candidate=MemoryCandidate(
                    kind=MemoryKind.PROJECT,
                    content="python_environment=.venv",
                    project_name="ubuntu-ai-assistant",
                    importance=1.0,
                    source="project_fact",
                ),
                score=1.0,
            ),
        )
    )

    planner = AIPlanner(provider=provider)

    planner.create_plan(
        "verifique o ambiente python",
        memory=memory,
    )

    assert provider.last_request is not None
    assert "Memórias relevantes:" in provider.last_request.prompt
    assert "python_environment=.venv" in provider.last_request.prompt
