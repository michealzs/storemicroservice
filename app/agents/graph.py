"""LangGraph ReAct agent for the shopping assistant.

Real LangGraph agent when an LLM provider is configured; a deterministic
RAG-only fallback (search the catalog and summarise hits) otherwise, so /chat
works and tests pass without secrets.
"""
from __future__ import annotations

import json

from app.config import Settings, get_settings
from app.observability import configure_langsmith, get_callbacks

SYSTEM_PROMPT = (
    "You are a helpful shopping assistant for an online store. Use search_products "
    "and recommend to ground answers in the live catalog. Suggest specific products "
    "with prices and never invent items that are not in the search results."
)


class CommerceAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._graph = None
        if self.settings.llm_configured:
            try:
                self._graph = self._build_graph()
            except Exception:  # pragma: no cover
                self._graph = None

    def _build_graph(self):
        from langgraph.prebuilt import create_react_agent

        from app.agents.tools import build_tools

        configure_langsmith(self.settings)
        return create_react_agent(self._llm(), build_tools())

    def _llm(self):
        if self.settings.llm_provider == "deepseek":
            from langchain_deepseek import ChatDeepSeek

            return ChatDeepSeek(
                model=self.settings.chat_model,
                api_key=self.settings.deepseek_api_key,
            )
        if self.settings.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=self.settings.chat_model,
                api_key=self.settings.anthropic_api_key,
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.settings.chat_model, api_key=self.settings.openai_api_key
        )

    def run(self, message: str) -> dict:
        if self._graph is None:
            return self._fallback(message)
        result = self._graph.invoke(
            {"messages": [("system", SYSTEM_PROMPT), ("user", message)]},
            config={"callbacks": get_callbacks(self.settings)},
        )
        messages = result.get("messages", [])
        reply = messages[-1].content if messages else ""
        used = [
            m.name
            for m in messages
            if getattr(m, "type", "") == "tool" and getattr(m, "name", None)
        ]
        return {"reply": reply, "used_tools": sorted(set(used)), "sources": []}

    def _fallback(self, message: str) -> dict:
        from app.agents.tools import search_products_raw

        hits = search_products_raw(message, k=5)
        sources = [h["metadata"].get("slug", "") for h in hits]
        lines = [
            "LLM provider not configured — returning catalog matches. "
            "Set DEEPSEEK_API_KEY (or OPENAI_API_KEY/ANTHROPIC_API_KEY) for conversational recommendations."
        ]
        if hits:
            lines.append("Top matches:")
            for h in hits:
                lines.append(f"- {h['metadata'].get('name', '?')}: {h['text'][:160]}")
        else:
            lines.append("No products ingested yet — POST /ingest first.")
        return {
            "reply": "\n".join(lines),
            "used_tools": ["search_products"] if hits else [],
            "sources": sources,
        }


_agent: CommerceAgent | None = None


def get_agent() -> CommerceAgent:
    global _agent
    if _agent is None:
        _agent = CommerceAgent()
    return _agent


def reset_agent() -> None:
    global _agent
    _agent = None
