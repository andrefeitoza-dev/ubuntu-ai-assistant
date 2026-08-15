from ubuntu_ai.planner.models import PlanningProfile


def test_planning_profile_renders_prompt() -> None:
    profile = PlanningProfile(
        profiles=("Git Repository",),
        recommendations=("Preserve o Git.",),
        risk_hints=("Falhas recentes.",),
        preferred_tools=("git", "ruff"),
    )

    prompt = profile.to_prompt()

    assert "Perfis detectados:" in prompt
    assert "Git Repository" in prompt
    assert "Recomendações:" in prompt
    assert "Preserve o Git." in prompt
    assert "Riscos observados:" in prompt
    assert "Ferramentas preferenciais:" in prompt
    assert "ruff" in prompt


def test_empty_planning_profile() -> None:
    profile = PlanningProfile()

    assert profile.is_empty()
    assert profile.to_prompt() == ""
