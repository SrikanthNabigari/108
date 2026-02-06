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


def _get_planets_in_sign(chart: BirthChart, rashi: Rashi) -> list[Planet]:
    """Get all planets placed in a given sign.

    Args:
        chart: Birth chart with planet positions
        rashi: The sign to check

    Returns:
        List of planets in that sign
    """
    return [p for p, pos in chart.planets.items() if pos.rashi == rashi]


def _count_argala_strength(planets: list[Planet]) -> float:
    """Calculate argala strength from planets in a sign.

    Benefics (Jupiter, Venus, Mercury, Moon) contribute +1 each.
    Malefics (Sun, Mars, Saturn, Rahu, Ketu) contribute +0.5 each.
    Empty sign = 0.

    Args:
        planets: List of planets in the sign

    Returns:
        Numerical strength of argala
    """
    if not planets:
        return 0.0

    benefics = {Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON}
    strength = 0.0
    for p in planets:
        if p in benefics:
            strength += 1.0
        else:
            strength += 0.5
    return strength


def calculate_argala(chart: BirthChart) -> dict:
    """Calculate Argala (planetary intervention) for all 12 houses.

    Argala is a Jaimini concept where planets in certain houses from a sign
    exert influence (intervention) on that sign. Argala can be obstructed
    by planets in the corresponding obstruction houses.

    Argala types:
    - 2nd house = Dhana Argala (wealth intervention)
    - 4th house = Sukha Argala (happiness intervention)
    - 11th house = Labha Argala (gains intervention)
    - 5th house = Putra Argala (children/merit intervention)

    Obstruction (Virodhargala):
    - 3rd house obstructs 2nd (Dhana)
    - 10th house obstructs 4th (Sukha)
    - 12th house obstructs 11th (Labha)
    - 9th house obstructs 5th (Putra)

    An argala is obstructed only if the obstruction house has MORE
    planets/strength than the argala house.

    Args:
        chart: Birth chart with planet positions

    Returns:
        Dictionary with argala analysis for all 12 houses.
        Each house entry contains the 4 argala types with their
        source planets, strength, obstruction, and net effect.
    """
    argala_types = [
        {
            "name": "dhana",
            "label": "Dhana Argala (Wealth)",
            "house_offset": 1,
            "obstruction_offset": 2,
        },
        {
            "name": "sukha",
            "label": "Sukha Argala (Happiness)",
            "house_offset": 3,
            "obstruction_offset": 9,
        },
        {
            "name": "labha",
            "label": "Labha Argala (Gains)",
            "house_offset": 10,
            "obstruction_offset": 11,
        },
        {
            "name": "putra",
            "label": "Putra Argala (Children/Merit)",
            "house_offset": 4,
            "obstruction_offset": 8,
        },
    ]

    lagna_index = RASHI_TO_INDEX[chart.lagna_rashi]
    result = {}

    for house_num in range(1, 13):
        house_sign_index = (lagna_index + house_num - 1) % 12
        house_argalas = {}
        active_count = 0

        for atype in argala_types:
            # Argala source sign
            argala_sign_index = (house_sign_index + atype["house_offset"]) % 12
            argala_rashi = INDEX_TO_RASHI[argala_sign_index]
            argala_planets = _get_planets_in_sign(chart, argala_rashi)
            argala_strength = _count_argala_strength(argala_planets)

            # Obstruction sign
            obstruction_sign_index = (house_sign_index + atype["obstruction_offset"]) % 12
            obstruction_rashi = INDEX_TO_RASHI[obstruction_sign_index]
            obstruction_planets = _get_planets_in_sign(chart, obstruction_rashi)
            obstruction_strength = _count_argala_strength(obstruction_planets)

            # Argala is active if source strength > obstruction strength
            is_obstructed = obstruction_strength >= argala_strength and argala_strength > 0
            is_active = argala_strength > 0 and not is_obstructed
            net_strength = (
                max(0.0, argala_strength - obstruction_strength) if argala_strength > 0 else 0.0
            )

            if is_active:
                active_count += 1

            house_argalas[atype["name"]] = {
                "label": atype["label"],
                "source_sign": argala_rashi.value,
                "source_planets": [p.value for p in argala_planets],
                "argala_strength": argala_strength,
                "obstruction_sign": obstruction_rashi.value,
                "obstruction_planets": [p.value for p in obstruction_planets],
                "obstruction_strength": obstruction_strength,
                "is_obstructed": is_obstructed,
                "is_active": is_active,
                "net_strength": round(net_strength, 2),
            }

        house_rashi = INDEX_TO_RASHI[house_sign_index]
        result[house_num] = {
            "house": house_num,
            "sign": house_rashi.value,
            "argalas": house_argalas,
            "active_argala_count": active_count,
            "summary": _get_argala_summary(active_count),
        }

    return result


