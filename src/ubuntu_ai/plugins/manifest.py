from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ubuntu_ai.plugins.exceptions import PluginManifestError

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


@dataclass(frozen=True, slots=True)
class PluginManifest:
    """Declarative metadata that describes a plugin package."""

    name: str
    version: str
    api_version: int
    entrypoint: str
    author: str = ""
    description: str = ""
    permissions: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> PluginManifest:
        try:
            name = str(data["name"]).strip().lower()
            version = str(data["version"]).strip()
            api_version = int(data["api_version"])
            entrypoint = str(data["entrypoint"]).strip()
        except (KeyError, TypeError, ValueError) as exc:
            raise PluginManifestError(
                "Manifesto precisa conter name, version, api_version e entrypoint."
            ) from exc

        if not _NAME_RE.fullmatch(name):
            raise PluginManifestError(f"Nome de plugin inválido: {name!r}")
        if not version:
            raise PluginManifestError("A versão do plugin não pode estar vazia.")
        if api_version < 1:
            raise PluginManifestError("api_version precisa ser maior ou igual a 1.")
        if ":" not in entrypoint:
            raise PluginManifestError("entrypoint deve usar o formato 'modulo:objeto'.")

        raw_permissions = data.get("permissions", ())
        if isinstance(raw_permissions, str) or not isinstance(raw_permissions, (list, tuple)):
            raise PluginManifestError("permissions deve ser uma lista de strings.")
        permissions = tuple(
            sorted({str(item).strip().lower() for item in raw_permissions if str(item).strip()})
        )

        return cls(
            name=name,
            version=version,
            api_version=api_version,
            entrypoint=entrypoint,
            author=str(data.get("author", "")).strip(),
            description=str(data.get("description", "")).strip(),
            permissions=permissions,
        )

    @classmethod
    def load(cls, path: str | Path) -> PluginManifest:
        manifest_path = Path(path)
        if not manifest_path.is_file():
            raise PluginManifestError(f"Manifesto não encontrado: {manifest_path}")
        try:
            if manifest_path.suffix.lower() == ".json":
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            elif manifest_path.suffix.lower() == ".toml":
                with manifest_path.open("rb") as stream:
                    data = tomllib.load(stream)
            else:
                raise PluginManifestError("Formato não suportado. Use plugin.toml ou plugin.json.")
        except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
            raise PluginManifestError(f"Não foi possível ler o manifesto {manifest_path}.") from exc

        if not isinstance(data, dict):
            raise PluginManifestError("O manifesto precisa conter um objeto raiz.")
        plugin_data = data.get("plugin", data)
        if not isinstance(plugin_data, dict):
            raise PluginManifestError("A seção [plugin] precisa ser um objeto.")
        return cls.from_mapping(plugin_data)
