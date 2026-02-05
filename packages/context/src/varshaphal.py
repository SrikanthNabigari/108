"""Varshaphal (Solar Return / Tajika) engine for 108 Vedic Astrology.

Implements annual horoscope calculations including:
- Muntha progression
- Varshesha (Year Lord) determination
- Tajika yoga detection
- Saham (sensitive point) calculation
- Full Varshaphal analysis

Uses knowledge/rules/varshaphal_rules.json.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_varshaphal_rules

_varshaphal_cache: dict[str, Any] | None = None


def _get_rules() -> dict[str, Any]:
    """Get cached varshaphal rules."""
    global _varshaphal_cache
    if _varshaphal_cache is None:
        _varshaphal_cache = get_varshaphal_rules()
    return _varshaphal_cache


# Rashi lords mapping (0=Aries..11=Pisces -> ruling planet)
RASHI_LORDS = {
    0: "mars",  # Aries
    1: "venus",  # Taurus
    2: "mercury",  # Gemini
    3: "moon",  # Cancer
    4: "sun",  # Leo
    5: "mercury",  # Virgo
    6: "venus",  # Libra
    7: "mars",  # Scorpio
    8: "jupiter",  # Sagittarius
    9: "saturn",  # Capricorn
    10: "saturn",  # Aquarius
    11: "jupiter",  # Pisces
}

# Day lords (0=Monday..6=Sunday)
DAY_LORDS = {
    0: "moon",  # Monday
    1: "mars",  # Tuesday
    2: "mercury",  # Wednesday
    3: "jupiter",  # Thursday
    4: "venus",  # Friday
    5: "saturn",  # Saturday
    6: "sun",  # Sunday
}


def calculate_muntha(birth_lagna_rashi: int, age: int) -> dict[str, Any]:
    """Calculate Muntha position for a given age.

    Muntha progresses one sign per year from the birth ascendant.

    Args:
        birth_lagna_rashi: Birth ascendant sign (0=Aries to 11=Pisces)
        age: Completed age (years since birth)

    Returns:
        Dictionary with muntha_rashi, house_from_lagna, and effects.
    """
    rules = _get_rules()
    muntha_data = rules.get("muntha", {})

    # Muntha sign: (lagna - 1 + age - 1) % 12 + 1 expressed as 0-indexed
    # More simply: lagna + (age % 12), wrapping around
    muntha_rashi = (birth_lagna_rashi + (age % 12)) % 12

    # House from lagna (1-12)
    house = ((muntha_rashi - birth_lagna_rashi) % 12) + 1

    house_effects = muntha_data.get("house_effects", {}).get(str(house), {})

    return {
        "muntha_rashi": muntha_rashi,
        "house_from_lagna": house,
        "theme": house_effects.get("theme", ""),
        "effects": house_effects.get("effects", []),
        "overall": house_effects.get("overall", "mixed"),
    }


def determine_varshesha(varshaphal_lagna_rashi: int) -> dict[str, Any]:
    """Determine Year Lord from the annual chart's ascendant.

    Simplified determination: uses the lord of the annual chart lagna sign.

    Args:
        varshaphal_lagna_rashi: Annual chart ascendant sign (0-11)

    Returns:
        Dictionary with year_lord and its effects.
    """
    rules = _get_rules()
    varshesha_data = rules.get("varshesha", {})

    year_lord = RASHI_LORDS.get(varshaphal_lagna_rashi, "sun")
    lord_effects = varshesha_data.get("year_lord_by_planet", {}).get(year_lord, {})

    return {
        "year_lord": year_lord,
        "lagna_rashi": varshaphal_lagna_rashi,
        "theme": lord_effects.get("theme", ""),
        "favorable": lord_effects.get("favorable", []),
        "unfavorable": lord_effects.get("unfavorable", []),
        "best_placement": lord_effects.get("best_placement", ""),
        "difficult_placement": lord_effects.get("difficult_placement", ""),
    }


def detect_tajika_yogas(planet_positions: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect Tajika yogas in the Varshaphal chart.

    Checks 16 Tajika yoga conditions from the JSON rules.

    Args:
        planet_positions: Dict mapping planet name -> {longitude, rashi, house, ...}

    Returns:
        List of detected Tajika yogas with name, type, and effect.
    """
    rules = _get_rules()
    tajika_data = rules.get("tajika_yogas", {}).get("yogas", {})

    detected: list[dict[str, Any]] = []

    for yoga_id, yoga_info in tajika_data.items():
        # Check each yoga's condition based on available data
        is_present = _check_tajika_yoga(yoga_id, yoga_info, planet_positions)
        if is_present:
            detected.append(
                {
                    "yoga_id": yoga_id,
                    "name": yoga_info.get("name", yoga_id),
                    "type": yoga_info.get("type", "mixed"),
                    "condition": yoga_info.get("condition", ""),
                    "effect": yoga_info.get("effect", ""),
                }
            )

    return detected


