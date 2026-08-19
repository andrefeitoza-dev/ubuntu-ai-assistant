from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ubuntu_ai.plugins.exceptions import PluginTrustError


class PluginTrustStore:
    """Registra aprovação explícita para o conteúdo completo de plugins."""

    def __init__(self, path: Path) -> None:
        self._path = path.expanduser()

    @staticmethod
    def fingerprint(manifest_path: Path) -> str:
        if manifest_path.is_symlink() or not manifest_path.is_file():
            raise PluginTrustError("O manifesto precisa ser um arquivo regular.")
        manifest = manifest_path.resolve()
        root = manifest.parent
        digest = hashlib.sha256()
        files = sorted(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".py", ".json", ".toml"}
        )
        if not files:
            raise PluginTrustError("O plugin não possui conteúdo verificável.")
        for path in files:
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise PluginTrustError("Links simbólicos não são aceitos em plugins.")
            digest.update(path.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def approve(self, manifest_path: Path) -> str:
        manifest = manifest_path.resolve()
        fingerprint = self.fingerprint(manifest)
        entries = self._read()
        entries[str(manifest)] = fingerprint
        self._write(entries)
        return fingerprint

    def is_trusted(self, manifest_path: Path) -> bool:
        manifest = manifest_path.resolve()
        expected = self._read().get(str(manifest))
        return expected is not None and expected == self.fingerprint(manifest)

    def require(self, manifest_path: Path) -> None:
        if not self.is_trusted(manifest_path):
            raise PluginTrustError(
                "Plugin não confiável ou alterado; aprove novamente antes de carregar."
            )

    def _read(self) -> dict[str, str]:
        if not self._path.is_file():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PluginTrustError("O armazenamento de confiança está inválido.") from exc
        if not isinstance(raw, dict):
            raise PluginTrustError("O armazenamento de confiança está inválido.")
        return {str(key): str(value) for key, value in raw.items()}

    def _write(self, entries: dict[str, str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = self._path.with_suffix(f"{self._path.suffix}.tmp")
        temporary.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(self._path)
        self._path.chmod(0o600)
