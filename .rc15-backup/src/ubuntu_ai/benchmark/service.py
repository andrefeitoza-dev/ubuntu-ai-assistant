from __future__ import annotations

from ubuntu_ai.benchmark.models import BenchmarkRecord
from ubuntu_ai.benchmark.recorder import BenchmarkRecorder
from ubuntu_ai.benchmark.report import BenchmarkReport


class BenchmarkService:
    """Serviço responsável pelas medições de desempenho."""

    def __init__(
        self,
        recorder: BenchmarkRecorder | None = None,
    ) -> None:
        self._recorder = recorder or BenchmarkRecorder()

    def record(
        self,
        operation: str,
        duration: float,
        success: bool = True,
    ) -> None:
        self._recorder.record(
            BenchmarkRecord(
                operation=operation,
                duration=duration,
                success=success,
            )
        )

    def report(self) -> BenchmarkReport:
        return BenchmarkReport(self._recorder.records)

    def clear(self) -> None:
        self._recorder.clear()