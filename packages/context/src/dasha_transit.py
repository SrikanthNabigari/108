"""Dasha-Transit Cross-Analysis Engine for 108 Vedic Astrology.

Connects WHAT (yogas/patterns) to WHEN (dasha periods) to NOW (current transits).
This is the core timing engine that determines when dasha lords get activated
by transit planets, producing actionable timing insights.

Key concepts:
- Dasha lords rule certain houses from the lagna
- When transit planets activate those houses or conjoin/aspect dasha lords,
  the dasha themes intensify
- Activation strength is scored 0-100
"""

from datetime import datetime, timedelta
from typing import Any

from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day
from packages.cosmos.src.houses import SIGN_RULERS

# Rashi lords (same as houses.py SIGN_RULERS, 0=Aries..11=Pisces)
RASHI_LORDS = SIGN_RULERS

# Which houses each planet rules (inverted from RASHI_LORDS)
_PLANET_OWNED_SIGNS: dict[str, list[int]] = {}
for _rashi, _lord in RASHI_LORDS.items():
    _PLANET_OWNED_SIGNS.setdefault(_lord, []).append(_rashi)

# House significations for theme generation
HOUSE_THEMES: dict[int, str] = {
    1: "self, health, personality",
    2: "wealth, family, speech",
    3: "courage, siblings, communication",
    4: "home, mother, happiness",
    5: "children, intelligence, creativity",
    6: "enemies, disease, service",
    7: "marriage, partnership, business",
    8: "transformation, longevity, occult",
    9: "fortune, dharma, higher learning",
    10: "career, status, authority",
    11: "gains, friends, aspirations",
    12: "losses, spirituality, foreign lands",
}

# Period quality mapping based on house activation
_QUALITY_MAP = {
    1: "growth",
    2: "wealth",
    3: "effort",
    4: "comfort",
    5: "creativity",
    6: "challenge",
    7: "relationships",
    8: "transformation",
    9: "fortune",
    10: "career",
    11: "gains",
    12: "spiritual",
}


def _get_house_from_lagna(planet_rashi: int, lagna_rashi: int) -> int:
    """Get house number (1-12) of a planet relative to lagna."""
    return ((planet_rashi - lagna_rashi) % 12) + 1


def _get_rashi_from_longitude(longitude: float) -> int:
    """Get rashi index (0-11) from longitude."""
    return int(longitude % 360) // 30


def _get_houses_owned_from_lagna(planet: str, lagna_rashi: int) -> list[int]:
    """Get the house numbers (1-12) that a planet lords over from the given lagna."""
    owned_signs = _PLANET_OWNED_SIGNS.get(planet.lower(), [])
    return [_get_house_from_lagna(sign, lagna_rashi) for sign in owned_signs]


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _score_transit_activation(
    transit_planet: str,
    transit_rashi: int,
    dasha_lord: str,
    natal_lord_rashi: int,
    _lagna_rashi: int,
) -> float:
    """Score how strongly a transit planet activates a dasha lord (0-1).

    Activation occurs when:
    1. Transit planet is in a sign owned by the dasha lord (0.3)
    2. Transit planet conjuncts natal position of dasha lord (0.4)
    3. Transit planet aspects natal position of dasha lord (0.2)
    4. Transit planet is a slow mover (bonus 0.1)
    """
    score = 0.0

    # 1. Transit in sign owned by dasha lord
    owned_signs = _PLANET_OWNED_SIGNS.get(dasha_lord, [])
    if transit_rashi in owned_signs:
        score += 0.3

    # 2. Conjunction with natal dasha lord position
    if transit_rashi == natal_lord_rashi:
        score += 0.4

    # 3. Aspect check (7th house aspect universal, special aspects for Mars/Jup/Sat)
    house_dist = ((natal_lord_rashi - transit_rashi) % 12) or 12
    aspect_houses = {7}
    special = {
        "mars": {4, 8},
        "jupiter": {5, 9},
        "saturn": {3, 10},
        "rahu": {5, 9},
        "ketu": {5, 9},
    }
    aspect_houses |= special.get(transit_planet, set())
    if house_dist in aspect_houses:
        score += 0.2

    # 4. Slow-mover bonus
    slow_planets = {"saturn", "jupiter", "rahu", "ketu"}
    if transit_planet in slow_planets:
        score += 0.1

    return min(score, 1.0)


