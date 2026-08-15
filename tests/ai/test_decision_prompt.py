from ubuntu_ai.ai.prompt_builder import PlanningPromptBuilder


def test_prompt_builder_includes_decision_context() -> None:
    prompt = PlanningPromptBuilder().build(
        request="teste",
        decision_context="Strategy: balanced",
    )

    assert "Decisão operacional:" in prompt
    assert "Strategy: balanced" in prompt
    assert "Solicitação atual: teste" in prompt
