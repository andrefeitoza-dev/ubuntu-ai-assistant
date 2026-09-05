from __future__ import annotations

from collections import namedtuple
from pathlib import Path

from ubuntu_ai.context import SystemHealthService, SystemMetrics
from ubuntu_ai.fast_path import CareCommandResult, CareDiagnosticResponder

DiskUsage = namedtuple("DiskUsage", "total used free percent")


def test_disk_diagnostic_reports_pressure_and_guided_next_steps(monkeypatch) -> None:
    monkeypatch.setattr(
        "ubuntu_ai.fast_path.care.psutil.disk_usage",
        lambda _path: DiskUsage(100, 95, 4 * 1024**3, 95.0),
    )

    response = CareDiagnosticResponder(home=Path("/tmp")).respond(
        "analise por que o disco esta cheio"
    )

    assert response is not None
    assert "nível crítico" in response
    assert "Mostre os maiores diretórios" in response
    assert "Nada foi removido" in response


def test_security_audit_is_read_only_and_reports_real_command_results(monkeypatch) -> None:
    monkeypatch.setattr("ubuntu_ai.fast_path.care.shutil.which", lambda name: f"/usr/bin/{name}")
    commands: list[tuple[str, ...]] = []

    def run(command: tuple[str, ...]) -> CareCommandResult:
        commands.append(command)
        return CareCommandResult(0, "enabled\n")

    response = CareDiagnosticResponder(runner=run).respond(
        "faca uma auditoria basica de seguranca deste computador"
    )

    assert response is not None
    assert "somente leitura" in response
    assert "enabled" in response
    assert "exigirão um plano e confirmação" in response
    assert commands == [
        ("ufw", "status"),
        ("systemctl", "is-enabled", "unattended-upgrades.service"),
    ]


def test_unknown_care_request_continues_through_router() -> None:
    assert CareDiagnosticResponder().respond("conte uma historia") is None


def test_computer_overview_reports_useful_information_without_sensitive_details(
    monkeypatch,
) -> None:
    metrics = SystemMetrics(12.0, 45.0, 4096, 2.0, 55.0, 100.0, 2, 130, 3600)
    monkeypatch.setattr("ubuntu_ai.fast_path.care.shutil.which", lambda name: f"/usr/bin/{name}")

    def run(command: tuple[str, ...]) -> CareCommandResult:
        output = "active" if command[0] == "ufw" else "enabled"
        return CareCommandResult(0, output)

    response = CareDiagnosticResponder(
        runner=run,
        health_service=SystemHealthService(lambda: metrics),
    ).respond("como esta o computador")

    assert response is not None
    assert "Memória RAM: 45.0%" in response
    assert "Processos em andamento: 130" in response
    assert "Rede: interface ativa detectada" in response
    assert "Firewall: ativo" in response
    assert "não expõe endereços, portas, nomes de processos" in response


def test_overview_explains_when_firewall_needs_administrative_permission(
    monkeypatch,
) -> None:
    metrics = SystemMetrics(12.0, 45.0, 4096, 2.0, 55.0, 100.0, 1, 130, 3600)
    monkeypatch.setattr("ubuntu_ai.fast_path.care.shutil.which", lambda name: f"/usr/bin/{name}")

    response = CareDiagnosticResponder(
        runner=lambda _command: CareCommandResult(1, stderr="You need to be root"),
        health_service=SystemHealthService(lambda: metrics),
    ).respond("como esta o computador")

    assert response is not None
    assert "não confirmado sem permissão administrativa" in response
