from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from celery import Celery
from celery.exceptions import Retry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.config import settings
from backend.app.db import PreviewSession, JobStatus
from backend.common.dlq import write_dead_letter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hivesync.preview_worker")

celery_app = Celery(
    "hivesync_preview_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

WORKER_ID = f"preview-{uuid.uuid4()}"
MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = [5, 20, 60]  # deterministic backoff


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@celery_app.task(name="hivesync.preview.request", bind=True, acks_late=True)
def run_preview(self, **payload: Any):
    preview_id = payload.get("preview_id")
    if not preview_id:
        logger.error("Missing preview_id in payload")
        return

    try:
        asyncio.run(_run_preview_async(preview_id, payload))
    except Exception as exc:
        # Retry unless this was the last attempt
        attempt = int(getattr(self.request, "retries", 0)) + 1
        if attempt <= MAX_RETRIES:
            delay = RETRY_DELAYS_SECONDS[min(attempt - 1, len(RETRY_DELAYS_SECONDS) - 1)]
            logger.exception("Preview %s failed (attempt %s/%s), retrying in %ss", preview_id, attempt, MAX_RETRIES, delay)
            raise self.retry(exc=exc, countdown=delay, max_retries=MAX_RETRIES)

        # Final failure -> DLQ + mark failed
        logger.exception("Preview %s failed permanently after %s attempts", preview_id, attempt)
        asyncio.run(_final_fail_to_dlq(preview_id, payload, exc, attempts=attempt))
        # Also emit to DLQ queue (optional consumer)
        celery_app.send_task(
            "hivesync.dlq.recorded",
            kwargs={"kind": "preview", "preview_id": preview_id},
            queue=settings.WORKER_DLQ_QUEUE,
        )


async def _run_preview_async(preview_id: str, payload: dict[str, Any]):
    async with SessionLocal() as session:
        ps = await _get_preview_session(session, preview_id)
        if not ps:
            raise RuntimeError(f"PreviewSession not found: {preview_id}")

        # idempotence: if already succeeded/failed, don't redo
        if ps.status in {JobStatus.succeeded, JobStatus.failed, JobStatus.cancelled}:
            logger.info("Preview %s already terminal (%s); skipping", preview_id, ps.status)
            return

        ps.status = JobStatus.running
        await session.commit()

        # Replace these sleeps with real preview build/stream logic later
        await asyncio.sleep(1)
        await asyncio.sleep(1)

        ps.status = JobStatus.succeeded
        ps.completed_at = utcnow()
        await session.commit()


async def _final_fail_to_dlq(preview_id: str, payload: dict[str, Any], exc: Exception, attempts: int) -> None:
    async with SessionLocal() as session:
        ps = await _get_preview_session(session, preview_id)
        if ps:
            ps.status = JobStatus.failed
            ps.error = f"{type(exc).__name__}: {exc}"
            ps.completed_at = utcnow()
            await session.commit()

        await write_dead_letter(
            session,
            task_name="hivesync.preview.request",
            queue=settings.WORKER_PREVIEW_QUEUE,
            celery_task_id=None,
            attempts=attempts,
            error_type=type(exc).__name__,
            error_message=str(exc),
            payload=payload,
            preview_id=preview_id,
        )


async def _get_preview_session(session: AsyncSession, preview_id: str) -> PreviewSession | None:
    res = await session.execute(select(PreviewSession).where(PreviewSession.preview_id == preview_id))
    return res.scalar_one_or_none()
