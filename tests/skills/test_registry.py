import pytest

from ubuntu_ai.skills.builtin.defaults import default_skills
from ubuntu_ai.skills.registry import SkillRegistry


def test_registry_resolves_skill_by_capability() -> None:
    registry = SkillRegistry(default_skills())

    assert registry.for_capability("docker").name == "containers"
    assert registry.for_capability("apt").name == "packages"


def test_registry_rejects_duplicate_skill() -> None:
    skill = default_skills()[0]
    registry = SkillRegistry((skill,))

    with pytest.raises(ValueError, match="Skill já registrada"):
        registry.register(skill)


def test_registry_exposes_all_capabilities() -> None:
    registry = SkillRegistry(default_skills())

    assert {item.name for item in registry.capabilities()} == {
        "apt",
        "docker",
        "git",
        "python",
        "shell",
        "snap",
        "ssh",
        "systemctl",
    }
