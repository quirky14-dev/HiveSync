from __future__ import annotations
from backend.observability_admin.router import router as observability_admin_router

import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routers import api_router
#from .redis import get_redis_client


def configure_logging() -> None:
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    # Ensure noisy loggers are tamed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    r = redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = r
    try:
        yield
    finally:
        await r.aclose()


app = FastAPI(title="HiveSync Backend (core)", version="0.1.0", lifespan=lifespan)

# CORS: permissive by default for local dev; tighten in deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(observability_admin_router)


@app.get("/health")
async def health():
    return {"ok": True, "service": "hivesync-backend", "slice": "core"}
