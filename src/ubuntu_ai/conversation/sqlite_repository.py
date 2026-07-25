from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from ubuntu_ai.conversation.models import ConversationMessage, ConversationRole
from ubuntu_ai.memory.database import default_database_path, prepare_database_path


class SQLiteConversationRepository:
    """Persistência SQLite de conversas no banco compartilhado de memória."""

    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = prepare_database_path(
            database_path or default_database_path()
        )
        self._initialize_schema()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def save_message(self, message: ConversationMessage) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversation_messages (
                    id, session_id, role, content, created_at, sequence
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message.id,
                    message.session_id,
                    message.role.value,
                    message.content,
                    message.created_at.isoformat(),
                    message.sequence,
                ),
            )

    def list_messages(
        self,
        *,
        session_id: str,
        limit: int = 50,
    ) -> tuple[ConversationMessage, ...]:
        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM (
                    SELECT *
                    FROM conversation_messages
                    WHERE session_id = ?
                    ORDER BY sequence DESC
                    LIMIT ?
                )
                ORDER BY sequence ASC
                """,
                (session_id, limit),
            ).fetchall()

        return tuple(self._message_from_row(row) for row in rows)

    def next_sequence(self, *, session_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COALESCE(MAX(sequence), 0) + 1 AS next_sequence
                FROM conversation_messages
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        return int(row["next_sequence"])

    def clear_session(self, *, session_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM conversation_messages WHERE session_id = ?",
                (session_id,),
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    UNIQUE(session_id, sequence)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversation_session_sequence
                ON conversation_messages (session_id, sequence)
                """
            )

    @staticmethod
    def _message_from_row(row: sqlite3.Row) -> ConversationMessage:
        return ConversationMessage(
            id=str(row["id"]),
            session_id=str(row["session_id"]),
            role=ConversationRole(str(row["role"])),
            content=str(row["content"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            sequence=int(row["sequence"]),
        )
