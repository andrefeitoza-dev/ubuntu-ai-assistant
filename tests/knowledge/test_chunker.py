import pytest

from ubuntu_ai.knowledge.chunker import DocumentChunker
from ubuntu_ai.knowledge.exceptions import KnowledgeValidationError


def test_chunker_splits_long_content_with_positions() -> None:
    chunker = DocumentChunker(chunk_size=100, overlap=10)
    chunks = chunker.split(document_id="doc-1", content="palavra " * 40)

    assert len(chunks) > 1
    assert [chunk.position for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.document_id == "doc-1" for chunk in chunks)


def test_chunker_rejects_invalid_overlap() -> None:
    with pytest.raises(KnowledgeValidationError):
        DocumentChunker(chunk_size=100, overlap=100)
