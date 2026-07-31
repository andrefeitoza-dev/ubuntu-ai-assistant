from pathlib import Path

from ubuntu_ai.knowledge.models import KnowledgeSource
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository
from ubuntu_ai.semantic import SemanticKnowledgeService, SQLiteSemanticRepository


def build_service(path: Path) -> tuple[KnowledgeService, SemanticKnowledgeService]:
    knowledge = KnowledgeService(SQLiteKnowledgeRepository(path))
    semantic = SemanticKnowledgeService(
        knowledge_service=knowledge,
        repository=SQLiteSemanticRepository(path),
    )
    return knowledge, semantic


def test_semantic_service_indexes_and_retrieves_local_knowledge(tmp_path: Path) -> None:
    knowledge, semantic = build_service(tmp_path / "knowledge.db")
    docker = knowledge.add_document(
        title="Docker Ubuntu",
        content="Instale o mecanismo de containers com apt e habilite o serviço docker.",
        source=KnowledgeSource.MANUAL,
    )
    knowledge.add_document(
        title="Python",
        content="Crie ambientes virtuais Python usando o módulo venv.",
        source=KnowledgeSource.MANUAL,
    )

    assert semantic.index_all() == 2
    context = semantic.retrieve("instalar containers e ativar docker", limit=1)

    assert context.matches[0].document.id == docker.id
    assert context.matches[0].semantic_score > 0


def test_semantic_service_refreshes_index_when_document_changes(tmp_path: Path) -> None:
    knowledge, semantic = build_service(tmp_path / "knowledge.db")
    document = knowledge.add_document(
        title="Rede",
        content="Configuração inicial de rede.",
        source=KnowledgeSource.MANUAL,
    )
    semantic.retrieve("rede")

    knowledge.update_document(
        document.id,
        content="Use ufw para configurar firewall e regras de segurança.",
    )
    context = semantic.retrieve("firewall ufw", limit=1)

    assert context.matches[0].document.id == document.id
    assert "ufw" in context.matches[0].chunk.content
