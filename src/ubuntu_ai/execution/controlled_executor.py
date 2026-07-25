from __future__ import annotations

from shlex import join

from ubuntu_ai.domain.plan import Plan
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
        """Executa um único comando."""

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

    def execute_plan(
        self,
        plan: Plan,
    ) -> tuple[ExecutionResult, ...]:
        """Executa todas as etapas de um plano."""

        results: list[ExecutionResult] = []

        for step in plan.steps:
            request = ExecutionRequest(
                command=join(step.command),
            )

            result = self.execute(request)

            results.append(result)

            if result.status == ExecutionStatus.BLOCKED:
                break

        return tuple(results)