"""Prashna (Horary) astrology module for 108 core package.

Prashna astrology erects a chart for the moment a question is asked and
judges the answer based on planetary positions at that exact time.

Key principles:
- Question time and location determine the chart
- Lagna (ascendant) strength indicates question validity
- Moon condition shows emotional state and timing
- Significator planet represents the question topic
- Judgment based on combined analysis of all factors

This module provides complete Prashna analysis for all question categories.
"""

from datetime import datetime
from typing import Any

from packages.core.src.constants import Planet, PrashnaCategory, PrashnaJudgment, Rashi
from packages.core.src.models import HouseCusps, PlanetPosition, PrashnaChart, PrashnaResult
from packages.cosmos.src.ephemeris import (
    get_all_planets,
    get_ayanamsa,
    get_house_cusps,
    get_julian_day,
)
from packages.cosmos.src.nakshatras import longitude_to_nakshatra

# Constants
RASHI_LIST = list(Rashi)

# Benefic and malefic planets
BENEFICS = [Planet.JUPITER, Planet.VENUS, Planet.MERCURY]
MALEFICS = [Planet.SATURN, Planet.MARS, Planet.RAHU, Planet.KETU, Planet.SUN]

# Sign mobility classification
MOVABLE_SIGNS = [Rashi.ARIES, Rashi.CANCER, Rashi.LIBRA, Rashi.CAPRICORN]
FIXED_SIGNS = [Rashi.TAURUS, Rashi.LEO, Rashi.SCORPIO, Rashi.AQUARIUS]
DUAL_SIGNS = [Rashi.GEMINI, Rashi.VIRGO, Rashi.SAGITTARIUS, Rashi.PISCES]

# Kendra houses (quadrants)
KENDRA_HOUSES = [1, 4, 7, 10]

# Trikona houses (trines)
TRIKONA_HOUSES = [1, 5, 9]

# Dusthana houses (evil houses)
DUSTHANA_HOUSES = [6, 8, 12]

# Planet exaltation signs
EXALTATION_SIGNS = {
    Planet.SUN: Rashi.ARIES,
    Planet.MOON: Rashi.TAURUS,
    Planet.MARS: Rashi.CAPRICORN,
    Planet.MERCURY: Rashi.VIRGO,
    Planet.JUPITER: Rashi.CANCER,
    Planet.VENUS: Rashi.PISCES,
    Planet.SATURN: Rashi.LIBRA,
}

# Planet own signs
OWN_SIGNS = {
    Planet.SUN: [Rashi.LEO],
    Planet.MOON: [Rashi.CANCER],
    Planet.MARS: [Rashi.ARIES, Rashi.SCORPIO],
    Planet.MERCURY: [Rashi.GEMINI, Rashi.VIRGO],
    Planet.JUPITER: [Rashi.SAGITTARIUS, Rashi.PISCES],
    Planet.VENUS: [Rashi.TAURUS, Rashi.LIBRA],
    Planet.SATURN: [Rashi.CAPRICORN, Rashi.AQUARIUS],
}

# Direction indicators for lost objects
DIRECTION_MAP = {
    Planet.SUN: "East",
    Planet.MOON: "Northwest",
    Planet.MARS: "South",
    Planet.MERCURY: "North",
    Planet.JUPITER: "Northeast",
    Planet.VENUS: "Southeast",
    Planet.SATURN: "West",
    Planet.RAHU: "Southwest",
    Planet.KETU: "Southwest",
}


def get_significator(category: PrashnaCategory) -> Planet:
    """Get the primary significator planet for a question category.

    Args:
        category: Question category enum

    Returns:
        Planet enum representing the significator

    Example:
        >>> get_significator(PrashnaCategory.MARRIAGE)
        <Planet.VENUS: 'venus'>
    """
    significator_map = {
        PrashnaCategory.HEALTH: Planet.SUN,
        PrashnaCategory.MARRIAGE: Planet.VENUS,
        PrashnaCategory.CAREER: Planet.SATURN,
        PrashnaCategory.TRAVEL: Planet.MOON,
        PrashnaCategory.LOST_OBJECTS: Planet.MOON,
        PrashnaCategory.LEGAL: Planet.JUPITER,
        PrashnaCategory.SPIRITUAL: Planet.JUPITER,
        PrashnaCategory.CHILDREN: Planet.JUPITER,
        PrashnaCategory.WEALTH: Planet.JUPITER,
        PrashnaCategory.EDUCATION: Planet.MERCURY,
    }
    return significator_map[category]


def _longitude_to_rashi(longitude: float) -> Rashi:
    """Convert longitude (0-360) to Rashi enum.

    Args:
        longitude: Ecliptic longitude in degrees (0-360)

    Returns:
        Rashi enum
    """
    index = int(longitude / 30) % 12
    return RASHI_LIST[index]


