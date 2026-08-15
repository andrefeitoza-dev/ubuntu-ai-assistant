from __future__ import annotations

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.skills.base import SkillContext
from ubuntu_ai.skills.registry import SkillRegistry


class SkillManager:
    """Resolve e aplica skills às etapas selecionadas pelo Planner."""

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def prepare_step(
        self,
        step: PlanStep,
        *,
        context: SkillContext | None = None,
    ) -> PlanStep:
        tool_name = step.tool_name or "shell"
        skill = self._registry.for_capability(tool_name)
        prepared = skill.prepare(step, context)
        if prepared.tool_name is None:
            prepared.tool_name = tool_name
        return prepared

    def prepare_plan(
        self,
        plan: Plan,
        *,
        context: SkillContext | None = None,
    ) -> Plan:
        plan.steps = [self.prepare_step(step, context=context) for step in plan.steps]
        return plan
