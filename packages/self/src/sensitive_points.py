"""
Sensitive Points (Sphutas) — Classical Jyotish sensitive degrees.

Three key points:
1. Bhrigu Bindu — Rahu-Moon midpoint. Most sensitive timing degree.
   Any transit over this point = major life event. (Brighu Nadi tradition)
2. Indu Lagna — Wealth sensitive point from BPHS Ch.35.
   Shows when and through what channel wealth flows.
3. Sree Lagna — Prosperity indicator (Moon + Venus).
   The degree of abundance and material fulfillment.
"""

from __future__ import annotations

from typing import Any

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

SIGN_TO_INDEX = {s.lower(): i for i, s in enumerate(SIGNS)}

SIGN_LORDS = {
    "Aries": "mars",
    "Taurus": "venus",
    "Gemini": "mercury",
    "Cancer": "moon",
    "Leo": "sun",
    "Virgo": "mercury",
    "Libra": "venus",
    "Scorpio": "mars",
    "Sagittarius": "jupiter",
    "Capricorn": "saturn",
    "Aquarius": "saturn",
    "Pisces": "jupiter",
}

# Indu Lagna Bindu values — fixed table from BPHS Ch.35
# Each planet contributes a fixed strength value
INDU_BINDUS = {
    "sun": 30,
    "moon": 16,
    "mars": 6,
    "mercury": 8,
    "jupiter": 10,
    "venus": 12,
    "saturn": 1,
    "rahu": 0,
    "ketu": 0,
}


def _normalize(longitude: float) -> float:
    return longitude % 360.0


def _sign_and_degree(longitude: float) -> tuple[str, float]:
    lon = _normalize(longitude)
    sign_idx = int(lon / 30)
    degree = lon % 30
    return SIGNS[sign_idx], degree


def calculate_bhrigu_bindu(
    rahu_longitude: float,
    moon_longitude: float,
) -> dict[str, Any]:
    """
    Calculate Bhrigu Bindu — the Rahu-Moon midpoint.

    This is the most sensitive timing degree in the chart.
    Any planet transiting within 1° of this point = major life event.
    Any natal planet conjunct this point = that planet's themes are fated/karmic.

    Args:
        rahu_longitude: Rahu's sidereal longitude (0-360°)
        moon_longitude: Moon's sidereal longitude (0-360°)

    Returns:
        Dict with longitude, sign, degree_in_sign, and interpretation
    """
    rahu = _normalize(rahu_longitude)
    moon = _normalize(moon_longitude)

    # Find the shorter arc midpoint
    diff = abs(moon - rahu)
    midpoint = _normalize(rahu + moon + 360) / 2 % 360 if diff > 180 else (rahu + moon) / 2

    midpoint = _normalize(midpoint)
    sign, degree = _sign_and_degree(midpoint)

    return {
        "longitude": round(midpoint, 4),
        "sign": sign,
        "degree_in_sign": round(degree, 4),
        "sign_lord": SIGN_LORDS[sign],
        "house_significance": f"Natal house of {sign} = primary life area activated by transits over this point",
        "orb_for_activation": 1.0,
        "method": "Midpoint of Rahu and Moon (shorter arc)",
        "source": "Brighu Nadi tradition",
    }


def calculate_indu_lagna(
    natal_planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
) -> dict[str, Any]:
    """
    Calculate Indu Lagna — the wealth sensitive point from BPHS Ch.35.

    Method:
    1. Find Jupiter's house from lagna → get that house lord → note its Bindu value
    2. Find Moon's house from lagna → get that house lord → note its Bindu value
    3. Sum both Bindus → count that many signs from lagna
    4. The resulting sign = Indu Lagna

    Args:
        natal_planets: {planet: {longitude, rashi, house, ...}}
        lagna_rashi: Ascendant sign (e.g. "libra")

    Returns:
        Dict with Indu Lagna sign, lord, bindu sum, and wealth interpretation
    """
    lagna_idx = SIGN_TO_INDEX.get(lagna_rashi.lower(), 0)

    def _get_house_from_lagna(planet_rashi: str) -> int:
        planet_idx = SIGN_TO_INDEX.get(planet_rashi.lower(), 0)
        return ((planet_idx - lagna_idx) % 12) + 1

    # Get Jupiter's data
    jupiter_data = natal_planets.get("jupiter", {})
    jupiter_rashi = (
        jupiter_data.get("rashi", "")
        or _sign_and_degree(float(jupiter_data.get("longitude", 0)))[0]
    )
    jupiter_house = _get_house_from_lagna(jupiter_rashi)

    # House lord of Jupiter's house
    jupiter_house_sign = SIGNS[(lagna_idx + jupiter_house - 1) % 12]
    jupiter_house_lord = SIGN_LORDS[jupiter_house_sign]
    jupiter_bindu = INDU_BINDUS.get(jupiter_house_lord, 0)

    # Get Moon's data
    moon_data = natal_planets.get("moon", {})
    moon_rashi = (
        moon_data.get("rashi", "") or _sign_and_degree(float(moon_data.get("longitude", 0)))[0]
    )
    moon_house = _get_house_from_lagna(moon_rashi)

    # House lord of Moon's house
    moon_house_sign = SIGNS[(lagna_idx + moon_house - 1) % 12]
    moon_house_lord = SIGN_LORDS[moon_house_sign]
    moon_bindu = INDU_BINDUS.get(moon_house_lord, 0)

    # Sum and count from lagna
    total_bindus = jupiter_bindu + moon_bindu
    # Count (total_bindus) signs from lagna (1-based, so subtract 1)
    indu_lagna_idx = (lagna_idx + total_bindus - 1) % 12
    indu_lagna_sign = SIGNS[indu_lagna_idx]
    indu_lagna_lord = SIGN_LORDS[indu_lagna_sign]

    return {
        "indu_lagna_sign": indu_lagna_sign,
        "indu_lagna_lord": indu_lagna_lord,
        "bindu_sum": total_bindus,
        "calculation": {
            "jupiter_house": jupiter_house,
            "jupiter_house_lord": jupiter_house_lord,
            "jupiter_bindu": jupiter_bindu,
            "moon_house": moon_house,
            "moon_house_lord": moon_house_lord,
            "moon_bindu": moon_bindu,
        },
        "wealth_channel": f"Wealth flows through {indu_lagna_lord}'s significations ({indu_lagna_sign} themes)",
        "source": "BPHS Chapter 35 — Indu Lagna",
        "method": "Jupiter house lord bindu + Moon house lord bindu, counted from lagna",
    }


