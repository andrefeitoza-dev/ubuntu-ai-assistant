from pathlib import Path

import pytest

from ubuntu_ai.knowledge.exceptions import KnowledgeValidationError
from ubuntu_ai.knowledge.extractor import DocumentExtractor


def test_extractor_reads_markdown(tmp_path: Path) -> None:
    path = tmp_path / "project-context.md"
    path.write_text("# UbuntuAI\n\nContexto do projeto.", encoding="utf-8")

    extracted = DocumentExtractor().extract(path)

    assert extracted.title == "project context"
    assert "UbuntuAI" in extracted.content
    assert extracted.metadata["suffix"] == ".md"


def test_extractor_formats_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"model":"qwen"}', encoding="utf-8")

    extracted = DocumentExtractor().extract(path)

    assert '  "model": "qwen"' in extracted.content


def test_extractor_rejects_unsupported_format(tmp_path: Path) -> None:
    path = tmp_path / "manual.pdf"
    path.write_bytes(b"pdf")

    with pytest.raises(KnowledgeValidationError):
        DocumentExtractor().extract(path)
