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
    check_sade_sati,
    get_antardasha_effect,
    get_antardasha_sequence,
    get_current_dasha,
    get_enriched_transit_analysis,
    get_mahadasha_sequence,
    get_pratyantardasha_effect,
    get_pratyantardasha_sequence,
)
from packages.context.src.dasha_transit import cross_analyze
from packages.core.src.knowledge_loader import get_dasha_guide
from packages.cosmos.src import get_all_planets
from packages.cosmos.src.ephemeris import get_julian_day
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

        # Find moon longitude — planets are keyed by name
        moon_data = chart.get("planets", {}).get("moon", {})
        moon_longitude = float(moon_data.get("longitude", 0)) if moon_data else None

        if moon_longitude is None or moon_longitude == 0:
            raise ValueError("Moon position not found in birth chart")

        # Get current dasha
        current = get_current_dasha(birth_dt, moon_longitude)

        # Free tier: current period only (preview for onboarding)
        if access == AccessLevel.PREVIEW:
            md = current.get("mahadasha", {}) if current else {}
            ad = current.get("antardasha", {}) if current else {}
            pd = current.get("pratyantardasha", {}) if current else {}
            # Mahadasha sequence for life chapters
            periods = get_mahadasha_sequence(birth_dt, moon_longitude, 120)

            # Antardasha sequence within current MD
            md_start = md.get("start_date")
            md_end = md.get("end_date")
            ad_seq = []
            if md.get("lord") and md_start and md_end:
                ad_seq = get_antardasha_sequence(md["lord"], md_start, md_end)

            # Pratyantardasha sequence within current AD
            ad_start = ad.get("start_date")
            ad_end = ad.get("end_date")
            pd_seq = []
            if ad.get("lord") and ad_start and ad_end:
                pd_seq = get_pratyantardasha_sequence(ad["lord"], ad_start, ad_end)

            def _fmt_seq(seq: list) -> list:
                return [
                    {
                        "lord": p.get("lord"),
                        "years": p.get("years"),
                        "start": str(p.get("start_date", "")),
                        "end": str(p.get("end_date", "")),
                    }
                    for p in seq
                ]

            # Check Sade Sati using current Saturn transit
            alerts = []
            try:
                now_utc = datetime.utcnow()
                current_jd = get_julian_day(now_utc)
                transit_planets = get_all_planets(current_jd)
                saturn_lon = transit_planets.get("saturn", {}).get("longitude", 0)
                saturn_rashi = int(saturn_lon / 30) % 12
                moon_rashi = chart.get("moon_rashi")
                if moon_rashi is not None:
                    # Convert moon_rashi name to index if needed
                    rashi_names = [
                        "aries",
                        "taurus",
                        "gemini",
                        "cancer",
                        "leo",
                        "virgo",
                        "libra",
                        "scorpio",
                        "sagittarius",
                        "capricorn",
                        "aquarius",
                        "pisces",
                    ]
                    if isinstance(moon_rashi, str):
                        moon_rashi_idx = (
                            rashi_names.index(moon_rashi.lower())
                            if moon_rashi.lower() in rashi_names
                            else 0
                        )
                    else:
                        moon_rashi_idx = int(moon_rashi)
                    sade_sati = check_sade_sati(moon_rashi_idx, saturn_rashi)
                    if sade_sati.get("active"):
                        alerts.append(
                            {
                                "type": "sade_sati",
                                "phase": sade_sati.get("phase"),
                                "description": sade_sati.get("description"),
                            }
                        )
            except Exception as alert_err:
                logger.warning(f"Failed to check alerts: {alert_err}")

            return {
                "current": {
                    "mahadasha_lord": md.get("lord"),
                    "mahadasha_start": str(md.get("start_date", "")),
                    "mahadasha_end": str(md.get("end_date", "")),
                    "remaining_years": md.get("years_remaining")
                    or md.get("days_remaining", 0) / 365.25,
                    "antardasha_lord": ad.get("lord"),
                    "antardasha_start": str(ad.get("start_date", "")),
                    "antardasha_end": str(ad.get("end_date", "")),
                    "pratyantardasha_lord": pd.get("lord"),
                    "pratyantardasha_start": str(pd.get("start_date", "")),
                    "pratyantardasha_end": str(pd.get("end_date", "")),
                },
                "mahadasha_sequence": _fmt_seq(periods),
                "antardasha_sequence": _fmt_seq(ad_seq),
                "pratyantardasha_sequence": _fmt_seq(pd_seq),
                "alerts": alerts,
            }

        # Pro+ tier: full timeline
        periods = get_mahadasha_sequence(birth_dt, moon_longitude, 120)

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


