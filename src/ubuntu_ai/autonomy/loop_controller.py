from __future__ import annotations

from ubuntu_ai.autonomy.goal import GoalStatus
from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.models import AutonomousCycleResult
from ubuntu_ai.autonomy.retry_policy import RetryPolicy
from ubuntu_ai.autonomy.self_healing import SelfHealingAdvisor
from ubuntu_ai.runtime_integration.models import RuntimeRequest
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime


class AutonomousLoopController:
    """Executa ciclos controlados até conclusão, bloqueio ou falha."""

    def __init__(
        self,
        *,
        runtime: MultiAgentRuntime,
        goal_manager: GoalManager,
        retry_policy: RetryPolicy | None = None,
        healing_advisor: SelfHealingAdvisor | None = None,
    ) -> None:
        self._runtime = runtime
        self._goal_manager = goal_manager
        self._retry_policy = retry_policy or RetryPolicy()
        self._healing_advisor = healing_advisor or SelfHealingAdvisor()

    def run_once(
        self,
        goal_id: str,
        *,
        session_id: str,
        execute: bool = True,
        execution_action=None,
    ) -> AutonomousCycleResult:
        goal = self._goal_manager.get(goal_id)
        goal = goal.with_status(GoalStatus.RUNNING).increment_attempts()
        self._goal_manager.update(goal)

        runtime_result = self._runtime.run(
            RuntimeRequest(
                request=goal.description,
                session_id=session_id,
                execute=execute,
            ),
            execution_action=execution_action,
        )

        reflection = runtime_result.reflection

        if reflection is None:
            completed = not execute
            updated = goal.with_status(
                GoalStatus.COMPLETED if completed else GoalStatus.BLOCKED
            ).with_progress(1.0 if completed else goal.progress)
            self._goal_manager.update(updated)

            return AutonomousCycleResult(
                goal=updated,
                runtime_result=runtime_result,
                completed=completed,
                retry_scheduled=False,
                reason=(
                    "Planejamento concluído." if completed else "Execução sem reflexão disponível."
                ),
            )

        if not reflection.failure.failed:
            updated = goal.with_status(GoalStatus.COMPLETED).with_progress(1.0)
            self._goal_manager.update(updated)

            return AutonomousCycleResult(
                goal=updated,
                runtime_result=runtime_result,
                completed=True,
                retry_scheduled=False,
                reason="Objetivo concluído com sucesso.",
            )

        retry = self._retry_policy.evaluate(goal, reflection)

        if retry.retry:
            healing = self._healing_advisor.advise(reflection)
            updated = goal.with_status(GoalStatus.BLOCKED)
            self._goal_manager.update(updated)

            return AutonomousCycleResult(
                goal=updated,
                runtime_result=runtime_result,
                completed=False,
                retry_scheduled=healing.safe_to_automate,
                reason=healing.reason,
            )

        updated = goal.with_status(GoalStatus.FAILED)
        self._goal_manager.update(updated)

        return AutonomousCycleResult(
            goal=updated,
            runtime_result=runtime_result,
            completed=False,
            retry_scheduled=False,
            reason=retry.reason,
        )

    def run_until_done(
        self,
        goal_id: str,
        *,
        session_id: str,
        execute: bool = True,
        execution_action=None,
    ) -> AutonomousCycleResult:
        """Executa tentativas controladas até conclusão ou interrupção segura."""

        while True:
            result = self.run_once(
                goal_id,
                session_id=session_id,
                execute=execute,
                execution_action=execution_action,
            )

            if result.completed:
                return result

            if not result.retry_scheduled:
                return result

            goal = self._goal_manager.get(goal_id)

            if goal.attempts >= goal.max_attempts:
                failed = goal.with_status(GoalStatus.FAILED)
                self._goal_manager.update(failed)

                return AutonomousCycleResult(
                    goal=failed,
                    runtime_result=result.runtime_result,
                    completed=False,
                    retry_scheduled=False,
                    reason="Limite de tentativas atingido.",
                )
