from __future__ import annotations

from dataclasses import dataclass, field

from ubuntu_ai.plugins.exceptions import PluginPermissionError
from ubuntu_ai.plugins.manifest import PluginManifest

DEFAULT_ALLOWED_PERMISSIONS = frozenset({"knowledge.read", "learning.write"})


@dataclass(frozen=True, slots=True)
class PluginPolicy:
    """Admission policy for plugins.

    This is a capability gate, not an operating-system process sandbox.
    """

    allowed_permissions: frozenset[str] = field(default_factory=lambda: DEFAULT_ALLOWED_PERMISSIONS)

    def validate(self, manifest: PluginManifest) -> None:
        denied = sorted(set(manifest.permissions) - self.allowed_permissions)
        if denied:
            names = ", ".join(denied)
            raise PluginPermissionError(
                f"Plugin {manifest.name} solicita permissões não autorizadas: {names}"
            )
