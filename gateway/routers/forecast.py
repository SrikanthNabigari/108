"""Forecast endpoints for the 108 Gateway."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user, get_db
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.context.src import (
    get_daily_forecast,
    get_monthly_forecast,
    get_weekly_forecast,
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

        return {
            "birth_datetime": row["birth_datetime"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "timezone": row["timezone"],
            "planets": json.loads(row["planets"]) if row["planets"] else {},
            "lagna_rashi": row["lagna_rashi"],
            "moon_rashi": row["moon_rashi"],
            "moon_nakshatra": row["moon_nakshatra"],
            "ayanamsa": row["ayanamsa"],
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


def _build_natal_planets(planets: dict) -> dict[str, Any]:
    """
    Build natal planets dict for forecast functions.

    Args:
        planets: Raw planets dict from DB.

    Returns:
        Formatted planets dict with required fields.
    """
    result = {}
    for planet_name, planet_data in planets.items():
        if isinstance(planet_data, dict):
            result[planet_name] = {
                "longitude": float(planet_data.get("longitude", 0)),
                "rashi": int(planet_data.get("rashi", 0)),
                "house": int(planet_data.get("house", 0)),
                "nakshatra": planet_data.get("nakshatra"),
            }
    return result


@router.get("/daily")
async def get_daily_forecast_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get daily forecast.

    Available to all tiers. Free tier returns limited data.

    Args:
        current_user: Authenticated user context.
        db: Database connection.

    Returns:
        dict: Daily forecast data.

    Raises:
        HTTPException: 401 if not authenticated, 404 if no birth
            chart, 500 if calculation fails.
    """
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_longitude = None

        for planet_data in chart.get("planets", {}).values():
            if isinstance(planet_data, dict) and planet_data.get("name") == "moon":
                moon_longitude = float(planet_data.get("longitude", 0))
                break

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        # Call forecast function
        forecast = get_daily_forecast(
            birth_datetime_iso=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=chart["lagna_rashi"],
        )

        # Free tier: limited response
        if current_user.subscription_tier == "free":
            return {
                "date": datetime.now().date().isoformat(),
                "day_rating": forecast.get("day_rating", 5),
                "summary": forecast.get("summary", ""),
                "access": "preview",
            }

        # Pro+ tier: full response
        return forecast

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate daily forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e


@router.get("/weekly")
async def get_weekly_forecast_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get weekly forecast.

    Available to pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Weekly forecast data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "forecast_weekly", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock weekly forecasts"},
                access,
                "Upgrade to Pro to unlock weekly forecasts",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_longitude = None

        for planet_data in chart.get("planets", {}).values():
            if isinstance(planet_data, dict) and planet_data.get("name") == "moon":
                moon_longitude = float(planet_data.get("longitude", 0))
                break

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        # Call forecast function
        forecast = get_weekly_forecast(
            birth_datetime_iso=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=chart["lagna_rashi"],
        )

        return forecast

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate weekly forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e


@router.get("/monthly")
async def get_monthly_forecast_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
    month: int | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """
    Get monthly forecast.

    Available to pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.
        month: Month number (1-12), defaults to current month.
        year: Year, defaults to current year.

    Returns:
        dict: Monthly forecast data (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "forecast_monthly", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock monthly forecasts"},
                access,
                "Upgrade to Pro to unlock monthly forecasts",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_longitude = None

        for planet_data in chart.get("planets", {}).values():
            if isinstance(planet_data, dict) and planet_data.get("name") == "moon":
                moon_longitude = float(planet_data.get("longitude", 0))
                break

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        # Default to current month/year if not specified
        now = datetime.now()
        if month is None:
            month = now.month
        if year is None:
            year = now.year

        # Call forecast function
        forecast = get_monthly_forecast(
            birth_datetime_iso=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=chart["lagna_rashi"],
            month=month,
            year=year,
        )

        return forecast

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate monthly forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e


@router.get("/yearly")
async def get_yearly_forecast_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get yearly forecast.

    Available to premium tier only. Aggregates monthly forecasts
    for the year.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Yearly forecast data (premium only).

    Raises:
        HTTPException: 401 if not authenticated, 403 if not premium,
            404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "forecast_yearly", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Premium only feature"},
                access,
                "Upgrade to Premium to unlock yearly forecasts",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_longitude = None

        for planet_data in chart.get("planets", {}).values():
            if isinstance(planet_data, dict) and planet_data.get("name") == "moon":
                moon_longitude = float(planet_data.get("longitude", 0))
                break

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        # Aggregate monthly forecasts for current year
        now = datetime.now()
        monthly_forecasts = []
        yearly_ratings = []

        for month in range(1, 13):
            try:
                forecast = get_monthly_forecast(
                    birth_datetime_iso=birth_dt.isoformat(),
                    birth_lat=chart["latitude"],
                    birth_lon=chart["longitude"],
                    natal_planets=natal_planets,
                    moon_longitude=moon_longitude,
                    lagna_rashi=chart["lagna_rashi"],
                    month=month,
                    year=now.year,
                )
                monthly_forecasts.append(
                    {
                        "month": month,
                        "rating": forecast.get("month_rating", 5),
                        "summary": forecast.get("theme", ""),
                    }
                )
                if "month_rating" in forecast:
                    yearly_ratings.append(forecast["month_rating"])
            except Exception as month_err:
                logger.warning(f"Failed to calculate month {month} for yearly: {month_err}")

        avg_rating = sum(yearly_ratings) / len(yearly_ratings) if yearly_ratings else 5

        return {
            "year": now.year,
            "yearly_rating": round(avg_rating, 1),
            "monthly_forecasts": monthly_forecasts,
            "overall_theme": "Yearly forecast aggregating monthly analysis",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate yearly forecast for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate forecast",
        ) from e
