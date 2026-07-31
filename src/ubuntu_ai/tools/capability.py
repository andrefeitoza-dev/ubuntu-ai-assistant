from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ubuntu_ai.domain.risk import RiskLevel


class CapabilityCategory(StrEnum):
    PACKAGE = "package"
    SERVICE = "service"
    CONTAINER = "container"
    VERSION_CONTROL = "version_control"
    PROGRAMMING = "programming"
    REMOTE = "remote"
    GENERAL = "general"


@dataclass(slots=True, frozen=True)
class ToolCapability:
    """Metadados usados para selecionar uma ferramenta de forma determinística."""

    name: str
    description: str
    category: CapabilityCategory
    executables: tuple[str, ...]
    intents: tuple[str, ...] = ()
    operating_systems: tuple[str, ...] = ("linux",)
    requires_elevation: bool = False
    risk: RiskLevel = RiskLevel.LOW
    priority: int = 50

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("O nome da capacidade não pode estar vazio.")
        if not self.executables:
            raise ValueError("A capacidade deve declarar ao menos um executável.")
        if not 0 <= self.priority <= 100:
            raise ValueError("A prioridade deve estar entre 0 e 100.")

    def supports_executable(self, executable: str) -> bool:
        return executable.lower() in {item.lower() for item in self.executables}
