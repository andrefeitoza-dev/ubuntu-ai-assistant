from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from ubuntu_ai.knowledge.chunker import DocumentChunker
from ubuntu_ai.knowledge.database import (
    default_knowledge_database_path,
    prepare_knowledge_database_path,
)
from ubuntu_ai.knowledge.exceptions import KnowledgeNotFoundError
from ubuntu_ai.knowledge.models import (
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeResult,
    KnowledgeSource,
    KnowledgeTag,
)
from ubuntu_ai.knowledge.repository import KnowledgeRepository


class SQLiteKnowledgeRepository(KnowledgeRepository):
    """Backend SQLite com índice FTS5 para documentos e trechos."""

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        chunker: DocumentChunker | None = None,
    ) -> None:
        self._database_path = prepare_knowledge_database_path(
            database_path or default_knowledge_database_path()
        )
        self._chunker = chunker or DocumentChunker()
        self._initialize_schema()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        with self._connect() as connection:
            self._insert_document(connection, document)
        return document

    def update_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        with self._connect() as connection:
            if not self._exists(connection, document.id):
                raise KnowledgeNotFoundError(
                    f"Documento de conhecimento não encontrado: {document.id}"
                )
            connection.execute("DELETE FROM knowledge_documents WHERE id = ?", (document.id,))
            self._insert_document(connection, document)
        return document

    def delete_document(self, document_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM knowledge_documents WHERE id = ?", (document_id,)
            )
        return cursor.rowcount > 0

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM knowledge_documents WHERE id = ?", (document_id,)
            ).fetchone()
        return None if row is None else self._document_from_row(row)

    def list_documents(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[KnowledgeDocument, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM knowledge_documents
                ORDER BY updated_at DESC, title ASC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
        return tuple(self._document_from_row(row) for row in rows)

    def search(self, query: str, *, limit: int = 10) -> tuple[KnowledgeResult, ...]:
        fts_query = self._to_fts_query(query)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    d.*,
                    c.id AS chunk_id,
                    c.position AS chunk_position,
                    c.content AS chunk_content,
                    bm25(knowledge_chunks_fts) AS rank
                FROM knowledge_chunks_fts
                JOIN knowledge_chunks c ON c.rowid = knowledge_chunks_fts.rowid
                JOIN knowledge_documents d ON d.id = c.document_id
                WHERE knowledge_chunks_fts MATCH ?
                ORDER BY rank ASC
                LIMIT ?
                """,
                (fts_query, limit * 4),
            ).fetchall()

        grouped: dict[str, list[sqlite3.Row]] = {}
        for row in rows:
            grouped.setdefault(str(row["id"]), []).append(row)

        results: list[KnowledgeResult] = []
        for document_rows in grouped.values():
            first = document_rows[0]
            chunks = tuple(
                KnowledgeChunk(
                    id=str(row["chunk_id"]),
                    document_id=str(row["id"]),
                    position=int(row["chunk_position"]),
                    content=str(row["chunk_content"]),
                )
                for row in document_rows[:3]
            )
            rank = abs(float(first["rank"]))
            score = 1.0 / (1.0 + rank)
            results.append(
                KnowledgeResult(
                    document=self._document_from_row(first),
                    score=score,
                    excerpt=self._excerpt(chunks[0].content, query),
                    matched_chunks=chunks,
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return tuple(results[:limit])

    def find_related(
        self,
        document_id: str,
        *,
        limit: int = 5,
    ) -> tuple[KnowledgeResult, ...]:
        document = self.get_document(document_id)
        if document is None:
            return ()
        terms = [tag.name for tag in document.tags]
        terms.extend(document.title.split())
        query = " ".join(dict.fromkeys(term for term in terms if len(term) > 2))
        if not query:
            return ()
        return tuple(
            result for result in self.search(query, limit=limit + 1)
            if result.document.id != document_id
        )[:limit]

    def list_chunks(self, document_id: str | None = None) -> tuple[KnowledgeChunk, ...]:
        """Lista trechos persistidos para indexação semântica local."""

        query = "SELECT id, document_id, position, content FROM knowledge_chunks"
        parameters: tuple[str, ...] = ()
        if document_id is not None:
            query += " WHERE document_id = ?"
            parameters = (document_id,)
        query += " ORDER BY document_id, position"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return tuple(
            KnowledgeChunk(
                id=str(row["id"]),
                document_id=str(row["document_id"]),
                position=int(row["position"]),
                content=str(row["content"]),
            )
            for row in rows
        )

    def document_exists(self, document_id: str) -> bool:
        with self._connect() as connection:
            return self._exists(connection, document_id)

    def reindex_document(self, document_id: str) -> int:
        document = self.get_document(document_id)
        if document is None:
            raise KnowledgeNotFoundError(
                f"Documento de conhecimento não encontrado: {document_id}"
            )
        with self._connect() as connection:
            connection.execute("DELETE FROM knowledge_chunks WHERE document_id = ?", (document_id,))
            chunks = self._chunker.split(document_id=document.id, content=document.content)
            self._insert_chunks(connection, chunks)
        return len(chunks)

    def reindex_all(self) -> int:
        documents = self.list_documents(limit=1_000_000)
        return sum(self.reindex_document(document.id) for document in documents)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_reference TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES knowledge_documents(id)
                        ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    UNIQUE(document_id, position)
                );

                CREATE INDEX IF NOT EXISTS idx_knowledge_documents_updated
                ON knowledge_documents(updated_at DESC);

                CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document
                ON knowledge_chunks(document_id, position);

                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts USING fts5(
                    content,
                    content='knowledge_chunks',
                    content_rowid='rowid',
                    tokenize='unicode61 remove_diacritics 2'
                );

                CREATE TRIGGER IF NOT EXISTS knowledge_chunks_ai
                AFTER INSERT ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(rowid, content)
                    VALUES (new.rowid, new.content);
                END;

                CREATE TRIGGER IF NOT EXISTS knowledge_chunks_ad
                AFTER DELETE ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts, rowid, content)
                    VALUES ('delete', old.rowid, old.content);
                END;

                CREATE TRIGGER IF NOT EXISTS knowledge_chunks_au
                AFTER UPDATE ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts, rowid, content)
                    VALUES ('delete', old.rowid, old.content);
                    INSERT INTO knowledge_chunks_fts(rowid, content)
                    VALUES (new.rowid, new.content);
                END;
                """
            )

    def _insert_document(
        self, connection: sqlite3.Connection, document: KnowledgeDocument
    ) -> None:
        connection.execute(
            """
            INSERT INTO knowledge_documents (
                id, title, content, source, source_reference,
                created_at, updated_at, tags_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document.id,
                document.title,
                document.content,
                document.source.value,
                document.source_reference,
                document.created_at.isoformat(),
                document.updated_at.isoformat(),
                json.dumps([tag.name for tag in document.tags], ensure_ascii=False),
                json.dumps(document.metadata, ensure_ascii=False, sort_keys=True),
            ),
        )
        chunks = self._chunker.split(document_id=document.id, content=document.content)
        self._insert_chunks(connection, chunks)

    @staticmethod
    def _insert_chunks(
        connection: sqlite3.Connection, chunks: tuple[KnowledgeChunk, ...]
    ) -> None:
        connection.executemany(
            """
            INSERT INTO knowledge_chunks (id, document_id, position, content)
            VALUES (?, ?, ?, ?)
            """,
            [(chunk.id, chunk.document_id, chunk.position, chunk.content) for chunk in chunks],
        )

    @staticmethod
    def _exists(connection: sqlite3.Connection, document_id: str) -> bool:
        row = connection.execute(
            "SELECT 1 FROM knowledge_documents WHERE id = ?", (document_id,)
        ).fetchone()
        return row is not None

    @staticmethod
    def _document_from_row(row: sqlite3.Row) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=str(row["id"]),
            title=str(row["title"]),
            content=str(row["content"]),
            source=KnowledgeSource(str(row["source"])),
            source_reference=(
                None
                if row["source_reference"] is None
                else str(row["source_reference"])
            ),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
            tags=tuple(KnowledgeTag(name) for name in json.loads(str(row["tags_json"]))),
            metadata={
                str(key): str(value)
                for key, value in json.loads(str(row["metadata_json"])).items()
            },
        )

    @staticmethod
    def _to_fts_query(query: str) -> str:
        tokens = [token.strip('"\'()[]{}:;,.!?') for token in query.split()]
        safe_tokens = [token.replace('"', '""') for token in tokens if token]
        return " OR ".join(f'"{token}"*' for token in safe_tokens)

    @staticmethod
    def _excerpt(content: str, query: str, *, width: int = 240) -> str:
        lowered = content.lower()
        positions = [lowered.find(token.lower()) for token in query.split()]
        positions = [position for position in positions if position >= 0]
        center = min(positions) if positions else 0
        start = max(center - width // 3, 0)
        end = min(start + width, len(content))
        excerpt = content[start:end].strip()
        if start > 0:
            excerpt = f"…{excerpt}"
        if end < len(content):
            excerpt = f"{excerpt}…"
        return excerpt
