"""Chat endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user, get_redis
from gateway.middleware.rate_limiter import check_rate_limit, get_rate_limit_headers
from gateway.models import (
    ChatRequest,
    ChatResponse,
    UserContext,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    redis: Annotated[Any, Depends(get_redis)],
) -> ChatResponse:
    """
    Send a message to the guide agent.

    Checks rate limit, calls guide agent, saves to chat_messages, and returns
    response with render blocks.

    Args:
        request: Chat message request.
        current_user: Authenticated user context.
        config: Application configuration.
        redis: Redis connection instance.

    Returns:
        ChatResponse: Agent response with remaining message count.

    Raises:
        HTTPException: 401 if not authenticated, 429 if rate limited,
            500 if agent call fails.
    """
    try:
        # Check rate limit
        rate_limit_result = await check_rate_limit(
            str(current_user.id),
            current_user.subscription_tier,
            redis,
            config,
        )

        if not rate_limit_result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Reset at {rate_limit_result.reset_at}",
                headers=get_rate_limit_headers(rate_limit_result),
            )

        # TODO: Call guide agent
        # Call packages or external agent endpoint to process message
        # Format message with user context and chart data
        agent_response = "TODO: Agent response"
        render_blocks = []

        # TODO: Save to chat_messages table
        # Insert message and response into database

        return ChatResponse(
            message=agent_response,
            render_blocks=render_blocks,
            remaining_messages=rate_limit_result.remaining,
            access="full",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process chat message for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        ) from e


@router.get("/history")
async def get_chat_history(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Get paginated chat history.

    Args:
        current_user: Authenticated user context.
        skip: Number of messages to skip (pagination offset).
        limit: Number of messages to return (max 100).

    Returns:
        dict: Paginated chat messages with total count.

    Raises:
        HTTPException: 401 if not authenticated, 500 if query fails.
    """
    try:
        if limit > 100:
            limit = 100

        # TODO: Query chat_messages table
        # Select messages for current_user, ordered by created_at DESC
        # Apply skip and limit for pagination

        return {
            "messages": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Failed to retrieve chat history for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history",
        ) from e


@router.get("/remaining")
async def get_remaining_messages(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    redis: Annotated[Any, Depends(get_redis)],
) -> dict[str, int]:
    """
    Get remaining chat messages for today.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        redis: Redis connection instance.

    Returns:
        dict: Remaining and total message counts.

    Raises:
        HTTPException: 401 if not authenticated, 500 if check fails.
    """
    try:
        rate_limit_result = await check_rate_limit(
            str(current_user.id),
            current_user.subscription_tier,
            redis,
            config,
        )

        return {
            "remaining": rate_limit_result.remaining,
            "limit": rate_limit_result.limit,
            "reset_at": rate_limit_result.reset_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get remaining messages for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve message count",
        ) from e
