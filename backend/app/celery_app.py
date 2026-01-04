from __future__ import annotations

from celery import Celery

from .config import settings

# Celery application (core emits tasks; workers consume later)
celery_app = Celery(
    "hivesync",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Stable task names emitted by backend/core (workers must implement these)
TASK_PREVIEW_REQUEST = "hivesync.preview.request"
TASK_AI_JOB_RUN = "hivesync.ai.run"

# Minimal, explicit defaults
celery_app.conf.update(
    task_default_queue=settings.WORKER_AI_QUEUE,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "recovery-sweep-every-minute": {
        "task": "hivesync.recovery.sweep",
        "schedule": 60.0,
    }
}