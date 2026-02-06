"""Planetary War (Graha Yuddha) detection for 108 Vedic Astrology.

In Vedic astrology, a Graha Yuddha (planetary war) occurs when two planets
(Mars, Mercury, Jupiter, Venus, Saturn only -- NOT Sun, Moon, Rahu, Ketu)
are within 1 degree of each other in longitude.

Traditional rules:
- The planet with higher latitude wins (some traditions: brighter planet wins)
- Special: Venus always wins when retrograde
- The loser's significations and house lordships suffer

References: BPHS Chapter 23, Jataka Parijata, Saravali
"""

import contextlib
import logging
from typing import Any

from packages.core.src.constants import Planet, Rashi

logger = logging.getLogger(__name__)

# Only these 5 planets can engage in planetary war
WAR_ELIGIBLE_PLANETS = {Planet.MARS, Planet.MERCURY, Planet.JUPITER, Planet.VENUS, Planet.SATURN}

# Maximum separation for a planetary war (in degrees)
WAR_ORB = 1.0

# Sign lordship for house effects
SIGN_LORDS: dict[Rashi, Planet] = {
    Rashi.ARIES: Planet.MARS,
    Rashi.TAURUS: Planet.VENUS,
    Rashi.GEMINI: Planet.MERCURY,
    Rashi.CANCER: Planet.MOON,
    Rashi.LEO: Planet.SUN,
    Rashi.VIRGO: Planet.MERCURY,
    Rashi.LIBRA: Planet.VENUS,
    Rashi.SCORPIO: Planet.MARS,
    Rashi.SAGITTARIUS: Planet.JUPITER,
    Rashi.CAPRICORN: Planet.SATURN,
    Rashi.AQUARIUS: Planet.SATURN,
    Rashi.PISCES: Planet.JUPITER,
}

# Natural significations of planets (what the loser's defeat affects)
PLANET_SIGNIFICATIONS: dict[Planet, list[str]] = {
    Planet.MARS: ["courage", "siblings", "energy", "property", "surgery"],
    Planet.MERCURY: ["intellect", "communication", "commerce", "education", "speech"],
    Planet.JUPITER: ["wisdom", "children", "fortune", "dharma", "guru"],
    Planet.VENUS: ["marriage", "relationships", "luxury", "arts", "vehicles"],
    Planet.SATURN: ["discipline", "career", "longevity", "service", "persistence"],
}


