"""Chart endpoints for the 108 Gateway."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user, get_db
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.cosmos.src import (
    RASHI_NAMES,
    get_divisional_chart,
    longitude_to_nakshatra,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _load_birth_chart(db: Any, user_id: str) -> dict[str, Any] | None:
    """
    Load user's birth chart from database.

    Args:
        db: Database connection.
        user_id: User UUID.

    Returns:
        Birth chart data or None if not found.
    """
    try:
        row = await db.fetchrow(
            "SELECT * FROM birth_charts WHERE user_id = $1",
            user_id,
        )
        if not row:
            return None

        # asyncpg returns JSONB as Python dict already — no json.loads needed
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "birth_datetime": row["birth_datetime"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "timezone": row["timezone"],
            "planets": row["planets"] if row["planets"] else {},
            "houses": row["houses"] if row["houses"] else {},
            "lagna_rashi": row["lagna_rashi"],
            "moon_rashi": row["moon_rashi"],
            "moon_nakshatra": row["moon_nakshatra"],
            "moon_nakshatra_pada": row.get("moon_nakshatra_pada"),
            "ayanamsa": row.get("ayanamsa"),
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


@router.get("/summary")
async def get_chart_summary(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get basic birth chart summary.

    Available to all tiers. Returns basic chart information without
    full calculations.

    Args:
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        dict: Basic chart summary.

    Raises:
        HTTPException: 401 if user is not authenticated, 404 if no
            birth chart found, 500 if chart calculation fails.
    """
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found. Please set birth details.",
            ) from None

        # Extract basic info from stored data
        planets = chart.get("planets", {})

        # Build planet list with name and rashi only
        planet_list = []
        for planet_name, planet_data in planets.items():
            if isinstance(planet_data, dict):
                rashi_num = int(planet_data.get("rashi", 0))
                rashi_name = RASHI_NAMES[rashi_num - 1] if 1 <= rashi_num <= 12 else "Unknown"
                planet_list.append(
                    {
                        "name": planet_name,
                        "rashi": rashi_name,
                        "rashi_number": rashi_num,
                    }
                )

        return {
            "user_id": str(current_user.id),
            "birth_datetime": chart["birth_datetime"].isoformat()
            if hasattr(chart["birth_datetime"], "isoformat")
            else str(chart["birth_datetime"]),
            "location": {
                "latitude": chart["latitude"],
                "longitude": chart["longitude"],
                "timezone": chart["timezone"],
            },
            "lagna_rashi": chart["lagna_rashi"],
            "moon_rashi": chart["moon_rashi"],
            "moon_nakshatra": chart["moon_nakshatra"],
            "planets": planet_list,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate chart summary for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate chart",
        ) from e


@router.get("/full")
async def get_full_chart(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get full birth chart with all divisional charts.

    Free tier gets D1 only. Pro and premium get all divisional charts.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Full chart data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "chart_divisional", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock full charts"},
                access,
                "Upgrade to Pro to unlock full charts",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        planets = chart.get("planets", {})
        houses = chart.get("houses", {})

        # Build full planet details
        planet_details = []
        for planet_name, planet_data in planets.items():
            if isinstance(planet_data, dict):
                longitude = float(planet_data.get("longitude", 0))
                rashi_num = int(planet_data.get("rashi", 0))
                rashi_name = RASHI_NAMES[rashi_num - 1] if 1 <= rashi_num <= 12 else "Unknown"

                nakshatra_info = longitude_to_nakshatra(longitude)

                planet_details.append(
                    {
                        "name": planet_name,
                        "longitude": longitude,
                        "rashi": rashi_name,
                        "rashi_number": rashi_num,
                        "nakshatra": nakshatra_info.get("name", "Unknown"),
                        "nakshatra_number": nakshatra_info.get("number"),
                        "pada": nakshatra_info.get("pada"),
                        "retrograde": planet_data.get("is_retrograde", False),
                        "speed": planet_data.get("speed"),
                    }
                )

        response = {
            "user_id": str(current_user.id),
            "birth_datetime": chart["birth_datetime"].isoformat()
            if hasattr(chart["birth_datetime"], "isoformat")
            else str(chart["birth_datetime"]),
            "location": {
                "latitude": chart["latitude"],
                "longitude": chart["longitude"],
                "timezone": chart["timezone"],
            },
            "lagna_rashi": chart["lagna_rashi"],
            "moon_rashi": chart["moon_rashi"],
            "moon_nakshatra": chart["moon_nakshatra"],
            "planets": planet_details,
        }

        # Add houses for pro+ tiers
        if access == AccessLevel.FULL:
            response["houses"] = houses

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate full chart for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate chart",
        ) from e


@router.get("/divisional/{division}")
async def get_divisional(
    division: int,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get specific divisional chart.

    Divisional charts (D2, D3, D7, D9, D10, etc.) are gated by
    subscription.

    Args:
        division: Divisional chart number (2, 3, 7, 9, 10, 12, etc.).
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Divisional chart data (gated by subscription tier).

    Raises:
        HTTPException: 400 if invalid division, 401 if not
            authenticated, 403 if locked for tier, 404 if no birth
            chart, 500 if calculation fails.
    """
    try:
        # Validate division number
        valid_divisions = [2, 3, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
        if division not in valid_divisions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid division. Valid values: {valid_divisions}",
            ) from None

        access = await check_feature_access(
            "chart_divisional", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock divisional charts"},
                access,
                "Upgrade to Pro to unlock divisional charts",
            ).model_dump()

        # Gate based on tier: free=locked, pro=D1/D9/D10, premium=all
        if current_user.subscription_tier == "pro" and division not in [1, 9, 10]:
            return gate_response(
                {"message": ("Upgrade to Premium to unlock this divisional chart")},
                AccessLevel.PREVIEW,
                "Upgrade to Premium",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        planets = chart.get("planets", {})

        # Build planets dict for divisional chart calculation
        planets_dict = {}
        for planet_name, planet_data in planets.items():
            if isinstance(planet_data, dict):
                planets_dict[planet_name] = float(planet_data.get("longitude", 0))

        # Calculate divisional chart
        divisional = get_divisional_chart(planets_dict, division)

        # Build response
        div_planets = []
        for planet_name, div_data in divisional.items():
            rashi_num = int(div_data.get("rashi", 0))
            rashi_name = RASHI_NAMES[rashi_num - 1] if 1 <= rashi_num <= 12 else "Unknown"

            div_planets.append(
                {
                    "name": planet_name,
                    "longitude": float(div_data.get("longitude", 0)),
                    "rashi": rashi_name,
                    "rashi_number": rashi_num,
                    "degree_in_sign": float(div_data.get("degree_in_sign", 0)),
                }
            )

        return {
            "user_id": str(current_user.id),
            "division": division,
            "division_name": f"D{division}",
            "planets": div_planets,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate D{division} chart for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate divisional chart",
        ) from e
