"""LangChain tools for the commerce shopping assistant."""
from __future__ import annotations

import json

from app.config import get_settings
from app.vectorstores import get_vector_store


def search_products_raw(query: str, k: int = 5) -> list[dict]:
    store = get_vector_store(get_settings())
    return [
        {"text": d.text, "metadata": d.metadata, "score": d.score}
        for d in store.similarity_search(query, k=k)
    ]


def build_tools() -> list:
    from langchain_core.tools import tool

    @tool
    def search_products(query: str) -> str:
        """Semantic search over the product catalog for items matching a shopper's need."""
        return json.dumps(search_products_raw(query))

    @tool
    def recommend(query: str) -> str:
        """Recommend products for an occasion, budget, or preference described in the query."""
        return json.dumps(search_products_raw(query, k=3))

    return [search_products, recommend]
