from importlib import import_module

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app
from ubuntu_ai.diagnostics.models import (
    AIDiagnosticReport,
    DiagnosticCheck,
    DiagnosticStatus,
)

runner = CliRunner()
module = import_module("ubuntu_ai.cli.diagnose_ai")


class FakeDiagnosticsService:
    def __init__(self, successful: bool = True) -> None:
        self._successful = successful

    def run(self, request: str) -> AIDiagnosticReport:
        status = DiagnosticStatus.PASSED if self._successful else DiagnosticStatus.FAILED
        return AIDiagnosticReport(
            provider="ollama",
            model="qwen2.5:3b",
            checks=(
                DiagnosticCheck(
                    name="Servidor Ollama",
                    status=status,
                    message="Resultado do teste.",
                    duration_seconds=0.1,
                ),
            ),
        )


def test_diagnose_ai_command_displays_report(monkeypatch) -> None:
    monkeypatch.setattr(
        module.container,
        "ai_diagnostics_service",
        lambda: FakeDiagnosticsService(),
    )

    result = runner.invoke(app, ["diagnose-ai"])

    assert result.exit_code == 0
    assert "Diagnóstico do Runtime de IA" in result.stdout
    assert "qwen2.5:3b" in result.stdout


def test_diagnose_ai_command_fails_when_runtime_is_unhealthy(monkeypatch) -> None:
    monkeypatch.setattr(
        module.container,
        "ai_diagnostics_service",
        lambda: FakeDiagnosticsService(successful=False),
    )

    result = runner.invoke(app, ["diagnose-ai"])

    assert result.exit_code == 1
    assert "FALHA" in result.stdout
