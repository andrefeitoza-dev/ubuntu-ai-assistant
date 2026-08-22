from __future__ import annotations

from dataclasses import dataclass, replace

from ubuntu_ai.agents.models import AgentKind
from ubuntu_ai.agents.orchestration import (
    OrchestrationGoal,
    OrchestrationResult,
    OrchestrationStatus,
    OrchestrationTask,
)
from ubuntu_ai.reflection.failure import FailureAnalysis, FailureClassifier
from ubuntu_ai.reflection.recovery import RecoveryAction, RecoveryPlan, RecoveryPlanner


@dataclass(frozen=True, slots=True)
class ReplanningDecision:
    task_id: str
    specialist: AgentKind
    failure: FailureAnalysis
    recovery: RecoveryPlan
    justification: str
    alternative: OrchestrationTask | None = None


@dataclass(frozen=True, slots=True)
class ReplanningReport:
    goal_id: str
    completed_task_ids: tuple[str, ...]
    decisions: tuple[ReplanningDecision, ...]
    recovery_goal: OrchestrationGoal | None

    @property
    def requires_review(self) -> bool:
        return any(
            decision.recovery.requires_confirmation or decision.alternative is None
            for decision in self.decisions
        )


class OrchestrationReplanner:
    """Analisa resultados parciais sem ampliar o escopo do objetivo original."""

    def __init__(
        self,
        classifier: FailureClassifier | None = None,
        recovery_planner: RecoveryPlanner | None = None,
    ) -> None:
        self._classifier = classifier or FailureClassifier()
        self._recovery_planner = recovery_planner or RecoveryPlanner()

    def analyze(
        self,
        goal: OrchestrationGoal,
        result: OrchestrationResult,
    ) -> ReplanningReport:
        if result.goal_id != goal.goal_id:
            raise ValueError("O resultado não pertence ao objetivo informado.")

        original = {task.task_id: task for task in goal.tasks}
        result_ids = [item.task_id for item in result.tasks]
        if len(result_ids) != len(set(result_ids)):
            raise ValueError("O resultado contém tarefas duplicadas.")
        unknown = {item.task_id for item in result.tasks} - original.keys()
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"O resultado contém tarefas fora do objetivo: {names}.")
        mismatched = [
            item.task_id
            for item in result.tasks
            if item.specialist is not original[item.task_id].specialist
        ]
        if mismatched:
            names = ", ".join(sorted(mismatched))
            raise ValueError(f"Especialista divergente no resultado: {names}.")

        completed = tuple(
            item.task_id for item in result.tasks if item.status is OrchestrationStatus.COMPLETED
        )
        decisions: list[ReplanningDecision] = []
        alternatives: list[OrchestrationTask] = []

        for item in result.tasks:
            if item.status is not OrchestrationStatus.FAILED:
                continue
            task = original[item.task_id]
            failure = self._classifier.classify(
                success=False,
                message=item.reason,
            )
            recovery = self._recovery_planner.build(failure)
            alternative = self._safe_alternative(task, recovery)
            justification = self._justification(failure, recovery, alternative)
            decisions.append(
                ReplanningDecision(
                    task_id=item.task_id,
                    specialist=item.specialist,
                    failure=failure,
                    recovery=recovery,
                    justification=justification,
                    alternative=alternative,
                )
            )
            if alternative is not None:
                alternatives.append(alternative)

        recovery_goal = self._recovery_goal(goal, alternatives)
        return ReplanningReport(
            goal_id=goal.goal_id,
            completed_task_ids=completed,
            decisions=tuple(decisions),
            recovery_goal=recovery_goal,
        )

    @staticmethod
    def _safe_alternative(
        task: OrchestrationTask,
        recovery: RecoveryPlan,
    ) -> OrchestrationTask | None:
        if not recovery.retry_allowed or RecoveryAction.RETRY not in recovery.actions:
            return None
        payload = task.payload
        if payload.attempt >= 3:
            return None
        next_attempt = payload.attempt + 1
        return replace(
            task,
            task_id=f"{task.task_id}-retry-{next_attempt}",
            payload=replace(payload, attempt=next_attempt),
            dependencies=(),
        )

    @staticmethod
    def _recovery_goal(
        goal: OrchestrationGoal,
        alternatives: list[OrchestrationTask],
    ) -> OrchestrationGoal | None:
        if not alternatives:
            return None
        context_keys = set().union(*(task.context_keys for task in alternatives))
        context = {key: goal.context[key] for key in sorted(context_keys)}
        return OrchestrationGoal(
            goal_id=f"{goal.goal_id}-recovery",
            description=f"Recuperação segura: {goal.description}",
            tasks=tuple(alternatives),
            context=context,
        )

    @staticmethod
    def _justification(
        failure: FailureAnalysis,
        recovery: RecoveryPlan,
        alternative: OrchestrationTask | None,
    ) -> str:
        if alternative is not None:
            return (
                f"Nova tentativa limitada autorizada para falha {failure.kind.value}; "
                "especialista, ações, destino e contexto foram preservados."
            )
        guidance = recovery.guidance[0] if recovery.guidance else "Revisão manual necessária."
        return f"Replanejamento automático bloqueado: {guidance}"
