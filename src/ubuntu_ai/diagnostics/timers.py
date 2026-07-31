from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


@contextmanager
def measure_time(target: list[float]) -> Iterator[None]:
    """Mede uma operação e grava a duração no alvo informado."""

    started_at = perf_counter()
    try:
        yield
    finally:
        target.append(perf_counter() - started_at)
