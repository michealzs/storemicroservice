"""pgvector backend (primary), backed by langchain-postgres' PGVector.

Wraps the LangChain ``PGVector`` store in our common interface. Requires a
Postgres instance with the ``vector`` extension (see docker-compose).
"""
from __future__ import annotations

from app.config import Settings
from app.vectorstores.base import Document


class PgVectorStore:
    def __init__(self, settings: Settings, embeddings) -> None:
        from langchain_postgres import PGVector

        # langchain-postgres expects a psycopg (v3) connection string.
        conn = settings.database_url.replace("+asyncpg", "+psycopg")
        self._store = PGVector(
            embeddings=embeddings,
            collection_name=settings.vector_collection,
            connection=conn,
            use_jsonb=True,
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        return self._store.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        results = self._store.similarity_search_with_score(query, k=k)
        return [
            Document(text=doc.page_content, metadata=doc.metadata, score=score)
            for doc, score in results
        ]
