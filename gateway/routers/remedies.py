"""Remedies and gemstone endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, UserContext

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def get_remedies(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get current active remedies for user's chart.

    Gated feature - pro and premium tiers. Returns mantras, charities,
    worship recommendations, and general remedies based on active doshas
    and weak planets.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Active remedies organized by category (gated by tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access("remedies", current_user.subscription_tier, config)

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock remedy analysis"},
                access,
                "Upgrade to Pro to unlock remedy analysis",
            ).dict()

        # TODO: Get current dasha from packages.context.src current_dasha
        # TODO: Get detected doshas from packages.patterns.src detect_doshas
        # TODO: Get weak planets from chart analysis
        # TODO: Call packages.patterns.src recommend_chart_remedies
        # Pass dasha lords, active doshas, weak planets
        # Return urgent, recommended, and optional remedies

        raise NotImplementedError("Remedy calculation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to get remedies for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve remedies",
        ) from e


@router.get("/gems")
async def get_gemstone_recommendations(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
) -> dict[str, Any]:
    """
    Get gemstone recommendations for user's chart.

    Gated feature - pro and premium tiers. Returns primary and supporting
    gemstones, contraindicated gems, and wearing instructions based on
    birth chart analysis.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.

    Returns:
        dict: Gemstone recommendations with details (gated by tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            500 if calculation fails.
    """
    try:
        access = await check_feature_access("remedies", current_user.subscription_tier, config)

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock gemstone analysis"},
                access,
                "Upgrade to Pro to unlock gemstone analysis",
            ).dict()

        # TODO: Get lagna rashi from user's chart
        # TODO: Get birth chart planets with shadbala scores
        # TODO: Get current dasha lord
        # TODO: Get active doshas
        # TODO: Call packages.patterns.src gem_recommendation
        # Pass lagna, planets, shadbala, dasha, doshas
        # Return primary gem, supporting gems, contraindications, instructions

        raise NotImplementedError("Gemstone recommendation integration required")

    except NotImplementedError:
        raise
    except Exception as e:
        logger.error(f"Failed to get gem recommendations for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gemstone recommendations",
        ) from e
