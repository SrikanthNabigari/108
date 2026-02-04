"""Utility functions for 108 core package."""
from typing import List, Tuple

from .constants import NAKSHATRA_SPAN, PADA_SPAN, Planet, Rashi


def normalize_degrees(degrees: float) -> float:
    """
    Normalize degrees to 0-360 range.

    Args:
        degrees: Raw degree value (can be any number)

    Returns:
        Normalized degree value between 0 and 360
    """
    degrees = degrees % 360
    return degrees if degrees >= 0 else degrees + 360


def longitude_to_rashi(longitude: float) -> Tuple[Rashi, float]:
    """
    Convert ecliptic longitude to rashi and degree within rashi.

    Args:
        longitude: Ecliptic longitude (0-360)

    Returns:
        Tuple of (rashi, degree_within_rashi)
        - rashi: Zodiac sign
        - degree_within_rashi: Degree within that rashi (0-30)
    """
    longitude = normalize_degrees(longitude)
    rashi_num = int(longitude / 30)
    rashi_degree = longitude % 30
    rashis = list(Rashi)
    return rashis[rashi_num], rashi_degree


def longitude_to_nakshatra(longitude: float) -> Tuple[int, int, float]:
    """
    Convert ecliptic longitude to nakshatra (lunar mansion).

    Args:
        longitude: Ecliptic longitude (0-360)

    Returns:
        Tuple of (nakshatra_number, pada, degree_in_nakshatra)
        - nakshatra_number: 1-27
        - pada: 1-4 (quarter within nakshatra)
        - degree_in_nakshatra: Degree within the nakshatra (0-13.333...)
    """
    longitude = normalize_degrees(longitude)
    nakshatra_num = int(longitude / NAKSHATRA_SPAN) + 1
    degree_in_nakshatra = longitude % NAKSHATRA_SPAN
    pada = int(degree_in_nakshatra / PADA_SPAN) + 1
    # Ensure pada is between 1 and 4
    pada = min(pada, 4)
    return nakshatra_num, pada, degree_in_nakshatra


def get_house_from_signs(planet_rashi: Rashi, lagna_rashi: Rashi) -> int:
    """
    Calculate house number from planet's rashi relative to lagna.

    This uses the whole sign house system where each rashi corresponds to a house.

    Args:
        planet_rashi: The rashi where the planet is located
        lagna_rashi: The rashi of the ascendant (Lagna)

    Returns:
        House number (1-12)
    """
    planet_num = list(Rashi).index(planet_rashi) + 1
    lagna_num = list(Rashi).index(lagna_rashi) + 1
    house = ((planet_num - lagna_num) % 12) + 1
    return house if house > 0 else 12


def is_kendra(house: int) -> bool:
    """
    Check if house is a kendra (quadrant house).

    Kendra houses: 1, 4, 7, 10

    Args:
        house: House number (1-12)

    Returns:
        True if house is a kendra, False otherwise
    """
    return house in [1, 4, 7, 10]


def is_trikona(house: int) -> bool:
    """
    Check if house is a trikona (triangle house).

    Trikona houses: 1, 5, 9

    Args:
        house: House number (1-12)

    Returns:
        True if house is a trikona, False otherwise
    """
    return house in [1, 5, 9]


def is_dusthana(house: int) -> bool:
    """
    Check if house is a dusthana (evil/challenging house).

    Dusthana houses: 6, 8, 12

    Args:
        house: House number (1-12)

    Returns:
        True if house is a dusthana, False otherwise
    """
    return house in [6, 8, 12]


def is_upachaya(house: int) -> bool:
    """
    Check if house is an upachaya (growth house).

    Upachaya houses: 3, 6, 10, 11

    Args:
        house: House number (1-12)

    Returns:
        True if house is an upachaya, False otherwise
    """
    return house in [3, 6, 10, 11]


def get_opposite_sign(rashi: Rashi) -> Rashi:
    """
    Get the opposite sign (7th house aspect).

    Args:
        rashi: Input zodiac sign

    Returns:
        The opposite rashi
    """
    rashis = list(Rashi)
    idx = rashis.index(rashi)
    opposite_idx = (idx + 6) % 12
    return rashis[opposite_idx]


def calculate_aspect_houses(planet: Planet, house: int) -> List[int]:
    """
    Get houses aspected by a planet from its position.

    All planets aspect the 7th house. Special planets have additional aspects:
    - Mars: 4th and 8th
    - Jupiter, Rahu, Ketu: 5th and 9th
    - Saturn: 3rd and 10th

    Args:
        planet: The planet
        house: House where the planet is located (1-12)

    Returns:
        List of houses aspected (including the 7th which all planets aspect)
    """
    # All planets aspect 7th house
    aspects = [(house + 6) % 12 + 1]

    # Special aspects for specific planets
    if planet in [Planet.MARS]:
        # Mars aspects 4th and 8th from itself
        aspects.extend([
            (house + 3) % 12 + 1,  # 4th house aspect
            (house + 7) % 12 + 1,  # 8th house aspect
        ])
    elif planet in [Planet.JUPITER, Planet.RAHU, Planet.KETU]:
        # Jupiter, Rahu, Ketu aspect 5th and 9th
        aspects.extend([
            (house + 4) % 12 + 1,  # 5th house aspect
            (house + 8) % 12 + 1,  # 9th house aspect
        ])
    elif planet == Planet.SATURN:
        # Saturn aspects 3rd and 10th
        aspects.extend([
            (house + 2) % 12 + 1,  # 3rd house aspect
            (house + 9) % 12 + 1,  # 10th house aspect
        ])

    return sorted(set(aspects))
