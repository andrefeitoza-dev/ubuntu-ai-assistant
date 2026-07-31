from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from ubuntu_ai.plugins.api import PLUGIN_API_VERSION, PluginContext, UbuntuAIPlugin
from ubuntu_ai.plugins.exceptions import (
    PluginCompatibilityError,
    PluginLoadError,
)
from ubuntu_ai.plugins.manifest import PluginManifest
from ubuntu_ai.plugins.registry import LoadedPlugin
from ubuntu_ai.plugins.sandbox import PluginPolicy


class PluginLoader:
    """Loads a plugin from a validated manifest and explicit entrypoint."""

    def __init__(self, policy: PluginPolicy | None = None) -> None:
        self._policy = policy or PluginPolicy()

    def load(self, manifest_path: str | Path) -> LoadedPlugin:
        path = Path(manifest_path).resolve()
        manifest = PluginManifest.load(path)
        if manifest.api_version != PLUGIN_API_VERSION:
            raise PluginCompatibilityError(
                f"Plugin {manifest.name} usa API {manifest.api_version}; "
                f"esta versão suporta API {PLUGIN_API_VERSION}."
            )
        self._policy.validate(manifest)

        module_name, object_name = manifest.entrypoint.split(":", 1)
        plugin_root = str(path.parent)
        inserted = plugin_root not in sys.path
        if inserted:
            sys.path.insert(0, plugin_root)
        try:
            module = importlib.import_module(module_name)
            target: Any = getattr(module, object_name)
            instance = target() if isinstance(target, type) else target
        except Exception as exc:
            raise PluginLoadError(
                f"Falha ao carregar o entrypoint de {manifest.name}."
            ) from exc
        finally:
            if inserted:
                sys.path.remove(plugin_root)

        if not isinstance(instance, UbuntuAIPlugin):
            raise PluginLoadError(
                f"Entrypoint de {manifest.name} não implementa UbuntuAIPlugin."
            )
        try:
            instance.initialize(PluginContext())
        except Exception as exc:
            raise PluginLoadError(
                f"Falha ao inicializar o plugin {manifest.name}."
            ) from exc
        return LoadedPlugin(manifest=manifest, instance=instance)
