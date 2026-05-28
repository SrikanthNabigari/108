"""Divisional charts (Varga) for Vedic astrology.

This module provides calculations for all 60 divisional charts used in Vedic astrology.
Divisional charts divide the zodiacal signs into smaller portions, each representing
different life areas and karmic influences.

Key divisional charts:
- D1 (Rashi): Birth chart
- D2 (Hora): Wealth and prosperity
- D3 (Drekkana): Siblings and courage
- D4 (Chaturthamsha): Vehicles and property
- D7 (Saptamsha): Children
- D9 (Navamsha): Marriage, dharma, soul purpose - MOST IMPORTANT
- D10 (Dashamsha): Career and reputation
- D12 (Dwadashamsha): Parents
- D16 (Shodashamsha): Vehicles and comforts
- D20 (Vimshamsha): Spiritual progress
- D24 (Chaturvimshamsha): Education
- D27 (Bhamsha): Strength and longevity
- D30 (Trimshamsha): Misfortunes and ailments
- D40 (Khavedamsha): Auspicious/inauspicious effects
- D45 (Akshavedamsha): General indications
- D60 (Shashtiamsha): Past life karma

All calculations use the sidereal zodiac (0-360°).
Rashis (signs) are numbered 0-11:
    0=Aries, 1=Taurus, 2=Gemini, 3=Cancer, 4=Leo, 5=Virgo,
    6=Libra, 7=Scorpio, 8=Sagittarius, 9=Capricorn, 10=Aquarius, 11=Pisces

Elements:
    Fire: Aries(0), Leo(4), Sagittarius(8)
    Earth: Taurus(1), Virgo(5), Capricorn(9)
    Air: Gemini(2), Libra(6), Aquarius(10)
    Water: Cancer(3), Scorpio(7), Pisces(11)
"""

import json
from pathlib import Path
from typing import TypedDict


# Type definitions
class DivisionalPosition(TypedDict):
    """Position of a planet in a divisional chart."""

    rashi: int  # 0-11 (zodiacal sign)
    rashi_name: str
    degree_in_sign: float
    division: int
    subdivisional_degree: float


class DivisionalChart(TypedDict):
    """Complete divisional chart for all planets."""

    division: int
    division_name: str
    positions: dict[str, DivisionalPosition]


class VargaStrength(TypedDict):
    """Strength of a planet across multiple vargas (divisional charts)."""

    planet: str
    total_strength: float
    strength_per_varga: dict[int, float]
    well_placed_vargas: list[int]
    badly_placed_vargas: list[int]


