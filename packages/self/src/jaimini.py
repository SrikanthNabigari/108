"""Jaimini astrology system implementation.

This module implements Jaimini astrology concepts including:
- Chara Karakas (movable significators)
- Jaimini aspects (special aspect rules)
- Arudha Padas (perceived reality)
- Karakamsha (Atmakaraka in D9)
- Chara Dasha (sign-based dasha system)

Jaimini is a major parashari tradition that emphasizes signs rather than planets,
and uses Chara Karakas (movable significators) determined by planetary degrees.
"""

from datetime import datetime, timedelta

from packages.core.src.constants import CharaKaraka, Planet, Rashi, SignMobility
from packages.core.src.models import (
    ArudhaPada,
    BirthChart,
    CharaDashaPeriod,
    CharaKarakaResult,
    KarakamshaResult,
)
from packages.cosmos.src.divisional import get_navamsha

# Rashi enum value to index mapping
RASHI_TO_INDEX = {
    Rashi.ARIES: 0,
    Rashi.TAURUS: 1,
    Rashi.GEMINI: 2,
    Rashi.CANCER: 3,
    Rashi.LEO: 4,
    Rashi.VIRGO: 5,
    Rashi.LIBRA: 6,
    Rashi.SCORPIO: 7,
    Rashi.SAGITTARIUS: 8,
    Rashi.CAPRICORN: 9,
    Rashi.AQUARIUS: 10,
    Rashi.PISCES: 11,
}

# Index to Rashi enum mapping
INDEX_TO_RASHI = {v: k for k, v in RASHI_TO_INDEX.items()}

# CharaKaraka sequence (highest to lowest degree)
CHARA_KARAKA_SEQUENCE = [
    CharaKaraka.ATMAKARAKA,
    CharaKaraka.AMATYAKARAKA,
    CharaKaraka.BHRATRIKARAKA,
    CharaKaraka.MATRIKARAKA,
    CharaKaraka.PUTRAKARAKA,
    CharaKaraka.GNATIKARAKA,
    CharaKaraka.DARAKARAKA,
]


def get_sign_mobility(rashi: Rashi) -> SignMobility:
    """Get the mobility classification of a sign.

    Args:
        rashi: The zodiac sign

    Returns:
        SignMobility: MOVABLE, FIXED, or DUAL

    Example:
        >>> get_sign_mobility(Rashi.ARIES)
        SignMobility.MOVABLE
        >>> get_sign_mobility(Rashi.TAURUS)
        SignMobility.FIXED
        >>> get_sign_mobility(Rashi.GEMINI)
        SignMobility.DUAL
    """
    movable = {Rashi.ARIES, Rashi.CANCER, Rashi.LIBRA, Rashi.CAPRICORN}
    fixed = {Rashi.TAURUS, Rashi.LEO, Rashi.SCORPIO, Rashi.AQUARIUS}
    dual = {Rashi.GEMINI, Rashi.VIRGO, Rashi.SAGITTARIUS, Rashi.PISCES}

    if rashi in movable:
        return SignMobility.MOVABLE
    elif rashi in fixed:
        return SignMobility.FIXED
    elif rashi in dual:
        return SignMobility.DUAL
    else:
        return SignMobility.MOVABLE  # Default


def calculate_chara_karakas(chart: BirthChart) -> list[CharaKarakaResult]:
    """Calculate Chara Karakas for all 7 planets (excluding Rahu/Ketu).

    Chara Karakas are determined by the degree within sign (rashi_degree).
    The planet with highest degree becomes Atmakaraka, second becomes Amatyakaraka, etc.

    Args:
        chart: Birth chart with planet positions

    Returns:
        List of 7 CharaKarakaResult objects, sorted from Atmakaraka to Darakaraka

    Example:
        >>> karakas = calculate_chara_karakas(chart)
        >>> karakas[0].karaka  # CharaKaraka.ATMAKARAKA
        >>> karakas[0].planet  # Planet with highest degree
    """
    # Get 7 planets (exclude Rahu and Ketu)
    seven_planets = [
        Planet.SUN,
        Planet.MOON,
        Planet.MARS,
        Planet.MERCURY,
        Planet.JUPITER,
        Planet.VENUS,
        Planet.SATURN,
    ]

    # Extract planet positions with their degrees
    planet_degrees = []
    for planet in seven_planets:
        if planet in chart.planets:
            pos = chart.planets[planet]
            planet_degrees.append((planet, pos.rashi_degree, pos.rashi))

    # Sort by degree descending (highest first)
    planet_degrees.sort(key=lambda x: x[1], reverse=True)

    # Assign Chara Karakas
    results = []
    for i, (planet, degree, rashi) in enumerate(planet_degrees):
        if i < len(CHARA_KARAKA_SEQUENCE):
            results.append(
                CharaKarakaResult(
                    karaka=CHARA_KARAKA_SEQUENCE[i],
                    planet=planet,
                    degree_in_sign=degree,
                    rashi=rashi,
                )
            )

    return results


