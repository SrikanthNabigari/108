"""Rate limiting middleware for the 108 Gateway."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from redis.asyncio import Redis

from gateway.models import SubscriptionTier

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""

    allowed: bool
    remaining: int
    limit: int
    reset_at: datetime


async def check_rate_limit(
    user_id: str,
    user_tier: SubscriptionTier,
    redis: Redis,
    config: dict[str, Any],
) -> RateLimitResult:
    """
    Check rate limit for user on current day.

    Uses Redis with key pattern `rate:{user_id}:{date}` incremented daily.
    Limits are loaded from config.chat_limits based on subscription tier.

    Args:
        user_id: User UUID as string.
        user_tier: User's subscription tier.
        redis: Redis connection instance.
        config: Application configuration with chat_limits.

    Returns:
        RateLimitResult: Rate limit status with remaining count and reset time.
    """
    # Get chat limit for this tier
    chat_limits = config.get("chat_limits", {})
    limit = chat_limits.get(user_tier.value, 5)

    # Premium tier has unlimited access
    if limit == -1:
        now = datetime.utcnow()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return RateLimitResult(
            allowed=True,
            remaining=-1,  # Unlimited
            limit=-1,
            reset_at=tomorrow,
        )

    # Build rate limit key with current date
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    rate_key = f"rate:{user_id}:{date_str}"

    # Calculate reset time (next midnight UTC)
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    try:
        # Increment counter and set expiry
        current = await redis.incr(rate_key)
        await redis.expire(rate_key, 86400)  # 24 hours

        remaining = max(0, limit - current)
        allowed = current <= limit

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            limit=limit,
            reset_at=tomorrow,
        )

    except Exception as e:
        logger.error(f"Rate limit check failed for {user_id}: {e}")
        # Fail open - allow request if Redis fails
        return RateLimitResult(
            allowed=True,
            remaining=limit,
            limit=limit,
            reset_at=tomorrow,
        )


def get_rate_limit_headers(result: RateLimitResult) -> dict[str, str]:
    """
    Get HTTP headers for rate limit response.

    Args:
        result: RateLimitResult from check_rate_limit.

    Returns:
        dict: Headers to include in response.
    """
    headers = {
        "X-RateLimit-Limit": str(result.limit),
        "X-RateLimit-Remaining": str(result.remaining),
        "X-RateLimit-Reset": str(int(result.reset_at.timestamp())),
    }
    return headers
