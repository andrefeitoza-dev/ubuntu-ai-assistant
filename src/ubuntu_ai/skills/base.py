from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field

from ubuntu_ai.domain.plan import PlanStep
from ubuntu_ai.tools.capability import ToolCapability


@dataclass(slots=True, frozen=True)
class SkillContext:
    """Dados opcionais usados por uma skill ao preparar uma etapa."""

    request: str = ""
    project_name: str | None = None
    variables: Mapping[str, str] = field(default_factory=dict)


class Skill(ABC):
    """Contrato de uma extensão executável do Ubuntu AI."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador estável da skill."""

    @property
    @abstractmethod
    def capabilities(self) -> tuple[ToolCapability, ...]:
        """Capacidades disponibilizadas pela skill."""

    def supports(self, step: PlanStep) -> bool:
        """Indica se a skill reconhece a ferramenta escolhida para a etapa."""

        if step.tool_name is None:
            return False
        names = {capability.name.lower() for capability in self.capabilities}
        return step.tool_name.lower() in names

    def prepare(self, step: PlanStep, context: SkillContext | None = None) -> PlanStep:
        """Valida ou transforma uma etapa antes do preflight."""

        del context
        if not step.command:
            raise ValueError("A etapa da skill precisa conter um comando.")
        return step

    def help(self) -> str:
        """Retorna uma descrição curta para descoberta e interfaces."""

        return f"Skill {self.name}: {len(self.capabilities)} capacidade(s)."
