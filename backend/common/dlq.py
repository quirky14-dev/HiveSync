from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db import DeadLetter


async def write_dead_letter(
    session: AsyncSession,
    *,
    task_name: str,
    queue: str,
    celery_task_id: Optional[str],
    attempts: int,
    error_type: str,
    error_message: str,
    payload: dict[str, Any],
    preview_id: str | None = None,
    ai_job_id=None,
) -> DeadLetter:
    dl = DeadLetter(
        task_name=task_name,
        queue=queue,
        celery_task_id=celery_task_id,
        attempts=attempts,
        error_type=error_type,
        error_message=error_message,
        payload=payload,
        preview_id=preview_id,
        ai_job_id=ai_job_id,
    )
    session.add(dl)
    await session.commit()
    await session.refresh(dl)
    return dl