def _angular_distance(lon1: float, lon2: float) -> float:
    """Minimum angular distance between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _get_planet_data(planet: Planet, planets: dict) -> dict | None:
    """Extract planet data from various dict formats."""
    data = planets.get(planet) or planets.get(planet.value)
    if data is None:
        return None
    if isinstance(data, dict):
        return data
    # PlanetPosition model
    return {
        "longitude": getattr(data, "longitude", 0.0),
        "latitude": getattr(data, "latitude", 0.0),
        "is_retrograde": getattr(data, "is_retrograde", False),
        "rashi": getattr(data, "rashi", None),
        "house": getattr(data, "house", None),
    }


def _determine_winner(
    planet1: Planet,
    data1: dict,
    planet2: Planet,
    data2: dict,
) -> tuple[Planet, Planet]:
    """Determine winner and loser of a planetary war.

    Traditional rules (in priority order):
    1. Venus always wins when retrograde
    2. The planet with higher (more northern) latitude wins

    Args:
        planet1: First planet
        data1: First planet's position data
        planet2: Second planet
        data2: Second planet's position data

    Returns:
        Tuple of (winner, loser)
    """
    # Special: Venus always wins when retrograde
    if planet1 == Planet.VENUS and data1.get("is_retrograde", False):
        return planet1, planet2
    if planet2 == Planet.VENUS and data2.get("is_retrograde", False):
        return planet2, planet1

    # Higher latitude wins
    lat1 = abs(data1.get("latitude", 0.0))
    lat2 = abs(data2.get("latitude", 0.0))

    if lat1 > lat2:
        return planet1, planet2
    elif lat2 > lat1:
        return planet2, planet1

    # Tiebreaker: higher longitude wins (as in strength.py convention)
    lon1 = data1.get("longitude", 0.0)
    lon2 = data2.get("longitude", 0.0)

    if lon1 >= lon2:
        return planet1, planet2
    return planet2, planet1


def detect_planetary_wars(planets: dict) -> list[dict]:
    """Detect all planetary wars (Graha Yuddha) in the chart.

    Checks all pairs of war-eligible planets (Mars, Mercury, Jupiter, Venus,
    Saturn) for conjunctions within 1 degree.

    Args:
        planets: Dictionary of planet positions. Keys can be Planet enums or
                 planet name strings. Values should have 'longitude', 'latitude',
                 and 'is_retrograde' attributes or keys.

    Returns:
        List of war dictionaries, each containing:
        - planet1 (str): First planet in war
        - planet2 (str): Second planet in war
        - winner (str): Planet that won the war
        - loser (str): Planet that lost the war
        - separation_degrees (float): Angular separation
        - effects (dict): Effects of the war on the loser
    """
    wars = []
    eligible = []

    # Collect eligible planets present in the chart
    for planet in WAR_ELIGIBLE_PLANETS:
        data = _get_planet_data(planet, planets)
        if data is not None:
            eligible.append((planet, data))

    # Check all pairs
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            p1, d1 = eligible[i]
            p2, d2 = eligible[j]

            lon1 = d1.get("longitude", 0.0)
            lon2 = d2.get("longitude", 0.0)

            separation = _angular_distance(lon1, lon2)

            if separation <= WAR_ORB:
                winner, loser = _determine_winner(p1, d1, p2, d2)
                loser_sigs = PLANET_SIGNIFICATIONS.get(loser, [])

                wars.append(
                    {
                        "planet1": p1.value,
                        "planet2": p2.value,
                        "winner": winner.value,
                        "loser": loser.value,
                        "separation_degrees": round(separation, 4),
                        "effects": {
                            "loser_weakened": True,
                            "affected_significations": loser_sigs,
                            "winner_strengthened": True,
                            "description": (
                                f"{winner.value.title()} wins the planetary war against "
                                f"{loser.value.title()}. {loser.value.title()}'s significations "
                                f"({', '.join(loser_sigs)}) are weakened."
                            ),
                        },
                    }
                )

    return wars


def get_war_effects(winner: str, loser: str, houses: dict | None = None) -> dict:
    """Get detailed effects of a planetary war on the loser's house lordships.

    Args:
        winner: Winner planet name (e.g., "mars")
        loser: Loser planet name (e.g., "mercury")
        houses: Optional dict mapping house numbers to their signs, or a
                lagna_rashi string from which house signs are derived.

    Returns:
        Dictionary with:
        - winner (str): Winner planet name
        - loser (str): Loser planet name
        - loser_significations (list[str]): Natural significations affected
        - affected_houses (list[int]): Houses ruled by the loser (if houses provided)
        - house_effects (list[dict]): Per-house effect descriptions
        - remedial_notes (str): Brief remedial guidance
    """
    try:
        loser_planet = Planet(loser.lower())
        winner_planet = Planet(winner.lower())
    except ValueError:
        return {
            "winner": winner,
            "loser": loser,
            "loser_significations": [],
            "affected_houses": [],
            "house_effects": [],
            "remedial_notes": "",
        }

    loser_sigs = PLANET_SIGNIFICATIONS.get(loser_planet, [])

    # Find houses ruled by the loser
    affected_houses: list[int] = []
    house_effects: list[dict[str, Any]] = []

    if houses:
        lagna_rashi = None
        if isinstance(houses, str):
            with contextlib.suppress(ValueError):
                lagna_rashi = Rashi(houses.lower())
        elif isinstance(houses, dict):
            # houses dict: {house_num: rashi_name}
            for h_num, h_sign in houses.items():
                try:
                    rashi = Rashi(h_sign.lower()) if isinstance(h_sign, str) else h_sign
                    if SIGN_LORDS.get(rashi) == loser_planet:
                        affected_houses.append(int(h_num))
                except (ValueError, AttributeError):
                    continue

        if lagna_rashi is not None:
            # Derive houses from lagna
            rashis = list(Rashi)
            lagna_idx = rashis.index(lagna_rashi)
            for h in range(1, 13):
                sign = rashis[(lagna_idx + h - 1) % 12]
                if SIGN_LORDS.get(sign) == loser_planet:
                    affected_houses.append(h)

        for h in affected_houses:
            house_effects.append(
                {
                    "house": h,
                    "effect": (
                        f"House {h} (ruled by {loser_planet.value.title()}) is weakened "
                        f"due to planetary war loss to {winner_planet.value.title()}"
                    ),
                }
            )

    remedial = (
        f"Strengthen {loser_planet.value.title()} through its gemstone, mantra, "
        f"or charity on its weekday to mitigate war effects."
    )

    return {
        "winner": winner_planet.value,
        "loser": loser_planet.value,
        "loser_significations": loser_sigs,
        "affected_houses": sorted(affected_houses),
        "house_effects": house_effects,
        "remedial_notes": remedial,
    }
