from pathlib import Path

from ubuntu_ai.knowledge.models import KnowledgeSource
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository
from ubuntu_ai.semantic import (
    RAGContextBuilder,
    SemanticKnowledgeService,
    SQLiteSemanticRepository,
)


def test_rag_context_contains_source_and_relevance(tmp_path: Path) -> None:
    path = tmp_path / "knowledge.db"
    knowledge = KnowledgeService(SQLiteKnowledgeRepository(path))
    knowledge.add_document(
        title="UFW",
        content="sudo ufw enable ativa o firewall do Ubuntu.",
        source=KnowledgeSource.FILE,
        source_reference="docs/security.md",
    )
    builder = RAGContextBuilder(
        SemanticKnowledgeService(
            knowledge_service=knowledge,
            repository=SQLiteSemanticRepository(path),
        )
    )

    prompt = builder.build("ativar firewall")

    assert prompt is not None
    assert "docs/security.md" in prompt
    assert "relevância=" in prompt
    assert "ufw enable" in prompt
