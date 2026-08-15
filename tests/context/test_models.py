from pathlib import Path

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
