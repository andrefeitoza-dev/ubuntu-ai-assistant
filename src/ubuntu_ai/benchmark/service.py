from __future__ import annotations

from ubuntu_ai.benchmark.models import BenchmarkRecord
from ubuntu_ai.benchmark.recorder import BenchmarkRecorder
from ubuntu_ai.benchmark.report import BenchmarkReport
from ubuntu_ai.benchmark.timer import BenchmarkTimer


class BenchmarkService:
    """Serviço central de medição de desempenho."""

    def __init__(self, recorder: BenchmarkRecorder | None = None) -> None:
        self._recorder = recorder or BenchmarkRecorder()

    def record(self, operation: str, duration: float, success: bool = True) -> None:
        self._recorder.record(BenchmarkRecord(operation, duration, success))

    def measure(self, operation: str) -> BenchmarkTimer:
        return BenchmarkTimer(operation, self._recorder)

    def report(self) -> BenchmarkReport:
        return BenchmarkReport(self._recorder.records)

    def clear(self) -> None:
        self._recorder.clear()
