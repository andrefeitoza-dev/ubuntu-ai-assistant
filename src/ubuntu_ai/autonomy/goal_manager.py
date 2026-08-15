from __future__ import annotations

from ubuntu_ai.autonomy.goal import Goal, GoalStatus


class GoalManager:
    """Gerencia o ciclo de vida de objetivos em memória."""

    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}

    def add(self, goal: Goal) -> None:
        if goal.goal_id in self._goals:
            raise ValueError(f"Objetivo já registrado: {goal.goal_id}")
        self._goals[goal.goal_id] = goal

    def get(self, goal_id: str) -> Goal:
        try:
            return self._goals[goal_id]
        except KeyError as exc:
            raise KeyError(f"Objetivo não encontrado: {goal_id}") from exc

    def update(self, goal: Goal) -> None:
        if goal.goal_id not in self._goals:
            raise KeyError(f"Objetivo não encontrado: {goal.goal_id}")
        self._goals[goal.goal_id] = goal

    def active(self) -> tuple[Goal, ...]:
        return tuple(
            goal
            for goal in self._goals.values()
            if goal.status
            in {
                GoalStatus.PENDING,
                GoalStatus.RUNNING,
                GoalStatus.BLOCKED,
            }
        )
