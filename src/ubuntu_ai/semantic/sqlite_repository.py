from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from pathlib import Path

from ubuntu_ai.knowledge.database import (
    default_knowledge_database_path,
    prepare_knowledge_database_path,
)
from ubuntu_ai.knowledge.models import KnowledgeChunk
from ubuntu_ai.semantic.repository import SemanticRepository


class SQLiteSemanticRepository(SemanticRepository):
    """Persiste embeddings no mesmo banco SQLite do Knowledge Engine."""

    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = prepare_knowledge_database_path(
            database_path or default_knowledge_database_path()
        )
        self._initialize_schema()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def upsert(self, chunk: KnowledgeChunk, vector: Sequence[float]) -> None:
        payload = json.dumps(list(vector), separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO knowledge_embeddings (chunk_id, document_id, vector_json)
                VALUES (?, ?, ?)
                ON CONFLICT(chunk_id) DO UPDATE SET
                    document_id = excluded.document_id,
                    vector_json = excluded.vector_json
                """,
                (chunk.id, chunk.document_id, payload),
            )

    def delete_document(self, document_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM knowledge_embeddings WHERE document_id = ?",
                (document_id,),
            )

    def list_vectors(self) -> tuple[tuple[str, tuple[float, ...]], ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT chunk_id, vector_json FROM knowledge_embeddings"
            ).fetchall()
        return tuple(
            (str(row["chunk_id"]), tuple(float(item) for item in json.loads(row["vector_json"])))
            for row in rows
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    vector_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_document
                ON knowledge_embeddings(document_id);
                """
            )
