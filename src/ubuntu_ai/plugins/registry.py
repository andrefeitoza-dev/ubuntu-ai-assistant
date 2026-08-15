from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.plugins.api import UbuntuAIPlugin
from ubuntu_ai.plugins.manifest import PluginManifest


@dataclass(frozen=True, slots=True)
class LoadedPlugin:
    manifest: PluginManifest
    instance: UbuntuAIPlugin


class PluginRegistry:
    """Tracks loaded plugins and prevents duplicate identities."""

    def __init__(self) -> None:
        self._plugins: dict[str, LoadedPlugin] = {}

    def register(self, plugin: LoadedPlugin) -> None:
        name = plugin.manifest.name
        if name in self._plugins:
            raise ValueError(f"Plugin já registrado: {name}")
        self._plugins[name] = plugin

    def unregister(self, name: str) -> LoadedPlugin:
        key = name.strip().lower()
        try:
            return self._plugins.pop(key)
        except KeyError as exc:
            raise KeyError(f"Plugin não encontrado: {name}") from exc

    def get(self, name: str) -> LoadedPlugin:
        key = name.strip().lower()
        try:
            return self._plugins[key]
        except KeyError as exc:
            raise KeyError(f"Plugin não encontrado: {name}") from exc

    def all(self) -> tuple[LoadedPlugin, ...]:
        return tuple(self._plugins[name] for name in sorted(self._plugins))
