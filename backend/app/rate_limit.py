from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import redis.asyncio as redis

from .config import settings


@dataclass(frozen=True)
class LimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class RedisRateLimiter:
    def __init__(self, client: redis.Redis):
        self.client = client

    async def hit(self, key: str, limit: int, window_seconds: int) -> LimitResult:
        # Fixed window: INCR + EXPIRE
        now = int(time.time())
        window_key = f"rl:{key}:{now // window_seconds}"
        pipe = self.client.pipeline()
        pipe.incr(window_key, 1)
        pipe.ttl(window_key)
        count, ttl = await pipe.execute()
        if ttl == -1:
            await self.client.expire(window_key, window_seconds)
            ttl = window_seconds
        remaining = max(0, limit - int(count))
        allowed = int(count) <= limit
        retry = int(ttl) if not allowed else 0
        return LimitResult(allowed=allowed, remaining=remaining, retry_after_seconds=retry)
