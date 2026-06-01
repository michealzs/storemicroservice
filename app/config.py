"""Central configuration. The only place environment variables are read.

Every other module receives a ``Settings`` instance (via :func:`get_settings`)
rather than reading ``os.environ`` directly.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    app_name: str = "AI Commerce Service"
    environment: str = "local"
    log_level: str = "INFO"

    # --- Database (SQLAlchemy async) ---
    # Default points at the docker-compose Postgres+pgvector service.
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    )

    # --- LLM provider ---
    # Provider for chat + embeddings. "openai" is the default; "anthropic" is
    # supported for chat. Missing keys degrade gracefully (see embeddings.py /
    # agents/graph.py) so the service still boots and non-LLM routes work.
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # --- Payments (Stripe). Optional; checkout works offline without it. ---
    stripe_secret_key: str | None = None

    # --- Vector store ---
    vector_backend: Literal["pgvector", "weaviate", "pinecone"] = "pgvector"
    vector_collection: str = "product_catalog"

    # Weaviate (optional)
    weaviate_url: str | None = None
    weaviate_api_key: str | None = None

    # Pinecone (optional)
    pinecone_api_key: str | None = None
    pinecone_index: str = "product-catalog"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # --- Observability ---
    # LangSmith is configured purely through env vars read by LangChain itself
    # (LANGCHAIN_TRACING_V2 / LANGCHAIN_API_KEY). We surface the toggle here so
    # /readyz can report it.
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "ai-commerce"

    # Langfuse (optional) — wired via callback handler in observability.py
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    @property
    def llm_configured(self) -> bool:
        if self.llm_provider == "openai":
            return bool(self.openai_api_key)
        return bool(self.anthropic_api_key)

    @property
    def langfuse_configured(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
