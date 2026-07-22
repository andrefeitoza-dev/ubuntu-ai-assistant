from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.execution.models import (
    ExecutionResult,
    ExecutionStatus,
)


@dataclass(slots=True, frozen=True)
class ExecutionStatistics:
    """Estatísticas consolidadas de uma execução."""

    total: int
    approved: int
    blocked: int
    executed: int
    failed: int
    total_duration: float


@dataclass(slots=True, frozen=True)
class ExecutionReport:
    """Relatório consolidado dos resultados de execução."""

    results: tuple[ExecutionResult, ...]
    statistics: ExecutionStatistics

    @classmethod
    def from_results(
        cls,
        results: tuple[ExecutionResult, ...],
    ) -> ExecutionReport:
        """Cria um relatório a partir dos resultados recebidos."""

        statistics = ExecutionStatistics(
            total=len(results),
            approved=cls._count_status(
                results,
                ExecutionStatus.APPROVED,
            ),
            blocked=cls._count_status(
                results,
                ExecutionStatus.BLOCKED,
            ),
            executed=cls._count_status(
                results,
                ExecutionStatus.EXECUTED,
            ),
            failed=cls._count_status(
                results,
                ExecutionStatus.FAILED,
            ),
            total_duration=sum(
                result.duration or 0.0
                for result in results
            ),
        )

        return cls(
            results=results,
            statistics=statistics,
        )

    @property
    def successful(self) -> bool:
        """Indica se o relatório não contém falhas ou bloqueios."""

        return (
            self.statistics.failed == 0
            and self.statistics.blocked == 0
        )

    @staticmethod
    def _count_status(
        results: tuple[ExecutionResult, ...],
        status: ExecutionStatus,
    ) -> int:
        """Conta resultados correspondentes ao status informado."""

        return sum(
            result.status is status
            for result in results
        )