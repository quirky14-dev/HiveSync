from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.config import settings
from backend.app.db import AIJob, JobStatus
from backend.common.dlq import write_dead_letter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hivesync.ai_worker")

celery_app = Celery(
    "hivesync_ai_worker",
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

WORKER_ID = f"ai-{uuid.uuid4()}"
MAX_RETRIES = 3
RETRY_DELAYS_SECONDS = [5, 20, 60]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@celery_app.task(name="hivesync.ai.run", bind=True, acks_late=True)
def run_ai_job(self, **payload: Any):
    job_id = payload.get("job_id")
    if not job_id:
        logger.error("Missing job_id in payload")
        return

    try:
        asyncio.run(_run_ai_job_async(job_id, payload))
    except Exception as exc:
        attempt = int(getattr(self.request, "retries", 0)) + 1
        if attempt <= MAX_RETRIES:
            delay = RETRY_DELAYS_SECONDS[min(attempt - 1, len(RETRY_DELAYS_SECONDS) - 1)]
            logger.exception("AIJob %s failed (attempt %s/%s), retrying in %ss", job_id, attempt, MAX_RETRIES, delay)
            raise self.retry(exc=exc, countdown=delay, max_retries=MAX_RETRIES)

        logger.exception("AIJob %s failed permanently after %s attempts", job_id, attempt)
        asyncio.run(_final_fail_to_dlq(job_id, payload, exc, attempts=attempt))
        celery_app.send_task(
            "hivesync.dlq.recorded",
            kwargs={"kind": "ai", "job_id": job_id},
            queue=settings.WORKER_DLQ_QUEUE,
        )


async def _run_ai_job_async(job_id: str, payload: dict[str, Any]):
    async with SessionLocal() as session:
        job = await _get_job(session, job_id)
        if not job:
            raise RuntimeError(f"AIJob not found: {job_id}")

        if job.status in {JobStatus.succeeded, JobStatus.failed, JobStatus.cancelled}:
            logger.info("AIJob %s already terminal (%s); skipping", job_id, job.status)
            return

        job.status = JobStatus.running
        await session.commit()

        # Replace with real AI execution later
        await asyncio.sleep(1)

        job.status = JobStatus.succeeded
        job.result = {
            "job_type": job.job_type,
            "summary": "AI job completed successfully",
            "selection": payload.get("selection"),
            "finished_at": utcnow().isoformat(),
        }
        job.completed_at = utcnow()
        await session.commit()


async def _final_fail_to_dlq(job_id: str, payload: dict[str, Any], exc: Exception, attempts: int) -> None:
    async with SessionLocal() as session:
        job = await _get_job(session, job_id)
        if job:
            job.status = JobStatus.failed
            job.error = f"{type(exc).__name__}: {exc}"
            job.completed_at = utcnow()
            await session.commit()

        await write_dead_letter(
            session,
            task_name="hivesync.ai.run",
            queue=settings.WORKER_AI_QUEUE,
            celery_task_id=None,
            attempts=attempts,
            error_type=type(exc).__name__,
            error_message=str(exc),
            payload=payload,
            ai_job_id=job.id if job else None,
        )


async def _get_job(session: AsyncSession, job_id: str) -> AIJob | None:
    # Accept string UUID
    try:
        uid = uuid.UUID(job_id)
    except Exception:
        uid = None

    if uid:
        res = await session.execute(select(AIJob).where(AIJob.id == uid))
    else:
        res = await session.execute(select(AIJob).where(AIJob.id == job_id))
    return res.scalar_one_or_none()
