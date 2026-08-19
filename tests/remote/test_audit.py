from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.remote.audit import RemoteAuditService
from ubuntu_ai.remote.models import RemoteExecutionResult, RemoteHost, RemoteHostKind


def test_audit_writes_protected_host_scoped_jsonl(tmp_path) -> None:
    service = RemoteAuditService(tmp_path / "audit")
    host = RemoteHost(name="production", kind=RemoteHostKind.SSH, hostname="server.local")
    result = RemoteExecutionResult("production", ("uname",), 0, "ok", "")

    service.record(
        host,
        ("uname",),
        RiskLevel.LOW,
        result=result,
        status="completed",
    )

    records = service.records("production")
    path = tmp_path / "audit" / "production.jsonl"
    assert len(records) == 1
    assert records[0].host == "production"
    assert records[0].command == ("uname",)
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700


def test_audit_keeps_different_hosts_in_different_files(tmp_path) -> None:
    service = RemoteAuditService(tmp_path)
    first = RemoteHost(name="first", kind=RemoteHostKind.SSH, hostname="first.local")
    second = RemoteHost(name="second", kind=RemoteHostKind.SSH, hostname="second.local")

    service.record(first, ("uptime",), RiskLevel.LOW, status="started")
    service.record(second, ("uptime",), RiskLevel.LOW, status="started")

    assert len(service.records("first")) == 1
    assert len(service.records("second")) == 1


def test_audit_redacts_common_secret_arguments(tmp_path) -> None:
    service = RemoteAuditService(tmp_path)
    host = RemoteHost(name="server", kind=RemoteHostKind.SSH, hostname="server.local")

    service.record(
        host,
        ("client", "--token", "secret-value", "--password=hidden"),
        RiskLevel.HIGH,
        status="started",
    )

    assert service.records("server")[0].command == (
        "client",
        "--token",
        "***",
        "--password=***",
    )
