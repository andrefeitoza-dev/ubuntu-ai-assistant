from ubuntu_ai.decision.models import Decision, DecisionStrategy, ExecutionMode


def test_decision_renders_prompt() -> None:
    decision = Decision(
        strategy=DecisionStrategy.CONSERVATIVE,
        execution_mode=ExecutionMode.REVIEW,
        preferred_tools=("git", "ruff"),
        preferred_skills=("git", "python"),
        risk_hints=("falha recente",),
        reasons=("contexto de risco",),
    )
    prompt = decision.to_prompt()
    assert "conservative" in prompt
    assert "review" in prompt
    assert "git" in prompt
    assert "python" in prompt
