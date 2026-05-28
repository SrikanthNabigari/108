"""Analysis endpoints for the 108 Gateway."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from gateway.dependencies import get_app_config, get_current_user, get_db
from gateway.middleware.entitlements import check_feature_access, gate_response
from gateway.models import AccessLevel, KPPredictionRequest, UserContext

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.context.src import (
    check_dhaiya,
    check_sade_sati,
    find_upcoming_aspects,
    get_antardasha_effect,
    get_antardasha_sequence,
    get_current_dasha,
    get_dhaiya_dates,
    get_enriched_transit_analysis,
    get_gochara,
    get_mahadasha_sequence,
    get_pratyantardasha_effect,
    get_pratyantardasha_sequence,
    get_sade_sati_dates,
    get_sookshma_dasha_effect,
    get_sookshma_dasha_sequence,
    get_transit_natal_aspects,
    get_transit_positions,
    get_transit_snapshot,
)
from packages.context.src.dasha_interpreter import interpret_dasha_combination
from packages.context.src.dasha_transit import cross_analyze
from packages.context.src.transit_tracker import (
    get_nakshatra_transit_triggers,
    get_upcoming_triggers,
)
from packages.core.src.constants import Planet, Rashi
from packages.core.src.knowledge_loader import (
    get_dasha_guide,
    get_planet_in_house_interpretations,
    get_planet_in_sign_interpretations,
    get_sookshma_dasha_guide,
    load_definition,
)
from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition
from packages.cosmos.src import get_all_planets, longitude_to_nakshatra
from packages.cosmos.src.ephemeris import get_julian_day
from packages.self.src import (
    DoshaDetector,
    StrengthCalculator,
    YogaDetector,
    analyze_transit_lordships,
    get_all_chara_karaka_analysis,
    get_atmakaraka_analysis,
    get_ishta_devata,
    get_kp_prediction,
    get_kp_significators,
    get_lordship_summary,
    get_ruling_planets,
    recommend_remedies,
)
from packages.self.src.kp import KP_HOUSE_GROUPS

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
                "latitude": float(planet_data.get("latitude", 0)),
                "speed": float(planet_data.get("speed", 0)),
                "rashi": int(planet_data.get("rashi", 0)),
                "house": int(planet_data.get("house", 0)),
                "nakshatra": planet_data.get("nakshatra"),
                "is_retrograde": planet_data.get("is_retrograde", False),
            }
    return result


RASHI_LIST = list(Rashi)

RASHI_NAME_TO_IDX: dict[str, int] = {
    "aries": 0,
    "taurus": 1,
    "gemini": 2,
    "cancer": 3,
    "leo": 4,
    "virgo": 5,
    "libra": 6,
    "scorpio": 7,
    "sagittarius": 8,
    "capricorn": 9,
    "aquarius": 10,
    "pisces": 11,
}


def _rashi_to_int(rashi: str | int | None) -> int:
    """Convert rashi name or int to 0-11 index."""
    if rashi is None:
        return 0
    if isinstance(rashi, int):
        return rashi % 12
    return RASHI_NAME_TO_IDX.get(rashi.lower(), 0)


def _build_chart_for_doshas(chart: dict) -> BirthChart:
    """Construct BirthChart from DB dict for DoshaDetector."""
    # Determine lagna index (0-11) for house calculation
    lagna_str = chart.get("lagna_rashi", "aries")
    lagna_idx = RASHI_NAME_TO_IDX.get(str(lagna_str).lower(), 0)

    planets_dict: dict[Planet, PlanetPosition] = {}
    for pname, pdata in chart.get("planets", {}).items():
        if not isinstance(pdata, dict):
            continue
        try:
            planet = Planet(pname)
        except ValueError:
            continue
        lon = float(pdata.get("longitude", 0))
        rashi_idx = int(pdata.get("rashi", int(lon / 30) % 12))
        nak_info = longitude_to_nakshatra(lon)

        # Compute house from lagna if not stored in DB
        stored_house = pdata.get("house")
        if isinstance(stored_house, int) and 1 <= stored_house <= 12:
            house = stored_house
        else:
            house = ((rashi_idx - lagna_idx) % 12) + 1

        planets_dict[planet] = PlanetPosition(
            planet=planet,
            longitude=lon,
            latitude=float(pdata.get("latitude", 0.0)),
            speed=float(pdata.get("speed", 0.0)),
            rashi=RASHI_LIST[rashi_idx % 12],
            rashi_degree=lon % 30,
            nakshatra=nak_info.get("name", ""),
            nakshatra_pada=nak_info.get("pada", 1),
            nakshatra_lord=Planet(nak_info.get("lord", "ketu")),
            is_retrograde=pdata.get("is_retrograde", False),
            house=house,
        )

    houses = chart.get("houses", {})
    asc = float(houses.get("ascendant", 0))
    mc = float(houses.get("mc", 0))
    cusps: list[float] = []
    for i in range(1, 13):
        h = houses.get(f"house_{i}")
        if isinstance(h, dict):
            cusps.append(float(h.get("longitude", (i - 1) * 30)))
        else:
            cusps.append(float(h if h is not None else (i - 1) * 30))

    lagna_str = chart.get("lagna_rashi", "aries")
    moon_str = chart.get("moon_rashi", "aries")

    birth_dt = chart.get("birth_datetime", datetime.utcnow())
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    return BirthChart(
        user_id="",
        birth_data=BirthData(
            datetime_utc=birth_dt,
            latitude=chart.get("latitude", 0),
            longitude=chart.get("longitude", 0),
            timezone="UTC",
        ),
        planets=planets_dict,
        houses=HouseCusps(ascendant=asc, mc=mc, cusps=cusps),
        lagna_rashi=Rashi(lagna_str),
        moon_rashi=Rashi(moon_str),
        moon_nakshatra=chart.get("moon_nakshatra", ""),
        ayanamsa=chart.get("ayanamsa") or 0.0,
        calculated_at=datetime.utcnow(),
    )


def _detect_dosha_markers(chart: dict) -> dict[str, list[dict]]:
    """Detect natal doshas and return planet -> marker mapping."""
    try:
        chart_obj = _build_chart_for_doshas(chart)
        detector = DoshaDetector()
        detected = detector.detect_all(chart_obj)

        markers: dict[str, list[dict]] = {}
        for dosha in detected:
            marker = {
                "dosha_id": dosha.dosha_id,
                "name": dosha.name,
                "severity": dosha.severity,
                "description": dosha.description,
                "remedies": dosha.remedies,
            }
            for planet in dosha.involved_planets:
                pname = planet.value if hasattr(planet, "value") else str(planet)
                markers.setdefault(pname, []).append(marker)
        return markers
    except Exception as e:
        logger.warning(f"Dosha detection failed: {e}")
        return {}


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

        # Detect yogas using BirthChart model
        chart_obj = _build_chart_for_doshas(chart)
        detector = YogaDetector()
        detected = detector.detect_all_yogas(chart_obj)

        # Enrich with effects/interpretation from yoga rules
        yoga_rules = detector.yoga_rules
        yogas = []
        for y in detected:
            rule = yoga_rules.get(y.yoga_id, {})
            entry: dict[str, Any] = {
                "yoga_id": y.yoga_id,
                "name": y.name,
                "category": y.category.value if hasattr(y.category, "value") else str(y.category),
                "is_present": y.is_present,
                "strength": y.strength,
                "involved_planets": [p.value for p in y.involved_planets],
                "description": y.description,
                "effects": rule.get("effects", []),
            }
            # Add conditions_met from rule for "Why it forms"
            conditions = rule.get("detection", {}).get("conditions", [])
            if conditions:
                entry["conditions_met"] = [
                    c.get("type", "").replace("_", " ").title() for c in conditions
                ]
            yogas.append(entry)

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

        # Detect doshas using BirthChart model
        chart_obj = _build_chart_for_doshas(chart)
        detector = DoshaDetector()
        detected = detector.detect_all(chart_obj)

        # Enrich with effects/conditions from dosha rules
        doshas = []
        for d in detected:
            rule = detector.dosha_rules.get(d.dosha_id, {})
            entry: dict[str, Any] = {
                "dosha_id": d.dosha_id,
                "name": d.name,
                "is_present": d.is_present,
                "severity": d.severity,
                "involved_planets": [p.value for p in d.involved_planets],
                "description": d.description,
                "remedies": d.remedies or rule.get("remedies", []),
                "effects": rule.get("effects", []),
            }
            conditions = rule.get("detection", {}).get("conditions", [])
            if conditions:
                entry["conditions_met"] = [
                    c.get("type", "").replace("_", " ").title() for c in conditions
                ]
            doshas.append(entry)

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

        # Extract current period components
        md = current.get("mahadasha", {}) if current else {}
        ad = current.get("antardasha", {}) if current else {}
        pd = current.get("pratyantardasha", {}) if current else {}
        sd = current.get("sookshma_dasha", {}) if current else {}

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

        # Sookshma Dasha sequence within current PD
        pd_start = pd.get("start_date")
        pd_end = pd.get("end_date")
        sd_seq = []
        if pd.get("lord") and pd_start and pd_end:
            pd_start_dt = (
                datetime.fromisoformat(pd_start) if isinstance(pd_start, str) else pd_start
            )
            pd_end_dt = datetime.fromisoformat(pd_end) if isinstance(pd_end, str) else pd_end
            sd_seq = get_sookshma_dasha_sequence(pd["lord"], pd_start_dt, pd_end_dt)

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
                    sade_sati_alert = {
                        "type": "sade_sati",
                        "phase": sade_sati.get("phase"),
                        "description": sade_sati.get("description"),
                        "effects": sade_sati.get("effects", []),
                        "remedies": sade_sati.get("remedies", []),
                        "duration_years": sade_sati.get("duration_years"),
                        "house_from_moon": sade_sati.get("house_from_moon"),
                    }
                    try:
                        ss_dates = get_sade_sati_dates(moon_rashi_idx, saturn_rashi)
                        sade_sati_alert["phase_dates"] = ss_dates.get("phase_dates", {})
                    except Exception:
                        pass
                    alerts.append(sade_sati_alert)

                dhaiya = check_dhaiya(moon_rashi_idx, saturn_rashi)
                if dhaiya.get("active"):
                    dhaiya_alert = {
                        "type": "dhaiya",
                        "dhaiya_type": dhaiya.get("type"),
                        "description": dhaiya.get("description"),
                        "effects": dhaiya.get("effects", []),
                        "remedies": dhaiya.get("remedies", []),
                        "duration_years": dhaiya.get("duration_years"),
                        "house_from_moon": dhaiya.get("house_from_moon"),
                    }
                    try:
                        dh_dates = get_dhaiya_dates(moon_rashi_idx, saturn_rashi)
                        dhaiya_alert["phase_dates"] = dh_dates.get("phase_dates", {})
                    except Exception:
                        pass
                    alerts.append(dhaiya_alert)
        except Exception as alert_err:
            logger.warning(f"Failed to check alerts: {alert_err}")

        dosha_markers = _detect_dosha_markers(chart) if chart else {}

        # Enrich with dasha guide data (theme, focus areas, practical advice)
        guide_data = get_dasha_guide()
        guide = guide_data.get("dasha_guide", guide_data)
        current_md_lord = (md.get("lord") or "").lower()
        current_guide = guide.get(current_md_lord, {})

        # Add theme + BPHS enrichment to each MD in the sequence
        md_seq_enriched = _fmt_seq(periods)
        lagna_rashi_name = chart.get("lagna_rashi", "aries") if chart else "aries"
        lagna_idx = _SIGN_TO_RASHI.get(
            lagna_rashi_name.lower() if isinstance(lagna_rashi_name, str) else "aries", 0
        )
        natal_planets = chart.get("planets", {}) if chart else {}

        from packages.self.src.transit_lordship import classify_planet_role

        for p in md_seq_enriched:
            lord_name = (p.get("lord") or "").lower()
            lord_guide = guide.get(lord_name, {})
            p["theme"] = lord_guide.get("theme", "")
            try:
                role = classify_planet_role(lord_name, lagna_idx)
                p["functional_nature"] = role["functional_nature"]
                p["houses_ruled"] = role["houses_ruled"]
            except Exception:
                pass

        # BPHS chart-specific analysis for current period
        bphs_data: dict[str, Any] | None = None
        if chart and natal_planets:
            try:
                bphs_data = interpret_dasha_combination(
                    md=current_md_lord,
                    ad=ad.get("lord", "").lower() or None,
                    pd=pd.get("lord", "").lower() or None,
                    natal_planets=_build_planets_for_analysis(natal_planets),
                    lagna_index=lagna_idx,
                )
            except Exception as bphs_err:
                logger.warning(f"BPHS dasha analysis failed: {bphs_err}")

        current_block: dict[str, Any] = {
            "mahadasha_lord": md.get("lord"),
            "mahadasha_start": str(md.get("start_date", "")),
            "mahadasha_end": str(md.get("end_date", "")),
            "remaining_years": md.get("years_remaining") or md.get("days_remaining", 0) / 365.25,
            "antardasha_lord": ad.get("lord"),
            "antardasha_start": str(ad.get("start_date", "")),
            "antardasha_end": str(ad.get("end_date", "")),
            "pratyantardasha_lord": pd.get("lord"),
            "pratyantardasha_start": str(pd.get("start_date", "")),
            "pratyantardasha_end": str(pd.get("end_date", "")),
            "sookshma_lord": sd.get("lord"),
            "sookshma_start": str(sd.get("start_date", "")),
            "sookshma_end": str(sd.get("end_date", "")),
            "theme": current_guide.get("theme", ""),
            "focus_areas": current_guide.get("focus_areas", []),
            "practical_advice": current_guide.get("practical_advice", []),
            "challenges": current_guide.get("challenges", ""),
            "opportunities": current_guide.get("opportunities", ""),
        }
        if bphs_data:
            current_block["bphs_analysis"] = bphs_data

        return {
            "current": current_block,
            "mahadasha_sequence": md_seq_enriched,
            "antardasha_sequence": _fmt_seq(ad_seq),
            "pratyantardasha_sequence": _fmt_seq(pd_seq),
            "sookshma_sequence": _fmt_seq(sd_seq),
            "alerts": alerts,
            "dosha_markers": dosha_markers,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate dasha timeline for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate dasha timeline",
        ) from e


# ── Classical area scoring (BPHS lordship-based) ──

_SIGN_TO_RASHI: dict[str, int] = {
    "aries": 0,
    "taurus": 1,
    "gemini": 2,
    "cancer": 3,
    "leo": 4,
    "virgo": 5,
    "libra": 6,
    "scorpio": 7,
    "sagittarius": 8,
    "capricorn": 9,
    "aquarius": 10,
    "pisces": 11,
}

_RASHI_NAMES = [
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

_EXALTATION: dict[str, str] = {
    "sun": "aries",
    "moon": "taurus",
    "mars": "capricorn",
    "mercury": "virgo",
    "jupiter": "cancer",
    "venus": "pisces",
    "saturn": "libra",
}

_DEBILITATION: dict[str, str] = {
    "sun": "libra",
    "moon": "scorpio",
    "mars": "cancer",
    "mercury": "pisces",
    "jupiter": "capricorn",
    "venus": "virgo",
    "saturn": "aries",
}

_OWN_SIGNS: dict[str, list[str]] = {
    "sun": ["leo"],
    "moon": ["cancer"],
    "mars": ["aries", "scorpio"],
    "mercury": ["gemini", "virgo"],
    "jupiter": ["sagittarius", "pisces"],
    "venus": ["taurus", "libra"],
    "saturn": ["capricorn", "aquarius"],
}

# Life areas and their associated houses (primary first)
_AREA_HOUSES: dict[str, list[int]] = {
    "career": [10, 6, 2],
    "relationships": [7, 5, 11],
    "health": [1, 6, 8],
    "finances": [2, 11, 5],
    "spiritual": [9, 12, 5],
    "family": [4, 2, 1],
    "education": [4, 5, 9],
    "travel": [3, 9, 12],
}

# Natural karaka planet for each area
_AREA_KARAKAS: dict[str, str] = {
    "career": "saturn",
    "relationships": "venus",
    "health": "sun",
    "finances": "jupiter",
    "spiritual": "ketu",
    "family": "moon",
    "education": "mercury",
    "travel": "rahu",
}

# Dusthana lords (6,8,12) bring challenges; trikona lords (1,5,9) bring fortune
_TRIKONA_HOUSES = {1, 5, 9}
_DUSTHANA_HOUSES = {6, 8, 12}

# All 8 life area keys for overlay iteration
_AREA_KEYS = list(_AREA_HOUSES.keys())

# House signification labels for focus_areas generation
_HOUSE_THEME_LABELS: dict[int, str] = {
    1: "Self & Personality",
    2: "Wealth & Speech",
    3: "Courage & Communication",
    4: "Home & Education",
    5: "Intelligence & Creativity",
    6: "Service & Health",
    7: "Partnerships & Marriage",
    8: "Transformation & Hidden Matters",
    9: "Dharma & Fortune",
    10: "Career & Status",
    11: "Gains & Aspirations",
    12: "Moksha & Foreign Lands",
}

# ── BPHS Overlay Helpers ──
# These functions generate chart-specific text from interpret_dasha_combination()
# output, replacing generic knowledge text in the dasha effects response.


def _bphs_focus_areas(lord_bphs: dict) -> list[str]:
    """Generate focus areas from houses ruled by the dasha lord.

    Returns top 2 signification themes per ruled house.
    """
    houses = lord_bphs.get("houses_ruled", [])
    if not houses:
        return []
    areas = []
    for h in houses:
        label = _HOUSE_THEME_LABELS.get(h)
        if label:
            areas.append(label)
    return areas


def _bphs_area_text(lord_bphs: dict, area: str) -> str:
    """Generate chart-specific area text from BPHS analysis.

    Checks lordship connection, placement connection, dignity, and
    relevant aspects to produce a 2-3 sentence paragraph.
    """
    area_houses = _AREA_HOUSES.get(area)
    if not area_houses:
        return ""

    houses_ruled = set(lord_bphs.get("houses_ruled", []))
    natal_house = lord_bphs.get("natal_house")
    dignity = lord_bphs.get("dignity", "neutral")
    lord_name = lord_bphs.get("lord", "").title()
    aspects = lord_bphs.get("aspects_received", [])

    sentences = []

    # 1. Lordship connection
    overlap = houses_ruled & set(area_houses)
    if overlap:
        house_labels = []
        for h in sorted(overlap):
            label = _HOUSE_THEME_LABELS.get(h, f"house {h}")
            house_labels.append(f"{h}th ({label.split(' & ')[0].lower()})")
        sentences.append(
            f"As {', '.join(house_labels)} lord, {lord_name} directly activates "
            f"this area through house ownership."
        )

    # 2. Placement connection
    if natal_house and natal_house in area_houses:
        house_label = _HOUSE_THEME_LABELS.get(natal_house, "")
        sentences.append(
            f"Placed in {natal_house}th house"
            + (f" ({house_label})" if house_label else "")
            + " -- personal initiative and direct experience shape outcomes."
        )

    # 3. Dignity modifier
    dignity_text = {
        "exalted": "Exalted dignity delivers strong, amplified results.",
        "own_sign": "In own sign -- confident, natural expression of results.",
        "debilitated": "Debilitated placement weakens natural significations; remedial measures help.",
    }.get(dignity, "")
    if dignity_text and (overlap or (natal_house and natal_house in area_houses)):
        sentences.append(dignity_text)

    # 4. Relevant aspects hitting area houses
    for asp in aspects:
        asp_planet = asp.get("planet", "").title()
        from_house = asp.get("from_house")
        nature = asp.get("nature", "neutral")
        if from_house and from_house in area_houses:
            verb = (
                "strengthens"
                if nature == "benefic"
                else "challenges"
                if nature == "malefic"
                else "influences"
            )
            sentences.append(f"{asp_planet}'s aspect from {from_house}th house {verb} this area.")

    return " ".join(sentences) if sentences else ""


def _bphs_opportunities(lord_bphs: dict) -> str:
    """Generate opportunities text from benefic aspects, good dignity, and yogas."""
    parts = []
    dignity = lord_bphs.get("dignity", "neutral")
    lord_name = lord_bphs.get("lord", "").title()

    # Good dignity
    if dignity == "exalted":
        parts.append(f"Exalted {lord_name} delivers peak results across all significations.")
    elif dignity == "own_sign":
        parts.append(f"{lord_name} in own sign operates with confidence and natural authority.")

    # Benefic aspects
    for asp in lord_bphs.get("aspects_received", []):
        if asp.get("nature") == "benefic":
            asp_planet = asp.get("planet", "").title()
            from_house = asp.get("from_house", "")
            parts.append(
                f"Benefic aspect from {asp_planet} (house {from_house}) strengthens results."
            )

    # Friendly conjunctions
    for conj in lord_bphs.get("conjunctions", []):
        if conj.get("relationship") == "friendly":
            parts.append(f"Conjunction with {conj['planet'].title()} (friend) enhances outcomes.")

    # Yogas
    for yoga in lord_bphs.get("yogas", []):
        parts.append(f"{yoga['name']} active -- amplifies positive potential.")

    return " ".join(parts) if parts else ""


def _bphs_challenges(lord_bphs: dict) -> str:
    """Generate challenges text from malefic aspects, debilitation, combustion."""
    parts = []
    dignity = lord_bphs.get("dignity", "neutral")
    lord_name = lord_bphs.get("lord", "").title()

    # Debilitation
    if dignity == "debilitated":
        parts.append(
            f"Debilitated {lord_name} weakens natural significations -- remedial measures recommended."
        )

    # Combustion
    if lord_bphs.get("is_combust"):
        parts.append(
            f"{lord_name} combust by Sun -- results less visible externally, inner growth emphasized."
        )

    # Retrograde
    if lord_bphs.get("is_retrograde"):
        parts.append(
            "Retrograde energy internalizes results -- patience needed for external outcomes."
        )

    # Malefic aspects
    for asp in lord_bphs.get("aspects_received", []):
        if asp.get("nature") == "malefic":
            asp_planet = asp.get("planet", "").title()
            parts.append(
                f"Malefic aspect from {asp_planet} creates obstacles and competitive pressure."
            )

    # Enemy conjunctions
    for conj in lord_bphs.get("conjunctions", []):
        if conj.get("relationship") == "hostile":
            parts.append(f"Conjunction with {conj['planet'].title()} (enemy) creates tension.")

    return " ".join(parts) if parts else ""


def _bphs_practical_advice(lord_bphs: dict) -> list[str]:
    """Generate practical advice from house_lord_reading and dignity."""
    advice = []
    reading = lord_bphs.get("house_lord_reading", {})
    dignity = lord_bphs.get("dignity", "neutral")

    # House lord reading positives (actionable items)
    for item in reading.get("positive", [])[:3]:
        advice.append(item)

    # Dignity-based advice
    if dignity == "exalted":
        advice.append("Leverage this period's exalted energy for bold initiatives and leadership.")
    elif dignity == "own_sign":
        advice.append(
            "Trust natural instincts -- own-sign placement supports authentic self-expression."
        )
    elif dignity == "debilitated":
        advice.append("Focus on remedial practices and avoid overcommitting during this period.")

    # Yoga-specific advice
    for yoga in lord_bphs.get("yogas", [])[:2]:
        advice.append(
            f"Activate {yoga['name']} potential through conscious effort in related areas."
        )

    return advice


def _bphs_positive(lord_bphs: dict) -> list[str]:
    """Generate positive effects list from benefic aspects, dignity, yogas."""
    items = []
    dignity = lord_bphs.get("dignity", "neutral")
    lord_name = lord_bphs.get("lord", "").title()

    # Good dignity
    if dignity == "exalted":
        items.append(f"Exalted {lord_name} delivers strong results in all significations.")
    elif dignity == "own_sign":
        items.append(f"{lord_name} in own sign brings confident, natural outcomes.")

    # Benefic aspects
    for asp in lord_bphs.get("aspects_received", []):
        if asp.get("nature") == "benefic":
            items.append(
                f"{asp['planet'].title()}'s aspect from house {asp.get('from_house', '')} brings blessings."
            )

    # Friendly conjunctions
    for conj in lord_bphs.get("conjunctions", []):
        if conj.get("relationship") == "friendly":
            items.append(
                f"Conjunction with {conj['planet'].title()} (friend) enhances this sub-period."
            )

    # Yogas
    for yoga in lord_bphs.get("yogas", []):
        items.append(f"{yoga['name']} active -- {yoga.get('strength', 0):.0%} strength.")

    # House lord reading positives
    for item in lord_bphs.get("house_lord_reading", {}).get("positive", [])[:2]:
        items.append(item)

    return items if items else ["Standard results expected for this period."]


def _bphs_negative(lord_bphs: dict) -> list[str]:
    """Generate negative effects list from malefic aspects, debilitation, combustion."""
    items = []
    dignity = lord_bphs.get("dignity", "neutral")
    lord_name = lord_bphs.get("lord", "").title()

    # Debilitation
    if dignity == "debilitated":
        items.append(f"Debilitated {lord_name} weakens natural significations.")

    # Combustion
    if lord_bphs.get("is_combust"):
        items.append(f"{lord_name} combust -- diminished external visibility of results.")

    # Retrograde
    if lord_bphs.get("is_retrograde"):
        items.append("Retrograde motion delays or internalizes expected outcomes.")

    # Malefic aspects
    for asp in lord_bphs.get("aspects_received", []):
        if asp.get("nature") == "malefic":
            items.append(
                f"{asp['planet'].title()}'s malefic aspect from house {asp.get('from_house', '')} creates pressure."
            )

    # Enemy conjunctions
    for conj in lord_bphs.get("conjunctions", []):
        if conj.get("relationship") == "hostile":
            items.append(f"Tension from {conj['planet'].title()} conjunction (enemy relationship).")

    # House lord reading negatives
    for item in lord_bphs.get("house_lord_reading", {}).get("negative", [])[:2]:
        items.append(item)

    return items if items else ["No significant challenges indicated for this period."]


def _compute_area_scores(
    md_lord: str,
    ad_lord: str | None,
    chart: dict[str, Any] | None,
) -> dict[str, int]:
    """Score 8 life areas 1-10 using classical BPHS lordship principles.

    Uses the dasha lord's house ownership, natal placement, dignity, and
    karaka alignment relative to the user's lagna to rate each area.
    Falls back to neutral 5 for all areas if no chart data available.
    """
    scores: dict[str, float] = dict.fromkeys(_AREA_HOUSES, 5.0)

    if not chart:
        return {area: int(val) for area, val in scores.items()}

    lagna = chart.get("lagna_rashi", "").lower()
    if lagna not in _SIGN_TO_RASHI:
        return {area: int(val) for area, val in scores.items()}

    lagna_idx = _SIGN_TO_RASHI[lagna]
    planets = chart.get("planets", {})

    def _get_owned_houses(planet: str) -> list[int]:
        """Get house numbers (1-12) owned by planet from lagna."""
        owned_signs = _OWN_SIGNS.get(planet, [])
        houses = []
        for sign in owned_signs:
            sign_idx = _SIGN_TO_RASHI.get(sign)
            if sign_idx is not None:
                houses.append(((sign_idx - lagna_idx) % 12) + 1)
        return houses

    def _get_placement_house(planet: str) -> int | None:
        """Get house number (1-12) where planet is natally placed."""
        pdata = planets.get(planet, {})
        lon = pdata.get("longitude")
        if lon is None:
            return None
        rashi_idx = int(float(lon)) // 30
        return ((rashi_idx - lagna_idx) % 12) + 1

    def _get_dignity(planet: str) -> str:
        """Determine dignity: exalted, own, debilitated, or neutral."""
        pdata = planets.get(planet, {})
        rashi = pdata.get("rashi", "").lower()
        if not rashi:
            lon = pdata.get("longitude")
            if lon is not None:
                rashi_idx = int(float(lon)) // 30
                rashi = _RASHI_NAMES[rashi_idx] if 0 <= rashi_idx < 12 else ""
        if rashi == _EXALTATION.get(planet):
            return "exalted"
        if rashi == _DEBILITATION.get(planet):
            return "debilitated"
        if rashi in _OWN_SIGNS.get(planet, []):
            return "own"
        return "neutral"

    def _score_lord(lord: str, weight: float) -> None:
        """Add area score contributions for a dasha lord."""
        lord = lord.lower()
        owned = _get_owned_houses(lord)
        placed = _get_placement_house(lord)
        dignity = _get_dignity(lord)

        # Dignity modifier (affects all areas)
        dignity_mod = {"exalted": 1.0, "own": 0.5, "debilitated": -1.5}.get(dignity, 0.0)

        # Functional nature: trikona lords are benefic, dusthana lords are malefic
        is_trikona_lord = bool(set(owned) & _TRIKONA_HOUSES)
        is_dusthana_lord = bool(set(owned) & _DUSTHANA_HOUSES)
        functional_mod = 0.0
        if is_trikona_lord:
            functional_mod = 0.5
        elif is_dusthana_lord:
            functional_mod = -0.5

        for area, area_houses in _AREA_HOUSES.items():
            primary = area_houses[0]
            secondaries = area_houses[1:]
            delta = 0.0

            # Lordship: does the dasha lord own this area's houses?
            if primary in owned:
                delta += 3.0
            for sec in secondaries:
                if sec in owned:
                    delta += 1.0

            # Placement: is the dasha lord sitting in this area's houses?
            if placed is not None:
                if placed == primary:
                    delta += 2.0
                elif placed in secondaries:
                    delta += 1.0

            # Natural karaka alignment
            if lord == _AREA_KARAKAS.get(area):
                delta += 1.0

            # Apply dignity + functional nature
            if delta != 0:
                delta += dignity_mod + functional_mod

            scores[area] += delta * weight

    # MD lord is primary influence (full weight)
    _score_lord(md_lord, weight=1.0)

    # AD lord modifies the picture (40% weight)
    if ad_lord:
        _score_lord(ad_lord, weight=0.4)

    return {area: max(1, min(10, round(val))) for area, val in scores.items()}


@router.get("/dasha/effects")
async def get_dasha_effects(
    md: str,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
    ad: str | None = None,
    pd: str | None = None,
    sd: str | None = None,
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
            "finances": md_guide.get("finances", ""),
            "family": md_guide.get("family", ""),
            "education": md_guide.get("education", ""),
            "travel": md_guide.get("travel", ""),
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

        # SD effects (combination PD x SD + per-planet guide)
        # Flatten guide fields to top level (matches MD/AD/PD pattern)
        if sd:
            sd_guide_data = get_sookshma_dasha_guide()
            sd_guide = sd_guide_data.get("sookshma_dasha_guide", sd_guide_data)
            sd_planet_guide = sd_guide.get(sd.lower(), {})
            sd_result: dict[str, Any] = {"lord": sd.lower(), **sd_planet_guide}
            if pd:
                sd_combo = get_sookshma_dasha_effect(pd.lower(), sd.lower())
                if sd_combo:
                    sd_result["combination_effects"] = sd_combo
            result["sookshma"] = sd_result

        # Relationship info between period lords
        if ad:
            result["md_ad_relationship"] = _get_planet_relationship(md.lower(), ad.lower())
        if ad and pd:
            result["ad_pd_relationship"] = _get_planet_relationship(ad.lower(), pd.lower())
        if pd and sd:
            result["pd_sd_relationship"] = _get_planet_relationship(pd.lower(), sd.lower())

        # Load birth chart ONCE for area scores + cross-analysis + doshas
        chart = await _load_birth_chart(db, str(current_user.id))

        # Area scores — classical lordship-based scoring from user's chart
        result["area_scores"] = _compute_area_scores(md.lower(), ad.lower() if ad else None, chart)

        # BPHS chart-specific dasha interpretation
        if chart:
            try:
                natal_planets_raw = chart.get("planets", {})
                lagna_rashi_name = chart.get("lagna_rashi", "aries")
                lagna_idx = _SIGN_TO_RASHI.get(
                    lagna_rashi_name.lower() if isinstance(lagna_rashi_name, str) else "aries",
                    0,
                )
                bphs = interpret_dasha_combination(
                    md=md.lower(),
                    ad=ad.lower() if ad else None,
                    pd=pd.lower() if pd else None,
                    natal_planets=_build_planets_for_analysis(natal_planets_raw),
                    lagna_index=lagna_idx,
                    sd=sd.lower() if sd else None,
                )
                result["bphs_analysis"] = bphs

                # ── BPHS Overlay: replace generic text with chart-specific content ──
                md_bphs = bphs.get("mahadasha")
                if md_bphs:
                    focus = _bphs_focus_areas(md_bphs)
                    if focus:
                        md_response["focus_areas"] = focus
                    for area_key in _AREA_KEYS:
                        text = _bphs_area_text(md_bphs, area_key)
                        if text:
                            md_response[area_key] = text
                    opp = _bphs_opportunities(md_bphs)
                    if opp:
                        md_response["opportunities"] = opp
                    chall = _bphs_challenges(md_bphs)
                    if chall:
                        md_response["challenges"] = chall
                    adv = _bphs_practical_advice(md_bphs)
                    if adv:
                        md_response["practical_advice"] = adv

                # AD overlay
                ad_bphs = bphs.get("antardasha")
                if ad_bphs and "antardasha" in result:
                    ad_resp = result["antardasha"]
                    ad_resp["general_effects"] = [
                        ad_bphs["summary"],
                        ad_bphs["prediction"],
                    ]
                    ad_resp["positive"] = _bphs_positive(ad_bphs)
                    ad_resp["negative"] = _bphs_negative(ad_bphs)
                    for area_key in _AREA_KEYS:
                        text = _bphs_area_text(ad_bphs, area_key)
                        if text:
                            ad_resp[area_key] = text

                # PD overlay
                pd_bphs = bphs.get("pratyantardasha")
                if pd_bphs and "pratyantardasha" in result:
                    pd_resp = result["pratyantardasha"]
                    pd_resp["theme"] = pd_bphs["summary"]
                    effects = [pd_bphs["summary"], pd_bphs["prediction"]]
                    # Add aspect/conjunction notes
                    for asp in pd_bphs.get("aspects_received", []):
                        effects.append(
                            f"{asp['planet'].title()} aspects from house {asp.get('from_house', '')}."
                        )
                    pd_resp["effects"] = effects

                # SD overlay
                sd_bphs = bphs.get("sookshma")
                if sd_bphs and "sookshma" in result:
                    result["sookshma"]["theme"] = sd_bphs["summary"]

            except Exception as bphs_err:
                logger.warning(f"BPHS dasha analysis failed: {bphs_err}")

        # Cross-analysis (requires birth chart + live transits — pro+ only)
        if access != AccessLevel.PREVIEW and chart:
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

        # Activated doshas — ONLY show doshas whose involved planets
        # match the current period lords (per BPHS: doshas manifest
        # during the dasha of involved planets, not at all times)
        if chart:
            try:
                all_markers = _detect_dosha_markers(chart)
                queried_lords = {md.lower()}
                if ad:
                    queried_lords.add(ad.lower())
                if pd:
                    queried_lords.add(pd.lower())
                if sd:
                    queried_lords.add(sd.lower())

                activated = []
                seen: set[str] = set()
                for lord in queried_lords:
                    for marker in all_markers.get(lord, []):
                        if marker["dosha_id"] not in seen:
                            seen.add(marker["dosha_id"])
                            activated.append({**marker, "activated_by": lord})
                if activated:
                    result["activated_doshas"] = activated
            except Exception as e:
                logger.warning(f"Dosha activation check failed: {e}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dasha effects for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dasha effects",
        ) from e


def _get_planet_relationship(planet1: str, planet2: str) -> dict[str, str]:
    """Get natural relationship between two planets.

    Returns dict with 'type' (friend/enemy/neutral/self) and 'label'.
    """
    p1, p2 = planet1.lower(), planet2.lower()
    if p1 == p2:
        return {"type": "self", "label": "Same planet"}

    relationships = load_definition("relationships")
    natural = relationships.get("natural_relationships", {})
    info = natural.get(p1, {})

    # Rahu/Ketu share relationships with Saturn/Mars respectively
    if p1 in ("rahu", "ketu") and not info:
        proxy = "saturn" if p1 == "rahu" else "mars"
        info = natural.get(proxy, {})
    p2_proxy = ("saturn" if p2 == "rahu" else "mars") if p2 in ("rahu", "ketu") else p2

    if p2_proxy in info.get("friends", []):
        return {
            "type": "friend",
            "label": f"{planet1.title()} and {planet2.title()} are natural friends",
        }
    if p2_proxy in info.get("enemies", []):
        return {
            "type": "enemy",
            "label": f"{planet1.title()} and {planet2.title()} are natural enemies",
        }
    return {"type": "neutral", "label": f"{planet1.title()} and {planet2.title()} are neutral"}


@router.get("/dasha/sub-periods")
async def get_dasha_sub_periods(
    parent_lord: str,
    parent_start: str,
    parent_end: str,
    level: str,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
    md_lord: str | None = None,
) -> dict[str, Any]:
    """Get sub-period sequence for a given parent period.

    Args:
        parent_lord: Lord of the parent period.
        parent_start: ISO start date of parent.
        parent_end: ISO end date of parent.
        level: 'ad' for antardashas, 'pd' for pratyantardashas.
        md_lord: Mahadasha lord (needed for relationship context).
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict with periods list, each including lord, dates, duration, and relationship.
    """
    try:
        await check_feature_access("analysis_dasha", current_user.subscription_tier, config)

        start_dt = datetime.fromisoformat(parent_start)
        end_dt = datetime.fromisoformat(parent_end)

        if level == "ad":
            sequence = get_antardasha_sequence(parent_lord, start_dt, end_dt)
            context_lord = parent_lord  # AD relates to MD
        elif level == "pd":
            sequence = get_pratyantardasha_sequence(parent_lord, start_dt, end_dt)
            context_lord = md_lord or parent_lord  # PD relates to AD (but MD for broader context)
        elif level == "sd":
            sequence = get_sookshma_dasha_sequence(parent_lord, start_dt, end_dt)
            context_lord = md_lord or parent_lord
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="level must be 'ad', 'pd', or 'sd'",
            )

        periods = []
        for p in sequence:
            lord = p.get("lord", "")
            rel = _get_planet_relationship(context_lord, lord)
            periods.append(
                {
                    "lord": lord,
                    "start": str(p.get("start_date", "")),
                    "end": str(p.get("end_date", "")),
                    "years": p.get("years"),
                    "relationship": rel["type"],
                    "relationship_label": rel["label"],
                }
            )

        # Attach dosha markers per period
        try:
            chart = await _load_birth_chart(db, str(current_user.id))
            if chart:
                all_markers = _detect_dosha_markers(chart)
                for p in periods:
                    p["dosha_markers"] = all_markers.get(p["lord"], [])
        except Exception as e:
            logger.warning(f"Dosha markers for sub-periods failed: {e}")

        return {
            "level": level,
            "parent_lord": parent_lord,
            "periods": periods,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sub-periods for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sub-periods",
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

        # Live ephemeris positions
        now_jd = get_julian_day(datetime.utcnow())
        live_positions = get_transit_positions(now_jd)

        # Build transit positions with nakshatra data
        transit_positions: dict[str, Any] = {}
        for planet, pos in live_positions.items():
            nak = longitude_to_nakshatra(pos["longitude"])
            nak_name = nak.get("name", "") if isinstance(nak, dict) else getattr(nak, "name", "")
            nak_pada = nak.get("pada", 0) if isinstance(nak, dict) else getattr(nak, "pada", 0)
            transit_positions[planet] = {
                "rashi": pos["rashi"],
                "rashi_num": pos["rashi_num"],
                "nakshatra": nak_name,
                "nakshatra_pada": nak_pada,
                "longitude": pos["longitude"],
                "degree_in_rashi": round(pos["degree_in_rashi"], 2),
                "is_retrograde": pos.get("is_retrograde", False),
                "speed": round(pos.get("speed", 0.0), 4),
            }

        # Preview tier: return positions + summary only
        if access == AccessLevel.PREVIEW:
            moon_idx = _rashi_to_int(chart.get("moon_rashi"))
            favorable = 0
            unfavorable = 0
            for planet, pos in transit_positions.items():
                gochara = get_gochara(moon_idx, planet, pos["rashi_num"])
                if gochara.get("is_favorable"):
                    favorable += 1
                else:
                    unfavorable += 1
            trend = (
                "positive"
                if favorable > unfavorable
                else ("mixed" if favorable == unfavorable else "challenging")
            )
            return {
                "transit_positions": transit_positions,
                "summary": {
                    "favorable_count": favorable,
                    "unfavorable_count": unfavorable,
                    "trend": trend,
                },
                "access": "preview",
                "upgrade_hint": "Upgrade to Pro for full transit analysis with gochara, aspects, and triggers",
            }

        # Full tier: enriched analysis + raw positions
        moon_idx = _rashi_to_int(chart.get("moon_rashi"))

        # Build int-rashi format for enriched analysis
        transit_for_enriched: dict[str, dict[str, Any]] = {}
        for planet, pos in transit_positions.items():
            transit_for_enriched[planet] = {
                "rashi": pos["rashi_num"],
                "nakshatra": pos["nakshatra"],
                "longitude": pos["longitude"],
                "is_retrograde": pos["is_retrograde"],
            }

        analysis = get_enriched_transit_analysis(
            natal_moon_rashi=moon_idx,
            transit_data=transit_for_enriched,
        )
        analysis["transit_positions"] = transit_positions

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate transit analysis for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze transits",
        ) from e


@router.get("/transits/aspects")
async def get_transit_aspects_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get current transit-to-natal aspects."""
    try:
        access = await check_feature_access(
            "analysis_transits", current_user.subscription_tier, config
        )
        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock transit aspects"},
                access,
                "Upgrade to Pro to unlock transit aspects",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Birth chart not found"
            ) from None

        natal_planets = _build_planets_for_analysis(chart.get("planets", {}))
        now_jd = get_julian_day(datetime.utcnow())
        live_positions = get_transit_positions(now_jd)
        aspects = get_transit_natal_aspects(natal_planets, live_positions)

        return {"aspects": aspects, "count": len(aspects)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transit aspects for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transit aspects",
        ) from e


