"""Authentication middleware for the 108 Gateway."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status

from gateway.config import Settings
from gateway.models import UserContext

logger = logging.getLogger(__name__)


@dataclass
class AuthMiddlewareConfig:
    """Configuration for authentication middleware."""

    supabase_jwt_secret: str
    supabase_service_key: str
    supabase_url: str


async def extract_bearer_token(request: Request) -> str:
    """
    Extract Bearer token from Authorization header.

    Args:
        request: FastAPI request object.

    Returns:
        str: The JWT token.

    Raises:
        HTTPException: 401 if token is missing or malformed.
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

    return auth_header[7:]  # Remove "Bearer " prefix


async def decode_jwt_token(
    token: str,
    jwt_secret: str,
) -> dict:
    """
    Decode JWT token using Supabase JWT secret.

    Args:
        token: JWT token string.
        jwt_secret: Supabase JWT secret for verification.

    Returns:
        dict: Decoded JWT payload.

    Raises:
        HTTPException: 401 if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
        )
        return payload
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


async def lookup_or_create_user(
    auth_id: str,
    email: str,
    db,
) -> UserContext:
    """
    Look up user in database by auth_id or create on first login.

    Args:
        auth_id: User UUID from Supabase auth.users.
        email: User email address.
        db: Database connection.

    Returns:
        UserContext: User context with subscription tier and metadata.

    Raises:
        HTTPException: 500 if database operation fails.
    """
    # TODO: Query users table by auth_id
    # If found, return UserContext with subscription_tier from database
    # If not found, create user with default free tier and return UserContext
    # Handle database errors appropriately
    raise NotImplementedError("Database integration required")


async def authenticate_request(
    request: Request,
    settings: Annotated[Settings, Depends(lambda: Settings())],
) -> UserContext | None:
    """
    Authenticate request by extracting and verifying JWT.

    Attaches user to request.state.user if authentication succeeds.

    Args:
        request: FastAPI request object.
        settings: Application settings.

    Returns:
        UserContext: Authenticated user context, or None if no auth header.

    Raises:
        HTTPException: 401 if token is invalid/expired.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    try:
        token = await extract_bearer_token(request)
        payload = await decode_jwt_token(token, settings.supabase_jwt_secret)

        auth_id = payload.get("sub")
        email = payload.get("email")

        if not auth_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # TODO: Integrate database connection
        # user_context = await lookup_or_create_user(auth_id, email, db)
        # request.state.user = user_context
        # return user_context
        raise NotImplementedError("Database integration required")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed",
        ) from e
