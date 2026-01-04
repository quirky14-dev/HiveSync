from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from backend.app.config import settings
from backend.app.db import (
    AsyncSessionLocal,
    User,
    Tier,
    PreviewSession,
    AIJob,
    JobStatus,
    Worker,
    AuditLog,
    DeadLetter,
)
from backend.app.routers import get_current_user
from backend.app.celery_app import TASK_AI_JOB_RUN, TASK_PREVIEW_REQUEST, celery_app


router = APIRouter(prefix="/admin/observability", tags=["admin-observability"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def require_admin(user: User):
    if user.tier != Tier.Admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")


class SystemOverviewOut(BaseModel):
    users_total: int
    previews_queued: int
    previews_running: int
    ai_jobs_queued: int
    ai_jobs_running: int


@router.get("/overview", response_model=SystemOverviewOut)
async def system_overview(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    users_total = (await db.execute(select(func.count()).select_from(User))).scalar_one()

    previews_queued = (
        await db.execute(
            select(func.count()).select_from(PreviewSession).where(PreviewSession.status == JobStatus.queued)
        )
    ).scalar_one()

    previews_running = (
        await db.execute(
            select(func.count()).select_from(PreviewSession).where(PreviewSession.status == JobStatus.running)
        )
    ).scalar_one()

    ai_jobs_queued = (
        await db.execute(select(func.count()).select_from(AIJob).where(AIJob.status == JobStatus.queued))
    ).scalar_one()

    ai_jobs_running = (
        await db.execute(select(func.count()).select_from(AIJob).where(AIJob.status == JobStatus.running))
    ).scalar_one()

    return SystemOverviewOut(
        users_total=users_total,
        previews_queued=previews_queued,
        previews_running=previews_running,
        ai_jobs_queued=ai_jobs_queued,
        ai_jobs_running=ai_jobs_running,
    )


class PreviewOut(BaseModel):
    id: uuid.UUID
    preview_id: str
    status: JobStatus
    user_id: Optional[uuid.UUID]
    team_id: Optional[uuid.UUID]
    project_id: Optional[uuid.UUID]
    created_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]


@router.get("/previews", response_model=list[PreviewOut])
async def list_previews(
    status: Optional[JobStatus] = None,
    limit: int = Field(default=50, ge=1, le=500),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    q = select(PreviewSession).order_by(PreviewSession.created_at.desc()).limit(limit)
    if status:
        q = q.where(PreviewSession.status == status)

    res = await db.execute(q)
    previews = res.scalars().all()

    return [
        PreviewOut(
            id=p.id,
            preview_id=p.preview_id,
            status=p.status,
            user_id=p.user_id,
            team_id=p.team_id,
            project_id=p.project_id,
            created_at=p.created_at,
            completed_at=p.completed_at,
            error=p.error,
        )
        for p in previews
    ]


class AIJobOut(BaseModel):
    id: uuid.UUID
    status: JobStatus
    job_type: str
    user_id: Optional[uuid.UUID]
    team_id: Optional[uuid.UUID]
    project_id: Optional[uuid.UUID]
    created_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]


@router.get("/ai-jobs", response_model=list[AIJobOut])
async def list_ai_jobs(
    status: Optional[JobStatus] = None,
    limit: int = Field(default=50, ge=1, le=500),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    q = select(AIJob).order_by(AIJob.created_at.desc()).limit(limit)
    if status:
        q = q.where(AIJob.status == status)

    res = await db.execute(q)
    jobs = res.scalars().all()

    return [
        AIJobOut(
            id=j.id,
            status=j.status,
            job_type=j.job_type,
            user_id=j.user_id,
            team_id=j.team_id,
            project_id=j.project_id,
            created_at=j.created_at,
            completed_at=j.completed_at,
            error=j.error,
        )
        for j in jobs
    ]


class WorkerOut(BaseModel):
    id: uuid.UUID
    worker_id: str
    kind: str
    last_heartbeat_at: datetime
    metadata: dict


@router.get("/workers", response_model=list[WorkerOut])
async def list_workers(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    res = await db.execute(select(Worker).order_by(Worker.last_heartbeat_at.desc()))
    workers = res.scalars().all()

    return [
        WorkerOut(
            id=w.id,
            worker_id=w.worker_id,
            kind=w.kind,
            last_heartbeat_at=w.last_heartbeat_at,
            metadata=w.metadata,
        )
        for w in workers
    ]


class AuditLogOut(BaseModel):
    id: uuid.UUID
    event_type: str
    user_id: Optional[uuid.UUID]
    project_id: Optional[uuid.UUID]
    metadata: dict
    created_at: datetime


@router.get("/audit-logs", response_model=list[AuditLogOut])
async def list_audit_logs(
    since_minutes: int = Field(default=60, ge=1, le=1440),
    limit: int = Field(default=100, ge=1, le=1000),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    since = datetime.utcnow() - timedelta(minutes=since_minutes)

    res = await db.execute(
        select(AuditLog).where(AuditLog.created_at >= since).order_by(AuditLog.created_at.desc()).limit(limit)
    )
    logs = res.scalars().all()

    return [
        AuditLogOut(
            id=l.id,
            event_type=l.event_type,
            user_id=l.user_id,
            project_id=l.project_id,
            metadata=l.metadata,
            created_at=l.created_at,
        )
        for l in logs
    ]


# -----------------------------
# DLQ
# -----------------------------

class DeadLetterOut(BaseModel):
    id: uuid.UUID
    task_name: str
    queue: str
    attempts: int
    error_type: str
    error_message: str
    payload: dict
    preview_id: Optional[str]
    ai_job_id: Optional[uuid.UUID]
    created_at: datetime


@router.get("/dlq", response_model=list[DeadLetterOut])
async def list_dead_letters(
    limit: int = Field(default=100, ge=1, le=1000),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    res = await db.execute(select(DeadLetter).order_by(DeadLetter.created_at.desc()).limit(limit))
    rows = res.scalars().all()
    return [
        DeadLetterOut(
            id=r.id,
            task_name=r.task_name,
            queue=r.queue,
            attempts=r.attempts,
            error_type=r.error_type,
            error_message=r.error_message,
            payload=r.payload,
            preview_id=r.preview_id,
            ai_job_id=r.ai_job_id,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/dlq/{dlq_id}/requeue")
async def requeue_dead_letter(
    dlq_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    require_admin(user)

    res = await db.execute(select(DeadLetter).where(DeadLetter.id == dlq_id))
    dl = res.scalar_one_or_none()
    if not dl:
        raise HTTPException(status_code=404, detail="DLQ entry not found")

    # Requeue the original task with original payload onto its original queue
    celery_app.send_task(
        dl.task_name,
        kwargs=dl.payload,
        queue=dl.queue,
    )

    return {"ok": True, "requeued_task": dl.task_name, "queue": dl.queue, "dlq_id": str(dl.id)}
