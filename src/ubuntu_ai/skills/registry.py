from __future__ import annotations

from collections.abc import Iterable

from ubuntu_ai.skills.base import Skill
from ubuntu_ai.tools.capability import ToolCapability


class SkillRegistry:
    """Registro central de skills e das capacidades que elas fornecem."""

    def __init__(self, skills: Iterable[Skill] = ()) -> None:
        self._skills: dict[str, Skill] = {}
        self._capability_owners: dict[str, str] = {}
        for skill in skills:
            self.register(skill)

    def register(self, skill: Skill, *, replace: bool = False) -> None:
        key = skill.name.strip().lower()
        if not key:
            raise ValueError("O nome da skill não pode estar vazio.")
        if key in self._skills and not replace:
            raise ValueError(f"Skill já registrada: {skill.name}")

        capability_names = [item.name.strip().lower() for item in skill.capabilities]
        if len(capability_names) != len(set(capability_names)):
            raise ValueError(f"A skill {skill.name} possui capacidades duplicadas.")

        for capability_name in capability_names:
            owner = self._capability_owners.get(capability_name)
            if owner is not None and owner != key and not replace:
                raise ValueError(f"Capacidade {capability_name} já pertence à skill {owner}.")

        if replace and key in self._skills:
            self.unregister(key)

        self._skills[key] = skill
        for capability_name in capability_names:
            self._capability_owners[capability_name] = key

    def unregister(self, name: str) -> Skill:
        key = name.strip().lower()
        try:
            skill = self._skills.pop(key)
        except KeyError as exc:
            raise KeyError(f"Skill não encontrada: {name}") from exc
        for capability in skill.capabilities:
            self._capability_owners.pop(capability.name.lower(), None)
        return skill

    def get(self, name: str) -> Skill:
        key = name.strip().lower()
        try:
            return self._skills[key]
        except KeyError as exc:
            raise KeyError(f"Skill não encontrada: {name}") from exc

    def for_capability(self, capability_name: str) -> Skill:
        key = capability_name.strip().lower()
        try:
            owner = self._capability_owners[key]
        except KeyError as exc:
            raise KeyError(f"Nenhuma skill fornece a capacidade: {capability_name}") from exc
        return self._skills[owner]

    def all(self) -> tuple[Skill, ...]:
        return tuple(sorted(self._skills.values(), key=lambda item: item.name))

    def capabilities(self) -> tuple[ToolCapability, ...]:
        capabilities = [capability for skill in self.all() for capability in skill.capabilities]
        return tuple(sorted(capabilities, key=lambda item: item.name))
