"""FastAPI application entrypoint for the AI Commerce Service."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    routes_cart,
    routes_catalog,
    routes_chat,
    routes_health,
    routes_ingest,
)
from app.config import get_settings
from app.observability import configure_langsmith

settings = get_settings()
logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_langsmith(settings)
    try:
        from app.db import init_models

        await init_models()
    except Exception as exc:  # pragma: no cover
        logging.getLogger(__name__).warning("init_models skipped: %s", exc)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(routes_health.router)
app.include_router(routes_catalog.router)
app.include_router(routes_cart.router)
app.include_router(routes_ingest.router)
app.include_router(routes_chat.router)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"service": settings.app_name, "docs": "/docs"}
