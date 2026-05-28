"""Remedies and gemstone endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, UserContext
from packages.context.src import get_current_dasha
from packages.self.src import recommend_gems, recommend_remedies

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

        # TODO: Load user's birth chart from DB
        # For now, use placeholder data
        birth_datetime = "1992-12-03T03:00:00+05:30"
        moon_longitude = 324.11
        _ = "libra"  # lagna_rashi placeholder for DB integration

        # Get current dasha
        current_dasha = get_current_dasha(birth_datetime, moon_longitude)

        # TODO: Get detected doshas from birth chart analysis
        active_doshas = []

        # TODO: Get weak planets from shadbala analysis
        weak_planets = []

        # Get remedies
        remedies_result = recommend_remedies(current_dasha, active_doshas, weak_planets)

        return {
            **remedies_result,
            "current_dasha": current_dasha,
            "access": "full",
        }

    except AccessLevel.LOCKED as e:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except Exception as e:
        logger.error(f"Failed to get remedies for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve remedies",
        ) from None


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

        # TODO: Load user's birth chart from DB
        lagna_rashi = "libra"
        planets = {
            "sun": {"longitude": 52.5, "sign": "taurus"},
            "moon": {"longitude": 102.5, "sign": "gemini"},
        }

        # TODO: Get shadbala scores
        shadbala = {}

        # TODO: Get current dasha lord
        current_dasha = {
            "mahadasha_lord": "mercury",
            "antardasha_lord": "saturn",
        }

        # TODO: Get active doshas
        active_doshas = []

        # Get gem recommendations
        gem_result = recommend_gems(
            lagna_rashi,
            planets,
            shadbala,
            current_dasha,
            active_doshas,
        )

        return {
            **gem_result,
            "access": "full",
        }

    except AccessLevel.LOCKED as e:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except Exception as e:
        logger.error(f"Failed to get gem recommendations for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve gemstone recommendations",
        ) from None
