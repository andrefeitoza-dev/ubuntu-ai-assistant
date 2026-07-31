from __future__ import annotations

from pathlib import Path

from ubuntu_ai.plugins.loader import PluginLoader
from ubuntu_ai.plugins.registry import LoadedPlugin, PluginRegistry
from ubuntu_ai.skills import SkillRegistry


class PluginManager:
    """Coordinates discovery, loading and skill registration."""

    MANIFEST_NAMES = ("plugin.toml", "plugin.json")

    def __init__(
        self,
        registry: PluginRegistry,
        skill_registry: SkillRegistry,
        loader: PluginLoader | None = None,
    ) -> None:
        self._registry = registry
        self._skill_registry = skill_registry
        self._loader = loader or PluginLoader()

    def discover(self, directory: str | Path) -> tuple[Path, ...]:
        root = Path(directory)
        if not root.exists():
            return ()
        manifests = [
            path
            for name in self.MANIFEST_NAMES
            for path in root.rglob(name)
            if path.is_file()
        ]
        return tuple(sorted(set(manifests)))

    def install(self, manifest_path: str | Path) -> LoadedPlugin:
        loaded = self._loader.load(manifest_path)
        registered_skills: list[str] = []
        try:
            for skill in loaded.instance.skills():
                self._skill_registry.register(skill)
                registered_skills.append(skill.name)
            self._registry.register(loaded)
        except Exception:
            for skill_name in reversed(registered_skills):
                self._skill_registry.unregister(skill_name)
            loaded.instance.shutdown()
            raise
        return loaded

    def install_all(self, directory: str | Path) -> tuple[LoadedPlugin, ...]:
        return tuple(self.install(path) for path in self.discover(directory))

    def uninstall(self, name: str) -> LoadedPlugin:
        loaded = self._registry.unregister(name)
        for skill in loaded.instance.skills():
            try:
                self._skill_registry.unregister(skill.name)
            except KeyError:
                pass
        loaded.instance.shutdown()
        return loaded
