"""Divisional chart (D9/D10) interpretation for 108 Vedic Astrology.

Interprets planet placements in Navamsha (D9) and Dashamsha (D10) charts
using knowledge/rules/divisional_interpretation.json.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_divisional_interpretation
from packages.cosmos.src.divisional import DivisionalChart, get_divisional_chart

_interp_cache: dict[str, Any] | None = None


def _get_interp() -> dict[str, Any]:
    """Get cached divisional interpretation rules."""
    global _interp_cache
    if _interp_cache is None:
        _interp_cache = get_divisional_interpretation()
    return _interp_cache


RASHI_NAMES_LOWER = [
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


def interpret_d9_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D9 (Navamsha) chart.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with theme, marriage, dharma, strength, characteristics.
    """
    interp = _get_interp()
    d9 = interp.get("d9_navamsha", {})
    planet_data = d9.get("planet_in_signs", {}).get(planet.lower(), {})
    sign_data = planet_data.get(rashi_name.lower(), {})

    if not sign_data:
        return {
            "planet": planet.lower(),
            "rashi": rashi_name.lower(),
            "found": False,
        }

    return {
        "planet": planet.lower(),
        "rashi": rashi_name.lower(),
        "found": True,
        "theme": sign_data.get("theme", ""),
        "marriage": sign_data.get("marriage", ""),
        "dharma": sign_data.get("dharma", ""),
        "strength": sign_data.get("strength", ""),
        "characteristics": sign_data.get("characteristics", ""),
    }


def interpret_d10_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D10 (Dashamsha) chart.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with theme, career, leadership, strength, characteristics.
    """
    interp = _get_interp()
    d10 = interp.get("d10_dashamsha", {})
    planet_data = d10.get("planet_in_signs", {}).get(planet.lower(), {})
    sign_data = planet_data.get(rashi_name.lower(), {})

    if not sign_data:
        return {
            "planet": planet.lower(),
            "rashi": rashi_name.lower(),
            "found": False,
        }

    return {
        "planet": planet.lower(),
        "rashi": rashi_name.lower(),
        "found": True,
        "theme": sign_data.get("theme", ""),
        "career": sign_data.get("career", ""),
        "leadership": sign_data.get("leadership", ""),
        "strength": sign_data.get("strength", ""),
        "characteristics": sign_data.get("characteristics", ""),
    }


def _get_house_meanings(division_key: str) -> dict[str, Any]:
    """Get house meanings for a divisional chart."""
    interp = _get_interp()
    return interp.get(division_key, {}).get("house_meanings", {})


def _get_special_rules(division_key: str) -> list[dict[str, Any]]:
    """Get special rules for a divisional chart."""
    interp = _get_interp()
    return interp.get(division_key, {}).get("special_rules", [])


def interpret_d9_chart(d9_chart: DivisionalChart) -> dict[str, Any]:
    """Interpret a complete D9 (Navamsha) chart.

    Args:
        d9_chart: DivisionalChart from get_divisional_chart(planets, 9)

    Returns:
        Dictionary with planet interpretations, house meanings, and special rules.
    """
    planet_interpretations: dict[str, Any] = {}

    for planet_name, pos in d9_chart.get("positions", {}).items():
        rashi_name = pos.get("rashi_name", "").lower()
        if rashi_name:
            planet_interpretations[planet_name] = interpret_d9_position(planet_name, rashi_name)

    house_meanings = _get_house_meanings("d9_navamsha")
    special_rules = _get_special_rules("d9_navamsha")

    return {
        "division": 9,
        "division_name": "Navamsha",
        "planets": planet_interpretations,
        "house_meanings": house_meanings,
        "special_rules": special_rules,
    }


def interpret_d10_chart(d10_chart: DivisionalChart) -> dict[str, Any]:
    """Interpret a complete D10 (Dashamsha) chart.

    Args:
        d10_chart: DivisionalChart from get_divisional_chart(planets, 10)

    Returns:
        Dictionary with planet interpretations, house meanings, and special rules.
    """
    planet_interpretations: dict[str, Any] = {}

    for planet_name, pos in d10_chart.get("positions", {}).items():
        rashi_name = pos.get("rashi_name", "").lower()
        if rashi_name:
            planet_interpretations[planet_name] = interpret_d10_position(planet_name, rashi_name)

    house_meanings = _get_house_meanings("d10_dashamsha")
    special_rules = _get_special_rules("d10_dashamsha")

    return {
        "division": 10,
        "division_name": "Dashamsha",
        "planets": planet_interpretations,
        "house_meanings": house_meanings,
        "special_rules": special_rules,
    }


def get_divisional_analysis(planet_longitudes: dict[str, float]) -> dict[str, Any]:
    """Full D9 + D10 analysis from planet longitudes.

    Args:
        planet_longitudes: Dict mapping planet name -> longitude (0-360)

    Returns:
        Dictionary with d9 and d10 interpretations.
    """
    d9_chart = get_divisional_chart(planet_longitudes, 9)
    d10_chart = get_divisional_chart(planet_longitudes, 10)

    return {
        "d9_navamsha": interpret_d9_chart(d9_chart),
        "d10_dashamsha": interpret_d10_chart(d10_chart),
    }
