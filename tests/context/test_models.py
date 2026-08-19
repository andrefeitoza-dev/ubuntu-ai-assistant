from pathlib import Path

from ubuntu_ai.context import HealthStatus, SystemHealthSnapshot, SystemMetrics
from ubuntu_ai.context.discovery.models import EnvironmentSnapshot
from ubuntu_ai.context.models import ContextSnapshot


def test_context_snapshot_renders_prompt() -> None:
    snapshot = ContextSnapshot(
        session_id="session-1",
        working_directory=Path("/tmp/project"),
        operating_system="Linux",
        project_name="project",
        last_commands=("echo ok",),
        last_errors=("false: failed",),
        previous_request="Mostre o status",
    )

    prompt = snapshot.to_prompt()

    assert "session_id=session-1" in prompt
    assert "project_name=project" in prompt
    assert "last_commands=echo ok" in prompt
    assert "previous_request=Mostre o status" in prompt


def test_context_snapshot_includes_automatic_system_health() -> None:
    health = SystemHealthSnapshot(
        SystemMetrics(10, 40, 4096, 0, 50, 100, 1, 120, 3600),
        HealthStatus.HEALTHY,
    )
    environment = EnvironmentSnapshot(
        working_directory="/tmp/project",
        project_name="project",
        git_repository=True,
        git_branch="main",
        python_version="3.12",
        virtual_environment=None,
        docker_available=False,
        ollama_available=True,
        operating_system="Ubuntu",
        health=health,
    )
    snapshot = ContextSnapshot(
        session_id="session-1",
        working_directory=Path("/tmp/project"),
        operating_system="Linux",
        environment=environment,
    )

    prompt = snapshot.to_prompt()

    assert "health=(status=healthy" in prompt
    assert "memory_available_mb=4096" in prompt
