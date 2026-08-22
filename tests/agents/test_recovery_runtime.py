from dataclasses import replace

import pytest

from ubuntu_ai.agents.models import AgentKind
from ubuntu_ai.agents.orchestration import (
    OrchestrationGoal,
    OrchestrationResult,
    OrchestrationStatus,
    OrchestrationTask,
    OrchestrationTaskResult,
)
from ubuntu_ai.agents.recovery_runtime import (
    ApprovedRecoveryMemory,
    OrchestrationRecoveryManager,
    RecoveryTelemetry,
    SQLiteRecoveryRepository,
)
from ubuntu_ai.agents.replanning import ReplanningReport
from ubuntu_ai.agents.specialists import SpecialistAction, SpecialistPayload
from ubuntu_ai.memory_intelligence.models import MemoryCandidate, MemoryKind, MemoryQuery


def goal() -> OrchestrationGoal:
    first = OrchestrationTask(
        "system", AgentKind.SYSTEM, SpecialistPayload("check", (SpecialistAction(("uptime",)),))
    )
    second = OrchestrationTask(
        "network",
        AgentKind.NETWORK,
        SpecialistPayload("check", (SpecialistAction(("ip", "route")),)),
        dependencies=("system",),
        context_keys=frozenset({"target"}),
    )
    return OrchestrationGoal("goal", "check", (first, second), {"target": "local", "secret": "x"})


def test_checkpoint_resumes_only_pending_tasks(tmp_path) -> None:
    original = goal()
    partial = OrchestrationResult(
        "goal",
        OrchestrationStatus.BLOCKED,
        (
            OrchestrationTaskResult("system", AgentKind.SYSTEM, OrchestrationStatus.COMPLETED),
            OrchestrationTaskResult("network", AgentKind.NETWORK, OrchestrationStatus.FAILED),
        ),
        2,
    )
    manager = OrchestrationRecoveryManager(SQLiteRecoveryRepository(tmp_path / "recovery.db"))
    manager.checkpoint(original, partial)

    resumed = manager.resume(original)

    assert [task.task_id for task in resumed.tasks] == ["network"]
    assert resumed.tasks[0].dependencies == ()
    assert dict(resumed.context) == {"target": "local"}


def test_changed_goal_cannot_use_old_checkpoint(tmp_path) -> None:
    original = goal()
    partial = OrchestrationResult("goal", OrchestrationStatus.BLOCKED, (), 2)
    manager = OrchestrationRecoveryManager(SQLiteRecoveryRepository(tmp_path / "recovery.db"))
    manager.checkpoint(original, partial)
    changed = replace(original, tasks=(replace(original.tasks[0], task_id="changed"),))

    with pytest.raises(PermissionError, match="mudou"):
        manager.resume(changed)


def test_unapproved_learning_is_excluded() -> None:
    candidates = (
        MemoryCandidate(MemoryKind.EXECUTION, "execução segura", similarity=0.8),
        MemoryCandidate(MemoryKind.LEARNING, "aprendizado", similarity=1.0, source="auto"),
    )

    selection = ApprovedRecoveryMemory().select(MemoryQuery("segura", limit=5), candidates)

    assert all(item.candidate.kind is not MemoryKind.LEARNING for item in selection.items)


def test_approved_learning_can_be_considered() -> None:
    candidate = MemoryCandidate(
        MemoryKind.LEARNING, "aprendizado aprovado", similarity=1.0, source="reviewed"
    )

    selection = ApprovedRecoveryMemory().select(
        MemoryQuery("aprovado"),
        (candidate,),
        approved_learning_sources=frozenset({"reviewed"}),
    )

    assert selection.items[0].candidate is candidate


def test_recovery_metrics_track_duration_and_success() -> None:
    telemetry = RecoveryTelemetry()
    report = ReplanningReport("goal", (), (), None)

    telemetry.observe(report, duration=2.0, succeeded=True)
    telemetry.observe(report, duration=4.0, succeeded=False)
    metrics = telemetry.metrics()

    assert metrics.analyses == 2
    assert metrics.average_duration == 3.0
    assert metrics.success_rate == 0.5
