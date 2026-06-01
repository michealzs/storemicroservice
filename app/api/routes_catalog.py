"""Catalog endpoints: products, categories, featured, search.

Ported from the Django store views (ActiveProductListView, ProductDetailAPI,
FeaturedProductListView, CategoryProductListView, SearchResultsView).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.domain.models import Category, Product
from app.domain.schemas import CategoryOut, ProductCreate, ProductOut

router = APIRouter(tags=["catalog"])


@router.get("/products", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product).where(Product.is_active.is_(True)).order_by(Product.created_at.desc())
    )
    return list(result.scalars())


@router.get("/products/{slug}", response_model=ProductOut)
async def product_detail(slug: str, session: AsyncSession = Depends(get_session)):
    product = await session.scalar(select(Product).where(Product.slug == slug))
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return product


@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(payload: ProductCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.scalar(select(Product).where(Product.slug == payload.slug))
    if exists:
        raise HTTPException(status_code=409, detail="slug already exists")
    category = None
    if payload.category_slug:
        category = await session.scalar(
            select(Category).where(Category.slug == payload.category_slug)
        )
    product = Product(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        vendor=payload.vendor,
        price=payload.price,
        discount_price=payload.discount_price,
        is_featured=payload.is_featured,
        category=category,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.get("/featured-products", response_model=list[ProductOut])
async def featured_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product).where(
            Product.is_active.is_(True), Product.is_featured.is_(True)
        )
    )
    return list(result.scalars())


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category).order_by(Category.name))
    return list(result.scalars())


@router.get("/category/{slug}", response_model=list[ProductOut])
async def category_products(slug: str, session: AsyncSession = Depends(get_session)):
    category = await session.scalar(select(Category).where(Category.slug == slug))
    if not category:
        raise HTTPException(status_code=404, detail="category not found")
    result = await session.execute(
        select(Product).where(
            Product.category_id == category.id, Product.is_active.is_(True)
        )
    )
    return list(result.scalars())


@router.get("/search", response_model=list[ProductOut])
async def search(q: str, session: AsyncSession = Depends(get_session)):
    like = f"%{q}%"
    result = await session.execute(
        select(Product).where(
            Product.is_active.is_(True),
            or_(Product.name.ilike(like), Product.description.ilike(like)),
        )
    )
    return list(result.scalars())