def _get_rashi_lord(rashi: Rashi) -> Planet:
    """Get the ruling planet of a rashi.

    Args:
        rashi: Rashi enum

    Returns:
        Planet enum representing the lord
    """
    lord_map = {
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
    return lord_map[rashi]


def _get_rashi_mobility(rashi: Rashi) -> str:
    """Get the mobility type of a rashi.

    Args:
        rashi: Rashi enum

    Returns:
        String: "movable", "fixed", or "dual"
    """
    if rashi in MOVABLE_SIGNS:
        return "movable"
    elif rashi in FIXED_SIGNS:
        return "fixed"
    else:
        return "dual"


def _calculate_house_from_cusps(planet_longitude: float, cusps: list[float]) -> int:
    """Calculate which house a planet is in based on cusps.

    Args:
        planet_longitude: Planet longitude (0-360)
        cusps: List of 12 house cusps

    Returns:
        House number (1-12)
    """
    # Normalize longitude
    planet_lon = planet_longitude % 360.0

    # Check each house boundary
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]

        # Handle wrap-around at 360/0
        if cusp_start < cusp_end:
            if cusp_start <= planet_lon < cusp_end:
                return i + 1
        else:
            # Wraps around 0
            if planet_lon >= cusp_start or planet_lon < cusp_end:
                return i + 1

    # Fallback (should not reach here)
    return 1


def create_prashna_chart(
    question: str,
    question_dt: datetime,
    latitude: float,
    longitude: float,
    category: PrashnaCategory,
) -> PrashnaChart:
    """Create a Prashna chart for a horary question.

    Erects a complete chart for the moment the question is asked, including
    all planetary positions, house cusps, and identifying the significator.

    Args:
        question: The question text
        question_dt: Time the question was asked
        latitude: Geographic latitude
        longitude: Geographic longitude
        category: Question category

    Returns:
        PrashnaChart model with complete chart data

    Example:
        >>> from datetime import datetime
        >>> chart = create_prashna_chart(
        ...     "Will I get the job?",
        ...     datetime(2024, 6, 15, 10, 30, 0),
        ...     28.6139,
        ...     77.2090,
        ...     PrashnaCategory.CAREER
        ... )
        >>> chart.lagna_rashi
        <Rashi.VIRGO: 'virgo'>
    """
    # Calculate Julian Day
    jd = get_julian_day(question_dt)

    # Get ayanamsa
    ayanamsa_value = get_ayanamsa(jd)

    # Get all planet positions
    planet_data = get_all_planets(jd, ayanamsa_value)

    # Get house cusps
    houses_data = get_house_cusps(jd, latitude, longitude, ayanamsa=ayanamsa_value)

    # Build PlanetPosition objects
    planets: dict[Planet, PlanetPosition] = {}

    for planet_name, pos_data in planet_data.items():
        planet_enum = Planet(planet_name)
        planet_lon = pos_data["longitude"]

        # Get nakshatra info
        nak_info = longitude_to_nakshatra(planet_lon)

        # Calculate house placement
        house = _calculate_house_from_cusps(planet_lon, houses_data["cusps"])

        # Get rashi
        rashi = _longitude_to_rashi(planet_lon)
        rashi_degree = planet_lon % 30.0

        planets[planet_enum] = PlanetPosition(
            planet=planet_enum,
            longitude=planet_lon,
            latitude=pos_data["latitude"],
            speed=pos_data["speed"],
            rashi=rashi,
            rashi_degree=rashi_degree,
            nakshatra=nak_info["name"],
            nakshatra_pada=nak_info["pada"],
            nakshatra_lord=Planet(nak_info["lord"]),
            is_retrograde=pos_data["is_retrograde"],
            house=house,
        )

    # Get lagna rashi and degree
    lagna_longitude = houses_data["ascendant"]
    lagna_rashi = _longitude_to_rashi(lagna_longitude)

    # Get significator for category
    significator = get_significator(category)

    # Build house cusps model
    house_cusps = HouseCusps(
        ascendant=houses_data["ascendant"],
        mc=houses_data["mc"],
        cusps=houses_data["cusps"],
    )

    return PrashnaChart(
        question=question,
        question_datetime=question_dt,
        category=category,
        latitude=latitude,
        longitude=longitude,
        lagna_rashi=lagna_rashi,
        lagna_degree=lagna_longitude,
        moon_position=planets[Planet.MOON],
        significator=significator,
        planets=planets,
        houses=house_cusps,
    )


