from __future__ import annotations

import re

from ubuntu_ai.knowledge.exceptions import KnowledgeValidationError
from ubuntu_ai.knowledge.models import KnowledgeChunk


class DocumentChunker:
    """Divide documentos em trechos indexáveis com sobreposição controlada."""

    def __init__(self, *, chunk_size: int = 1000, overlap: int = 150) -> None:
        if chunk_size < 100:
            raise KnowledgeValidationError("O tamanho do trecho deve ser pelo menos 100.")
        if overlap < 0 or overlap >= chunk_size:
            raise KnowledgeValidationError(
                "A sobreposição deve ser não negativa e menor que o trecho."
            )
        self._chunk_size = chunk_size
        self._overlap = overlap

    def split(self, *, document_id: str, content: str) -> tuple[KnowledgeChunk, ...]:
        normalized = re.sub(r"\r\n?", "\n", content).strip()
        if not normalized:
            raise KnowledgeValidationError("O conteúdo para divisão não pode estar vazio.")

        parts: list[str] = []
        start = 0
        while start < len(normalized):
            target_end = min(start + self._chunk_size, len(normalized))
            end = self._natural_boundary(normalized, start, target_end)
            piece = normalized[start:end].strip()
            if piece:
                parts.append(piece)
            if end >= len(normalized):
                break
            start = max(end - self._overlap, start + 1)

        return tuple(
            KnowledgeChunk.create(
                document_id=document_id,
                position=position,
                content=piece,
            )
            for position, piece in enumerate(parts)
        )

    @staticmethod
    def _natural_boundary(content: str, start: int, target_end: int) -> int:
        if target_end >= len(content):
            return len(content)
        minimum = start + ((target_end - start) // 2)
        candidates = [
            content.rfind("\n\n", minimum, target_end),
            content.rfind("\n", minimum, target_end),
            content.rfind(". ", minimum, target_end),
            content.rfind(" ", minimum, target_end),
        ]
        boundary = max(candidates)
        return target_end if boundary < minimum else boundary + 1
