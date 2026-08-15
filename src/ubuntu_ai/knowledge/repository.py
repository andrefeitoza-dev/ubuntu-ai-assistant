from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ubuntu_ai.knowledge.models import KnowledgeDocument, KnowledgeResult


class KnowledgeRepository(ABC):
    """Contrato de persistência e busca do Knowledge Engine."""

    @abstractmethod
    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Persiste e retorna um novo documento."""

    @abstractmethod
    def update_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """Atualiza e retorna um documento existente."""

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """Remove um documento e informa se ele existia."""

    @abstractmethod
    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        """Obtém um documento pelo identificador."""

    @abstractmethod
    def list_documents(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[KnowledgeDocument]:
        """Lista documentos em ordem definida pelo backend."""

    @abstractmethod
    def search(self, query: str, *, limit: int = 10) -> Sequence[KnowledgeResult]:
        """Pesquisa documentos e retorna resultados ranqueados."""

    @abstractmethod
    def find_related(
        self,
        document_id: str,
        *,
        limit: int = 5,
    ) -> Sequence[KnowledgeResult]:
        """Encontra documentos relacionados a outro documento."""

    @abstractmethod
    def document_exists(self, document_id: str) -> bool:
        """Informa se um documento existe."""
