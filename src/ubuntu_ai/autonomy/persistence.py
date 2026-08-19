from __future__ import annotations

import os
import re
import sqlite3
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from ubuntu_ai.autonomy.long_tasks import LongTask, LongTaskStatus
from ubuntu_ai.autonomy.scheduler import AutomationRisk, ScheduledAutomation

_SENSITIVE = re.compile(r"(?i)(password|passwd|token|secret|api[_-]?key|private[_-]?key)\s*[:=]")


def default_automation_database() -> Path:
    return Path.home() / ".ubuntu_ai" / "automation.db"


class SQLiteAutomationRepository:
    """Persiste checkpoints e histórico sem aceitar segredos aparentes."""

    def __init__(self, database_path: Path | None = None) -> None:
        self._path = (database_path or default_automation_database()).expanduser()
        self._prepare()
        self._initialize()

    @property
    def database_path(self) -> Path:
        return self._path

    def save(self, task: LongTask) -> None:
        self._validate_safe(task)
        values = (
            task.task_id,
            task.goal_id,
            task.description,
            task.total_steps,
            task.max_duration,
            task.status.value,
            task.completed_steps,
            task.message,
            task.started_at,
            task.updated_at,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO automation_tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    goal_id=excluded.goal_id,
                    description=excluded.description,
                    total_steps=excluded.total_steps,
                    max_duration=excluded.max_duration,
                    status=excluded.status,
                    completed_steps=excluded.completed_steps,
                    message=excluded.message,
                    started_at=excluded.started_at,
                    updated_at=excluded.updated_at
                """,
                values,
            )
            connection.execute(
                """
                INSERT INTO automation_history (
                    task_id, status, completed_steps, message, recorded_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    task.task_id,
                    task.status.value,
                    task.completed_steps,
                    task.message,
                    task.updated_at,
                ),
            )

    def get(self, task_id: str) -> LongTask | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM automation_tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
        return self._task(row) if row is not None else None

    def list_tasks(self) -> tuple[LongTask, ...]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM automation_tasks ORDER BY rowid").fetchall()
        return tuple(self._task(row) for row in rows)

    def history(self, task_id: str) -> tuple[tuple[str, int, str], ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT status, completed_steps, message
                FROM automation_history WHERE task_id = ? ORDER BY id
                """,
                (task_id,),
            ).fetchall()
        return tuple(
            (str(row["status"]), int(row["completed_steps"]), str(row["message"])) for row in rows
        )

    def recover_interrupted(self) -> tuple[LongTask, ...]:
        recovered: list[LongTask] = []
        for task in self.list_tasks():
            if task.status not in {LongTaskStatus.RUNNING, LongTaskStatus.PAUSED}:
                continue
            restored = replace(
                task,
                status=LongTaskStatus.PENDING,
                message="Recuperada após interrupção; aguardando retomada segura.",
                started_at=None,
                updated_at=None,
            )
            self.save(restored)
            recovered.append(restored)
        return tuple(recovered)

    def save_schedule(self, item: ScheduledAutomation) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO automation_schedules VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(schedule_id) DO UPDATE SET
                    task_id=excluded.task_id,
                    run_at=excluded.run_at,
                    risk=excluded.risk,
                    confirmed=excluded.confirmed,
                    claimed=excluded.claimed
                """,
                (
                    item.schedule_id,
                    item.task_id,
                    item.run_at.isoformat(),
                    item.risk.value,
                    int(item.confirmed),
                    int(item.claimed),
                ),
            )

    def list_schedules(self) -> tuple[ScheduledAutomation, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM automation_schedules ORDER BY rowid"
            ).fetchall()
        return tuple(
            ScheduledAutomation(
                schedule_id=str(row["schedule_id"]),
                task_id=str(row["task_id"]),
                run_at=datetime.fromisoformat(str(row["run_at"])),
                risk=AutomationRisk(str(row["risk"])),
                confirmed=bool(row["confirmed"]),
                claimed=bool(row["claimed"]),
            )
            for row in rows
        )

    def _prepare(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self._path.parent, 0o700)
        self._path.touch(mode=0o600, exist_ok=True)
        os.chmod(self._path, 0o600)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_tasks (
                    task_id TEXT PRIMARY KEY, goal_id TEXT NOT NULL,
                    description TEXT NOT NULL, total_steps INTEGER NOT NULL,
                    max_duration REAL NOT NULL, status TEXT NOT NULL,
                    completed_steps INTEGER NOT NULL, message TEXT NOT NULL,
                    started_at REAL, updated_at REAL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_schedules (
                    schedule_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    run_at TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    confirmed INTEGER NOT NULL,
                    claimed INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL, status TEXT NOT NULL,
                    completed_steps INTEGER NOT NULL, message TEXT NOT NULL,
                    recorded_at REAL
                )
                """
            )

    @staticmethod
    def _validate_safe(task: LongTask) -> None:
        if _SENSITIVE.search(task.description) or _SENSITIVE.search(task.message):
            raise ValueError("Checkpoint rejeitado: conteúdo potencialmente secreto.")

    @staticmethod
    def _task(row: sqlite3.Row) -> LongTask:
        return LongTask(
            task_id=str(row["task_id"]),
            goal_id=str(row["goal_id"]),
            description=str(row["description"]),
            total_steps=int(row["total_steps"]),
            max_duration=float(row["max_duration"]),
            status=LongTaskStatus(str(row["status"])),
            completed_steps=int(row["completed_steps"]),
            message=str(row["message"]),
            started_at=float(row["started_at"]) if row["started_at"] is not None else None,
            updated_at=float(row["updated_at"]) if row["updated_at"] is not None else None,
        )
