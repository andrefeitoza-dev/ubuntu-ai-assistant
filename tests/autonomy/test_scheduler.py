from datetime import UTC, datetime, timedelta

import pytest

from ubuntu_ai.autonomy.scheduler import (
    AutomationRisk,
    LocalAutomationScheduler,
    ScheduledAutomation,
)


def item(risk: AutomationRisk) -> ScheduledAutomation:
    return ScheduledAutomation(
        schedule_id=f"s-{risk.value}",
        task_id="task-1",
        run_at=datetime.now(UTC) - timedelta(seconds=1),
        risk=risk,
    )


def test_low_risk_schedule_is_ready_without_confirmation() -> None:
    scheduler = LocalAutomationScheduler()
    scheduler.schedule(item(AutomationRisk.LOW))

    ready = scheduler.claim_ready()

    assert len(ready) == 1
    assert ready[0].claimed


@pytest.mark.parametrize("risk", (AutomationRisk.MEDIUM, AutomationRisk.HIGH))
def test_sensitive_schedule_waits_for_confirmation(risk: AutomationRisk) -> None:
    scheduler = LocalAutomationScheduler()
    scheduled = scheduler.schedule(item(risk))

    assert scheduled.requires_confirmation
    assert scheduler.claim_ready() == ()

    scheduler.confirm(scheduled.schedule_id)

    assert len(scheduler.claim_ready()) == 1


def test_critical_action_cannot_be_scheduled() -> None:
    with pytest.raises(ValueError, match="CRITICAL"):
        item(AutomationRisk.CRITICAL)


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValueError, match="fuso"):
        ScheduledAutomation("s1", "t1", datetime.now(), AutomationRisk.LOW)


def test_scheduler_lists_items_in_stable_order() -> None:
    scheduler = LocalAutomationScheduler()
    high = item(AutomationRisk.HIGH)
    low = item(AutomationRisk.LOW)

    scheduler.schedule(high)
    scheduler.schedule(low)

    assert scheduler.all() == (high, low)
