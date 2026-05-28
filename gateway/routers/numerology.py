"""Numerology endpoints for the 108 Gateway."""

from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from gateway.dependencies import get_current_user, get_db
from gateway.models import UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.self.src.numerology import (
    NUMBER_PLANET_MAP,
    _sum_digits,
    analyze_name,
    calculate_full_profile,
    calculate_personal_day,
    calculate_personal_month,
    cross_reference_jyotish,
    get_compound_meaning,
    get_number_compatibility,
    get_personal_cycles,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / Response Models ──


class NameAnalysisRequest(BaseModel):
    """Request body for name analysis."""

    name: str = Field(..., min_length=1, max_length=200)
    system: str = Field(default="chaldean", pattern="^(chaldean|pythagorean)$")


# ── Helpers ──


async def _load_birth_chart(db: Any, user_id: str) -> dict[str, Any] | None:
    """Load user's birth chart from database.

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

        planets_raw = row["planets"]
        houses_raw = row["houses"]
        return {
            "birth_datetime": row["birth_datetime"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "timezone": row["timezone"],
            "planets": json.loads(planets_raw)
            if isinstance(planets_raw, str)
            else (planets_raw or {}),
            "houses": json.loads(houses_raw) if isinstance(houses_raw, str) else (houses_raw or {}),
            "lagna_rashi": row.get("lagna_rashi"),
            "moon_rashi": row.get("moon_rashi"),
            "moon_nakshatra": row.get("moon_nakshatra"),
            "ayanamsa": row.get("ayanamsa"),
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


def _extract_birth_date(chart_row: dict[str, Any]) -> date:
    """Extract a date object from the birth_datetime in a chart row.

    Args:
        chart_row: Chart data dict with 'birth_datetime' field.

    Returns:
        date object from the birth datetime.

    Raises:
        ValueError: If birth_datetime is missing or cannot be parsed.
    """
    birth_dt = chart_row.get("birth_datetime")
    if birth_dt is None:
        raise ValueError("birth_datetime is missing from chart data")
    if isinstance(birth_dt, datetime):
        return birth_dt.date()
    if isinstance(birth_dt, date):
        return birth_dt
    if isinstance(birth_dt, str):
        return datetime.fromisoformat(birth_dt).date()
    raise ValueError(f"Unsupported birth_datetime type: {type(birth_dt)}")


# ── Endpoints ──


@router.get("/profile")
async def get_numerology_profile(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
    name: str | None = None,
) -> dict[str, Any]:
    """Get full numerology profile for the authenticated user.

    Includes psychic number, destiny number, name number (if name provided),
    personal year/month/day cycles, Lo Shu grid analysis, and ruling planets.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
        name: Optional name for name number calculation.

    Returns:
        dict: Complete numerology profile.

    Raises:
        HTTPException: 404 if no birth chart found, 500 on calculation error.
    """
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found. Please set birth details.",
            ) from None

        birth_date = _extract_birth_date(chart)
        profile = calculate_full_profile(birth_date, name=name)

        result = profile.model_dump()

        # Add Jyotish cross-reference if planet data is available
        planets = chart.get("planets", {})
        if planets:
            jyotish_ref = cross_reference_jyotish(
                profile.psychic_number,
                profile.destiny_number,
                birth_chart_planets=planets,
            )
            result["jyotish_cross_reference"] = jyotish_ref

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Numerology profile calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Numerology profile calculation failed: {e}",
        ) from e


@router.get("/cycles")
async def get_numerology_cycles(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
) -> dict[str, Any]:
    """Get personal year/month/day cycles for the authenticated user.

    Returns personal cycles for the specified date or today if not provided.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
        year: Target year (defaults to current year).
        month: Target month (defaults to current month).
        day: Target day (defaults to current day).

    Returns:
        dict: Personal cycle data with year/month/day numbers and meanings.

    Raises:
        HTTPException: 404 if no birth chart found, 500 on calculation error.
    """
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found. Please set birth details.",
            ) from None

        birth_date = _extract_birth_date(chart)
        today = date.today()
        target_date = date(
            year or today.year,
            month or today.month,
            day or today.day,
        )

        cycles = get_personal_cycles(birth_date, target_date)
        return cycles.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Numerology cycles calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Numerology cycles calculation failed: {e}",
        ) from e


@router.post("/name-analysis")
async def post_name_analysis(
    request: NameAnalysisRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
) -> dict[str, Any]:
    """Analyze a name's numerological value.

    Supports both Chaldean (Vedic) and Pythagorean (Western) systems.

    Args:
        request: Name and system to use.
        current_user: Authenticated user context.

    Returns:
        dict: Name analysis with values from the requested system.

    Raises:
        HTTPException: 500 on calculation error.
    """
    try:
        # Get full analysis from both systems
        analysis = analyze_name(request.name)
        result = analysis.model_dump()

        # If pythagorean was specifically requested, indicate the preferred system
        result["preferred_system"] = request.system

        # Add compound meaning for the chaldean value
        compound_meaning = get_compound_meaning(analysis.chaldean_value)
        if compound_meaning:
            result["compound_meaning"] = compound_meaning

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Name analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Name analysis failed: {e}",
        ) from e


@router.get("/compatibility")
async def get_numerology_compatibility(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
    number_1: int | None = Query(default=None, ge=1, le=9),
    number_2: int | None = Query(default=None, ge=1, le=9),
    partner_user_id: str | None = None,
) -> dict[str, Any]:
    """Get number compatibility between two people.

    Either provide two numbers directly, or provide a partner_user_id to
    compare psychic numbers from birth charts.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
        number_1: First number (1-9).
        number_2: Second number (1-9).
        partner_user_id: Partner's user ID for chart-based comparison.

    Returns:
        dict: Compatibility analysis with score, nature, and description.

    Raises:
        HTTPException: 400 if invalid parameters, 404 if charts not found,
            500 on calculation error.
    """
    try:
        if partner_user_id:
            # Fetch both users' birth charts and compare psychic numbers
            user_chart = await _load_birth_chart(db, str(current_user.id))
            if not user_chart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Your birth chart not found. Please set birth details.",
                ) from None

            partner_chart = await _load_birth_chart(db, partner_user_id)
            if not partner_chart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Partner birth chart not found.",
                ) from None

            from packages.self.src.numerology import calculate_psychic_number

            user_birth_date = _extract_birth_date(user_chart)
            partner_birth_date = _extract_birth_date(partner_chart)

            num1, _ = calculate_psychic_number(user_birth_date.day)
            num2, _ = calculate_psychic_number(partner_birth_date.day)
        elif number_1 is not None and number_2 is not None:
            num1 = number_1
            num2 = number_2
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Provide either number_1 and number_2 (1-9) or "
                    "partner_user_id for chart-based comparison."
                ),
            ) from None

        compatibility = get_number_compatibility(num1, num2)
        return compatibility.model_dump()

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Numerology compatibility failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Numerology compatibility calculation failed: {e}",
        ) from e


@router.get("/daily")
async def get_daily_numerology(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    db: Annotated[Any, Depends(get_db)],
    date_str: str | None = Query(default=None, alias="date"),
) -> dict[str, Any]:
    """Get daily numerology forecast for the authenticated user.

    Returns the personal day number, ruling planet, compound meaning,
    and lucky numbers for the specified date.

    Args:
        current_user: Authenticated user context.
        db: Database connection.
        date_str: ISO date string (defaults to today).

    Returns:
        dict: Daily numerology with personal_day, ruling_planet,
            compound_meaning, and lucky_numbers.

    Raises:
        HTTPException: 404 if no birth chart found, 500 on calculation error.
    """
    try:
        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found. Please set birth details.",
            ) from None

        birth_date = _extract_birth_date(chart)

        target_date = date.fromisoformat(date_str) if date_str else date.today()

        personal_day = calculate_personal_day(birth_date, target_date)
        ruling_planet = NUMBER_PLANET_MAP.get(personal_day, "unknown")

        # Calculate the compound number for today (target_day + personal_month sum)
        pm = calculate_personal_month(birth_date, target_date.year, target_date.month)
        compound_sum = pm + _sum_digits(target_date.day)
        compound = compound_sum if compound_sum >= 10 else None
        compound_meaning = get_compound_meaning(compound)

        # Lucky numbers: the personal day number itself plus friendly numbers
        friendly = {
            1: [1, 3, 5, 9],
            2: [2, 6, 7],
            3: [1, 3, 5, 6, 9],
            4: [4, 6, 8],
            5: [1, 3, 5, 9],
            6: [2, 3, 6, 9],
            7: [2, 5, 7],
            8: [4, 6, 8],
            9: [1, 3, 5, 6, 9],
        }
        lucky_numbers = friendly.get(personal_day, [personal_day])

        return {
            "date": target_date.isoformat(),
            "personal_day": personal_day,
            "ruling_planet": ruling_planet,
            "compound_number": compound,
            "compound_meaning": compound_meaning,
            "lucky_numbers": lucky_numbers,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Daily numerology calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Daily numerology calculation failed: {e}",
        ) from e
