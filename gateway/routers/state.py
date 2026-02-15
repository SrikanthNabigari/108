"""State Map endpoints for the 108 Gateway.

Provides state vector computation for the State Map Flutter screen.
Follows the same pattern as gateway/routers/forecast.py.
"""

from __future__ import annotations

import json
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from gateway.dependencies import get_current_user, get_db
from gateway.models import UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.context.src.state_engine import compute_state_range, compute_state_vector

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Helpers (same pattern as forecast.py) ──


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
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


def _build_natal_planets(planets: dict) -> dict[str, Any]:
    """Build natal planets dict for state engine."""
    result = {}
    for planet_name, planet_data in planets.items():
        if isinstance(planet_data, dict):
            result[planet_name] = {
                "longitude": float(planet_data.get("longitude", 0)),
                "latitude": float(planet_data.get("latitude", 0)),
                "speed": float(planet_data.get("speed", 0)),
                "rashi": int(planet_data.get("rashi", 0)),
                "house": int(planet_data.get("house", 0)),
                "nakshatra": planet_data.get("nakshatra"),
                "is_retrograde": planet_data.get("is_retrograde", False),
            }
    return result


def _extract_moon_longitude(planets: dict) -> float | None:
    """Extract moon longitude from planets dict."""
    moon_data = planets.get("moon", {})
    if isinstance(moon_data, dict) and "longitude" in moon_data:
        return float(moon_data["longitude"])
    return None


# ── Endpoints ──


@router.get("/now")
async def get_state_now(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get current state vector — the 'NOW' card data.

    Available to all subscription tiers (free/pro/premium).
    """
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_lon = _extract_moon_longitude(chart.get("planets", {}))
        if moon_lon is None:
            raise ValueError("Moon position not found in birth chart")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        result = compute_state_vector(
            birth_datetime=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_lon,
            lagna_rashi=chart["lagna_rashi"],
            moon_rashi=chart.get("moon_rashi"),
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State now failed for {current_user.id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute state: {e}",
        ) from e


@router.get("/date/{date_str}")
async def get_state_for_date(
    date_str: str,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get state vector for a specific date (YYYY-MM-DD).

    Available to all subscription tiers.
    """
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        ) from None

    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_lon = _extract_moon_longitude(chart.get("planets", {}))
        if moon_lon is None:
            raise ValueError("Moon position not found")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        result = compute_state_vector(
            birth_datetime=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_lon,
            lagna_rashi=chart["lagna_rashi"],
            moon_rashi=chart.get("moon_rashi"),
            query_datetime=query_date.isoformat(),
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State date failed for {current_user.id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute state: {e}",
        ) from e


@router.get("/range")
async def get_state_range(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
    start: str = Query(..., description="Start date YYYY-MM-DD"),
    end: str = Query(..., description="End date YYYY-MM-DD"),
    resolution: str = Query("daily", description="hourly|daily|weekly|monthly|yearly"),
) -> dict[str, Any]:
    """Get state vectors for a date range — powers the heat map.

    Available to all subscription tiers.
    """
    # Validate resolution
    valid_resolutions = ("hourly", "daily", "weekly", "monthly", "yearly")
    if resolution not in valid_resolutions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid resolution. Use one of: {', '.join(valid_resolutions)}",
        )

    # Validate date formats
    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        ) from None

    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        natal_planets = _build_natal_planets(chart.get("planets", {}))
        moon_lon = _extract_moon_longitude(chart.get("planets", {}))
        if moon_lon is None:
            raise ValueError("Moon position not found")

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        result = compute_state_range(
            birth_datetime=birth_dt.isoformat(),
            birth_lat=chart["latitude"],
            birth_lon=chart["longitude"],
            natal_planets=natal_planets,
            moon_longitude=moon_lon,
            lagna_rashi=chart["lagna_rashi"],
            moon_rashi=chart.get("moon_rashi"),
            start_date=start,
            end_date=end,
            resolution=resolution,
        )

        # Load user events for overlay
        try:
            rows = await db.fetch(
                "SELECT * FROM user_events WHERE user_id = $1 "
                "AND event_date >= $2 AND event_date <= $3 "
                "ORDER BY event_date",
                str(current_user.id),
                datetime.strptime(start, "%Y-%m-%d").date(),
                datetime.strptime(end, "%Y-%m-%d").date(),
            )
            result["events"] = [
                {
                    "id": str(row["id"]),
                    "date": (row["event_date"].isoformat() if row["event_date"] else ""),
                    "type": row["event_type"],
                    "description": row["event_description"],
                    "actual_rating": (
                        float(row["actual_rating"]) if row.get("actual_rating") else None
                    ),
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning(f"Failed to load events: {e}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State range failed for {current_user.id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute state range: {e}",
        ) from e
