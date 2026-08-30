from __future__ import annotations

import json
import os
import shlex
import stat
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from ubuntu_ai.execution.models import ExecutionResult


def default_local_action_audit_path() -> Path:
    return Path.home() / ".local" / "state" / "ubuntu-ai" / "audit" / "local-actions.jsonl"


@dataclass(frozen=True, slots=True)
class LocalActionAuditRecord:
    timestamp: str
    session_id: str
    request: str
    intent: str
    target: str | None
    command: tuple[str, ...]
    policy_reason: str | None
    status: str
    message: str
    return_code: int | None
    duration: float | None


class LocalActionAuditService:
    """Persiste metadados redigidos das ações locais em JSONL protegido."""

    _SECRET_OPTIONS = frozenset({"--password", "--secret", "--token", "-p"})

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or default_local_action_audit_path()

    def record(
        self,
        *,
        session_id: str,
        request: str,
        intent: str,
        command: str,
        result: ExecutionResult,
    ) -> LocalActionAuditRecord:
        arguments = tuple(shlex.split(command))
        protected = self._redact(arguments[:32])
        record = LocalActionAuditRecord(
            timestamp=datetime.now(UTC).isoformat(),
            session_id=session_id,
            request=self._clean(self._redact_text(request), limit=1000),
            intent=self._clean(intent, limit=200),
            target=self._target(protected),
            command=protected,
            policy_reason=result.policy_reason,
            status=result.status.value,
            message=self._clean(result.message, limit=500),
            return_code=result.return_code,
            duration=result.duration,
        )
        self._path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self._path.parent, 0o700)
        descriptor = os.open(
            self._path,
            os.O_APPEND | os.O_CREAT | os.O_WRONLY | os.O_NOFOLLOW,
            0o600,
        )
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise OSError("O destino da auditoria não é um arquivo regular.")
        with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
        os.chmod(self._path, 0o600)
        return record

    def records(self, *, limit: int = 100) -> tuple[LocalActionAuditRecord, ...]:
        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")
        if not self._path.is_file():
            return ()
        records: list[LocalActionAuditRecord] = []
        for line in self._path.read_text(encoding="utf-8").splitlines()[-limit:]:
            if not line.strip():
                continue
            data = json.loads(line)
            data["command"] = tuple(data["command"])
            records.append(LocalActionAuditRecord(**data))
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
            if option.casefold() in cls._SECRET_OPTIONS:
                protected.append(f"{option}=***" if separator else argument)
                redact_next = not separator
                continue
            protected.append(cls._clean(cls._safe_url(argument), limit=500))
        return tuple(protected)

    @staticmethod
    def _safe_url(value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return value
        host = parsed.hostname
        try:
            port = parsed.port
        except ValueError:
            return "[invalid-url]"
        if port is not None:
            host = f"{host}:{port}"
        return urlunsplit((parsed.scheme, host, "", "", ""))

    @classmethod
    def _redact_text(cls, value: str) -> str:
        try:
            arguments = tuple(shlex.split(value))
        except ValueError:
            return "[unparseable-request]"
        return " ".join(cls._redact(arguments))

    @staticmethod
    def _target(command: tuple[str, ...]) -> str | None:
        if len(command) < 2:
            return command[0] if command else None
        return command[-1]

    @staticmethod
    def _clean(value: str, *, limit: int) -> str:
        clean = "".join(character if ord(character) >= 32 else " " for character in value)
        return " ".join(clean.split())[:limit]