def _get_argala_summary(active_count: int) -> str:
    """Get a summary description based on active argala count.

    Args:
        active_count: Number of active (unobstructed) argalas

    Returns:
        Summary string
    """
    summaries = {
        0: "No active argala - house lacks planetary support",
        1: "Mild argala - some planetary support for this house",
        2: "Moderate argala - good planetary support",
        3: "Strong argala - significant planetary intervention",
    }
    return summaries.get(active_count, "Very strong argala - all four types active")


def _interpret_upapada_sign(ul_rashi: Rashi) -> dict:
    """Interpret the Upapada Lagna sign to describe partner type.

    The sign where UL falls describes the nature and personality of the spouse.

    Args:
        ul_rashi: The rashi where Upapada Lagna is placed

    Returns:
        Dictionary with sign, element, quality, and description of partner type
    """
    sign_interpretations = {
        Rashi.ARIES: {
            "element": "fire",
            "quality": "movable",
            "partner_type": (
                "Independent, assertive, and energetic partner. "
                "Spouse may be athletic, competitive, or a natural leader."
            ),
        },
        Rashi.TAURUS: {
            "element": "earth",
            "quality": "fixed",
            "partner_type": (
                "Stable, sensual, and materially comfortable partner. "
                "Spouse values security, beauty, and luxury."
            ),
        },
        Rashi.GEMINI: {
            "element": "air",
            "quality": "dual",
            "partner_type": (
                "Intellectual, communicative, and versatile partner. "
                "Spouse is witty, curious, and may have multiple interests."
            ),
        },
        Rashi.CANCER: {
            "element": "water",
            "quality": "movable",
            "partner_type": (
                "Nurturing, emotional, and family-oriented partner. "
                "Spouse is caring, protective, and deeply attached."
            ),
        },
        Rashi.LEO: {
            "element": "fire",
            "quality": "fixed",
            "partner_type": (
                "Dignified, proud, and charismatic partner. "
                "Spouse commands respect, may be from a good family or prominent."
            ),
        },
        Rashi.VIRGO: {
            "element": "earth",
            "quality": "dual",
            "partner_type": (
                "Analytical, service-oriented, and practical partner. "
                "Spouse is detail-oriented, health-conscious, and methodical."
            ),
        },
        Rashi.LIBRA: {
            "element": "air",
            "quality": "movable",
            "partner_type": (
                "Balanced, charming, and diplomatic partner. "
                "Spouse values harmony, beauty, and social relationships."
            ),
        },
        Rashi.SCORPIO: {
            "element": "water",
            "quality": "fixed",
            "partner_type": (
                "Intense, transformative, and deeply passionate partner. "
                "Spouse is secretive, powerful, and magnetically attractive."
            ),
        },
        Rashi.SAGITTARIUS: {
            "element": "fire",
            "quality": "dual",
            "partner_type": (
                "Philosophical, optimistic, and adventurous partner. "
                "Spouse is well-educated, spiritual, or fond of travel."
            ),
        },
        Rashi.CAPRICORN: {
            "element": "earth",
            "quality": "movable",
            "partner_type": (
                "Disciplined, ambitious, and mature partner. "
                "Spouse is hardworking, responsible, and status-conscious."
            ),
        },
        Rashi.AQUARIUS: {
            "element": "air",
            "quality": "fixed",
            "partner_type": (
                "Unconventional, humanitarian, and independent partner. "
                "Spouse is progressive, intellectual, and socially conscious."
            ),
        },
        Rashi.PISCES: {
            "element": "water",
            "quality": "dual",
            "partner_type": (
                "Compassionate, spiritual, and imaginative partner. "
                "Spouse is intuitive, artistic, and emotionally deep."
            ),
        },
    }

    info = sign_interpretations.get(
        ul_rashi,
        {
            "element": "unknown",
            "quality": "unknown",
            "partner_type": "Partner characteristics require deeper analysis.",
        },
    )

    return {
        "sign": ul_rashi.value,
        "element": info["element"],
        "quality": info["quality"],
        "partner_type": info["partner_type"],
    }


