from __future__ import annotations

from datetime import datetime, timedelta, timezone

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.config import settings
from backend.app.db import (
    Worker,
    PreviewSession,
    AIJob,
    JobStatus,
)

celery = Celery(
    "hivesync_recovery",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

STALE_WORKER_SECONDS = 60
STUCK_JOB_MINUTES = 10


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@celery.task(name="hivesync.recovery.sweep")
def recovery_sweep():
    import asyncio
    asyncio.run(_recovery_async())


async def _recovery_async():
    async with SessionLocal() as session:
        now = utcnow()

        # ---- stale workers
        stale_before = now - timedelta(seconds=STALE_WORKER_SECONDS)
        res = await session.execute(
            select(Worker).where(Worker.last_heartbeat_at < stale_before)
        )
        for w in res.scalars().all():
            w.metadata = {**(w.metadata or {}), "stale": True}
        await session.commit()

        # ---- stuck previews
        stuck_before = now - timedelta(minutes=STUCK_JOB_MINUTES)
        res = await session.execute(
            select(PreviewSession).where(
                PreviewSession.status == JobStatus.running,
                PreviewSession.created_at < stuck_before,
            )
        )
        for p in res.scalars().all():
            p.status = JobStatus.failed
            p.error = "stuck_timeout"
            p.completed_at = now

        # ---- stuck AI jobs
        res = await session.execute(
            select(AIJob).where(
                AIJob.status == JobStatus.running,
                AIJob.created_at < stuck_before,
            )
        )
        for j in res.scalars().all():
            j.status = JobStatus.failed
            j.error = "stuck_timeout"
            j.completed_at = now

        await session.commit()
