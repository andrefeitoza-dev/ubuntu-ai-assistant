from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkRecord:
    """Representa uma medição de desempenho."""

    operation: str
    duration: float
    success: bool = True

    def __post_init__(self) -> None:
        if not self.operation.strip():
            raise ValueError("A operação do benchmark não pode estar vazia.")
        if self.duration < 0:
            raise ValueError("A duração do benchmark não pode ser negativa.")
