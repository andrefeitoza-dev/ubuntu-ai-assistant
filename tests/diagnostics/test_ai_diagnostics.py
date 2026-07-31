from typing import Any

from ubuntu_ai.core.config import AppConfig
from ubuntu_ai.diagnostics.ai_diagnostics import AIDiagnosticsService
from ubuntu_ai.diagnostics.models import DiagnosticStatus
from ubuntu_ai.services.ollama import OllamaInfo


class FakeOllamaService:
    def __init__(self, responses: list[str]) -> None:
        self._responses = iter(responses)
        self.prompts: list[str] = []

    def get_info(self) -> OllamaInfo:
        return OllamaInfo(
            available=True,
            version="0.1.0",
            models=["qwen2.5:3b"],
        )

    def generate(self, prompt: str, model: str) -> str:
        self.prompts.append(prompt)
        return next(self._responses)


def test_diagnostics_validates_minimal_and_structured_generation() -> None:
    service = AIDiagnosticsService(
        config=AppConfig(),
        ollama_service=FakeOllamaService(  # type: ignore[arg-type]
            [
                "OK",
                (
                    '{"goal":"Mostrar diretório","estimated_seconds":1,'
                    '"risk":"low","steps":[{"title":"Executar pwd",'
                    '"description":"Mostra o diretório",'
                    '"command":["pwd"]}]}'
                ),
            ]
        ),
    )

    report = service.run()

    assert report.successful is True
    assert len(report.checks) == 5
    assert all(check.status is DiagnosticStatus.PASSED for check in report.checks)


def test_diagnostics_warns_when_structured_response_is_not_json() -> None:
    service = AIDiagnosticsService(
        config=AppConfig(),
        ollama_service=FakeOllamaService(  # type: ignore[arg-type]
            ["OK", "Não consigo gerar JSON."],
        ),
    )

    report = service.run()

    structured = next(
        check for check in report.checks if check.name == "Geração estruturada"
    )
    assert structured.status is DiagnosticStatus.WARNING
    assert report.successful is True


def test_extract_json_accepts_markdown_fence() -> None:
    content = """```json
{"goal": "Teste"}
```"""

    assert AIDiagnosticsService._extract_json(content) == '{"goal": "Teste"}'
