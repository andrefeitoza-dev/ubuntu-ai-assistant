from __future__ import annotations

from ubuntu_ai.autonomy.goal import Goal
from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.long_tasks import LongTask, LongTaskManager
from ubuntu_ai.autonomy.loop_controller import AutonomousLoopController
from ubuntu_ai.autonomy.models import AutonomousCycleResult


class AutonomousRuntime:
    """Fachada para registrar objetivos e executar ciclos autônomos."""

    def __init__(
        self,
        *,
        controller: AutonomousLoopController,
        goal_manager: GoalManager,
        long_tasks: LongTaskManager | None = None,
    ) -> None:
        self._controller = controller
        self._goal_manager = goal_manager
        self._long_tasks = long_tasks or LongTaskManager()

    @property
    def long_tasks(self) -> LongTaskManager:
        return self._long_tasks

    def register_long_task(self, task: LongTask) -> LongTask:
        return self._long_tasks.register(task)

    def register_goal(self, goal: Goal) -> None:
        self._goal_manager.add(goal)

    def run_once(
        self,
        goal_id: str,
        *,
        session_id: str,
        execute: bool = True,
        execution_action=None,
    ) -> AutonomousCycleResult:
        return self._controller.run_once(
            goal_id,
            session_id=session_id,
            execute=execute,
            execution_action=execution_action,
        )

    def run_until_done(
        self,
        goal_id: str,
        *,
        session_id: str,
        execute: bool = True,
        execution_action=None,
    ) -> AutonomousCycleResult:
        """Executa um objetivo até conclusão ou interrupção segura."""

        return self._controller.run_until_done(
            goal_id,
            session_id=session_id,
            execute=execute,
            execution_action=execution_action,
        )
