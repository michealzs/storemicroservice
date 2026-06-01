"""Test fixtures: in-memory sqlite DB + httpx client, no external services."""
from __future__ import annotations

import os

import pytest
import pytest_asyncio

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["VECTOR_BACKEND"] = "pgvector"  # falls back to in-memory store
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("ANTHROPIC_API_KEY", None)


@pytest_asyncio.fixture
async def client():
    from httpx import ASGITransport, AsyncClient

    from app.db import init_models
    from app.main import app
    from app.vectorstores import reset_vector_store

    reset_vector_store()
    await init_models()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def seeded_client(client):
    """Client with a couple of products created via the API."""
    await client.post(
        "/products",
        json={
            "name": "Wireless Headphones", "slug": "headphones",
            "description": "Noise cancelling over-ear bluetooth headphones",
            "vendor": "Acme", "price": 199.0, "discount_price": 149.0,
            "is_featured": True,
        },
    )
    await client.post(
        "/products",
        json={
            "name": "Water Bottle", "slug": "water-bottle",
            "description": "Insulated stainless steel bottle for hiking",
            "vendor": "Acme", "price": 29.0,
        },
    )
    return client


@pytest.fixture(autouse=True)
def _reset_agent():
    from app.agents import reset_agent

    reset_agent()
    yield
    reset_agent()
