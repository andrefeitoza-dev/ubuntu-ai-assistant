from __future__ import annotations

from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.execution.policy import ExecutionPolicy
from ubuntu_ai.execution.system_executor import SystemExecutor


class ControlledExecutor:
    """Aplica políticas de segurança antes de autorizar uma execução."""

    def __init__(
        self,
        policy: ExecutionPolicy,
        system_executor: SystemExecutor | None = None,
    ) -> None:
        self._policy = policy
        self._system_executor = system_executor

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Avalia a solicitação e executa somente quando permitido."""

        decision = self._policy.evaluate(request)

        if not decision.allowed:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                message=decision.reason,
                command=request.command,
            )

        if self._system_executor is None:
            return ExecutionResult(
                status=ExecutionStatus.APPROVED,
                message=decision.reason,
                command=request.command,
            )

        return self._system_executor.execute(request)