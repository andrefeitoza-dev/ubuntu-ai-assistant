import pytest

from ubuntu_ai.domain.plan import PlanStep
from ubuntu_ai.skills import SkillManager, SkillRegistry, default_skills


def build_manager() -> SkillManager:
    return SkillManager(SkillRegistry(default_skills()))


@pytest.mark.parametrize(
    "command",
    [
        ["pwd"],
        ["ls", "-la"],
        ["whoami"],
        ["hostname"],
        ["/usr/bin/pwd"],
        ["env", "LANG=C", "pwd"],
        ["VAR=value", "pwd"],
        ["sudo", "-u", "root", "pwd"],
        ["nohup", "pwd"],
    ],
)
def test_shell_skill_accepts_general_executables(command: list[str]) -> None:
    manager = build_manager()
    step = PlanStep(
        "Comando shell",
        "Executar comando geral",
        command,
        tool_name="shell",
    )

    assert manager.prepare_step(step) is step


def test_specialized_skill_accepts_absolute_executable_path() -> None:
    manager = build_manager()
    step = PlanStep(
        "Git status",
        "Consultar repositório",
        ["/usr/bin/git", "status"],
        tool_name="git",
    )

    assert manager.prepare_step(step) is step


def test_specialized_skill_resolves_sudo_and_env_wrappers() -> None:
    manager = build_manager()
    apt_step = PlanStep(
        "Atualizar pacotes",
        "Atualizar índices",
        ["sudo", "-u", "root", "apt", "update"],
        tool_name="apt",
    )
    python_step = PlanStep(
        "Executar Python",
        "Executar script",
        ["env", "PYTHONPATH=src", "python3", "app.py"],
        tool_name="python",
    )

    assert manager.prepare_step(apt_step) is apt_step
    assert manager.prepare_step(python_step) is python_step


def test_specialized_skill_still_rejects_incompatible_executable() -> None:
    manager = build_manager()
    step = PlanStep(
        "Comando incompatível",
        "Não deve usar Git como Docker",
        ["git", "status"],
        tool_name="docker",
    )

    with pytest.raises(ValueError, match="não aceita o executável git"):
        manager.prepare_step(step)
