from __future__ import annotations

import re
from collections.abc import Iterable

from ubuntu_ai.intent.models import IntentEntity


class EntityExtractor:
    """Extrai tecnologias conhecidas de uma solicitação textual."""

    DEFAULT_ENTITIES: tuple[str, ...] = (
        "apt",
        "docker",
        "git",
        "github",
        "java",
        "kubernetes",
        "linux",
        "mysql",
        "nginx",
        "node",
        "npm",
        "ollama",
        "postgresql",
        "python",
        "redis",
        "snap",
        "systemd",
        "ubuntu",
        "uv",
    )

    def __init__(self, entities: Iterable[str] | None = None) -> None:
        source = entities or self.DEFAULT_ENTITIES
        self._entities = tuple(
            sorted({entity.strip().lower() for entity in source if entity.strip()})
        )

    def extract(self, request: str) -> tuple[IntentEntity, ...]:
        normalized = request.lower()
        matches = [
            IntentEntity(name=entity)
            for entity in self._entities
            if re.search(rf"(?<![\w-]){re.escape(entity)}(?![\w-])", normalized)
        ]
        return tuple(matches)
