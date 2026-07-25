from collections.abc import Sequence

from ubuntu_ai.knowledge.models import KnowledgeDocument, KnowledgeResult
from ubuntu_ai.knowledge.repository import KnowledgeRepository


class FakeKnowledgeRepository(KnowledgeRepository):
    def __init__(self) -> None:
        self.documents: dict[str, KnowledgeDocument] = {}
        self.search_results: list[KnowledgeResult] = []
        self.related_results: list[KnowledgeResult] = []

    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.documents[document.id] = document
        return document

    def update_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.documents[document.id] = document
        return document

    def delete_document(self, document_id: str) -> bool:
        return self.documents.pop(document_id, None) is not None

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        return self.documents.get(document_id)

    def list_documents(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[KnowledgeDocument]:
        values = list(self.documents.values())
        return values[offset : offset + limit]

    def search(self, query: str, *, limit: int = 10) -> Sequence[KnowledgeResult]:
        return self.search_results[:limit]

    def find_related(
        self,
        document_id: str,
        *,
        limit: int = 5,
    ) -> Sequence[KnowledgeResult]:
        return self.related_results[:limit]

    def document_exists(self, document_id: str) -> bool:
        return document_id in self.documents