def _interpret_upapada_lord(ul_lord: Planet, ul_lord_rashi: Rashi, ul_lord_house: int) -> dict:
    """Interpret the UL lord's placement for marriage quality assessment.

    The lord of the Upapada sign and its placement indicates the overall
    quality and nature of the marriage.

    Args:
        ul_lord: Planet ruling the UL sign
        ul_lord_rashi: Rashi where UL lord is placed
        ul_lord_house: House number (1-12) where UL lord is placed

    Returns:
        Dictionary with lord, placement, and quality assessment
    """
    # House-based quality assessment
    kendra_houses = {1, 4, 7, 10}
    trikona_houses = {1, 5, 9}
    dusthana_houses = {6, 8, 12}
    upachaya_houses = {3, 6, 10, 11}

    quality_factors = []
    quality_score = 50.0

    if ul_lord_house in kendra_houses:
        quality_score += 20
        quality_factors.append(
            f"UL lord {ul_lord.value} in kendra house {ul_lord_house}: "
            "strong marriage, stable relationship"
        )
    elif ul_lord_house in trikona_houses:
        quality_score += 15
        quality_factors.append(
            f"UL lord {ul_lord.value} in trikona house {ul_lord_house}: "
            "fortunate marriage, dharmic partnership"
        )
    elif ul_lord_house in dusthana_houses:
        quality_score -= 15
        if ul_lord_house == 6:
            quality_factors.append(
                f"UL lord {ul_lord.value} in 6th house: conflict or health issues in marriage"
            )
        elif ul_lord_house == 8:
            quality_factors.append(
                f"UL lord {ul_lord.value} in 8th house: transformation or hidden issues in marriage"
            )
        else:
            quality_factors.append(
                f"UL lord {ul_lord.value} in 12th house: loss or separation tendency in marriage"
            )
    elif ul_lord_house in upachaya_houses:
        quality_score += 5
        quality_factors.append(
            f"UL lord {ul_lord.value} in upachaya house {ul_lord_house}: "
            "marriage improves over time"
        )
    else:
        quality_factors.append(
            f"UL lord {ul_lord.value} in house {ul_lord_house}: moderate marriage quality"
        )

    # Exaltation/debilitation of UL lord
    exaltation_signs = {
        Planet.SUN: Rashi.ARIES,
        Planet.MOON: Rashi.TAURUS,
        Planet.MARS: Rashi.CAPRICORN,
        Planet.MERCURY: Rashi.VIRGO,
        Planet.JUPITER: Rashi.CANCER,
        Planet.VENUS: Rashi.PISCES,
        Planet.SATURN: Rashi.LIBRA,
    }
    debilitation_signs = {
        Planet.SUN: Rashi.LIBRA,
        Planet.MOON: Rashi.SCORPIO,
        Planet.MARS: Rashi.CANCER,
        Planet.MERCURY: Rashi.PISCES,
        Planet.JUPITER: Rashi.CAPRICORN,
        Planet.VENUS: Rashi.VIRGO,
        Planet.SATURN: Rashi.ARIES,
    }

    if ul_lord in exaltation_signs and ul_lord_rashi == exaltation_signs[ul_lord]:
        quality_score += 20
        quality_factors.append(f"UL lord {ul_lord.value} exalted: excellent marriage quality")
    elif ul_lord in debilitation_signs and ul_lord_rashi == debilitation_signs[ul_lord]:
        quality_score -= 20
        quality_factors.append(f"UL lord {ul_lord.value} debilitated: challenges in marriage")

    quality_score = max(0.0, min(100.0, quality_score))

    if quality_score >= 70:
        quality_summary = "High quality marriage expected"
    elif quality_score >= 50:
        quality_summary = "Moderate marriage quality"
    else:
        quality_summary = "Marriage may face significant challenges"

    return {
        "lord": ul_lord.value,
        "lord_sign": ul_lord_rashi.value,
        "lord_house": ul_lord_house,
        "quality_score": round(quality_score, 2),
        "quality_summary": quality_summary,
        "factors": quality_factors,
    }


