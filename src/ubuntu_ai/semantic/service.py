from __future__ import annotations

from ubuntu_ai.knowledge.models import KnowledgeChunk, KnowledgeDocument
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.semantic.embedder import LocalHashEmbedder
from ubuntu_ai.semantic.models import RetrievalContext, SemanticMatch
from ubuntu_ai.semantic.repository import SemanticRepository


class SemanticKnowledgeService:
    """Indexa e recupera conhecimento por ranking híbrido local."""

    def __init__(
        self,
        *,
        knowledge_service: KnowledgeService,
        repository: SemanticRepository,
        embedder: LocalHashEmbedder | None = None,
        lexical_weight: float = 0.35,
    ) -> None:
        if not 0.0 <= lexical_weight <= 1.0:
            raise ValueError("O peso lexical deve estar entre 0 e 1.")
        self._knowledge_service = knowledge_service
        self._repository = repository
        self._embedder = embedder or LocalHashEmbedder()
        self._lexical_weight = lexical_weight

    def index_document(self, document: KnowledgeDocument) -> int:
        chunks = self._chunks_for(document)
        self._repository.delete_document(document.id)
        for chunk in chunks:
            self._repository.upsert(chunk, self._embedder.embed(chunk.content))
        return len(chunks)

    def index_all(self) -> int:
        return sum(
            self.index_document(document)
            for document in self._knowledge_service.list_documents(limit=1_000_000)
        )

    def retrieve(self, query: str, *, limit: int = 5) -> RetrievalContext:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("A consulta semântica não pode estar vazia.")
        if limit < 1:
            raise ValueError("O limite deve ser maior que zero.")

        self._ensure_index()
        query_vector = self._embedder.embed(normalized_query)
        chunks = self._all_chunks()
        documents = {
            document.id: document
            for document in self._knowledge_service.list_documents(limit=1_000_000)
        }
        lexical_by_chunk = self._lexical_scores(normalized_query, limit=max(limit * 4, 10))

        candidates: list[SemanticMatch] = []
        for chunk_id, vector in self._repository.list_vectors():
            chunk = chunks.get(chunk_id)
            if chunk is None:
                continue
            document = documents.get(chunk.document_id)
            if document is None:
                continue
            semantic_score = self._embedder.cosine_similarity(query_vector, vector)
            lexical_score = lexical_by_chunk.get(chunk.id, 0.0)
            score = (
                self._lexical_weight * lexical_score + (1.0 - self._lexical_weight) * semantic_score
            )
            if score <= 0:
                continue
            candidates.append(
                SemanticMatch(
                    document=document,
                    chunk=chunk,
                    score=score,
                    lexical_score=lexical_score,
                    semantic_score=semantic_score,
                )
            )

        candidates.sort(key=lambda item: item.score, reverse=True)
        return RetrievalContext(query=normalized_query, matches=tuple(candidates[:limit]))

    def _ensure_index(self) -> None:
        chunks = self._all_chunks()
        indexed_ids = {chunk_id for chunk_id, _ in self._repository.list_vectors()}
        current_ids = set(chunks)
        if indexed_ids == current_ids:
            return

        for document in self._knowledge_service.list_documents(limit=1_000_000):
            self.index_document(document)

    def _all_chunks(self) -> dict[str, KnowledgeChunk]:
        chunks: dict[str, KnowledgeChunk] = {}
        for document in self._knowledge_service.list_documents(limit=1_000_000):
            for chunk in self._chunks_for(document):
                chunks[chunk.id] = chunk
        return chunks

    def _chunks_for(self, document: KnowledgeDocument) -> tuple[KnowledgeChunk, ...]:
        repository = self._knowledge_service.repository
        list_chunks = getattr(repository, "list_chunks", None)
        if callable(list_chunks):
            return tuple(list_chunks(document.id))
        return (
            KnowledgeChunk.create(
                document_id=document.id,
                position=0,
                content=document.content,
            ),
        )

    def _lexical_scores(self, query: str, *, limit: int) -> dict[str, float]:
        scores: dict[str, float] = {}
        for result in self._knowledge_service.search(query, limit=limit):
            for chunk in result.matched_chunks:
                scores[chunk.id] = max(scores.get(chunk.id, 0.0), min(result.score, 1.0))
        return scores


class RAGContextBuilder:
    """Constrói contexto de recuperação para o Planner e futuras camadas."""

    def __init__(self, service: SemanticKnowledgeService) -> None:
        self._service = service

    def build(self, query: str, *, limit: int = 5, max_chars: int = 4_000) -> str | None:
        context = self._service.retrieve(query, limit=limit)
        prompt = context.to_prompt(max_chars=max_chars)
        return prompt or None