def get_atmakaraka(chart: BirthChart) -> CharaKarakaResult:
    """Get the Atmakaraka (soul significator) - planet with highest degree.

    Args:
        chart: Birth chart with planet positions

    Returns:
        CharaKarakaResult: The Atmakaraka

    Example:
        >>> ak = get_atmakaraka(chart)
        >>> ak.karaka  # CharaKaraka.ATMAKARAKA
        >>> ak.planet  # The planet serving as AK
    """
    karakas = calculate_chara_karakas(chart)
    return karakas[0]


def get_jaimini_aspects(from_rashi: Rashi) -> list[Rashi]:
    """Get the 3 signs that a sign aspects in Jaimini system.

    Jaimini aspects are different from Parashari. Every sign aspects 3 signs:
    - The 5th, 8th, and 11th signs from itself (counting inclusively)

    Args:
        from_rashi: The sign from which aspects are calculated

    Returns:
        List of 3 Rashi values that are aspected

    Example:
        >>> aspects = get_jaimini_aspects(Rashi.ARIES)
        >>> # Returns [Leo (5th), Scorpio (8th), Aquarius (11th)]
    """
    base_index = RASHI_TO_INDEX[from_rashi]

    # Jaimini aspects: 5th, 8th, and 11th signs (indices +4, +7, +10)
    aspect_indices = [(base_index + 4) % 12, (base_index + 7) % 12, (base_index + 10) % 12]

    return [INDEX_TO_RASHI[idx] for idx in aspect_indices]


