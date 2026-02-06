"""Parashari Aspects (Graha Drishti) for Vedic Astrology.

This module calculates planetary aspects based on Brihat Parasara Hora Shastra (BPHS).
In Vedic astrology, aspects are house-based (not degree-based like Western astrology).

Rules:
- All planets aspect the 7th house from their position with full strength (1.0).
- Mars has special aspects on the 4th and 8th houses (0.75 strength).
- Jupiter has special aspects on the 5th and 9th houses (1.0 strength).
- Saturn has special aspects on the 3rd and 10th houses (0.75 strength).
- Rahu and Ketu aspect like Jupiter: 5th and 9th (1.0 strength).

Aspect data is loaded from knowledge/definitions/aspects.json.
"""

import json
from pathlib import Path

# Special aspects beyond the universal 7th house aspect.
# Maps planet -> list of (vedic_house_number, strength) for special aspects.
# In Vedic counting, "4th house" = 3 signs forward (1-based inclusive).
# The 7th house is universal and always included.
SPECIAL_ASPECTS: dict[str, list[tuple[int, float]]] = {
    "mars": [(4, 0.75), (8, 0.75)],
    "jupiter": [(5, 1.0), (9, 1.0)],
    "saturn": [(3, 0.75), (10, 0.75)],
    "rahu": [(5, 1.0), (9, 1.0)],
    "ketu": [(5, 1.0), (9, 1.0)],
}


def _vedic_house_from(base_house: int, nth_house: int) -> int:
    """Calculate which house number is the Nth house from a base house.

    In Vedic astrology, counting is 1-based inclusive:
    - 1st from house 1 = house 1 (itself)
    - 7th from house 1 = house 7
    - 4th from house 10 = house 1 (wraps around)

    Args:
        base_house: Starting house (1-12)
        nth_house: The Nth house to find (1-12)

    Returns:
        int: Target house number (1-12)
    """
    return ((base_house - 1 + nth_house - 1) % 12) + 1


def _load_aspect_data() -> dict:
    """Load aspect definitions from knowledge file.

    Returns:
        dict: Complete aspect data from aspects.json
    """
    aspects_path = (
        Path(__file__).parent.parent.parent.parent / "knowledge" / "definitions" / "aspects.json"
    )
    with aspects_path.open() as f:
        return json.load(f)


