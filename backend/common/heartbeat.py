from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db import Worker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def heartbeat(
    session: AsyncSession,
    *,
    worker_id: str,
    kind: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    res = await session.execute(
        select(Worker).where(Worker.worker_id == worker_id)
    )
    w = res.scalar_one_or_none()
    if not w:
        w = Worker(
            worker_id=worker_id,
            kind=kind,
            last_heartbeat_at=utcnow(),
            metadata=metadata or {},
        )
        session.add(w)
    else:
        w.last_heartbeat_at = utcnow()
        if metadata is not None:
            w.metadata = metadata
    await session.commit()
