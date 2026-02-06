"""
108 Context MCP Server

Provides dasha calculations, transit analysis, and timing tools.
Includes Vimshottari Dasha periods, Sade Sati tracking, and muhurta evaluation.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add packages to path
SERVICES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERVICES_ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402

# Import context package functions
from packages.context.src import (  # noqa: E402
    calculate_all_inauspicious,
    check_dhaiya,
    check_sade_sati,
    evaluate_muhurta,
    find_next_good_muhurta,
    get_antardasha_effect,
    get_antardasha_sequence,
    get_current_dasha,
    get_dasha_balance_at_birth,
    get_gochara,
    get_mahadasha_sequence,
    get_pratyantardasha_effect,
)
from packages.context.src.ashtottari_dasha import (  # noqa: E402
    calculate_ashtottari_sequence,
    get_current_ashtottari,
    is_ashtottari_applicable,
)
from packages.context.src.muhurta import (  # noqa: E402
    get_abhijit_muhurta,
    get_brahma_muhurta,
    get_eclipse_periods,
    get_marana_kaal,
)
from packages.context.src.narayana_dasha import (  # noqa: E402
    calculate_narayana_sequence,
    get_current_narayana_dasha,
)
from packages.context.src.progressions import get_current_progressions  # noqa: E402
from packages.context.src.transits import get_enriched_transit_analysis  # noqa: E402
from packages.context.src.yogini_dasha import (  # noqa: E402
    calculate_yogini_sequence,
    get_current_yogini_dasha,
    get_yogini_antardasha,
)

# Import cosmos constants
from packages.cosmos.src import (  # noqa: E402
    get_all_planets,
    get_julian_day,
    get_karana,
    get_sunrise_sunset,
    get_tithi,
    get_vara,
    get_yoga,
    longitude_to_nakshatra,
)

# Initialize MCP server
mcp = FastMCP("108-context")

SIGNS = [
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


@mcp.tool()
def current_dasha(
    birth_datetime: str, moon_longitude: float, query_datetime: str | None = None
) -> dict[str, Any]:
    """
    Get current Mahadasha, Antardasha, and Pratyantardasha.

    Args:
        birth_datetime: Birth datetime in ISO format (e.g., "1992-12-03T03:00:00+05:30")
        moon_longitude: Moon's sidereal longitude at birth (0-360)
        query_datetime: Date to check (ISO format), defaults to now

    Returns:
        Current dasha periods with lords, dates, remaining time, and interpretation

    Example:
        current_dasha("1992-12-03T03:00:00+05:30", 324.11, "2026-02-04")
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        if query_datetime:
            query_dt = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            if query_dt.tzinfo:
                query_dt = query_dt.replace(tzinfo=None)
        else:
            query_dt = datetime.now()

        result = get_current_dasha(birth_dt, moon_longitude, query_dt)

        md_lord = result["mahadasha"]["lord"]
        ad_lord = result["antardasha"]["lord"]
        pd_info = result.get("pratyantardasha")
        pd_lord = pd_info.get("lord") if pd_info else None

        # Get effects data
        ad_effects = get_antardasha_effect(md_lord, ad_lord)
        pd_effects = None
        if pd_lord:
            pd_effects = get_pratyantardasha_effect(md_lord, ad_lord, pd_lord)

        return {
            "query_date": query_dt.isoformat(),
            "mahadasha": {
                "lord": md_lord,
                "start_date": result["mahadasha"]["start_date"].isoformat(),
                "end_date": result["mahadasha"]["end_date"].isoformat(),
                "days_remaining": result["mahadasha"]["days_remaining"],
                "years_total": result["mahadasha"].get("years", 0),
            },
            "antardasha": {
                "lord": ad_lord,
                "start_date": result["antardasha"]["start_date"].isoformat(),
                "end_date": result["antardasha"]["end_date"].isoformat(),
                "days_remaining": result["antardasha"]["days_remaining"],
                "effects": ad_effects,
            },
            "pratyantardasha": {
                **pd_info,
                "effects": pd_effects,
            }
            if pd_info
            else None,
            "interpretation": _get_dasha_interpretation(md_lord, ad_lord),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def dasha_periods(
    birth_datetime: str,
    moon_longitude: float,
    years: int = 120,  # noqa: ARG001 - Reserved for future pagination
) -> dict[str, Any]:
    """
    Get all Mahadasha periods for lifetime.

    Args:
        birth_datetime: Birth datetime in ISO format
        moon_longitude: Moon's sidereal longitude at birth (0-360)
        years: Number of years to calculate (default 120 = full cycle)

    Returns:
        Complete Mahadasha timeline with start/end dates, lords, and durations

    Example:
        dasha_periods("1992-12-03T03:00:00+05:30", 324.11, 120)
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        # Get initial balance
        balance = get_dasha_balance_at_birth(moon_longitude, birth_dt)

        # Get full sequence
        mahadashas = get_mahadasha_sequence(birth_dt, moon_longitude)

        periods = []
        for m in mahadashas:
            periods.append(
                {
                    "lord": m["lord"],
                    "start_date": m["start_date"].isoformat(),
                    "end_date": m["end_date"].isoformat(),
                    "years": m["years"],
                    "is_current": m.get("is_current", False),
                }
            )

        return {
            "birth_datetime": birth_datetime,
            "moon_longitude": moon_longitude,
            "birth_nakshatra_lord": balance["lord"],
            "initial_balance_years": balance["remaining_years"],
            "count": len(periods),
            "mahadashas": periods,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def transit_analysis(natal_moon_rashi: str, transit_positions: dict[str, str]) -> dict[str, Any]:
    """
    Analyze current transits from natal Moon (Gochara).

    Args:
        natal_moon_rashi: Birth Moon sign (e.g., "aquarius")
        transit_positions: Current planet signs {planet: sign}
                          Expected keys: sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu

    Returns:
        Transit analysis with favorable/unfavorable indicators, Sade Sati status, and overall assessment

    Example:
        transit_analysis("aquarius", {"sun": "aries", "saturn": "aquarius", "mars": "virgo"})
    """
    try:
        moon_idx = SIGNS.index(natal_moon_rashi.lower())

        # Convert transit positions to indices
        transits = {}
        for planet, sign in transit_positions.items():
            if sign.lower() in SIGNS:
                transits[planet.lower()] = SIGNS.index(sign.lower())

        # Analyze each planet's transit
        planet_analysis = {}
        for planet, rashi_idx in transits.items():
            gochara = get_gochara(planet, rashi_idx, moon_idx)
            planet_analysis[planet] = {
                "current_sign": SIGNS[rashi_idx],
                "house_from_moon": gochara.get("house_from_moon", 0),
                "is_favorable": gochara.get("is_favorable", False),
                "effects": gochara.get("effects", []),
            }

        # Check Sade Sati
        saturn_idx = transits.get("saturn", -1)
        sade_sati = check_sade_sati(moon_idx, saturn_idx) if saturn_idx >= 0 else {"active": False}

        # Check Dhaiya
        dhaiya = check_dhaiya(moon_idx, saturn_idx) if saturn_idx >= 0 else {"active": False}

        return {
            "natal_moon": natal_moon_rashi,
            "planets": planet_analysis,
            "sade_sati": sade_sati,
            "dhaiya": dhaiya,
            "overall_assessment": _assess_transits(planet_analysis, sade_sati, dhaiya),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def sade_sati_status(natal_moon_rashi: str, saturn_rashi: str) -> dict[str, Any]:
    """
    Check Sade Sati status and phase.

    Sade Sati is a 7.5-year transit of Saturn that tests and transforms.
    It has three phases:
    - Rising (1st phase): Saturn in 12th from Moon
    - Peak (2nd phase): Saturn transiting over Moon
    - Setting (3rd phase): Saturn in 2nd from Moon

    Args:
        natal_moon_rashi: Birth Moon sign (e.g., "aquarius")
        saturn_rashi: Current Saturn sign (e.g., "aquarius")

    Returns:
        Sade Sati status, current phase, effects, and remedies

    Example:
        sade_sati_status("aquarius", "capricorn")
    """
    try:
        moon_idx = SIGNS.index(natal_moon_rashi.lower())
        saturn_idx = SIGNS.index(saturn_rashi.lower())

        result = check_sade_sati(moon_idx, saturn_idx)

        if result["active"]:
            phase = result.get("phase", "unknown")
            return {
                "is_active": True,
                "natal_moon": natal_moon_rashi,
                "saturn_current": saturn_rashi,
                "phase": phase,
                "phase_description": _get_sade_sati_description(phase),
                "effects": _get_sade_sati_effects(phase),
                "remedies": [
                    "Worship Lord Hanuman on Saturdays",
                    "Recite Shani Stotra or Shani Chalisa daily",
                    "Donate black sesame seeds, iron, or black items on Saturdays",
                    "Perform Shani Puja or Abhisheka",
                    "Chant 'Om Sham Shanicharaya Namah' 108 times",
                    "Wear Blue Sapphire only after proper astrological analysis",
                    "Practice meditation and patience",
                    "Engage in social service and charity",
                ],
            }
        else:
            return {
                "is_active": False,
                "natal_moon": natal_moon_rashi,
                "saturn_current": saturn_rashi,
                "note": "Sade Sati is not currently active",
                "distance": _calculate_house_distance(moon_idx, saturn_idx),
                "years_until_sade_sati": _years_until_sade_sati(moon_idx, saturn_idx),
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def dhaiya_status(natal_moon_rashi: str, saturn_rashi: str) -> dict[str, Any]:
    """
    Check Dhaiya (Small Panoti) or Kantaka Shani status.

    Dhaiya occurs when Saturn transits the 4th or 8th house from natal Moon.
    It lasts about 2.5 years and is milder than Sade Sati but still challenging.

    Args:
        natal_moon_rashi: Birth Moon sign
        saturn_rashi: Current Saturn sign

    Returns:
        Dhaiya status, effects, and duration

    Example:
        dhaiya_status("gemini", "virgo")
    """
    try:
        moon_idx = SIGNS.index(natal_moon_rashi.lower())
        saturn_idx = SIGNS.index(saturn_rashi.lower())

        result = check_dhaiya(moon_idx, saturn_idx)

        if result["active"]:
            result.get("phase", "unknown")
            return {
                "is_active": True,
                "type": "Dhaiya (Kantaka Shani)",
                "natal_moon": natal_moon_rashi,
                "saturn_current": saturn_rashi,
                "house_position": result.get("house_position", 0),
                "effects": [
                    "Obstacles in work and projects",
                    "Health concerns and immunity issues",
                    "Financial pressures and unexpected expenses",
                    "Mental stress and anxiety",
                    "Relationship tensions",
                ],
                "remedies": [
                    "Worship Lord Shani and Hanuman",
                    "Recite Shani Chalisa",
                    "Donate to the needy on Saturdays",
                    "Wear Iron ring on Saturn finger",
                    "Practice patience and acceptance",
                ],
            }
        else:
            return {
                "is_active": False,
                "type": "Dhaiya (Kantaka Shani)",
                "natal_moon": natal_moon_rashi,
                "saturn_current": saturn_rashi,
                "note": "Dhaiya is not currently active",
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def muhurta_check(
    datetime_iso: str,
    activity: str,
    latitude: float = 0,
    longitude: float = 0,
) -> dict[str, Any]:
    """
    Check muhurta quality for a specific activity.

    Muhurta is an auspicious moment for starting important activities.
    This evaluates the time against Vedic calendar principles.

    Args:
        datetime_iso: Date/time to check in ISO format
        activity: Activity type (marriage, travel, business_start, surgery,
                 new_job, house_warming, etc.)
        latitude: Location latitude (optional)
        longitude: Location longitude (optional)

    Returns:
        Muhurta evaluation with score, quality, panchanga, and inauspicious periods

    Example:
        muhurta_check("2026-02-14T18:00:00+05:30", "marriage", 12.97, 77.59)
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)

        # Calculate panchanga for the time
        jd = get_julian_day(dt)
        planets = get_all_planets(jd)

        sun_lon = planets["sun"]["longitude"]
        moon_lon = planets["moon"]["longitude"]

        tithi_data = get_tithi(sun_lon, moon_lon)
        yoga_data = get_yoga(sun_lon, moon_lon)
        karana_data = get_karana(tithi_data["number"])
        vara_data = get_vara(dt)
        moon_nak = longitude_to_nakshatra(moon_lon)

        panchanga = {
            "tithi": tithi_data["number"],
            "tithi_progress": round(tithi_data.get("progress", 0), 2),
            "nakshatra": moon_nak["name"],
            "nakshatra_number": moon_nak["number"],
            "yoga": yoga_data["number"],
            "karana": karana_data["number"],
            "vara": vara_data["weekday"],
        }

        # Evaluate muhurta
        try:
            evaluation = evaluate_muhurta(activity, panchanga, dt)
        except (ValueError, TypeError):
            evaluation = {"quality": "unknown", "score": 0, "factors": []}

        # Calculate actual sunrise/sunset (use location if provided, else defaults)
        if latitude != 0 or longitude != 0:
            sr_data = get_sunrise_sunset(dt, latitude, longitude)
            sunrise = sr_data["sunrise"].replace(tzinfo=None)
            sunset = sr_data["sunset"].replace(tzinfo=None)
        else:
            sunrise = dt.replace(hour=6, minute=0, second=0)
            sunset = dt.replace(hour=18, minute=0, second=0)
        weekday = dt.strftime("%A").lower()

        inauspicious = calculate_all_inauspicious(sunrise, sunset, weekday)

        return {
            "datetime": datetime_iso,
            "activity": activity,
            "panchanga": panchanga,
            "evaluation": {
                "quality": evaluation.get("quality", "unknown"),
                "score": evaluation.get("score", 0),
                "is_favorable": evaluation.get("score", 0) >= 6,
            },
            "inauspicious_periods": {
                "rahu_kaal": {
                    "start": inauspicious["rahu_kaal"]["start"].strftime("%H:%M")
                    if inauspicious.get("rahu_kaal")
                    else None,
                    "end": inauspicious["rahu_kaal"]["end"].strftime("%H:%M")
                    if inauspicious.get("rahu_kaal")
                    else None,
                },
                "yamaghanda": {
                    "start": inauspicious["yamaghanda"]["start"].strftime("%H:%M")
                    if inauspicious.get("yamaghanda")
                    else None,
                    "end": inauspicious["yamaghanda"]["end"].strftime("%H:%M")
                    if inauspicious.get("yamaghanda")
                    else None,
                },
                "gulika": {
                    "start": inauspicious["gulika"]["start"].strftime("%H:%M")
                    if inauspicious.get("gulika")
                    else None,
                    "end": inauspicious["gulika"]["end"].strftime("%H:%M")
                    if inauspicious.get("gulika")
                    else None,
                },
            },
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def find_good_muhurta(
    start_date: str, end_date: str, activity: str, count: int = 5
) -> dict[str, Any]:
    """
    Find next good muhurta dates for an activity.

    Args:
        start_date: Start date in ISO format
        end_date: End date in ISO format
        activity: Activity type (marriage, travel, surgery, etc.)
        count: Number of good muhurtas to find (default 5)

    Returns:
        List of recommended muhurta dates with quality scores

    Example:
        find_good_muhurta("2026-02-10", "2026-03-10", "marriage", 5)
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        if start_dt.tzinfo:
            start_dt = start_dt.replace(tzinfo=None)
        if end_dt.tzinfo:
            end_dt = end_dt.replace(tzinfo=None)

        results = find_next_good_muhurta(start_dt, end_dt, activity, count)

        muhurtas = []
        for r in results:
            muhurtas.append(
                {
                    "datetime": r["datetime"].isoformat(),
                    "quality": r.get("quality", "good"),
                    "score": r.get("score", 0),
                    "tithi": r.get("tithi", 0),
                    "nakshatra": r.get("nakshatra", ""),
                    "vara": r.get("vara", ""),
                }
            )

        return {
            "activity": activity,
            "search_period": {"start": start_date, "end": end_date},
            "muhurtas_found": len(muhurtas),
            "recommendations": muhurtas,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def antardasha_periods(
    birth_datetime: str, moon_longitude: float, mahadasha_lord: str | None = None
) -> dict[str, Any]:
    """
    Get Antardasha (sub-period) breakdown for a Mahadasha.

    Args:
        birth_datetime: Birth datetime in ISO format
        moon_longitude: Moon's sidereal longitude at birth
        mahadasha_lord: Specific Mahadasha lord to analyze (optional)
                       If not provided, returns for current Mahadasha

    Returns:
        List of Antardasha periods with dates and lords

    Example:
        antardasha_periods("1992-12-03T03:00:00+05:30", 324.11, "mercury")
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        # Get antardasha sequences
        antardashas = get_antardasha_sequence(birth_dt, moon_longitude, mahadasha_lord)

        periods = []
        for a in antardashas:
            periods.append(
                {
                    "mahadasha_lord": a["mahadasha_lord"],
                    "antardasha_lord": a["antardasha_lord"],
                    "start_date": a["start_date"].isoformat(),
                    "end_date": a["end_date"].isoformat(),
                    "months": a.get("months", 0),
                }
            )

        return {
            "birth_datetime": birth_datetime,
            "mahadasha_lord": mahadasha_lord,
            "antardasha_count": len(periods),
            "antardashas": periods,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def antardasha_effects(mahadasha_lord: str, antardasha_lord: str) -> dict[str, Any]:
    """
    Get detailed Antardasha effects (81 combinations).

    Retrieves comprehensive interpretation for any Mahadasha-Antardasha combination,
    including effects on health, career, relationships, finances, and spiritual growth.

    Args:
        mahadasha_lord: Mahadasha planet (sun, moon, mars, mercury, jupiter, venus, saturn, rahu, ketu)
        antardasha_lord: Antardasha planet

    Returns:
        Detailed effects dictionary including:
        - general_effects: Overall themes of this period
        - positive: Favorable outcomes
        - negative: Challenges to watch
        - health: Health-related effects
        - career: Professional matters
        - relationships: Relationship dynamics
        - finances: Financial indications
        - spiritual: Spiritual growth aspects

    Example:
        antardasha_effects("jupiter", "venus")
    """
    try:
        effects = get_antardasha_effect(mahadasha_lord, antardasha_lord)

        if effects:
            return {
                "mahadasha": mahadasha_lord.lower(),
                "antardasha": antardasha_lord.lower(),
                "found": True,
                **effects,
            }
        else:
            return {
                "mahadasha": mahadasha_lord.lower(),
                "antardasha": antardasha_lord.lower(),
                "found": False,
                "message": f"No effects data found for {mahadasha_lord}-{antardasha_lord} combination",
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def pratyantardasha_effects(
    mahadasha_lord: str, antardasha_lord: str, pratyantardasha_lord: str
) -> dict[str, Any]:
    """
    Get detailed Pratyantardasha effects (729 combinations).

    Retrieves interpretation for the third level of Vimshottari Dasha system.
    Pratyantardasha provides fine-grained timing for events within Antardasha.

    Args:
        mahadasha_lord: Mahadasha planet
        antardasha_lord: Antardasha planet
        pratyantardasha_lord: Pratyantardasha planet

    Returns:
        Detailed effects dictionary including:
        - theme: Overall theme of this period
        - duration_description: Human-readable duration
        - effects: General effects
        - health: Health indications
        - career: Professional matters
        - relationships: Relationship dynamics
        - finances: Financial outlook
        - timing: Auspicious timing within period
        - recommendations: Suggested actions

    Example:
        pratyantardasha_effects("jupiter", "venus", "saturn")
    """
    try:
        effects = get_pratyantardasha_effect(mahadasha_lord, antardasha_lord, pratyantardasha_lord)

        if effects:
            return {
                "mahadasha": mahadasha_lord.lower(),
                "antardasha": antardasha_lord.lower(),
                "pratyantardasha": pratyantardasha_lord.lower(),
                "found": True,
                **effects,
            }
        else:
            return {
                "mahadasha": mahadasha_lord.lower(),
                "antardasha": antardasha_lord.lower(),
                "pratyantardasha": pratyantardasha_lord.lower(),
                "found": False,
                "message": (
                    f"No effects data found for "
                    f"{mahadasha_lord}-{antardasha_lord}-{pratyantardasha_lord} combination"
                ),
            }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def enriched_transit(
    natal_moon_rashi: str,
    transit_positions: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """
    Enriched transit analysis with nakshatra effects, combustion, and retrograde data.

    Extends basic Gochara analysis with:
    - Nakshatra-specific transit effects (243 combinations)
    - Combustion detection for each planet
    - Retrograde effects for retrograde planets
    - Sade Sati and Dhaiya status

    Args:
        natal_moon_rashi: Birth Moon sign (e.g., "aquarius")
        transit_positions: Dict of planet transit data. Each value should have:
            - sign: Current sign name (e.g., "aquarius")
            - nakshatra: Current nakshatra (e.g., "shatabhisha")
            - longitude: Current longitude (0-360)
            - is_retrograde: Whether planet is retrograde ("true"/"false")

    Returns:
        Enriched transit analysis with per-planet nakshatra effects,
        combustion status, retrograde effects, and overall assessment

    Example:
        enriched_transit("aquarius", {
            "sun": {"sign": "aquarius", "nakshatra": "shatabhisha", "longitude": "310", "is_retrograde": "false"},
            "saturn": {"sign": "aquarius", "nakshatra": "shatabhisha", "longitude": "315", "is_retrograde": "true"}
        })
    """
    try:
        moon_idx = SIGNS.index(natal_moon_rashi.lower())

        # Convert string-based transit data to typed format
        typed_data: dict[str, dict[str, Any]] = {}
        for planet, data in transit_positions.items():
            sign_name = data.get("sign", "").lower()
            rashi_idx = SIGNS.index(sign_name) if sign_name in SIGNS else 0
            typed_data[planet.lower()] = {
                "rashi": rashi_idx,
                "nakshatra": data.get("nakshatra", ""),
                "longitude": float(data.get("longitude", 0)),
                "is_retrograde": str(data.get("is_retrograde", "false")).lower() == "true",
            }

        result = get_enriched_transit_analysis(moon_idx, typed_data)
        return result

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def yogini_dasha(
    birth_datetime: str,
    moon_nakshatra: int,
    moon_pada: int,
    degree_in_nakshatra: float,
    query_datetime: str | None = None,
) -> dict[str, Any]:
    """
    Calculate Yogini Dasha periods (36-year cycle with 8 Yoginis).

    The Yogini Dasha system uses 8 Yoginis (Mangala, Pingala, Dhanya,
    Bhramari, Bhadrika, Ulka, Siddha, Sankata) totaling 36 years per cycle.

    Args:
        birth_datetime: Birth datetime in ISO format
        moon_nakshatra: Moon's nakshatra number (1-27)
        moon_pada: Moon's pada (1-4)
        degree_in_nakshatra: Degrees traversed in nakshatra (0-13.333)
        query_datetime: Query datetime (ISO format, defaults to now)

    Returns:
        Current Yogini Dasha, full sequence, and antardasha breakdown

    Example:
        yogini_dasha("1992-12-03T03:00:00+05:30", 25, 3, 10.0, "2026-02-04")
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        query_dt = None
        if query_datetime:
            query_dt = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            if query_dt.tzinfo:
                query_dt = query_dt.replace(tzinfo=None)

        # Get current dasha
        current = get_current_yogini_dasha(
            birth_dt, moon_nakshatra, moon_pada, degree_in_nakshatra, query_dt
        )

        # Get full sequence (3 cycles = 108 years)
        periods = calculate_yogini_sequence(
            birth_dt, moon_nakshatra, moon_pada, degree_in_nakshatra, cycles=3
        )

        # Get antardashas for current maha-dasha
        current_maha = None
        for p in periods:
            start = p.start_date.replace(tzinfo=None) if p.start_date.tzinfo else p.start_date
            end = p.end_date.replace(tzinfo=None) if p.end_date.tzinfo else p.end_date
            check_dt = query_dt or datetime.now()
            if start <= check_dt < end:
                current_maha = p
                break

        antardashas = []
        if current_maha:
            antardashas = get_yogini_antardasha(current_maha)

        return {
            "system": "yogini",
            "birth_datetime": birth_datetime,
            "current": {
                "yogini": current["yogini"].value
                if hasattr(current["yogini"], "value")
                else str(current["yogini"]),
                "lord": current["lord"].value
                if hasattr(current["lord"], "value")
                else str(current["lord"]),
                "start_date": current["start_date"].isoformat(),
                "end_date": current["end_date"].isoformat(),
                "remaining_days": current["remaining_days"],
            },
            "antardashas": [
                {
                    "yogini": ad["yogini"].value
                    if hasattr(ad["yogini"], "value")
                    else str(ad["yogini"]),
                    "lord": ad["lord"].value if hasattr(ad["lord"], "value") else str(ad["lord"]),
                    "start_date": ad["start_date"].isoformat(),
                    "end_date": ad["end_date"].isoformat(),
                }
                for ad in antardashas
            ],
            "full_sequence": [
                {
                    "yogini": p.yogini.value if hasattr(p.yogini, "value") else str(p.yogini),
                    "lord": p.planet_lord.value
                    if hasattr(p.planet_lord, "value")
                    else str(p.planet_lord),
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat(),
                    "duration_years": p.duration_years,
                }
                for p in periods
            ],
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def narayana_dasha(
    birth_datetime: str,
    chart_data: dict[str, Any],
    query_datetime: str | None = None,
) -> dict[str, Any]:
    """
    Calculate Narayana Dasha periods (sign-based 108-year cycle).

    Narayana Dasha is a Jaimini sign-based dasha system. Direction of
    progression depends on lagna parity (odd=forward, even=reverse).

    Args:
        birth_datetime: Birth datetime in ISO format
        chart_data: Chart data including planets and lagna_rashi
        query_datetime: Query datetime (ISO format, defaults to now)

    Returns:
        Current Narayana Dasha, full sequence, and antardasha breakdown

    Example:
        narayana_dasha("1992-12-03T03:00:00+05:30",
                       {"lagna_rashi": "libra", "planets": {...}})
    """
    try:
        from packages.core.src import (
            BirthChart,
            BirthData,
            HouseCusps,
            Planet,
            PlanetPosition,
            Rashi,
        )

        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        # Build BirthChart from chart_data
        lagna_str = chart_data.get("lagna_rashi", "aries").lower()
        lagna_enum = Rashi(lagna_str)

        planet_positions = {}
        planets_data = chart_data.get("planets", {})
        for pname, pdata in planets_data.items():
            try:
                p_enum = Planet(pname.lower())
                r_enum = Rashi(pdata.get("sign", "aries").lower())
                planet_positions[p_enum] = PlanetPosition(
                    planet=p_enum,
                    longitude=pdata.get("longitude", 0.0),
                    latitude=0.0,
                    speed=0.0,
                    rashi=r_enum,
                    rashi_degree=pdata.get("longitude", 0.0) % 30,
                    nakshatra=pdata.get("nakshatra", "ashwini"),
                    nakshatra_pada=pdata.get("nakshatra_pada", 1),
                    nakshatra_lord=Planet.KETU,
                    is_retrograde=pdata.get("is_retrograde", False),
                    house=pdata.get("house", 1),
                )
            except (ValueError, KeyError):
                continue

        chart = BirthChart(
            user_id="mcp_query",
            birth_data=BirthData(
                datetime_utc=birth_dt, latitude=0.0, longitude=0.0, timezone="UTC"
            ),
            planets=planet_positions,
            houses=HouseCusps(ascendant=0.0, mc=270.0, cusps=[i * 30 for i in range(12)]),
            lagna_rashi=lagna_enum,
            moon_rashi=Rashi(chart_data.get("moon_rashi", "aries").lower()),
            moon_nakshatra=chart_data.get("moon_nakshatra", "ashwini"),
            ayanamsa=23.45,
            calculated_at=datetime.now(),
        )

        # Calculate
        periods = calculate_narayana_sequence(birth_dt, chart, cycles=1)

        query_dt = None
        if query_datetime:
            query_dt = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            if query_dt.tzinfo:
                query_dt = query_dt.replace(tzinfo=None)

        current = get_current_narayana_dasha(birth_dt, chart, query_dt)

        return {
            "system": "narayana",
            "birth_datetime": birth_datetime,
            "current": {
                "rashi": current["rashi"].value
                if hasattr(current["rashi"], "value")
                else str(current["rashi"]),
                "start_date": current["start_date"].isoformat(),
                "end_date": current["end_date"].isoformat(),
                "remaining_days": current["remaining_days"],
            },
            "full_sequence": [
                {
                    "rashi": p.rashi.value if hasattr(p.rashi, "value") else str(p.rashi),
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat(),
                    "duration_years": p.duration_years,
                    "is_forward": p.is_forward,
                }
                for p in periods
            ],
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def compare_dashas(
    birth_datetime: str,
    moon_longitude: float,
    moon_nakshatra: int,
    moon_pada: int,
    degree_in_nakshatra: float,
    query_datetime: str | None = None,
) -> dict[str, Any]:
    """
    Compare current Vimshottari and Yogini Dasha periods.

    Provides side-by-side comparison of both major dasha systems
    for a given moment.

    Args:
        birth_datetime: Birth datetime in ISO format
        moon_longitude: Moon's sidereal longitude (0-360)
        moon_nakshatra: Moon's nakshatra number (1-27)
        moon_pada: Moon's pada (1-4)
        degree_in_nakshatra: Degrees traversed in nakshatra (0-13.333)
        query_datetime: Query datetime (ISO format, defaults to now)

    Returns:
        Side-by-side comparison of Vimshottari and Yogini dasha periods

    Example:
        compare_dashas("1992-12-03T03:00:00+05:30", 326.85, 25, 3, 10.0)
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        query_dt = None
        if query_datetime:
            query_dt = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            if query_dt.tzinfo:
                query_dt = query_dt.replace(tzinfo=None)

        # Vimshottari
        vimshottari = get_current_dasha(birth_dt, moon_longitude, query_dt)

        # Yogini
        yogini_current = get_current_yogini_dasha(
            birth_dt, moon_nakshatra, moon_pada, degree_in_nakshatra, query_dt
        )

        return {
            "query_date": (query_dt or datetime.now()).isoformat(),
            "vimshottari": {
                "mahadasha_lord": vimshottari["mahadasha"]["lord"],
                "antardasha_lord": vimshottari["antardasha"]["lord"],
                "mahadasha_end": vimshottari["mahadasha"]["end_date"].isoformat(),
                "days_remaining": vimshottari["mahadasha"]["days_remaining"],
            },
            "yogini": {
                "yogini": yogini_current["yogini"].value
                if hasattr(yogini_current["yogini"], "value")
                else str(yogini_current["yogini"]),
                "lord": yogini_current["lord"].value
                if hasattr(yogini_current["lord"], "value")
                else str(yogini_current["lord"]),
                "end_date": yogini_current["end_date"].isoformat(),
                "remaining_days": yogini_current["remaining_days"],
            },
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def abhijit_muhurta(datetime_iso: str, latitude: float, longitude: float) -> dict[str, Any]:
    """
    Calculate Abhijit Muhurta (the most universally auspicious time of the day).

    Abhijit is the 8th muhurta of the day (around local noon). The day is divided
    into 15 muhurtas from sunrise to sunset. Abhijit is ideal for starting any
    important activity.

    Args:
        datetime_iso: Date in ISO format (e.g., "2026-02-04T12:00:00+05:30")
        latitude: Geographic latitude (-90 to 90)
        longitude: Geographic longitude (-180 to 180)

    Returns:
        Start and end times of Abhijit Muhurta for the given date/location

    Example:
        abhijit_muhurta("2026-02-04T12:00:00+05:30", 16.726, 81.288)
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)

        sr_data = get_sunrise_sunset(dt, latitude, longitude)
        sunrise = sr_data["sunrise"]
        sunset = sr_data["sunset"]
        if sunrise.tzinfo:
            sunrise = sunrise.replace(tzinfo=None)
        if sunset.tzinfo:
            sunset = sunset.replace(tzinfo=None)

        start, end = get_abhijit_muhurta(sunrise, sunset)

        return {
            "datetime": datetime_iso,
            "location": {"latitude": latitude, "longitude": longitude},
            "abhijit_start": start.isoformat(),
            "abhijit_end": end.isoformat(),
            "duration_minutes": round((end - start).total_seconds() / 60, 1),
            "sunrise": sunrise.isoformat(),
            "sunset": sunset.isoformat(),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def brahma_muhurta(datetime_iso: str, latitude: float, longitude: float) -> dict[str, Any]:
    """
    Calculate Brahma Muhurta (best time for spiritual practices).

    Brahma Muhurta starts 96 minutes before sunrise and lasts 48 minutes.
    It is the ideal time for meditation, prayer, study, and spiritual practice.

    Args:
        datetime_iso: Date in ISO format
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        Start and end times of Brahma Muhurta

    Example:
        brahma_muhurta("2026-02-04T12:00:00+05:30", 16.726, 81.288)
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)

        sr_data = get_sunrise_sunset(dt, latitude, longitude)
        sunrise = sr_data["sunrise"]
        if sunrise.tzinfo:
            sunrise = sunrise.replace(tzinfo=None)

        start, end = get_brahma_muhurta(sunrise)

        return {
            "datetime": datetime_iso,
            "location": {"latitude": latitude, "longitude": longitude},
            "brahma_start": start.isoformat(),
            "brahma_end": end.isoformat(),
            "duration_minutes": 48,
            "sunrise": sunrise.isoformat(),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def eclipse_periods(year: int, month: int) -> dict[str, Any]:
    """
    Check for solar and lunar eclipses in a given month.

    Eclipses are universally inauspicious for muhurta purposes.
    No important activities should be initiated during eclipse periods.

    Args:
        year: Calendar year (e.g., 2026)
        month: Calendar month (1-12)

    Returns:
        List of eclipse events with type, start/end times, and description

    Example:
        eclipse_periods(2026, 3)
    """
    try:
        eclipses = get_eclipse_periods(year, month)

        formatted = []
        for eclipse in eclipses:
            formatted.append(
                {
                    "type": eclipse["type"],
                    "start": eclipse["start"].isoformat()
                    if hasattr(eclipse["start"], "isoformat")
                    else str(eclipse["start"]),
                    "maximum": eclipse["maximum"].isoformat()
                    if hasattr(eclipse["maximum"], "isoformat")
                    else str(eclipse["maximum"]),
                    "end": eclipse["end"].isoformat()
                    if hasattr(eclipse["end"], "isoformat")
                    else str(eclipse["end"]),
                    "description": eclipse.get("description", ""),
                }
            )

        return {
            "year": year,
            "month": month,
            "eclipse_count": len(formatted),
            "eclipses": formatted,
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def marana_kaal(weekday: int) -> dict[str, Any]:
    """
    Get Marana Kaal (death-like inauspicious periods) for a weekday.

    These are extremely inauspicious time windows for each day of the week.
    No important activities should be initiated during these periods.

    Args:
        weekday: Day of week (0=Monday, 1=Tuesday, ..., 6=Sunday)

    Returns:
        List of inauspicious time windows in HH:MM format

    Example:
        marana_kaal(0)  # Monday
    """
    try:
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        periods = get_marana_kaal(weekday)

        return {
            "weekday": weekday,
            "day_name": day_names[weekday],
            "periods": [{"start": p[0], "end": p[1]} for p in periods],
            "count": len(periods),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def ashtottari_dasha(
    moon_nakshatra: int,
    degree_in_nakshatra: float,
    birth_datetime: str,
    rahu_house: int = 0,
    lagna_lord_house: int = 0,
    query_datetime: str | None = None,
) -> dict[str, Any]:
    """
    Calculate Ashtottari Dasha (108-year planetary period system).

    Ashtottari uses 8 planets (Sun, Moon, Mars, Mercury, Saturn, Jupiter, Venus, Rahu)
    in a 108-year cycle. It is applicable when Rahu is in kendra/trikona from Lagna lord.

    Args:
        moon_nakshatra: Moon's nakshatra number (1-27)
        degree_in_nakshatra: Degrees traversed in nakshatra (0 to ~13.333)
        birth_datetime: Birth datetime in ISO format
        rahu_house: House number of Rahu (1-12), 0 to skip applicability check
        lagna_lord_house: House number of Lagna lord (1-12), 0 to skip
        query_datetime: Query datetime (ISO format, defaults to now)

    Returns:
        Applicability status, current Mahadasha/Antardasha, and full sequence

    Example:
        ashtottari_dasha(25, 10.0, "1992-12-03T03:00:00+05:30", 7, 1)
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        query_dt = None
        if query_datetime:
            query_dt = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            if query_dt.tzinfo:
                query_dt = query_dt.replace(tzinfo=None)

        # Check applicability
        applicable = True
        if rahu_house > 0 and lagna_lord_house > 0:
            applicable = is_ashtottari_applicable(rahu_house, lagna_lord_house)

        # Get current dasha
        current = get_current_ashtottari(birth_dt, moon_nakshatra, degree_in_nakshatra, query_dt)

        # Get full sequence
        periods = calculate_ashtottari_sequence(birth_dt, moon_nakshatra, degree_in_nakshatra)

        return {
            "system": "ashtottari",
            "applicable": applicable,
            "birth_datetime": birth_datetime,
            "current": {
                "mahadasha": {
                    "lord": current["mahadasha"]["lord"],
                    "start_date": current["mahadasha"]["start_date"].isoformat(),
                    "end_date": current["mahadasha"]["end_date"].isoformat(),
                    "years": current["mahadasha"]["years"],
                },
                "antardasha": {
                    "lord": current["antardasha"]["lord"],
                    "start_date": current["antardasha"]["start_date"].isoformat(),
                    "end_date": current["antardasha"]["end_date"].isoformat(),
                },
                "remaining_days_maha": current["remaining_days_maha"],
                "remaining_days_antar": current["remaining_days_antar"],
            },
            "full_sequence": [
                {
                    "lord": p["lord"],
                    "start_date": p["start_date"].isoformat(),
                    "end_date": p["end_date"].isoformat(),
                    "years": round(p["years"], 2),
                }
                for p in periods
            ],
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def secondary_progressions(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    query_datetime: str | None = None,
) -> dict[str, Any]:
    """
    Calculate Secondary Progressions (day-for-a-year technique).

    Secondary Progressions show how the birth chart evolves over time.
    Each day after birth represents one year of life. Active progressed-to-natal
    aspects indicate current life themes.

    Args:
        birth_datetime: Birth datetime in ISO format
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        query_datetime: Query datetime (ISO format, defaults to now)

    Returns:
        Progressed positions, active aspects to natal chart, and current age

    Example:
        secondary_progressions("1992-12-03T03:00:00+05:30", 16.726, 81.288)
    """
    try:
        birth_dt = datetime.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)

        query_dt = None
        if query_datetime:
            query_dt = datetime.fromisoformat(query_datetime.replace("Z", "+00:00"))
            if query_dt.tzinfo:
                query_dt = query_dt.replace(tzinfo=None)

        result = get_current_progressions(birth_dt, birth_lat, birth_lon, query_dt)

        return {
            "system": "secondary_progressions",
            "birth_datetime": birth_datetime,
            "query_datetime": query_datetime or datetime.now().isoformat(),
            "age_years": result.get("age"),
            "progressed_positions": result.get("progressed_positions", {}),
            "natal_positions": result.get("natal_positions", {}),
            "active_aspects": result.get("active_aspects", []),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


def _get_dasha_interpretation(maha_lord: str, antar_lord: str) -> dict[str, Any]:
    """Get detailed interpretation for dasha combination from JSON knowledge base.

    Returns structured effects data for all 81 MD-AD combinations.
    """
    effects = get_antardasha_effect(maha_lord, antar_lord)

    if effects:
        return {
            "summary": effects.get("general_effects", [])[:2],  # Brief summary
            "general": effects.get("general_effects", []),
            "positive": effects.get("positive", []),
            "negative": effects.get("negative", []),
            "health": effects.get("health"),
            "career": effects.get("career"),
            "relationships": effects.get("relationships"),
            "finances": effects.get("finances"),
            "spiritual": effects.get("spiritual"),
        }

    # Fallback for missing data
    return {
        "summary": [f"{maha_lord.capitalize()}-{antar_lord.capitalize()} dasha period"],
        "general": [f"Combined influences of {maha_lord} and {antar_lord}"],
        "positive": [],
        "negative": [],
        "health": None,
        "career": None,
        "relationships": None,
        "finances": None,
        "spiritual": None,
    }


def _get_sade_sati_description(phase: str) -> str:
    """Get description for Sade Sati phase."""
    descriptions = {
        "rising": "Saturn in 12th from Moon - Beginning phase, mental stress and sleep disturbances",
        "peak": "Saturn over Moon - Most intense phase, tests character and inner strength",
        "setting": "Saturn in 2nd from Moon - Final phase, financial and family concerns",
    }
    return descriptions.get(phase.lower(), "Unknown Sade Sati phase")


def _get_sade_sati_effects(phase: str) -> list[str]:
    """Get effects for Sade Sati phase."""
    effects = {
        "rising": [
            "Mental anxiety and depression",
            "Sleep disturbances and nightmares",
            "Hidden enemies become active",
            "Losses and setbacks",
            "Spiritual awakening begins",
        ],
        "peak": [
            "Health issues and immunity problems",
            "Career challenges and job losses",
            "Relationship tests and separations",
            "Financial pressures",
            "Character building experiences",
            "Inner strength development",
        ],
        "setting": [
            "Financial burdens and expenses",
            "Family responsibilities increase",
            "Speech problems and communication issues",
            "Losses continue but diminish",
            "Lessons consolidate",
            "Transformation completes",
        ],
    }
    return effects.get(phase.lower(), ["Sade Sati effects vary by individual karma"])


def _assess_transits(planets: dict, sade_sati: dict, dhaiya: dict) -> str:
    """Provide overall transit assessment."""
    if sade_sati.get("active"):
        if sade_sati.get("phase") == "peak":
            return "challenging_peak"
        else:
            return "challenging"
    elif dhaiya.get("active"):
        return "moderately_challenging"
    else:
        favorable_count = sum(1 for p in planets.values() if p.get("is_favorable"))
        if favorable_count >= 3:
            return "very_favorable"
        elif favorable_count >= 1:
            return "generally_favorable"
        else:
            return "mixed"


def _calculate_house_distance(moon_idx: int, saturn_idx: int) -> int:
    """Calculate house distance between two sign indices."""
    distance = (saturn_idx - moon_idx) % 12
    return distance if distance > 0 else 12


def _years_until_sade_sati(moon_idx: int, saturn_idx: int) -> float | None:
    """
    Estimate years until Sade Sati begins.
    Returns None if Sade Sati is already active or just ended.
    Saturn takes about 2.5 years per sign.
    """
    distance = _calculate_house_distance(moon_idx, saturn_idx)

    if distance == 12 or distance == 1:
        return None  # Sade Sati active or just ending

    if distance <= 11:
        # Years until Saturn reaches 12th house from Moon
        years_per_sign = 2.5
        years_until = (12 - distance) * years_per_sign
        return round(years_until, 1)

    return None


if __name__ == "__main__":
    mcp.run()
