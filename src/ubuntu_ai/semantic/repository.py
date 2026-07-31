from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ubuntu_ai.knowledge.models import KnowledgeChunk


class SemanticRepository(ABC):
    """Contrato de persistência dos vetores de conhecimento."""

    @abstractmethod
    def upsert(self, chunk: KnowledgeChunk, vector: Sequence[float]) -> None:
        """Insere ou substitui o vetor de um trecho."""

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Remove todos os vetores associados a um documento."""

    @abstractmethod
    def list_vectors(self) -> Sequence[tuple[str, tuple[float, ...]]]:
        """Lista identificadores de trecho e vetores persistidos."""
