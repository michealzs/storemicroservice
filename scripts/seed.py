"""Seed sample categories and products. Usage: python -m scripts.seed"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.db import SessionLocal, init_models
from app.domain.models import Category, Product

CATEGORIES = [
    ("Electronics", "electronics"),
    ("Home", "home"),
    ("Outdoors", "outdoors"),
]

PRODUCTS = [
    ("Wireless Noise-Cancelling Headphones", "headphones", "electronics", 199.0, 149.0,
     "Over-ear Bluetooth headphones with active noise cancellation and 30h battery."),
    ("Smart LED Desk Lamp", "desk-lamp", "home", 49.0, 39.0,
     "Dimmable desk lamp with adjustable color temperature and USB charging port."),
    ("Insulated Stainless Steel Bottle", "water-bottle", "outdoors", 29.0, 0.0,
     "Keeps drinks cold 24h or hot 12h. Leak-proof 750ml bottle for hiking."),
    ("Mechanical Keyboard", "keyboard", "electronics", 119.0, 99.0,
     "Hot-swappable mechanical keyboard with tactile switches and RGB backlight."),
    ("Camping Hammock", "hammock", "outdoors", 59.0, 45.0,
     "Lightweight double parachute-nylon hammock with tree straps included."),
]


async def main() -> None:
    await init_models()
    async with SessionLocal() as session:
        cats: dict[str, Category] = {}
        for name, slug in CATEGORIES:
            cat = await session.scalar(select(Category).where(Category.slug == slug))
            if not cat:
                cat = Category(name=name, slug=slug, description=f"{name} products")
                session.add(cat)
                await session.flush()
            cats[slug] = cat

        for name, slug, cat_slug, price, discount, desc in PRODUCTS:
            exists = await session.scalar(select(Product).where(Product.slug == slug))
            if not exists:
                session.add(
                    Product(
                        name=name, slug=slug, description=desc, vendor="Acme",
                        price=price, discount_price=discount,
                        is_featured=discount > 0, category=cats[cat_slug],
                    )
                )
        await session.commit()
    print(f"Seeded {len(CATEGORIES)} categories and {len(PRODUCTS)} products.")


if __name__ == "__main__":
    asyncio.run(main())
