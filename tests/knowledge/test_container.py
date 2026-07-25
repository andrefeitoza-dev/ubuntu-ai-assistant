import pytest

from tests.knowledge.fakes import FakeKnowledgeRepository
from ubuntu_ai.container.container import Container
from ubuntu_ai.knowledge.exceptions import KnowledgeRepositoryNotConfiguredError


def test_container_requires_explicit_knowledge_backend() -> None:
    container = Container()

    with pytest.raises(KnowledgeRepositoryNotConfiguredError):
        container.knowledge_repository()


def test_container_builds_service_from_registered_repository() -> None:
    container = Container()
    repository = FakeKnowledgeRepository()

    container.register_knowledge_repository(repository)

    assert container.knowledge_repository() is repository
    assert container.knowledge_service() is container.knowledge_service()