# Constants
RASHI_NAMES = [
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

ELEMENT_MAP = {
    0: "fire",  # Aries
    1: "earth",  # Taurus
    2: "air",  # Gemini
    3: "water",  # Cancer
    4: "fire",  # Leo
    5: "earth",  # Virgo
    6: "air",  # Libra
    7: "water",  # Scorpio
    8: "fire",  # Sagittarius
    9: "earth",  # Capricorn
    10: "air",  # Aquarius
    11: "water",  # Pisces
}

DIVISIONAL_NAMES = {
    1: "Rashi",
    2: "Hora",
    3: "Drekkana",
    4: "Chaturthamsha",
    5: "Panchamsha",
    6: "Shashthamsha",
    7: "Saptamsha",
    8: "Ashtamsha",
    9: "Navamsha",
    10: "Dashamsha",
    12: "Dwadashamsha",
    16: "Shodashamsha",
    20: "Vimshamsha",
    24: "Chaturvimshamsha",
    27: "Bhamsha",
    30: "Trimshamsha",
    40: "Khavedamsha",
    45: "Akshavedamsha",
    60: "Shashtiamsha",
    150: "Nadi Amsha",
}


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360° range.

    Args:
        longitude: Longitude in degrees

    Returns:
        float: Normalized longitude (0-360°)
    """
    return longitude % 360.0


def _get_rashi_from_longitude(longitude: float) -> int:
    """Get rashi (sign) number from longitude (0-11).

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        int: Rashi number (0-11)
    """
    return int((longitude % 360.0) / 30)


def _get_degree_in_sign(longitude: float) -> float:
    """Get degree within a sign (0-30°).

    Args:
        longitude: Longitude in degrees

    Returns:
        float: Degree within sign (0-30°)
    """
    return longitude % 30


def _get_element(rashi: int) -> str:
    """Get element of a rashi.

    Args:
        rashi: Rashi number (0-11)

    Returns:
        str: Element name ("fire", "earth", "air", or "water")
    """
    return ELEMENT_MAP.get(rashi, "unknown")


def get_d1_position(longitude: float) -> DivisionalPosition:
    """Get D1 (Rashi) position from longitude.

    D1 is the birth chart - the main divisional chart.
    Simply divides the zodiac into 12 signs of 30° each.

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Rashi chart

    Example:
        >>> pos = get_d1_position(65.5)
        >>> pos['rashi']  # 2 (Gemini)
        >>> pos['degree_in_sign']  # 5.5
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    return DivisionalPosition(
        rashi=rashi,
        rashi_name=RASHI_NAMES[rashi],
        degree_in_sign=degree,
        division=1,
        subdivisional_degree=degree,
    )


def get_hora(longitude: float) -> DivisionalPosition:
    """Get D2 (Hora) position from longitude.

    Hora chart divides each sign into 2 parts of 15° each.
    Represents wealth and prosperity.

    Rules:
    - Odd signs: 0-15° = Leo, 15-30° = Cancer
    - Even signs: 0-15° = Cancer, 15-30° = Leo

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Hora chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Determine which half (0 or 1)
    hora_half = 0 if degree < 15 else 1

    # Calculate resulting rashi
    # Even signs: Leo (4) then Cancer (3); Odd signs: Cancer (3) then Leo (4)
    if rashi % 2 == 0:  # noqa: SIM108
        result_rashi = 4 if hora_half == 0 else 3
    else:
        result_rashi = 3 if hora_half == 0 else 4

    # Degree within the resulting sign
    subdivisional_degree = degree % 15

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=2,
        subdivisional_degree=subdivisional_degree,
    )


def get_drekkana(longitude: float) -> DivisionalPosition:
    """Get D3 (Drekkana) position from longitude.

    Drekkana chart divides each sign into 3 parts of 10° each.
    Represents siblings and courage.

    Rules:
    - 1st drekkana (0-10°): Same sign
    - 2nd drekkana (10-20°): 5th from sign
    - 3rd drekkana (20-30°): 9th from sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Drekkana chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Determine which drekkana (0, 1, or 2)
    drekkana_num = int(degree / 10)

    # Calculate resulting rashi based on drekkana
    if drekkana_num == 0:
        result_rashi = rashi
    elif drekkana_num == 1:
        result_rashi = (rashi + 5) % 12
    else:  # drekkana_num == 2
        result_rashi = (rashi + 9) % 12

    subdivisional_degree = degree % 10

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=3,
        subdivisional_degree=subdivisional_degree,
    )


def get_chaturthamsha(longitude: float) -> DivisionalPosition:
    """Get D4 (Chaturthamsha) position from longitude.

    Chaturthamsha chart divides each sign into 4 parts of 7°30' each.
    Represents vehicles and property.

    Rules:
    - Odd signs: Start from same sign
    - Even signs: Start from 7th sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Chaturthamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each chaturthamsha is 7.5°
    chaturthamsha_num = int(degree / 7.5)

    # Calculate resulting rashi
    if (rashi % 2) == 0:  # Even sign
        # Even signs start from 7th sign
        result_rashi = (rashi + 7 + chaturthamsha_num) % 12
    else:  # Odd sign
        # Odd signs start from same sign
        result_rashi = (rashi + chaturthamsha_num) % 12

    subdivisional_degree = degree % 7.5

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=4,
        subdivisional_degree=subdivisional_degree,
    )


def get_saptamsha(longitude: float) -> DivisionalPosition:
    """Get D7 (Saptamsha) position from longitude.

    Saptamsha chart divides each sign into 7 parts of ~4°17'8.57" each.
    Represents children and progeny.

    Rules:
    - Odd signs: Start from same sign
    - Even signs: Start from 7th sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Saptamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each saptamsha is 30/7 degrees
    saptamsha_size = 30 / 7  # ~4.286°
    saptamsha_num = int(degree / saptamsha_size)

    # Calculate resulting rashi
    if (rashi % 2) == 0:  # Even sign
        # Even signs start from 7th sign
        result_rashi = (rashi + 7 + saptamsha_num) % 12
    else:  # Odd sign
        # Odd signs start from same sign
        result_rashi = (rashi + saptamsha_num) % 12

    subdivisional_degree = degree % saptamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=7,
        subdivisional_degree=subdivisional_degree,
    )


