from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from .auth import (
    ACCESS_TOKEN_MINUTES,
    REFRESH_TOKEN_DAYS,
    constant_time_compare,
    create_access_token,
    create_preview_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    hmac_sha256_hex,
    verify_password,
    verify_preview_token,
)
from .celery_app import TASK_AI_JOB_RUN, TASK_PREVIEW_REQUEST, celery_app
from .config import settings
from .db import (
    AIJob,
    AsyncSessionLocal,
    Comment,
    JobStatus,
    Notification,
    PreviewSession,
    Project,
    RefreshToken,
    SessionToken,
    Task,
    Team,
    TeamMember,
    TeamRole,
    Tier,
    User,
    utcnow as db_utcnow,
)

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)

api_router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    refresh_token: Optional[str] = None


async def get_current_user(
    db=Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization")
    token = creds.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    from sqlalchemy import select

    res = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_team_role(
    team_id: uuid.UUID,
    user: User,
    db,
    allowed: set[TeamRole],
) -> TeamMember:
    from sqlalchemy import select

    res = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
    )
    tm = res.scalar_one_or_none()
    if not tm or tm.role not in allowed:
        raise HTTPException(status_code=403, detail="Forbidden")
    return tm


def forbid_if_guest(tm: TeamMember):
    if tm.role == TeamRole.guest:
        raise HTTPException(status_code=403, detail="Guest accounts are read-only")


# -----------------------------
# Auth
# -----------------------------

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    username: Optional[str] = Field(default=None, min_length=3, max_length=64)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


@api_router.post("/auth/register", response_model=TokenPair)
async def register(data: RegisterIn, db=Depends(get_db)):
    from sqlalchemy import select

    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    u = User(
        email=str(data.email),
        username=data.username,
        password_hash=hash_password(data.password),
        tier=Tier.Free,
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)

    access = create_access_token(str(u.id), u.tier)
    refresh = create_refresh_token()
    rt = RefreshToken(
        user_id=u.id,
        token_hash=hash_refresh_token(refresh),
        expires_at=db_utcnow() + timedelta(days=REFRESH_TOKEN_DAYS),
        revoked=False,
    )
    db.add(rt)
    await db.commit()

    return TokenPair(
        access_token=access,
        expires_in_seconds=ACCESS_TOKEN_MINUTES * 60,
        refresh_token=refresh,
    )


