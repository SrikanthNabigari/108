"""FastAPI dependencies for the 108 Gateway."""

from __future__ import annotations

import json
import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from gateway.config import Settings
from gateway.models import UserContext

logger = logging.getLogger(__name__)

_settings_cache: Settings | None = None


async def get_settings() -> Settings:
    """
    Get cached settings singleton.

    Returns:
        Settings: Application settings loaded from environment.

    Raises:
        RuntimeError: If settings cannot be loaded.
    """
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = Settings()
    return _settings_cache


async def get_redis(request: Request) -> Redis:
    """
    Get Redis connection from application state.

    Args:
        request: FastAPI request object.

    Returns:
        Redis: Redis connection instance.

    Raises:
        RuntimeError: If Redis is not initialized in app state.
    """
    redis = getattr(request.app.state, "redis", None)
    if redis is None:
        raise RuntimeError("Redis not initialized")
    return redis


async def get_db(request: Request):
    """
    Get database connection from application state.

    Args:
        request: FastAPI request object.

    Returns:
        Database connection instance.

    Raises:
        RuntimeError: If database is not initialized in app state.
    """
    db = getattr(request.app.state, "db", None)
    if db is None:
        raise RuntimeError("Database not initialized")
    return db


async def get_current_user(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserContext:
    """
    Extract and verify JWT from Authorization header.

    Decodes the JWT token using the Supabase JWT secret and validates it.
    The user information is attached to request.state by the auth middleware.

    Args:
        request: FastAPI request object.
        settings: Application settings.

    Returns:
        UserContext: Authenticated user context.

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing.
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

    token = auth_header[7:]  # Remove "Bearer " prefix

    try:
        jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
        )
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

    user_context = getattr(request.state, "user", None)
    if user_context is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user_context


async def get_app_config(
    redis: Annotated[Redis, Depends(get_redis)],
) -> dict:
    """
    Load application configuration from Redis cache (with DB fallback).

    Attempts to load cached config from Redis first, then falls back to
    querying the database if not cached.

    Args:
        redis: Redis connection instance.

    Returns:
        dict: Application configuration dictionary.

    Raises:
        RuntimeError: If configuration cannot be loaded.
    """
    cache_key = "app_config:v1"

    # Try Redis cache first
    cached = await redis.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            logger.warning("Invalid cached config, falling back to DB")

    # TODO: Load from database if not in cache
    # Once database is set up, query the app_config table
    # and cache the result for 5 minutes
    raise RuntimeError("Configuration not available")
