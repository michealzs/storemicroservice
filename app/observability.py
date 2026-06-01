"""Tracing/observability wiring for Langfuse and LangSmith.

- LangSmith: configured entirely through environment variables that LangChain
  reads on its own (``LANGCHAIN_TRACING_V2``, ``LANGCHAIN_API_KEY``,
  ``LANGCHAIN_PROJECT``). We just make sure they are exported when set.
- Langfuse: attached as a LangChain callback handler.

``get_callbacks`` returns an empty list when nothing is configured, so callers
can always pass ``callbacks=get_callbacks()`` safely.
"""
from __future__ import annotations

import os

from app.config import Settings, get_settings


def configure_langsmith(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if settings.langchain_tracing_v2 and settings.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)


def get_callbacks(settings: Settings | None = None) -> list:
    settings = settings or get_settings()
    callbacks: list = []
    if settings.langfuse_configured:
        try:
            from langfuse.callback import CallbackHandler

            callbacks.append(
                CallbackHandler(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host,
                )
            )
        except Exception:  # pragma: no cover - missing optional dep
            pass
    return callbacks
