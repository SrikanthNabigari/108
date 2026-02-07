"""Chat endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import (
    get_app_config,
    get_current_user,
    get_db,
    get_redis,
)
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
    db: Annotated[object, Depends(get_db)],
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
        db: Database connection.

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

        # Load user's birth chart from database
        chart_query = """
            SELECT * FROM birth_charts WHERE user_id = $1
        """
        chart_row = await db.fetchrow(chart_query, str(current_user.id))

        # Load recent chat history
        history_query = """
            SELECT * FROM chat_messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 10
        """
        history_rows = await db.fetch(history_query, str(current_user.id))

        # Build context dict for Guide agent
        chart_context = {}
        if chart_row:
            chart_context = {
                "lagna_rashi": chart_row.get("lagna_rashi"),
                "moon_rashi": chart_row.get("moon_rashi"),
                "moon_nakshatra": chart_row.get("moon_nakshatra"),
                "birth_datetime": str(chart_row.get("birth_datetime")),
            }

        chart_context["chat_history"] = [
            {
                "role": row["role"],
                "content": row["message"],
                "timestamp": row["created_at"].isoformat(),
            }
            for row in history_rows
        ]

        # TODO: Call guide agent with context
        # For now, return placeholder response with structured data
        agent_response = (
            "Based on your chart, I can provide insights about "
            "your astrological patterns. How can I help you today?"
        )
        render_blocks = [
            {
                "type": "astrological_context",
                "data": chart_context,
            }
        ]

        # Save user message to database
        import uuid

        message_id = uuid.uuid4()
        await db.execute(
            """
            INSERT INTO chat_messages
            (id, user_id, role, message, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            """,
            str(message_id),
            str(current_user.id),
            "user",
            request.message,
        )

        # Save AI response
        response_id = uuid.uuid4()
        await db.execute(
            """
            INSERT INTO chat_messages
            (id, user_id, role, message, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            """,
            str(response_id),
            str(current_user.id),
            "assistant",
            agent_response,
        )

        # Increment daily usage counter
        await redis.incr(f"chat_usage:{current_user.id}:{current_user.subscription_tier}")

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
        ) from None


@router.get("/history")
async def get_chat_history(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[object, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Get paginated chat history.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
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

        # Query chat messages
        query = """
            SELECT *
            FROM chat_messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """

        rows = await db.fetch(query, str(current_user.id), limit, skip)

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM chat_messages WHERE user_id = $1"
        count_row = await db.fetchrow(count_query, str(current_user.id))
        total = count_row["total"] if count_row else 0

        messages = [
            {
                "id": row["id"],
                "role": row["role"],
                "message": row["message"],
                "created_at": row["created_at"].isoformat(),
            }
            for row in rows
        ]

        return {
            "messages": messages,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Failed to retrieve chat history for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history",
        ) from None


@router.get("/remaining")
async def get_remaining_messages(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    redis: Annotated[Any, Depends(get_redis)],
) -> dict[str, int | str]:
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
        ) from None