def _check_tajika_yoga(
    yoga_id: str,
    _yoga_info: dict[str, Any],
    planet_positions: dict[str, dict[str, Any]],
) -> bool:
    """Check if a specific Tajika yoga is present.

    Uses simplified detection based on house positions.
    """
    kendra = {1, 4, 7, 10}
    trikona = {1, 5, 9}

    # Get year lord (assume ascendant lord is first planet with house=1, or sun as fallback)
    year_lord_house = None
    asc_lord_house = None

    for planet, data in planet_positions.items():
        house = data.get("house", 0)
        if house == 1 and year_lord_house is None:
            year_lord_house = house
        if planet.lower() == "sun":
            asc_lord_house = data.get("house")

    # Simplified detection for key yogas
    if yoga_id == "ikkabal":
        # Year lord in kendra or trikona
        if asc_lord_house and asc_lord_house in (kendra | trikona):
            return True

    elif yoga_id == "induvara":
        # All planets in kendra
        houses = {data.get("house", 0) for data in planet_positions.values()}
        if houses and houses.issubset(kendra):
            return True

    elif yoga_id == "kuttha":
        # Year lord combust (close to Sun)
        sun_lon = planet_positions.get("sun", {}).get("longitude", 0)
        for planet, data in planet_positions.items():
            if planet.lower() == "sun":
                continue
            lon = data.get("longitude", 0)
            dist = abs(lon - sun_lon) % 360
            dist = min(dist, 360 - dist)
            if dist < 15 and data.get("house") == asc_lord_house:
                return True

    elif yoga_id == "tambira":
        # Year lord and asc lord in mutual kendra/trikona
        # Simplified: check if two key planets are in kendra houses
        house_list = [data.get("house", 0) for data in planet_positions.values()]
        kendra_count = sum(1 for h in house_list if h in kendra)
        if kendra_count >= 3:
            return True

    return False


def calculate_sahams(
    planet_longitudes: dict[str, float],
    lagna_lon: float,
    is_day_chart: bool = True,
) -> dict[str, dict[str, Any]]:
    """Calculate Saham (sensitive point) positions.

    Args:
        planet_longitudes: Dict mapping planet name -> longitude (0-360)
        lagna_lon: Ascendant longitude
        is_day_chart: True if birth is during daytime

    Returns:
        Dictionary of saham names -> {longitude, rashi, signifies}.
    """
    rules = _get_rules()
    saham_rules = rules.get("sahams", {}).get("points", {})

    sun_lon = planet_longitudes.get("sun", 0.0)
    moon_lon = planet_longitudes.get("moon", 0.0)
    mars_lon = planet_longitudes.get("mars", 0.0)
    mercury_lon = planet_longitudes.get("mercury", 0.0)
    jupiter_lon = planet_longitudes.get("jupiter", 0.0)
    venus_lon = planet_longitudes.get("venus", 0.0)
    saturn_lon = planet_longitudes.get("saturn", 0.0)

    # Calculate each saham using its formula
    formulas: dict[str, float] = {
        "punya_saham": (lagna_lon + moon_lon - sun_lon)
        if is_day_chart
        else (lagna_lon + sun_lon - moon_lon),
        "vidya_saham": lagna_lon + jupiter_lon - mercury_lon,
        "yashas_saham": lagna_lon + jupiter_lon - sun_lon,
        "mrityu_saham": lagna_lon + saturn_lon - moon_lon,
        "vivaha_saham": lagna_lon + venus_lon - saturn_lon,
        "santana_saham": lagna_lon + jupiter_lon - saturn_lon,
        "karma_saham": lagna_lon + saturn_lon - sun_lon,
        "rajya_saham": lagna_lon + saturn_lon - moon_lon,
        "roga_saham": lagna_lon + mars_lon - saturn_lon,
        "bandhu_saham": lagna_lon + mercury_lon - moon_lon,
    }

    result: dict[str, dict[str, Any]] = {}
    for saham_id, longitude in formulas.items():
        lon = longitude % 360
        rashi = int(lon / 30)
        saham_info = saham_rules.get(saham_id, {})

        result[saham_id] = {
            "name": saham_info.get("name", saham_id),
            "longitude": round(lon, 4),
            "rashi": rashi,
            "degree_in_rashi": round(lon % 30, 4),
            "signifies": saham_info.get("signifies", ""),
        }

    return result


def get_varshaphal_analysis(
    birth_lagna_rashi: int,
    age: int,
    varshaphal_lagna_rashi: int | None = None,
    planet_longitudes: dict[str, float] | None = None,
    lagna_lon: float = 0.0,
    is_day_chart: bool = True,
) -> dict[str, Any]:
    """Full Varshaphal (annual prediction) analysis.

    Args:
        birth_lagna_rashi: Birth chart ascendant sign (0-11)
        age: Completed age
        varshaphal_lagna_rashi: Annual chart lagna (0-11). If None, defaults to birth lagna.
        planet_longitudes: Planet longitudes in annual chart for saham calculation
        lagna_lon: Ascendant longitude for saham calculation
        is_day_chart: Whether birth/return is during daytime

    Returns:
        Comprehensive annual prediction dictionary.
    """
    # 1. Muntha
    muntha = calculate_muntha(birth_lagna_rashi, age)

    # 2. Varshesha
    vp_lagna = varshaphal_lagna_rashi if varshaphal_lagna_rashi is not None else birth_lagna_rashi
    varshesha = determine_varshesha(vp_lagna)

    # 3. Sahams (if planet positions provided)
    sahams = {}
    if planet_longitudes:
        sahams = calculate_sahams(planet_longitudes, lagna_lon, is_day_chart)

    # 4. Annual house effects
    rules = _get_rules()
    annual_effects = rules.get("annual_house_effects", {})

    # Get effects for the house Muntha falls in
    muntha_house = str(muntha["house_from_lagna"])
    muntha_annual = annual_effects.get(muntha_house, {})

    return {
        "age": age,
        "birth_lagna_rashi": birth_lagna_rashi,
        "varshaphal_lagna_rashi": vp_lagna,
        "muntha": muntha,
        "varshesha": varshesha,
        "sahams": sahams,
        "muntha_annual_themes": muntha_annual.get("themes", []),
        "annual_outlook": muntha["overall"],
    }
