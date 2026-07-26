from tests.knowledge.fakes import FakeKnowledgeRepository
from ubuntu_ai.container.container import Container
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository


def test_container_builds_default_sqlite_knowledge_backend() -> None:
    container = Container()

    assert isinstance(container.knowledge_repository(), SQLiteKnowledgeRepository)


def test_container_builds_service_from_registered_repository() -> None:
    container = Container()
    repository = FakeKnowledgeRepository()

    container.register_knowledge_repository(repository)

    assert container.knowledge_repository() is repository
    assert container.knowledge_service() is container.knowledge_service()
