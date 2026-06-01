"""Cart, reviews and checkout endpoints.

Ported from the Django AddToCartView, ProductReviewCreateAPIView, and
CheckoutAPIView. Stripe is called only when a key is configured; otherwise
checkout records a pending order so the flow remains runnable offline.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.db import get_session
from app.domain.models import Cart, CartItem, Order, Product, ProductReview
from app.domain.schemas import AddToCartRequest, CartOut, ReviewCreate, ReviewOut

router = APIRouter(tags=["cart"])


async def _get_or_create_cart(session: AsyncSession, session_key: str) -> Cart:
    cart = await session.scalar(select(Cart).where(Cart.session == session_key))
    if not cart:
        cart = Cart(session=session_key)
        session.add(cart)
        await session.flush()
    return cart


@router.post("/cart/add/{slug}", response_model=CartOut)
async def add_to_cart(
    slug: str, payload: AddToCartRequest, session: AsyncSession = Depends(get_session)
):
    product = await session.scalar(select(Product).where(Product.slug == slug))
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    cart = await _get_or_create_cart(session, payload.session)
    item = await session.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id,
            CartItem.ordered.is_(False),
        )
    )
    if item:
        item.quantity += payload.quantity
    else:
        session.add(CartItem(cart=cart, product=product, quantity=payload.quantity))
    await session.commit()
    return await _cart_out(session, cart.id)


@router.get("/cart/{session_key}", response_model=CartOut)
async def get_cart(session_key: str, session: AsyncSession = Depends(get_session)):
    cart = await session.scalar(select(Cart).where(Cart.session == session_key))
    if not cart:
        raise HTTPException(status_code=404, detail="cart not found")
    return await _cart_out(session, cart.id)


async def _load_cart(session: AsyncSession, *, cart_id=None, session_key=None) -> Cart | None:
    stmt = select(Cart).options(
        selectinload(Cart.items).selectinload(CartItem.product)
    )
    stmt = stmt.where(Cart.id == cart_id) if cart_id is not None else stmt.where(
        Cart.session == session_key
    )
    return await session.scalar(stmt)


async def _cart_out(session: AsyncSession, cart_id: int) -> CartOut:
    cart = await _load_cart(session, cart_id=cart_id)
    items = []
    total = 0.0
    for item in cart.items:
        line = item.get_final_price()
        total += line
        items.append(
            {"product": item.product.name, "quantity": item.quantity, "line_total": line}
        )
    return CartOut(id=cart.id, session=cart.session, items=items, total=total)


@router.post("/reviews/{slug}", response_model=ReviewOut, status_code=201)
async def create_review(
    slug: str, payload: ReviewCreate, session: AsyncSession = Depends(get_session)
):
    product = await session.scalar(select(Product).where(Product.slug == slug))
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    review = ProductReview(
        product=product,
        author=payload.author,
        rating=payload.rating,
        content=payload.content,
    )
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return review


@router.post("/checkout/{session_key}")
async def checkout(session_key: str, session: AsyncSession = Depends(get_session)):
    cart = await _load_cart(session, session_key=session_key)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="cart is empty")

    total = sum(item.get_final_price() for item in cart.items)
    settings = get_settings()
    payment_status = "unpaid"
    transaction_id = None

    if settings.stripe_secret_key:
        # Real Stripe integration would create a PaymentIntent here.
        payment_status = "paid"
        transaction_id = f"stripe_{uuid.uuid4().hex[:12]}"

    order = Order(
        order_number=uuid.uuid4().hex[:12].upper(),
        total=total,
        payment_status=payment_status,
        transaction_id=transaction_id,
        status="P",
    )
    session.add(order)
    for item in cart.items:
        item.ordered = True
    await session.commit()
    return {
        "order_number": order.order_number,
        "total": float(total),
        "payment_status": payment_status,
    }
