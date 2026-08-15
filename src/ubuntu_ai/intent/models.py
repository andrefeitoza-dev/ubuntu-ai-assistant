from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class IntentCategory(StrEnum):
    """Categorias funcionais reconhecidas pelo motor de intenção."""

    DIAGNOSIS = "diagnosis"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    QUERY = "query"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"
    UNKNOWN = "unknown"


class IntentGoal(StrEnum):
    """Objetivos operacionais de alto nível."""

    INSPECT = "inspect"
    PROVISION = "provision"
    CONFIGURE = "configure"
    REPAIR = "repair"
    REMOVE = "remove"
    UPDATE = "update"
    EXECUTE = "execute"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class IntentEntity:
    """Entidade identificada na solicitação do usuário."""

    name: str
    kind: str = "technology"

    def __post_init__(self) -> None:
        normalized_name = self.name.strip().lower()
        normalized_kind = self.kind.strip().lower()
        if not normalized_name:
            raise ValueError("O nome da entidade não pode estar vazio.")
        if not normalized_kind:
            raise ValueError("O tipo da entidade não pode estar vazio.")
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "kind", normalized_kind)


@dataclass(frozen=True, slots=True)
class Intent:
    """Representa a interpretação estruturada de uma solicitação."""

    request: str
    category: IntentCategory
    goal: IntentGoal
    confidence: float
    entities: tuple[IntentEntity, ...] = field(default_factory=tuple)
    requires_confirmation: bool = False
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_request = self.request.strip()
        if not normalized_request:
            raise ValueError("A solicitação da intenção não pode estar vazia.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("A confiança deve estar entre 0.0 e 1.0.")
        object.__setattr__(self, "request", normalized_request)

    @property
    def entity_names(self) -> tuple[str, ...]:
        return tuple(entity.name for entity in self.entities)
