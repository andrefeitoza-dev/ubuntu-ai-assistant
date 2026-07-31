from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.domain.plan import PlanStep
from ubuntu_ai.skills.base import Skill, SkillContext
from ubuntu_ai.tools.capability import ToolCapability


@dataclass(slots=True, frozen=True)
class BuiltinSkill(Skill):
    """Skill declarativa para ferramentas nativas suportadas pelo projeto."""

    skill_name: str
    provided_capabilities: tuple[ToolCapability, ...]
    description: str

    @property
    def name(self) -> str:
        return self.skill_name

    @property
    def capabilities(self) -> tuple[ToolCapability, ...]:
        return self.provided_capabilities

    def prepare(self, step: PlanStep, context: SkillContext | None = None) -> PlanStep:
        del context
        Skill.prepare(self, step)
        capability = next(
            item for item in self.capabilities if item.name == (step.tool_name or "shell")
        )
        executable = step.command[0].lower()
        wrappers = {"sudo", "env", "command", "nohup"}
        index = 0
        while executable in wrappers and index < len(step.command) - 1:
            index += 1
            executable = step.command[index].lower()
        if not capability.supports_executable(executable):
            raise ValueError(
                f"A skill {self.name} não aceita o executável {executable} "
                f"para a capacidade {capability.name}."
            )
        return step

    def help(self) -> str:
        names = ", ".join(item.name for item in self.capabilities)
        return f"{self.description} Capacidades: {names}."
