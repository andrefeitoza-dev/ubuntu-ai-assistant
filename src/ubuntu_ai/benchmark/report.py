from __future__ import annotations

from ubuntu_ai.benchmark.models import BenchmarkRecord


class BenchmarkReport:
    """Gera estatísticas simples de benchmark."""

    def __init__(
        self,
        records: tuple[BenchmarkRecord, ...],
    ) -> None:
        self._records = records

    @property
    def total_duration(self) -> float:
        return sum(record.duration for record in self._records)

    @property
    def operations(self) -> int:
        return len(self._records)

    @property
    def average_duration(self) -> float:
        if not self._records:
            return 0.0

        return self.total_duration / len(self._records)