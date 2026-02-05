"""Planetary retrograde (Vakri) effects for 108 Vedic Astrology.

Provides retrograde analysis using knowledge/rules/retrograde_rules.json.
Covers Mars, Mercury, Jupiter, Venus, Saturn natal and transit effects.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_retrograde_rules

_retrograde_cache: dict[str, Any] | None = None


def _get_rules() -> dict[str, Any]:
    """Get cached retrograde rules."""
    global _retrograde_cache
    if _retrograde_cache is None:
        _retrograde_cache = get_retrograde_rules()
    return _retrograde_cache


# Planets that can be retrograde (Sun and Moon never retrograde, Rahu/Ketu always retrograde)
RETROGRADE_PLANETS = {"mars", "mercury", "jupiter", "venus", "saturn"}


def get_retrograde_effects(
    planet: str,
    is_natal: bool = True,
    house: int | None = None,
) -> dict[str, Any]:
    """Get retrograde effects for a planet.

    Args:
        planet: Planet name (lowercase: mars, mercury, jupiter, venus, saturn)
        is_natal: True for birth chart retrograde, False for transit retrograde
        house: House number (1-12) for transit house-specific effects

    Returns:
        Dictionary with general, positive, negative effects, house_effects, and remedies.
    """
    rules = _get_rules()
    planet_lower = planet.lower()

    if planet_lower not in RETROGRADE_PLANETS:
        return {
            "planet": planet_lower,
            "is_natal": is_natal,
            "effects": {},
            "remedies": [],
        }

    planet_rules = rules.get("planets", {}).get(planet_lower, {})
    if not planet_rules:
        return {
            "planet": planet_lower,
            "is_natal": is_natal,
            "effects": {},
            "remedies": [],
        }

    if is_natal:
        effects_data = planet_rules.get("natal_effects", {})
    else:
        effects_data = planet_rules.get("transit_effects", {})

    result: dict[str, Any] = {
        "planet": planet_lower,
        "is_natal": is_natal,
        "general": effects_data.get("general", []),
        "positive": effects_data.get("positive", []),
        "negative": effects_data.get("negative", []),
        "remedies": planet_rules.get("remedies", []),
    }

    # Add karmic indication for natal
    if is_natal:
        result["karmic_indication"] = effects_data.get("karmic_indication", "")

    # Add house-specific effects for transit
    if not is_natal and house is not None:
        house_effects = effects_data.get("house_effects", {}).get(str(house), {})
        result["house_effects"] = house_effects
    else:
        result["house_effects"] = {}

    return result


def get_retrograde_analysis(
    planets: dict[str, dict[str, Any]],
    is_natal: bool = True,
) -> dict[str, Any]:
    """Analyze retrograde effects for all retrograde planets.

    Args:
        planets: Dict mapping planet name -> {is_retrograde: bool, house: int, ...}
        is_natal: Whether this is natal chart analysis

    Returns:
        Dictionary with retrograde_planets list, count, and karmic_themes.
    """
    retrograde_planets: list[dict[str, Any]] = []
    karmic_themes: list[str] = []

    for name, data in planets.items():
        planet_lower = name.lower()
        if planet_lower not in RETROGRADE_PLANETS:
            continue

        is_retro = data.get("is_retrograde", False) if isinstance(data, dict) else False
        if not is_retro:
            continue

        house = data.get("house") if isinstance(data, dict) else None
        effects = get_retrograde_effects(planet_lower, is_natal=is_natal, house=house)
        retrograde_planets.append(effects)

        if is_natal and effects.get("karmic_indication"):
            karmic_themes.append(effects["karmic_indication"])

    return {
        "retrograde_planets": retrograde_planets,
        "count": len(retrograde_planets),
        "karmic_themes": karmic_themes,
    }