def cross_analyze(
    natal_planets: dict[str, dict[str, Any]],
    current_transits: dict[str, dict[str, Any]],
    current_dasha: dict[str, Any],
    lagna_rashi: str | int,
    moon_rashi: str | int,  # noqa: ARG001
) -> dict[str, Any]:
    """Cross-analyze dasha periods with current transits.

    Determines which life themes are currently activated by combining
    dasha lord significations with transit planet positions.

    Args:
        natal_planets: Birth chart planet positions {planet: {longitude, rashi, ...}}
        current_transits: Current transit positions {planet: {longitude, rashi, ...}}
        current_dasha: Current dasha info {mahadasha: str, antardasha: str, pratyantardasha: str}
        lagna_rashi: Ascendant sign (0-11 int or name string)
        moon_rashi: Moon sign (0-11 int or name string, reserved for future use)

    Returns:
        Dictionary with active_themes, strongest_house, most_active_planet,
        overall_period_quality, and score.
    """
    # Normalize rashi inputs
    if isinstance(lagna_rashi, str):
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
        lagna_idx = (
            rashi_names.index(lagna_rashi.lower()) if lagna_rashi.lower() in rashi_names else 0
        )
    else:
        lagna_idx = int(lagna_rashi)

    # moon_rashi kept in signature for API compatibility (used in future enhancements)

    # Extract dasha lords
    md_lord = current_dasha.get("mahadasha", "")
    ad_lord = current_dasha.get("antardasha", "")
    pd_lord = current_dasha.get("pratyantardasha", "")

    dasha_lords = [lord for lord in [md_lord, ad_lord, pd_lord] if lord]

    active_themes: list[dict[str, Any]] = []
    house_scores: dict[int, float] = dict.fromkeys(range(1, 13), 0.0)
    planet_scores: dict[str, float] = {}

    for dasha_lord in dasha_lords:
        # Get natal position of dasha lord
        natal_data = natal_planets.get(dasha_lord, {})
        natal_lon = natal_data.get("longitude", 0)
        natal_rashi = natal_data.get("rashi", _get_rashi_from_longitude(natal_lon))
        if isinstance(natal_rashi, str):
            natal_rashi = _get_rashi_from_longitude(natal_lon)

        # Houses owned by this dasha lord from lagna
        owned_houses = _get_houses_owned_from_lagna(dasha_lord, lagna_idx)

        # Dasha level weight: MD=1.0, AD=0.6, PD=0.3
        if dasha_lord == md_lord:
            level_weight = 1.0
            level_label = "Mahadasha"
        elif dasha_lord == ad_lord:
            level_weight = 0.6
            level_label = "Antardasha"
        else:
            level_weight = 0.3
            level_label = "Pratyantardasha"

        # Check each transit planet for activation
        for t_planet, t_data in current_transits.items():
            t_lon = t_data.get("longitude", 0)
            t_rashi = t_data.get("rashi", _get_rashi_from_longitude(t_lon))
            if isinstance(t_rashi, str):
                t_rashi = _get_rashi_from_longitude(t_lon)

            activation = _score_transit_activation(
                t_planet, t_rashi, dasha_lord, natal_rashi, lagna_idx
            )

            if activation > 0.1:
                weighted_score = activation * level_weight

                # Accumulate house scores
                for house in owned_houses:
                    house_scores[house] += weighted_score

                # Accumulate planet scores
                planet_scores[t_planet] = planet_scores.get(t_planet, 0) + weighted_score

                # Build theme description
                house_themes = [HOUSE_THEMES.get(h, "") for h in owned_houses]
                t_house = _get_house_from_lagna(t_rashi, lagna_idx)

                theme = {
                    "theme": f"{', '.join(house_themes)}",
                    "strength": round(weighted_score, 2),
                    "dasha_trigger": f"{dasha_lord.title()} {level_label} ({', '.join(str(h) for h in owned_houses)} lord) active",
                    "transit_trigger": f"Transit {t_planet.title()} in house {t_house}",
                    "houses_activated": owned_houses,
                    "transit_planet": t_planet,
                    "dasha_lord": dasha_lord,
                }
                active_themes.append(theme)

    # Sort themes by strength descending
    active_themes.sort(key=lambda x: x["strength"], reverse=True)

    # Determine strongest house
    strongest_house = max(house_scores, key=house_scores.get) if house_scores else 1

    # Most active planet
    most_active = max(planet_scores, key=planet_scores.get) if planet_scores else (md_lord or "sun")

    # Overall quality based on strongest house
    quality = _QUALITY_MAP.get(strongest_house, "mixed")

    # Overall score (0-100)
    total_activation = sum(house_scores.values())
    score = min(int(total_activation * 50), 100)

    return {
        "active_themes": active_themes[:10],  # Top 10
        "strongest_house": strongest_house,
        "most_active_planet": most_active,
        "overall_period_quality": quality,
        "score": score,
        "house_scores": {h: round(s, 2) for h, s in house_scores.items() if s > 0},
        "dasha_lords": dasha_lords,
    }