def _get_sign_lord(rashi: Rashi) -> Planet:
    """Get the ruling planet of a sign.

    Args:
        rashi: The zodiac sign

    Returns:
        Planet: The lord of the sign

    Note:
        For dual-lorded signs (Aquarius, Scorpio), returns the primary classical lord.
    """
    lordships = {
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
    return lordships[rashi]


def calculate_arudha_pada(house_num: int, chart: BirthChart) -> ArudhaPada:
    """Calculate the Arudha Pada for a specific house.

    Arudha Pada represents the perceived reality or image of a house.

    Algorithm:
    1. Find the sign of the house
    2. Find the lord of that sign
    3. Count from house sign to lord's sign = N (minimum 1)
    4. Count N signs from lord's sign forward = Pada sign
    5. Special rules:
       - If lord is in the house itself (N=1), pada = 10th from house
       - If pada falls in same house or 7th from it, shift to 10th from house

    Args:
        house_num: House number (1-12)
        chart: Birth chart with lagna and planet positions

    Returns:
        ArudhaPada: The calculated Arudha Pada position

    Example:
        >>> pada = calculate_arudha_pada(1, chart)  # A1 (Arudha Lagna)
        >>> pada.rashi  # Sign where pada falls
    """
    # Get the sign of the house
    lagna_index = RASHI_TO_INDEX[chart.lagna_rashi]
    house_sign_index = (lagna_index + house_num - 1) % 12
    house_sign = INDEX_TO_RASHI[house_sign_index]

    # Find the lord of the house sign
    house_lord = _get_sign_lord(house_sign)

    # Find where the lord is placed
    if house_lord not in chart.planets:
        # If lord not found, default to house sign itself
        return ArudhaPada(
            house_number=house_num,
            rashi=house_sign,
            house_lord=house_lord,
            calculation_note="Lord not found in chart",
        )

    lord_position = chart.planets[house_lord]
    lord_sign_index = RASHI_TO_INDEX[lord_position.rashi]

    # Count from house sign to lord's sign (minimum 1)
    if lord_sign_index >= house_sign_index:
        count_to_lord = lord_sign_index - house_sign_index + 1
    else:
        count_to_lord = 12 - house_sign_index + lord_sign_index + 1

    # Special case: lord in house itself
    if count_to_lord == 1:
        pada_index = (house_sign_index + 9) % 12  # 10th from house
        note = "Lord in house itself - pada at 10th"
    else:
        # Count N signs from lord's sign
        pada_index = (lord_sign_index + count_to_lord - 1) % 12
        note = f"Counted {count_to_lord} from lord position"

        # Check if pada is in same house or 7th from it
        if pada_index == house_sign_index or pada_index == (house_sign_index + 6) % 12:
            pada_index = (house_sign_index + 9) % 12  # Shift to 10th
            note += " - shifted to 10th (pada in same/7th)"

    pada_rashi = INDEX_TO_RASHI[pada_index]

    return ArudhaPada(
        house_number=house_num,
        rashi=pada_rashi,
        house_lord=house_lord,
        calculation_note=note,
    )


def calculate_all_arudha_padas(chart: BirthChart) -> list[ArudhaPada]:
    """Calculate Arudha Padas for all 12 houses.

    Args:
        chart: Birth chart with lagna and planet positions

    Returns:
        List of 12 ArudhaPada objects (A1 through A12)

    Example:
        >>> padas = calculate_all_arudha_padas(chart)
        >>> padas[0]  # A1 (Arudha Lagna)
        >>> padas[6]  # A7 (Dara Pada - spouse)
    """
    return [calculate_arudha_pada(house_num, chart) for house_num in range(1, 13)]


def get_karakamsha(chart: BirthChart) -> KarakamshaResult:
    """Calculate the Karakamsha - Atmakaraka's position in D9 (Navamsha).

    The Karakamsha is one of the most important concepts in Jaimini astrology.
    It represents the soul's deepest purpose and karmic direction.

    Args:
        chart: Birth chart with planet positions

    Returns:
        KarakamshaResult: Karakamsha analysis with planets in that sign

    Example:
        >>> km = get_karakamsha(chart)
        >>> km.navamsha_rashi  # AK's D9 sign
        >>> km.planets_in_karakamsha  # Planets sharing that D9 sign
    """
    # Get Atmakaraka
    ak = get_atmakaraka(chart)
    ak_planet = ak.planet
    ak_position = chart.planets[ak_planet]

    # Calculate AK's navamsha position
    ak_navamsha = get_navamsha(ak_position.longitude)
    karakamsha_rashi = INDEX_TO_RASHI[ak_navamsha["rashi"]]

    # Find other planets in the same navamsha sign
    planets_in_km = []
    for planet, pos in chart.planets.items():
        nav = get_navamsha(pos.longitude)
        if nav["rashi"] == ak_navamsha["rashi"] and planet != ak_planet:
            planets_in_km.append(planet)

    # Generate interpretation based on karakamsha sign
    interpretations = {
        Rashi.ARIES: "Dynamic soul purpose, leadership, pioneering initiatives",
        Rashi.TAURUS: "Stable values, material security, artistic pursuits",
        Rashi.GEMINI: "Communicative dharma, intellectual pursuits, versatility",
        Rashi.CANCER: "Nurturing purpose, emotional intelligence, family focus",
        Rashi.LEO: "Creative expression, authority, self-confidence",
        Rashi.VIRGO: "Service-oriented, analytical, perfection in craft",
        Rashi.LIBRA: "Diplomatic purpose, partnerships, balance and harmony",
        Rashi.SCORPIO: "Transformative path, deep research, occult knowledge",
        Rashi.SAGITTARIUS: "Philosophical pursuits, higher learning, teaching",
        Rashi.CAPRICORN: "Disciplined achievement, structure, responsibility",
        Rashi.AQUARIUS: "Humanitarian goals, innovation, collective welfare",
        Rashi.PISCES: "Spiritual liberation, compassion, transcendence",
    }

    interpretation = interpretations.get(
        karakamsha_rashi, "Unique soul purpose requiring deep reflection"
    )

    return KarakamshaResult(
        atmakaraka=ak_planet,
        navamsha_rashi=karakamsha_rashi,
        planets_in_karakamsha=planets_in_km,
        interpretation=interpretation,
    )


def calculate_chara_dasha(
    birth_dt: datetime, chart: BirthChart, years: int = 108
) -> list[CharaDashaPeriod]:
    """Calculate Chara Dasha periods starting from birth.

    Chara Dasha is a sign-based dasha system where each sign rules for 1-12 years.
    The duration is determined by the distance from the sign to its lord.

    Algorithm:
    1. Start from lagna sign
    2. Direction: If lagna is odd-footed (Aries, Gemini, Leo, Libra, Sag, Aquarius),
       go forward; if even-footed, go backward
    3. Duration = distance from sign to its lord (1-12 years)
    4. For dual-lorded signs (Aquarius, Scorpio), use the stronger lord

    Args:
        birth_dt: Birth datetime
        chart: Birth chart with lagna and planet positions
        years: Total years to calculate (default 108, can go up to 120)

    Returns:
        List of CharaDashaPeriod objects in chronological order

    Example:
        >>> periods = calculate_chara_dasha(birth_dt, chart, years=120)
        >>> periods[0]  # First dasha period (starting from lagna)
        >>> periods[0].duration_years  # Years in that sign's dasha
    """
    lagna = chart.lagna_rashi
    lagna_index = RASHI_TO_INDEX[lagna]

    # Determine if lagna is odd-footed (forward) or even-footed (backward)
    # Odd-footed: indices 0, 2, 4, 6, 8, 10 (Aries, Gemini, Leo, Libra, Sag, Aquarius)
    is_forward = lagna_index % 2 == 0

    periods = []
    current_date = birth_dt
    total_years_calculated = 0

    # Generate sequence of 12 signs
    sign_sequence = []
    for i in range(12):
        sign_index = (lagna_index + i) % 12 if is_forward else (lagna_index - i) % 12
        sign_sequence.append(INDEX_TO_RASHI[sign_index])

    # Calculate duration for each sign and create periods
    for rashi in sign_sequence:
        if total_years_calculated >= years:
            break

        # Get sign lord
        lord = _get_sign_lord(rashi)

        # For dual-lorded signs, we'll use the primary lord
        # (More sophisticated logic could check strength)

        # Find lord's position
        if lord not in chart.planets:
            duration = 12  # Default if lord not found
        else:
            lord_sign = chart.planets[lord].rashi
            lord_index = RASHI_TO_INDEX[lord_sign]
            sign_index = RASHI_TO_INDEX[rashi]

            # Calculate distance
            if rashi in {
                Rashi.ARIES,
                Rashi.GEMINI,
                Rashi.LEO,
                Rashi.LIBRA,
                Rashi.SAGITTARIUS,
                Rashi.AQUARIUS,
            }:
                # Odd signs: count forward
                if lord_index >= sign_index:
                    distance = lord_index - sign_index
                else:
                    distance = 12 - sign_index + lord_index
            else:
                # Even signs: count backward (12 - forward count)
                if sign_index >= lord_index:
                    forward_dist = sign_index - lord_index
                else:
                    forward_dist = 12 - lord_index + sign_index
                distance = 12 - forward_dist

            # If lord is in the sign itself, duration = 12
            duration = 12 if distance == 0 else distance

            # Ensure duration is 1-12
            duration = max(1, min(12, duration))

        end_date = current_date + timedelta(days=int(duration * 365.25))

        periods.append(
            CharaDashaPeriod(
                rashi=rashi, start_date=current_date, end_date=end_date, duration_years=duration
            )
        )

        current_date = end_date
        total_years_calculated += duration

    return periods


__all__ = [
    "calculate_all_arudha_padas",
    "calculate_arudha_pada",
    "calculate_chara_dasha",
    "calculate_chara_karakas",
    "get_atmakaraka",
    "get_jaimini_aspects",
    "get_karakamsha",
    "get_sign_mobility",
]