def get_navamsha(longitude: float) -> DivisionalPosition:
    """Get D9 (Navamsha) position from longitude.

    Navamsha chart divides each sign into 9 parts of 3°20' each.
    THE MOST IMPORTANT divisional chart in Vedic astrology!
    Represents marriage, dharma, and soul's ultimate purpose.

    Rules based on element:
    - Fire signs (Aries, Leo, Sag): Start from Aries (0)
    - Earth signs (Taurus, Virgo, Cap): Start from Capricorn (9)
    - Air signs (Gemini, Libra, Aqua): Start from Libra (6)
    - Water signs (Cancer, Scorp, Pisces): Start from Cancer (3)

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Navamsha chart

    Example:
        >>> pos = get_navamsha(125.0)  # Leo 5°
        >>> pos['rashi']  # Should be in fire sign sequence
        >>> pos['division']  # 9
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each navamsha is 30/9 = 3°20' (3.333°)
    navamsha_size = 30 / 9
    navamsha_num = int(degree / navamsha_size)  # 0-8

    # Get element of the sign
    element = _get_element(rashi)

    # Determine starting rashi based on element
    if element == "fire":
        # Fire signs start from Aries (0)
        result_rashi = (0 + navamsha_num) % 12
    elif element == "earth":
        # Earth signs start from Capricorn (9)
        result_rashi = (9 + navamsha_num) % 12
    elif element == "air":
        # Air signs start from Libra (6)
        result_rashi = (6 + navamsha_num) % 12
    elif element == "water":
        # Water signs start from Cancer (3)
        result_rashi = (3 + navamsha_num) % 12
    else:
        result_rashi = rashi

    subdivisional_degree = degree % navamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=9,
        subdivisional_degree=subdivisional_degree,
    )


def get_dashamsha(longitude: float) -> DivisionalPosition:
    """Get D10 (Dashamsha) position from longitude.

    Dashamsha chart divides each sign into 10 parts of 3° each.
    Represents career, profession, and reputation.

    Rules:
    - Odd signs: Start from same sign
    - Even signs: Start from 9th sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Dashamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each dashamsha is 3°
    dashamsha_num = int(degree / 3)

    # Calculate resulting rashi
    if (rashi % 2) == 0:  # Even sign
        # Even signs start from 9th sign
        result_rashi = (rashi + 9 + dashamsha_num) % 12
    else:  # Odd sign
        # Odd signs start from same sign
        result_rashi = (rashi + dashamsha_num) % 12

    subdivisional_degree = degree % 3

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=10,
        subdivisional_degree=subdivisional_degree,
    )


def get_dwadashamsha(longitude: float) -> DivisionalPosition:
    """Get D12 (Dwadashamsha) position from longitude.

    Dwadashamsha chart divides each sign into 12 parts of 2°30' each.
    Represents parents and ancestral influences.

    Rules:
    - Always start from same sign and progress through all 12 rashis

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Dwadashamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each dwadashamsha is 2.5°
    dwadashamsha_num = int(degree / 2.5)

    # Always start from the same sign
    result_rashi = (rashi + dwadashamsha_num) % 12

    subdivisional_degree = degree % 2.5

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=12,
        subdivisional_degree=subdivisional_degree,
    )


def get_shodashamsha(longitude: float) -> DivisionalPosition:
    """Get D16 (Shodashamsha) position from longitude.

    Shodashamsha chart divides each sign into 16 parts of 1°52'30" each.
    Represents vehicles and physical comforts.

    Rules:
    - Odd signs: Start from same sign
    - Even signs: Start from 9th sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Shodashamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each shodashamsha is 30/16 = 1.875°
    shodashamsha_size = 30 / 16
    shodashamsha_num = int(degree / shodashamsha_size)

    # Calculate resulting rashi
    if (rashi % 2) == 0:  # Even sign
        # Even signs start from 9th sign
        result_rashi = (rashi + 9 + shodashamsha_num) % 12
    else:  # Odd sign
        # Odd signs start from same sign
        result_rashi = (rashi + shodashamsha_num) % 12

    subdivisional_degree = degree % shodashamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=16,
        subdivisional_degree=subdivisional_degree,
    )


