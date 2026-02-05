"""Planetary combustion (Asta) detection for 108 Vedic Astrology.

Combustion occurs when a planet is too close to the Sun, losing strength.
Uses thresholds from knowledge/rules/combustion_rules.json.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_combustion_rules

_combustion_cache: dict[str, Any] | None = None


def _get_rules() -> dict[str, Any]:
    """Get cached combustion rules."""
    global _combustion_cache
    if _combustion_cache is None:
        _combustion_cache = get_combustion_rules()
    return _combustion_cache


def _angular_distance(lon1: float, lon2: float) -> float:
    """Minimum angular distance between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def check_combustion(
    planet: str,
    planet_lon: float,
    sun_lon: float,
    is_retrograde: bool = False,
) -> dict[str, Any]:
    """Check if a planet is combust (too close to the Sun).

    Args:
        planet: Planet name (lowercase: moon, mars, mercury, jupiter, venus, saturn)
        planet_lon: Planet's sidereal longitude (0-360)
        sun_lon: Sun's sidereal longitude (0-360)
        is_retrograde: Whether the planet is retrograde

    Returns:
        Dictionary with combustion status, angular distance, effects, and remedies.
    """
    rules = _get_rules()
    planet_lower = planet.lower()

    # Sun, Rahu, Ketu cannot be combust
    if planet_lower in ("sun", "rahu", "ketu"):
        return {
            "planet": planet_lower,
            "is_combust": False,
            "is_deep_combust": False,
            "angular_distance": None,
            "strength_loss": 0,
            "effects": {},
            "remedies": [],
        }

    planet_rules = rules.get("planets", {}).get(planet_lower)
    if not planet_rules:
        return {
            "planet": planet_lower,
            "is_combust": False,
            "is_deep_combust": False,
            "angular_distance": None,
            "strength_loss": 0,
            "effects": {},
            "remedies": [],
        }

    dist = _angular_distance(planet_lon, sun_lon)

    # Mercury and Venus have special retrograde combustion degrees
    if is_retrograde and planet_lower in ("mercury", "venus"):
        combust_deg = planet_rules.get(
            "combustion_degree_retrograde", planet_rules["combustion_degree"]
        )
        deep_deg = planet_rules.get(
            "deep_combustion_degree_retrograde", planet_rules["deep_combustion_degree"]
        )
    else:
        combust_deg = planet_rules["combustion_degree"]
        deep_deg = planet_rules["deep_combustion_degree"]

    is_deep = dist <= deep_deg
    is_combust = dist <= combust_deg

    if is_deep:
        strength_loss = 0.825  # 75-90% average
    elif is_combust:
        strength_loss = 0.625  # 50-75% average
    else:
        strength_loss = 0.0

    effects = planet_rules.get("effects", {}) if is_combust else {}
    remedies = planet_rules.get("remedies", []) if is_combust else []

    return {
        "planet": planet_lower,
        "is_combust": is_combust,
        "is_deep_combust": is_deep,
        "angular_distance": round(dist, 4),
        "strength_loss": strength_loss,
        "effects": effects,
        "remedies": remedies,
    }


def get_combustion_analysis(
    planets: dict[str, dict[str, float | bool]],
) -> dict[str, Any]:
    """Analyze combustion for all planets relative to the Sun.

    Args:
        planets: Dict mapping planet name -> {longitude, is_retrograde}.
                 Must include "sun".

    Returns:
        Dictionary with combust_planets list, total_count, critical_combustions.
    """
    sun_data = planets.get("sun")
    if not sun_data:
        return {"combust_planets": [], "total_count": 0, "critical_combustions": []}

    sun_lon = sun_data.get("longitude", 0.0) if isinstance(sun_data, dict) else float(sun_data)

    combust_planets: list[dict[str, Any]] = []
    critical: list[str] = []

    for name, data in planets.items():
        if name.lower() == "sun":
            continue

        if isinstance(data, dict):
            lon = data.get("longitude", 0.0)
            retro = data.get("is_retrograde", False)
        else:
            lon = float(data)
            retro = False

        result = check_combustion(name, lon, sun_lon, is_retrograde=retro)
        if result["is_combust"]:
            combust_planets.append(result)
            if result["is_deep_combust"]:
                critical.append(name.lower())

    return {
        "combust_planets": combust_planets,
        "total_count": len(combust_planets),
        "critical_combustions": critical,
    }


def get_combustion_house_effects(planet: str, house: int) -> dict[str, Any]:
    """Get house-specific combustion effects for a planet.

    Args:
        planet: Planet name (lowercase)
        house: House number (1-12)

    Returns:
        Dictionary with house description, general effects, and planet-specific effects.
    """
    rules = _get_rules()
    house_effects = rules.get("house_wise_effects", {}).get(str(house), {})

    if not house_effects:
        return {"house": house, "planet": planet.lower(), "effects": {}}

    planet_lower = planet.lower()
    return {
        "house": house,
        "planet": planet_lower,
        "description": house_effects.get("description", ""),
        "general_effects": house_effects.get("general_effects", ""),
        "planet_specific": house_effects.get(planet_lower, ""),
    }