def analyze_lagna_strength(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze the ascendant (lagna) strength in a Prashna chart.

    The lagna represents the querent (person asking the question) and its
    strength indicates whether the question is valid and answerable.

    Args:
        chart: PrashnaChart to analyze

    Returns:
        Dictionary with:
            - score: Strength score (0-100)
            - degree_quality: "too_early", "good", or "too_late"
            - lagna_lord_strength: Description of lagna lord placement
            - factors: List of influencing factors
    """
    score = 50.0
    factors = []

    # Check lagna degree within sign
    lagna_degree_in_sign = chart.lagna_degree % 30.0

    if lagna_degree_in_sign < 3.0:
        degree_quality = "too_early"
        score -= 20
        factors.append("Lagna in early degrees (question premature)")
    elif lagna_degree_in_sign > 27.0:
        degree_quality = "too_late"
        score -= 20
        factors.append("Lagna in late degrees (question too late)")
    else:
        degree_quality = "good"
        score += 10
        factors.append("Lagna in middle degrees (good timing)")

    # Get lagna lord
    lagna_lord = _get_rashi_lord(chart.lagna_rashi)
    lagna_lord_pos = chart.planets.get(lagna_lord)

    if lagna_lord_pos:
        # Check if lagna lord is in kendra or trikona
        if lagna_lord_pos.house in KENDRA_HOUSES:
            score += 15
            factors.append(f"Lagna lord {lagna_lord.value} in kendra (strong)")
            lagna_lord_strength = "strong (kendra)"
        elif lagna_lord_pos.house in TRIKONA_HOUSES:
            score += 10
            factors.append(f"Lagna lord {lagna_lord.value} in trikona (good)")
            lagna_lord_strength = "good (trikona)"
        elif lagna_lord_pos.house in DUSTHANA_HOUSES:
            score -= 10
            factors.append(f"Lagna lord {lagna_lord.value} in dusthana (weak)")
            lagna_lord_strength = "weak (dusthana)"
        else:
            lagna_lord_strength = "moderate"

        # Check retrograde
        if lagna_lord_pos.is_retrograde:
            score -= 5
            factors.append(f"Lagna lord {lagna_lord.value} retrograde (delays)")
    else:
        lagna_lord_strength = "unknown"

    # Check planets in lagna (house 1)
    planets_in_lagna = [p for p in chart.planets.values() if p.house == 1]

    for planet_pos in planets_in_lagna:
        if planet_pos.planet in BENEFICS:
            score += 10
            factors.append(f"Benefic {planet_pos.planet.value} in lagna (positive)")
        elif planet_pos.planet in MALEFICS:
            score -= 10
            factors.append(f"Malefic {planet_pos.planet.value} in lagna (challenging)")

    # Clamp score
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 2),
        "degree_quality": degree_quality,
        "lagna_lord_strength": lagna_lord_strength,
        "factors": factors,
    }


def analyze_moon_condition(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze the Moon's condition in a Prashna chart.

    The Moon represents the querent's mind and emotions, and also provides
    timing indications.

    Args:
        chart: PrashnaChart to analyze

    Returns:
        Dictionary with:
            - score: Condition score (0-100)
            - phase: "waxing" or "waning"
            - speed_quality: "fast", "normal", or "slow"
            - factors: List of influencing factors
    """
    score = 50.0
    factors = []

    moon_pos = chart.moon_position
    sun_pos = chart.planets[Planet.SUN]

    # Determine moon phase
    moon_sun_diff = (moon_pos.longitude - sun_pos.longitude) % 360.0

    if moon_sun_diff < 180.0:
        phase = "waxing"
        score += 15
        factors.append("Moon waxing (favorable, growing energy)")
    else:
        phase = "waning"
        score -= 5
        factors.append("Moon waning (less favorable, declining energy)")

    # Check moon speed
    moon_speed = abs(moon_pos.speed)

    if moon_speed > 13.0:
        speed_quality = "fast"
        score += 10
        factors.append(f"Moon fast ({moon_speed:.2f}°/day, quick results)")
    elif moon_speed < 12.0:
        speed_quality = "slow"
        score -= 5
        factors.append(f"Moon slow ({moon_speed:.2f}°/day, delays possible)")
    else:
        speed_quality = "normal"
        factors.append(f"Moon normal speed ({moon_speed:.2f}°/day)")

    # Check if moon's nakshatra lord is benefic
    nak_lord = moon_pos.nakshatra_lord
    if nak_lord in BENEFICS:
        score += 10
        factors.append(f"Moon in nakshatra of benefic {nak_lord.value} (good)")
    elif nak_lord in MALEFICS:
        score -= 5
        factors.append(f"Moon in nakshatra of malefic {nak_lord.value} (challenging)")

    # Check moon house placement
    if moon_pos.house in DUSTHANA_HOUSES:
        score -= 15
        factors.append(f"Moon in dusthana house {moon_pos.house} (unfavorable)")
    elif moon_pos.house in KENDRA_HOUSES:
        score += 10
        factors.append(f"Moon in kendra house {moon_pos.house} (strong)")
    elif moon_pos.house in TRIKONA_HOUSES:
        score += 10
        factors.append(f"Moon in trikona house {moon_pos.house} (favorable)")

    # Clamp score
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 2),
        "phase": phase,
        "speed_quality": speed_quality,
        "factors": factors,
    }