@api_router.post("/auth/login", response_model=TokenPair)
async def login(data: LoginIn, db=Depends(get_db)):
    from sqlalchemy import select

    res = await db.execute(select(User).where(User.email == str(data.email)))
    u = res.scalar_one_or_none()
    if not u or not u.password_hash or not verify_password(data.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    u.last_login = db_utcnow()
    await db.commit()

    access = create_access_token(str(u.id), u.tier)
    refresh = create_refresh_token()
    rt = RefreshToken(
        user_id=u.id,
        token_hash=hash_refresh_token(refresh),
        expires_at=db_utcnow() + timedelta(days=REFRESH_TOKEN_DAYS),
        revoked=False,
    )
    db.add(rt)
    await db.commit()

    return TokenPair(
        access_token=access,
        expires_in_seconds=ACCESS_TOKEN_MINUTES * 60,
        refresh_token=refresh,
    )


@api_router.post("/auth/refresh", response_model=TokenPair)
async def refresh(data: RefreshIn, db=Depends(get_db)):
    from sqlalchemy import select

    token_hash = hash_refresh_token(data.refresh_token)
    res = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = res.scalar_one_or_none()
    if not rt or rt.revoked or rt.expires_at < db_utcnow():
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    rt.revoked = True
    await db.commit()

    user_res = await db.execute(select(User).where(User.id == rt.user_id))
    u = user_res.scalar_one()

    access = create_access_token(str(u.id), u.tier)
    new_refresh = create_refresh_token()
    new_rt = RefreshToken(
        user_id=u.id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=db_utcnow() + timedelta(days=REFRESH_TOKEN_DAYS),
        revoked=False,
    )
    db.add(new_rt)
    await db.commit()

    return TokenPair(
        access_token=access,
        expires_in_seconds=ACCESS_TOKEN_MINUTES * 60,
        refresh_token=new_refresh,
    )


@api_router.post("/auth/logout")
async def logout(data: RefreshIn, db=Depends(get_db)):
    from sqlalchemy import select

    token_hash = hash_refresh_token(data.refresh_token)
    res = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = res.scalar_one_or_none()
    if rt:
        rt.revoked = True
        await db.commit()
    return {"ok": True}


class SessionTokenOut(BaseModel):
    token: str
    url: str
    expires_at: datetime


@api_router.post("/auth/session-token", response_model=SessionTokenOut)
async def create_session_token(user: User = Depends(get_current_user), db=Depends(get_db)):
    token = secrets.token_urlsafe(32)
    exp = db_utcnow() + timedelta(minutes=5)
    st = SessionToken(token=token, user_id=user.id, expires_at=exp, used=False)
    db.add(st)
    await db.commit()
    return SessionTokenOut(token=token, url=f"{settings.BASE_URL}/login/session/{token}", expires_at=exp)


class ExchangeIn(BaseModel):
    token: str


@api_router.post("/auth/session-token/exchange", response_model=TokenPair)
async def exchange_session_token(data: ExchangeIn, db=Depends(get_db)):
    from sqlalchemy import select

    res = await db.execute(select(SessionToken).where(SessionToken.token == data.token))
    st = res.scalar_one_or_none()
    if not st or st.used or st.expires_at < db_utcnow():
        raise HTTPException(status_code=401, detail="Invalid session token")
    st.used = True
    await db.commit()

    user_res = await db.execute(select(User).where(User.id == st.user_id))
    u = user_res.scalar_one()

    access = create_access_token(str(u.id), u.tier)
    return TokenPair(access_token=access, expires_in_seconds=ACCESS_TOKEN_MINUTES * 60)


# -----------------------------
# Teams
# -----------------------------

class TeamCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)


