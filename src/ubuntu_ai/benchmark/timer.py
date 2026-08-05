from __future__ import annotations

from time import perf_counter
from types import TracebackType

from ubuntu_ai.benchmark.models import BenchmarkRecord
from ubuntu_ai.benchmark.recorder import BenchmarkRecorder


class BenchmarkTimer:
    """Mede uma operação e registra seu resultado automaticamente."""

    def __init__(self, operation: str, recorder: BenchmarkRecorder) -> None:
        if not operation.strip():
            raise ValueError("A operação do benchmark não pode estar vazia.")
        self._operation = operation.strip()
        self._recorder = recorder
        self._started_at: float | None = None

    def __enter__(self) -> BenchmarkTimer:
        self._started_at = perf_counter()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if self._started_at is None:
            raise RuntimeError("O timer de benchmark não foi iniciado.")
        self._recorder.record(
            BenchmarkRecord(
                operation=self._operation,
                duration=perf_counter() - self._started_at,
                success=exception_type is None,
            )
        )
        return False
