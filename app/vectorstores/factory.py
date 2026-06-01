"""Select and construct the configured vector store.

Falls back to an in-memory store when the configured backend can't be built
(missing optional dependency, service down, or a non-Postgres test database),
so the app and tests always have a working RAG layer.
"""
from __future__ import annotations

import logging

from app.config import Settings, get_settings
from app.embeddings import get_embeddings
from app.vectorstores.base import VectorStore
from app.vectorstores.memory_store import MemoryVectorStore

logger = logging.getLogger(__name__)

_cache: dict[str, VectorStore] = {}


def build_vector_store(settings: Settings | None = None) -> VectorStore:
    settings = settings or get_settings()
    embeddings = get_embeddings(settings)
    backend = settings.vector_backend

    try:
        if backend == "pgvector":
            from app.vectorstores.pgvector_store import PgVectorStore

            return PgVectorStore(settings, embeddings)
        if backend == "weaviate":
            from app.vectorstores.weaviate_store import WeaviateStore

            return WeaviateStore(settings, embeddings)
        if backend == "pinecone":
            from app.vectorstores.pinecone_store import PineconeStore

            return PineconeStore(settings, embeddings)
    except Exception as exc:  # pragma: no cover - depends on external services
        logger.warning(
            "Vector backend '%s' unavailable (%s); using in-memory fallback.",
            backend,
            exc,
        )

    return MemoryVectorStore(embeddings)


def get_vector_store(settings: Settings | None = None) -> VectorStore:
    settings = settings or get_settings()
    key = settings.vector_backend
    if key not in _cache:
        _cache[key] = build_vector_store(settings)
    return _cache[key]


def reset_vector_store() -> None:
    """Test helper to drop the cached store."""
    _cache.clear()