_POSITIVE_KEYWORDS = {
    "excellent",
    "peak",
    "growth",
    "gain",
    "success",
    "favorable",
    "benefit",
    "prosperity",
    "wealth",
    "promotion",
    "strong",
    "improve",
    "good",
    "best",
    "powerful",
    "fortunate",
    "auspicious",
    "rise",
    "expand",
    "opportunity",
}
_NEGATIVE_KEYWORDS = {
    "challenge",
    "conflict",
    "disease",
    "loss",
    "accident",
    "obstacle",
    "difficulty",
    "stress",
    "decline",
    "weak",
    "danger",
    "enemy",
    "debt",
    "setback",
    "delay",
    "tension",
    "trouble",
    "unfavorable",
    "problem",
    "fear",
}
_AREA_KEYWORDS: dict[str, set[str]] = {
    "career": {
        "career",
        "profession",
        "job",
        "promotion",
        "status",
        "authority",
        "business",
        "work",
    },
    "health": {
        "health",
        "disease",
        "vitality",
        "body",
        "physical",
        "illness",
        "medical",
        "surgery",
    },
    "relationships": {
        "relationship",
        "marriage",
        "partner",
        "love",
        "family",
        "spouse",
        "romantic",
    },
    "finances": {"finance", "wealth", "money", "income", "property", "gain", "loss", "expense"},
    "spiritual": {"spiritual", "meditation", "mantra", "temple", "dharma", "karma", "devotion"},
}


def _compute_area_scores(
    md_guide: dict[str, Any],
    ad_effects: dict[str, Any] | None,
    pd_effects: dict[str, Any] | None,
) -> dict[str, int]:
    """Score 5 life areas 1-10 from effects text using keyword matching."""
    scores: dict[str, float] = {
        "career": 5,
        "health": 5,
        "relationships": 5,
        "finances": 5,
        "spiritual": 5,
    }

    # Collect all text fields into one blob per area
    area_texts: dict[str, str] = {}
    for area in scores:
        parts: list[str] = []
        # MD guide has explicit area fields
        if md_guide.get(area):
            parts.append(str(md_guide[area]).lower())
        if md_guide.get("challenges"):
            parts.append(str(md_guide["challenges"]).lower())
        if md_guide.get("opportunities"):
            parts.append(str(md_guide["opportunities"]).lower())
        # AD effects have area fields too
        if ad_effects:
            if ad_effects.get(area):
                parts.append(str(ad_effects[area]).lower())
            for key in ("positive", "negative", "general_effects"):
                val = ad_effects.get(key)
                if isinstance(val, list):
                    parts.extend(str(v).lower() for v in val)
                elif val:
                    parts.append(str(val).lower())
        # PD effects
        if pd_effects:
            if pd_effects.get(area):
                parts.append(str(pd_effects[area]).lower())
            effects_list = pd_effects.get("effects")
            if isinstance(effects_list, list):
                parts.extend(str(v).lower() for v in effects_list)
        area_texts[area] = " ".join(parts)

    # Score each area by sentiment of relevant text
    for area, text in area_texts.items():
        if not text:
            continue
        words = set(text.split())
        pos_count = len(words & _POSITIVE_KEYWORDS)
        neg_count = len(words & _NEGATIVE_KEYWORDS)
        # Also check area-specific keyword density
        relevance = len(words & _AREA_KEYWORDS.get(area, set()))
        # Net sentiment: each positive word +0.5, negative -0.5, relevance +0.2
        delta = (pos_count * 0.5) - (neg_count * 0.5) + (relevance * 0.2)
        scores[area] = max(1, min(10, round(5 + delta)))

    return {area: int(val) for area, val in scores.items()}


