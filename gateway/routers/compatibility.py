"""Compatibility analysis endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import (
    AccessLevel,
    CompatibilityFullRequest,
    CompatibilityQuickRequest,
    UserContext,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/quick")
async def get_quick_compatibility(
    request: CompatibilityQuickRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get quick compatibility check (Ashta Kuta).

    Gated feature - pro and premium tiers.

    Args:
        request: Compatibility check request with partner birth details.
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Quick compatibility score and analysis (gated by tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "compatibility_quick", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock compatibility check"},
                access,
                "Upgrade to Pro to unlock compatibility check",
            ).dict()

        # TODO: Call packages.patterns.src kundali_matching function
        # Extract nakshatra and rashi for both users
        # Calculate Ashta Kuta score (out of 36)
        # Return score, verdict, and interpretation

        raise NotImplementedError("Compatibility calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate compatibility for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate compatibility",
        ) from e


@router.post("/full")
async def get_full_compatibility(
    request: CompatibilityFullRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get full compatibility analysis (Synastry).

    Gated feature - premium tier only.

    Args:
        request: Full compatibility request with partner birth details.
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Full synastry analysis (premium only).

    Raises:
        HTTPException: 401 if not authenticated, 403 if not premium,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "compatibility_full", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Premium only feature"},
                access,
                "Upgrade to Premium to unlock full compatibility analysis",
            ).dict()

        # TODO: Call packages.patterns.src synastry_analysis function
        # Overlay both charts, calculate cross aspects
        # Compute composite midpoint chart
        # Analyze house overlays and planetary aspects
        # Return detailed synastry report

        raise NotImplementedError("Synastry calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate synastry for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate synastry",
        ) from e
