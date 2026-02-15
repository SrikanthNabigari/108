"""Daily Forecast Engine for 108 Vedic Astrology.

Generates a comprehensive daily forecast by combining ALL available timing tools:
- Panchanga (tithi, vara, yoga, karana, nakshatra)
- Transit Moon position and quality
- Choghadiya periods (auspicious/inauspicious time slots)
- Rahu Kaal / Yamaghanda / Gulika (inauspicious windows)
- Ashtakavarga BAV score for Moon's current sign
- Current Vimshottari Dasha (MD/AD/PD)
- Active transit-natal aspects for the day

Produces a day_rating (1-10) and actionable recommendations.
"""

from datetime import datetime
from typing import Any

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

RASHI_NAMES = [
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

WEEKDAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

# Panchanga yoga quality map (name -> score adjustment, -2 to +2)
_YOGA_QUALITY: dict[str, int] = {
    "Vishkumbha": -2,
    "Atiganda": -2,
    "Shoola": -2,
    "Vyatipata": -2,
    "Ganda": -1,
    "Vyaghata": -1,
    "Vajra": -1,
    "Parigha": -1,
    "Priti": 1,
    "Ayushman": 1,
    "Saubhagya": 1,
    "Shobhana": 1,
    "Sukarma": 1,
    "Dhriti": 1,
    "Vriddhi": 1,
    "Dhruva": 1,
    "Harshana": 1,
    "Shiva": 1,
    "Siddha": 2,
    "Siddhi": 2,
    "Brahma": 1,
    "Indra": 1,
    "Vaidhriti": -2,
    "Variyan": 0,
    "Sadhya": 1,
    "Subha": 1,
    "Sukla": 1,
}

# Vara quality (planet ruling day)
_VARA_QUALITY: dict[str, float] = {
    "monday": 0.5,  # Moon — neutral-good
    "tuesday": -0.5,  # Mars — challenging
    "wednesday": 1.0,  # Mercury — good
    "thursday": 1.5,  # Jupiter — excellent
    "friday": 1.0,  # Venus — good
    "saturday": -1.0,  # Saturn — challenging
    "sunday": 0.5,  # Sun — neutral-good
}

# Dasha lord natural quality (benefic / malefic tendency)
_DASHA_LORD_QUALITY: dict[str, float] = {
    "jupiter": 1.5,
    "venus": 1.0,
    "mercury": 0.5,
    "moon": 0.5,
    "sun": 0.0,
    "mars": -0.5,
    "saturn": -0.5,
    "rahu": -0.5,
    "ketu": -0.5,
}

# Area -> associated houses (8 areas, matching state_engine.AREA_HOUSES)
AREA_HOUSES: dict[str, list[int]] = {
    "career": [10, 6, 2],
    "finance": [2, 11, 5],
    "relationships": [7, 5, 1],
    "health": [1, 6, 8],
    "spiritual": [12, 9, 5],
    "family": [4, 2, 1],
    "education": [4, 5, 9],
    "travel": [3, 9, 12],
}

# Area -> associated planets (8 areas)
AREA_PLANETS: dict[str, list[str]] = {
    "career": ["saturn", "sun", "mars"],
    "finance": ["jupiter", "venus", "mercury"],
    "relationships": ["venus", "moon", "jupiter"],
    "health": ["sun", "mars", "saturn"],
    "spiritual": ["jupiter", "ketu", "moon"],
    "family": ["moon", "venus", "mars"],
    "education": ["mercury", "jupiter", "moon"],
    "travel": ["rahu", "jupiter", "moon"],
}


# -------------------------------------------------------------------------
# Helper utilities
# -------------------------------------------------------------------------


def _get_rashi_index(name: str) -> int:
    """Convert rashi name to 0-based index."""
    low = name.lower()
    if low in RASHI_NAMES:
        return RASHI_NAMES.index(low)
    return 0


def _house_from_lagna(planet_rashi: int, lagna_rashi: int) -> int:
    """House number (1-12) of a planet from lagna."""
    return ((planet_rashi - lagna_rashi) % 12) + 1


def _panchanga_quality_score(panchanga: dict[str, Any]) -> float:
    """Score panchanga quality on a 0-10 scale.

    Considers tithi, vara, yoga, karana.
    """
    score = 5.0  # baseline

    # Tithi quality: Shukla Paksha generally better
    tithi = panchanga.get("tithi", {})
    paksha = tithi.get("paksha", "")
    tithi_num = tithi.get("number", 1)
    if isinstance(paksha, str) and paksha.lower() == "shukla":
        score += 0.5
    elif isinstance(paksha, str) and paksha.lower() == "krishna":
        score -= 0.3
    # Auspicious tithis: 2,3,5,7,10,11,13
    if tithi_num in (2, 3, 5, 7, 10, 11, 13):
        score += 0.5
    # Inauspicious: 4,8,9,14,30(amavasya)
    if tithi_num in (4, 8, 9, 14, 30):
        score -= 0.7

    # Yoga quality
    yoga_name = panchanga.get("yoga", {}).get("name", "")
    yoga_adj = _YOGA_QUALITY.get(yoga_name, 0)
    score += yoga_adj * 0.5

    # Vara quality
    vara_name = panchanga.get("vara", {}).get("name", "")
    vara_adj = _VARA_QUALITY.get(vara_name.lower(), 0.0)
    score += vara_adj * 0.5

    # Karana — Bava/Balava/Kaulava/Taitila are good
    karana_name = panchanga.get("karana", {}).get("name", "")
    good_karanas = {"Bava", "Balava", "Kaulava", "Taitila", "Gaja", "Vanija"}
    if karana_name in good_karanas:
        score += 0.3

    return max(0.0, min(10.0, score))


def _aspect_quality_score(aspects: list[dict[str, Any]]) -> float:
    """Score transit aspects quality on a 0-10 scale."""
    if not aspects:
        return 5.0

    benefic_aspects = {"trine", "sextile"}
    malefic_aspects = {"square", "opposition"}
    benefic_planets = {"jupiter", "venus"}
    malefic_planets = {"saturn", "mars", "rahu", "ketu"}

    score = 5.0
    for asp in aspects:
        aspect_type = asp.get("aspect_type", "")
        transit_planet = asp.get("transit_planet", "").lower()
        orb = asp.get("orb", 5.0)
        # Tighter orb = stronger influence
        strength = max(0.1, 1.0 - (orb / 8.0))

        if aspect_type in benefic_aspects:
            if transit_planet in benefic_planets:
                score += 1.0 * strength
            else:
                score += 0.5 * strength
        elif aspect_type in malefic_aspects:
            if transit_planet in malefic_planets:
                score -= 1.0 * strength
            else:
                score -= 0.4 * strength
        elif aspect_type == "conjunction":
            if transit_planet in benefic_planets:
                score += 0.8 * strength
            elif transit_planet in malefic_planets:
                score -= 0.6 * strength

    return max(0.0, min(10.0, score))


def _moon_bav_to_quality(bav_score: int) -> str:
    """Convert BAV score (0-8) to quality label."""
    if bav_score >= 5:
        return "favorable"
    if bav_score >= 4:
        return "neutral"
    if bav_score >= 2:
        return "unfavorable"
    return "very_unfavorable"


def _generate_recommendations(
    panchanga: dict[str, Any],  # noqa: ARG001
    moon_house_from_lagna: int,
    weekday: str,
    aspect_quality: float,
    dasha_quality: float,
) -> dict[str, Any]:
    """Generate best_for / avoid / tip recommendations."""
    best_for: list[str] = []
    avoid: list[str] = []

    vara_lower = weekday.lower()

    # Jupiter day = education, spiritual
    if vara_lower == "thursday":
        best_for.extend(["education", "spiritual", "legal"])
    elif vara_lower == "friday":
        best_for.extend(["relationships", "art", "purchases"])
    elif vara_lower == "wednesday":
        best_for.extend(["communication", "trade", "travel"])
    elif vara_lower == "saturday":
        avoid.extend(["new_ventures", "travel"])
        best_for.append("discipline")
    elif vara_lower == "tuesday":
        best_for.extend(["physical_activity", "courage"])
        avoid.append("surgery")

    # Moon house influences
    if moon_house_from_lagna in (1, 5, 9):
        best_for.append("spiritual")
    if moon_house_from_lagna in (2, 11):
        best_for.append("finance")
    if moon_house_from_lagna in (6, 8, 12):
        avoid.append("important_decisions")

    # Aspect quality
    if aspect_quality >= 7:
        best_for.append("major_decisions")
    elif aspect_quality <= 3:
        avoid.append("risky_ventures")

    tip = f"Moon in house {moon_house_from_lagna} + {vara_lower.capitalize()}"
    if dasha_quality >= 1:
        tip += " = supportive dasha energy"
    elif dasha_quality <= -0.5:
        tip += " = exercise patience"

    return {
        "best_for": list(set(best_for)) or ["routine_tasks"],
        "avoid": list(set(avoid)) or [],
        "tip": tip,
    }


def _compute_day_rating(
    panchanga_score: float,
    moon_bav: int,
    aspect_score: float,
    dasha_quality: float,
) -> int:
    """Compute overall day rating (1-10) from component scores.

    Weights:
    - Panchanga quality: 30%
    - Moon BAV score:    20%
    - Transit aspects:   30%
    - Dasha nature:      20%
    """
    # Normalize moon_bav from 0-8 to 0-10 scale
    moon_score = (moon_bav / 8.0) * 10.0

    # Normalize dasha quality from roughly -1 to 1.5 -> 0-10
    dasha_score = max(0.0, min(10.0, 5.0 + dasha_quality * 3.0))

    weighted = panchanga_score * 0.30 + moon_score * 0.20 + aspect_score * 0.30 + dasha_score * 0.20

    return max(1, min(10, round(weighted)))


def _generate_daily_summary(
    day_rating: int,
    moon_sign: str,
    moon_house_from_lagna: int,
    dasha_md: str,
    dasha_ad: str,
) -> str:
    """Generate a concise daily summary sentence."""
    if day_rating >= 8:
        tone = "A highly positive day"
    elif day_rating >= 6:
        tone = "A generally positive day"
    elif day_rating >= 4:
        tone = "A mixed day"
    else:
        tone = "A challenging day"

    return (
        f"{tone} with Moon in {moon_sign.title()} activating your "
        f"house {moon_house_from_lagna}. "
        f"Dasha energy: {dasha_md.title()}-{dasha_ad.title()} period active."
    )


# -------------------------------------------------------------------------
# Main public function
# -------------------------------------------------------------------------


def get_daily_forecast(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    natal_planets: dict[str, dict[str, Any]],
    moon_longitude: float,
    lagna_rashi: str,
    query_date: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
) -> dict[str, Any]:
    """Generate a comprehensive daily forecast.

    Combines panchanga, transit Moon, choghadiya, inauspicious periods,
    ashtakavarga, dasha, and transit aspects into a single forecast.

    Args:
        birth_datetime: ISO-format birth datetime string
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        natal_planets: Birth chart planet positions {planet: {longitude, ...}}
        moon_longitude: Natal Moon longitude (degrees)
        lagna_rashi: Ascendant sign name (e.g. "libra")
        query_date: Date to forecast (ISO date string, defaults to today)
        location_lat: Current location latitude (defaults to birth lat)
        location_lon: Current location longitude (defaults to birth lon)

    Returns:
        Comprehensive daily forecast dictionary.
    """
    from packages.context.src.dasha import get_current_dasha
    from packages.context.src.muhurta import (
        calculate_choghadiya,
        calculate_gulika,
        calculate_rahu_kaal,
        calculate_yamaghanda,
    )
    from packages.context.src.transit_aspects import get_transit_natal_aspects
    from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day
    from packages.cosmos.src.panchanga import get_panchanga
    from packages.cosmos.src.sunrise_sunset import get_sunrise_sunset

    # ---- Resolve dates and location ----
    qdate = datetime.fromisoformat(query_date) if query_date else datetime.now()
    # Normalize to start of day for consistency
    forecast_date = datetime(qdate.year, qdate.month, qdate.day, 12, 0, 0)

    loc_lat = location_lat if location_lat is not None else birth_lat
    loc_lon = location_lon if location_lon is not None else birth_lon

    birth_dt = datetime.fromisoformat(birth_datetime)
    lagna_idx = _get_rashi_index(lagna_rashi)

    # ---- 1. Panchanga ----
    try:
        panchanga_raw = get_panchanga(forecast_date, loc_lat, loc_lon)
    except Exception:
        panchanga_raw = {}

    panchanga_out = {
        "tithi": panchanga_raw.get("tithi", {}).get("name", "Unknown"),
        "vara": panchanga_raw.get("vara", {}).get("name", forecast_date.strftime("%A")),
        "yoga": panchanga_raw.get("yoga", {}).get("name", "Unknown"),
        "karana": panchanga_raw.get("karana", {}).get("name", "Unknown"),
        "nakshatra": panchanga_raw.get("nakshatra", {}).get("name", "Unknown"),
    }

    panchanga_score = _panchanga_quality_score(panchanga_raw)

    # ---- 2. Transit Moon position ----
    try:
        jd = get_julian_day(forecast_date)
        all_transits = get_all_planets(jd)
        moon_data = all_transits.get("moon", {})
        moon_transit_lon = moon_data.get("longitude", 0.0)
    except Exception:
        moon_transit_lon = 0.0
        all_transits = {}

    moon_rashi_idx = int(moon_transit_lon // 30)
    moon_sign = RASHI_NAMES[moon_rashi_idx] if 0 <= moon_rashi_idx < 12 else "aries"
    moon_house_from_lagna = _house_from_lagna(moon_rashi_idx, lagna_idx)
    natal_moon_rashi_idx = int(moon_longitude // 30)
    moon_house_from_moon = _house_from_lagna(moon_rashi_idx, natal_moon_rashi_idx)

    # Nakshatra of transit Moon
    moon_nak_num = int(moon_transit_lon / 13.333333333) + 1
    moon_nakshatra = panchanga_raw.get("nakshatra", {}).get("name", f"Nakshatra {moon_nak_num}")

    # ---- 3. Ashtakavarga BAV for Moon's sign ----
    # BAV requires full BirthChart object — use neutral default
    moon_bav = 4
    moon_quality = _moon_bav_to_quality(moon_bav)

    moon_transit_out = {
        "sign": moon_sign,
        "house_from_lagna": moon_house_from_lagna,
        "house_from_moon": moon_house_from_moon,
        "nakshatra": moon_nakshatra,
        "ashtakavarga_score": moon_bav,
        "quality": moon_quality,
    }

    # ---- 4. Current dasha ----
    dasha_md = "unknown"
    dasha_ad = "unknown"
    dasha_pd = "unknown"
    dasha_quality = 0.0
    try:
        dasha_info = get_current_dasha(birth_dt, moon_longitude, forecast_date)
        if dasha_info:
            dasha_md = dasha_info["mahadasha"]["lord"]
            dasha_ad = dasha_info["antardasha"]["lord"]
            if dasha_info.get("pratyantardasha"):
                dasha_pd = dasha_info["pratyantardasha"]["lord"]
            # Average quality of MD + AD
            dasha_quality = (
                _DASHA_LORD_QUALITY.get(dasha_md, 0.0) + _DASHA_LORD_QUALITY.get(dasha_ad, 0.0)
            ) / 2.0
    except Exception:
        dasha_info = None

    active_dasha_out = {
        "mahadasha": dasha_md,
        "antardasha": dasha_ad,
        "pratyantardasha": dasha_pd,
        "theme": _dasha_theme(dasha_md, dasha_ad, dasha_pd),
    }

    # ---- 5. Transit aspects active today ----
    transit_aspects_today: list[dict[str, Any]] = []
    aspect_score = 5.0
    try:
        transit_dict: dict[str, dict[str, Any]] = {}
        for planet, data in all_transits.items():
            transit_dict[planet] = {
                "longitude": data.get("longitude", 0.0),
                "rashi": int(data.get("longitude", 0.0) // 30),
                "speed": data.get("speed", 0),
            }

        raw_aspects = get_transit_natal_aspects(natal_planets, transit_dict, orb=5.0)
        for asp in raw_aspects:
            transit_aspects_today.append(
                {
                    "transit": asp.get("transit_planet", ""),
                    "natal": asp.get("natal_planet", ""),
                    "aspect": asp.get("aspect_type", ""),
                    "orb": asp.get("orb", 0.0),
                    "effect": asp.get("effect", ""),
                }
            )
        aspect_score = _aspect_quality_score(raw_aspects)
    except Exception:
        pass

    # ---- 6. Sunrise/sunset + inauspicious periods ----
    weekday = forecast_date.strftime("%A").lower()
    inauspicious_out: dict[str, Any] = {}
    choghadiya_highlights: dict[str, Any] = {"best_periods": [], "avoid_periods": []}
    try:
        sun_times = get_sunrise_sunset(forecast_date, loc_lat, loc_lon)
        sunrise = sun_times["sunrise"]
        sunset = sun_times["sunset"]

        # Rahu Kaal
        rk = calculate_rahu_kaal(sunrise, sunset, weekday)
        inauspicious_out["rahu_kaal"] = {
            "start": rk["start"].strftime("%H:%M"),
            "end": rk["end"].strftime("%H:%M"),
        }

        # Yamaghanda
        yg = calculate_yamaghanda(sunrise, sunset, weekday)
        inauspicious_out["yamaghanda"] = {
            "start": yg["start"].strftime("%H:%M"),
            "end": yg["end"].strftime("%H:%M"),
        }

        # Gulika
        gk = calculate_gulika(sunrise, sunset, weekday)
        inauspicious_out["gulika"] = {
            "start": gk["start"].strftime("%H:%M"),
            "end": gk["end"].strftime("%H:%M"),
        }

        # Choghadiya
        chogs = calculate_choghadiya(sunrise, sunset, weekday)
        for ch in chogs:
            entry = {
                "name": ch["name"],
                "start": ch["start"].strftime("%H:%M"),
                "end": ch["end"].strftime("%H:%M"),
                "quality": ch["quality"],
            }
            if ch["quality"] in ("excellent", "good"):
                choghadiya_highlights["best_periods"].append(entry)
            elif ch["quality"] == "poor":
                choghadiya_highlights["avoid_periods"].append(entry)
    except Exception:
        pass

    # ---- 7. Compute overall rating ----
    day_rating = _compute_day_rating(panchanga_score, moon_bav, aspect_score, dasha_quality)

    # ---- 8. Recommendations (knowledge-backed) ----
    try:
        from packages.context.src.forecast_knowledge import (
            build_daily_recommendations,
            build_daily_summary,
        )

        tithi_name = panchanga_out.get("tithi", "")
        recommendations = build_daily_recommendations(
            weekday=weekday,
            tithi_name=tithi_name,
            moon_nakshatra=moon_nakshatra,
            dasha_md=dasha_md,
            dasha_ad=dasha_ad,
            transit_aspects=transit_aspects_today,
            is_chandrashtama=(moon_house_from_moon == 8),
        )
    except Exception:
        recommendations = _generate_recommendations(
            panchanga_raw,
            moon_house_from_lagna,
            weekday,
            aspect_score,
            dasha_quality,
        )

    # ---- 9. Summary (knowledge-backed) ----
    try:
        summary = build_daily_summary(
            day_rating=day_rating,
            moon_sign=moon_sign,
            moon_nakshatra=moon_nakshatra,
            moon_house_from_lagna=moon_house_from_lagna,
            dasha_md=dasha_md,
            dasha_ad=dasha_ad,
            transit_aspects=transit_aspects_today,
            is_chandrashtama=(moon_house_from_moon == 8),
        )
    except Exception:
        summary = _generate_daily_summary(
            day_rating,
            moon_sign,
            moon_house_from_lagna,
            dasha_md,
            dasha_ad,
        )

    # ---- 10. State engine (single source of truth for composite + areas) ----
    area_scores: dict[str, dict[str, Any]] = {}
    state_composite: float | None = None
    mental_state = ""
    hora_lord = ""
    active_yogas: list[str] = []
    active_doshas: list[str] = []
    sade_sati_info: dict[str, Any] = {"active": False, "phase": None}
    factor_scores: list[dict[str, Any]] = []

    try:
        from packages.context.src.state_engine import compute_state_vector

        state_vec = compute_state_vector(
            birth_datetime=birth_datetime,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
            query_datetime=forecast_date.isoformat(),
            location_lat=loc_lat,
            location_lon=loc_lon,
        )
        for area in state_vec.get("areas", []):
            area_scores[area["id"]] = {
                "score": area["score"],
                "insight": area["insight"],
                "dominant_planet": area["dominant_planet"],
                "double_transit": area["double_transit"],
            }
        # Extract rich data from state vector
        state_composite = state_vec.get("composite")
        mental_state = state_vec.get("mental_state", "")
        hora_lord = state_vec.get("hora_lord", "")
        active_yogas = state_vec.get("natal_yogas", [])
        active_doshas = state_vec.get("natal_doshas", [])
        sade_sati_info = state_vec.get("sade_sati", {"active": False, "phase": None})
        factor_scores = state_vec.get("factors", [])
    except Exception:
        # Fallback: all areas neutral
        for area_id in AREA_HOUSES:
            area_scores[area_id] = {
                "score": 5.0,
                "insight": f"Score unavailable for {area_id}",
                "dominant_planet": AREA_PLANETS.get(area_id, [""])[0]
                if AREA_PLANETS.get(area_id)
                else "",
                "double_transit": False,
            }

    # Use state engine composite as day_rating if available (replaces primitive weights)
    if state_composite is not None:
        day_rating = max(1, min(10, round(state_composite)))

    # ---- 11. Gochara summary per planet ----
    gochara_summary: list[dict[str, Any]] = []
    try:
        from packages.context.src.transits import get_gochara

        transit_rashis = {p: int(d.get("longitude", 0) // 30) for p, d in all_transits.items()}
        for planet_name, planet_data in all_transits.items():
            if planet_name == "moon":
                continue  # Moon has its own section
            t_rashi = int(planet_data.get("longitude", 0) // 30)
            gochara = get_gochara(natal_moon_rashi_idx, planet_name, t_rashi, transit_rashis)
            gochara_summary.append(
                {
                    "planet": planet_name,
                    "sign": RASHI_NAMES[t_rashi] if 0 <= t_rashi < 12 else "unknown",
                    "house_from_moon": gochara.get("house_from_moon", 0),
                    "is_favorable": gochara.get("is_favorable", False),
                    "has_vedha": gochara.get("has_vedha", False),
                    "net_effect": gochara.get("net_effect", "neutral"),
                }
            )
    except Exception:
        pass

    # ---- 12. Chandrashtama check (8th from natal Moon) ----
    is_chandrashtama = moon_house_from_moon == 8

    # ---- 13. Upcoming triggers (next 3 days) ----
    upcoming_triggers: list[dict[str, Any]] = []
    try:
        from packages.context.src.transit_tracker import get_upcoming_triggers

        triggers = get_upcoming_triggers(
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            birth_datetime=birth_datetime,
            lagna_rashi=lagna_rashi,
            query_date=qdate.strftime("%Y-%m-%d"),
            days_ahead=3,
        )
        upcoming_triggers = triggers[:5]  # top 5
    except Exception:
        pass

    return {
        "date": qdate.strftime("%Y-%m-%d"),
        "day_rating": day_rating,
        "summary": summary,
        "mental_state": mental_state,
        "composite_score": state_composite,
        "panchanga": panchanga_out,
        "moon_transit": moon_transit_out,
        "active_dasha": active_dasha_out,
        "transit_aspects_today": transit_aspects_today,
        "inauspicious_periods": inauspicious_out,
        "choghadiya_highlights": choghadiya_highlights,
        "recommendations": recommendations,
        "area_scores": area_scores,
        "hora_lord": hora_lord,
        "gochara_summary": gochara_summary,
        "is_chandrashtama": is_chandrashtama,
        "active_yogas": active_yogas[:10],  # top 10
        "active_doshas": active_doshas,
        "sade_sati": sade_sati_info,
        "factor_scores": factor_scores,
        "upcoming_triggers": upcoming_triggers,
    }


def _dasha_theme(md: str, ad: str, pd: str) -> str:
    """Generate a short dasha theme description."""
    themes: dict[str, str] = {
        "sun": "authority",
        "moon": "emotions",
        "mars": "action",
        "mercury": "intellect",
        "jupiter": "wisdom",
        "venus": "comfort",
        "saturn": "discipline",
        "rahu": "ambition",
        "ketu": "detachment",
    }
    md_t = themes.get(md, md)
    ad_t = themes.get(ad, ad)
    pd_t = themes.get(pd, pd)
    if pd and pd != "unknown":
        return f"{md_t.title()} meets {ad_t}, with {pd_t} undertone"
    return f"{md_t.title()} meets {ad_t}"
