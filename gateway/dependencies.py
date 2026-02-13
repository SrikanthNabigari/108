"""FastAPI dependencies for the 108 Gateway."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWKClient

from gateway.config import Settings
from gateway.models import SubscriptionTier, UserContext

logger = logging.getLogger(__name__)

_settings_cache: Settings | None = None
_jwks_client: PyJWKClient | None = None


async def get_settings() -> Settings:
    """Get cached settings singleton."""
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = Settings()
    return _settings_cache


def _get_jwks_client(supabase_url: str) -> PyJWKClient:
    """Get or create cached JWKS client for Supabase auth."""
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        logger.info(f"JWKS client initialized: {jwks_url}")
    return _jwks_client


async def get_redis(request: Request) -> Any:
    """Get Redis connection from app state. Returns None if unavailable."""
    return getattr(request.app.state, "redis", None)


async def get_db(request: Request):
    """Get database pool from application state."""
    db = getattr(request.app.state, "db", None)
    if db is None:
        raise RuntimeError("Database not initialized")
    return db


def _decode_token(token: str, settings: Settings) -> dict:
    """Decode JWT using JWKS (ES256) with HS256 fallback."""
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "")

    if alg in ("ES256", "RS256"):
        # Use JWKS public key verification
        jwks_client = _get_jwks_client(settings.supabase_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=[alg],
            options={"verify_aud": False},
        )
    else:
        # Fallback to HS256 with JWT secret
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )


async def get_current_user(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserContext:
    """
    Extract JWT, decode it, look up (or auto-create) user in DB, return UserContext.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = auth_header[7:]

    try:
        payload = _decode_token(token, settings)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e

    # Extract Supabase user id from the `sub` claim
    auth_id = payload.get("sub")
    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing sub claim",
        )

    # Look up user by auth_id in database
    db = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    try:
        row = await db.fetchrow(
            "SELECT * FROM public.users WHERE auth_id = $1",
            auth_id,
        )
    except Exception as db_err:
        logger.error(f"DB query failed: {db_err!r}, auth_id={auth_id}")
        logger.error(f"DB pool: {db}, type: {type(db)}")
        raise

    if row is None:
        # First-login provisioning: auto-create user row
        email = payload.get("email", "")
        phone = payload.get("phone", "")
        new_id = uuid.uuid4()

        await db.execute(
            """
            INSERT INTO public.users (id, auth_id, email, phone, subscription_tier, created_at, updated_at)
            VALUES ($1, $2, $3, $4, 'free', NOW(), NOW())
            """,
            new_id,
            auth_id,
            email,
            phone,
        )

        # Also provision a credit wallet
        await db.execute(
            "INSERT INTO public.credit_wallets (user_id, balance) VALUES ($1, 0)",
            new_id,
        )

        row = await db.fetchrow("SELECT * FROM public.users WHERE id = $1", new_id)

    user_context = UserContext(
        id=row["id"],
        auth_id=str(row["auth_id"]),
        email=row.get("email") or "",
        phone=row.get("phone"),
        name=row.get("name"),
        subscription_tier=SubscriptionTier(row.get("subscription_tier", "free")),
    )

    # Override subscription tier for local testing
    if settings.env == "development" and settings.dev_tier != "free":
        user_context = UserContext(
            id=user_context.id,
            auth_id=user_context.auth_id,
            email=user_context.email,
            phone=user_context.phone,
            name=user_context.name,
            subscription_tier=SubscriptionTier(settings.dev_tier),
        )

    return user_context


async def get_app_config(request: Request) -> dict:
    """Load app config from Redis cache, falling back to app.state.config."""
    redis = getattr(request.app.state, "redis", None)

    if redis is not None:
        try:
            cached = await redis.get("app_config:v1")
            if cached:
                return json.loads(cached)
        except Exception:
            logger.warning("Failed to read config from Redis, using in-memory")

    # Fallback to in-memory config set during startup
    config = getattr(request.app.state, "config", None)
    if config:
        return config

    # Ultimate fallback
    from gateway.main import DEFAULT_APP_CONFIG

    return DEFAULT_APP_CONFIG
