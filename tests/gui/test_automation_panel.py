from ubuntu_ai.autonomy.long_tasks import (
    LongTask,
    LongTaskStatus,
)
from ubuntu_ai.autonomy.observability import AutomationMetrics
from ubuntu_ai.gui.automation_panel import summary_text, task_row


def test_task_row_presents_status_progress_and_description() -> None:
    task = LongTask(
        task_id="task-1",
        goal_id="goal-1",
        description="Diagnóstico de rede",
        total_steps=4,
        completed_steps=2,
        status=LongTaskStatus.RUNNING,
    )

    assert task_row(task) == ("task-1 · running · 50% · Diagnóstico de rede")


def test_summary_text_presents_target_metrics_and_audit_events() -> None:
    metrics = AutomationMetrics(
        total_events=8,
        active_tasks=2,
        completed_tasks=3,
        failed_tasks=1,
        cancelled_tasks=1,
        timed_out_tasks=0,
        average_progress=0.5,
    )

    assert summary_text(
        target="servidor-tcc",
        metrics=metrics,
        event_count=8,
    ) == ("Destino: servidor-tcc · Ativas: 2 · Concluídas: 3 · Falhas: 1 · Eventos auditáveis: 8")
