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
    """Load user's birth chart from database."""
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
            "planets": json.loads(row["planets"])
            if isinstance(row["planets"], str)
            else (row["planets"] or {}),
            "lagna_rashi": row.get("lagna_rashi"),
            "moon_rashi": row.get("moon_rashi"),
            "moon_nakshatra": row.get("moon_nakshatra"),
            "ayanamsa": row.get("ayanamsa"),
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


def _build_natal_planets(planets: dict) -> dict[str, Any]:
    """Build natal planets dict for forecast functions."""
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


def _extract_moon_longitude(planets: dict) -> float | None:
    """Extract moon longitude — planet names are dict KEYS, not a 'name' field."""
    moon_data = planets.get("moon", {})
    if isinstance(moon_data, dict) and "longitude" in moon_data:
        return float(moon_data["longitude"])
    return None


@router.get("/daily")
async def get_daily_forecast_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get daily forecast. Available to all tiers."""
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_longitude = _extract_moon_longitude(chart.get("planets", {}))

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        forecast = get_daily_forecast(
            birth_datetime=birth_dt.isoformat(),
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
    """Get weekly forecast. Pro and premium tiers."""
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
        moon_longitude = _extract_moon_longitude(chart.get("planets", {}))

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        forecast = get_weekly_forecast(
            birth_datetime=birth_dt.isoformat(),
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
    """Get monthly forecast. Pro and premium tiers."""
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
        moon_longitude = _extract_moon_longitude(chart.get("planets", {}))

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        now = datetime.now()
        if month is None:
            month = now.month
        if year is None:
            year = now.year

        forecast = get_monthly_forecast(
            birth_datetime=birth_dt.isoformat(),
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
    """Get yearly forecast. Premium tier only."""
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
        moon_longitude = _extract_moon_longitude(chart.get("planets", {}))

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        now = datetime.now()
        monthly_forecasts = []
        yearly_ratings = []

        for m in range(1, 13):
            try:
                forecast = get_monthly_forecast(
                    birth_datetime=birth_dt.isoformat(),
                    birth_lat=chart["latitude"],
                    birth_lon=chart["longitude"],
                    natal_planets=natal_planets,
                    moon_longitude=moon_longitude,
                    lagna_rashi=chart["lagna_rashi"],
                    month=m,
                    year=now.year,
                )
                monthly_forecasts.append(
                    {
                        "month": m,
                        "rating": forecast.get("month_rating", 5),
                        "summary": forecast.get("theme", ""),
                    }
                )
                if "month_rating" in forecast:
                    yearly_ratings.append(forecast["month_rating"])
            except Exception as month_err:
                logger.warning(f"Failed to calculate month {m} for yearly: {month_err}")

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
