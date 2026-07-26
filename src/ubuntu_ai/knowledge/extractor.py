from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ubuntu_ai.knowledge.exceptions import KnowledgeValidationError


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    title: str
    content: str
    source_reference: str
    metadata: dict[str, str]


class DocumentExtractor:
    """Extrai texto de formatos locais seguros suportados pelo Knowledge Engine."""

    SUPPORTED_SUFFIXES = frozenset({".txt", ".md", ".rst", ".log", ".json", ".yaml", ".yml"})

    def extract(self, path: Path) -> ExtractedDocument:
        resolved = path.expanduser().resolve()
        if not resolved.is_file():
            raise KnowledgeValidationError(f"Arquivo não encontrado: {resolved}")
        if resolved.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            supported = ", ".join(sorted(self.SUPPORTED_SUFFIXES))
            raise KnowledgeValidationError(
                f"Formato não suportado: {resolved.suffix or 'sem extensão'}. "
                f"Formatos: {supported}."
            )

        try:
            raw = resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise KnowledgeValidationError(
                f"O arquivo não está codificado em UTF-8: {resolved}"
            ) from error
        except OSError as error:
            raise KnowledgeValidationError(f"Não foi possível ler: {resolved}") from error

        content = self._normalize_content(raw, resolved.suffix.lower())
        if not content.strip():
            raise KnowledgeValidationError(f"O arquivo está vazio: {resolved}")

        return ExtractedDocument(
            title=resolved.stem.replace("_", " ").replace("-", " ").strip() or resolved.name,
            content=content.strip(),
            source_reference=str(resolved),
            metadata={
                "filename": resolved.name,
                "suffix": resolved.suffix.lower(),
                "size_bytes": str(resolved.stat().st_size),
            },
        )

    @staticmethod
    def _normalize_content(raw: str, suffix: str) -> str:
        if suffix != ".json":
            return raw
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as error:
            raise KnowledgeValidationError("O arquivo JSON é inválido.") from error
        return json.dumps(parsed, ensure_ascii=False, indent=2)
