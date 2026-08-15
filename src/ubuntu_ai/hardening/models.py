from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True, slots=True)
class ComponentHealth:
    name: str
    status: HealthStatus
    message: str = ""


@dataclass(frozen=True, slots=True)
class HealthReport:
    status: HealthStatus
    components: tuple[ComponentHealth, ...]

    @property
    def ready(self) -> bool:
        return self.status is not HealthStatus.UNHEALTHY


@dataclass(frozen=True, slots=True)
class OperationMetric:
    operation: str
    calls: int
    failures: int
    total_duration: float

    @property
    def average_duration(self) -> float:
        if self.calls == 0:
            return 0.0
        return self.total_duration / self.calls


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    metrics: tuple[OperationMetric, ...]

    @property
    def total_calls(self) -> int:
        return sum(metric.calls for metric in self.metrics)

    @property
    def total_failures(self) -> int:
        return sum(metric.failures for metric in self.metrics)
