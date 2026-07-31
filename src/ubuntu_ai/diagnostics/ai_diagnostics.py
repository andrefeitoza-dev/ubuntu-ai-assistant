from __future__ import annotations

import json
from collections.abc import Callable
from time import perf_counter

from ubuntu_ai.ai.prompt_builder import PlanningPromptBuilder
from ubuntu_ai.core.config import AppConfig
from ubuntu_ai.diagnostics.models import (
    AIDiagnosticReport,
    DiagnosticCheck,
    DiagnosticStatus,
)
from ubuntu_ai.services.ollama import OllamaService

ProgressCallback = Callable[[str], None]


class AIDiagnosticsService:
    """Executa verificações isoladas no runtime local de IA."""

    def __init__(
        self,
        *,
        config: AppConfig,
        ollama_service: OllamaService,
        prompt_builder: PlanningPromptBuilder | None = None,
    ) -> None:
        self._config = config
        self._ollama_service = ollama_service
        self._prompt_builder = prompt_builder or PlanningPromptBuilder()

    def run(
        self,
        request: str = "mostrar o diretório atual",
        *,
        progress: ProgressCallback | None = None,
    ) -> AIDiagnosticReport:
        """Verifica servidor, modelo, geração mínima e geração estruturada."""

        checks: list[DiagnosticCheck] = []

        self._notify(progress, "Consultando o servidor Ollama...")
        checks.append(self._check_server())
        if checks[-1].status is DiagnosticStatus.FAILED:
            return self._report(checks)

        self._notify(progress, "Validando o modelo configurado...")
        checks.append(self._check_model())
        if checks[-1].status is DiagnosticStatus.FAILED:
            return self._report(checks)

        self._notify(progress, "Executando geração mínima...")
        checks.append(
            self._check_generation(
                name="Geração mínima",
                prompt="Responda somente OK.",
                expect_json=False,
            )
        )

        planning_prompt = self._prompt_builder.build(request=request)
        self._notify(progress, "Executando geração de plano estruturado...")
        checks.append(
            self._check_generation(
                name="Geração estruturada",
                prompt=planning_prompt,
                expect_json=True,
            )
        )

        checks.append(self._prompt_check(planning_prompt))
        return self._report(checks)

    def _check_server(self) -> DiagnosticCheck:
        started_at = perf_counter()
        info = self._ollama_service.get_info()
        duration = perf_counter() - started_at

        if not info.available:
            return DiagnosticCheck(
                name="Servidor Ollama",
                status=DiagnosticStatus.FAILED,
                message="O servidor Ollama não respondeu.",
                duration_seconds=duration,
                details={"url": self._config.ollama_base_url},
            )

        return DiagnosticCheck(
            name="Servidor Ollama",
            status=DiagnosticStatus.PASSED,
            message="Servidor online.",
            duration_seconds=duration,
            details={
                "url": self._config.ollama_base_url,
                "version": info.version or "desconhecida",
                "models": str(len(info.models)),
            },
        )

    def _check_model(self) -> DiagnosticCheck:
        info = self._ollama_service.get_info()
        if self._config.ollama_model not in info.models:
            return DiagnosticCheck(
                name="Modelo configurado",
                status=DiagnosticStatus.FAILED,
                message="O modelo configurado não está instalado.",
                details={
                    "configured": self._config.ollama_model,
                    "installed": ", ".join(info.models) or "nenhum",
                },
            )

        return DiagnosticCheck(
            name="Modelo configurado",
            status=DiagnosticStatus.PASSED,
            message="Modelo instalado e disponível.",
            details={"model": self._config.ollama_model},
        )

    def _check_generation(
        self,
        *,
        name: str,
        prompt: str,
        expect_json: bool,
    ) -> DiagnosticCheck:
        started_at = perf_counter()
        try:
            content = self._ollama_service.generate(
                prompt=prompt,
                model=self._config.ollama_model,
            )
        except (RuntimeError, ValueError) as error:
            duration = perf_counter() - started_at
            return DiagnosticCheck(
                name=name,
                status=DiagnosticStatus.FAILED,
                message=str(error),
                duration_seconds=duration,
                details=self._prompt_details(prompt),
            )

        duration = perf_counter() - started_at
        details = self._prompt_details(prompt)
        details["response_characters"] = str(len(content))
        details["response_preview"] = self._preview(content)

        if expect_json:
            try:
                parsed = json.loads(self._extract_json(content))
            except (json.JSONDecodeError, ValueError) as error:
                details["json_error"] = str(error)
                return DiagnosticCheck(
                    name=name,
                    status=DiagnosticStatus.WARNING,
                    message="O modelo respondeu, mas não produziu JSON válido.",
                    duration_seconds=duration,
                    details=details,
                )

            required_fields = {"goal", "estimated_seconds", "risk", "steps"}
            missing_fields = required_fields.difference(parsed)
            if missing_fields:
                details["missing_fields"] = ", ".join(sorted(missing_fields))
                return DiagnosticCheck(
                    name=name,
                    status=DiagnosticStatus.WARNING,
                    message="O JSON não contém todos os campos obrigatórios.",
                    duration_seconds=duration,
                    details=details,
                )

        return DiagnosticCheck(
            name=name,
            status=DiagnosticStatus.PASSED,
            message="Resposta recebida com sucesso.",
            duration_seconds=duration,
            details=details,
        )

    def _prompt_check(self, prompt: str) -> DiagnosticCheck:
        status = DiagnosticStatus.PASSED
        message = "O prompt está dentro do limite recomendado."
        if len(prompt) > 12_000:
            status = DiagnosticStatus.WARNING
            message = "O prompt é grande e pode degradar modelos locais em CPU."

        return DiagnosticCheck(
            name="Tamanho do prompt",
            status=status,
            message=message,
            details=self._prompt_details(prompt),
        )

    def _report(self, checks: list[DiagnosticCheck]) -> AIDiagnosticReport:
        return AIDiagnosticReport(
            provider=self._config.ai_provider,
            model=self._config.ollama_model,
            checks=tuple(checks),
        )

    @staticmethod
    def _extract_json(content: str) -> str:
        stripped = content.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            stripped = "\n".join(lines).strip()

        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end < start:
            raise ValueError("Nenhum objeto JSON foi encontrado na resposta.")
        return stripped[start : end + 1]

    @staticmethod
    def _prompt_details(prompt: str) -> dict[str, str]:
        return {
            "prompt_characters": str(len(prompt)),
            "prompt_lines": str(len(prompt.splitlines())),
            "prompt_preview": AIDiagnosticsService._preview(prompt),
        }

    @staticmethod
    def _preview(value: str, limit: int = 240) -> str:
        normalized = " ".join(value.split())
        if len(normalized) <= limit:
            return normalized
        return normalized[: limit - 3] + "..."

    @staticmethod
    def _notify(callback: ProgressCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)
