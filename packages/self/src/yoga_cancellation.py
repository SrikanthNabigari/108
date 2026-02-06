"""Comprehensive Yoga Cancellation (Yoga Bhanga) Engine for 108 Vedic Astrology.

This module provides a standalone, comprehensive engine for evaluating whether
detected yogas are cancelled, partially weakened, or fully negated based on
classical Vedic astrology principles.

Cancellation rules include:
- Pancha Mahapurusha yogas: cancelled by combustion or planetary war loss
- Raja Yoga: cancelled when forming planets are debilitated or in 6/8/12
- Dhana Yoga: cancelled when 2nd/11th lords afflicted by malefics
- Gajakesari: cancelled when Moon/Jupiter in dusthana from Lagna
- Neecha Bhanga: itself cancelled if debilitated planet is combust

References: BPHS, Phaladipika, Jataka Parijata
"""

import json
import logging
from pathlib import Path
from typing import Any

from packages.core.src.constants import Planet, Rashi

logger = logging.getLogger(__name__)

# Sign lordship mapping
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

# Exaltation signs
PLANET_EXALTATION: dict[Planet, Rashi] = {
    Planet.SUN: Rashi.ARIES,
    Planet.MOON: Rashi.TAURUS,
    Planet.MARS: Rashi.CAPRICORN,
    Planet.MERCURY: Rashi.VIRGO,
    Planet.JUPITER: Rashi.CANCER,
    Planet.VENUS: Rashi.PISCES,
    Planet.SATURN: Rashi.LIBRA,
}

# Debilitation signs
PLANET_DEBILITATION: dict[Planet, Rashi] = {
    Planet.SUN: Rashi.LIBRA,
    Planet.MOON: Rashi.SCORPIO,
    Planet.MARS: Rashi.CANCER,
    Planet.MERCURY: Rashi.PISCES,
    Planet.JUPITER: Rashi.CAPRICORN,
    Planet.VENUS: Rashi.VIRGO,
    Planet.SATURN: Rashi.ARIES,
}

MALEFIC_PLANETS = {Planet.MARS, Planet.SATURN, Planet.RAHU, Planet.KETU}
DUSTHANA_HOUSES = {6, 8, 12}
KENDRA_HOUSES = {1, 4, 7, 10}

# Combustion orbs (degrees from Sun)
COMBUSTION_ORBS: dict[Planet, float] = {
    Planet.MOON: 12.0,
    Planet.MARS: 17.0,
    Planet.MERCURY: 14.0,
    Planet.JUPITER: 11.0,
    Planet.VENUS: 10.0,
    Planet.SATURN: 15.0,
}

# Yoga type mapping for cancellation rules
PANCHA_MAHAPURUSHA_TYPES = {"pancha_mahapurusha", "hamsa", "malavya", "ruchaka", "bhadra", "sasa"}
RAJA_YOGA_TYPES = {"raja", "raja_yoga"}
DHANA_YOGA_TYPES = {"dhana", "dhana_yoga"}
GAJAKESARI_TYPES = {"gajakesari", "gaj_kesari", "gajakesari_yoga"}

_cancellation_rules_cache: dict[str, Any] | None = None


def _load_cancellation_rules() -> dict[str, Any]:
    """Load cancellation rules from knowledge base."""
    global _cancellation_rules_cache
    if _cancellation_rules_cache is not None:
        return _cancellation_rules_cache

    rules_path = (
        Path(__file__).parent.parent.parent.parent
        / "knowledge"
        / "rules"
        / "yoga_cancellation_rules.json"
    )
    try:
        with rules_path.open() as f:
            _cancellation_rules_cache = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load yoga cancellation rules: {e}")
        _cancellation_rules_cache = {}

    return _cancellation_rules_cache


