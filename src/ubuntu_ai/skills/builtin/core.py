from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePath

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
        """Valida a compatibilidade entre a etapa e a capacidade selecionada.

        A capacidade ``shell`` é o fallback geral do agente. Ela aceita qualquer
        executável não vazio; a autorização final continua sob responsabilidade
        das políticas de execução e do preflight.
        """

        del context
        Skill.prepare(self, step)

        capability = next(
            item for item in self.capabilities if item.name == (step.tool_name or "shell")
        )
        executable = self._resolve_executable(step.command)

        if capability.name == "shell":
            return step

        if not capability.supports_executable(executable):
            raise ValueError(
                f"A skill {self.name} não aceita o executável {executable} "
                f"para a capacidade {capability.name}."
            )

        return step

    def help(self) -> str:
        names = ", ".join(item.name for item in self.capabilities)
        return f"{self.description} Capacidades: {names}."

    @staticmethod
    def _resolve_executable(command: list[str] | tuple[str, ...]) -> str:
        """Obtém o executável real, ignorando wrappers e opções comuns."""

        if not command:
            raise ValueError("A etapa da skill precisa conter um comando.")

        arguments = list(command)
        index = 0

        while index < len(arguments):
            token = arguments[index]
            normalized = PurePath(token).name.lower()

            if normalized == "sudo":
                index = BuiltinSkill._skip_sudo_options(arguments, index + 1)
                continue

            if normalized == "env":
                index = BuiltinSkill._skip_env_prefix(arguments, index + 1)
                continue

            if normalized in {"command", "nohup"}:
                index += 1
                continue

            if "=" in token and not token.startswith(("/", "./", "../")):
                name, _, _ = token.partition("=")
                if name.isidentifier():
                    index += 1
                    continue

            return normalized

        raise ValueError("Não foi possível identificar o executável da etapa.")

    @staticmethod
    def _skip_sudo_options(arguments: list[str], index: int) -> int:
        options_with_value = {
            "-C",
            "-D",
            "-R",
            "-T",
            "-U",
            "-g",
            "-h",
            "-p",
            "-r",
            "-t",
            "-u",
        }

        while index < len(arguments) and arguments[index].startswith("-"):
            option = arguments[index]
            index += 1
            if option in options_with_value and index < len(arguments):
                index += 1

        return index

    @staticmethod
    def _skip_env_prefix(arguments: list[str], index: int) -> int:
        while index < len(arguments):
            token = arguments[index]

            if token == "--":
                return index + 1

            if token.startswith("-"):
                index += 1
                continue

            name, separator, _ = token.partition("=")
            if separator and name.isidentifier():
                index += 1
                continue

            return index

        return index
