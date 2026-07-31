import pytest

from ubuntu_ai.domain.plan import PlanStep
from ubuntu_ai.skills import SkillManager, SkillRegistry, default_skills


def test_manager_prepares_compatible_step() -> None:
    manager = SkillManager(SkillRegistry(default_skills()))
    step = PlanStep("Status", "Ver Docker", ["docker", "ps"], tool_name="docker")

    assert manager.prepare_step(step) is step


def test_manager_rejects_command_owned_by_another_skill() -> None:
    manager = SkillManager(SkillRegistry(default_skills()))
    step = PlanStep("Erro", "Comando incompatível", ["git", "status"], tool_name="docker")

    with pytest.raises(ValueError, match="não aceita o executável"):
        manager.prepare_step(step)
