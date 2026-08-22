import pytest

from ubuntu_ai.agents.models import AgentKind
from ubuntu_ai.agents.orchestration import (
    OrchestrationGoal,
    OrchestrationResult,
    OrchestrationStatus,
    OrchestrationTask,
    OrchestrationTaskResult,
)
from ubuntu_ai.agents.replanning import OrchestrationReplanner
from ubuntu_ai.agents.specialists import SpecialistAction, SpecialistPayload
from ubuntu_ai.reflection.failure import FailureKind


def task(
    task_id: str,
    specialist: AgentKind = AgentKind.NETWORK,
    *,
    attempt: int = 1,
) -> OrchestrationTask:
    command = {
        AgentKind.NETWORK: ("ip", "route"),
        AgentKind.SYSTEM: ("uptime",),
    }[specialist]
    return OrchestrationTask(
        task_id=task_id,
        specialist=specialist,
        payload=SpecialistPayload(
            request="diagnosticar",
            actions=(SpecialistAction(command),),
            attempt=attempt,
        ),
        context_keys=frozenset({"target"}),
    )


def result(
    goal_id: str,
    *items: tuple[str, AgentKind, OrchestrationStatus, str],
) -> OrchestrationResult:
    return OrchestrationResult(
        goal_id=goal_id,
        status=OrchestrationStatus.BLOCKED,
        tasks=tuple(
            OrchestrationTaskResult(
                task_id=task_id,
                specialist=specialist,
                status=status,
                reason=reason,
            )
            for task_id, specialist, status, reason in items
        ),
        total_tasks=len(items),
    )


def test_replanner_analyzes_partial_result_and_preserves_scope() -> None:
    system = task("system", AgentKind.SYSTEM)
    network = task("network")
    goal = OrchestrationGoal(
        "health",
        "Diagnóstico",
        (system, network),
        context={"target": "local", "secret": "do-not-share"},
    )
    partial = result(
        "health",
        ("system", AgentKind.SYSTEM, OrchestrationStatus.COMPLETED, ""),
        (
            "network",
            AgentKind.NETWORK,
            OrchestrationStatus.FAILED,
            "network is unreachable",
        ),
    )

    report = OrchestrationReplanner().analyze(goal, partial)

    assert report.completed_task_ids == ("system",)
    assert report.decisions[0].failure.kind is FailureKind.NETWORK
    assert report.recovery_goal is not None
    retry = report.recovery_goal.tasks[0]
    assert retry.specialist is AgentKind.NETWORK
    assert retry.payload.actions == network.payload.actions
    assert retry.payload.attempt == 2
    assert dict(report.recovery_goal.context) == {"target": "local"}
    assert "preservados" in report.decisions[0].justification


@pytest.mark.parametrize(
    ("message", "kind"),
    (
        ("permission denied", FailureKind.PERMISSION),
        ("command not found", FailureKind.NOT_FOUND),
        ("unexpected failure", FailureKind.UNKNOWN),
    ),
)
def test_replanner_blocks_unsafe_or_unverified_alternative(message: str, kind) -> None:
    original = task("network")
    goal = OrchestrationGoal(
        "goal",
        "Diagnóstico",
        (original,),
        context={"target": "local"},
    )

    report = OrchestrationReplanner().analyze(
        goal,
        result(
            "goal",
            ("network", AgentKind.NETWORK, OrchestrationStatus.FAILED, message),
        ),
    )

    assert report.decisions[0].failure.kind is kind
    assert report.decisions[0].alternative is None
    assert report.recovery_goal is None
    assert report.requires_review


def test_replanner_respects_attempt_limit() -> None:
    original = task("network", attempt=3)
    goal = OrchestrationGoal(
        "goal",
        "Diagnóstico",
        (original,),
        context={"target": "local"},
    )

    report = OrchestrationReplanner().analyze(
        goal,
        result(
            "goal",
            (
                "network",
                AgentKind.NETWORK,
                OrchestrationStatus.FAILED,
                "connection refused",
            ),
        ),
    )

    assert report.decisions[0].alternative is None
    assert report.recovery_goal is None


def test_replanner_rejects_foreign_result() -> None:
    goal = OrchestrationGoal(
        "goal",
        "Diagnóstico",
        (task("network"),),
        context={"target": "local"},
    )

    with pytest.raises(ValueError, match="não pertence"):
        OrchestrationReplanner().analyze(
            goal,
            result(
                "other",
                (
                    "network",
                    AgentKind.NETWORK,
                    OrchestrationStatus.FAILED,
                    "timeout",
                ),
            ),
        )


def test_replanner_rejects_task_outside_original_goal() -> None:
    goal = OrchestrationGoal(
        "goal",
        "Diagnóstico",
        (task("network"),),
        context={"target": "local"},
    )

    with pytest.raises(ValueError, match="fora do objetivo"):
        OrchestrationReplanner().analyze(
            goal,
            result(
                "goal",
                (
                    "intruder",
                    AgentKind.SYSTEM,
                    OrchestrationStatus.FAILED,
                    "timeout",
                ),
            ),
        )


def test_replanner_rejects_specialist_changed_by_result() -> None:
    goal = OrchestrationGoal(
        "goal",
        "Diagnóstico",
        (task("network"),),
        context={"target": "local"},
    )

    with pytest.raises(ValueError, match="Especialista divergente"):
        OrchestrationReplanner().analyze(
            goal,
            result(
                "goal",
                (
                    "network",
                    AgentKind.SYSTEM,
                    OrchestrationStatus.FAILED,
                    "timeout",
                ),
            ),
        )


def test_replanner_rejects_duplicate_results() -> None:
    goal = OrchestrationGoal(
        "goal",
        "Diagnóstico",
        (task("network"),),
        context={"target": "local"},
    )

    duplicate = (
        "network",
        AgentKind.NETWORK,
        OrchestrationStatus.FAILED,
        "timeout",
    )
    with pytest.raises(ValueError, match="duplicadas"):
        OrchestrationReplanner().analyze(
            goal,
            result("goal", duplicate, duplicate),
        )
