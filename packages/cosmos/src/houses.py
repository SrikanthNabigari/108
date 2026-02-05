"""House calculations module for Vedic astrology.

This module provides comprehensive house-related calculations for Vedic astrology,
including determining which house a planet is in, house lordship, house significations,
and house classifications (Kendra, Trikona, Dusthana, etc.).

All house calculations use the sidereal/Vedic zodiac (0-360 degrees).

Key Concepts:
    - Houses are numbered 1-12, starting from the Ascendant
    - Each house has a lord (ruler), determined by which sign falls in that house
    - House significations describe the natural meanings of each house
    - Houses are categorized by their astrological properties
    - Natural significators (Karakas) show the planet naturally associated with each house
"""

from enum import Enum

# Sign rulership mapping - essential for house lordship calculations
SIGN_RULERS = {
    0: "mars",  # Aries (0-30°)
    1: "venus",  # Taurus (30-60°)
    2: "mercury",  # Gemini (60-90°)
    3: "moon",  # Cancer (90-120°)
    4: "sun",  # Leo (120-150°)
    5: "mercury",  # Virgo (150-180°)
    6: "venus",  # Libra (180-210°)
    7: "mars",  # Scorpio (210-240°)
    8: "jupiter",  # Sagittarius (240-270°)
    9: "saturn",  # Capricorn (270-300°)
    10: "saturn",  # Aquarius (300-330°)
    11: "jupiter",  # Pisces (330-360°)
}