def get_vimshamsha(longitude: float) -> DivisionalPosition:
    """Get D20 (Vimshamsha) position from longitude.

    Vimshamsha chart divides each sign into 20 parts of 1°30' each.
    Represents spiritual progress and divine grace.

    Rules:
    - Each sign always starts from the same sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Vimshamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each vimshamsha is 1.5°
    vimshamsha_size = 30 / 20
    vimshamsha_num = int(degree / vimshamsha_size)

    result_rashi = (rashi + vimshamsha_num) % 12

    subdivisional_degree = degree % vimshamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=20,
        subdivisional_degree=subdivisional_degree,
    )


def get_chaturvimshamsha(longitude: float) -> DivisionalPosition:
    """Get D24 (Chaturvimshamsha) position from longitude.

    Chaturvimshamsha chart divides each sign into 24 parts of 1°15' each.
    Represents education and learning abilities.

    Rules:
    - Each sign starts from the same sign

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Chaturvimshamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each chaturvimshamsha is 1.25°
    chaturvimshamsha_size = 30 / 24
    chaturvimshamsha_num = int(degree / chaturvimshamsha_size)

    result_rashi = (rashi + chaturvimshamsha_num) % 12

    subdivisional_degree = degree % chaturvimshamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=24,
        subdivisional_degree=subdivisional_degree,
    )


def get_bhamsha(longitude: float) -> DivisionalPosition:
    """Get D27 (Bhamsha/Nakshatramsha) position from longitude.

    Bhamsha chart divides each sign into 27 parts of ~1°6'40" each.
    Represents strength, health, and longevity.

    Note: 27 divisions align with the 27 nakshatras.
    Each sign starts from the same sign.

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Bhamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each bhamsha is 30/27 degrees
    bhamsha_size = 30 / 27
    bhamsha_num = int(degree / bhamsha_size)

    result_rashi = (rashi + bhamsha_num) % 12

    subdivisional_degree = degree % bhamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=27,
        subdivisional_degree=subdivisional_degree,
    )


def get_trimshamsha(longitude: float) -> DivisionalPosition:
    """Get D30 (Trimshamsha) position from longitude.

    Trimshamsha chart divides each sign into 30 parts of 1° each.
    Represents misfortunes, ailments, and challenges.

    Special rules - NOT equal divisions:
    - For odd signs: 5°(Mars), 5°(Venus), 8°(Mercury), 7°(Moon), 5°(Sun)
    - For even signs: 5°(Sun), 5°(Mercury), 8°(Venus), 7°(Mars), 5°(Moon)

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Trimshamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Define boundaries for odd and even signs
    if (rashi % 2) == 0:  # Even sign
        # Even: Sun(5), Mercury(5), Venus(8), Mars(7), Moon(5)
        boundaries = [
            (0, 5, 0),  # Sun
            (5, 10, 1),  # Mercury
            (10, 18, 2),  # Venus
            (18, 25, 4),  # Mars
            (25, 30, 3),  # Moon
        ]
    else:  # Odd sign
        # Odd: Mars(5), Venus(5), Mercury(8), Moon(7), Sun(5)
        boundaries = [
            (0, 5, 4),  # Mars
            (5, 10, 2),  # Venus
            (10, 18, 1),  # Mercury
            (18, 25, 3),  # Moon
            (25, 30, 0),  # Sun
        ]

    # Find which section the degree falls in
    planet_num = 0  # Default
    for start, end, planet in boundaries:
        if start <= degree < end:
            planet_num = planet
            break

    # Planet rulers: 0=Sun, 1=Mercury, 2=Venus, 3=Moon, 4=Mars
    planet_rulers = [0, 1, 2, 3, 4]  # Rashi numbers of planet exaltations
    result_rashi = (rashi + planet_rulers[planet_num]) % 12

    subdivisional_degree = degree % 1

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=30,
        subdivisional_degree=subdivisional_degree,
    )


