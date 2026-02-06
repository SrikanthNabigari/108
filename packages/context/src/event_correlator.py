"""Event Correlation Engine for 108 Vedic Astrology.

Allows users to input past life events with dates and correlates them
with the dasha periods and transit configurations active at that time.
This validates chart accuracy and builds a historical pattern.

Example flow:
1. User says "I got promoted on March 15, 2020"
2. System finds: Mercury MD / Venus AD, Jupiter transiting 10th house
3. System explains: "Mercury as 10th lord in his own dasha + Jupiter blessing
   the career house = classic promotion combination"
"""

from datetime import datetime
from typing import Any

from packages.context.src.dasha import get_current_dasha
from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day
from packages.cosmos.src.houses import SIGN_RULERS

# House significations for event type matching
EVENT_TYPE_HOUSES: dict[str, list[int]] = {
    "career": [10, 6, 2, 11],
    "marriage": [7, 2, 5, 11],
    "health": [1, 6, 8, 12],
    "money": [2, 11, 5, 9],
    "education": [4, 5, 9, 2],
    "travel": [3, 9, 12, 7],
    "loss": [8, 12, 6, 2],
    "children": [5, 9, 2, 11],
    "property": [4, 2, 11, 10],
    "spiritual": [9, 12, 5, 8],
}

# Planets naturally associated with event types
EVENT_TYPE_PLANETS: dict[str, list[str]] = {
    "career": ["sun", "saturn", "mercury", "jupiter"],
    "marriage": ["venus", "jupiter", "moon", "mars"],
    "health": ["sun", "mars", "saturn", "moon"],
    "money": ["jupiter", "venus", "mercury", "moon"],
    "education": ["mercury", "jupiter", "moon", "venus"],
    "travel": ["moon", "rahu", "mercury", "venus"],
    "loss": ["saturn", "rahu", "ketu", "mars"],
    "children": ["jupiter", "venus", "moon", "mercury"],
    "property": ["mars", "venus", "saturn", "moon"],
    "spiritual": ["ketu", "jupiter", "saturn", "moon"],
}

# Rashi lords (reuse from houses.py)
RASHI_LORDS = SIGN_RULERS

# Inverted: planet -> owned signs
_PLANET_OWNED_SIGNS: dict[str, list[int]] = {}
for _rashi, _lord in RASHI_LORDS.items():
    _PLANET_OWNED_SIGNS.setdefault(_lord, []).append(_rashi)


def _get_house_from_lagna(rashi: int, lagna_rashi: int) -> int:
    """Get house number (1-12) from rashi relative to lagna."""
    return ((rashi - lagna_rashi) % 12) + 1


def _get_houses_owned_from_lagna(planet: str, lagna_rashi: int) -> list[int]:
    """Get the houses (1-12) a planet lords from the given lagna."""
    owned = _PLANET_OWNED_SIGNS.get(planet.lower(), [])
    return [_get_house_from_lagna(s, lagna_rashi) for s in owned]


