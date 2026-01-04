from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError

from .config import settings
from .db import Tier

ph = PasswordHasher(time_cost=2, memory_cost=102400, parallelism=8, hash_len=32, salt_len=16)

ACCESS_TOKEN_MINUTES = 15  # ambiguity_resolution Q3.1
REFRESH_TOKEN_DAYS = 30


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def _jwt_encode(payload: dict[str, Any], secret: str) -> str:
    return jwt.encode(payload, secret, algorithm="HS256")


def _jwt_decode(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])


def create_access_token(user_id: str, tier: Tier) -> str:
    now = utcnow()
    payload = {
        "sub": user_id,
        "tier": tier.value,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_MINUTES)).timestamp()),
        "type": "access",
        "jti": secrets.token_urlsafe(16),
    }
    return _jwt_encode(payload, settings.JWT_SECRET)


def create_refresh_token() -> str:
    # opaque, stored hashed in DB
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    # peppered hash so DB leak doesn't reveal tokens
    m = hashlib.sha256()
    m.update(settings.API_TOKEN_PEPPER.encode("utf-8"))
    m.update(token.encode("utf-8"))
    return m.hexdigest()


def decode_access_token(token: str) -> dict[str, Any]:
    payload = _jwt_decode(token, settings.JWT_SECRET)
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload


def create_preview_token(preview_id: str, user_id: str, device_id: str, expires_in_seconds: int = 900) -> str:
    # ambiguity_resolution Q3.3 => JWT; fields include preview_id, user_id, expires_at, device_id
    now = utcnow()
    exp = now + timedelta(seconds=expires_in_seconds)
    payload = {
        "preview_id": preview_id,
        "user_id": user_id,
        "device_id": device_id,
        "expires_at": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "preview",
        "jti": secrets.token_urlsafe(12),
    }
    return _jwt_encode(payload, settings.PREVIEW_TOKEN_SECRET)


def verify_preview_token(token: str) -> dict[str, Any]:
    payload = _jwt_decode(token, settings.PREVIEW_TOKEN_SECRET)
    if payload.get("type") != "preview":
        raise JWTError("Invalid token type")
    return payload


def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def hmac_sha256_hex(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