@api_router.post("/teams")
async def create_team(data: TeamCreateIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    t = Team(name=data.name)
    db.add(t)
    await db.commit()
    await db.refresh(t)

    tm = TeamMember(team_id=t.id, user_id=user.id, role=TeamRole.owner)
    db.add(tm)
    await db.commit()
    return {"id": str(t.id), "name": t.name, "created_at": t.created_at}


@api_router.get("/teams")
async def list_my_teams(user: User = Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import select

    res = await db.execute(
        select(Team, TeamMember.role)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .where(TeamMember.user_id == user.id)
    )
    out = []
    for team, role in res.all():
        out.append({"id": str(team.id), "name": team.name, "role": role.value})
    return out


class JoinTeamIn(BaseModel):
    team_id: uuid.UUID


@api_router.post("/teams/join")
async def join_team(data: JoinTeamIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import select

    if user.tier == Tier.Free:
        res = await db.execute(select(TeamMember).where(TeamMember.user_id == user.id))
        memberships = res.scalars().all()
        if len(memberships) >= 1:
            raise HTTPException(status_code=403, detail="Free accounts can join only one team.")

    team_res = await db.execute(select(Team).where(Team.id == data.team_id))
    team = team_res.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    role = TeamRole.guest if user.tier == Tier.Free else TeamRole.member
    tm = TeamMember(team_id=team.id, user_id=user.id, role=role)
    db.add(tm)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Already a team member")
    return {"ok": True, "team_id": str(team.id), "role": role.value}


# -----------------------------
# Projects / Tasks / Comments
# -----------------------------

class ProjectCreateIn(BaseModel):
    team_id: uuid.UUID
    name: str = Field(min_length=1, max_length=160)
    description: Optional[str] = None


@api_router.post("/projects")
async def create_project(data: ProjectCreateIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    tm = await require_team_role(
        data.team_id, user, db, allowed={TeamRole.owner, TeamRole.admin, TeamRole.member, TeamRole.guest}
    )
    forbid_if_guest(tm)

    p = Project(team_id=data.team_id, name=data.name, description=data.description)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return {"id": str(p.id), "team_id": str(p.team_id), "name": p.name, "description": p.description}


@api_router.get("/teams/{team_id}/projects")
async def list_projects(team_id: uuid.UUID, user: User = Depends(get_current_user), db=Depends(get_db)):
    await require_team_role(
        team_id, user, db, allowed={TeamRole.owner, TeamRole.admin, TeamRole.member, TeamRole.guest}
    )
    from sqlalchemy import select

    res = await db.execute(select(Project).where(Project.team_id == team_id).order_by(Project.created_at.desc()))
    return [{"id": str(p.id), "name": p.name, "description": p.description} for p in res.scalars().all()]


class TaskCreateIn(BaseModel):
    project_id: uuid.UUID
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


@api_router.post("/tasks")
async def create_task(data: TaskCreateIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import select

    proj_res = await db.execute(select(Project).where(Project.id == data.project_id))
    proj = proj_res.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    tm = await require_team_role(
        proj.team_id, user, db, allowed={TeamRole.owner, TeamRole.admin, TeamRole.member, TeamRole.guest}
    )
    forbid_if_guest(tm)

    t = Task(project_id=proj.id, title=data.title, description=data.description, created_by_user_id=user.id)
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return {"id": str(t.id), "project_id": str(t.project_id), "title": t.title}


class CommentCreateIn(BaseModel):
    task_id: uuid.UUID
    body: str = Field(min_length=1, max_length=10000)


@api_router.post("/comments")
async def create_comment(data: CommentCreateIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import select

    task_res = await db.execute(select(Task).where(Task.id == data.task_id))
    task = task_res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    proj_res = await db.execute(select(Project).where(Project.id == task.project_id))
    proj = proj_res.scalar_one()

    tm = await require_team_role(
        proj.team_id, user, db, allowed={TeamRole.owner, TeamRole.admin, TeamRole.member, TeamRole.guest}
    )
    forbid_if_guest(tm)

    c = Comment(task_id=task.id, user_id=user.id, body=data.body)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {"id": str(c.id), "task_id": str(c.task_id), "body": c.body, "created_at": c.created_at}


# -----------------------------
# Notifications
# -----------------------------

@api_router.get("/notifications")
async def list_notifications(user: User = Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import select

    res = await db.execute(
        select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(100)
    )
    notifs = res.scalars().all()
    return [
        {"id": str(n.id), "type": n.type, "data": n.data, "created_at": n.created_at, "read_at": n.read_at}
        for n in notifs
    ]


class MarkReadIn(BaseModel):
    notification_id: uuid.UUID


@api_router.post("/notifications/mark-read")
async def mark_notification_read(data: MarkReadIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import select

    res = await db.execute(
        select(Notification).where(Notification.id == data.notification_id, Notification.user_id == user.id)
    )
    n = res.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    n.read_at = db_utcnow()
    await db.commit()
    return {"ok": True}


# -----------------------------
# Preview (enqueue immediately)
# -----------------------------

class PreviewCreateIn(BaseModel):
    project_id: uuid.UUID
    team_id: uuid.UUID
    device_id: str = Field(min_length=1, max_length=128)


@api_router.post("/preview/request")
async def request_preview(data: PreviewCreateIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    tm = await require_team_role(
        data.team_id, user, db, allowed={TeamRole.owner, TeamRole.admin, TeamRole.member, TeamRole.guest}
    )
    if tm.role == TeamRole.guest:
        raise HTTPException(status_code=403, detail="Guests cannot generate previews")

    preview_id = secrets.token_urlsafe(16)

    ps = PreviewSession(
        preview_id=preview_id,
        user_id=user.id,
        team_id=data.team_id,
        project_id=data.project_id,
        device_id=data.device_id,
        status=JobStatus.queued,
        tier_snapshot=user.tier,
    )
    db.add(ps)
    await db.commit()

    preview_token = create_preview_token(preview_id=preview_id, user_id=str(user.id), device_id=data.device_id)

    # Enqueue immediately (explicit override)
    try:
        celery_app.send_task(
            TASK_PREVIEW_REQUEST,
            kwargs={
                "preview_id": preview_id,
                "preview_token": preview_token,
                "user_id": str(user.id),
                "team_id": str(data.team_id),
                "project_id": str(data.project_id),
                "device_id": data.device_id,
                "tier_snapshot": user.tier.value,
                "requested_at": ps.created_at.isoformat(),
                "schema_version": 1,
            },
            queue=settings.WORKER_PREVIEW_QUEUE,
        )
    except Exception as e:
        # Make failure visible and consistent
        ps.status = JobStatus.failed
        ps.error = f"enqueue_failed: {type(e).__name__}"
        await db.commit()
        logger.exception("Failed to enqueue preview task")
        raise HTTPException(status_code=503, detail="Preview queue unavailable")

    return {"preview_id": preview_id, "preview_token": preview_token, "status": ps.status.value}


class PreviewHeartbeatIn(BaseModel):
    project_id: uuid.UUID
    preview_token: str
    client_id: uuid.UUID
    last_event_at: datetime


@api_router.post("/preview/heartbeat")
async def preview_heartbeat(data: PreviewHeartbeatIn, db=Depends(get_db)):
    try:
        payload = verify_preview_token(data.preview_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid preview token")

    preview_id = payload.get("preview_id")
    if not preview_id:
        raise HTTPException(status_code=401, detail="Invalid preview token")

    from sqlalchemy import select

    res = await db.execute(select(PreviewSession).where(PreviewSession.preview_id == preview_id))
    ps = res.scalar_one_or_none()
    if not ps:
        raise HTTPException(status_code=404, detail="Preview not found")

    return {"ok": True, "preview_id": preview_id}


# -----------------------------
# AI Jobs (enqueue immediately)
# -----------------------------

class AIJobCreateIn(BaseModel):
    project_id: uuid.UUID
    selection: dict[str, Any] = Field(default_factory=dict)
    job_type: str = Field(min_length=1, max_length=64)
    team_id: Optional[uuid.UUID] = None


@api_router.post("/ai/jobs")
async def submit_ai_job(data: AIJobCreateIn, user: User = Depends(get_current_user), db=Depends(get_db)):
    team_id = data.team_id
    if team_id:
        tm = await require_team_role(
            team_id, user, db, allowed={TeamRole.owner, TeamRole.admin, TeamRole.member, TeamRole.guest}
        )
        if tm.role == TeamRole.guest:
            raise HTTPException(status_code=403, detail="Guests cannot run AI jobs")

    job = AIJob(
        user_id=user.id,
        team_id=team_id,
        project_id=data.project_id,
        status=JobStatus.queued,
        tier_snapshot=user.tier,
        job_type=data.job_type,
        params={"selection": data.selection},
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    try:
        celery_app.send_task(
            TASK_AI_JOB_RUN,
            kwargs={
                "job_id": str(job.id),
                "job_type": job.job_type,
                "user_id": str(user.id),
                "team_id": str(team_id) if team_id else None,
                "project_id": str(data.project_id),
                "tier_snapshot": user.tier.value,
                "selection": data.selection,
                "requested_at": job.created_at.isoformat(),
                "schema_version": 1,
            },
            queue=settings.WORKER_AI_QUEUE,
        )
    except Exception as e:
        job.status = JobStatus.failed
        job.error = f"enqueue_failed: {type(e).__name__}"
        await db.commit()
        logger.exception("Failed to enqueue AI job task")
        raise HTTPException(status_code=503, detail="AI queue unavailable")

    return {"id": str(job.id), "status": job.status.value}


# -----------------------------
# Billing
# -----------------------------

class StartCheckoutIn(BaseModel):
    tier: str  # "pro" | "premium"
    billing_cycle: str  # "monthly" | "yearly"


@api_router.post("/billing/start-checkout")
async def start_checkout(data: StartCheckoutIn, user: User = Depends(get_current_user)):
    if not settings.LZ_API_KEY or not settings.LZ_STORE_ID:
        raise HTTPException(status_code=503, detail="Billing not configured")

    tier = data.tier.lower()
    cycle = data.billing_cycle.lower()
    if tier not in {"pro", "premium"} or cycle not in {"monthly", "yearly"}:
        raise HTTPException(status_code=400, detail="Invalid tier or billing_cycle")

    variant_map = {
        ("pro", "monthly"): settings.LZ_PRO_MONTHLY_VARIANT_ID,
        ("pro", "yearly"): settings.LZ_PRO_YEARLY_VARIANT_ID,
        ("premium", "monthly"): settings.LZ_PREMIUM_MONTHLY_VARIANT_ID,
        ("premium", "yearly"): settings.LZ_PREMIUM_YEARLY_VARIANT_ID,
    }
    variant_id = variant_map.get((tier, cycle))
    if not variant_id:
        raise HTTPException(status_code=503, detail="Variant not configured")

    headers = {
        "Authorization": f"Bearer {settings.LZ_API_KEY}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }
    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "custom_price": None,
                "checkout_data": {"custom": {"user_id": str(user.id)}},
            },
            "relationships": {
                "store": {"data": {"type": "stores", "id": str(settings.LZ_STORE_ID)}},
                "variant": {"data": {"type": "variants", "id": str(variant_id)}},
            },
        }
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post("https://api.lemonsqueezy.com/v1/checkouts", headers=headers, json=payload)
        if r.status_code >= 400:
            logger.error("LemonSqueezy checkout error %s: %s", r.status_code, r.text)
            raise HTTPException(status_code=502, detail="Billing provider error")
        data = r.json()

    url = (
        data.get("data", {}).get("attributes", {}).get("url")
        or data.get("data", {}).get("attributes", {}).get("checkout_url")
    )
    if not url:
        raise HTTPException(status_code=502, detail="Billing provider response missing url")
    return {"checkout_url": url}


@api_router.post("/billing/webhook")
async def billing_webhook(request: Request, db=Depends(get_db)):
    raw = await request.body()
    sig = request.headers.get("X-Signature", "")
    expected = hmac_sha256_hex(settings.LZ_WEBHOOK_SECRET, raw)
    if not sig or not constant_time_compare(sig, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_name = payload.get("meta", {}).get("event_name") or payload.get("event_name")
    data = payload.get("data") or {}
    attributes = data.get("attributes") or {}
    custom_data = attributes.get("custom_data") or attributes.get("checkout_data", {}).get("custom") or {}
    user_id = custom_data.get("user_id")

    if not event_name or not user_id:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    from sqlalchemy import select

    res = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    variant_id = str(attributes.get("variant_id") or "")
    tier = None
    if variant_id in {str(settings.LZ_PRO_MONTHLY_VARIANT_ID), str(settings.LZ_PRO_YEARLY_VARIANT_ID)}:
        tier = Tier.Pro
    if variant_id in {str(settings.LZ_PREMIUM_MONTHLY_VARIANT_ID), str(settings.LZ_PREMIUM_YEARLY_VARIANT_ID)}:
        tier = Tier.Premium

    if event_name in {
        "subscription_cancelled",
        "subscription_expired",
        "subscription_paused",
        "subscription_payment_failed",
    }:
        if user.tier != Tier.Admin:
            user.tier = Tier.Free
    elif event_name in {
        "subscription_created",
        "subscription_updated",
        "subscription_resumed",
        "subscription_payment_recovered",
    }:
        if tier and user.tier != Tier.Admin:
            user.tier = tier

    await db.commit()
    return {"ok": True}
