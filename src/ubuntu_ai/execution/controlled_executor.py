from __future__ import annotations

from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.execution.policy import ExecutionPolicy


class ControlledExecutor:
    """Executor responsável por aplicar políticas antes da execução."""

    def __init__(
        self,
        policy: ExecutionPolicy,
    ) -> None:
        self._policy = policy

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        decision = self._policy.evaluate(request)

        if not decision.allowed:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                message=decision.reason,
            )

        return ExecutionResult(
            status=ExecutionStatus.APPROVED,
            message=decision.reason,
        )