def get_khavedamsha(longitude: float) -> DivisionalPosition:
    """Get D40 (Khavedamsha) position from longitude.

    Khavedamsha chart divides each sign into 40 parts of 0°45' each.
    Represents auspicious and inauspicious effects.

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Khavedamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each khavedamsha is 30/40 = 0.75°
    khavedamsha_size = 30 / 40
    khavedamsha_num = int(degree / khavedamsha_size)

    result_rashi = (rashi + khavedamsha_num) % 12

    subdivisional_degree = degree % khavedamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=40,
        subdivisional_degree=subdivisional_degree,
    )


def get_akshavedamsha(longitude: float) -> DivisionalPosition:
    """Get D45 (Akshavedamsha) position from longitude.

    Akshavedamsha chart divides each sign into 45 parts of 40' each.
    Represents general indications and overall character.

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Akshavedamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each akshavedamsha is 30/45 = 2/3 degree
    akshavedamsha_size = 30 / 45
    akshavedamsha_num = int(degree / akshavedamsha_size)

    result_rashi = (rashi + akshavedamsha_num) % 12

    subdivisional_degree = degree % akshavedamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=45,
        subdivisional_degree=subdivisional_degree,
    )


def get_shashtiamsha(longitude: float) -> DivisionalPosition:
    """Get D60 (Shashtiamsha) position from longitude.

    Shashtiamsha chart divides each sign into 60 parts of 0°30' each.
    Represents past life karma and very subtle effects.

    The most fine-grained divisional chart.

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Shashtiamsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = _get_rashi_from_longitude(longitude)
    degree = _get_degree_in_sign(longitude)

    # Each shashtiamsha is 0.5°
    shashtiamsha_size = 30 / 60
    shashtiamsha_num = int(degree / shashtiamsha_size)

    result_rashi = (rashi + shashtiamsha_num) % 12

    subdivisional_degree = degree % shashtiamsha_size

    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=60,
        subdivisional_degree=subdivisional_degree,
    )


def get_nadi_amsha(longitude: float) -> DivisionalPosition:
    """D-150: Nadi Amsha — each sign divided into 150 parts of 0.2° each.

    Used in Nadi Jyotish for precise karmic detail and KP sublord analysis.
    At this resolution, 1-minute birth time error = ~0.17° = ~0.85 amshas shift.

    Args:
        longitude: Longitude in degrees (0-360°)

    Returns:
        DivisionalPosition: Position in Nadi Amsha chart
    """
    longitude = _normalize_longitude(longitude)
    rashi = int(longitude / 30)
    degree = longitude % 30
    amsha_num = int(degree / 0.2)  # 0-149
    result_rashi = (rashi * 150 + amsha_num) % 12
    subdivisional_degree = degree % 0.2
    return DivisionalPosition(
        rashi=result_rashi,
        rashi_name=RASHI_NAMES[result_rashi],
        degree_in_sign=subdivisional_degree,
        division=150,
        subdivisional_degree=subdivisional_degree,
    )


def get_nadi_type_from_amsha(amsha_num: int) -> str:
    """Returns Adi, Madhya, or Antya based on D-150 amsha number (0-149).

    Args:
        amsha_num: Amsha number from 0 to 149

    Returns:
        str: Nadi type - "Adi", "Madhya", or "Antya"
    """
    if amsha_num < 50:
        return "Adi"
    elif amsha_num < 100:
        return "Madhya"
    else:
        return "Antya"


def get_divisional_position(longitude: float, division: int) -> DivisionalPosition:
    """Get divisional chart position for any D1-D60 chart.

    Dispatcher function that routes to the appropriate divisional chart
    calculator based on the division number.

    Args:
        longitude: Longitude in degrees (0-360°)
        division: Division number (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60, 150)

    Returns:
        DivisionalPosition: Position in the requested divisional chart

    Raises:
        ValueError: If division is not supported

    Example:
        >>> pos = get_divisional_position(125.5, 9)  # D9 (Navamsha)
        >>> pos['division']  # 9
    """
    division_map = {
        1: get_d1_position,
        2: get_hora,
        3: get_drekkana,
        4: get_chaturthamsha,
        7: get_saptamsha,
        9: get_navamsha,
        10: get_dashamsha,
        12: get_dwadashamsha,
        16: get_shodashamsha,
        20: get_vimshamsha,
        24: get_chaturvimshamsha,
        27: get_bhamsha,
        30: get_trimshamsha,
        40: get_khavedamsha,
        45: get_akshavedamsha,
        60: get_shashtiamsha,
        150: get_nadi_amsha,
    }

    if division not in division_map:
        raise ValueError(
            f"Unsupported division: {division}. Supported divisions: {sorted(division_map.keys())}"
        )

    return division_map[division](longitude)


def get_divisional_chart(planets: dict[str, float], division: int) -> DivisionalChart:
    """Get complete divisional chart for all planets.

    Calculates divisional positions for all provided planets in a single
    divisional chart.

    Args:
        planets: Dictionary mapping planet names to longitudes in degrees
                 Example: {"sun": 125.5, "moon": 215.3, "mars": 45.2}
        division: Division number (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60, 150)

    Returns:
        DivisionalChart: Complete chart with positions for all planets

    Raises:
        ValueError: If division is not supported

    Example:
        >>> planets = {
        ...     "sun": 125.5,
        ...     "moon": 215.3,
        ...     "mars": 45.2,
        ...     "mercury": 130.0,
        ...     "jupiter": 250.0,
        ...     "venus": 100.0,
        ...     "saturn": 320.0
        ... }
        >>> chart = get_divisional_chart(planets, 9)  # D9 (Navamsha)
        >>> chart['division']  # 9
        >>> chart['positions']['sun']['rashi']  # Sun's navamsha rashi
    """
    positions = {}
    for planet_name, longitude in planets.items():
        positions[planet_name] = get_divisional_position(longitude, division)

    division_name = DIVISIONAL_NAMES.get(division, f"D{division}")

    return DivisionalChart(
        division=division,
        division_name=division_name,
        positions=positions,
    )


def get_varga_vimshopaka(
    planets: dict[str, float], divisions: list[int] | None = None
) -> dict[str, VargaStrength]:
    """Calculate Varga Vimshopaka (strength from multiple vargas).

    Varga Vimshopaka measures how well-placed a planet is across multiple
    divisional charts. A planet is "well-placed" if it's in a sign where it
    has natural strength (exaltation, own sign, etc.) or good aspect.

    This provides a composite strength score for each planet across the
    specified divisions.

    Args:
        planets: Dictionary mapping planet names to longitudes
        divisions: List of division numbers to consider. If None, uses
                   the 16 main divisions: [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]

    Returns:
        Dictionary mapping planet names to VargaStrength objects containing:
        - total_strength: Sum of strength across all vargas (0-100 scale)
        - strength_per_varga: Dictionary of strength for each division
        - well_placed_vargas: List of divisions where planet is well-placed
        - badly_placed_vargas: List of divisions where planet is badly-placed

    Example:
        >>> planets = {"sun": 125.5, "moon": 215.3, "mars": 45.2}
        >>> strength = get_varga_vimshopaka(planets)
        >>> strength['sun']['total_strength']  # Overall strength
        >>> strength['sun']['well_placed_vargas']  # Which vargas favor the sun
    """
    if divisions is None:
        divisions = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]

    result = {}

    for planet_name, longitude in planets.items():
        strength_per_varga = {}
        well_placed = []
        badly_placed = []

        for division in divisions:
            pos = get_divisional_position(longitude, division)
            rashi = pos["rashi"]

            # Simple heuristic: check if planet is in its natural sign
            # This is a simplified calculation; real Jyotish uses more complex rules
            planet_index = _get_planet_index(planet_name)
            exaltation_rashi = _get_exaltation_rashi(planet_name)

            # Calculate strength (0-100)
            # Strong if in own sign or exaltation
            if rashi in (planet_index, exaltation_rashi):
                strength = 100
                well_placed.append(division)
            # Weak if in detriment (7th from exaltation)
            elif rashi == (exaltation_rashi + 6) % 12:
                strength = 20
                badly_placed.append(division)
            else:
                # Average strength in other signs
                strength = 50

            strength_per_varga[division] = strength

        # Calculate total strength (average across all divisions)
        total_strength = sum(strength_per_varga.values()) / len(divisions)

        result[planet_name] = VargaStrength(
            planet=planet_name,
            total_strength=round(total_strength, 2),
            strength_per_varga=strength_per_varga,
            well_placed_vargas=well_placed,
            badly_placed_vargas=badly_placed,
        )

    return result


def _get_planet_index(planet_name: str) -> int:
    """Get the primary rashi (sign) index for a planet.

    Returns the sign where the planet naturally rules or is exalted.

    Args:
        planet_name: Planet name (lowercase)

    Returns:
        int: Rashi number (0-11)
    """
    planet_rashis = {
        "sun": 4,  # Leo (own sign)
        "moon": 3,  # Cancer (own sign)
        "mars": 0,  # Aries (own sign)
        "mercury": 2,  # Gemini (own sign)
        "jupiter": 8,  # Sagittarius (own sign)
        "venus": 1,  # Taurus (own sign)
        "saturn": 9,  # Capricorn (own sign)
        "rahu": 10,  # Aquarius (co-ruler by tradition)
        "ketu": 7,  # Scorpio (co-ruler by tradition)
    }
    return planet_rashis.get(planet_name.lower(), 0)


def _get_exaltation_rashi(planet_name: str) -> int:
    """Get the exaltation rashi (sign) for a planet.

    Args:
        planet_name: Planet name (lowercase)

    Returns:
        int: Rashi number (0-11)
    """
    exaltations = {
        "sun": 0,  # Aries
        "moon": 1,  # Taurus
        "mars": 9,  # Capricorn
        "mercury": 5,  # Virgo
        "jupiter": 3,  # Cancer
        "venus": 11,  # Pisces
        "saturn": 6,  # Libra
        "rahu": 1,  # Taurus
        "ketu": 7,  # Scorpio
    }
    return exaltations.get(planet_name.lower(), 0)


# Sign lords mapping
SIGN_LORDS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


# Dignity scoring constants
DIGNITY_SCORES = {
    "exalted": 20,
    "moolatrikona": 18,
    "own": 15,
    "friend": 10,
    "neutral": 5,
    "enemy": 2,
    "debilitated": 0,
}


# Varga scheme definitions
VARGA_SCHEMES = {
    "shad_varga": [1, 2, 3, 9, 12, 30],
    "sapta_varga": [1, 2, 3, 7, 9, 12, 30],
    "dasha_varga": [1, 2, 3, 4, 7, 9, 10, 12, 16, 30],
    "shodasha_varga": [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60],
}


def _load_dignities() -> dict:
    """Load dignities data from knowledge file.

    Returns:
        dict: Complete dignities data including planets and friendship table
    """
    dignities_path = (
        Path(__file__).parent.parent.parent.parent / "knowledge" / "definitions" / "dignities.json"
    )
    with dignities_path.open() as f:
        return json.load(f)


def _load_friendship_table() -> dict:
    """Load friendship table from dignities.json.

    Returns:
        dict: Friendship relationships for all planets
    """
    data = _load_dignities()
    return data.get("friendship_table", {})


def get_planet_dignity_in_sign(planet: str, rashi_name: str) -> str:
    """Determine a planet's dignity in a specific sign.

    Uses dignities.json data and friendship table to determine the
    relationship between a planet and the sign it occupies.

    Args:
        planet: Planet name (lowercase: sun, moon, mars, etc.)
        rashi_name: Sign name (lowercase: aries, taurus, etc.)

    Returns:
        str: Dignity level ("exalted", "moolatrikona", "own", "friend", "neutral", "enemy", "debilitated")

    Example:
        >>> get_planet_dignity_in_sign("sun", "aries")
        "exalted"
        >>> get_planet_dignity_in_sign("sun", "libra")
        "debilitated"
    """
    # Load dignities data
    dignities_data = _load_dignities()
    planet_lower = planet.lower()
    rashi_lower = rashi_name.lower()

    # Get planet data
    if planet_lower not in dignities_data["planets"]:
        return "neutral"

    planet_data = dignities_data["planets"][planet_lower]

    # Check exaltation
    if planet_data.get("exaltation") and planet_data["exaltation"]["sign"] == rashi_lower:
        return "exalted"

    # Check debilitation
    if planet_data.get("debilitation") and planet_data["debilitation"]["sign"] == rashi_lower:
        return "debilitated"

    # Check moolatrikona (just check sign match, not degree range)
    if planet_data.get("moolatrikona") and planet_data["moolatrikona"]["sign"] == rashi_lower:
        return "moolatrikona"

    # Check own sign
    if rashi_lower in planet_data.get("own_signs", []):
        return "own"

    # Check friendship with sign lord
    friendship_table = _load_friendship_table()
    sign_lord = SIGN_LORDS.get(rashi_lower)

    if sign_lord and planet_lower in friendship_table:
        planet_relationships = friendship_table[planet_lower]

        if sign_lord in planet_relationships.get("friends", []):
            return "friend"
        elif sign_lord in planet_relationships.get("enemies", []):
            return "enemy"
        elif sign_lord in planet_relationships.get("neutrals", []):
            return "neutral"

    # Default to neutral
    return "neutral"


def calculate_vimshopaka_bala(planet: str, longitude: float, scheme: str = "shad_varga") -> dict:
    """Calculate Vimshopaka Bala (divisional strength) for a planet.

    Proper Vimshopaka calculation using dignity lookup per varga chart.
    Evaluates a planet's strength across multiple divisional charts.

    Args:
        planet: Planet name (lowercase)
        longitude: Planet's longitude in degrees (0-360)
        scheme: Varga scheme to use ("shad_varga", "sapta_varga", "dasha_varga", "shodasha_varga")

    Returns:
        dict: Contains:
            - total_points (int): Sum of dignity scores across all vargas
            - max_points (int): Maximum possible points
            - percentage (float): Strength percentage (0-100)
            - category (str): Strength category
            - varga_details (list): Details for each varga

    Example:
        >>> result = calculate_vimshopaka_bala("sun", 125.5, "shad_varga")
        >>> result['percentage']  # 75.5
        >>> result['category']  # "excellent"
    """
    # Get divisions for the scheme
    if scheme not in VARGA_SCHEMES:
        raise ValueError(f"Unknown scheme: {scheme}. Available: {list(VARGA_SCHEMES.keys())}")

    divisions = VARGA_SCHEMES[scheme]
    varga_details = []
    total_points = 0

    # Calculate dignity score for each varga
    for division in divisions:
        # Get planet's position in this divisional chart
        position = get_divisional_position(longitude, division)
        rashi_name = position["rashi_name"].lower()

        # Get dignity in this sign
        dignity = get_planet_dignity_in_sign(planet, rashi_name)

        # Get score for this dignity
        score = DIGNITY_SCORES.get(dignity, 5)

        varga_details.append(
            {
                "division": division,
                "rashi": position["rashi_name"],
                "dignity": dignity,
                "score": score,
            }
        )

        total_points += score

    # Calculate percentage and category
    max_points = len(divisions) * 20
    percentage = (total_points / max_points) * 100

    if percentage > 75:
        category = "excellent"
    elif percentage > 60:
        category = "good"
    elif percentage > 40:
        category = "moderate"
    elif percentage > 25:
        category = "weak"
    else:
        category = "very_weak"

    return {
        "total_points": total_points,
        "max_points": max_points,
        "percentage": round(percentage, 2),
        "category": category,
        "varga_details": varga_details,
    }


def get_all_vimshopaka(planets: dict[str, float], scheme: str = "shad_varga") -> dict[str, dict]:
    """Calculate Vimshopaka Bala for all planets.

    Args:
        planets: Dictionary mapping planet names to longitudes
        scheme: Varga scheme to use (default: "shad_varga")

    Returns:
        dict: Dictionary mapping planet names to their vimshopaka results

    Example:
        >>> planets = {"sun": 125.5, "moon": 215.3, "mars": 45.2}
        >>> results = get_all_vimshopaka(planets, "shad_varga")
        >>> results['sun']['percentage']
    """
    result = {}
    for planet_name, longitude in planets.items():
        result[planet_name] = calculate_vimshopaka_bala(planet_name, longitude, scheme)
    return result


__all__ = [
    "DIGNITY_SCORES",
    "DIVISIONAL_NAMES",
    "ELEMENT_MAP",
    # Constants
    "RASHI_NAMES",
    "SIGN_LORDS",
    "VARGA_SCHEMES",
    "DivisionalChart",
    # Type definitions
    "DivisionalPosition",
    "VargaStrength",
    "calculate_vimshopaka_bala",
    "get_akshavedamsha",
    "get_all_vimshopaka",
    "get_bhamsha",
    "get_chaturthamsha",
    "get_chaturvimshamsha",
    # Core divisional position functions
    "get_d1_position",
    "get_dashamsha",
    "get_divisional_chart",
    # Dispatcher functions
    "get_divisional_position",
    "get_drekkana",
    "get_dwadashamsha",
    "get_hora",
    "get_khavedamsha",
    "get_nadi_amsha",
    "get_nadi_type_from_amsha",
    "get_navamsha",
    "get_planet_dignity_in_sign",
    "get_saptamsha",
    "get_shashtiamsha",
    "get_shodashamsha",
    "get_trimshamsha",
    "get_varga_vimshopaka",
    "get_vimshamsha",
]
