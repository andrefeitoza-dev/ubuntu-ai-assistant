from pathlib import Path

from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.runtime_integration.context_builder import RuntimeContextBuilder
from ubuntu_ai.runtime_integration.models import RuntimeRequest


def test_context_builder_uses_explicit_snapshot() -> None:
    snapshot = ContextSnapshot(
        session_id="s",
        working_directory=Path("/tmp"),
        operating_system="Linux",
    )

    result = RuntimeContextBuilder().build(
        RuntimeRequest(
            request="status",
            session_id="s",
            context=snapshot,
        )
    )

    assert result is snapshot