def analyze_significator(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze the significator planet for the question.

    The significator represents the matter being asked about. Its strength
    and placement indicate the outcome.

    Args:
        chart: PrashnaChart to analyze

    Returns:
        Dictionary with:
            - score: Strength score (0-100)
            - house: House placement
            - dignity: "exalted", "own_sign", "neutral", "debilitated"
            - factors: List of influencing factors
    """
    score = 50.0
    factors = []

    significator = chart.significator
    sig_pos = chart.planets[significator]

    # Check house placement
    house = sig_pos.house

    if house in KENDRA_HOUSES:
        score += 20
        factors.append(f"{significator.value} in kendra house {house} (strong)")
    elif house in TRIKONA_HOUSES:
        score += 15
        factors.append(f"{significator.value} in trikona house {house} (favorable)")
    elif house in DUSTHANA_HOUSES:
        score -= 20
        factors.append(f"{significator.value} in dusthana house {house} (weak)")

    # Check dignity (exaltation, own sign, etc.)
    sig_rashi = sig_pos.rashi

    if significator in EXALTATION_SIGNS and sig_rashi == EXALTATION_SIGNS[significator]:
        dignity = "exalted"
        score += 25
        factors.append(f"{significator.value} exalted in {sig_rashi.value} (excellent)")
    elif significator in OWN_SIGNS and sig_rashi in OWN_SIGNS[significator]:
        dignity = "own_sign"
        score += 20
        factors.append(f"{significator.value} in own sign {sig_rashi.value} (strong)")
    else:
        dignity = "neutral"
        factors.append(f"{significator.value} in {sig_rashi.value}")

    # Check retrograde
    if sig_pos.is_retrograde:
        score -= 15
        factors.append(f"{significator.value} retrograde (delays, obstacles)")

    # Check if significator is combust (too close to Sun)
    sun_pos = chart.planets[Planet.SUN]
    distance_from_sun = abs(sig_pos.longitude - sun_pos.longitude)
    distance_from_sun = min(distance_from_sun, 360.0 - distance_from_sun)

    if significator != Planet.SUN and distance_from_sun < 8.0:
        score -= 15
        factors.append(f"{significator.value} combust (too close to Sun, weakened)")

    # Clamp score
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 2),
        "house": house,
        "dignity": dignity,
        "factors": factors,
    }


def judge_prashna(chart: PrashnaChart) -> tuple[PrashnaJudgment, float]:
    """Judge the overall outcome of a Prashna question.

    Combines lagna strength, moon condition, and significator analysis to
    determine the likely outcome.

    Args:
        chart: PrashnaChart to judge

    Returns:
        Tuple of (judgment enum, total score 0-100)

    Example:
        >>> judgment, score = judge_prashna(chart)
        >>> judgment
        <PrashnaJudgment.FAVORABLE: 'favorable'>
        >>> score
        75.3
    """
    # Analyze all three factors
    lagna_analysis = analyze_lagna_strength(chart)
    moon_analysis = analyze_moon_condition(chart)
    sig_analysis = analyze_significator(chart)

    # Weighted average
    total_score = (
        lagna_analysis["score"] * 0.30
        + moon_analysis["score"] * 0.30
        + sig_analysis["score"] * 0.40
    )

    # Determine judgment based on score
    if total_score > 70:
        judgment = PrashnaJudgment.FAVORABLE
    elif total_score >= 55:
        judgment = PrashnaJudgment.NEUTRAL
    elif total_score >= 40:
        judgment = PrashnaJudgment.DELAYED
    else:
        judgment = PrashnaJudgment.UNFAVORABLE

    return judgment, round(total_score, 2)


def predict_timing(chart: PrashnaChart) -> dict[str, Any]:
    """Predict timing of the outcome for a Prashna question.

    Uses lagna degree and sign mobility to estimate when the outcome will
    manifest.

    Args:
        chart: PrashnaChart to analyze

    Returns:
        Dictionary with:
            - estimate: Timing estimate string
            - timing_unit: "days", "weeks", or "months"
            - confidence: Confidence level
    """
    lagna_degree_in_sign = chart.lagna_degree % 30.0
    rashi_mobility = _get_rashi_mobility(chart.lagna_rashi)

    # Determine base timing from degree
    if lagna_degree_in_sign < 10.0:
        degree_timing = "quick"
    elif lagna_degree_in_sign < 20.0:
        degree_timing = "moderate"
    else:
        degree_timing = "delayed"

    # Determine timing unit from sign mobility
    if rashi_mobility == "movable":
        timing_unit = "days"
        if degree_timing == "quick":
            estimate = "1-7 days"
        elif degree_timing == "moderate":
            estimate = "1-2 weeks"
        else:
            estimate = "2-4 weeks"
    elif rashi_mobility == "fixed":
        timing_unit = "months"
        if degree_timing == "quick":
            estimate = "1-3 months"
        elif degree_timing == "moderate":
            estimate = "3-6 months"
        else:
            estimate = "6-12 months"
    else:  # dual
        timing_unit = "weeks"
        if degree_timing == "quick":
            estimate = "1-2 weeks"
        elif degree_timing == "moderate":
            estimate = "3-6 weeks"
        else:
            estimate = "2-3 months"

    # Confidence based on lagna strength
    lagna_analysis = analyze_lagna_strength(chart)
    confidence = "high" if lagna_analysis["degree_quality"] == "good" else "moderate"

    return {
        "estimate": estimate,
        "timing_unit": timing_unit,
        "confidence": confidence,
    }


def analyze_health_prashna(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze a health-related Prashna question.

    Focuses on 1st house (self), 6th house (disease), and 8th house (danger).

    Args:
        chart: PrashnaChart with HEALTH category

    Returns:
        Dictionary with analysis, factors, and outlook
    """
    factors = []
    outlook_score = 50.0

    # Check 1st house (self/vitality)
    planets_in_1st = [p for p in chart.planets.values() if p.house == 1]
    for p in planets_in_1st:
        if p.planet in BENEFICS:
            outlook_score += 10
            factors.append(f"Benefic {p.planet.value} in 1st house (good vitality)")
        else:
            outlook_score -= 5
            factors.append(f"Malefic {p.planet.value} in 1st house (health concerns)")

    # Check 6th house (disease)
    planets_in_6th = [p for p in chart.planets.values() if p.house == 6]
    if len(planets_in_6th) == 0:
        outlook_score += 10
        factors.append("6th house empty (no disease indicated)")
    else:
        outlook_score -= 10
        factors.append("Planets in 6th house (disease possible)")

    # Check 8th house (danger/chronic issues)
    planets_in_8th = [p for p in chart.planets.values() if p.house == 8]
    if len(planets_in_8th) > 0:
        outlook_score -= 15
        factors.append("Planets in 8th house (chronic issues or danger)")

    # Check significator (Sun for health)
    sun_pos = chart.planets[Planet.SUN]
    if sun_pos.rashi == EXALTATION_SIGNS[Planet.SUN]:
        outlook_score += 15
        factors.append("Sun exalted (strong vitality)")

    if outlook_score >= 60:
        outlook = "Positive - Recovery likely"
    elif outlook_score >= 40:
        outlook = "Moderate - Care needed"
    else:
        outlook = "Concerning - Medical attention advised"

    return {
        "analysis": "Health analysis based on 1st, 6th, and 8th houses",
        "factors": factors,
        "outlook": outlook,
    }


def analyze_marriage_prashna(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze a marriage-related Prashna question.

    Focuses on 7th house (spouse/partnership) and Venus (significator).

    Args:
        chart: PrashnaChart with MARRIAGE category

    Returns:
        Dictionary with analysis, factors, and outlook
    """
    factors = []
    outlook_score = 50.0

    # Check 7th house
    planets_in_7th = [p for p in chart.planets.values() if p.house == 7]
    for p in planets_in_7th:
        if p.planet in BENEFICS:
            outlook_score += 15
            factors.append(f"Benefic {p.planet.value} in 7th house (favorable for marriage)")
        else:
            outlook_score -= 10
            factors.append(f"Malefic {p.planet.value} in 7th house (obstacles possible)")

    # Check Venus (marriage significator)
    venus_pos = chart.planets[Planet.VENUS]
    if (
        venus_pos.rashi in OWN_SIGNS[Planet.VENUS]
        or venus_pos.rashi == EXALTATION_SIGNS[Planet.VENUS]
    ):
        outlook_score += 20
        factors.append("Venus strong (excellent for marriage)")
    if venus_pos.is_retrograde:
        outlook_score -= 10
        factors.append("Venus retrograde (delays or reconsideration)")

    # Check lagna lord and 7th lord relationship
    lagna_lord = _get_rashi_lord(chart.lagna_rashi)
    seventh_rashi = _longitude_to_rashi((chart.lagna_degree + 180.0) % 360.0)
    seventh_lord = _get_rashi_lord(seventh_rashi)

    lagna_lord_house = chart.planets[lagna_lord].house
    seventh_lord_house = chart.planets[seventh_lord].house

    if lagna_lord_house in KENDRA_HOUSES and seventh_lord_house in KENDRA_HOUSES:
        outlook_score += 15
        factors.append("Both lagna lord and 7th lord in kendras (strong union)")

    if outlook_score >= 65:
        outlook = "Favorable - Marriage prospects good"
    elif outlook_score >= 45:
        outlook = "Neutral - Some effort needed"
    else:
        outlook = "Challenging - Obstacles present"

    return {
        "analysis": "Marriage analysis based on 7th house and Venus",
        "factors": factors,
        "outlook": outlook,
    }


def analyze_career_prashna(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze a career-related Prashna question.

    Focuses on 10th house (career) and Saturn/Sun (significators).

    Args:
        chart: PrashnaChart with CAREER category

    Returns:
        Dictionary with analysis, factors, and outlook
    """
    factors = []
    outlook_score = 50.0

    # Always add baseline factors
    factors.append("Career analysis initiated for 10th house, Saturn, and Sun")

    # Check 10th house
    planets_in_10th = [p for p in chart.planets.values() if p.house == 10]
    if len(planets_in_10th) == 0:
        factors.append("10th house empty (neutral career indication)")
    else:
        for p in planets_in_10th:
            if p.planet in [Planet.JUPITER, Planet.MERCURY, Planet.SUN, Planet.SATURN]:
                outlook_score += 15
                factors.append(f"{p.planet.value} in 10th house (career support)")
            elif p.planet in [Planet.MARS, Planet.RAHU]:
                outlook_score += 5
                factors.append(f"{p.planet.value} in 10th house (ambition and drive)")

    # Check Saturn (career karma)
    saturn_pos = chart.planets[Planet.SATURN]
    if saturn_pos.house in KENDRA_HOUSES:
        outlook_score += 15
        factors.append("Saturn in kendra (career stability)")
    else:
        factors.append(f"Saturn in house {saturn_pos.house}")

    if saturn_pos.is_retrograde:
        outlook_score -= 5
        factors.append("Saturn retrograde (delays in career)")

    # Check Sun (authority)
    sun_pos = chart.planets[Planet.SUN]
    if sun_pos.house in [1, 10]:
        outlook_score += 10
        factors.append("Sun in 1st or 10th (leadership potential)")
    else:
        factors.append(f"Sun in house {sun_pos.house}")

    # Check Jupiter (expansion)
    jupiter_pos = chart.planets[Planet.JUPITER]
    if jupiter_pos.house in [1, 10, 11]:
        outlook_score += 10
        factors.append("Jupiter well-placed (growth opportunities)")
    else:
        factors.append(f"Jupiter in house {jupiter_pos.house}")

    if outlook_score >= 65:
        outlook = "Positive - Career success likely"
    elif outlook_score >= 45:
        outlook = "Moderate - Steady progress expected"
    else:
        outlook = "Challenging - Patience required"

    return {
        "analysis": "Career analysis based on 10th house, Saturn, and Sun",
        "factors": factors,
        "outlook": outlook,
    }


def analyze_travel_prashna(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze a travel-related Prashna question.

    Focuses on 3rd house (short travel), 9th house (long travel), and Moon.

    Args:
        chart: PrashnaChart with TRAVEL category

    Returns:
        Dictionary with analysis, factors, and outlook
    """
    factors = []
    outlook_score = 50.0

    # Check 3rd house (short journeys)
    planets_in_3rd = [p for p in chart.planets.values() if p.house == 3]
    if len(planets_in_3rd) > 0:
        outlook_score += 10
        factors.append("Planets in 3rd house (short travel indicated)")

    # Check 9th house (long journeys)
    planets_in_9th = [p for p in chart.planets.values() if p.house == 9]
    if len(planets_in_9th) > 0:
        outlook_score += 10
        factors.append("Planets in 9th house (long travel indicated)")

    # Check Moon (movement)
    moon_pos = chart.moon_position
    moon_rashi_mobility = _get_rashi_mobility(moon_pos.rashi)

    if moon_rashi_mobility == "movable":
        outlook_score += 15
        factors.append("Moon in movable sign (travel favored)")
    elif moon_rashi_mobility == "fixed":
        outlook_score -= 10
        factors.append("Moon in fixed sign (travel delayed)")

    if abs(moon_pos.speed) > 13.0:
        outlook_score += 10
        factors.append("Moon fast (quick travel)")

    # Check malefics in 3rd or 9th
    for p in chart.planets.values():
        if p.house in [3, 9] and p.planet in MALEFICS:
            outlook_score -= 10
            factors.append(f"Malefic {p.planet.value} in travel house (obstacles)")

    if outlook_score >= 60:
        outlook = "Favorable - Travel smooth"
    elif outlook_score >= 40:
        outlook = "Moderate - Minor delays possible"
    else:
        outlook = "Difficult - Postpone if possible"

    return {
        "analysis": "Travel analysis based on 3rd, 9th houses and Moon",
        "factors": factors,
        "outlook": outlook,
    }


def analyze_lost_object_prashna(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze a lost object Prashna question.

    Focuses on Moon and 2nd house (possessions), with direction indicators.

    Args:
        chart: PrashnaChart with LOST_OBJECTS category

    Returns:
        Dictionary with analysis, factors, and outlook
    """
    factors = []
    outlook_score = 50.0

    # Find strongest planet for direction
    strongest_planet = None
    max_strength = -1

    for planet, pos in chart.planets.items():
        strength = 0
        if pos.house in KENDRA_HOUSES:
            strength += 3
        if planet in BENEFICS:
            strength += 2
        if not pos.is_retrograde:
            strength += 1

        if strength > max_strength:
            max_strength = strength
            strongest_planet = planet

    if strongest_planet and strongest_planet in DIRECTION_MAP:
        direction = DIRECTION_MAP[strongest_planet]
        factors.append(f"Look in {direction} direction (indicated by {strongest_planet.value})")

    # Moon significator for lost objects
    moon_pos = chart.moon_position

    if moon_pos.house in [1, 4, 7, 10]:
        outlook_score += 20
        factors.append("Moon in kendra (object likely to be found)")
    elif moon_pos.house in DUSTHANA_HOUSES:
        outlook_score -= 20
        factors.append("Moon in dusthana (recovery difficult)")

    # Check 2nd house (possessions)
    planets_in_2nd = [p for p in chart.planets.values() if p.house == 2]
    for p in planets_in_2nd:
        if p.planet in BENEFICS:
            outlook_score += 15
            factors.append("Benefic in 2nd house (recovery likely)")

    if outlook_score >= 60:
        outlook = "Likely found - Search indicated direction"
    elif outlook_score >= 40:
        outlook = "Possible recovery - Keep searching"
    else:
        outlook = "Recovery uncertain - May be lost"

    return {
        "analysis": "Lost object analysis based on Moon, 2nd house, and directions",
        "factors": factors,
        "outlook": outlook,
    }


def analyze_legal_prashna(chart: PrashnaChart) -> dict[str, Any]:
    """Analyze a legal matter Prashna question.

    Compares strength of 1st house (self) vs 7th house (opponent).

    Args:
        chart: PrashnaChart with LEGAL category

    Returns:
        Dictionary with analysis, factors, and outlook
    """
    factors = []
    querent_score = 0
    opponent_score = 0

    # Get 1st lord (querent)
    lagna_lord = _get_rashi_lord(chart.lagna_rashi)
    lagna_lord_pos = chart.planets[lagna_lord]

    if lagna_lord_pos.house in KENDRA_HOUSES:
        querent_score += 3
        factors.append("Lagna lord in kendra (querent strong)")
    if not lagna_lord_pos.is_retrograde:
        querent_score += 1

    # Get 7th lord (opponent)
    seventh_rashi = _longitude_to_rashi((chart.lagna_degree + 180.0) % 360.0)
    seventh_lord = _get_rashi_lord(seventh_rashi)
    seventh_lord_pos = chart.planets[seventh_lord]

    if seventh_lord_pos.house in KENDRA_HOUSES:
        opponent_score += 3
        factors.append("7th lord in kendra (opponent strong)")
    if not seventh_lord_pos.is_retrograde:
        opponent_score += 1

    # Check Jupiter (justice)
    jupiter_pos = chart.planets[Planet.JUPITER]
    if jupiter_pos.house in [1, 10]:
        querent_score += 2
        factors.append("Jupiter favors querent (justice on your side)")
    elif jupiter_pos.house in [7]:
        opponent_score += 2
        factors.append("Jupiter favors opponent")

    # Determine outlook
    if querent_score > opponent_score + 1:
        outlook = "Favorable - Case in your favor"
    elif opponent_score > querent_score + 1:
        outlook = "Unfavorable - Opponent stronger"
    else:
        outlook = "Neutral - Outcome uncertain, settlement advised"

    factors.append(f"Querent strength: {querent_score}, Opponent strength: {opponent_score}")

    return {
        "analysis": "Legal analysis based on 1st vs 7th house lords",
        "factors": factors,
        "outlook": outlook,
    }


def analyze_prashna(
    question: str,
    question_dt: datetime,
    latitude: float,
    longitude: float,
    category: PrashnaCategory,
) -> PrashnaResult:
    """Complete Prashna analysis for a horary question.

    This is the main entry point for Prashna astrology. It creates the chart,
    analyzes all factors, and provides a complete judgment with timing.

    Args:
        question: The question text
        question_dt: Time the question was asked
        latitude: Geographic latitude
        longitude: Geographic longitude
        category: Question category

    Returns:
        PrashnaResult with complete analysis and recommendation

    Example:
        >>> from datetime import datetime
        >>> result = analyze_prashna(
        ...     "Will I get the job?",
        ...     datetime(2024, 6, 15, 10, 30, 0),
        ...     28.6139,
        ...     77.2090,
        ...     PrashnaCategory.CAREER
        ... )
        >>> result.judgment
        <PrashnaJudgment.FAVORABLE: 'favorable'>
    """
    # Create chart
    chart = create_prashna_chart(question, question_dt, latitude, longitude, category)

    # Judge the prashna
    judgment, strength_score = judge_prashna(chart)

    # Predict timing
    timing = predict_timing(chart)

    # Get category-specific analysis
    category_analysis_map = {
        PrashnaCategory.HEALTH: analyze_health_prashna,
        PrashnaCategory.MARRIAGE: analyze_marriage_prashna,
        PrashnaCategory.CAREER: analyze_career_prashna,
        PrashnaCategory.TRAVEL: analyze_travel_prashna,
        PrashnaCategory.LOST_OBJECTS: analyze_lost_object_prashna,
        PrashnaCategory.LEGAL: analyze_legal_prashna,
    }

    category_func = category_analysis_map.get(category)
    if category_func:
        category_analysis = category_func(chart)
    else:
        # Default analysis for other categories
        sig_analysis = analyze_significator(chart)
        category_analysis = {
            "analysis": f"Analysis for {category.value}",
            "factors": sig_analysis["factors"],
            "outlook": "See overall judgment",
        }

    # Collect all factors
    lagna_analysis = analyze_lagna_strength(chart)
    moon_analysis = analyze_moon_condition(chart)
    sig_analysis = analyze_significator(chart)

    favorable_factors = []
    unfavorable_factors = []

    for factor in lagna_analysis["factors"] + moon_analysis["factors"] + sig_analysis["factors"]:
        if any(word in factor.lower() for word in ["good", "strong", "favorable", "excellent"]):
            favorable_factors.append(factor)
        elif any(word in factor.lower() for word in ["weak", "bad", "unfavorable", "challenging"]):
            unfavorable_factors.append(factor)

    # Add category-specific factors
    for factor in category_analysis["factors"]:
        if any(
            word in factor.lower()
            for word in ["good", "strong", "favorable", "excellent", "likely"]
        ):
            favorable_factors.append(factor)
        else:
            unfavorable_factors.append(factor)

    # Build recommendation
    recommendations = []
    recommendations.append(f"Overall judgment: {judgment.value}")
    recommendations.append(f"Estimated timing: {timing['estimate']}")
    recommendations.append(f"Category outlook: {category_analysis['outlook']}")

    if judgment == PrashnaJudgment.FAVORABLE:
        recommendations.append("Proceed with confidence. The stars favor this endeavor.")
    elif judgment == PrashnaJudgment.NEUTRAL:
        recommendations.append("Outcome is neutral. Success depends on effort and circumstances.")
    elif judgment == PrashnaJudgment.DELAYED:
        recommendations.append("Delays expected. Be patient and persistent.")
    else:
        recommendations.append("Unfavorable indications. Consider alternative approaches.")

    recommendation = " ".join(recommendations)

    return PrashnaResult(
        chart=chart,
        judgment=judgment,
        strength_score=strength_score,
        favorable_factors=favorable_factors,
        unfavorable_factors=unfavorable_factors,
        timing=timing,
        recommendation=recommendation,
    )


__all__ = [
    "analyze_career_prashna",
    "analyze_health_prashna",
    "analyze_lagna_strength",
    "analyze_legal_prashna",
    "analyze_lost_object_prashna",
    "analyze_marriage_prashna",
    "analyze_moon_condition",
    "analyze_prashna",
    "analyze_significator",
    "analyze_travel_prashna",
    "create_prashna_chart",
    "get_significator",
    "judge_prashna",
    "predict_timing",
]
