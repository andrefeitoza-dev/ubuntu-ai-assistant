from __future__ import annotations

from ubuntu_ai.decision.models import Decision
from ubuntu_ai.decision.rules import choose_execution_mode, choose_strategy, preferred_skills
from ubuntu_ai.planner.models import PlanningProfile


class DecisionEngine:
    """Transforma um PlanningProfile em uma decisão operacional."""

    def decide(self, profile: PlanningProfile) -> Decision:
        reasons: list[str] = []
        if profile.profiles:
            reasons.append("O ambiente possui perfis detectados relevantes ao planejamento.")
        if profile.risk_hints:
            reasons.append("Há sinais de risco no contexto; revisão adicional é recomendada.")
        if "docker" in profile.preferred_tools:
            reasons.append("Docker está disponível e pode isolar alterações do host.")
        return Decision(
            strategy=choose_strategy(profile),
            execution_mode=choose_execution_mode(profile),
            preferred_tools=profile.preferred_tools,
            preferred_skills=preferred_skills(profile),
            risk_hints=profile.risk_hints,
            reasons=tuple(reasons),
        )
