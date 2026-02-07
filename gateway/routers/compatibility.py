"""Compatibility analysis endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config, get_current_user
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import (
    AccessLevel,
    CompatibilityFullRequest,
    CompatibilityQuickRequest,
    UserContext,
)
from packages.cosmos.src import (
    get_all_planets,
    get_house_cusps,
    longitude_to_nakshatra,
)
from packages.self.src import calculate_ashta_kuta, get_synastry_report

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

        # Get user's moon position from birth chart (TODO: load from DB)
        # For now, we'll need to calculate partner positions
        user_nakshatra = 1  # TODO: Get from user's birth chart
        user_rashi = "aries"  # TODO: Get from user's birth chart

        # Calculate partner's planets and houses
        partner_planets = get_all_planets(
            request.partner_birth_datetime.isoformat(),
            request.partner_latitude,
            request.partner_longitude,
            request.partner_timezone_offset,
        )

        # Extract partner moon position
        partner_moon_lon = partner_planets.get("moon", {}).get("longitude", 0)
        partner_nakshatra_data = longitude_to_nakshatra(partner_moon_lon)
        partner_nakshatra = partner_nakshatra_data.get("nakshatra_number", 1)

        # Get partner's rashi
        partner_rashi = partner_planets.get("moon", {}).get("sign", "aries")

        # Calculate Ashta Kuta score
        kuta_result = calculate_ashta_kuta(
            user_nakshatra, user_rashi, partner_nakshatra, partner_rashi
        )

        return {
            "score": kuta_result.get("total_score", 0),
            "max_score": 36,
            "percentage": (kuta_result.get("total_score", 0) / 36) * 100,
            "verdict": kuta_result.get("verdict", ""),
            "kuta_details": kuta_result,
            "access": "full",
        }

    except AccessLevel.LOCKED as e:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except Exception as e:
        logger.error(f"Failed to calculate compatibility for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate compatibility",
        ) from None


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

        # Get user's birth chart (TODO: load from DB)
        # For now, use mock data
        user_planets = {
            "sun": {"longitude": 52.5, "sign": "taurus"},
            "moon": {"longitude": 102.5, "sign": "gemini"},
        }
        user_cusps = [0] * 12  # TODO: Load from DB

        # Calculate partner's planets and houses
        partner_planets_data = get_all_planets(
            request.partner_birth_datetime.isoformat(),
            request.partner_latitude,
            request.partner_longitude,
            request.partner_timezone_offset,
        )

        partner_cusps_data = get_house_cusps(
            request.partner_birth_datetime.isoformat(),
            request.partner_latitude,
            request.partner_longitude,
        )

        # Call synastry function
        synastry_result = get_synastry_report(
            user_planets,
            user_cusps,
            partner_planets_data,
            partner_cusps_data.get("cusps", []),
        )

        return {
            **synastry_result,
            "access": "full",
        }

    except AccessLevel.LOCKED as e:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except Exception as e:
        logger.error(f"Failed to calculate synastry for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate synastry",
        ) from None
