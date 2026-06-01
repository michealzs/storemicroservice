"""Common vector-store interface shared by all backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class Document:
    text: str
    metadata: dict = field(default_factory=dict)
    score: float | None = None


@runtime_checkable
class VectorStore(Protocol):
    """Minimal surface every backend adapter implements."""

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> list[str]:
        ...

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        ...
