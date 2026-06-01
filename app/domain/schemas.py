"""Pydantic schemas for the commerce API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    name: str
    slug: str
    vendor: str
    description: str
    price: float
    discount_price: float
    is_active: bool
    is_featured: bool

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str = ""
    vendor: str = ""
    price: float
    discount_price: float = 0
    is_featured: bool = False
    category_slug: str | None = None


class ReviewCreate(BaseModel):
    author: str = "anonymous"
    rating: int = Field(5, ge=1, le=5)
    content: str = ""


class ReviewOut(BaseModel):
    id: int
    author: str
    rating: int
    content: str

    model_config = {"from_attributes": True}


class AddToCartRequest(BaseModel):
    session: str
    quantity: int = Field(1, ge=1)


class CartOut(BaseModel):
    id: int
    session: str
    items: list[dict]
    total: float


class ChatRequest(BaseModel):
    message: str = Field(..., examples=["Recommend a gift under $50"])
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    used_tools: list[str] = []
    sources: list[str] = []


class IngestResponse(BaseModel):
    products_indexed: int
