"""Transit Lordship Resolver for Vedic astrology.

Determines functional roles of planets based on house lordship for a given lagna,
and analyzes how transiting planets activate those lordships. This bridges the
gap between raw transit positions and meaningful life-area predictions.

Key concepts:
    - Each planet rules 1-2 houses depending on lagna
    - Functional nature (yogakaraka, benefic, malefic, maraka, neutral) is lagna-specific
    - A transit activates the themes of the houses the transiting planet lords
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.cosmos.src.houses import (
    DUSTHANA_HOUSES,
    HOUSE_SIGNIFICATIONS,
    KENDRA_HOUSES,
    MARAKA_HOUSES,
    SIGN_RULERS,
    TRIKONA_HOUSES,
    get_house_from_reference,
    get_house_lord,
)


def _load_lord_interpretations() -> dict:
    """Load house lord placement interpretations from knowledge base."""
    path = (
        Path(__file__).parent.parent.parent.parent
        / "knowledge"
        / "interpretations"
        / "house_lord_in_house.json"
    )
    try:
        with path.open() as f:
            data = json.load(f)
        return data.get("house_lord_in_house", data)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_LORD_INTERPRETATIONS = _load_lord_interpretations()

# Houses considered favorable for transit placement
_FAVORABLE_HOUSES = {1, 2, 4, 5, 7, 9, 10, 11}
_CHALLENGING_HOUSES = {3, 6, 8, 12}


def get_all_house_lords(lagna_rashi: int) -> dict[int, str]:
    """Return the lord of each house (1-12) for the given lagna.

    Args:
        lagna_rashi: Lagna rashi number (0-11), where 0=Aries, 6=Libra, etc.

    Returns:
        Dict mapping house number (1-12) to planet name.

    Example:
        >>> lords = get_all_house_lords(6)  # Libra lagna
        >>> lords[1]
        'venus'
        >>> lords[4]
        'saturn'
    """
    return {house: get_house_lord(house, lagna_rashi) for house in range(1, 13)}


def get_planet_lordships(planet: str, lagna_rashi: int) -> list[int]:
    """Return which houses a planet lords for the given lagna (reverse lookup).

    Args:
        planet: Planet name (lowercase, e.g. "mars", "saturn").
        lagna_rashi: Lagna rashi number (0-11).

    Returns:
        Sorted list of house numbers the planet rules. Sun and Moon always
        rule exactly 1 house; other planets rule 2.

    Example:
        >>> get_planet_lordships("saturn", 6)  # Libra lagna
        [4, 5]
    """
    planet_lower = planet.lower()
    houses: list[int] = []
    for house in range(1, 13):
        sign_on_house = (lagna_rashi + house - 1) % 12
        if SIGN_RULERS[sign_on_house] == planet_lower:
            houses.append(house)
    return sorted(houses)


def classify_planet_role(planet: str, lagna_rashi: int) -> dict[str, Any]:
    """Classify the functional role of a planet for a given lagna.

    Determines whether a planet acts as yogakaraka, benefic, malefic,
    maraka, or neutral based on the houses it lords.

    Args:
        planet: Planet name (lowercase).
        lagna_rashi: Lagna rashi number (0-11).

    Returns:
        Dict with keys: planet, houses_ruled, functional_nature,
        is_kendradhipati, is_trikonadhipati, is_dusthana_lord,
        is_yogakaraka, is_maraka.

    Example:
        >>> role = classify_planet_role("saturn", 6)  # Libra lagna
        >>> role["functional_nature"]
        'yogakaraka'
        >>> role["is_yogakaraka"]
        True
    """
    planet_lower = planet.lower()
    houses_ruled = get_planet_lordships(planet_lower, lagna_rashi)

    is_kendradhipati = any(h in KENDRA_HOUSES for h in houses_ruled)
    is_trikonadhipati = any(h in TRIKONA_HOUSES for h in houses_ruled)
    is_dusthana_lord = any(h in DUSTHANA_HOUSES for h in houses_ruled)
    is_maraka = any(h in MARAKA_HOUSES for h in houses_ruled)
    is_yogakaraka = is_kendradhipati and is_trikonadhipati

    # Determine primary functional nature
    if is_yogakaraka:
        functional_nature = "yogakaraka"
    elif is_trikonadhipati and not is_dusthana_lord:
        functional_nature = "benefic"
    elif is_dusthana_lord and not is_trikonadhipati and not is_kendradhipati:
        functional_nature = "malefic"
    elif is_maraka and not is_trikonadhipati and not is_yogakaraka:
        functional_nature = "maraka"
    else:
        functional_nature = "neutral"

    return {
        "planet": planet_lower,
        "houses_ruled": houses_ruled,
        "functional_nature": functional_nature,
        "is_kendradhipati": is_kendradhipati,
        "is_trikonadhipati": is_trikonadhipati,
        "is_dusthana_lord": is_dusthana_lord,
        "is_yogakaraka": is_yogakaraka,
        "is_maraka": is_maraka,
    }


def _determine_transit_quality(
    functional_nature: str,
    transit_house: int,
    is_yogakaraka: bool,
) -> str:
    """Determine the quality of a transit based on nature and house placement.

    Args:
        functional_nature: The planet's functional nature string.
        transit_house: The house the planet is transiting (1-12).
        is_yogakaraka: Whether the planet is yogakaraka.

    Returns:
        One of "excellent", "favorable", "challenging", or "neutral".
    """
    in_kendra_or_trikona = transit_house in KENDRA_HOUSES or transit_house in TRIKONA_HOUSES
    in_dusthana = transit_house in DUSTHANA_HOUSES

    if is_yogakaraka and in_kendra_or_trikona:
        return "excellent"
    if functional_nature == "benefic" and not in_dusthana:
        return "favorable"
    if functional_nature in ("malefic", "maraka") and in_dusthana:
        return "challenging"
    if functional_nature == "yogakaraka" and not in_dusthana:
        return "favorable"
    if in_dusthana and functional_nature not in ("yogakaraka", "benefic"):
        return "challenging"
    return "neutral"


def analyze_transit_lordships(
    transit_positions: dict[str, dict[str, Any]],
    lagna_rashi: int,
) -> list[dict[str, Any]]:
    """Analyze lordship effects for all transiting planets.

    For each planet in transit_positions, determines what houses it lords,
    its functional nature, the house it currently transits, and interprets
    the effects using house_lord_in_house.json.

    Args:
        transit_positions: Dict mapping planet name to a dict with at least
            "longitude" (float) and "rashi_num" (int 0-11).
        lagna_rashi: Lagna rashi number (0-11).

    Returns:
        List of analysis dicts, one per planet.

    Example:
        >>> transits = {"saturn": {"longitude": 340.0, "rashi_num": 11}}
        >>> results = analyze_transit_lordships(transits, 6)
        >>> results[0]["functional_nature"]
        'yogakaraka'
    """
    results: list[dict[str, Any]] = []

    for planet_name, pos_data in transit_positions.items():
        planet_lower = planet_name.lower()
        transit_rashi = pos_data["rashi_num"]
        transit_house = get_house_from_reference(transit_rashi, lagna_rashi)

        role = classify_planet_role(planet_lower, lagna_rashi)
        houses_ruled = role["houses_ruled"]

        effects_per_house: list[dict[str, Any]] = []
        for ruled_house in houses_ruled:
            key = f"lord_{ruled_house}_in_house_{transit_house}"
            interpretation = _LORD_INTERPRETATIONS.get(key, {})

            quality = _determine_transit_quality(
                role["functional_nature"],
                transit_house,
                role["is_yogakaraka"],
            )

            effects_per_house.append(
                {
                    "ruled_house": ruled_house,
                    "themes": HOUSE_SIGNIFICATIONS.get(ruled_house, []),
                    "interpretation": interpretation,
                    "transit_quality": quality,
                }
            )

        results.append(
            {
                "planet": planet_lower,
                "transit_rashi": transit_rashi,
                "transit_house": transit_house,
                "houses_ruled": houses_ruled,
                "functional_nature": role["functional_nature"],
                "role_details": role,
                "effects_per_house": effects_per_house,
            }
        )

    return results


def get_lordship_summary(transit_lordships: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate transit lordship analysis into a human-readable summary.

    Args:
        transit_lordships: Output of analyze_transit_lordships().

    Returns:
        Dict with yogakaraka_transits, benefic_transits, malefic_transits,
        maraka_transits, dusthana_activations, favorable_count,
        unfavorable_count, and key_insight.
    """
    yogakaraka_transits: list[str] = []
    benefic_transits: list[str] = []
    malefic_transits: list[str] = []
    maraka_transits: list[str] = []
    dusthana_activations: list[int] = []
    favorable_count = 0
    unfavorable_count = 0

    for entry in transit_lordships:
        nature = entry["functional_nature"]
        planet = entry["planet"]

        if nature == "yogakaraka":
            yogakaraka_transits.append(planet)
        elif nature == "benefic":
            benefic_transits.append(planet)
        elif nature == "malefic":
            malefic_transits.append(planet)
        elif nature == "maraka":
            maraka_transits.append(planet)

        # Count favorable / unfavorable from per-house effects
        for effect in entry.get("effects_per_house", []):
            quality = effect.get("transit_quality", "neutral")
            if quality in ("excellent", "favorable"):
                favorable_count += 1
            elif quality == "challenging":
                unfavorable_count += 1

        # Track dusthana activations
        if entry.get("role_details", {}).get("is_dusthana_lord"):
            for h in entry["houses_ruled"]:
                if h in DUSTHANA_HOUSES:
                    dusthana_activations.append(h)

    # Build key insight
    if yogakaraka_transits:
        yk = yogakaraka_transits[0]
        # Find transit house for first yogakaraka
        yk_house = None
        for entry in transit_lordships:
            if entry["planet"] == yk:
                yk_house = entry["transit_house"]
                break
        key_insight = f"Yogakaraka {yk} transiting house {yk_house} — strong period for growth"
    elif unfavorable_count > favorable_count:
        houses_str = ", ".join(str(h) for h in sorted(set(dusthana_activations)))
        if houses_str:
            key_insight = f"Challenging period — dusthana lords active in houses {houses_str}"
        else:
            key_insight = "Challenging period — difficult planetary placements"
    elif favorable_count > unfavorable_count:
        benefic_houses: list[int] = []
        for entry in transit_lordships:
            if entry["functional_nature"] in ("benefic", "yogakaraka"):
                benefic_houses.extend(entry["houses_ruled"])
        houses_str = ", ".join(str(h) for h in sorted(set(benefic_houses)))
        key_insight = f"Favorable period — benefic lords supporting houses {houses_str}"
    else:
        key_insight = "Mixed period with balanced planetary influences"

    return {
        "yogakaraka_transits": yogakaraka_transits,
        "benefic_transits": benefic_transits,
        "malefic_transits": malefic_transits,
        "maraka_transits": maraka_transits,
        "dusthana_activations": sorted(set(dusthana_activations)),
        "favorable_count": favorable_count,
        "unfavorable_count": unfavorable_count,
        "key_insight": key_insight,
    }
