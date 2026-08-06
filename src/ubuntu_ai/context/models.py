from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ubuntu_ai.context.discovery.models import EnvironmentSnapshot


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """Immutable snapshot of the information available to the agent."""

    session_id: str
    working_directory: Path
    operating_system: str
    project_name: str | None = None
    last_commands: tuple[str, ...] = ()
    last_errors: tuple[str, ...] = ()
    previous_request: str | None = None
    conversation_history: tuple[str, ...] = ()
    environment: EnvironmentSnapshot | None = None

    def to_prompt(self) -> str:
        """Render the snapshot as compact planning context."""

        project = self.project_name or "none"
        previous_request = self.previous_request or "none"
        commands = ", ".join(self.last_commands) or "none"
        errors = " | ".join(self.last_errors) or "none"
        conversation = " | ".join(self.conversation_history) or "none"

        if self.environment is None:
            environment = "none"
        else:
            environment = (
                f"project={self.environment.project_name}; "
                f"git={self.environment.git_repository}; "
                f"branch={self.environment.git_branch}; "
                f"python={self.environment.python_version}; "
                f"venv={self.environment.virtual_environment}; "
                f"docker={self.environment.docker_available}; "
                f"ollama={self.environment.ollama_available}"
            )

        return (
            f"session_id={self.session_id}\n"
            f"working_directory={self.working_directory}\n"
            f"operating_system={self.operating_system}\n"
            f"project_name={project}\n"
            f"previous_request={previous_request}\n"
            f"last_commands={commands}\n"
            f"last_errors={errors}\n"
            f"conversation_history={conversation}\n"
            f"environment={environment}"
        )