def find_activation_windows(
    natal_planets: dict[str, dict[str, Any]],
    current_dasha: dict[str, Any],
    start_date: str | datetime,
    end_date: str | datetime,
    lagna_rashi: str | int,
    latitude: float = 0.0,  # noqa: ARG001
    longitude: float = 0.0,  # noqa: ARG001
) -> list[dict[str, Any]]:
    """Find specific date windows when dasha lords get transit activation.

    Scans the date range at weekly intervals and identifies periods of
    elevated activation.

    Args:
        natal_planets: Birth chart planet positions
        current_dasha: Current dasha info {mahadasha, antardasha, pratyantardasha}
        start_date: Start of search window (ISO string or datetime)
        end_date: End of search window (ISO string or datetime)
        lagna_rashi: Ascendant sign (0-11 or name)
        latitude: Geographic latitude (reserved for location-specific transits)
        longitude: Geographic longitude (reserved for location-specific transits)

    Returns:
        List of activation windows with date, score, and description.
    """
    start_dt = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
    end_dt = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date

    # Normalize lagna
    if isinstance(lagna_rashi, str):
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
        lagna_idx = (
            rashi_names.index(lagna_rashi.lower()) if lagna_rashi.lower() in rashi_names else 0
        )
    else:
        lagna_idx = int(lagna_rashi)

    windows: list[dict[str, Any]] = []
    current_dt = start_dt
    step = timedelta(days=7)

    while current_dt <= end_dt:
        try:
            jd = get_julian_day(current_dt)
            transit_raw = get_all_planets(jd)

            # Convert raw positions to expected format
            transits = {}
            for planet, data in transit_raw.items():
                lon = data["longitude"]
                transits[planet] = {
                    "longitude": lon,
                    "rashi": int(lon // 30),
                }

            result = cross_analyze(natal_planets, transits, current_dasha, lagna_idx, 0)

            if result["score"] > 20:
                windows.append(
                    {
                        "date": current_dt.strftime("%Y-%m-%d"),
                        "score": result["score"],
                        "strongest_house": result["strongest_house"],
                        "quality": result["overall_period_quality"],
                        "active_count": len(result["active_themes"]),
                        "most_active_planet": result["most_active_planet"],
                    }
                )
        except Exception:
            pass

        current_dt += step

    # Merge consecutive windows into ranges
    merged = _merge_windows(windows)
    return merged


def _merge_windows(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge consecutive weekly windows into date ranges."""
    if not windows:
        return []

    merged: list[dict[str, Any]] = []
    current = windows[0].copy()
    current["start_date"] = current["date"]
    current["end_date"] = current["date"]
    peak_score = current["score"]

    for w in windows[1:]:
        # Check if consecutive (within 10 days)
        prev_date = datetime.strptime(current["end_date"], "%Y-%m-%d")
        curr_date = datetime.strptime(w["date"], "%Y-%m-%d")
        diff = (curr_date - prev_date).days

        if diff <= 10 and w["quality"] == current["quality"]:
            current["end_date"] = w["date"]
            if w["score"] > peak_score:
                peak_score = w["score"]
                current["score"] = peak_score
                current["strongest_house"] = w["strongest_house"]
                current["most_active_planet"] = w["most_active_planet"]
        else:
            current.pop("date", None)
            merged.append(current)
            current = w.copy()
            current["start_date"] = current["date"]
            current["end_date"] = current["date"]
            peak_score = current["score"]

    current.pop("date", None)
    merged.append(current)
    return merged