def _analyze_second_from_ul(chart: BirthChart, ul_rashi: Rashi) -> dict:
    """Analyze the 2nd house from Upapada for marriage sustenance.

    The 2nd from UL is critical for marriage longevity. Benefics here
    sustain the marriage; malefics create separation risk.

    Args:
        chart: Birth chart with planet positions
        ul_rashi: Rashi of the Upapada Lagna

    Returns:
        Dictionary with planets, sustenance assessment, and separation risk
    """
    ul_index = RASHI_TO_INDEX[ul_rashi]
    second_from_ul_index = (ul_index + 1) % 12
    second_from_ul_rashi = INDEX_TO_RASHI[second_from_ul_index]

    benefics = {Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON}
    malefics = {Planet.SATURN, Planet.MARS, Planet.RAHU, Planet.KETU, Planet.SUN}

    planets_in_second = _get_planets_in_sign(chart, second_from_ul_rashi)
    benefics_found = [p.value for p in planets_in_second if p in benefics]
    malefics_found = [p.value for p in planets_in_second if p in malefics]

    factors = []
    separation_risk = "low"

    if benefics_found:
        factors.append(
            f"Benefics in 2nd from UL ({', '.join(benefics_found)}): marriage sustenance is strong"
        )
    if malefics_found:
        factors.append(
            f"Malefics in 2nd from UL ({', '.join(malefics_found)}): separation or discord risk"
        )
        separation_risk = "high" if len(malefics_found) >= 2 else "moderate"

    if not planets_in_second:
        factors.append("2nd from UL empty: no strong sustenance or threat indicators")

    # Check lord of 2nd from UL
    second_lord = _get_sign_lord(second_from_ul_rashi)
    if second_lord in chart.planets:
        second_lord_pos = chart.planets[second_lord]
        dusthana = {6, 8, 12}
        if second_lord_pos.house in dusthana:
            separation_risk = "high" if separation_risk == "moderate" else "moderate"
            factors.append(
                f"Lord of 2nd from UL ({second_lord.value}) in dusthana "
                f"house {second_lord_pos.house}: weakens marriage sustenance"
            )

    return {
        "second_from_ul_sign": second_from_ul_rashi.value,
        "planets_in_second": [p.value for p in planets_in_second],
        "benefics": benefics_found,
        "malefics": malefics_found,
        "separation_risk": separation_risk,
        "factors": factors,
    }