def calculate_sree_lagna(
    moon_longitude: float,
    venus_longitude: float,
    lagna_longitude: float | None = None,
) -> dict[str, Any]:
    """
    Calculate Sree Lagna — the prosperity sensitive point.

    Method: (Moon longitude + Venus longitude) % 360
    This gives the degree of material abundance and fulfillment.

    Args:
        moon_longitude: Moon's sidereal longitude
        venus_longitude: Venus's sidereal longitude
        lagna_longitude: Ascendant longitude (optional, for house calculation)

    Returns:
        Dict with Sree Lagna longitude, sign, degree, and interpretation
    """
    moon = _normalize(moon_longitude)
    venus = _normalize(venus_longitude)
    sree = _normalize(moon + venus)

    sign, degree = _sign_and_degree(sree)
    sree_lord = SIGN_LORDS[sign]

    result: dict[str, Any] = {
        "longitude": round(sree, 4),
        "sign": sign,
        "degree_in_sign": round(degree, 4),
        "sign_lord": sree_lord,
        "prosperity_channel": f"Prosperity manifests through {sree_lord} ({sign} themes)",
        "source": "Jyotish tradition — Moon + Venus conjunction point",
        "method": "(Moon longitude + Venus longitude) mod 360",
    }

    if lagna_longitude is not None:
        lagna_sign_idx = int(_normalize(lagna_longitude) / 30)
        sree_sign_idx = SIGN_TO_INDEX[sign.lower()]
        house = ((sree_sign_idx - lagna_sign_idx) % 12) + 1
        result["house_from_lagna"] = house

    return result


def get_all_sensitive_points(
    natal_planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    lagna_longitude: float | None = None,
) -> dict[str, Any]:
    """
    Calculate all three sensitive points for a birth chart.

    Args:
        natal_planets: {planet: {longitude, rashi, house}}
        lagna_rashi: Ascendant sign
        lagna_longitude: Ascendant longitude (optional)

    Returns:
        Complete sensitive points analysis
    """
    rahu_lon = float(natal_planets.get("rahu", {}).get("longitude", 0))
    moon_lon = float(natal_planets.get("moon", {}).get("longitude", 0))
    venus_lon = float(natal_planets.get("venus", {}).get("longitude", 0))

    bb = calculate_bhrigu_bindu(rahu_lon, moon_lon)
    il = calculate_indu_lagna(natal_planets, lagna_rashi)
    sl = calculate_sree_lagna(moon_lon, venus_lon, lagna_longitude)

    # Find natal planets conjunct Bhrigu Bindu (within 3°)
    bb_lon = bb["longitude"]
    natal_conjunctions = []
    for planet, data in natal_planets.items():
        p_lon = float(data.get("longitude", 0))
        diff = abs(p_lon - bb_lon) % 360
        if diff > 180:
            diff = 360 - diff
        if diff <= 3.0:
            natal_conjunctions.append(
                {
                    "planet": planet,
                    "orb": round(diff, 2),
                    "significance": f"Natal {planet} conjunct Bhrigu Bindu — {planet} themes are karmically fated and activated by transits over {bb['sign']} {round(bb['degree_in_sign'], 1)}°",
                }
            )

    return {
        "success": True,
        "bhrigu_bindu": bb,
        "indu_lagna": il,
        "sree_lagna": sl,
        "natal_conjunctions_with_bb": natal_conjunctions,
        "summary": {
            "bhrigu_bindu": f"{bb['sign']} {round(bb['degree_in_sign'], 2)}° — watch transits here for major events",
            "indu_lagna": f"{il['indu_lagna_sign']} — wealth channel through {il['indu_lagna_lord']}",
            "sree_lagna": f"{sl['sign']} {round(sl['degree_in_sign'], 2)}° — prosperity through {sl['sign_lord']}",
        },
    }
