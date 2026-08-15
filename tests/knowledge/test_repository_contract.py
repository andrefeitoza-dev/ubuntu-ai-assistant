from tests.knowledge.fakes import FakeKnowledgeRepository
from ubuntu_ai.knowledge.models import KnowledgeDocument, KnowledgeSource


def test_repository_contract_supports_document_lifecycle() -> None:
    repository = FakeKnowledgeRepository()
    document = KnowledgeDocument.create(
        title="README",
        content="Documentação do projeto",
        source=KnowledgeSource.FILE,
    )

    repository.add_document(document)
    assert repository.document_exists(document.id)
    assert repository.get_document(document.id) == document

    updated = document.with_updates(content="Documentação atualizada")
    repository.update_document(updated)
    assert repository.get_document(document.id) == updated

    assert repository.delete_document(document.id) is True
    assert repository.delete_document(document.id) is False
