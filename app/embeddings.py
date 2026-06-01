"""Embedding provider with a deterministic offline fallback.

When ``OPENAI_API_KEY`` is configured we use real OpenAI embeddings. Otherwise
we fall back to a deterministic hash-based embedding so the service (and the
test suite) runs end-to-end with zero secrets. The fallback is *not* good for
real semantic search, but keeps every code path exercised.
"""
from __future__ import annotations

import hashlib
import math

from app.config import Settings, get_settings


class FakeDeterministicEmbeddings:
    """LangChain-compatible embeddings: deterministic, offline, normalized."""

    def __init__(self, dimensions: int = 1536) -> None:
        self.dimensions = dimensions

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        # Spread token hashes across the vector for a stable pseudo-embedding.
        for token in text.lower().split() or [text.lower()]:
            h = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(0, len(h), 2):
                idx = (h[i] << 8 | h[i + 1]) % self.dimensions
                vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


_cached_embeddings = None


def get_embeddings(settings: Settings | None = None):
    """Return an embeddings object. Real OpenAI when keyed, fake otherwise."""
    global _cached_embeddings
    if _cached_embeddings is not None:
        return _cached_embeddings
    settings = settings or get_settings()
    if settings.llm_provider == "openai" and settings.openai_api_key:
        try:
            from langchain_openai import OpenAIEmbeddings

            _cached_embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                api_key=settings.openai_api_key,
                dimensions=settings.embedding_dimensions,
            )
            return _cached_embeddings
        except Exception:  # pragma: no cover - missing optional dep
            pass
    _cached_embeddings = FakeDeterministicEmbeddings(
        dimensions=settings.embedding_dimensions
    )
    return _cached_embeddings
