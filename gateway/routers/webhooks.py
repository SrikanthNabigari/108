"""Webhook endpoints for the 108 Gateway."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
        app_user_id = payload.get("event", {}).get("app_user_id")

        logger.info(f"RevenueCat webhook received: {event_type} for {app_user_id}")

        # Get database connection
        db = request.app.state.db
        redis = request.app.state.redis

        # Map RevenueCat product IDs to subscription tiers
        product_id = payload.get("event", {}).get("product_id", "").lower()
        subscription_mapping = {
            "pro_annual": "pro",
            "pro_monthly": "pro",
            "premium_annual": "premium",
            "premium_monthly": "premium",
        }

        # Process event based on type
        if event_type == "INITIAL_PURCHASE":
            tier = subscription_mapping.get(product_id, "pro")
            await db.execute(
                "UPDATE users SET subscription_tier = $1 WHERE revenuecat_id = $2",
                tier,
                app_user_id,
            )

        elif event_type == "RENEWAL":
            # Subscription renewed, tier already set
            tier = subscription_mapping.get(product_id, "pro")
            await db.execute(
                "UPDATE users SET subscription_tier = $1 WHERE revenuecat_id = $2",
                tier,
                app_user_id,
            )

        elif event_type == "CANCELLATION":
            # Downgrade to free tier
            await db.execute(
                "UPDATE users SET subscription_tier = $1 WHERE revenuecat_id = $2",
                "free",
                app_user_id,
            )

        elif event_type == "NON_RENEWING_PURCHASE":
            # Credit purchase - extract amount and add to wallet
            price_in_usd = payload.get("event", {}).get("price_in_usd", 0.0)
            # Simple mapping: $1 USD = 10 credits (configurable)
            credit_amount = int(price_in_usd * 10)

            # Get user ID from revenuecat_id
            user_row = await db.fetchrow(
                "SELECT id FROM users WHERE revenuecat_id = $1",
                app_user_id,
            )

            if user_row:
                user_id = user_row["id"]

                # Add transaction
                import uuid

                transaction_id = uuid.uuid4()
                await db.execute(
                    """
                    INSERT INTO credit_transactions
                    (id, user_id, amount, transaction_type, description,
                     created_at)
                    VALUES ($1, $2, $3, $4, $5, NOW())
                    """,
                    str(transaction_id),
                    str(user_id),
                    credit_amount,
                    "credit_purchase",
                    f"Purchased {credit_amount} credits",
                )

                # Update wallet balance
                await db.execute(
                    """
                    INSERT INTO credit_wallets
                    (user_id, balance, created_at, updated_at)
                    VALUES ($1, $2, NOW(), NOW())
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = credit_wallets.balance + $2,
                        updated_at = NOW()
                    """,
                    str(user_id),
                    credit_amount,
                )

        # Invalidate user cache in Redis
        if app_user_id:
            # Clear any cached user data
            await redis.delete(f"user:{app_user_id}:*")

        return {"status": "processed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process RevenueCat webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook",
        ) from None
