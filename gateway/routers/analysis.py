"""Analysis endpoints for the 108 Gateway."""

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
from gateway.models import AccessLevel, KPPredictionRequest, UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.context.src import (
    get_current_dasha,
    get_enriched_transit_analysis,
    get_mahadasha_sequence,
)
from packages.self.src import (
    DoshaDetector,
    YogaDetector,
    get_kp_prediction,
    get_kp_significators,
    recommend_remedies,
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
            "houses": json.loads(row["houses"]) if row["houses"] else {},
            "lagna_rashi": row["lagna_rashi"],
            "moon_rashi": row["moon_rashi"],
            "moon_nakshatra": row["moon_nakshatra"],
            "ayanamsa": row["ayanamsa"],
        }
    except Exception as e:
        logger.error(f"Failed to load birth chart: {e}")
        return None


def _build_planets_for_analysis(planets: dict) -> dict[str, Any]:
    """
    Build planets dict for analysis functions.

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
                "is_retrograde": planet_data.get("is_retrograde", False),
            }
    return result


@router.get("/yogas")
async def get_yogas(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get detected yogas in birth chart.

    Gated feature - pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Detected yogas (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "analysis_yogas", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock yoga analysis"},
                access,
                "Upgrade to Pro to unlock yoga analysis",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        planets = _build_planets_for_analysis(chart.get("planets", {}))

        # Detect yogas
        detector = YogaDetector(
            planets=planets,
            lagna_rashi=chart["lagna_rashi"],
            moon_rashi=chart["moon_rashi"],
        )
        yogas = detector.detect_all()

        # Free tier: names only
        if access == AccessLevel.PREVIEW:
            return {
                "total_yogas": len(yogas),
                "yogas": [
                    {
                        "name": yoga.get("name"),
                        "category": yoga.get("category"),
                    }
                    for yoga in yogas
                ],
            }

        # Pro+ tier: full details
        return {
            "total_yogas": len(yogas),
            "yogas": yogas,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to detect yogas for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze yogas",
        ) from e


@router.get("/doshas")
async def get_doshas(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get detected doshas in birth chart.

    Gated feature - pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Detected doshas (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "analysis_doshas", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock dosha analysis"},
                access,
                "Upgrade to Pro to unlock dosha analysis",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        planets = _build_planets_for_analysis(chart.get("planets", {}))

        # Detect doshas
        detector = DoshaDetector(
            planets=planets,
            lagna_rashi=chart["lagna_rashi"],
            moon_rashi=chart["moon_rashi"],
        )
        doshas = detector.detect_all()

        # Free tier: names only
        if access == AccessLevel.PREVIEW:
            return {
                "total_doshas": len(doshas),
                "doshas": [
                    {
                        "name": dosha.get("name"),
                        "severity": dosha.get("severity"),
                    }
                    for dosha in doshas
                ],
            }

        # Pro+ tier: full details including remedies
        remedies_list = []
        for dosha in doshas:
            try:
                dosha_remedies = recommend_remedies(
                    active_doshas=[dosha],
                    weak_planets=[],
                    current_dasha={},
                    lagna_rashi=chart["lagna_rashi"],
                )
                remedies_list.append(
                    {
                        "dosha_name": dosha.get("name"),
                        "remedies": dosha_remedies,
                    }
                )
            except Exception as remedy_err:
                logger.warning(f"Failed to get remedies for dosha: {remedy_err}")

        return {
            "total_doshas": len(doshas),
            "doshas": doshas,
            "remedies": remedies_list,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to detect doshas for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze doshas",
        ) from e


@router.get("/dasha")
async def get_dasha_timeline(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get dasha timeline (Vimshottari dasha periods).

    Gated feature - pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Dasha periods (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "analysis_dasha", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock dasha analysis"},
                access,
                "Upgrade to Pro to unlock dasha analysis",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        birth_dt = chart["birth_datetime"]
        if isinstance(birth_dt, str):
            birth_dt = datetime.fromisoformat(birth_dt)

        # Find moon longitude
        moon_longitude = None
        for planet_data in chart.get("planets", {}).values():
            if isinstance(planet_data, dict) and planet_data.get("name") == "moon":
                moon_longitude = float(planet_data.get("longitude", 0))
                break

        if moon_longitude is None:
            raise ValueError("Moon position not found in birth chart")

        # Get current dasha
        current = get_current_dasha(
            birth_datetime_iso=birth_dt.isoformat(),
            moon_longitude=moon_longitude,
        )

        # Free tier: only current mahadasha
        if access == AccessLevel.PREVIEW:
            return {
                "current_mahadasha": current.get("mahadasha_lord"),
                "mahadasha_start": current.get("mahadasha_start"),
                "mahadasha_end": current.get("mahadasha_end"),
                "remaining_years": current.get("remaining_years"),
            }

        # Pro+ tier: full timeline
        periods = get_mahadasha_sequence(
            birth_datetime_iso=birth_dt.isoformat(),
            moon_longitude=moon_longitude,
            years=120,
        )

        return {
            "current": current,
            "mahadasha_sequence": periods,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate dasha timeline for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate dasha timeline",
        ) from e


@router.get("/transits")
async def get_transit_analysis(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get transit analysis (Gochara).

    Gated feature - pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Transit analysis (gated by subscription tier).

    Raises:
        HTTPException: 401 if not authenticated, 403 if locked for
            tier, 404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access(
            "analysis_transits", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock transit analysis"},
                access,
                "Upgrade to Pro to unlock transit analysis",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        # Build transit positions dict (would come from current ephemeris)
        # For now, use a placeholder with standard transit format
        transit_positions = {
            "sun": {"sign": chart["lagna_rashi"], "nakshatra": ""},
            "moon": {"sign": chart["moon_rashi"], "nakshatra": ""},
            "mars": {"sign": chart["lagna_rashi"], "nakshatra": ""},
            "mercury": {"sign": chart["moon_rashi"], "nakshatra": ""},
            "jupiter": {"sign": chart["lagna_rashi"], "nakshatra": ""},
            "venus": {"sign": chart["moon_rashi"], "nakshatra": ""},
            "saturn": {"sign": chart["lagna_rashi"], "nakshatra": ""},
            "rahu": {"sign": chart["moon_rashi"], "nakshatra": ""},
            "ketu": {"sign": chart["lagna_rashi"], "nakshatra": ""},
        }

        # Get enriched transit analysis
        analysis = get_enriched_transit_analysis(
            natal_moon_rashi=chart["moon_rashi"],
            transit_positions=transit_positions,
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate transit analysis for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze transits",
        ) from e


@router.post("/kp")
async def get_kp_predictions(
    request: KPPredictionRequest,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """
    Get KP (Krishnamurti Paddhati) predictions.

    Premium tier only. Uses cuspal sub-lords for precise timing.

    Args:
        request: KP prediction request with event type.
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: KP predictions (premium only).

    Raises:
        HTTPException: 401 if not authenticated, 403 if not premium,
            404 if no birth chart, 500 if calculation fails.
    """
    try:
        access = await check_feature_access("analysis_kp", current_user.subscription_tier, config)

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Premium only feature"},
                access,
                "Upgrade to Premium to unlock KP predictions",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        planets = _build_planets_for_analysis(chart.get("planets", {}))
        houses = chart.get("houses", {})

        # Get cusps as list (12 house cusps in order)
        cusps = []
        for i in range(1, 13):
            cusp = houses.get(f"house_{i}", {})
            if isinstance(cusp, dict):
                cusps.append(float(cusp.get("longitude", 0)))
            else:
                cusps.append(float(cusp))

        # Build planets dict for KP (needs longitude)
        planets_for_kp = {}
        for planet_name, planet_data in planets.items():
            planets_for_kp[planet_name] = planet_data.get("longitude", 0)

        # Get KP prediction
        prediction = get_kp_prediction(
            planets=planets_for_kp,
            cusps=cusps,
            query_datetime=datetime.now().isoformat(),
            query_type=request.event_type,
        )

        # Get significators for the event
        significators = get_kp_significators(
            event_type=request.event_type,
            planets=planets_for_kp,
            cusps=cusps,
        )

        return {
            "event_type": request.event_type,
            "prediction": prediction,
            "significators": significators,
            "timing": request.timing_preference,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate KP predictions for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate KP predictions",
        ) from e
