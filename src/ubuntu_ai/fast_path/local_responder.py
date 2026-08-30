"""Respostas locais instantâneas que não precisam de um modelo de linguagem."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from ubuntu_ai.context.health import SystemHealthService
from ubuntu_ai.fast_path.capabilities import CapabilityCatalog
from ubuntu_ai.fast_path.linux_commands import LinuxCommandCatalog
from ubuntu_ai.fast_path.linux_knowledge import LinuxKnowledgeResponder
from ubuntu_ai.fast_path.runtime_status import RuntimeStatusResponder
from ubuntu_ai.fast_path.software import InstalledSoftwareResponder
from ubuntu_ai.fast_path.system_facts import SystemFactResponder


@dataclass(frozen=True, slots=True)
class LocalResponse:
    text: str
    route: str = "local"


class LocalResponder:
    """Resolve consultas simples localmente, sem acionar o Ollama."""

    _WEEKDAYS = (
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    )
    _MONTHS = (
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    )

    _DATE_REQUESTS = {
        "que dia e hoje",
        "qual e o dia de hoje",
        "qual a data de hoje",
        "hoje e que dia",
        "data de hoje",
    }
    _MONTH_REQUESTS = {
        "que mes estamos",
        "qual e o mes atual",
        "qual o mes atual",
        "em que mes estamos",
        "mes atual",
    }
    _YEAR_REQUESTS = {
        "que ano estamos",
        "qual e o ano atual",
        "qual o ano atual",
        "em que ano estamos",
        "ano atual",
    }
    _TIME_REQUESTS = {
        "que horas sao",
        "qual e a hora",
        "qual a hora",
        "hora atual",
        "horario atual",
    }
    _CANCEL_REQUESTS = {
        "cancelar",
        "cancele",
        "cancel",
        "interromper",
    }
    _SLOW_REQUESTS = {
        "por que meu computador esta lento",
        "por que este computador esta lento",
        "por que o computador esta lento",
        "meu computador esta lento",
        "diagnostique a lentidao do meu computador",
    }
    _HEALTH_REQUESTS = {
        "como esta o computador",
        "como esta este computador",
        "saude do computador",
        "estado do computador",
        "estado do sistema",
        "o computador esta sobrecarregado",
        "diagnostico rapido do computador",
    }

    def __init__(
        self,
        now: Callable[[], datetime] | None = None,
        health_service: SystemHealthService | None = None,
        system_facts: SystemFactResponder | None = None,
        commands: LinuxCommandCatalog | None = None,
        capabilities: CapabilityCatalog | None = None,
        software: InstalledSoftwareResponder | None = None,
        runtime_status: RuntimeStatusResponder | None = None,
        linux_knowledge: LinuxKnowledgeResponder | None = None,
    ) -> None:
        self._now = now or datetime.now
        self._health_service = health_service or SystemHealthService()
        self._system_facts = system_facts or SystemFactResponder(health=self._health_service)
        self._commands = commands or LinuxCommandCatalog()
        self._capabilities = capabilities or CapabilityCatalog()
        self._software = software or InstalledSoftwareResponder()
        self._runtime_status = runtime_status or RuntimeStatusResponder()
        self._linux_knowledge = linux_knowledge or LinuxKnowledgeResponder()

    @classmethod
    def _is_date_request(cls, normalized: str) -> bool:
        if normalized in cls._DATE_REQUESTS:
            return True

        words = set(normalized.split())
        current = {"atual", "atuais", "hoje", "agora", "estamos"}
        request = {"mostre", "mostrar", "exiba", "exibir", "informe", "qual", "que"}

        if "data" in words and (words & current or words & request):
            return True

        return {"dia", "mes"} <= words and bool(words & (current | request))

    @classmethod
    def _is_month_request(cls, normalized: str) -> bool:
        if normalized in cls._MONTH_REQUESTS:
            return True

        words = set(normalized.split())
        context = {
            "atual",
            "atuais",
            "hoje",
            "agora",
            "estamos",
            "mostre",
            "mostrar",
            "informe",
            "qual",
            "que",
        }
        return "mes" in words and bool(words & context)

    @classmethod
    def _is_year_request(cls, normalized: str) -> bool:
        if normalized in cls._YEAR_REQUESTS:
            return True

        words = set(normalized.split())
        context = {
            "atual",
            "atuais",
            "hoje",
            "agora",
            "estamos",
            "mostre",
            "mostrar",
            "informe",
            "qual",
            "que",
        }
        return "ano" in words and bool(words & context)

    @classmethod
    def _is_time_request(cls, normalized: str) -> bool:
        if normalized in cls._TIME_REQUESTS:
            return True

        words = set(normalized.split())
        context = {
            "atual",
            "atuais",
            "agora",
            "mostre",
            "mostrar",
            "informe",
            "qual",
            "que",
        }
        return bool(words & {"hora", "horas", "horario"}) and bool(words & context)

    def respond(self, request: str) -> LocalResponse | None:
        normalized = self._normalize(request)

        if self._is_date_request(normalized):
            current = self._now()
            weekday = self._WEEKDAYS[current.weekday()]
            month = self._MONTHS[current.month - 1]
            return LocalResponse(f"Hoje é {weekday}, {current.day} de {month} de {current.year}.")

        if self._is_month_request(normalized):
            current = self._now()
            month = self._MONTHS[current.month - 1]
            return LocalResponse(f"Estamos em {month} de {current.year}.")

        if self._is_year_request(normalized):
            current = self._now()
            return LocalResponse(f"Estamos em {current.year}.")

        if self._is_time_request(normalized):
            current = self._now()
            return LocalResponse(f"Agora são {current:%H:%M}.")

        capability_response = self._capabilities.respond(normalized)
        if capability_response is not None:
            return LocalResponse(capability_response)

        command_response = self._commands.respond(normalized)
        if command_response is not None:
            return LocalResponse(command_response)

        knowledge_response = self._linux_knowledge.respond(normalized)
        if knowledge_response is not None:
            return LocalResponse(knowledge_response)

        software_response = self._software.respond(normalized)
        if software_response is not None:
            return LocalResponse(software_response)

        runtime_response = self._runtime_status.respond(normalized)
        if runtime_response is not None:
            return LocalResponse(runtime_response)

        system_response = self._system_facts.respond(normalized)
        if system_response is not None:
            return LocalResponse(system_response)

        if normalized in self._CANCEL_REQUESTS:
            return LocalResponse("Não há nenhuma operação em andamento para cancelar.")

        if normalized in self._SLOW_REQUESTS:
            return LocalResponse(self._slow_diagnosis())

        if normalized in self._HEALTH_REQUESTS:
            return LocalResponse(self._health_service.snapshot().to_text())

        return None

    def _slow_diagnosis(self) -> str:
        snapshot = self._health_service.snapshot()
        metrics = snapshot.metrics

        if metrics is None:
            return (
                "Não foi possível coletar métricas locais para diagnosticar "
                "a lentidão deste computador."
            )

        findings = []
        if metrics.cpu_percent >= 80:
            findings.append(f"CPU elevada: {metrics.cpu_percent:.1f}%.")
        if metrics.memory_percent >= 80:
            findings.append(f"Memória elevada: {metrics.memory_percent:.1f}%.")
        if metrics.swap_percent >= 50:
            findings.append(f"Swap elevada: {metrics.swap_percent:.1f}%.")
        if metrics.disk_percent >= 90:
            findings.append(f"Disco próximo da capacidade: {metrics.disk_percent:.1f}% usado.")

        if not findings:
            findings.append(
                "As métricas atuais não indicam sobrecarga elevada de CPU, memória, swap ou disco."
            )

        findings.append(f"Processos em execução: {metrics.process_count}.")
        findings.append("Para aprofundar, consulte os processos que mais usam CPU e memória.")

        return "Diagnóstico local de desempenho:\n" + "\n".join(
            f"• {finding}" for finding in findings
        )

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return " ".join(normalized.split())
