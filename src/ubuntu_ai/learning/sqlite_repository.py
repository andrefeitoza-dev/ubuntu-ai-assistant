from __future__ import annotations

import sqlite3
from pathlib import Path

from ubuntu_ai.learning.database import default_database_path, prepare_database_path
from ubuntu_ai.learning.models import LearningOutcome, LearningPattern


class SQLiteLearningRepository:
    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = prepare_database_path(database_path or default_database_path())
        self._initialize_schema()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def record_outcome(
        self,
        pattern: LearningPattern,
        outcome: LearningOutcome,
    ) -> LearningPattern:
        project_scope = pattern.project_name or ""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM learning_patterns
                WHERE request_pattern = ? AND command = ? AND project_scope = ?
                """,
                (pattern.request_pattern, pattern.command, project_scope),
            ).fetchone()
            current = self._from_row(row) if row is not None else pattern
            updated = current.with_outcome(outcome)
            connection.execute(
                """
                INSERT INTO learning_patterns (
                    id, created_at, updated_at, request_pattern, command,
                    project_scope, project_name, success_count, failure_count,
                    blocked_count, positive_feedback, negative_feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_pattern, command, project_scope) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    success_count = excluded.success_count,
                    failure_count = excluded.failure_count,
                    blocked_count = excluded.blocked_count,
                    positive_feedback = excluded.positive_feedback,
                    negative_feedback = excluded.negative_feedback
                """,
                self._values(updated),
            )
        return updated

    def get_pattern(self, pattern_id: str) -> LearningPattern | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM learning_patterns WHERE id = ?", (pattern_id,)
            ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_patterns(
        self,
        *,
        project_name: str | None = None,
        limit: int = 100,
    ) -> tuple[LearningPattern, ...]:
        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")
        query = "SELECT * FROM learning_patterns"
        params: list[object] = []
        if project_name is not None:
            query += " WHERE project_scope IN (?, '')"
            params.append(project_name)
        query += " ORDER BY updated_at DESC, rowid DESC LIMIT ?"
        params.append(limit)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def record_feedback(self, pattern_id: str, *, helpful: bool) -> LearningPattern:
        current = self.get_pattern(pattern_id)
        if current is None:
            raise KeyError(f"Padrão de aprendizado não encontrado: {pattern_id}")
        updated = current.with_feedback(helpful=helpful)
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE learning_patterns SET updated_at = ?, positive_feedback = ?,
                    negative_feedback = ? WHERE id = ?
                """,
                (
                    updated.updated_at.isoformat(),
                    updated.positive_feedback,
                    updated.negative_feedback,
                    updated.id,
                ),
            )
        return updated

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    request_pattern TEXT NOT NULL,
                    command TEXT NOT NULL,
                    project_scope TEXT NOT NULL,
                    project_name TEXT,
                    success_count INTEGER NOT NULL DEFAULT 0,
                    failure_count INTEGER NOT NULL DEFAULT 0,
                    blocked_count INTEGER NOT NULL DEFAULT 0,
                    positive_feedback INTEGER NOT NULL DEFAULT 0,
                    negative_feedback INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(request_pattern, command, project_scope)
                )
                """
            )

    @staticmethod
    def _values(pattern: LearningPattern) -> tuple[object, ...]:
        return (
            pattern.id,
            pattern.created_at.isoformat(),
            pattern.updated_at.isoformat(),
            pattern.request_pattern,
            pattern.command,
            pattern.project_name or "",
            pattern.project_name,
            pattern.success_count,
            pattern.failure_count,
            pattern.blocked_count,
            pattern.positive_feedback,
            pattern.negative_feedback,
        )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> LearningPattern:
        from datetime import datetime

        return LearningPattern(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            request_pattern=row["request_pattern"],
            command=row["command"],
            project_name=row["project_name"],
            success_count=row["success_count"],
            failure_count=row["failure_count"],
            blocked_count=row["blocked_count"],
            positive_feedback=row["positive_feedback"],
            negative_feedback=row["negative_feedback"],
        )
