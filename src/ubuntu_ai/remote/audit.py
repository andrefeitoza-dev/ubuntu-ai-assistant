from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.remote.models import RemoteExecutionResult, RemoteHost


def default_remote_audit_directory() -> Path:
    return Path.home() / ".local" / "state" / "ubuntu-ai" / "remote"


@dataclass(frozen=True, slots=True)
class RemoteAuditRecord:
    timestamp: str
    host: str
    hostname: str | None
    command: tuple[str, ...]
    risk: str
    return_code: int | None
    status: str


class RemoteAuditService:
    """Mantém trilha JSONL separada e protegida para cada destino."""

    _SECRET_OPTIONS = {"--password", "--token", "--secret", "-p"}

    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def record(
        self,
        host: RemoteHost,
        command: tuple[str, ...],
        risk: RiskLevel,
        *,
        result: RemoteExecutionResult | None = None,
        status: str,
    ) -> RemoteAuditRecord:
        record = RemoteAuditRecord(
            timestamp=datetime.now(UTC).isoformat(),
            host=host.name,
            hostname=host.hostname,
            command=self._redact(command),
            risk=risk.value,
            return_code=None if result is None else result.return_code,
            status=status,
        )
        self._directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self._directory, 0o700)
        path = self._directory / f"{host.name.lower()}.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        os.chmod(path, 0o600)
        return record

    def records(self, host_name: str) -> tuple[RemoteAuditRecord, ...]:
        path = self._directory / f"{host_name.strip().lower()}.jsonl"
        if not path.exists():
            return ()
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            data["command"] = tuple(data["command"])
            records.append(RemoteAuditRecord(**data))
        return tuple(records)

    @classmethod
    def _redact(cls, command: tuple[str, ...]) -> tuple[str, ...]:
        protected: list[str] = []
        redact_next = False
        for argument in command:
            if redact_next:
                protected.append("***")
                redact_next = False
                continue
            option, separator, _value = argument.partition("=")
            if option.lower() in cls._SECRET_OPTIONS:
                protected.append(f"{option}=***" if separator else argument)
                redact_next = not separator
                continue
            protected.append(argument)
        return tuple(protected)
