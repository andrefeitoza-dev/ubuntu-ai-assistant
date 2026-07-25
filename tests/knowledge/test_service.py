import pytest

from tests.knowledge.fakes import FakeKnowledgeRepository
from ubuntu_ai.knowledge.exceptions import (
    KnowledgeNotFoundError,
    KnowledgeValidationError,
)
from ubuntu_ai.knowledge.models import KnowledgeResult, KnowledgeSource
from ubuntu_ai.knowledge.service import KnowledgeService


def test_service_adds_document_through_repository() -> None:
    repository = FakeKnowledgeRepository()
    service = KnowledgeService(repository)

    document = service.add_document(
        title="Planner",
        content="O planner cria planos de execução.",
        source=KnowledgeSource.FILE,
        tags=("Python", "python"),
    )

    assert repository.get_document(document.id) == document
    assert tuple(tag.name for tag in document.tags) == ("python",)


def test_service_updates_existing_document() -> None:
    repository = FakeKnowledgeRepository()
    service = KnowledgeService(repository)
    document = service.add_document(
        title="Planner",
        content="Versão inicial",
        source=KnowledgeSource.MANUAL,
    )

    updated = service.update_document(document.id, content="Versão final")

    assert updated.content == "Versão final"
    assert repository.get_document(document.id) == updated


def test_service_requires_existing_document_for_update() -> None:
    service = KnowledgeService(FakeKnowledgeRepository())

    with pytest.raises(KnowledgeNotFoundError):
        service.update_document("missing", title="Novo")


def test_service_rejects_empty_search() -> None:
    service = KnowledgeService(FakeKnowledgeRepository())

    with pytest.raises(KnowledgeValidationError):
        service.search("  ")


def test_service_delegates_search_results() -> None:
    repository = FakeKnowledgeRepository()
    service = KnowledgeService(repository)
    document = service.add_document(
        title="Docker",
        content="Instalação do Docker",
        source=KnowledgeSource.FILE,
    )
    result = KnowledgeResult(document=document, score=0.9, excerpt="Instalação do Docker")
    repository.search_results.append(result)

    assert service.search("docker") == [result]


def test_find_related_requires_existing_document() -> None:
    service = KnowledgeService(FakeKnowledgeRepository())

    with pytest.raises(KnowledgeNotFoundError):
        service.find_related("missing")


def test_list_documents_validates_pagination() -> None:
    service = KnowledgeService(FakeKnowledgeRepository())

    with pytest.raises(KnowledgeValidationError):
        service.list_documents(offset=-1)
