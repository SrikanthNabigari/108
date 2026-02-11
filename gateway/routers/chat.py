"""Chat endpoints for the 108 Gateway."""

from __future__ import annotations

import json
import logging
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.config import Settings
from gateway.dependencies import (
    get_app_config,
    get_current_user,
    get_db,
    get_redis,
    get_settings,
)
from gateway.models import (
    ChatRequest,
    UserContext,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Guide agent + ChatEngine singletons ──

_guide_agent = None
_chat_engine = None


def _get_guide_agent(settings: Settings):
    """Lazy-init Guide agent singleton. Returns None if unavailable."""
    global _guide_agent
    if _guide_agent is not None:
        return _guide_agent
    if not settings.anthropic_api_key:
        return None
    try:
        from packages.guide.src.agent import Guide

        _guide_agent = Guide(api_key=settings.anthropic_api_key)
        return _guide_agent
    except Exception as exc:
        logger.warning("Guide agent init failed, will use ChatEngine: %s", exc)
        return None


def _get_chat_engine(settings: Settings):
    """Lazy-init ChatEngine singleton. Returns None if no API key."""
    global _chat_engine
    if _chat_engine is not None:
        return _chat_engine
    if not settings.anthropic_api_key:
        return None
    try:
        from packages.guide.src.chat_engine import ChatEngine

        _chat_engine = ChatEngine(api_key=settings.anthropic_api_key)
        return _chat_engine
    except Exception as exc:
        logger.warning("ChatEngine init failed: %s", exc)
        return None


def _build_birth_context(chart_row: Any) -> dict[str, Any]:
    """Build birth_context dict from a DB chart row."""
    if not chart_row:
        return {}

    signs = [
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    ]

    planets_raw = chart_row.get("planets", {})
    if isinstance(planets_raw, str):
        planets_raw = json.loads(planets_raw)

    # Compute lagna rashi index for house calculation
    lagna_rashi = (chart_row.get("lagna_rashi") or "aries").lower()
    lagna_idx = signs.index(lagna_rashi) if lagna_rashi in signs else 0

    natal_planets = {}
    for planet_name, planet_data in (planets_raw or {}).items():
        if isinstance(planet_data, dict):
            lon = float(planet_data.get("longitude", 0))
            # Compute rashi and house from longitude if not stored
            rashi_idx = int(lon / 30) % 12
            rashi_name = signs[rashi_idx]
            house = ((rashi_idx - lagna_idx) % 12) + 1

            natal_planets[planet_name] = {
                "longitude": lon,
                "rashi": planet_data.get("rashi", rashi_idx),
                "rashi_name": rashi_name,
                "house": planet_data.get("house", house),
                "nakshatra": planet_data.get("nakshatra"),
                "is_retrograde": planet_data.get("is_retrograde", False),
                "speed": planet_data.get("speed", 0),
            }

    moon_data = natal_planets.get("moon", {})
    moon_lon = float(moon_data.get("longitude", 0)) if moon_data else None

    birth_dt = chart_row.get("birth_datetime")
    if isinstance(birth_dt, datetime):
        birth_dt_str = birth_dt.isoformat()
    else:
        birth_dt_str = str(birth_dt) if birth_dt else ""

    return {
        "birth_datetime": birth_dt_str,
        "birth_lat": float(chart_row.get("latitude", 0)),
        "birth_lon": float(chart_row.get("longitude", 0)),
        "natal_planets": natal_planets,
        "moon_longitude": moon_lon,
        "lagna_rashi": chart_row.get("lagna_rashi"),
        "moon_rashi": chart_row.get("moon_rashi"),
        "moon_nakshatra": chart_row.get("moon_nakshatra"),
    }


async def _check_chat_rate_limit(
    user_id: str,
    tier: str,
    redis: Any,
    config: dict,
    *,
    env: str = "production",
) -> dict[str, Any]:
    """Check rate limit, returning remaining count. Works without Redis."""
    # Development mode — unlimited messages
    if env == "development":
        return {"allowed": True, "remaining": -1, "limit": -1}

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


@router.post("")
async def send_message(
    request: ChatRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    redis: Annotated[Any, Depends(get_redis)],
    db: Annotated[object, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, Any]:
    """Send a message to the guide agent."""
    try:
        rate = await _check_chat_rate_limit(
            str(current_user.id),
            current_user.subscription_tier.value,
            redis,
            config,
            env=settings.env,
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

        # Build birth context for ChatEngine
        birth_context = _build_birth_context(chart_row)

        # Build chat history in [{role, content}] format
        chat_history = [
            {"role": row["role"], "content": row["message"]} for row in reversed(history_rows)
        ]

        # Prefer Guide agent (has memory, personality, intent routing)
        # Fallback to ChatEngine, then to static response
        tokens_used = 0
        agent_response = None
        render_blocks: list[dict[str, Any]] = []

        has_chart = birth_context.get("moon_longitude") is not None
        logger.info(
            "Chat: has_chart=%s, moon_lon=%s", has_chart, birth_context.get("moon_longitude")
        )

        # Try Guide agent first
        guide = _get_guide_agent(settings) if has_chart else None
        logger.info("Chat: guide_agent=%s", "loaded" if guide else "None")
        if guide is not None:
            try:
                from packages.guide.src.chat_blocks import analysis_to_blocks, build_blocks

                logger.info(
                    "Chat: calling guide.chat() with %d history messages", len(chat_history)
                )
                result = guide.chat(
                    user_input=request.message,
                    user_id=str(current_user.id),
                    birth_chart=birth_context,
                    chat_history=chat_history,
                )
                agent_response = result.get("response", "")
                analysis = result.get("analysis_results", {})

                # Prefer direct tool results (from LLM tool-use loop)
                # over analysis_to_blocks (from graph-computed data)
                tool_tuples = analysis.pop("_tool_results", None)
                if tool_tuples:
                    render_blocks = build_blocks(tool_tuples)
                    logger.info(
                        "Chat: built %d blocks from %d tool calls",
                        len(render_blocks),
                        len(tool_tuples),
                    )
                else:
                    render_blocks = analysis_to_blocks(analysis)
                    logger.info("Chat: built %d blocks from analysis_results", len(render_blocks))
            except Exception as exc:
                logger.warning("Guide agent failed, trying ChatEngine: %s", exc, exc_info=True)

        # Fallback to ChatEngine
        if agent_response is None:
            engine = _get_chat_engine(settings)
            logger.info(
                "Chat: fallback engine=%s, has_chart=%s", "loaded" if engine else "None", has_chart
            )
            if engine and has_chart:
                try:
                    logger.info("Chat: calling ChatEngine.chat()...")
                    result = engine.chat(
                        message=request.message,
                        birth_context=birth_context,
                        chat_history=chat_history,
                        personality_style=birth_context.get("moon_rashi"),
                    )
                    agent_response = result.text
                    render_blocks = result.blocks
                    tokens_used = result.tokens_used
                    logger.info("Chat: ChatEngine returned %d blocks", len(render_blocks))
                except Exception as exc:
                    logger.warning("ChatEngine failed: %s", exc, exc_info=True)

        # Final fallback — no API key or no birth chart
        if agent_response is None:
            logger.info("Chat: using static fallback response")
            agent_response = (
                "Based on your chart, I can provide insights about "
                "your astrological patterns. How can I help you today?"
            )
            render_blocks = []

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
        blocks_json = json.dumps(render_blocks, default=str)
        await db.execute(
            """
            INSERT INTO chat_messages
            (id, user_id, role, message, content_type, blocks, created_at)
            VALUES ($1, $2, 'assistant', $3, 'text', $4::jsonb, $5)
            """,
            response_id,
            current_user.id,
            agent_response,
            blocks_json,
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
                "tokensUsed": tokens_used,
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
        def _parse_blocks(raw: Any) -> list:
            if not raw:
                return []
            if isinstance(raw, str):
                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    return []
            return raw if isinstance(raw, list) else []

        messages = [
            {
                "id": str(row["id"]),
                "userId": str(row["user_id"]),
                "role": row["role"],
                "content": row["message"],
                "contentType": row.get("content_type", "text"),
                "metadata": row.get("metadata") or {},
                "blocks": _parse_blocks(row.get("blocks")),
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
