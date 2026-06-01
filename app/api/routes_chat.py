"""Conversational endpoint backed by the LangGraph agent."""
from __future__ import annotations

from fastapi import APIRouter

from app.agents import get_agent
from app.domain.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    result = get_agent().run(payload.message)
    return ChatResponse(**result)