def _check_separation_indicators(chart: BirthChart, ul_rashi: Rashi) -> dict:
    """Check for classical separation indicators related to Upapada.

    Multiple factors can indicate separation in marriage:
    - Rahu/Ketu axis on UL or 2nd from UL
    - Saturn aspecting or placed in UL
    - UL lord debilitated or combust
    - Malefics in 2nd from UL without benefic aspect

    Args:
        chart: Birth chart
        ul_rashi: Rashi of Upapada Lagna

    Returns:
        Dictionary with separation indicators and risk assessment
    """
    ul_index = RASHI_TO_INDEX[ul_rashi]
    indicators = []

    # Check Rahu/Ketu on UL
    planets_in_ul = _get_planets_in_sign(chart, ul_rashi)
    if Planet.RAHU in planets_in_ul:
        indicators.append("Rahu on Upapada: unconventional marriage or illusion about spouse")
    if Planet.KETU in planets_in_ul:
        indicators.append("Ketu on Upapada: detachment from marriage or past-life karmic bond")

    # Check Saturn on UL
    if Planet.SATURN in planets_in_ul:
        indicators.append("Saturn on Upapada: delays and hardship in marriage, but longevity")

    # Check Rahu/Ketu on 2nd from UL
    second_ul_index = (ul_index + 1) % 12
    second_ul_rashi = INDEX_TO_RASHI[second_ul_index]
    planets_in_2nd = _get_planets_in_sign(chart, second_ul_rashi)

    if Planet.RAHU in planets_in_2nd:
        indicators.append("Rahu in 2nd from UL: disruption risk in marriage sustenance")
    if Planet.KETU in planets_in_2nd:
        indicators.append("Ketu in 2nd from UL: sudden separation or loss tendency")

    # Check UL lord combustion (proximity to Sun)
    ul_lord = _get_sign_lord(ul_rashi)
    if ul_lord in chart.planets and ul_lord != Planet.SUN:
        ul_lord_pos = chart.planets[ul_lord]
        sun_pos = chart.planets.get(Planet.SUN)
        if sun_pos:
            distance = abs(ul_lord_pos.longitude - sun_pos.longitude)
            distance = min(distance, 360.0 - distance)
            if distance < 8.0:
                indicators.append(f"UL lord {ul_lord.value} combust: weakened marriage prospects")

    risk_level = "low"
    if len(indicators) >= 3:
        risk_level = "high"
    elif len(indicators) >= 1:
        risk_level = "moderate"

    return {
        "indicators": indicators,
        "indicator_count": len(indicators),
        "risk_level": risk_level,
    }


def _analyze_dk_ul_connection(chart: BirthChart, ul_rashi: Rashi) -> dict:
    """Analyze the connection between Darakaraka and Upapada Lagna.

    When Darakaraka (planet with lowest degree = spouse significator) has
    a connection to UL, it strengthens marriage indications. Connections include:
    - DK placed in UL sign
    - DK aspecting UL (Jaimini aspects)
    - DK lord of UL sign

    Args:
        chart: Birth chart
        ul_rashi: Rashi of Upapada Lagna

    Returns:
        Dictionary with DK planet, connections found, and strength assessment
    """
    karakas = calculate_chara_karakas(chart)
    dk_result = karakas[-1]  # Last one is Darakaraka (lowest degree)
    dk_planet = dk_result.planet
    dk_rashi = dk_result.rashi

    connections = []
    connection_strength = 0.0

    # DK placed in UL sign
    if dk_rashi == ul_rashi:
        connections.append(
            f"Darakaraka {dk_planet.value} placed in Upapada sign: very strong marriage indication"
        )
        connection_strength += 30.0

    # DK aspecting UL (Jaimini aspects)
    dk_aspects = get_jaimini_aspects(dk_rashi)
    if ul_rashi in dk_aspects:
        connections.append(
            f"Darakaraka {dk_planet.value} aspects Upapada (Jaimini): spouse connection confirmed"
        )
        connection_strength += 20.0

    # DK is lord of UL
    ul_lord = _get_sign_lord(ul_rashi)
    if dk_planet == ul_lord:
        connections.append(
            f"Darakaraka {dk_planet.value} is also lord of Upapada: very strong marital bond"
        )
        connection_strength += 25.0

    # DK in kendra/trikona from UL
    ul_index = RASHI_TO_INDEX[ul_rashi]
    dk_index = RASHI_TO_INDEX[dk_rashi]
    distance = (dk_index - ul_index) % 12
    kendra_offsets = {0, 3, 6, 9}
    trikona_offsets = {0, 4, 8}

    if distance in kendra_offsets and distance != 0:
        connections.append("Darakaraka in kendra from UL: solid marriage foundation")
        connection_strength += 15.0
    elif distance in trikona_offsets and distance != 0:
        connections.append("Darakaraka in trikona from UL: fortunate marriage connection")
        connection_strength += 10.0

    if not connections:
        connections.append("No direct DK-UL connection: spouse may come through other factors")

    connection_strength = min(100.0, connection_strength)

    return {
        "darakaraka_planet": dk_planet.value,
        "darakaraka_sign": dk_rashi.value,
        "darakaraka_degree": round(dk_result.degree_in_sign, 2),
        "connections": connections,
        "connection_strength": round(connection_strength, 2),
    }


