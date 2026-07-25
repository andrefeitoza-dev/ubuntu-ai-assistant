import pytest

from ubuntu_ai.knowledge.exceptions import KnowledgeValidationError
from ubuntu_ai.knowledge.models import (
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeResult,
    KnowledgeSource,
    KnowledgeTag,
)


def test_tag_is_normalized() -> None:
    assert KnowledgeTag("  Python  ").name == "python"


def test_document_create_normalizes_and_deduplicates_tags() -> None:
    document = KnowledgeDocument.create(
        title="  ADR principal ",
        content="  Conteúdo da arquitetura. ",
        source=KnowledgeSource.FILE,
        tags=(KnowledgeTag("architecture"), KnowledgeTag("Architecture")),
    )

    assert document.title == "ADR principal"
    assert document.content == "Conteúdo da arquitetura."
    assert document.tags == (KnowledgeTag("architecture"),)


def test_document_rejects_empty_content() -> None:
    with pytest.raises(KnowledgeValidationError):
        KnowledgeDocument.create(
            title="Documento",
            content=" ",
            source=KnowledgeSource.MANUAL,
        )


def test_document_update_preserves_identity() -> None:
    document = KnowledgeDocument.create(
        title="Original",
        content="Conteúdo",
        source=KnowledgeSource.MANUAL,
    )

    updated = document.with_updates(title="Atualizado")

    assert updated.id == document.id
    assert updated.created_at == document.created_at
    assert updated.title == "Atualizado"
    assert updated.updated_at >= document.updated_at


def test_chunk_rejects_negative_position() -> None:
    with pytest.raises(KnowledgeValidationError):
        KnowledgeChunk.create(document_id="doc", position=-1, content="trecho")


def test_result_rejects_negative_score() -> None:
    document = KnowledgeDocument.create(
        title="Documento",
        content="Conteúdo",
        source=KnowledgeSource.MANUAL,
    )

    with pytest.raises(KnowledgeValidationError):
        KnowledgeResult(document=document, score=-0.1, excerpt="resultado")
