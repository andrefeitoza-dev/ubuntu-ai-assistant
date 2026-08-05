from __future__ import annotations

from collections import defaultdict

from ubuntu_ai.benchmark.models import BenchmarkRecord


class BenchmarkReport:
    """Gera estatísticas agregadas de benchmark."""

    def __init__(self, records: tuple[BenchmarkRecord, ...]) -> None:
        self._records = records

    @property
    def records(self) -> tuple[BenchmarkRecord, ...]:
        return self._records

    @property
    def total_duration(self) -> float:
        return sum(record.duration for record in self._records)

    @property
    def operations(self) -> int:
        return len(self._records)

    @property
    def successful_operations(self) -> int:
        return sum(record.success for record in self._records)

    @property
    def failed_operations(self) -> int:
        return self.operations - self.successful_operations

    @property
    def average_duration(self) -> float:
        if not self._records:
            return 0.0
        return self.total_duration / self.operations

    def duration_by_operation(self) -> dict[str, float]:
        totals: defaultdict[str, float] = defaultdict(float)
        for record in self._records:
            totals[record.operation] += record.duration
        return dict(totals)
