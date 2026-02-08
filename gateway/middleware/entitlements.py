"""Entitlements engine for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Any, TypeVar

from gateway.models import AccessLevel, GatedResponse, SubscriptionTier

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def check_feature_access(
    feature_key: str,
    user_tier: SubscriptionTier,
    config: dict[str, Any],
) -> AccessLevel:
    """
    Check feature access level for a user tier.

    Loads feature gates from app_config and determines access level
    based on user's subscription tier.

    Args:
        feature_key: Feature identifier (e.g., "forecast_weekly", "chart_navamsha").
        user_tier: User's subscription tier (free, pro, premium).
        config: Application configuration dict with feature_gates.

    Returns:
        AccessLevel: FULL, PREVIEW, or LOCKED.
    """
    feature_gates = config.get("feature_gates", {})
    feature = feature_gates.get(feature_key, {})

    # tier_access is a string like "full", "preview", or "locked"
    tier_access = feature.get(user_tier.value, "locked")

    if tier_access == "full":
        return AccessLevel.FULL
    elif tier_access == "preview":
        return AccessLevel.PREVIEW
    else:
        return AccessLevel.LOCKED


def gate_response(
    data: T,
    access_level: AccessLevel,
    upgrade_hint: str | None = None,
) -> GatedResponse[T]:
    """
    Wrap response with access level and optional upgrade hint.

    Args:
        data: Response payload.
        access_level: Access level for this feature.
        upgrade_hint: Optional hint for upgrade path.

    Returns:
        GatedResponse: Wrapped response with access metadata.
    """
    return GatedResponse(
        data=data,
        access=access_level,
        upgrade_hint=upgrade_hint,
    )


async def get_upgrade_hint(
    current_tier: SubscriptionTier,
    required_tier: SubscriptionTier,
) -> str:
    """
    Get user-friendly upgrade hint message.

    Args:
        current_tier: User's current subscription tier.
        required_tier: Required tier for feature.

    Returns:
        str: Upgrade hint message.
    """
    if current_tier == SubscriptionTier.FREE:
        if required_tier == SubscriptionTier.PRO:
            return "Upgrade to Pro to unlock this feature"
        else:
            return "Upgrade to Premium to unlock this feature"
    elif current_tier == SubscriptionTier.PRO:
        return "Upgrade to Premium to unlock this feature"
    return ""


async def check_entitlement(
    feature_key: str,
    user_tier: SubscriptionTier,
    config: dict[str, Any],
    raise_on_locked: bool = True,
) -> tuple[AccessLevel, str | None]:
    """
    Check entitlement and return access level with upgrade hint.

    Args:
        feature_key: Feature identifier.
        user_tier: User's subscription tier.
        config: Application configuration.
        raise_on_locked: If True, raise HTTPException when locked.

    Returns:
        tuple: (AccessLevel, upgrade_hint)

    Raises:
        HTTPException: 403 if feature is locked and raise_on_locked=True.
    """
    access = await check_feature_access(feature_key, user_tier, config)

    if access == AccessLevel.LOCKED:
        if raise_on_locked:
            from fastapi import HTTPException

            hint = await get_upgrade_hint(user_tier, SubscriptionTier.PRO)
            raise HTTPException(
                status_code=403,
                detail=f"Feature locked: {hint}",
            )
        else:
            hint = await get_upgrade_hint(user_tier, SubscriptionTier.PRO)
            return access, hint

    return access, None
