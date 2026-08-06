from __future__ import annotations

from collections.abc import Sequence

from ubuntu_ai.knowledge.exceptions import (
    KnowledgeNotFoundError,
    KnowledgeValidationError,
)
from ubuntu_ai.knowledge.models import (
    KnowledgeDocument,
    KnowledgeResult,
    KnowledgeSource,
    KnowledgeTag,
)
from ubuntu_ai.knowledge.repository import KnowledgeRepository


class KnowledgeService:
    """Fachada de regras de negócio independente do backend."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self._repository = repository

    @property
    def repository(self) -> KnowledgeRepository:
        """Expõe o repositório para operações administrativas controladas."""

        return self._repository

    def add_document(
        self,
        *,
        title: str,
        content: str,
        source: KnowledgeSource,
        source_reference: str | None = None,
        tags: Sequence[str] = (),
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeDocument:
        document = KnowledgeDocument.create(
            title=title,
            content=content,
            source=source,
            source_reference=source_reference,
            tags=self._normalize_tags(tags),
            metadata=metadata,
        )
        return self._repository.add_document(document)

    def update_document(
        self,
        document_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
        source_reference: str | None = None,
        tags: Sequence[str] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeDocument:
        current = self.require_document(document_id)
        updated = current.with_updates(
            title=title,
            content=content,
            source_reference=source_reference,
            tags=None if tags is None else self._normalize_tags(tags),
            metadata=metadata,
        )
        return self._repository.update_document(updated)

    def delete_document(self, document_id: str) -> None:
        normalized_id = self._validate_identifier(document_id)
        if not self._repository.delete_document(normalized_id):
            raise KnowledgeNotFoundError(
                f"Documento de conhecimento não encontrado: {normalized_id}"
            )

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        return self._repository.get_document(self._validate_identifier(document_id))

    def require_document(self, document_id: str) -> KnowledgeDocument:
        normalized_id = self._validate_identifier(document_id)
        document = self._repository.get_document(normalized_id)
        if document is None:
            raise KnowledgeNotFoundError(
                f"Documento de conhecimento não encontrado: {normalized_id}"
            )
        return document

    def list_documents(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[KnowledgeDocument]:
        self._validate_pagination(limit=limit, offset=offset)
        return self._repository.list_documents(limit=limit, offset=offset)

    def search(self, query: str, *, limit: int = 10) -> Sequence[KnowledgeResult]:
        normalized_query = query.strip()
        if not normalized_query:
            raise KnowledgeValidationError("A consulta de busca não pode estar vazia.")
        self._validate_limit(limit)
        return self._repository.search(normalized_query, limit=limit)

    def find_related(
        self,
        document_id: str,
        *,
        limit: int = 5,
    ) -> Sequence[KnowledgeResult]:
        normalized_id = self._validate_identifier(document_id)
        self._validate_limit(limit)
        if not self._repository.document_exists(normalized_id):
            raise KnowledgeNotFoundError(
                f"Documento de conhecimento não encontrado: {normalized_id}"
            )
        return self._repository.find_related(normalized_id, limit=limit)

    @staticmethod
    def _normalize_tags(tags: Sequence[str]) -> tuple[KnowledgeTag, ...]:
        return tuple(dict.fromkeys(KnowledgeTag(tag) for tag in tags))

    @staticmethod
    def _validate_identifier(document_id: str) -> str:
        normalized_id = document_id.strip()
        if not normalized_id:
            raise KnowledgeValidationError("O identificador do documento não pode estar vazio.")
        return normalized_id

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if limit < 1:
            raise KnowledgeValidationError("O limite deve ser maior que zero.")

    @classmethod
    def _validate_pagination(cls, *, limit: int, offset: int) -> None:
        cls._validate_limit(limit)
        if offset < 0:
            raise KnowledgeValidationError("O deslocamento não pode ser negativo.")
