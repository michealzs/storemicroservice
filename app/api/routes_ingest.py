"""Embed the product catalog into the vector store for RAG."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.domain.models import Product
from app.domain.schemas import IngestResponse
from app.vectorstores import get_vector_store

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
async def ingest_catalog(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).where(Product.is_active.is_(True)))
    products = list(result.scalars())

    texts = [
        f"{p.name} by {p.vendor or 'unknown'} — ${float(p.price):.2f}. {p.description}"
        for p in products
    ]
    metadatas = [{"slug": p.slug, "name": p.name, "price": float(p.price)} for p in products]
    if texts:
        get_vector_store().add_texts(texts=texts, metadatas=metadatas)
    return IngestResponse(products_indexed=len(texts))
