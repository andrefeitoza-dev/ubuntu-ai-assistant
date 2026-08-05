from __future__ import annotations

from ubuntu_ai.benchmark.models import BenchmarkRecord


class BenchmarkRecorder:
    """Armazena medições durante a execução."""

    def __init__(self) -> None:
        self._records: list[BenchmarkRecord] = []

    def record(self, record: BenchmarkRecord) -> None:
        self._records.append(record)

    @property
    def records(self) -> tuple[BenchmarkRecord, ...]:
        return tuple(self._records)

    def clear(self) -> None:
        self._records.clear()
