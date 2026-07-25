from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from ubuntu_ai.knowledge.exceptions import KnowledgeValidationError


class KnowledgeSource(StrEnum):
    """Origem lógica de um documento de conhecimento."""

    FILE = "file"
    CONVERSATION = "conversation"
    EXECUTION = "execution"
    MANUAL = "manual"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class KnowledgeTag:
    """Etiqueta normalizada associada a um documento."""

    name: str

    def __post_init__(self) -> None:
        normalized = self.name.strip().lower()
        if not normalized:
            raise KnowledgeValidationError("A etiqueta não pode estar vazia.")
        object.__setattr__(self, "name", normalized)


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    """Trecho indexável pertencente a um documento."""

    id: str
    document_id: str
    position: int
    content: str

    @classmethod
    def create(
        cls,
        *,
        document_id: str,
        position: int,
        content: str,
    ) -> KnowledgeChunk:
        normalized_document_id = document_id.strip()
        normalized_content = content.strip()

        if not normalized_document_id:
            raise KnowledgeValidationError("O identificador do documento não pode estar vazio.")
        if position < 0:
            raise KnowledgeValidationError("A posição do trecho não pode ser negativa.")
        if not normalized_content:
            raise KnowledgeValidationError("O conteúdo do trecho não pode estar vazio.")

        return cls(
            id=str(uuid4()),
            document_id=normalized_document_id,
            position=position,
            content=normalized_content,
        )


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    """Documento independente da tecnologia de persistência."""

    id: str
    title: str
    content: str
    source: KnowledgeSource
    source_reference: str | None
    created_at: datetime
    updated_at: datetime
    tags: tuple[KnowledgeTag, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        content: str,
        source: KnowledgeSource,
        source_reference: str | None = None,
        tags: tuple[KnowledgeTag, ...] = (),
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeDocument:
        normalized_title = title.strip()
        normalized_content = content.strip()
        normalized_reference = source_reference.strip() if source_reference else None

        if not normalized_title:
            raise KnowledgeValidationError("O título do documento não pode estar vazio.")
        if not normalized_content:
            raise KnowledgeValidationError("O conteúdo do documento não pode estar vazio.")

        now = datetime.now(UTC)
        unique_tags = tuple(dict.fromkeys(tags))

        return cls(
            id=str(uuid4()),
            title=normalized_title,
            content=normalized_content,
            source=source,
            source_reference=normalized_reference,
            created_at=now,
            updated_at=now,
            tags=unique_tags,
            metadata=dict(metadata or {}),
        )

    def with_updates(
        self,
        *,
        title: str | None = None,
        content: str | None = None,
        source_reference: str | None = None,
        tags: tuple[KnowledgeTag, ...] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeDocument:
        """Retorna uma nova versão preservando identidade e criação."""

        normalized_title = self.title if title is None else title.strip()
        normalized_content = self.content if content is None else content.strip()

        if not normalized_title:
            raise KnowledgeValidationError("O título do documento não pode estar vazio.")
        if not normalized_content:
            raise KnowledgeValidationError("O conteúdo do documento não pode estar vazio.")

        reference = self.source_reference
        if source_reference is not None:
            reference = source_reference.strip() or None

        updated_tags = self.tags if tags is None else tuple(dict.fromkeys(tags))
        updated_metadata = self.metadata if metadata is None else dict(metadata)

        return KnowledgeDocument(
            id=self.id,
            title=normalized_title,
            content=normalized_content,
            source=self.source,
            source_reference=reference,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            tags=updated_tags,
            metadata=updated_metadata,
        )


@dataclass(frozen=True, slots=True)
class KnowledgeResult:
    """Resultado ranqueado retornado por qualquer backend de busca."""

    document: KnowledgeDocument
    score: float
    excerpt: str
    matched_chunks: tuple[KnowledgeChunk, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.score < 0:
            raise KnowledgeValidationError("A pontuação do resultado não pode ser negativa.")
        if not self.excerpt.strip():
            raise KnowledgeValidationError("O resumo do resultado não pode estar vazio.")
