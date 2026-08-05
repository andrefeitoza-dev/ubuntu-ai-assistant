from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BenchmarkRecord:
    """Representa uma medição de desempenho."""

    operation: str
    duration: float
    success: bool = True
