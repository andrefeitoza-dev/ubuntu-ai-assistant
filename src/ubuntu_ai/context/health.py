from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import psutil


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    memory_available_mb: int
    swap_percent: float
    disk_percent: float
    disk_free_gb: float
    active_network_interfaces: int
    process_count: int
    uptime_seconds: int


@dataclass(frozen=True, slots=True)
class SystemHealthSnapshot:
    metrics: SystemMetrics | None
    status: HealthStatus

    def to_prompt(self) -> str:
        if self.metrics is None:
            return "status=unknown"
        value = self.metrics
        return (
            f"status={self.status.value}; cpu_percent={value.cpu_percent:.1f}; "
            f"memory_percent={value.memory_percent:.1f}; "
            f"memory_available_mb={value.memory_available_mb}; "
            f"swap_percent={value.swap_percent:.1f}; "
            f"disk_percent={value.disk_percent:.1f}; "
            f"disk_free_gb={value.disk_free_gb:.1f}; "
            f"active_network_interfaces={value.active_network_interfaces}; "
            f"process_count={value.process_count}; uptime_seconds={value.uptime_seconds}"
        )

    def to_text(self) -> str:
        if self.metrics is None:
            return "Não foi possível obter o estado atual do computador."
        value = self.metrics
        labels = {
            HealthStatus.HEALTHY: "saudável",
            HealthStatus.ATTENTION: "requer atenção",
            HealthStatus.CRITICAL: "está em estado crítico",
            HealthStatus.UNKNOWN: "tem estado desconhecido",
        }
        uptime_hours = value.uptime_seconds / 3600
        return (
            f"O computador {labels[self.status]}.\n"
            f"CPU: {value.cpu_percent:.1f}% · RAM: {value.memory_percent:.1f}% "
            f"({value.memory_available_mb} MiB disponíveis) · "
            f"Swap: {value.swap_percent:.1f}%\n"
            f"Disco pessoal: {value.disk_percent:.1f}% usado "
            f"({value.disk_free_gb:.1f} GiB livres) · "
            f"Processos: {value.process_count} · "
            f"Interfaces de rede ativas: {value.active_network_interfaces} · "
            f"Tempo ligado: {uptime_hours:.1f} h."
        )


class SystemHealthService:
    """Coleta métricas locais sem shell, sudo ou conteúdo de arquivos."""

    def __init__(
        self,
        metrics_provider: Callable[[], SystemMetrics] | None = None,
    ) -> None:
        self._metrics_provider = metrics_provider or self._collect_metrics

    def snapshot(self) -> SystemHealthSnapshot:
        try:
            metrics = self._metrics_provider()
        except (OSError, RuntimeError, ValueError):
            return SystemHealthSnapshot(None, HealthStatus.UNKNOWN)
        return SystemHealthSnapshot(metrics, self._status(metrics))

    @staticmethod
    def _status(metrics: SystemMetrics) -> HealthStatus:
        highest = max(
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.swap_percent,
            metrics.disk_percent,
        )
        if highest >= 95 or metrics.disk_free_gb <= 1:
            return HealthStatus.CRITICAL
        if highest >= 80 or metrics.disk_free_gb <= 5:
            return HealthStatus.ATTENTION
        return HealthStatus.HEALTHY

    @staticmethod
    def _collect_metrics() -> SystemMetrics:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage(str(Path.home()))
        interfaces = psutil.net_if_stats()
        active_interfaces = sum(status.isup and name != "lo" for name, status in interfaces.items())
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=None),
            memory_percent=memory.percent,
            memory_available_mb=memory.available // (1024 * 1024),
            swap_percent=swap.percent,
            disk_percent=disk.percent,
            disk_free_gb=disk.free / (1024**3),
            active_network_interfaces=active_interfaces,
            process_count=len(psutil.pids()),
            uptime_seconds=max(0, int(time.time() - psutil.boot_time())),
        )