@router.get("/transits/triggers")
async def get_transit_triggers_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
    days: int = 30,
) -> dict[str, Any]:
    """Get upcoming transit triggers (ingresses, stations, aspects, dasha changes)."""
    try:
        access = await check_feature_access(
            "analysis_transits", current_user.subscription_tier, config
        )
        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock transit triggers"},
                access,
                "Upgrade to Pro to unlock transit triggers",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Birth chart not found"
            ) from None

        natal_planets = _build_planets_for_analysis(chart.get("planets", {}))
        lagna_rashi = chart.get("lagna_rashi", "Libra")
        moon_rashi = chart.get("moon_rashi", "Aquarius")

        triggers = get_upcoming_triggers(
            natal_planets=natal_planets,
            lagna_rashi=lagna_rashi,
            moon_rashi=moon_rashi,
            start_date=datetime.utcnow().isoformat(),
            days_ahead=min(days, 90),
        )

        return {"triggers": triggers, "count": len(triggers)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transit triggers for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transit triggers",
        ) from e


@router.get("/transits/snapshot")
async def get_transit_snapshot_endpoint(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get house-centric transit snapshot with activation scores and lordship analysis.

    Combines house activation engine (double transit, aspects, gochara, ashtakavarga)
    with transit lordship resolver (functional nature, yogakaraka detection).

    Gated feature - preview tier gets positions + house scores + double transit only.
    Full tier includes lordship analysis.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Transit snapshot with house activations and lordship analysis.
    """
    try:
        access = await check_feature_access(
            "analysis_transits", current_user.subscription_tier, config
        )
        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock transit snapshot"},
                access,
                "Upgrade to Pro to unlock transit snapshot",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Birth chart not found"
            ) from None

        natal_planets = _build_planets_for_analysis(chart.get("planets", {}))
        lagna_idx = _rashi_to_int(chart.get("lagna_rashi"))
        moon_idx = _rashi_to_int(chart.get("moon_rashi"))

        now_jd = get_julian_day(datetime.utcnow())
        # Build BirthChart for Ashtakavarga BAV lookups in snapshot
        try:
            birth_chart = _build_chart_for_doshas(chart)
        except Exception:
            birth_chart = None
        snapshot = get_transit_snapshot(
            julian_day=now_jd,
            lagna_rashi=lagna_idx,
            moon_rashi=moon_idx,
            natal_planets=natal_planets,
            chart=birth_chart,
        )

        # Preview tier: positions + house scores + double transit only
        if access == AccessLevel.PREVIEW:
            return {
                "transit_positions": snapshot.get("transit_positions", {}),
                "house_activations": [
                    {
                        "house": h["house"],
                        "score": h["score"],
                        "grade": h["grade"],
                        "double_transit": h["double_transit"],
                        "themes": h["themes"],
                    }
                    for h in snapshot.get("house_activations", [])
                ],
                "double_transit_houses": snapshot.get("double_transit_houses", []),
                "most_active_houses": snapshot.get("most_active_houses", []),
                "gochara_summary": snapshot.get("gochara_summary", []),
                "active_aspects": snapshot.get("active_aspects", []),
                "overall_trend": snapshot.get("overall_trend", "mixed"),
                "access": "preview",
                "upgrade_hint": "Upgrade to Pro for full lordship analysis and detailed house breakdowns",
            }

        # Full tier: everything including lordship analysis
        transit_positions = snapshot.get("transit_positions", {})
        lordship_analysis = analyze_transit_lordships(transit_positions, lagna_idx)
        lordship_summary = get_lordship_summary(lordship_analysis)

        # Enrich house activations with planet-in-house interpretations
        house_interp_data = get_planet_in_house_interpretations()
        for activation in snapshot.get("house_activations", []):
            planet_interps = []
            for planet_name in activation.get("planets_present", []):
                key = f"{planet_name.lower()}_in_house_{activation['house']}"
                interp = house_interp_data.get(key)
                if interp:
                    planet_interps.append(
                        {
                            "planet": planet_name,
                            "summary": interp.get("summary", ""),
                            "positive": interp.get("positive", []),
                            "negative": interp.get("negative", []),
                        }
                    )
            if planet_interps:
                activation["planet_interpretations"] = planet_interps

        return {
            **snapshot,
            "lordship_analysis": lordship_analysis,
            "lordship_summary": lordship_summary,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transit snapshot for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transit snapshot",
        ) from e


@router.get("/transits/{planet}")
async def get_transit_planet_detail(
    planet: str,
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get detailed transit info for a single planet."""
    try:
        valid_planets = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        }
        planet_lower = planet.lower()
        if planet_lower not in valid_planets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid planet: {planet}. Must be one of: {', '.join(sorted(valid_planets))}",
            )

        access = await check_feature_access(
            "analysis_transits", current_user.subscription_tier, config
        )
        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock planet transit details"},
                access,
                "Upgrade to Pro to unlock planet transit details",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Birth chart not found"
            ) from None

        # Current transit position
        now_jd = get_julian_day(datetime.utcnow())
        live_positions = get_transit_positions(now_jd)
        pos = live_positions.get(planet_lower, {})

        nak = longitude_to_nakshatra(pos.get("longitude", 0.0))
        nak_name = nak.get("name", "") if isinstance(nak, dict) else getattr(nak, "name", "")
        nak_pada = nak.get("pada", 0) if isinstance(nak, dict) else getattr(nak, "pada", 0)

        position = {
            "planet": planet_lower,
            "longitude": pos.get("longitude", 0.0),
            "rashi": pos.get("rashi", ""),
            "rashi_num": pos.get("rashi_num", 0),
            "degree_in_rashi": round(pos.get("degree_in_rashi", 0.0), 2),
            "nakshatra": nak_name,
            "nakshatra_pada": nak_pada,
            "speed": round(pos.get("speed", 0.0), 4),
            "is_retrograde": pos.get("is_retrograde", False),
        }

        # Gochara (house from Moon)
        moon_idx = _rashi_to_int(chart.get("moon_rashi"))
        gochara = get_gochara(moon_idx, planet_lower, pos.get("rashi_num", 0))

        # Natal aspects for this planet
        natal_planets = _build_planets_for_analysis(chart.get("planets", {}))
        single_transit = {planet_lower: pos}
        aspects = get_transit_natal_aspects(natal_planets, single_transit)

        # Upcoming aspects for this planet (30 days)
        upcoming = find_upcoming_aspects(
            natal_planets=natal_planets,
            start_date=datetime.utcnow().isoformat(),
            days_ahead=30,
        )
        planet_upcoming = [
            a for a in upcoming if a.get("transit_planet", "").lower() == planet_lower
        ]

        # Interpretations from knowledge base
        lagna_idx = _rashi_to_int(chart.get("lagna_rashi"))
        rashi_num = pos.get("rashi_num", 0)
        transit_house = (rashi_num - lagna_idx) % 12 + 1

        sign_interpretation = None
        sign_name = pos.get("rashi", "").lower() if isinstance(pos.get("rashi"), str) else ""
        if sign_name:
            sign_data = get_planet_in_sign_interpretations()
            sign_key = f"{planet_lower}_in_{sign_name}"
            if sign_key in sign_data:
                sign_interpretation = sign_data[sign_key]

        house_interpretation = None
        house_data = get_planet_in_house_interpretations()
        house_key = f"{planet_lower}_in_house_{transit_house}"
        if house_key in house_data:
            house_interpretation = house_data[house_key]

        result: dict[str, Any] = {
            "position": position,
            "transit_house": transit_house,
            "gochara": gochara,
            "natal_aspects": aspects,
            "upcoming": planet_upcoming[:10],
        }
        if sign_interpretation:
            result["sign_interpretation"] = sign_interpretation
        if house_interpretation:
            result["house_interpretation"] = house_interpretation

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transit detail for {planet}/{current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transit planet detail",
        ) from e


