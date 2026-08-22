from __future__ import annotations

import platform
import re
import subprocess
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

import psutil

from ubuntu_ai.context.discovery import (
    CpuDetector,
    HostnameDetector,
    KernelDetector,
    MemoryDetector,
    OperatingSystemDetector,
)
from ubuntu_ai.context.health import SystemHealthService, SystemHealthSnapshot


@dataclass(frozen=True, slots=True)
class SystemFacts:
    operating_system: str
    kernel: str
    architecture: str
    hostname: str
    cpu: str
    memory_mb: int | None
    health: SystemHealthSnapshot
    battery_percent: float | None
    failed_services: int | None


class SystemFactResponder:
    """Responde consultas factuais locais sem shell, sudo ou Ollama."""

    def __init__(
        self,
        *,
        operating_system: OperatingSystemDetector | None = None,
        kernel: KernelDetector | None = None,
        hostname: HostnameDetector | None = None,
        cpu: CpuDetector | None = None,
        memory: MemoryDetector | None = None,
        health: SystemHealthService | None = None,
        battery_provider: Callable[[], float | None] | None = None,
        failed_services_provider: Callable[[], int | None] | None = None,
    ) -> None:
        self._operating_system = operating_system or OperatingSystemDetector()
        self._kernel = kernel or KernelDetector()
        self._hostname = hostname or HostnameDetector()
        self._cpu = cpu or CpuDetector()
        self._memory = memory or MemoryDetector()
        self._health = health or SystemHealthService()
        self._battery_provider = battery_provider or self._battery_percent
        self._failed_services_provider = failed_services_provider or self._failed_services

    def respond(self, request: str) -> str | None:
        topic = self.topic_for(request)
        if topic is None:
            return None

        facts = self._collect(topic)
        if topic == "operating_system":
            return f"Sistema deste computador: {facts.operating_system}."
        if topic == "kernel":
            return f"Kernel deste computador: {facts.kernel} ({facts.architecture})."
        if topic == "hostname":
            return f"Nome deste computador: {facts.hostname}."
        if topic == "cpu":
            return f"Processador deste computador: {facts.cpu}."
        if topic == "memory":
            if facts.memory_mb is None:
                return "Não foi possível consultar a memória total deste computador."
            total_gib = facts.memory_mb / 1024
            metrics = facts.health.metrics
            available = (
                f" · {metrics.memory_available_mb / 1024:.1f} GiB disponíveis"
                if metrics is not None
                else ""
            )
            return f"Memória RAM: {total_gib:.1f} GiB no total{available}."
        if topic == "disk":
            metrics = facts.health.metrics
            if metrics is None:
                return "Não foi possível consultar o armazenamento deste computador."
            return (
                f"Disco pessoal: {metrics.disk_percent:.1f}% usado · "
                f"{metrics.disk_free_gb:.1f} GiB livres."
            )
        if topic == "processes":
            metrics = facts.health.metrics
            if metrics is None:
                return "Não foi possível consultar os processos deste computador."
            return f"Existem {metrics.process_count} processos em execução."
        if topic == "network":
            metrics = facts.health.metrics
            if metrics is None:
                return "Não foi possível consultar a rede deste computador."
            return (
                "Interfaces de rede ativas, sem contar loopback: "
                f"{metrics.active_network_interfaces}."
            )
        if topic == "battery":
            if facts.battery_percent is None:
                return "Este computador não informou uma bateria disponível."
            return f"Bateria deste computador: {facts.battery_percent:.0f}%."
        if topic == "services":
            if facts.failed_services is None:
                return "Não foi possível consultar os serviços deste computador."
            if facts.failed_services == 0:
                return "Não existem serviços do sistema em estado de falha."
            return f"Serviços em estado de falha: {facts.failed_services}."
        return self._summary(facts)

    @classmethod
    def matches(cls, request: str) -> bool:
        """Indica se a frase solicita um fato do computador selecionado."""

        return cls.topic_for(request) is not None

    @classmethod
    def topic_for(cls, request: str) -> str | None:
        """Retorna o assunto factual sem consultar a máquina."""

        return cls._topic(cls._normalize(request))

    def _collect(self, topic: str) -> SystemFacts:
        return SystemFacts(
            operating_system=self._operating_system.detect(),
            kernel=self._kernel.detect(),
            architecture=platform.machine() or "arquitetura desconhecida",
            hostname=self._hostname.detect(),
            cpu=self._cpu.detect(),
            memory_mb=self._memory.detect(),
            health=self._health.snapshot(),
            battery_percent=(
                self._safe_optional(self._battery_provider)
                if topic in {"battery", "summary"}
                else None
            ),
            failed_services=(
                self._safe_optional(self._failed_services_provider)
                if topic in {"services", "summary"}
                else None
            ),
        )

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return " ".join(normalized.split())

    @staticmethod
    def _safe_optional(provider: Callable[[], float | int | None]):
        try:
            return provider()
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError):
            return None

    @staticmethod
    def _battery_percent() -> float | None:
        battery = psutil.sensors_battery()
        return None if battery is None else battery.percent

    @staticmethod
    def _failed_services() -> int | None:
        result = subprocess.run(
            ("systemctl", "--failed", "--no-legend", "--plain"),
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
            shell=False,
        )
        if result.returncode not in {0, 1}:
            return None
        return sum(bool(line.strip()) for line in result.stdout.splitlines())

    @staticmethod
    def _topic(request: str) -> str | None:
        if request.startswith(("o que e ", "explique ", "como funciona ")):
            return None

        if any(
            phrase in request
            for phrase in (
                "resumo deste computador",
                "resumo do computador",
                "informacoes deste computador",
                "informacoes do computador",
                "configuracao deste computador",
                "configuracao do computador",
            )
        ):
            return "summary"
        if "versao" in request and ("ubuntu" in request or "sistema operacional" in request):
            return "operating_system"
        if "qual" in request and "sistema operacional" in request:
            return "operating_system"
        if "kernel" in request and request.startswith(("qual", "mostre", "informe")):
            return "kernel"
        if "hostname" in request or "nome deste computador" in request:
            return "hostname"
        if any(word in request for word in ("cpu", "processador")) and request.startswith(
            ("qual", "mostre", "informe")
        ):
            return "cpu"
        if any(word in request for word in ("memoria", "ram")) and (
            request.startswith(("qual", "quanto", "mostre", "informe")) or "tenho" in request
        ):
            return "memory"
        if any(word in request for word in ("disco", "armazenamento", "espaco livre")) and (
            request.startswith(("qual", "quanto", "informe"))
            or "espaco" in request
            or "livre" in request
            or "disponivel" in request
        ):
            return "disk"
        if any(
            phrase in request
            for phrase in (
                "quantos processos",
                "processos em execucao",
                "processos ativos",
            )
        ):
            return "processes"
        if "rede" in request and any(
            phrase in request
            for phrase in (
                "quantas interfaces",
                "interfaces ativas",
                "estado da rede",
                "informacoes da rede",
            )
        ):
            return "network"
        if "bateria" in request and any(
            word in request for word in ("quanto", "qual", "nivel", "estado", "mostre")
        ):
            return "battery"
        if "servicos" in request and any(
            word in request for word in ("falha", "falhando", "estado", "mostre", "existem")
        ):
            return "services"
        return None

    @staticmethod
    def _summary(facts: SystemFacts) -> str:
        lines = [
            "Computador: local",
            f"Sistema: {facts.operating_system}",
            f"Kernel: {facts.kernel}",
            f"Arquitetura: {facts.architecture}",
            f"Hostname: {facts.hostname}",
            f"CPU: {facts.cpu}",
        ]
        if facts.memory_mb is not None:
            lines.append(f"Memória: {facts.memory_mb / 1024:.1f} GiB")
        if facts.health.metrics is not None:
            metrics = facts.health.metrics
            lines.extend(
                (
                    f"Disco livre: {metrics.disk_free_gb:.1f} GiB",
                    f"Processos: {metrics.process_count}",
                    f"Interfaces de rede ativas: {metrics.active_network_interfaces}",
                )
            )
        if facts.battery_percent is not None:
            lines.append(f"Bateria: {facts.battery_percent:.0f}%")
        if facts.failed_services is not None:
            lines.append(f"Serviços em falha: {facts.failed_services}")
        return "\n".join(lines)
