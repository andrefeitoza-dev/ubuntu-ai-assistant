from pathlib import Path

from ubuntu_ai.ai.prompt_builder import PlanningPromptBuilder
from ubuntu_ai.context.models import ContextSnapshot


def test_prompt_builder_includes_context_and_conversation() -> None:
    context = ContextSnapshot(
        session_id="session",
        working_directory=Path("/tmp/project"),
        operating_system="Ubuntu",
        conversation_history=("user: install docker", "assistant: plan ready"),
    )

    prompt = PlanningPromptBuilder().build(
        request="now postgres",
        context=context,
    )

    assert "session_id=session" in prompt
    assert "user: install docker" in prompt
    assert "Solicitação atual: now postgres" in prompt