@router.get("/dasha/effects")
async def get_dasha_effects(
    md: str,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
    ad: str | None = None,
    pd: str | None = None,
) -> dict[str, Any]:
    """Get dasha effects and cross-analysis for MD/AD/PD combination.

    Args:
        md: Mahadasha lord name (required).
        ad: Antardasha lord name (optional).
        pd: Pratyantardasha lord name (optional).
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict with mahadasha, antardasha, pratyantardasha effects,
        cross_analysis, and area_scores.
    """
    try:
        access = await check_feature_access(
            "analysis_dasha", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock dasha effects"},
                access,
                "Upgrade to Pro to unlock dasha effects",
            ).model_dump()

        # Load MD guide — knowledge content available at all tiers
        guide_data = get_dasha_guide()
        guide = guide_data.get("dasha_guide", guide_data)
        md_guide = guide.get(md.lower(), {})

        # Build MD response (full knowledge for all tiers)
        md_response: dict[str, Any] = {
            "lord": md.lower(),
            "duration_years": md_guide.get("duration_years"),
            "theme": md_guide.get("theme", ""),
            "focus_areas": md_guide.get("focus_areas", []),
            "career": md_guide.get("career", ""),
            "health": md_guide.get("health", ""),
            "relationships": md_guide.get("relationships", ""),
            "spiritual": md_guide.get("spiritual", ""),
            "challenges": md_guide.get("challenges", ""),
            "opportunities": md_guide.get("opportunities", ""),
            "practical_advice": md_guide.get("practical_advice", []),
        }

        result: dict[str, Any] = {"mahadasha": md_response}

        # AD effects (from knowledge JSON — available at all tiers)
        ad_effects: dict[str, Any] | None = None
        if ad:
            ad_effects = get_antardasha_effect(md.lower(), ad.lower())
            if ad_effects:
                result["antardasha"] = {"lord": ad.lower(), **ad_effects}

        # PD effects (from knowledge JSON — available at all tiers)
        pd_effects: dict[str, Any] | None = None
        if ad and pd:
            pd_effects = get_pratyantardasha_effect(md.lower(), ad.lower(), pd.lower())
            if pd_effects:
                result["pratyantardasha"] = {"lord": pd.lower(), **pd_effects}

        # Area scores (derived from knowledge text — available at all tiers)
        result["area_scores"] = _compute_area_scores(md_guide, ad_effects, pd_effects)

        # Cross-analysis (requires birth chart + live transits — pro+ only)
        if access != AccessLevel.PREVIEW:
            chart = await _load_birth_chart(db, str(current_user.id))
            if chart:
                try:
                    planets = _build_planets_for_analysis(chart.get("planets", {}))
                    now_utc = datetime.utcnow()
                    current_jd = get_julian_day(now_utc)
                    transit_planets = get_all_planets(current_jd)
                    transit_dict: dict[str, dict[str, Any]] = {}
                    for pname, pdata in transit_planets.items():
                        if isinstance(pdata, dict):
                            transit_dict[pname] = {
                                "longitude": float(pdata.get("longitude", 0)),
                                "rashi": int(float(pdata.get("longitude", 0))) // 30,
                            }
                    dasha_info = {
                        "mahadasha": md.lower(),
                        "antardasha": ad.lower() if ad else "",
                        "pratyantardasha": pd.lower() if pd else "",
                    }
                    cross = cross_analyze(
                        natal_planets=planets,
                        current_transits=transit_dict,
                        current_dasha=dasha_info,
                        lagna_rashi=chart.get("lagna_rashi", "aries"),
                        moon_rashi=chart.get("moon_rashi", "aries"),
                    )
                    result["cross_analysis"] = {
                        "active_themes": cross.get("active_themes", []),
                        "strongest_house": cross.get("strongest_house"),
                        "period_quality": cross.get("overall_period_quality", ""),
                        "score": cross.get("score", 50),
                    }
                except Exception as cross_err:
                    logger.warning(f"Cross-analysis failed: {cross_err}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dasha effects for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dasha effects",
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
