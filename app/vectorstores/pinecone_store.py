"""Pinecone backend adapter (optional)."""
from __future__ import annotations

from app.config import Settings
from app.vectorstores.base import Document


class PineconeStore:
    def __init__(self, settings: Settings, embeddings) -> None:
        from langchain_pinecone import PineconeVectorStore
        from pinecone import Pinecone, ServerlessSpec

        if not settings.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is not configured")

        pc = Pinecone(api_key=settings.pinecone_api_key)
        existing = {idx["name"] for idx in pc.list_indexes()}
        if settings.pinecone_index not in existing:
            pc.create_index(
                name=settings.pinecone_index,
                dimension=settings.embedding_dimensions,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.pinecone_cloud, region=settings.pinecone_region
                ),
            )
        self._store = PineconeVectorStore(
            index_name=settings.pinecone_index,
            embedding=embeddings,
            pinecone_api_key=settings.pinecone_api_key,
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        return self._store.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        results = self._store.similarity_search_with_score(query, k=k)
        return [
            Document(text=doc.page_content, metadata=doc.metadata, score=score)
            for doc, score in results
        ]