def get_planet_aspects(planet: str, house: int) -> list[int]:
    """Get houses aspected by a planet from its position.

    All planets aspect the 7th house from their position.
    Mars additionally aspects the 4th and 8th houses.
    Jupiter additionally aspects the 5th and 9th houses.
    Saturn additionally aspects the 3rd and 10th houses.
    Rahu/Ketu aspect like Jupiter (5th and 9th).

    Args:
        planet: Planet name (lowercase: sun, moon, mars, etc.)
        house: House number where the planet is placed (1-12)

    Returns:
        list[int]: Sorted list of house numbers (1-12) that the planet aspects

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> get_planet_aspects("mars", 1)
        [4, 7, 8]
        >>> get_planet_aspects("sun", 3)
        [9]
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    planet_lower = planet.lower()

    # Universal 7th aspect (all planets)
    aspected = {_vedic_house_from(house, 7)}

    # Special aspects
    if planet_lower in SPECIAL_ASPECTS:
        for nth_house, _strength in SPECIAL_ASPECTS[planet_lower]:
            aspected.add(_vedic_house_from(house, nth_house))

    return sorted(aspected)


def get_aspect_strength(aspecting: str, aspected_house: int, planet_house: int) -> float:
    """Get the drishti (aspect) strength of a planet on a specific house.

    Strength values:
    - Full aspect (1.0): 7th house for all planets; 5th/9th for Jupiter/Rahu/Ketu
    - Three-quarter aspect (0.75): 4th/8th for Mars; 3rd/10th for Saturn
    - No aspect (0.0): House is not aspected by the planet

    Args:
        aspecting: Planet name (lowercase)
        aspected_house: The house being aspected (1-12)
        planet_house: The house where the aspecting planet is placed (1-12)

    Returns:
        float: Aspect strength (0.0, 0.75, or 1.0)

    Raises:
        ValueError: If house numbers are not 1-12

    Example:
        >>> get_aspect_strength("mars", 4, 1)
        0.75
        >>> get_aspect_strength("jupiter", 9, 5)
        1.0
        >>> get_aspect_strength("sun", 3, 1)
        0.0
    """
    if not isinstance(aspected_house, int) or aspected_house < 1 or aspected_house > 12:
        raise ValueError(f"aspected_house must be 1-12, got {aspected_house}")
    if not isinstance(planet_house, int) or planet_house < 1 or planet_house > 12:
        raise ValueError(f"planet_house must be 1-12, got {planet_house}")

    planet_lower = aspecting.lower()

    # Calculate Vedic house number: what Nth house is aspected_house from planet_house?
    # 1-based inclusive counting: house 1 to house 7 = "7th house" = offset of 6.
    offset = (aspected_house - planet_house) % 12
    # offset 0 means same house (12th from itself in Vedic = not a standard aspect target)
    vedic_nth = offset + 1 if offset > 0 else 13  # 13 means same house, never matches

    # Check 7th house (universal full aspect)
    if vedic_nth == 7:
        return 1.0

    # Check special aspects
    if planet_lower in SPECIAL_ASPECTS:
        for nth_house, strength in SPECIAL_ASPECTS[planet_lower]:
            if vedic_nth == nth_house:
                return strength

    return 0.0


def get_all_aspects(planet_positions: dict[str, int]) -> dict[str, list[dict]]:
    """Get complete aspect map for all planets.

    Given a mapping of planet names to their house positions, returns
    the full aspect picture showing which houses each planet aspects
    and with what strength.

    Args:
        planet_positions: Dictionary mapping planet names to house numbers (1-12).
                          Example: {"sun": 1, "moon": 4, "mars": 7}

    Returns:
        dict: Mapping of planet names to lists of aspect dictionaries.
              Each aspect dict has: {"house": int, "strength": float}

    Example:
        >>> positions = {"sun": 1, "mars": 4}
        >>> aspects = get_all_aspects(positions)
        >>> aspects["sun"]
        [{"house": 7, "strength": 1.0}]
        >>> aspects["mars"]
        [{"house": 7, "strength": 0.75}, {"house": 10, "strength": 1.0}, {"house": 11, "strength": 0.75}]
    """
    result = {}

    for planet, house in planet_positions.items():
        planet_lower = planet.lower()
        aspected_houses = get_planet_aspects(planet_lower, house)

        aspects = []
        for aspected_house in aspected_houses:
            strength = get_aspect_strength(planet_lower, aspected_house, house)
            aspects.append({"house": aspected_house, "strength": strength})

        result[planet_lower] = aspects

    return result


def get_houses_aspected_by(planet_positions: dict[str, int]) -> dict[int, list[dict]]:
    """Get aspects received by each house from all planets.

    Inverts the aspect map to show, for each house, which planets
    aspect it and with what strength.

    Args:
        planet_positions: Dictionary mapping planet names to house numbers (1-12).

    Returns:
        dict: Mapping of house numbers (1-12) to lists of aspect dictionaries.
              Each dict has: {"planet": str, "strength": float, "from_house": int}

    Example:
        >>> positions = {"sun": 1, "mars": 4}
        >>> received = get_houses_aspected_by(positions)
        >>> received[7]
        [{"planet": "sun", "strength": 1.0, "from_house": 1}, ...]
    """
    houses_received: dict[int, list[dict]] = {h: [] for h in range(1, 13)}

    for planet, house in planet_positions.items():
        planet_lower = planet.lower()
        aspected_houses = get_planet_aspects(planet_lower, house)

        for aspected_house in aspected_houses:
            strength = get_aspect_strength(planet_lower, aspected_house, house)
            houses_received[aspected_house].append(
                {"planet": planet_lower, "strength": strength, "from_house": house}
            )

    return houses_received


__all__ = [
    "SPECIAL_ASPECTS",
    "get_all_aspects",
    "get_aspect_strength",
    "get_houses_aspected_by",
    "get_planet_aspects",
]
