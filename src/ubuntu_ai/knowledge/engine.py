from __future__ import annotations

from pathlib import Path

from ubuntu_ai.knowledge.extractor import DocumentExtractor
from ubuntu_ai.knowledge.models import KnowledgeDocument, KnowledgeResult, KnowledgeSource
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository


class KnowledgeEngine:
    """Orquestra ingestão, consulta e manutenção da base de conhecimento."""

    def __init__(
        self,
        service: KnowledgeService,
        *,
        extractor: DocumentExtractor | None = None,
    ) -> None:
        self._service = service
        self._extractor = extractor or DocumentExtractor()

    def import_file(
        self,
        path: Path,
        *,
        title: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> KnowledgeDocument:
        extracted = self._extractor.extract(path)
        return self._service.add_document(
            title=title or extracted.title,
            content=extracted.content,
            source=KnowledgeSource.FILE,
            source_reference=extracted.source_reference,
            tags=tags,
            metadata=extracted.metadata,
        )

    def add_text(
        self,
        *,
        title: str,
        content: str,
        tags: tuple[str, ...] = (),
    ) -> KnowledgeDocument:
        return self._service.add_document(
            title=title,
            content=content,
            source=KnowledgeSource.MANUAL,
            tags=tags,
        )

    def search(self, query: str, *, limit: int = 10) -> tuple[KnowledgeResult, ...]:
        return tuple(self._service.search(query, limit=limit))

    def reindex(self, document_id: str | None = None) -> int:
        repository = self._service.repository
        if not isinstance(repository, SQLiteKnowledgeRepository):
            raise RuntimeError("O reindexamento requer SQLiteKnowledgeRepository.")
        if document_id is None:
            return repository.reindex_all()
        return repository.reindex_document(document_id)