def _marriage_timing_from_ul(chart: BirthChart, ul_rashi: Rashi) -> dict:
    """Estimate marriage timing indicators from Upapada analysis.

    Jaimini timing principles based on UL:
    - Transit of Jupiter/Saturn over UL or 7th from UL activates marriage
    - Chara Dasha of UL sign or its 7th triggers marriage
    - UL lord's transit position relative to natal UL

    This provides qualitative timing indicators, not exact dates.

    Args:
        chart: Birth chart
        ul_rashi: Rashi of Upapada Lagna

    Returns:
        Dictionary with timing indicators and activating signs
    """
    ul_index = RASHI_TO_INDEX[ul_rashi]
    seventh_from_ul_index = (ul_index + 6) % 12
    seventh_from_ul = INDEX_TO_RASHI[seventh_from_ul_index]

    # Signs that can activate marriage
    activating_signs = [ul_rashi, seventh_from_ul]

    # Also consider trikona from UL (5th and 9th)
    fifth_from_ul = INDEX_TO_RASHI[(ul_index + 4) % 12]
    ninth_from_ul = INDEX_TO_RASHI[(ul_index + 8) % 12]

    timing_factors = [
        f"Jupiter or Saturn transiting {ul_rashi.value} or "
        f"{seventh_from_ul.value} can trigger marriage",
        f"Chara Dasha of {ul_rashi.value} or {seventh_from_ul.value} "
        "is a strong marriage timing period",
        f"Trikona signs ({fifth_from_ul.value}, {ninth_from_ul.value}) "
        "from UL are secondary timing indicators",
    ]

    # UL lord placement for additional timing clue
    ul_lord = _get_sign_lord(ul_rashi)
    if ul_lord in chart.planets:
        ul_lord_sign = chart.planets[ul_lord].rashi
        timing_factors.append(
            f"UL lord {ul_lord.value} in {ul_lord_sign.value}: "
            "transit activation of this sign also relevant for timing"
        )

    return {
        "primary_activating_signs": [s.value for s in activating_signs],
        "secondary_activating_signs": [fifth_from_ul.value, ninth_from_ul.value],
        "timing_factors": timing_factors,
    }


