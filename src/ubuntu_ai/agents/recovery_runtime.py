from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass, replace
from pathlib import Path

from ubuntu_ai.agents.orchestration import OrchestrationGoal, OrchestrationResult
from ubuntu_ai.agents.replanning import ReplanningReport
from ubuntu_ai.memory_intelligence.engine import MemoryIntelligenceEngine
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemoryQuery,
    MemorySelection,
)


@dataclass(frozen=True, slots=True)
class RecoveryCheckpoint:
    goal_id: str
    fingerprint: str
    completed_task_ids: tuple[str, ...]


class SQLiteRecoveryRepository:
    """Persiste somente identidade e progresso; payloads e segredos ficam de fora."""

    def __init__(self, path: Path) -> None:
        self._path = path.expanduser()
        self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self._path.parent, 0o700)
        self._path.touch(mode=0o600, exist_ok=True)
        os.chmod(self._path, 0o600)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS recovery_checkpoints ("
                "goal_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, "
                "completed_task_ids TEXT NOT NULL)"
            )

    def save(self, checkpoint: RecoveryCheckpoint) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO recovery_checkpoints VALUES (?, ?, ?) "
                "ON CONFLICT(goal_id) DO UPDATE SET fingerprint=excluded.fingerprint, "
                "completed_task_ids=excluded.completed_task_ids",
                (
                    checkpoint.goal_id,
                    checkpoint.fingerprint,
                    json.dumps(checkpoint.completed_task_ids),
                ),
            )

    def get(self, goal_id: str) -> RecoveryCheckpoint | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM recovery_checkpoints WHERE goal_id = ?", (goal_id,)
            ).fetchone()
        if row is None:
            return None
        return RecoveryCheckpoint(
            goal_id=str(row[0]),
            fingerprint=str(row[1]),
            completed_task_ids=tuple(json.loads(str(row[2]))),
        )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)


class OrchestrationRecoveryManager:
    def __init__(self, repository: SQLiteRecoveryRepository) -> None:
        self._repository = repository

    def checkpoint(self, goal: OrchestrationGoal, result: OrchestrationResult) -> None:
        if goal.goal_id != result.goal_id:
            raise ValueError("Resultado e objetivo não correspondem.")
        known = {task.task_id: task.specialist for task in goal.tasks}
        result_ids = [item.task_id for item in result.tasks]
        if len(result_ids) != len(set(result_ids)):
            raise ValueError("O resultado contém tarefas duplicadas.")
        if set(result_ids) - known.keys():
            raise ValueError("O resultado contém tarefas fora do objetivo.")
        if any(item.specialist is not known[item.task_id] for item in result.tasks):
            raise ValueError("O resultado contém especialista divergente.")
        completed = tuple(item.task_id for item in result.tasks if item.status.value == "completed")
        self._repository.save(RecoveryCheckpoint(goal.goal_id, _fingerprint(goal), completed))

    def resume(self, goal: OrchestrationGoal) -> OrchestrationGoal:
        checkpoint = self._repository.get(goal.goal_id)
        if checkpoint is None:
            raise KeyError(f"Checkpoint não encontrado: {goal.goal_id}")
        if checkpoint.fingerprint != _fingerprint(goal):
            raise PermissionError("O objetivo mudou após o checkpoint; retomada bloqueada.")
        completed = set(checkpoint.completed_task_ids)
        pending = tuple(task for task in goal.tasks if task.task_id not in completed)
        if not pending:
            raise ValueError("O objetivo já foi concluído.")
        pending_ids = {task.task_id for task in pending}
        tasks = tuple(
            replace(
                task, dependencies=tuple(dep for dep in task.dependencies if dep in pending_ids)
            )
            for task in pending
        )
        keys = set().union(*(task.context_keys for task in tasks))
        return OrchestrationGoal(
            goal_id=f"{goal.goal_id}-resume",
            description=f"Retomada segura: {goal.description}",
            tasks=tasks,
            context={key: goal.context[key] for key in sorted(keys)},
        )


class ApprovedRecoveryMemory:
    """Consulta histórico local sem aceitar aprendizado não aprovado."""

    def __init__(self, engine: MemoryIntelligenceEngine | None = None) -> None:
        self._engine = engine or MemoryIntelligenceEngine()

    def select(
        self,
        query: MemoryQuery,
        candidates: tuple[MemoryCandidate, ...],
        *,
        approved_learning_sources: frozenset[str] = frozenset(),
    ) -> MemorySelection:
        safe = tuple(
            candidate
            for candidate in candidates
            if candidate.kind is not MemoryKind.LEARNING
            or candidate.source in approved_learning_sources
        )
        return self._engine.select(query=query, candidates=safe)


@dataclass(frozen=True, slots=True)
class RecoveryMetrics:
    analyses: int
    retries_proposed: int
    reviews_required: int
    average_duration: float
    success_rate: float


class RecoveryTelemetry:
    def __init__(self) -> None:
        self._records: list[tuple[bool, bool, float, bool]] = []

    def observe(self, report: ReplanningReport, *, duration: float, succeeded: bool) -> None:
        if duration < 0:
            raise ValueError("duration não pode ser negativa.")
        self._records.append(
            (report.recovery_goal is not None, report.requires_review, duration, succeeded)
        )

    def metrics(self) -> RecoveryMetrics:
        total = len(self._records)
        return RecoveryMetrics(
            analyses=total,
            retries_proposed=sum(record[0] for record in self._records),
            reviews_required=sum(record[1] for record in self._records),
            average_duration=(sum(record[2] for record in self._records) / total if total else 0.0),
            success_rate=(sum(record[3] for record in self._records) / total if total else 0.0),
        )


def _fingerprint(goal: OrchestrationGoal) -> str:
    structure = [
        {
            "id": task.task_id,
            "specialist": task.specialist.value,
            "request": task.payload.request,
            "actions": [
                {"argv": action.argv, "risk": action.risk.value} for action in task.payload.actions
            ],
            "environment": task.payload.environment.value,
            "target": task.payload.target,
            "attempt": task.payload.attempt,
            "confirmed": task.payload.confirmed,
            "dependencies": task.dependencies,
            "context_keys": sorted(task.context_keys),
        }
        for task in goal.tasks
    ]
    data = json.dumps(structure, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()