def _angular_distance(lon1: float, lon2: float) -> float:
    """Minimum angular distance between two longitudes (0-180)."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _house_from_reference(planet_rashi: Rashi, ref_rashi: Rashi) -> int:
    """Get house number of planet_rashi from ref_rashi."""
    rashis = list(Rashi)
    planet_idx = rashis.index(planet_rashi)
    ref_idx = rashis.index(ref_rashi)
    return ((planet_idx - ref_idx) % 12) + 1


def _is_combust(planet: str, planets: dict, sun_longitude: float) -> bool:
    """Check if a planet is combust (too close to Sun)."""
    try:
        p = Planet(planet.lower()) if isinstance(planet, str) else planet
    except ValueError:
        return False

    if p == Planet.SUN or p in (Planet.RAHU, Planet.KETU):
        return False

    orb = COMBUSTION_ORBS.get(p)
    if orb is None:
        return False

    planet_data = planets.get(p) or planets.get(planet)
    if planet_data is None:
        return False

    if isinstance(planet_data, dict):
        planet_lon = planet_data.get("longitude", 0.0)
    else:
        planet_lon = getattr(planet_data, "longitude", 0.0)

    return _angular_distance(planet_lon, sun_longitude) < orb


def _is_debilitated(planet: str, planets: dict) -> bool:
    """Check if a planet is in its debilitation sign."""
    try:
        p = Planet(planet.lower()) if isinstance(planet, str) else planet
    except ValueError:
        return False

    debil_sign = PLANET_DEBILITATION.get(p)
    if debil_sign is None:
        return False

    planet_data = planets.get(p) or planets.get(planet)
    if planet_data is None:
        return False

    if isinstance(planet_data, dict):
        rashi = planet_data.get("rashi")
        if isinstance(rashi, str):
            rashi = Rashi(rashi)
    else:
        rashi = getattr(planet_data, "rashi", None)

    return rashi == debil_sign


def _get_planet_rashi(planet_key: Any, planets: dict) -> Rashi | None:
    """Extract rashi from planet data."""
    planet_data = planets.get(planet_key)
    if planet_data is None:
        return None

    if isinstance(planet_data, dict):
        rashi = planet_data.get("rashi")
        if isinstance(rashi, str):
            return Rashi(rashi)
        return rashi
    return getattr(planet_data, "rashi", None)


def _get_planet_house(planet_key: Any, planets: dict) -> int | None:
    """Extract house from planet data."""
    planet_data = planets.get(planet_key)
    if planet_data is None:
        return None

    if isinstance(planet_data, dict):
        return planet_data.get("house")
    return getattr(planet_data, "house", None)


def _get_planet_longitude(planet_key: Any, planets: dict) -> float | None:
    """Extract longitude from planet data."""
    planet_data = planets.get(planet_key)
    if planet_data is None:
        return None

    if isinstance(planet_data, dict):
        return planet_data.get("longitude")
    return getattr(planet_data, "longitude", None)


def _has_simple_neecha_bhanga(planet: Planet, planets: dict, lagna_rashi: str) -> bool:
    """Simplified Neecha Bhanga check for cancellation engine.

    Conditions (any one suffices):
    1. Lord of debilitation sign in kendra from Lagna
    2. Lord of exaltation sign in kendra from Lagna
    3. Debilitated planet in kendra house
    4. Debilitated planet is retrograde
    """
    try:
        lagna = Rashi(lagna_rashi) if isinstance(lagna_rashi, str) else lagna_rashi
    except ValueError:
        return False

    debil_sign = PLANET_DEBILITATION.get(planet)
    if debil_sign is None:
        return False

    planet_rashi = _get_planet_rashi(planet, planets)
    if planet_rashi != debil_sign:
        return False

    # Condition 4: Retrograde
    planet_data = planets.get(planet)
    if planet_data is not None:
        is_retro = (
            planet_data.get("is_retrograde", False)
            if isinstance(planet_data, dict)
            else getattr(planet_data, "is_retrograde", False)
        )
        if is_retro:
            return True

    # Condition 3: In kendra house
    house = _get_planet_house(planet, planets)
    if house is not None and house in KENDRA_HOUSES:
        return True

    # Condition 1: Lord of debilitation sign in kendra from Lagna
    debil_lord = SIGN_LORDS.get(debil_sign)
    if debil_lord and debil_lord in planets:
        lord_rashi = _get_planet_rashi(debil_lord, planets)
        if lord_rashi is not None:
            h = _house_from_reference(lord_rashi, lagna)
            if h in KENDRA_HOUSES:
                return True

    # Condition 2: Lord of exaltation sign in kendra from Lagna
    exalt_sign = PLANET_EXALTATION.get(planet)
    if exalt_sign:
        exalt_lord = SIGN_LORDS.get(exalt_sign)
        if exalt_lord and exalt_lord in planets:
            lord_rashi = _get_planet_rashi(exalt_lord, planets)
            if lord_rashi is not None:
                h = _house_from_reference(lord_rashi, lagna)
                if h in KENDRA_HOUSES:
                    return True

    return False


def _count_malefic_conjunctions(planet: Planet, planets: dict) -> int:
    """Count number of malefic planets conjunct (in same sign) as target planet."""
    planet_rashi = _get_planet_rashi(planet, planets)
    if planet_rashi is None:
        return 0

    count = 0
    for malefic in MALEFIC_PLANETS:
        if malefic == planet:
            continue
        mal_rashi = _get_planet_rashi(malefic, planets)
        if mal_rashi == planet_rashi:
            count += 1
    return count


def get_cancellation_rules(yoga_type: str) -> list[dict]:
    """Load cancellation rules for a specific yoga type from the knowledge base.

    Args:
        yoga_type: Type of yoga (e.g., "pancha_mahapurusha", "raja_yoga", "dhana_yoga")

    Returns:
        List of cancellation rule dictionaries for the given type.
    """
    rules = _load_cancellation_rules()
    cancellation_types = rules.get("cancellation_types", {})

    yoga_lower = yoga_type.lower()

    # Direct match
    if yoga_lower in cancellation_types:
        return cancellation_types[yoga_lower].get("conditions", [])

    # Check by category mapping
    if yoga_lower in PANCHA_MAHAPURUSHA_TYPES:
        return cancellation_types.get("pancha_mahapurusha", {}).get("conditions", [])
    if yoga_lower in RAJA_YOGA_TYPES:
        return cancellation_types.get("raja_yoga", {}).get("conditions", [])
    if yoga_lower in DHANA_YOGA_TYPES:
        return cancellation_types.get("dhana_yoga", {}).get("conditions", [])
    if yoga_lower in GAJAKESARI_TYPES:
        return cancellation_types.get("gajakesari", {}).get("conditions", [])

    # Fall back to general rules
    return rules.get("general_cancellation_conditions", [])


def check_yoga_cancellation(
    yoga: dict,
    planets: dict,
    lagna_rashi: str,
    sun_longitude: float,
) -> dict:
    """Check if a specific yoga is cancelled based on comprehensive rules.

    Evaluates the yoga against type-specific and general cancellation conditions.

    Args:
        yoga: Dictionary with at least 'category' (or 'type') and 'involved_planets'
              keys. May also include 'name', 'id', etc.
        planets: Dictionary of planet positions. Keys can be Planet enums or strings.
                 Values should have 'longitude', 'rashi', 'house', 'is_retrograde' attrs.
        lagna_rashi: Ascendant sign name (e.g., "aries", "libra")
        sun_longitude: Sun's sidereal longitude in degrees (0-360)

    Returns:
        Dictionary with:
        - cancelled (bool): Whether the yoga is fully cancelled
        - reason (str): Description of why it was cancelled
        - partial (bool): Whether the yoga is partially weakened
        - modified_strength (float): Strength multiplier (0.0-1.0, where 1.0 = no effect)
    """
    result = {
        "cancelled": False,
        "reason": "",
        "partial": False,
        "modified_strength": 1.0,
    }

    category = yoga.get("category", yoga.get("type", "other")).lower()
    involved_planets = yoga.get("involved_planets", [])

    if not involved_planets:
        return result

    # Normalize involved planets to Planet enums
    planet_enums = []
    for p in involved_planets:
        try:
            planet_enums.append(Planet(p.lower()) if isinstance(p, str) else p)
        except ValueError:
            continue

    if not planet_enums:
        return result

    # --- TYPE-SPECIFIC CHECKS ---

    # 1. Pancha Mahapurusha cancellation
    if category in PANCHA_MAHAPURUSHA_TYPES:
        for p in planet_enums:
            if _is_combust(p, planets, sun_longitude):
                return {
                    "cancelled": True,
                    "reason": f"{p.value.title()} is combust - Pancha Mahapurusha yoga cancelled",
                    "partial": False,
                    "modified_strength": 0.0,
                }

    # 2. Raja Yoga: mutual dusthana check
    if category in RAJA_YOGA_TYPES and len(planet_enums) >= 2:
        for i in range(len(planet_enums)):
            r_i = _get_planet_rashi(planet_enums[i], planets)
            for j in range(i + 1, len(planet_enums)):
                r_j = _get_planet_rashi(planet_enums[j], planets)
                if r_i is not None and r_j is not None:
                    h = _house_from_reference(r_j, r_i)
                    if h in DUSTHANA_HOUSES:
                        return {
                            "cancelled": True,
                            "reason": (
                                f"{planet_enums[j].value.title()} is in house {h} "
                                f"from {planet_enums[i].value.title()} (dusthana) - "
                                "Raja Yoga cancelled"
                            ),
                            "partial": False,
                            "modified_strength": 0.0,
                        }

    # 3. Dhana Yoga: 2nd/11th lord affliction
    if category in DHANA_YOGA_TYPES:
        for p in planet_enums:
            if _count_malefic_conjunctions(p, planets) >= 2:
                return {
                    "cancelled": True,
                    "reason": (
                        f"{p.value.title()} is afflicted by 2+ malefics - Dhana Yoga cancelled"
                    ),
                    "partial": False,
                    "modified_strength": 0.0,
                }

    # 4. Gajakesari: Moon or Jupiter in dusthana from Lagna
    if category in GAJAKESARI_TYPES:
        try:
            lagna = Rashi(lagna_rashi) if isinstance(lagna_rashi, str) else lagna_rashi
        except ValueError:
            lagna = None

        if lagna:
            for target in (Planet.MOON, Planet.JUPITER):
                if target in planets:
                    target_rashi = _get_planet_rashi(target, planets)
                    if target_rashi is not None:
                        h = _house_from_reference(target_rashi, lagna)
                        if h in DUSTHANA_HOUSES:
                            return {
                                "cancelled": True,
                                "reason": (
                                    f"{target.value.title()} is in house {h} "
                                    f"from Lagna (dusthana) - Gajakesari cancelled"
                                ),
                                "partial": False,
                                "modified_strength": 0.0,
                            }

    # --- GENERAL CHECKS (apply to all yoga types) ---
    reasons = []
    min_strength = 1.0

    for p in planet_enums:
        # Combustion
        if _is_combust(p, planets, sun_longitude):
            return {
                "cancelled": True,
                "reason": f"{p.value.title()} is combust by Sun",
                "partial": False,
                "modified_strength": 0.0,
            }

        # Debilitation without Neecha Bhanga
        if _is_debilitated(p, planets) and not _has_simple_neecha_bhanga(p, planets, lagna_rashi):
            return {
                "cancelled": True,
                "reason": (f"{p.value.title()} is debilitated without Neecha Bhanga"),
                "partial": False,
                "modified_strength": 0.0,
            }

        # Severe malefic affliction
        if _count_malefic_conjunctions(p, planets) >= 2:
            return {
                "cancelled": True,
                "reason": (f"{p.value.title()} is conjunct 2+ malefics"),
                "partial": False,
                "modified_strength": 0.0,
            }

        # Partial: debilitation WITH Neecha Bhanga (weakened but not cancelled)
        if _is_debilitated(p, planets) and _has_simple_neecha_bhanga(p, planets, lagna_rashi):
            reasons.append(
                f"{p.value.title()} is debilitated (has Neecha Bhanga - partially weakened)"
            )
            min_strength = min(min_strength, 0.6)

        # Partial: single malefic conjunction
        mal_count = _count_malefic_conjunctions(p, planets)
        if mal_count == 1:
            reasons.append(f"{p.value.title()} conjunct 1 malefic (partially weakened)")
            min_strength = min(min_strength, 0.7)

    if min_strength < 1.0:
        result["partial"] = True
        result["modified_strength"] = round(min_strength, 2)
        result["reason"] = "; ".join(reasons)

    return result


def apply_cancellations_to_chart(
    yogas: list[dict],
    planets: dict,
    lagna_rashi: str,
    sun_longitude: float,
) -> list[dict]:
    """Apply cancellation checks to all detected yogas in a chart.

    Args:
        yogas: List of yoga dictionaries, each with 'category' and 'involved_planets'.
        planets: Dictionary of planet positions.
        lagna_rashi: Ascendant sign name.
        sun_longitude: Sun's sidereal longitude.

    Returns:
        List of yogas with cancellation status added. Each yoga dict gets:
        - 'cancellation': the full cancellation result dict
        - 'effective_strength': original strength * modified_strength
    """
    results = []
    for yoga in yogas:
        cancellation = check_yoga_cancellation(yoga, planets, lagna_rashi, sun_longitude)

        enriched = dict(yoga)
        enriched["cancellation"] = cancellation

        original_strength = yoga.get("strength", 1.0)
        enriched["effective_strength"] = round(
            original_strength * cancellation["modified_strength"], 4
        )

        results.append(enriched)

    return results
