"""Weaviate backend adapter (optional)."""
from __future__ import annotations

from app.config import Settings
from app.vectorstores.base import Document


class WeaviateStore:
    def __init__(self, settings: Settings, embeddings) -> None:
        import weaviate
        from langchain_weaviate import WeaviateVectorStore

        if not settings.weaviate_url:
            raise RuntimeError("WEAVIATE_URL is not configured")

        auth = None
        if settings.weaviate_api_key:
            from weaviate.classes.init import Auth

            auth = Auth.api_key(settings.weaviate_api_key)

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.weaviate_url,
            auth_credentials=auth,
        )
        self._store = WeaviateVectorStore(
            client=client,
            index_name=settings.vector_collection.capitalize(),
            text_key="text",
            embedding=embeddings,
        )

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        return self._store.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        results = self._store.similarity_search_with_score(query, k=k)
        return [
            Document(text=doc.page_content, metadata=doc.metadata, score=score)
            for doc, score in results
        ]
