from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum


class AutomationRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class ScheduledAutomation:
    schedule_id: str
    task_id: str
    run_at: datetime
    risk: AutomationRisk
    confirmed: bool = False
    claimed: bool = False

    def __post_init__(self) -> None:
        if not self.schedule_id.strip() or not self.task_id.strip():
            raise ValueError("Identificadores do agendamento não podem estar vazios.")
        if self.run_at.tzinfo is None:
            raise ValueError("run_at deve possuir fuso horário.")
        if self.risk is AutomationRisk.CRITICAL:
            raise ValueError("Ações CRITICAL não podem ser agendadas.")

    @property
    def requires_confirmation(self) -> bool:
        return self.risk is not AutomationRisk.LOW and not self.confirmed


class LocalAutomationScheduler:
    """Agenda tarefas locais sem liberar riscos sensíveis automaticamente."""

    def __init__(self) -> None:
        self._items: dict[str, ScheduledAutomation] = {}

    def schedule(self, item: ScheduledAutomation) -> ScheduledAutomation:
        if item.schedule_id in self._items:
            raise ValueError(f"Agendamento já registrado: {item.schedule_id}")
        self._items[item.schedule_id] = item
        return item

    def confirm(self, schedule_id: str) -> ScheduledAutomation:
        item = self.get(schedule_id)
        confirmed = replace(item, confirmed=True)
        self._items[schedule_id] = confirmed
        return confirmed

    def all(self) -> tuple[ScheduledAutomation, ...]:
        return tuple(self._items[key] for key in sorted(self._items))

    def get(self, schedule_id: str) -> ScheduledAutomation:
        try:
            return self._items[schedule_id]
        except KeyError as exc:
            raise KeyError(f"Agendamento não encontrado: {schedule_id}") from exc

    def due(self, now: datetime | None = None) -> tuple[ScheduledAutomation, ...]:
        current = now or datetime.now(UTC)
        if current.tzinfo is None:
            raise ValueError("now deve possuir fuso horário.")
        return tuple(
            item for item in self._items.values() if not item.claimed and item.run_at <= current
        )

    def claim_ready(self, now: datetime | None = None) -> tuple[ScheduledAutomation, ...]:
        ready: list[ScheduledAutomation] = []
        for item in self.due(now):
            if item.requires_confirmation:
                continue
            claimed = replace(item, claimed=True)
            self._items[item.schedule_id] = claimed
            ready.append(claimed)
        return tuple(ready)
