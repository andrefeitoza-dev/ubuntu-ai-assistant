from __future__ import annotations

import json
import os
import platform
import stat
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

from ubuntu_ai.version import __version__


class SanitizedDiagnosticExporter:
    """Exporta somente metadados agregados para um arquivo privado."""

    def __init__(self, directory: Path | None = None) -> None:
        self._directory = directory or (Path.home() / "Downloads")

    def export(
        self,
        *,
        audit_records: tuple[Any, ...] = (),
        simulation: bool,
        denied_capabilities: tuple[str, ...],
    ) -> Path:
        directory = self._directory.expanduser()
        if directory.exists() and (directory.is_symlink() or not directory.is_dir()):
            raise OSError("O destino do diagnóstico não é um diretório seguro.")
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        resolved = directory.resolve(strict=True)
        if directory.is_symlink():
            raise OSError("Links simbólicos não são aceitos para exportação.")

        now = datetime.now(UTC)
        destination = resolved / f"ubuntu-ai-diagnostico-{now:%Y%m%d-%H%M%S-%f}.json"
        statuses = Counter(str(getattr(record, "status", "unknown")) for record in audit_records)
        process = psutil.Process()
        payload = {
            "schema": 1,
            "generated_at": now.isoformat(),
            "application": {
                "name": "Ubuntu AI Assistant",
                "version": __version__,
                "creator": "Andre Anderson Feitoza",
            },
            "environment": {
                "system": platform.system(),
                "release": platform.release(),
                "python": platform.python_version(),
            },
            "runtime": {
                "rss_mib": round(process.memory_info().rss / (1024 * 1024), 1),
                "threads": process.num_threads(),
                "simulation": simulation,
                "denied_capabilities": list(denied_capabilities),
            },
            "audit_summary": {
                "records_considered": len(audit_records),
                "statuses": dict(sorted(statuses.items())),
            },
            "privacy": (
                "Sem conversas, comandos, stdout/stderr, hostname, tokens ou caminhos privados."
            ),
        }
        descriptor = os.open(
            destination,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
            0o600,
        )
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise OSError("O destino do diagnóstico não é um arquivo regular.")
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.chmod(destination, 0o600)
        return destination
