"""In-memory cosine-similarity store.

Used as the universal fallback when a real backend (pgvector/Weaviate/Pinecone)
is unavailable — e.g. during tests on sqlite, or local runs without the vector
service up. Keeps RAG code paths fully exercised without external infra.
"""
from __future__ import annotations

import math

from app.vectorstores.base import Document


class MemoryVectorStore:
    def __init__(self, embeddings) -> None:
        self._embeddings = embeddings
        self._items: list[tuple[list[float], str, dict]] = []

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        metadatas = metadatas or [{} for _ in texts]
        vectors = self._embeddings.embed_documents(texts)
        ids: list[str] = []
        for vec, text, meta in zip(vectors, texts, metadatas):
            self._items.append((vec, text, meta))
            ids.append(str(len(self._items) - 1))
        return ids

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        if not self._items:
            return []
        qv = self._embeddings.embed_query(query)
        scored = [
            Document(text=text, metadata=meta, score=self._cosine(qv, vec))
            for vec, text, meta in self._items
        ]
        scored.sort(key=lambda d: d.score or 0.0, reverse=True)
        return scored[:k]
