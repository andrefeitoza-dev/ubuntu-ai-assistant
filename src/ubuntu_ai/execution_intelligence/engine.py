from __future__ import annotations

from ubuntu_ai.domain.plan import PlanStep
from ubuntu_ai.execution_intelligence.models import PreflightReport
from ubuntu_ai.execution_intelligence.preflight import PreflightEngine
from ubuntu_ai.skills.manager import SkillManager
from ubuntu_ai.tools.capability_registry import CapabilityRegistry


class ExecutionIntelligence:
    """Fachada de diagnóstico anterior à execução."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        preflight: PreflightEngine | None = None,
        skill_manager: SkillManager | None = None,
    ) -> None:
        self._registry = registry
        self._preflight = preflight or PreflightEngine()
        self._skill_manager = skill_manager

    def inspect_step(self, step: PlanStep) -> PreflightReport:
        if self._skill_manager is not None:
            step = self._skill_manager.prepare_step(step)
        tool_name = step.tool_name or "shell"
        capability = self._registry.get(tool_name)
        return self._preflight.check(capability)
