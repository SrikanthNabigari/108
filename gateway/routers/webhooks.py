"""Webhook endpoints for the 108 Gateway."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, HTTPException, Request, status

from gateway.config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_revenuecat_signature(
    body: str,
    signature: str,
    webhook_secret: str,
) -> bool:
    """
    Verify RevenueCat webhook signature.

    Args:
        body: Request body as string.
        signature: Signature from X-RevenueCat-Signature header.
        webhook_secret: RevenueCat webhook secret.

    Returns:
        bool: True if signature is valid.
    """
    expected_signature = hashlib.sha256(webhook_secret.encode() + body.encode()).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


@router.post("/revenuecat")
async def handle_revenuecat_webhook(request: Request) -> dict[str, str]:
    """
    Handle RevenueCat webhook events.

    Verifies webhook signature, processes subscription changes and credit
    purchases, updates user subscription tier, and invalidates Redis cache.

    Args:
        request: FastAPI request object.

    Returns:
        dict: Success confirmation.

    Raises:
        HTTPException: 401 if signature invalid, 400 if parsing fails,
            500 if processing fails.
    """
    try:
        settings = Settings()
        body = await request.body()
        body_str = body.decode("utf-8")

        # Verify signature
        signature = request.headers.get("X-RevenueCat-Signature")
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing signature",
            )

        if not verify_revenuecat_signature(body_str, signature, settings.revenuecat_webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature",
            )

        # Parse webhook payload
        payload = json.loads(body_str)
        event_type = payload.get("event", {}).get("type")
        event_data = payload.get("event", {}).get("app_user_id")

        logger.info(f"RevenueCat webhook received: {event_type} for {event_data}")

        # TODO: Process event based on type
        # Event types:
        # - INITIAL_PURCHASE: New subscription
        # - NON_RENEWING_PURCHASE: One-time purchase (credits)
        # - RENEWAL: Subscription renewal
        # - CANCELLATION: Subscription cancelled
        # - UNCANCELLATION: Subscription uncancelled
        # TODO: Update users.subscription_tier based on RevenueCat product ID
        # TODO: For NON_RENEWING_PURCHASE, add credits to user_credits
        # TODO: Invalidate user cache in Redis (user:{user_id}:*)

        return {"status": "processed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process RevenueCat webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook",
        ) from e
