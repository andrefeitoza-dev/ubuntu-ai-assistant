from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanningProfile:
    """Representa recomendações estruturadas para o planejamento."""

    profiles: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    risk_hints: tuple[str, ...] = ()
    preferred_tools: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        return not (
            self.profiles or self.recommendations or self.risk_hints or self.preferred_tools
        )

    def to_prompt(self) -> str:
        sections: list[str] = []

        if self.profiles:
            sections.append("Perfis detectados:")
            sections.extend(f"- {item}" for item in self.profiles)

        if self.recommendations:
            if sections:
                sections.append("")
            sections.append("Recomendações:")
            sections.extend(f"- {item}" for item in self.recommendations)

        if self.risk_hints:
            if sections:
                sections.append("")
            sections.append("Riscos observados:")
            sections.extend(f"- {item}" for item in self.risk_hints)

        if self.preferred_tools:
            if sections:
                sections.append("")
            sections.append("Ferramentas preferenciais:")
            sections.extend(f"- {item}" for item in self.preferred_tools)

        return "\n".join(sections)
