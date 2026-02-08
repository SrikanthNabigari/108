"""Chat endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
import uuid
from datetime import datetime, timedelta
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
from gateway.models import (
    ChatRequest,
    UserContext,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _check_chat_rate_limit(
    user_id: str,
    tier: str,
    redis: Any,
    config: dict,
) -> dict[str, Any]:
    """Check rate limit, returning remaining count. Works without Redis."""
    chat_limits = config.get("chat_limits", {})
    limit = chat_limits.get(tier, 5)

    # Unlimited
    if limit == -1:
        return {"allowed": True, "remaining": -1, "limit": -1}

    if redis is None:
        # No Redis — allow but can't track accurately
        return {"allowed": True, "remaining": limit, "limit": limit}

    try:
        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")
        rate_key = f"rate:{user_id}:{date_str}"

        current = await redis.incr(rate_key)
        await redis.expire(rate_key, 86400)

        remaining = max(0, limit - current)
        return {"allowed": current <= limit, "remaining": remaining, "limit": limit}
    except Exception as e:
        logger.warning(f"Rate limit check failed: {e}")
        return {"allowed": True, "remaining": limit, "limit": limit}


@router.post("/")
async def send_message(
    request: ChatRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    redis: Annotated[Any, Depends(get_redis)],
    db: Annotated[object, Depends(get_db)],
) -> dict[str, Any]:
    """Send a message to the guide agent."""
    try:
        rate = await _check_chat_rate_limit(
            str(current_user.id),
            current_user.subscription_tier.value,
            redis,
            config,
        )

        if not rate["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily message limit reached",
            )

        # Load user's birth chart context
        chart_row = await db.fetchrow(
            "SELECT * FROM birth_charts WHERE user_id = $1",
            current_user.id,
        )

        # Load recent chat history
        history_rows = await db.fetch(
            """
            SELECT * FROM chat_messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 10
            """,
            current_user.id,
        )

        # Build context dict for guide agent
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
        agent_response = (
            "Based on your chart, I can provide insights about "
            "your astrological patterns. How can I help you today?"
        )
        render_blocks: list[dict[str, Any]] = []

        # Save user message
        user_msg_id = uuid.uuid4()
        now = datetime.utcnow()
        await db.execute(
            """
            INSERT INTO chat_messages
            (id, user_id, role, message, content_type, blocks, created_at)
            VALUES ($1, $2, 'user', $3, 'text', '[]'::jsonb, $4)
            """,
            user_msg_id,
            current_user.id,
            request.message,
            now,
        )

        # Save assistant response
        response_id = uuid.uuid4()
        response_time = datetime.utcnow()
        await db.execute(
            """
            INSERT INTO chat_messages
            (id, user_id, role, message, content_type, blocks, created_at)
            VALUES ($1, $2, 'assistant', $3, 'text', $4::jsonb, $5)
            """,
            response_id,
            current_user.id,
            agent_response,
            "[]",
            response_time,
        )

        # Return shape matching ChatMessageModel expected by mobile
        return {
            "message": {
                "id": str(response_id),
                "userId": str(current_user.id),
                "role": "assistant",
                "content": agent_response,
                "contentType": "text",
                "metadata": {},
                "blocks": render_blocks,
                "tokensUsed": 0,
                "createdAt": response_time.isoformat(),
            },
            "remainingMessages": rate["remaining"],
        }

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
    """Get paginated chat history."""
    try:
        if limit > 100:
            limit = 100

        rows = await db.fetch(
            """
            SELECT *
            FROM chat_messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            current_user.id,
            limit,
            skip,
        )

        count_row = await db.fetchrow(
            "SELECT COUNT(*) as total FROM chat_messages WHERE user_id = $1",
            current_user.id,
        )
        total = count_row["total"] if count_row else 0

        # Return messages in ChatMessageModel shape
        messages = [
            {
                "id": str(row["id"]),
                "userId": str(row["user_id"]),
                "role": row["role"],
                "content": row["message"],
                "contentType": row.get("content_type", "text"),
                "metadata": row.get("metadata") or {},
                "blocks": row.get("blocks") or [],
                "tokensUsed": row.get("tokens_used", 0),
                "createdAt": row["created_at"].isoformat(),
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
) -> dict[str, Any]:
    """Get remaining chat messages for today."""
    try:
        chat_limits = config.get("chat_limits", {})
        limit = chat_limits.get(current_user.subscription_tier.value, 5)

        if limit == -1:
            return {"remaining": -1, "limit": -1, "reset_at": ""}

        if redis is None:
            return {"remaining": limit, "limit": limit, "reset_at": ""}

        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")
        rate_key = f"rate:{current_user.id}:{date_str}"

        current = await redis.get(rate_key)
        used = int(current) if current else 0
        remaining = max(0, limit - used)

        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        return {
            "remaining": remaining,
            "limit": limit,
            "reset_at": tomorrow.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get remaining messages for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve message count",
        ) from None