@router.get("/strength")
async def get_strength(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get Shadbala (six-fold strength) for all planets.

    Gated feature - pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Planet strengths (gated by subscription tier).
    """
    try:
        access = await check_feature_access(
            "analysis_strength", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock strength analysis"},
                access,
                "Upgrade to Pro to unlock strength analysis",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        chart_obj = _build_chart_for_doshas(chart)
        calculator = StrengthCalculator()

        # Required minimum Shadbala virupas per planet (BPHS-based).
        # Ratio = total_virupas / required → 1.0 means "meets threshold".
        _required_virupas: dict[str, float] = {
            "sun": 390,
            "moon": 360,
            "mars": 300,
            "mercury": 420,
            "jupiter": 390,
            "venus": 330,
            "saturn": 300,
            "rahu": 300,
            "ketu": 300,
        }

        planets_list = []
        for planet in Planet:
            if planet not in chart_obj.planets:
                continue
            result = calculator.calculate_shadbala(planet, chart_obj)
            total_virupas = result.get("total", 0.0)
            required = _required_virupas.get(planet.value, 300)
            ratio = total_virupas / required if required > 0 else 0.0

            # Grade based on ratio (1.0 = meets BPHS minimum)
            grade = (
                "very_strong"
                if ratio >= 1.5
                else "strong"
                if ratio >= 1.0
                else "average"
                if ratio >= 0.7
                else "weak"
            )
            entry: dict[str, Any] = {
                "planet": planet.value,
                "total_shadbala": round(ratio, 2),
                "grade": grade,
            }
            if access != AccessLevel.PREVIEW:
                components = result.get("components", {})
                entry["components"] = {
                    k: round(v, 2) if isinstance(v, float) else v for k, v in components.items()
                }
            planets_list.append(entry)

        return {"planets": planets_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate strength for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate strength",
        ) from e


@router.get("/atmakaraka")
async def get_atmakaraka(
    current_user: Annotated[UserContext, Depends(get_current_user)],
    config: Annotated[dict, Depends(get_app_config)],
    db: Annotated[Any, Depends(get_db)],
) -> dict[str, Any]:
    """Get Atmakaraka analysis, Ishta Devata, and Chara Karakas.

    Gated feature - pro and premium tiers.

    Args:
        current_user: Authenticated user context.
        config: Application configuration.
        db: Database connection.

    Returns:
        dict: Soul purpose analysis (gated by subscription tier).
    """
    try:
        access = await check_feature_access(
            "analysis_atmakaraka", current_user.subscription_tier, config
        )

        if access == AccessLevel.LOCKED:
            return gate_response(
                {"message": "Upgrade to Pro to unlock Atmakaraka analysis"},
                access,
                "Upgrade to Pro to unlock Atmakaraka analysis",
            ).model_dump()

        chart = await _load_birth_chart(db, str(current_user.id))
        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birth chart not found",
            ) from None

        chart_obj = _build_chart_for_doshas(chart)
        ak_analysis = get_atmakaraka_analysis(chart_obj)

        # Preview tier: AK planet name only
        if access == AccessLevel.PREVIEW:
            return {
                "atmakaraka": {
                    "planet": ak_analysis.get("planet", ""),
                    "sign": ak_analysis.get("sign", ""),
                },
            }

        # Full tier: AK + ishta devata + chara karakas
        ishta = get_ishta_devata(chart_obj)
        chara = get_all_chara_karaka_analysis(chart_obj)

        return {
            "atmakaraka": ak_analysis,
            "ishta_devata": ishta,
            "chara_karakas": chara.get("karakas", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get atmakaraka for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get atmakaraka analysis",
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

        # Get cusps — DB stores {"cusps": [12 floats], "ascendant": ..., "mc": ...}
        raw_cusps = houses.get("cusps", [])
        if isinstance(raw_cusps, list) and len(raw_cusps) == 12:
            cusps = [float(c) for c in raw_cusps]
        else:
            # Fallback: try house_1..house_12 keys, then equal houses
            cusps = []
            for i in range(1, 13):
                h = houses.get(f"house_{i}")
                if isinstance(h, dict):
                    cusps.append(float(h.get("longitude", (i - 1) * 30)))
                elif h is not None:
                    cusps.append(float(h))
                else:
                    cusps.append(float((i - 1) * 30))

        # Map Flutter query IDs to KP house group keys
        query_map = {
            "short_travel": "travel_short",
            "foreign_travel": "travel_foreign",
        }
        kp_query_type = query_map.get(request.event_type, request.event_type)

        # Phase 3: Get ruling planets at query time for confirmation
        ruling_planets_data = None
        try:
            now_iso = datetime.utcnow().isoformat()
            lat = chart.get("latitude", 0)
            lon = chart.get("longitude", 0)
            if lat and lon:
                ruling_planets_data = get_ruling_planets(now_iso, float(lat), float(lon))
        except Exception as rp_err:
            logger.warning(f"Ruling planets calculation failed: {rp_err}")

        # Get KP prediction (planets already has full dict structure)
        prediction = get_kp_prediction(
            planets=planets,
            cusps=cusps,
            query_type=kp_query_type,
            ruling_planets=ruling_planets_data,
        )

        # Get significators for all houses
        significators = get_kp_significators(
            planets=planets,
            cusps=cusps,
        )

        # Format cusp_analysis for frontend (flatten field names)
        cusp_raw = prediction.get("cusp_analysis", {})
        cusp_analysis = {
            "sign": cusp_raw.get("cusp_sign", ""),
            "sign_lord": cusp_raw.get("sign_lord", ""),
            "star_lord": cusp_raw.get("star_lord", ""),
            "sub_lord": cusp_raw.get("sub_lord", ""),
        }

        # Format timing_hints as a flat list for frontend
        timing_raw = prediction.get("timing_hints", {})
        timing_hints = timing_raw.get("transit_triggers", []) + [
            f"Watch {p.title()} dasha" for p in timing_raw.get("dasha_lords_to_watch", [])
        ]

        # Format significators with string keys for JSON
        sigs_formatted = {}
        for house_num, sig_data in significators.items():
            sigs_formatted[str(house_num)] = sig_data

        # --- KP Classical Timing: per-house significator check ---
        # Real KP method: event happens when MD+AD+PD lords are ALL significators
        # of the supporting houses (e.g., 2,7,11 for marriage).
        kp_groups = KP_HOUSE_GROUPS.get(kp_query_type, {})
        supporting_houses: list[int] = kp_groups.get("support", [])

        # Build a set of planets that significate each supporting house.
        house_significator_planets: set[str] = set()
        for house in supporting_houses:
            house_sigs = significators.get(house, {}).get("all_significators", [])
            for sig in house_sigs:
                house_significator_planets.add(sig.lower())

        timing_windows: list[dict[str, Any]] = []
        try:
            birth_dt = chart["birth_datetime"]
            if isinstance(birth_dt, str):
                birth_dt = datetime.fromisoformat(birth_dt)

            moon_data = chart.get("planets", {}).get("moon", {})
            moon_lon = float(moon_data.get("longitude", 0)) if moon_data else 0.0

            if moon_lon and house_significator_planets:
                now = datetime.now(birth_dt.tzinfo) if birth_dt.tzinfo else datetime.now()
                now_naive = now.replace(tzinfo=None) if now.tzinfo else now
                lookback = now_naive.replace(year=now_naive.year - 10)
                lookahead = now_naive.replace(year=now_naive.year + 15)

                md_sequence = get_mahadasha_sequence(birth_dt, moon_lon, 120)

                for md_item in md_sequence:
                    md_start = md_item["start_date"]
                    md_end = md_item["end_date"]
                    md_lord = md_item["lord"]

                    md_end_naive = md_end.replace(tzinfo=None) if md_end.tzinfo else md_end
                    md_start_naive = md_start.replace(tzinfo=None) if md_start.tzinfo else md_start

                    if md_end_naive < lookback:
                        continue
                    if md_start_naive > lookahead:
                        break

                    # MD lord must be a significator of supporting houses
                    md_is_sig = md_lord in house_significator_planets
                    if not md_is_sig:
                        continue

                    ad_sequence = get_antardasha_sequence(md_lord, md_start, md_end)
                    for ad_item in ad_sequence:
                        ad_start = ad_item["start_date"]
                        ad_end = ad_item["end_date"]
                        ad_start_naive = (
                            ad_start.replace(tzinfo=None) if ad_start.tzinfo else ad_start
                        )
                        ad_end_naive = ad_end.replace(tzinfo=None) if ad_end.tzinfo else ad_end

                        if ad_end_naive < lookback:
                            continue
                        if ad_start_naive > lookahead:
                            break

                        ad_lord = ad_item["lord"]
                        ad_is_sig = ad_lord in house_significator_planets

                        if not ad_is_sig:
                            continue

                        # Both MD and AD are significators — this is a relevant AD window
                        is_past = ad_end_naive < now_naive
                        is_current = ad_start_naive <= now_naive <= ad_end_naive

                        # Drill into PD for precise timing (current + future only)
                        pd_entries: list[dict[str, Any]] = []
                        if not is_past:
                            try:
                                pd_seq = get_pratyantardasha_sequence(
                                    ad_lord,
                                    ad_start,
                                    ad_end,
                                )
                                for pd_item in pd_seq:
                                    pd_lord = (pd_item.get("lord") or "").lower()
                                    pd_start_dt = pd_item.get("start_date")
                                    pd_end_dt = pd_item.get("end_date")
                                    if not pd_start_dt or not pd_end_dt:
                                        continue
                                    pd_is_sig = pd_lord in house_significator_planets
                                    if pd_is_sig:
                                        duration_days = (pd_end_dt - pd_start_dt).days

                                        # SD drill-down: Sookshma periods where lord is also a significator
                                        sd_entries: list[dict[str, Any]] = []
                                        try:
                                            sd_seq = get_sookshma_dasha_sequence(
                                                pd_lord,
                                                pd_start_dt,
                                                pd_end_dt,
                                            )
                                            for sd_item in sd_seq:
                                                sd_lord = (sd_item.get("lord") or "").lower()
                                                if sd_lord in house_significator_planets:
                                                    sd_start_dt = sd_item["start_date"]
                                                    sd_end_dt = sd_item["end_date"]
                                                    sd_entries.append(
                                                        {
                                                            "sd_lord": sd_lord.title(),
                                                            "start": sd_start_dt.strftime(
                                                                "%Y-%m-%d"
                                                            ),
                                                            "end": sd_end_dt.strftime("%Y-%m-%d"),
                                                            "duration_days": (
                                                                sd_end_dt - sd_start_dt
                                                            ).days,
                                                        }
                                                    )
                                        except Exception:
                                            pass

                                        pd_entries.append(
                                            {
                                                "pd_lord": pd_lord.title(),
                                                "start": pd_start_dt.strftime("%Y-%m-%d"),
                                                "end": pd_end_dt.strftime("%Y-%m-%d"),
                                                "duration_days": duration_days,
                                                "window_type": "peak",
                                                "sd_periods": sd_entries,
                                            }
                                        )
                            except Exception:
                                pass

                        timing_windows.append(
                            {
                                "md_lord": md_lord.title(),
                                "ad_lord": ad_lord.title(),
                                "start": ad_start.strftime("%Y-%m-%d"),
                                "end": ad_end.strftime("%Y-%m-%d"),
                                "is_past": is_past,
                                "is_current": is_current,
                                "pd_periods": pd_entries,
                            }
                        )

                        if len(timing_windows) >= 12:
                            break
                    if len(timing_windows) >= 12:
                        break
        except Exception:
            pass  # Timing windows are supplementary — don't fail the endpoint

        # KP nakshatra transit triggers — Sun/Moon entering significator nakshatras
        transit_trigger_dates: list[dict[str, Any]] = []
        try:
            if house_significator_planets:
                sig_list = list(house_significator_planets)
                scan_end = now_naive + timedelta(days=365)
                transit_trigger_dates = get_nakshatra_transit_triggers(
                    sig_list,
                    now_naive,
                    scan_end,
                )
        except Exception:
            pass  # Transit triggers are supplementary

        # Build ruling planets section for response (internal confirmation data)
        ruling_planets_section = None
        if ruling_planets_data:
            ruling_planets_section = {
                "planets": ruling_planets_data.get("ruling_planets", []),
                "frequencies": ruling_planets_data.get("frequencies", {}),
                "strongest": ruling_planets_data.get("strongest", ""),
                "confirmed": prediction.get("ruling_planet_confirmation", False),
            }

        result = {
            "event_type": request.event_type,
            "prediction": {
                "query_type": prediction.get("query_type", kp_query_type),
                "primary_house": prediction.get("primary_house", 1),
                "cusp_analysis": cusp_analysis,
                "judgment": prediction.get("judgment", "mixed"),
                "confidence": int(prediction.get("confidence", 0.5) * 100),
                "timing_hints": timing_hints,
                "explanation": prediction.get("explanation", ""),
            },
            "significators": sigs_formatted,
            "timing": request.timing_preference,
            "timing_windows": timing_windows,
            "transit_triggers": transit_trigger_dates[:20],
        }
        if ruling_planets_section:
            result["ruling_planets"] = ruling_planets_section
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate KP predictions for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate KP predictions",
        ) from e
