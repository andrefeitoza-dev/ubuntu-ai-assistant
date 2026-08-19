from __future__ import annotations

from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.long_tasks import LongTaskManager
from ubuntu_ai.autonomy.loop_controller import AutonomousLoopController
from ubuntu_ai.autonomy.observability import AutomationTelemetry
from ubuntu_ai.autonomy.persistence import SQLiteAutomationRepository
from ubuntu_ai.autonomy.runtime import AutonomousRuntime
from ubuntu_ai.autonomy.scheduler import LocalAutomationScheduler
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime


def build_autonomous_runtime(
    runtime: MultiAgentRuntime,
) -> AutonomousRuntime:
    goal_manager = GoalManager()
    repository = SQLiteAutomationRepository()
    telemetry = AutomationTelemetry()
    long_tasks = LongTaskManager()
    repository.recover_interrupted()
    long_tasks.restore(repository.list_tasks())
    for task in long_tasks.all():
        telemetry.observe(task)
    long_tasks.subscribe(repository.save)
    long_tasks.subscribe(telemetry.observe)
    scheduler = LocalAutomationScheduler()
    for item in repository.list_schedules():
        scheduler.schedule(item)
    controller = AutonomousLoopController(
        runtime=runtime,
        goal_manager=goal_manager,
    )
    return AutonomousRuntime(
        controller=controller,
        goal_manager=goal_manager,
        long_tasks=long_tasks,
        scheduler=scheduler,
        telemetry=telemetry,
    )