def _rashi_name_to_idx(name: str) -> int:
    """Convert rashi name to index 0-11."""
    names = [
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
    lower = name.lower()
    return names.index(lower) if lower in names else 0


def correlate_event(
    event_date: str | datetime,
    event_type: str,
    event_description: str,
    birth_datetime: str | datetime,
    natal_planets: dict[str, dict[str, Any]],
    moon_longitude: float,
    lagna_rashi: str | int,
    latitude: float = 0.0,  # noqa: ARG001
    longitude: float = 0.0,  # noqa: ARG001
) -> dict[str, Any]:
    """Correlate a single life event with dasha and transit data.

    Args:
        event_date: Date of the event (ISO string or datetime)
        event_type: Type of event (career, marriage, health, money, education, travel, loss)
        event_description: User's description of the event
        birth_datetime: Birth date and time (ISO string or datetime)
        natal_planets: Birth chart positions {planet: {longitude, rashi, ...}}
        moon_longitude: Moon longitude at birth (for dasha calculation)
        lagna_rashi: Ascendant sign (0-11 or name)
        latitude: Geographic latitude (reserved for location-specific analysis)
        longitude: Geographic longitude (reserved for location-specific analysis)

    Returns:
        Dictionary with event details, dasha_at_event, transit_at_event,
        correlation_score, and explanation.
    """
    # Parse dates
    event_dt = datetime.fromisoformat(event_date) if isinstance(event_date, str) else event_date

    if isinstance(birth_datetime, str):
        birth_dt = datetime.fromisoformat(birth_datetime)
    else:
        birth_dt = birth_datetime

    # Ensure both are timezone-naive or both have timezone for comparison
    if event_dt.tzinfo is not None and birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=event_dt.tzinfo)
    elif event_dt.tzinfo is None and birth_dt.tzinfo is not None:
        event_dt = event_dt.replace(tzinfo=birth_dt.tzinfo)

    # Normalize lagna
    if isinstance(lagna_rashi, str):
        lagna_idx = _rashi_name_to_idx(lagna_rashi)
    else:
        lagna_idx = int(lagna_rashi)

    event_type_lower = event_type.lower()

    # 1. Get dasha at event time
    dasha_at_event = get_current_dasha(birth_dt, moon_longitude, event_dt)

    dasha_info = {}
    dasha_explanation_parts = []
    dasha_score = 0.0

    if dasha_at_event:
        md_lord = dasha_at_event["mahadasha"]["lord"]
        ad_lord = dasha_at_event["antardasha"]["lord"]
        pd_lord = dasha_at_event.get("pratyantardasha", {})
        pd_lord_name = pd_lord.get("lord", "") if pd_lord else ""

        dasha_info = {
            "mahadasha": md_lord,
            "antardasha": ad_lord,
            "pratyantardasha": pd_lord_name,
        }

        # Score dasha relevance to event type
        relevant_houses = EVENT_TYPE_HOUSES.get(event_type_lower, [])
        relevant_planets = EVENT_TYPE_PLANETS.get(event_type_lower, [])

        for lord, weight, label in [
            (md_lord, 0.5, "Mahadasha"),
            (ad_lord, 0.3, "Antardasha"),
            (pd_lord_name, 0.2, "Pratyantardasha"),
        ]:
            if not lord:
                continue
            owned_houses = _get_houses_owned_from_lagna(lord, lagna_idx)
            house_match = any(h in relevant_houses for h in owned_houses)
            planet_match = lord in relevant_planets

            if house_match:
                dasha_score += weight * 0.6
                matched_houses = [h for h in owned_houses if h in relevant_houses]
                dasha_explanation_parts.append(
                    f"{lord.title()} {label} lords house(s) {matched_houses} relevant to {event_type_lower}"
                )
            if planet_match:
                dasha_score += weight * 0.4
                dasha_explanation_parts.append(
                    f"{lord.title()} is a natural significator for {event_type_lower}"
                )

    # 2. Get transits at event time
    transit_info = {}
    transit_score = 0.0
    transit_explanation_parts = []

    try:
        jd = get_julian_day(event_dt)
        transit_raw = get_all_planets(jd)

        for planet, data in transit_raw.items():
            lon = data["longitude"]
            rashi = int(lon // 30)
            house = _get_house_from_lagna(rashi, lagna_idx)
            transit_info[planet] = {
                "longitude": round(lon, 2),
                "rashi": rashi,
                "house": house,
            }

            # Score transit relevance
            relevant_houses = EVENT_TYPE_HOUSES.get(event_type_lower, [])
            relevant_planets = EVENT_TYPE_PLANETS.get(event_type_lower, [])

            if house in relevant_houses:
                # Weight by planet importance
                planet_weight = 0.15 if planet in ("saturn", "jupiter", "rahu") else 0.08
                transit_score += planet_weight
                transit_explanation_parts.append(
                    f"Transit {planet.title()} in house {house} ({event_type_lower}-related)"
                )

            if planet in relevant_planets and house in relevant_houses[:2]:
                transit_score += 0.1
    except Exception:
        pass

    # 3. Check for yogas active (dasha lord + transit lord interaction)
    yoga_score = 0.0
    yogas_active = []

    if dasha_at_event and transit_info:
        md_lord = dasha_at_event["mahadasha"]["lord"]
        ad_lord = dasha_at_event["antardasha"]["lord"]

        for lord in [md_lord, ad_lord]:
            natal_data = natal_planets.get(lord, {})
            natal_lon = natal_data.get("longitude", 0)
            natal_rashi = int(natal_lon // 30)

            # Check if any transit planet conjuncts natal dasha lord
            for t_planet, t_info in transit_info.items():
                if t_info["rashi"] == natal_rashi:
                    yoga_score += 0.15
                    yogas_active.append(
                        f"Transit {t_planet.title()} conjunct natal {lord.title()} (dasha lord activation)"
                    )

    # 4. Combined correlation score (0-100)
    raw_score = (dasha_score * 40) + (transit_score * 40) + (yoga_score * 20)
    correlation_score = min(int(raw_score * 100 / max(raw_score, 1) if raw_score > 0 else 0), 100)
    # Normalize to a reasonable range
    correlation_score = min(int((dasha_score + transit_score + yoga_score) * 80), 100)

    # 5. Build explanation
    all_explanations = dasha_explanation_parts + transit_explanation_parts + yogas_active
    explanation = (
        ". ".join(all_explanations[:5]) if all_explanations else "No strong correlations found"
    )

    return {
        "event": event_description,
        "event_type": event_type_lower,
        "date": event_dt.strftime("%Y-%m-%d"),
        "dasha_at_event": dasha_info,
        "dasha_explanation": ". ".join(dasha_explanation_parts)
        if dasha_explanation_parts
        else "No strong dasha correlation",
        "transit_at_event": transit_info,
        "transit_explanation": ". ".join(transit_explanation_parts)
        if transit_explanation_parts
        else "No strong transit correlation",
        "yogas_active": yogas_active,
        "correlation_score": correlation_score,
        "explanation": explanation,
    }


def batch_correlate(
    events: list[dict[str, Any]],
    birth_data: dict[str, Any],
) -> dict[str, Any]:
    """Correlate multiple life events and return chart accuracy score.

    Args:
        events: List of event dicts, each with: date, type, description
        birth_data: Dictionary with: birth_datetime, natal_planets, moon_longitude,
                   lagna_rashi, latitude, longitude

    Returns:
        Dictionary with individual correlations and overall chart_accuracy_score.
    """
    results = []
    total_score = 0

    for event in events:
        try:
            result = correlate_event(
                event_date=event["date"],
                event_type=event.get("type", "career"),
                event_description=event.get("description", ""),
                birth_datetime=birth_data["birth_datetime"],
                natal_planets=birth_data["natal_planets"],
                moon_longitude=birth_data["moon_longitude"],
                lagna_rashi=birth_data["lagna_rashi"],
                latitude=birth_data.get("latitude", 0.0),
                longitude=birth_data.get("longitude", 0.0),
            )
            results.append(result)
            total_score += result["correlation_score"]
        except Exception as e:
            results.append(
                {
                    "event": event.get("description", ""),
                    "date": event.get("date", ""),
                    "error": str(e),
                    "correlation_score": 0,
                }
            )

    avg_score = total_score // max(len(results), 1)

    return {
        "events": results,
        "total_events": len(events),
        "average_correlation": avg_score,
        "chart_accuracy_score": avg_score,
        "accuracy_label": _accuracy_label(avg_score),
    }


def _accuracy_label(score: int) -> str:
    """Convert score to human-readable accuracy label."""
    if score >= 75:
        return "high"
    elif score >= 50:
        return "moderate"
    elif score >= 25:
        return "low"
    else:
        return "inconclusive"
