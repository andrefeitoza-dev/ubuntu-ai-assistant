from __future__ import annotations

from dataclasses import replace
from shlex import join

from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.execution.mode import ExecutionMode, execution_mode
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.execution.permissions import CapabilityPermissions, capability_permissions
from ubuntu_ai.execution.policy import ExecutionPolicy
from ubuntu_ai.execution.system_executor import SystemExecutor


class ControlledExecutor:
    """Aplica políticas de segurança antes de autorizar uma execução."""

    def __init__(
        self,
        policy: ExecutionPolicy,
        system_executor: SystemExecutor | None = None,
        mode: ExecutionMode | None = None,
        permissions: CapabilityPermissions | None = None,
    ) -> None:
        self._policy = policy
        self._system_executor = system_executor
        self._mode = mode or execution_mode
        self._permissions = permissions or capability_permissions

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
                policy_reason=decision.reason,
            )

        permission_reason = self._permissions.denial_reason(request.command)
        if permission_reason is not None:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                message=permission_reason,
                command=request.command,
                policy_reason=permission_reason,
            )

        if self._system_executor is None:
            return ExecutionResult(
                status=ExecutionStatus.APPROVED,
                message=decision.reason,
                command=request.command,
                policy_reason=decision.reason,
            )

        effective_request = replace(request, dry_run=True) if self._mode.simulation else request
        return replace(
            self._system_executor.execute(effective_request),
            policy_reason=decision.reason,
        )

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