# Alternative mapping by sign name
SIGN_NAME_TO_RULER = {
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

# Rashi names in order
RASHI_NAMES = [
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

# House significations
HOUSE_SIGNIFICATIONS = {
    1: ["self", "body", "personality", "appearance", "constitution", "temperament"],
    2: ["wealth", "family", "speech", "food", "resources", "voice"],
    3: ["siblings", "courage", "communication", "writing", "short journeys"],
    4: ["mother", "home", "happiness", "education", "vehicles", "real estate"],
    5: ["children", "intelligence", "creativity", "romance", "speculation", "past lives"],
    6: ["enemies", "disease", "debts", "service", "subordinates", "litigation"],
    7: ["marriage", "partnership", "business", "spouse", "relationships", "contracts"],
    8: ["longevity", "transformation", "occult", "inheritance", "hidden matters"],
    9: ["father", "dharma", "fortune", "philosophy", "long journeys", "higher learning"],
    10: ["career", "status", "karma", "profession", "public image", "authority"],
    11: ["gains", "friends", "aspirations", "social networks", "fulfillment", "income"],
    12: ["losses", "moksha", "foreign lands", "spirituality", "confinement", "isolation"],
}

# Natural significators (Karakas) for each house
HOUSE_KARAKAS = {
    1: "sun",  # Self, personality
    2: "jupiter",  # Wealth, family
    3: "mars",  # Courage, siblings
    4: "moon",  # Mother, home, happiness
    5: "jupiter",  # Children, intelligence
    6: "mars",  # Enemies, disease
    7: "venus",  # Marriage, partnership
    8: "mars",  # Longevity, transformation
    9: "jupiter",  # Dharma, fortune
    10: "sun",  # Career, status
    11: "jupiter",  # Gains, aspirations
    12: "saturn",  # Losses, moksha
}

# House categories
BENEFIC_HOUSES = {1, 4, 5, 7, 9, 10, 11}  # Generally auspicious
MALEFIC_HOUSES = {6, 8, 12}  # Generally difficult (Dusthana)
KENDRA_HOUSES = {1, 4, 7, 10}  # Angular houses
TRIKONA_HOUSES = {1, 5, 9}  # Trine houses (most auspicious)
DUSTHANA_HOUSES = {6, 8, 12}  # Difficult/evil houses
UPACHAYA_HOUSES = {3, 6, 10, 11}  # Houses of growth
MARAKA_HOUSES = {2, 7}  # Death-inflicting houses


class HouseCategory(Enum):
    """Enumeration of house categories."""

    KENDRA = "kendra"  # Angular
    TRIKONA = "trikona"  # Trine
    DUSTHANA = "dusthana"  # Difficult
    UPACHAYA = "upachaya"  # Growth
    MARAKA = "maraka"  # Death-inflicting
    OTHER = "other"


def get_house_for_longitude(longitude: float, cusps: list[float]) -> int:
    """Determine which house a given longitude falls into.

    Given a planetary longitude (0-360°) and a list of house cusps,
    determines which house (1-12) the longitude falls into.

    Args:
        longitude: Ecliptic longitude in degrees (0-360)
        cusps: List of 12 house cusp longitudes (0-360), typically from ephemeris.get_house_cusps()

    Returns:
        int: House number (1-12)

    Raises:
        ValueError: If house count is incorrect or parameters are invalid
        TypeError: If parameters are not numeric

    Example:
        >>> cusps = [10.0, 40.0, 70.0, 100.0, 130.0, 160.0, 190.0, 220.0, 250.0, 280.0, 310.0, 340.0]
        >>> house = get_house_for_longitude(75.0, cusps)
        >>> house
        3

    Note:
        House placement accounts for house cusp order. If a degree is between
        cusp N and cusp N+1, it falls in house N. Wrapping is handled at house 12.
    """
    if not isinstance(longitude, int | float):
        raise TypeError(f"longitude must be numeric, got {type(longitude)}")

    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    # Normalize longitude to 0-360
    longitude = float(longitude) % 360.0

    # Find which house the longitude falls into
    for house in range(1, 13):
        cusp_idx = house - 1
        next_cusp_idx = house % 12

        current_cusp = cusps[cusp_idx]
        next_cusp = cusps[next_cusp_idx]

        # Handle wrapping around 0°
        if next_cusp < current_cusp:
            # Cusps cross the 0° line
            if longitude >= current_cusp or longitude < next_cusp:
                return house
        else:
            # Normal case: current < next
            if current_cusp <= longitude < next_cusp:
                return house

    # Fallback (should rarely happen with proper input)
    return 1


def longitude_to_rashi(longitude: float) -> int:
    """Convert longitude to rashi (zodiac sign) number.

    Args:
        longitude: Ecliptic longitude in degrees (0-360)

    Returns:
        int: Rashi number (0-11), where 0=Aries, 1=Taurus, etc.

    Example:
        >>> rashi = longitude_to_rashi(45.0)
        >>> rashi
        1  # Taurus
    """
    longitude = float(longitude) % 360.0
    return int(longitude // 30)


def rashi_to_sign_name(rashi: int) -> str:
    """Convert rashi number to sign name.

    Args:
        rashi: Rashi number (0-11)

    Returns:
        str: Sign name (e.g., "aries", "taurus")

    Raises:
        ValueError: If rashi is not 0-11
    """
    if not isinstance(rashi, int) or rashi < 0 or rashi > 11:
        raise ValueError(f"Rashi must be 0-11, got {rashi}")
    return RASHI_NAMES[rashi]


def sign_name_to_rashi(sign_name: str) -> int:
    """Convert sign name to rashi number.

    Args:
        sign_name: Sign name (e.g., "aries", "leo")

    Returns:
        int: Rashi number (0-11)

    Raises:
        ValueError: If sign name is not recognized
    """
    sign_lower = sign_name.lower()
    rashi = RASHI_NAMES.index(sign_lower) if sign_lower in RASHI_NAMES else -1

    if rashi == -1:
        raise ValueError(f"Unknown sign: {sign_name}. Valid signs: {', '.join(RASHI_NAMES)}")

    return rashi


def get_house_lord(house: int, lagna_sign: int) -> str:
    """Get the lord (ruler) of a house.

    The lord of a house is the planet that rules the sign occupying that house.
    For example, if Aries (ruled by Mars) is on the 2nd house cusp,
    Mars is the 2nd house lord.

    Args:
        house: House number (1-12)
        lagna_sign: Lagna (Ascendant) rashi number (0-11)

    Returns:
        str: Planet name (e.g., "mars", "venus", "sun")

    Raises:
        ValueError: If house or lagna_sign are invalid

    Example:
        >>> lord = get_house_lord(7, 3)  # 7th house with Lagna at Cancer
        >>> lord
        'mars'  # Scorpio is on 7th house, ruled by Mars
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    if not isinstance(lagna_sign, int) or lagna_sign < 0 or lagna_sign > 11:
        raise ValueError(f"Lagna sign must be 0-11, got {lagna_sign}")

    # Calculate which sign is on the given house
    # House N is occupied by sign: (Lagna + N - 1) % 12
    house_sign_rashi = (lagna_sign + house - 1) % 12

    # Get the ruler of that sign
    return SIGN_RULERS[house_sign_rashi]


def get_house_lord_by_name(house: int, lagna_sign_name: str) -> str:
    """Get the lord of a house using sign names.

    Convenience function that accepts sign names instead of rashi numbers.

    Args:
        house: House number (1-12)
        lagna_sign_name: Lagna sign name (e.g., "aries", "leo")

    Returns:
        str: Planet name

    Raises:
        ValueError: If house or sign name are invalid
    """
    lagna_rashi = sign_name_to_rashi(lagna_sign_name)
    return get_house_lord(house, lagna_rashi)


def get_planets_in_house(planets: dict[str, float], house: int, cusps: list[float]) -> list[str]:
    """Get all planets in a specific house.

    Given a dictionary of planetary longitudes and a house number,
    returns a list of planets currently occupying that house.

    Args:
        planets: Dict mapping planet names to their longitudes (0-360)
                 Example: {"sun": 45.5, "moon": 120.3, ...}
        house: House number (1-12)
        cusps: List of 12 house cusp longitudes from ephemeris

    Returns:
        list: Planet names occupying the house (empty list if none)

    Example:
        >>> planets = {"sun": 125.0, "moon": 200.0, "mars": 180.0}
        >>> cusps = [10.0, 40.0, 70.0, 100.0, 130.0, 160.0, 190.0, 220.0, 250.0, 280.0, 310.0, 340.0]
        >>> in_house = get_planets_in_house(planets, 5, cusps)
        >>> in_house
        ['mars']
    """
    if not isinstance(planets, dict):
        raise TypeError(f"planets must be a dict, got {type(planets)}")

    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    planets_in_house = []

    for planet_name, longitude in planets.items():
        if get_house_for_longitude(longitude, cusps) == house:
            planets_in_house.append(planet_name)

    return planets_in_house


def get_house_from_reference(planet_sign: int, reference_sign: int) -> int:
    """Calculate which house a planet is in relative to a reference sign.

    Given a planet's rashi and a reference rashi (typically the Ascendant),
    calculates which house (1-12) the planet occupies from that reference.

    Args:
        planet_sign: Planet's rashi number (0-11)
        reference_sign: Reference rashi number, typically Lagna (0-11)

    Returns:
        int: House number (1-12) relative to the reference sign

    Example:
        >>> # Sun in Gemini (2), Lagna in Aries (0)
        >>> house = get_house_from_reference(2, 0)
        >>> house
        3  # Sun is in 3rd house from Lagna

    Note:
        This calculation is sign-based and doesn't account for exact degrees
        or house cusps. It's suitable for whole sign house systems or rough estimates.
    """
    if not isinstance(planet_sign, int) or planet_sign < 0 or planet_sign > 11:
        raise ValueError(f"planet_sign must be 0-11, got {planet_sign}")

    if not isinstance(reference_sign, int) or reference_sign < 0 or reference_sign > 11:
        raise ValueError(f"reference_sign must be 0-11, got {reference_sign}")

    # House calculation: how many signs forward from reference?
    house = ((planet_sign - reference_sign) % 12) + 1

    return house


def get_house_significations(house: int) -> list[str]:
    """Get the natural significations (meanings) of a house.

    Returns a list of topics and life areas naturally represented by the house.

    Args:
        house: House number (1-12)

    Returns:
        list: List of signification keywords

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> sigs = get_house_significations(7)
        >>> sigs
        ['marriage', 'partnership', 'business', 'spouse', 'relationships', 'contracts']
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    return HOUSE_SIGNIFICATIONS.get(house, [])


def get_house_karaka(house: int) -> str:
    """Get the natural significator (Karaka) for a house.

    The Karaka is the planet that naturally represents the house's significations.

    Args:
        house: House number (1-12)

    Returns:
        str: Planet name (the Karaka for this house)

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> karaka = get_house_karaka(7)
        >>> karaka
        'venus'  # Venus naturally represents marriage and partnerships
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    return HOUSE_KARAKAS.get(house, "")


def is_benefic_house(house: int) -> bool:
    """Check if a house is generally benefic (auspicious).

    Benefic houses are those that generally produce positive results.
    The benefic houses are 1, 4, 5, 7, 9, 10, and 11.

    Args:
        house: House number (1-12)

    Returns:
        bool: True if house is benefic, False otherwise

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> is_benefic_house(5)
        True
        >>> is_benefic_house(6)
        False
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    return house in BENEFIC_HOUSES


def is_malefic_house(house: int) -> bool:
    """Check if a house is generally malefic (difficult).

    Malefic/Dusthana houses are 6, 8, and 12, which present challenges.

    Args:
        house: House number (1-12)

    Returns:
        bool: True if house is malefic, False otherwise

    Raises:
        ValueError: If house is not 1-12
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    return house in MALEFIC_HOUSES


def get_house_category(house: int) -> str:
    """Get the astrological category of a house.

    Returns the primary category:
    - "kendra" (angular): 1, 4, 7, 10
    - "trikona" (trine): 1, 5, 9
    - "dusthana" (difficult): 6, 8, 12
    - "upachaya" (growth): 3, 6, 10, 11
    - "maraka" (death-inflicting): 2, 7
    - "other": for houses not in primary categories

    Args:
        house: House number (1-12)

    Returns:
        str: Category name

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> get_house_category(1)
        'kendra'
        >>> get_house_category(6)
        'dusthana'
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    if house in KENDRA_HOUSES:
        return HouseCategory.KENDRA.value
    elif house in TRIKONA_HOUSES:
        return HouseCategory.TRIKONA.value
    elif house in DUSTHANA_HOUSES:
        return HouseCategory.DUSTHANA.value
    elif house in UPACHAYA_HOUSES:
        return HouseCategory.UPACHAYA.value
    elif house in MARAKA_HOUSES:
        return HouseCategory.MARAKA.value
    else:
        return HouseCategory.OTHER.value


def get_house_categories(house: int) -> list[str]:
    """Get all applicable categories for a house.

    Unlike get_house_category(), this returns all categories a house belongs to,
    since some houses fall into multiple categories (e.g., house 1 is both Kendra and Trikona).

    Args:
        house: House number (1-12)

    Returns:
        list: List of category names

    Example:
        >>> get_house_categories(1)
        ['kendra', 'trikona']
        >>> get_house_categories(10)
        ['kendra', 'upachaya']
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    categories = []

    if house in KENDRA_HOUSES:
        categories.append(HouseCategory.KENDRA.value)
    if house in TRIKONA_HOUSES:
        categories.append(HouseCategory.TRIKONA.value)
    if house in DUSTHANA_HOUSES:
        categories.append(HouseCategory.DUSTHANA.value)
    if house in UPACHAYA_HOUSES:
        categories.append(HouseCategory.UPACHAYA.value)
    if house in MARAKA_HOUSES:
        categories.append(HouseCategory.MARAKA.value)

    return categories if categories else [HouseCategory.OTHER.value]


def get_trinal_houses(house: int) -> list[int]:
    """Get trinal houses from a given house.

    Trinal houses are the 1st, 5th, and 9th from a given reference house.
    These are the most auspicious house positions.

    Args:
        house: Reference house number (1-12)

    Returns:
        list: The 1st, 5th, and 9th houses from the given house

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> get_trinal_houses(3)
        [3, 7, 11]
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    return [
        ((house - 1 + 0) % 12) + 1,  # 1st from house
        ((house - 1 + 4) % 12) + 1,  # 5th from house
        ((house - 1 + 8) % 12) + 1,  # 9th from house
    ]


def get_kendras_from(house: int) -> list[int]:
    """Get all Kendra (angular) houses from a given house.

    Kendras are the 1st, 4th, 7th, and 10th houses from a given reference.

    Args:
        house: Reference house number (1-12)

    Returns:
        list: The 1st, 4th, 7th, and 10th houses from the given house

    Raises:
        ValueError: If house is not 1-12

    Example:
        >>> get_kendras_from(2)
        [2, 5, 8, 11]
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    return [
        ((house - 1 + 0) % 12) + 1,  # 1st from house
        ((house - 1 + 3) % 12) + 1,  # 4th from house
        ((house - 1 + 6) % 12) + 1,  # 7th from house
        ((house - 1 + 9) % 12) + 1,  # 10th from house
    ]


def get_house_lord_strength(
    house_lord: str,  # noqa: ARG001
    planet_positions: dict[str, dict[str, float]],  # noqa: ARG001
    house: int,  # noqa: ARG001
) -> float | None:
    """Calculate the strength of a house lord.

    Note: This is a placeholder for integration with planetary strength calculations.
    Full implementation requires Shadbala and other strength metrics from the ephemeris module.

    Args:
        house_lord: Planet name (e.g., "mars", "venus")
        planet_positions: Dict of planet positions from get_all_planets()
        house: House number for context

    Returns:
        Optional[float]: Strength value (0-100) or None if not available
    """
    # This would integrate with shadbala calculations
    return None


def get_house_lord_placement(
    house_lord: str, planet_positions: dict[str, dict[str, float]], cusps: list[float]
) -> int | None:
    """Determine which house the lord of a specific house is placed in.

    This is useful for analyzing the strength and effectiveness of a house
    through its lord's placement.

    Args:
        house_lord: Planet name (the lord of the house we're analyzing)
        planet_positions: Dict of planet positions with "longitude" keys
        cusps: List of 12 house cusps

    Returns:
        int: House number where the house lord is placed (1-12), or None if not found

    Example:
        >>> planets = {"mars": 125.0, "venus": 200.0, ...}
        >>> cusps = [10.0, 40.0, 70.0, 100.0, 130.0, 160.0, 190.0, 220.0, 250.0, 280.0, 310.0, 340.0]
        >>> placement = get_house_lord_placement("mars", planets, cusps)
        >>> placement
        5  # Mars (7th house lord) is placed in the 5th house
    """
    if not isinstance(planet_positions, dict) or house_lord not in planet_positions:
        return None

    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    lord_longitude = planet_positions[house_lord]

    return get_house_for_longitude(lord_longitude, cusps)


def get_all_planets_by_house(planets: dict[str, float], cusps: list[float]) -> dict[int, list[str]]:
    """Organize all planets by their houses.

    Args:
        planets: Dict mapping planet names to longitudes (0-360)
        cusps: List of 12 house cusps

    Returns:
        dict: Mapping of house number (1-12) to list of planets in that house

    Example:
        >>> planets = {"sun": 45.0, "moon": 120.0, "mars": 75.0}
        >>> cusps = [10.0, 40.0, 70.0, 100.0, 130.0, 160.0, 190.0, 220.0, 250.0, 280.0, 310.0, 340.0]
        >>> by_house = get_all_planets_by_house(planets, cusps)
        >>> by_house
        {1: ['sun'], 3: ['mars'], 4: ['moon']}
    """
    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    planets_by_house = {i: [] for i in range(1, 13)}

    for planet_name, longitude in planets.items():
        house = get_house_for_longitude(longitude, cusps)
        planets_by_house[house].append(planet_name)

    # Remove empty houses for cleaner output
    return {house: planets_list for house, planets_list in planets_by_house.items() if planets_list}


def get_house_analysis(
    house: int, lagna_sign: int, planets: dict[str, float], cusps: list[float]
) -> dict[str, any]:
    """Get comprehensive analysis of a specific house.

    Combines house lord, significations, categorization, and planetary placements.

    Args:
        house: House number (1-12)
        lagna_sign: Lagna rashi number (0-11)
        planets: Dict of planetary longitudes
        cusps: List of 12 house cusps

    Returns:
        dict: Comprehensive house analysis including:
            - number: House number
            - lord: Planet ruling the house
            - lord_sign: Sign on the house cusp
            - significations: List of house meanings
            - karaka: Natural significator
            - categories: Applicable house categories
            - benefic: Whether house is benefic
            - planets_in_house: Planets currently occupying it
            - lord_placement: Which house the lord is in

    Raises:
        ValueError: If parameters are invalid
    """
    if not isinstance(house, int) or house < 1 or house > 12:
        raise ValueError(f"House must be 1-12, got {house}")

    lord = get_house_lord(house, lagna_sign)
    house_sign_rashi = (lagna_sign + house - 1) % 12
    house_sign_name = rashi_to_sign_name(house_sign_rashi)

    planets_in_h = get_planets_in_house(planets, house, cusps)
    lord_placement = get_house_lord_placement(lord, planets, cusps)

    return {
        "number": house,
        "lord": lord,
        "lord_sign": house_sign_name,
        "significations": get_house_significations(house),
        "karaka": get_house_karaka(house),
        "categories": get_house_categories(house),
        "benefic": is_benefic_house(house),
        "planets_in_house": planets_in_h,
        "lord_placement": lord_placement,
    }
