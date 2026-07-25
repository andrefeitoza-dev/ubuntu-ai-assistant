from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from ubuntu_ai.memory.database import default_database_path, prepare_database_path
from ubuntu_ai.memory.models import ExecutionRecord, MemoryEventType


class SQLiteMemoryRepository:
    """Repositório SQLite para o histórico persistente do UbuntuAI."""

    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = prepare_database_path(
            database_path or default_database_path()
        )
        self._initialize_schema()

    @property
    def database_path(self) -> Path:
        """Retorna o caminho do banco utilizado pelo repositório."""

        return self._database_path

    def save_execution(self, record: ExecutionRecord) -> None:
        """Persiste um registro de execução."""

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO execution_history (
                    id,
                    event_type,
                    created_at,
                    session_id,
                    user_request,
                    command,
                    status,
                    message,
                    working_directory,
                    project_name,
                    return_code,
                    stdout,
                    stderr,
                    duration
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.event_type.value,
                    record.created_at.isoformat(),
                    record.session_id,
                    record.user_request,
                    record.command,
                    record.status,
                    record.message,
                    record.working_directory,
                    record.project_name,
                    record.return_code,
                    record.stdout,
                    record.stderr,
                    record.duration,
                ),
            )

    def get_execution(self, record_id: str) -> ExecutionRecord | None:
        """Busca um registro pelo identificador."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM execution_history
                WHERE id = ?
                """,
                (record_id,),
            ).fetchone()

        return self._record_from_row(row) if row is not None else None

    def get_last_execution(self) -> ExecutionRecord | None:
        """Retorna a execução mais recente."""

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM execution_history
                ORDER BY created_at DESC, rowid DESC
                LIMIT 1
                """
            ).fetchone()

        return self._record_from_row(row) if row is not None else None

    def list_executions(
        self,
        *,
        limit: int = 50,
        since: datetime | None = None,
        status: str | None = None,
        project_name: str | None = None,
    ) -> tuple[ExecutionRecord, ...]:
        """Lista execuções da mais recente para a mais antiga."""

        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")

        clauses: list[str] = []
        parameters: list[object] = []

        if since is not None:
            clauses.append("created_at >= ?")
            parameters.append(since.isoformat())

        if status is not None:
            clauses.append("status = ?")
            parameters.append(status)

        if project_name is not None:
            clauses.append("project_name = ?")
            parameters.append(project_name)

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        parameters.append(limit)

        query = f"""
            SELECT *
            FROM execution_history
            {where_clause}
            ORDER BY created_at DESC, rowid DESC
            LIMIT ?
        """

        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()

        return tuple(self._record_from_row(row) for row in rows)

    def count_executions(
        self,
        *,
        since: datetime | None = None,
        status: str | None = None,
    ) -> int:
        """Conta execuções usando filtros opcionais."""

        clauses: list[str] = []
        parameters: list[object] = []

        if since is not None:
            clauses.append("created_at >= ?")
            parameters.append(since.isoformat())

        if status is not None:
            clauses.append("status = ?")
            parameters.append(status)

        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        with self._connect() as connection:
            row = connection.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM execution_history
                {where_clause}
                """,
                parameters,
            ).fetchone()

        return int(row["total"])

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_history (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    user_request TEXT NOT NULL,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    working_directory TEXT NOT NULL,
                    project_name TEXT,
                    return_code INTEGER,
                    stdout TEXT NOT NULL DEFAULT '',
                    stderr TEXT NOT NULL DEFAULT '',
                    duration REAL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_history_created_at
                ON execution_history (created_at DESC)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_history_status
                ON execution_history (status)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_history_project
                ON execution_history (project_name)
                """
            )

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> ExecutionRecord:
        return ExecutionRecord(
            id=str(row["id"]),
            event_type=MemoryEventType(str(row["event_type"])),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            session_id=str(row["session_id"]),
            user_request=str(row["user_request"]),
            command=str(row["command"]),
            status=str(row["status"]),
            message=str(row["message"]),
            working_directory=str(row["working_directory"]),
            project_name=(
                str(row["project_name"])
                if row["project_name"] is not None
                else None
            ),
            return_code=(
                int(row["return_code"])
                if row["return_code"] is not None
                else None
            ),
            stdout=str(row["stdout"]),
            stderr=str(row["stderr"]),
            duration=(
                float(row["duration"])
                if row["duration"] is not None
                else None
            ),
        )
