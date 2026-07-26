from pathlib import Path

from ubuntu_ai.ai import AIProvider, AIRequest, AIResponse
from ubuntu_ai.knowledge.models import KnowledgeSource
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository
from ubuntu_ai.planner.ai_planner import AIPlanner


class FakeAIProvider(AIProvider):
    def __init__(self, content: str) -> None:
        self.content = content
        self.last_request: AIRequest | None = None

    def generate(self, request: AIRequest) -> AIResponse:
        self.last_request = request
        return AIResponse(content=self.content)


def test_ai_planner_includes_relevant_knowledge_in_prompt(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    service = KnowledgeService(repository)
    service.add_document(
        title="Docker policy",
        content="Na empresa, instale Docker usando o pacote docker.io.",
        source=KnowledgeSource.MANUAL,
    )
    provider = FakeAIProvider(
        '{"goal":"Instalar Docker","estimated_seconds":60,'
        '"risk":"medium","steps":[{"title":"Instalar",'
        '"description":"Instala Docker","command":["echo","ok"]}]}'
    )

    AIPlanner(provider, knowledge_service=service).create_plan("instalar docker")

    assert provider.last_request is not None
    assert "Conhecimento local relevante" in provider.last_request.prompt
    assert "docker.io" in provider.last_request.prompt
