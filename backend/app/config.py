from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    PORT: int = 4000
    BASE_URL: str = "http://localhost:4000"

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "hivesync"
    POSTGRES_USER: str = "hivesync"
    POSTGRES_PASSWORD: str = "REPLACE_ME"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    API_TOKEN_PEPPER: str = "REPLACE_ME_WITH_LONG_RANDOM_STRING"
    JWT_SECRET: str = "REPLACE_ME_WITH_LONG_RANDOM_STRING"
    SESSION_SECRET: str = "REPLACE_ME_FOR_BROWSER_SESSIONS"
    DEVICE_TOKEN_SECRET: str = "REPLACE_ME_WITH_LONG_RANDOM_STRING"
    WORKER_CALLBACK_SECRET: str = "REPLACE_ME_WITH_LONG_RANDOM_STRING"
    PREVIEW_TOKEN_SECRET: str = "REPLACE_ME_WITH_LONG_RANDOM_STRING"
    PREVIEW_DEVICE_CONTEXT_SECRET: str = "REPLACE_ME"

    AUTH_EMAIL_ENABLED: bool = True
    AUTH_GOOGLE_CLIENT_ID: Optional[str] = None
    AUTH_APPLE_CLIENT_ID: Optional[str] = None
    AUTH_APPLE_TEAM_ID: Optional[str] = None
    AUTH_APPLE_KEY_ID: Optional[str] = None
    AUTH_APPLE_PRIVATE_KEY: Optional[str] = None

    R2_BUCKET: Optional[str] = None
    R2_ACCESS_KEY: Optional[str] = None
    R2_SECRET_KEY: Optional[str] = None
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ENDPOINT: Optional[str] = None
    R2_PUBLIC_BASE_URL: Optional[str] = None

    LZ_API_KEY: Optional[str] = None
    LZ_STORE_ID: Optional[str] = None
    LZ_WEBHOOK_SECRET: str = "REPLACE_ME"
    LZ_PRO_MONTHLY_VARIANT_ID: Optional[str] = None
    LZ_PRO_YEARLY_VARIANT_ID: Optional[str] = None
    LZ_PREMIUM_MONTHLY_VARIANT_ID: Optional[str] = None
    LZ_PREMIUM_YEARLY_VARIANT_ID: Optional[str] = None

    WORKER_PREVIEW_QUEUE: str = "preview_tasks"
    WORKER_AI_QUEUE: str = "ai_tasks"
    WORKER_MAP_QUEUE: str = "map_tasks"
    WORKER_BILLING_QUEUE: str = "billing_tasks"
    WORKER_DELETION_QUEUE: str = "deletion_tasks"

    # NEW: DLQ queue (optional). Tasks exceeding retries will be persisted to DB
    # and also emitted here for optional manual consumers.
    WORKER_DLQ_QUEUE: str = "dlq_tasks"

    LOG_LEVEL: str = "info"
    SENTRY_DSN: Optional[str] = None

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


settings = Settings()
