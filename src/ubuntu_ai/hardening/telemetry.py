from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from time import perf_counter

from ubuntu_ai.hardening.models import OperationMetric, TelemetrySnapshot


@dataclass(slots=True)
class _MutableMetric:
    calls: int = 0
    failures: int = 0
    total_duration: float = 0.0


class RuntimeTelemetry:
    """Coleta métricas leves sem backend externo."""

    def __init__(self) -> None:
        self._metrics: dict[str, _MutableMetric] = defaultdict(_MutableMetric)
        self._lock = Lock()

    @contextmanager
    def measure(self, operation: str) -> Iterator[None]:
        normalized = operation.strip()
        if not normalized:
            raise ValueError("O nome da operação não pode estar vazio.")

        started_at = perf_counter()
        failed = False
        try:
            yield
        except Exception:
            failed = True
            raise
        finally:
            duration = perf_counter() - started_at
            with self._lock:
                metric = self._metrics[normalized]
                metric.calls += 1
                metric.total_duration += duration
                if failed:
                    metric.failures += 1

    def snapshot(self) -> TelemetrySnapshot:
        with self._lock:
            metrics = tuple(
                OperationMetric(
                    operation=name,
                    calls=value.calls,
                    failures=value.failures,
                    total_duration=value.total_duration,
                )
                for name, value in sorted(self._metrics.items())
            )
        return TelemetrySnapshot(metrics=metrics)

    def reset(self) -> None:
        with self._lock:
            self._metrics.clear()
