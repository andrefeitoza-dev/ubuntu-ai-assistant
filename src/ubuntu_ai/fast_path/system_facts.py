from __future__ import annotations

import platform
import re
import unicodedata
from dataclasses import dataclass

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
    ) -> None:
        self._operating_system = operating_system or OperatingSystemDetector()
        self._kernel = kernel or KernelDetector()
        self._hostname = hostname or HostnameDetector()
        self._cpu = cpu or CpuDetector()
        self._memory = memory or MemoryDetector()
        self._health = health or SystemHealthService()

    def respond(self, normalized: str) -> str | None:
        topic = self._topic(normalized)
        if topic is None:
            return None

        facts = self._collect()
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
        return self._summary(facts)

    @classmethod
    def matches(cls, request: str) -> bool:
        """Indica se a frase solicita um fato do computador selecionado."""

        value = unicodedata.normalize("NFKD", request)
        value = value.encode("ascii", "ignore").decode().lower()
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        return cls._topic(" ".join(value.split())) is not None

    def _collect(self) -> SystemFacts:
        return SystemFacts(
            operating_system=self._operating_system.detect(),
            kernel=self._kernel.detect(),
            architecture=platform.machine() or "arquitetura desconhecida",
            hostname=self._hostname.detect(),
            cpu=self._cpu.detect(),
            memory_mb=self._memory.detect(),
            health=self._health.snapshot(),
        )

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
        if "quantos processos" in request:
            return "processes"
        if "quantas interfaces" in request and "rede" in request:
            return "network"
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
        return "\n".join(lines)
