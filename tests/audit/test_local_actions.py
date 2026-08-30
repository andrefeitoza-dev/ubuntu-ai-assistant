import json
from pathlib import Path

import pytest

from ubuntu_ai.audit import LocalActionAuditService
from ubuntu_ai.execution import ExecutionResult, ExecutionStatus


def result(**overrides) -> ExecutionResult:
    values = {
        "status": ExecutionStatus.EXECUTED,
        "message": "Solicitação enviada.",
        "command": "firefox https://example.com/private?token=secret",
        "return_code": 0,
        "duration": 0.2,
        "policy_reason": "Comando autorizado.",
    }
    values.update(overrides)
    return ExecutionResult(**values)


def test_records_protected_structured_local_action(tmp_path: Path) -> None:
    path = tmp_path / "audit" / "local-actions.jsonl"
    service = LocalActionAuditService(path)

    record = service.record(
        session_id="session-1",
        request="Abra o site privado.",
        intent="Abrir site",
        command="firefox https://example.com/private?token=secret",
        result=result(),
    )

    assert record.target == "https://example.com"
    assert record.command == ("firefox", "https://example.com")
    assert record.policy_reason == "Comando autorizado."
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    assert service.records() == (record,)


def test_redacts_secret_options_in_command_and_request(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    service = LocalActionAuditService(path)

    service.record(
        session_id="session-1",
        request="execute ferramenta --token segredo",
        intent="Teste",
        command="ferramenta --password=segredo --token segredo",
        result=result(),
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "segredo" not in path.read_text(encoding="utf-8")
    assert payload["command"] == ["ferramenta", "--password=***", "--token", "***"]
    assert payload["request"] == "execute ferramenta --token ***"


def test_records_block_reason_without_output_payload(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    service = LocalActionAuditService(path)

    record = service.record(
        session_id="session-1",
        request="Execute algo inseguro",
        intent="Executar",
        command="rm -rf /",
        result=result(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado.",
            policy_reason="Comando crítico bloqueado.",
            stdout="conteúdo sensível",
            stderr="detalhe sensível",
        ),
    )

    assert record.status == "blocked"
    assert record.policy_reason == "Comando crítico bloqueado."
    serialized = path.read_text(encoding="utf-8")
    assert "conteúdo sensível" not in serialized
    assert "detalhe sensível" not in serialized


def test_rejects_invalid_history_limit(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="limite"):
        LocalActionAuditService(tmp_path / "audit.jsonl").records(limit=0)


def test_refuses_symbolic_link_as_audit_file(tmp_path: Path) -> None:
    destination = tmp_path / "destination"
    destination.write_text("preserve", encoding="utf-8")
    audit = tmp_path / "audit.jsonl"
    audit.symlink_to(destination)

    with pytest.raises(OSError):
        LocalActionAuditService(audit).record(
            session_id="session-1",
            request="Abra o Firefox",
            intent="Abrir aplicativo",
            command="gtk-launch firefox",
            result=result(),
        )

    assert destination.read_text(encoding="utf-8") == "preserve"
