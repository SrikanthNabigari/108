"""Compatibility analysis endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gateway.dependencies import get_app_config, get_current_user, get_db
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
    db: Annotated[object, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get quick compatibility check (Ashta Kuta).

    Gated feature - pro and premium tiers.

    Args:
        request: Compatibility check request with partner birth details.
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection pool.

    Returns:
        dict: Quick compatibility score and analysis (gated by tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for tier,
            400 if no birth chart, 500 if calculation fails.
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

        # Load user's birth chart from DB
        chart_row = await db.fetchrow(
            "SELECT * FROM birth_charts WHERE user_id = $1",
            str(current_user.id),
        )
        if chart_row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Birth chart not found. Please enter birth details first.",
            )

        import json as _json

        user_planets = (
            _json.loads(chart_row["planets"])
            if isinstance(chart_row["planets"], str)
            else (chart_row["planets"] or {})
        )
        user_moon_data = user_planets.get("moon", {})
        user_moon_lon = float(user_moon_data.get("longitude", 0))
        user_nakshatra_data = longitude_to_nakshatra(user_moon_lon)
        user_nakshatra = user_nakshatra_data.get("nakshatra_number", 1)
        user_rashi = user_moon_data.get("sign", "aries")

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
    db: Annotated[object, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get full compatibility analysis (Synastry).

    Gated feature - premium tier only.

    Args:
        request: Full compatibility request with partner birth details.
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection pool.

    Returns:
        dict: Full synastry analysis (premium only).

    Raises:
        HTTPException: 401 if not authenticated, 403 if not premium,
            400 if no birth chart, 500 if calculation fails.
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

        # Load user's birth chart from DB
        chart_row = await db.fetchrow(
            "SELECT * FROM birth_charts WHERE user_id = $1",
            str(current_user.id),
        )
        if chart_row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Birth chart not found. Please enter birth details first.",
            )

        import json as _json

        user_planets = (
            _json.loads(chart_row["planets"])
            if isinstance(chart_row["planets"], str)
            else (chart_row["planets"] or {})
        )
        user_cusps_raw = chart_row.get("cusps")
        if user_cusps_raw is not None:
            user_cusps = (
                _json.loads(user_cusps_raw) if isinstance(user_cusps_raw, str) else user_cusps_raw
            )
        else:
            user_cusps = [0] * 12

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
