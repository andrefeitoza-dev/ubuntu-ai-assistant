import platform
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AgentContext:
    """Contexto atual disponível para o Agent Runtime."""

    working_directory: Path
    operating_system: str
    project_name: str | None = None


class ContextProvider:
    """Descobre informações básicas do ambiente atual."""

    def get_context(self) -> AgentContext:
        working_directory = Path.cwd()

        project_name = (
            working_directory.name if (working_directory / "pyproject.toml").exists() else None
        )

        return AgentContext(
            working_directory=working_directory,
            operating_system=platform.system(),
            project_name=project_name,
        )
