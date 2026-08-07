from __future__ import annotations

from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.loop_controller import AutonomousLoopController
from ubuntu_ai.autonomy.runtime import AutonomousRuntime
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime


def build_autonomous_runtime(
    runtime: MultiAgentRuntime,
) -> AutonomousRuntime:
    goal_manager = GoalManager()
    controller = AutonomousLoopController(
        runtime=runtime,
        goal_manager=goal_manager,
    )
    return AutonomousRuntime(
        controller=controller,
        goal_manager=goal_manager,
    )
