from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ubuntu_ai.plugins.api import PLUGIN_API_VERSION
from ubuntu_ai.plugins.exceptions import PluginError
from ubuntu_ai.plugins.manager import PluginManager
from ubuntu_ai.plugins.manifest import PluginManifest
from ubuntu_ai.plugins.sandbox import PluginPolicy
from ubuntu_ai.plugins.trust import PluginTrustStore


class PluginCatalogStatus(StrEnum):
    READY = "ready"
    UNTRUSTED = "untrusted"
    INCOMPATIBLE = "incompatible"
    DENIED = "denied"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class PluginCatalogEntry:
    manifest_path: Path
    name: str
    version: str
    status: PluginCatalogStatus
    reason: str
    fingerprint: str | None = None


class PluginCatalog:
    """Inspeciona manifestos sem importar ou inicializar código."""

    def __init__(
        self,
        trust_store: PluginTrustStore,
        policy: PluginPolicy | None = None,
    ) -> None:
        self._trust = trust_store
        self._policy = policy or PluginPolicy()

    def scan(self, directory: Path) -> tuple[PluginCatalogEntry, ...]:
        root = directory.expanduser().resolve()
        if not root.is_dir():
            return ()
        manifests = sorted(
            {
                manifest
                for name in PluginManager.MANIFEST_NAMES
                for manifest in root.rglob(name)
                if manifest.is_file()
            }
        )
        return tuple(self.inspect(path, root=root) for path in manifests)

    def inspect(self, manifest_path: Path, *, root: Path | None = None) -> PluginCatalogEntry:
        path = manifest_path.expanduser()
        boundary = (root or path.parent).resolve()
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(boundary):
                raise ValueError("Manifesto fora do catálogo ou acessado por link simbólico.")
            manifest = PluginManifest.load(path)
            fingerprint = self._trust.fingerprint(path)
            if manifest.api_version != PLUGIN_API_VERSION:
                return self._entry(
                    path,
                    manifest,
                    PluginCatalogStatus.INCOMPATIBLE,
                    "API incompatível.",
                    fingerprint,
                )
            try:
                self._policy.validate(manifest)
            except PluginError as exc:
                return self._entry(
                    path,
                    manifest,
                    PluginCatalogStatus.DENIED,
                    str(exc),
                    fingerprint,
                )
            if not self._trust.is_trusted(path):
                return self._entry(
                    path,
                    manifest,
                    PluginCatalogStatus.UNTRUSTED,
                    "Aprovação explícita necessária.",
                    fingerprint,
                )
            return self._entry(
                path,
                manifest,
                PluginCatalogStatus.READY,
                "Plugin compatível e aprovado.",
                fingerprint,
            )
        except Exception as exc:
            return PluginCatalogEntry(
                manifest_path=path,
                name=path.parent.name,
                version="",
                status=PluginCatalogStatus.INVALID,
                reason=str(exc),
            )

    @staticmethod
    def _entry(
        path: Path,
        manifest: PluginManifest,
        status: PluginCatalogStatus,
        reason: str,
        fingerprint: str,
    ) -> PluginCatalogEntry:
        return PluginCatalogEntry(
            manifest_path=path.resolve(),
            name=manifest.name,
            version=manifest.version,
            status=status,
            reason=reason,
            fingerprint=fingerprint,
        )