def interpret_upapada(chart: BirthChart) -> dict:
    """Complete Upapada Lagna analysis for marriage from Jaimini perspective.

    The Upapada Lagna (UL) is the Arudha Pada of the 12th house and is the
    primary Jaimini indicator for marriage. This function provides a comprehensive
    marriage analysis including:
    - UL sign = type of partner
    - UL lord placement = marriage quality
    - 2nd from UL = marriage sustenance
    - 7th from UL = physical relationship
    - Darakaraka connection = spouse bond strength
    - Marriage timing indicators

    Args:
        chart: Birth chart with planet positions and lagna

    Returns:
        Dictionary with complete Upapada marriage analysis
    """
    # Calculate UL (Arudha of 12th house)
    ul_pada = calculate_arudha_pada(12, chart)
    ul_rashi = ul_pada.rashi

    # 1. Partner type from UL sign
    sign_analysis = _interpret_upapada_sign(ul_rashi)

    # 2. UL lord placement for marriage quality
    ul_lord = _get_sign_lord(ul_rashi)
    if ul_lord in chart.planets:
        ul_lord_pos = chart.planets[ul_lord]
        lord_analysis = _interpret_upapada_lord(ul_lord, ul_lord_pos.rashi, ul_lord_pos.house)
    else:
        lord_analysis = {
            "lord": ul_lord.value,
            "lord_sign": "unknown",
            "lord_house": 0,
            "quality_score": 50.0,
            "quality_summary": "UL lord not found in chart",
            "factors": [],
        }

    # 3. Marriage sustenance (2nd from UL)
    second_analysis = _analyze_second_from_ul(chart, ul_rashi)

    # 4. Seventh from UL (physical relationship)
    ul_index = RASHI_TO_INDEX[ul_rashi]
    seventh_from_ul_index = (ul_index + 6) % 12
    seventh_from_ul = INDEX_TO_RASHI[seventh_from_ul_index]
    planets_in_7th_from_ul = _get_planets_in_sign(chart, seventh_from_ul)

    benefics = {Planet.JUPITER, Planet.VENUS, Planet.MERCURY, Planet.MOON}
    seventh_factors = []
    if planets_in_7th_from_ul:
        benefics_7th = [p.value for p in planets_in_7th_from_ul if p in benefics]
        malefics_7th = [p.value for p in planets_in_7th_from_ul if p not in benefics]
        if benefics_7th:
            seventh_factors.append(
                f"Benefics in 7th from UL ({', '.join(benefics_7th)}): "
                "harmonious physical relationship"
            )
        if malefics_7th:
            seventh_factors.append(
                f"Malefics in 7th from UL ({', '.join(malefics_7th)}): "
                "challenges in physical compatibility"
            )
    else:
        seventh_factors.append("7th from UL empty: neutral physical compatibility")

    seventh_analysis = {
        "sign": seventh_from_ul.value,
        "planets": [p.value for p in planets_in_7th_from_ul],
        "factors": seventh_factors,
    }

    # 5. Separation indicators
    separation = _check_separation_indicators(chart, ul_rashi)

    # 6. DK-UL connection
    dk_connection = _analyze_dk_ul_connection(chart, ul_rashi)

    # 7. Marriage timing
    timing = _marriage_timing_from_ul(chart, ul_rashi)

    # Overall summary
    quality_score = lord_analysis["quality_score"]
    if separation["risk_level"] == "high":
        quality_score -= 15
    elif separation["risk_level"] == "moderate":
        quality_score -= 5
    if dk_connection["connection_strength"] >= 30:
        quality_score += 10
    if second_analysis["separation_risk"] == "high":
        quality_score -= 10

    quality_score = max(0.0, min(100.0, quality_score))

    if quality_score >= 70:
        overall_summary = "Strong Upapada indications for a successful and fulfilling marriage."
    elif quality_score >= 50:
        overall_summary = (
            "Moderate Upapada indications. Marriage is likely but may require "
            "effort and understanding from both partners."
        )
    else:
        overall_summary = (
            "Challenging Upapada indications for marriage. There may be delays, "
            "obstacles, or need for compromise."
        )

    return {
        "upapada_lagna": {
            "sign": ul_rashi.value,
            "calculation_note": ul_pada.calculation_note,
        },
        "partner_type": sign_analysis,
        "marriage_quality": lord_analysis,
        "marriage_sustenance": second_analysis,
        "physical_relationship": seventh_analysis,
        "separation_indicators": separation,
        "dk_connection": dk_connection,
        "marriage_timing": timing,
        "overall_score": round(quality_score, 2),
        "overall_summary": overall_summary,
    }


__all__ = [
    "calculate_all_arudha_padas",
    "calculate_argala",
    "calculate_arudha_pada",
    "calculate_chara_dasha",
    "calculate_chara_karakas",
    "get_atmakaraka",
    "get_jaimini_aspects",
    "get_karakamsha",
    "get_sign_mobility",
    "interpret_upapada",
]
