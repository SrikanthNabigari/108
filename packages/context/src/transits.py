"""Gochara (Transit) analysis module for 108 Vedic Astrology app.

This module implements transit analysis based on the Gochara system, which evaluates
how transiting planets affect the natal Moon's position. It includes:

- Gochara (planetary transit) analysis for each planet
- Sade Sati detection (7.5-year Saturn cycle)
- Dhaiya (Kantaka Shani) detection (4th/8th Saturn from Moon)
- Vedha (obstruction) analysis for favorable transits
- Complete transit summaries for all planets

The system calculates planetary positions relative to the natal Moon (1-12 houses)
and determines whether transits are favorable, unfavorable, or obstructed.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_nakshatra_transit_rules, get_transit_rules

# Module-level cache for transit rules
_transit_rules_cache: dict[str, Any] | None = None


def _get_transit_rules() -> dict[str, Any]:
    """Get cached transit rules from JSON."""
    global _transit_rules_cache
    if _transit_rules_cache is None:
        _transit_rules_cache = get_transit_rules()
    return _transit_rules_cache


def _get_gochara_favorable() -> dict[str, list[int]]:
    """Get gochara favorable positions from JSON, with fallback."""
    rules = _get_transit_rules()
    data = rules.get("gochara_favorable", {})

    if data:
        return data

    # Fallback to defaults
    return {
        "sun": [3, 6, 10, 11],
        "moon": [1, 3, 6, 7, 10, 11],
        "mars": [3, 6, 11],
        "mercury": [2, 4, 6, 8, 10, 11],
        "jupiter": [2, 5, 7, 9, 11],
        "venus": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "saturn": [3, 6, 11],
        "rahu": [3, 6, 10, 11],
        "ketu": [3, 6, 10, 11],
    }


def _get_vedha_points() -> dict[str, dict[int, int]]:
    """Get vedha points from JSON, with fallback."""
    rules = _get_transit_rules()
    data = rules.get("vedha_points", {})

    if data:
        # Convert string keys to int for nested dicts
        result = {}
        for planet, vedha_dict in data.items():
            if isinstance(vedha_dict, dict):
                result[planet] = {int(k): v for k, v in vedha_dict.items()}
        return result

    # Fallback to defaults
    return {
        "sun": {3: 9, 6: 12, 10: 4, 11: 5},
        "moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
        "mars": {3: 12, 6: 9, 11: 5},
        "mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
        "jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
        "venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
        "saturn": {3: 12, 6: 9, 11: 5},
    }


def _get_transit_effects() -> dict[str, dict[int, list[str]]]:
    """Get transit effects from JSON, with fallback."""
    rules = _get_transit_rules()
    data = rules.get("transit_effects", {})

    if data:
        # Convert string keys to int and flatten positive/negative to single list
        result = {}
        for planet, house_dict in data.items():
            result[planet] = {}
            for house_str, effects in house_dict.items():
                house = int(house_str)
                if isinstance(effects, dict):
                    # Combine positive and negative effects
                    combined = effects.get("positive", []) + effects.get("negative", [])
                    result[planet][house] = combined
                elif isinstance(effects, list):
                    result[planet][house] = effects
        return result

    # Will use inline defaults in the code
    return {}


# Backwards-compatible exports (loaded at module level)
GOCHARA_FAVORABLE = _get_gochara_favorable()
VEDHA_POINTS = _get_vedha_points()
_transit_effects_from_json = _get_transit_effects()

# Transit effects for each planet in each house from Moon
# Use JSON data if available, otherwise use defaults
_DEFAULT_TRANSIT_EFFECTS = {
    "sun": {
        1: ["Authority", "Fame", "Confidence", "Leadership"],
        2: ["Financial challenges", "Speech issues", "Family tension"],
        3: ["Courage", "Siblings support", "Short travels", "Communication"],
        4: ["Home troubles", "Mother's health", "Property issues"],
        5: ["Creative blocks", "Children concerns", "Speculation losses"],
        6: ["Disease", "Enemies active", "Debt", "Disputes"],
        7: ["Partnership stress", "Marriage discord", "Business conflict"],
        8: ["Obstacles", "Hidden enemies", "Financial loss", "Health issues"],
        9: ["Good fortune", "Pilgrimage", "Teaching success", "Philosophy"],
        10: ["Career progress", "Authority gains", "Father's support", "Recognition"],
        11: ["Gains", "Friends support", "Network expansion", "Success"],
        12: ["Expenditure", "Foreign travels", "Hospitalization", "Spiritual pursuits"],
    },
    "moon": {
        1: ["Peace", "Emotional stability", "Mental clarity", "Comfort"],
        2: ["Good family relations", "Wealth gains", "Good food"],
        3: ["Courage", "Siblings support", "Short travels", "Communication"],
        4: ["Home comforts", "Mother's blessings", "Property gains"],
        5: ["Progeny joy", "Creative pursuits", "Pleasure"],
        6: ["Disease", "Enemies", "Debts", "Competitors"],
        7: ["Marriage joy", "Partnership harmony", "Business growth"],
        8: ["Mental agitation", "Enemies increase", "Health issues"],
        9: ["Spiritual growth", "Good karma", "Teacher's grace"],
        10: ["Career progress", "Public recognition", "Authority"],
        11: ["Gains", "Friendship", "Wish fulfillment"],
        12: ["Expenditure", "Travels", "Bed pleasures", "Hospitalization"],
    },
    "mars": {
        1: ["Courage", "Anger", "Conflicts", "Accidents risk"],
        2: ["Family discord", "Speech problems", "Financial pressure"],
        3: ["Courage", "Military success", "Athletic achievement"],
        4: ["Landed property", "Vehicles", "Mother's trouble"],
        5: ["Children issues", "Speculation losses", "Creative blocks"],
        6: ["Enemies defeated", "Disease recovery", "Competition success"],
        7: ["Marriage discord", "Partnership conflict", "Legal battles"],
        8: ["Obstacles", "Accidents", "Surgery risk", "Hidden dangers"],
        9: ["Religious zeal", "Success in pursuit", "Warrior spirit"],
        10: ["Career progress", "Authority", "Leadership", "Success"],
        11: ["Gains from efforts", "Elder brother support"],
        12: ["Expenditure", "Injuries", "Hidden enemies", "Legal troubles"],
    },
    "mercury": {
        1: ["Nervousness", "Intellectual confusion", "Communication issues"],
        2: ["Financial gains", "Business success", "Good speech"],
        3: ["Intelligence", "Communication", "Business expansion"],
        4: ["Mental peace", "Educational pursuits", "Property"],
        5: ["Intellectual pursuits", "Entertainment", "Speculation"],
        6: ["Mental conflict", "Enemies through words", "Health issues"],
        7: ["Partnership communication", "Marriage adjustment", "Trade success"],
        8: ["Mental agitation", "Deception risk", "Intellectual blocks"],
        9: ["Spiritual learning", "Good karma", "Pilgrimage"],
        10: ["Career progress", "Intellectual recognition", "Business growth"],
        11: ["Gains through commerce", "Networking", "Friendships"],
        12: ["Mental confusion", "Travels", "Expenditure", "Deception"],
    },
    "jupiter": {
        1: ["Wisdom", "Spiritual inclination", "Good fortune", "Health"],
        2: ["Wealth gains", "Family prosperity", "Inheritance"],
        3: ["Intellectual growth", "Communication skill", "Younger brother support"],
        4: ["Comfort", "Property", "Mother's blessings", "Peace"],
        5: ["Progeny joy", "Creative success", "Spiritual advancement"],
        6: ["Enemy defeat", "Health improvement", "Debt relief"],
        7: ["Marriage harmony", "Partnership success", "Relationship growth"],
        8: ["Hidden obstacles", "Secret gains", "Occult interest"],
        9: ["Spirituality peak", "Pilgrimage", "Teacher's grace", "Good karma"],
        10: ["Career peak", "Fame", "Leadership", "Success", "Authority"],
        11: ["Major gains", "Friendship expansion", "Wishes fulfilled"],
        12: ["Spiritual pursuits", "Monastic interests", "Hidden gains"],
    },
    "venus": {
        1: ["Pleasure", "Attraction", "Sensuality", "Comfort"],
        2: ["Wealth", "Luxury", "Family happiness", "Good food"],
        3: ["Creativity", "Communication", "Short travels", "Harmony"],
        4: ["Home comforts", "Vehicles", "Property", "Mother's love"],
        5: ["Romance", "Children", "Pleasures", "Entertainment"],
        6: ["Relationship discord", "Financial strain", "Enemies"],
        7: ["Marriage peak", "Partnership harmony", "Love relationship"],
        8: ["Relationship challenges", "Financial stress", "Temptations"],
        9: ["Spiritual love", "Devotion", "Pilgrimage", "Good karma"],
        10: ["Career satisfaction", "Artistic success", "Public approval"],
        11: ["Social gains", "Friendships", "Wish fulfillment"],
        12: ["Expenditure on pleasure", "Foreign travels", "Bedroom joys"],
    },
    "saturn": {
        1: ["Heaviness", "Delays", "Restrictions", "Discipline needed"],
        2: ["Financial pressure", "Family burden", "Dental issues"],
        3: ["Delays in communication", "Struggles", "Hard work needed"],
        4: ["Property issues", "Mother's health", "Domestic stress"],
        5: ["Progeny delays", "Creative blocks", "Speculation losses"],
        6: ["Disease", "Enemies defeated slowly", "Hard labor"],
        7: ["Marriage delays", "Partnership strain", "Patience needed"],
        8: ["Maximum obstacles", "Health crises", "Financial loss"],
        9: ["Spiritual discipline", "Hard karma", "Meditation"],
        10: ["Career obstacles", "Delayed promotions", "Hard work success"],
        11: ["Slow gains", "Friendships based on karma", "Patience"],
        12: ["Expenditure", "Hospitalization", "Seclusion", "Spiritual withdrawal"],
    },
    "rahu": {
        1: ["Confusion", "Obsession", "Illusion", "Worldly desires"],
        2: ["Wealth through unconventional means", "Speech confusion"],
        3: ["Risk-taking", "Unconventional pursuits", "Communication issues"],
        4: ["Property complications", "Family drama", "Ancestors' influence"],
        5: ["Speculation", "Unconventional progeny", "Entertainment"],
        6: ["Disease", "Enemies", "Legal complications"],
        7: ["Unusual partnership", "Marriage complications", "Confusion"],
        8: ["Obstacles", "Obsessions", "Hidden enemies"],
        9: ["Foreign travel", "Unconventional spirituality", "Pilgrimages"],
        10: ["Unusual career growth", "Fame through unconventional means"],
        11: ["Unusual gains", "Networking with unusual people"],
        12: ["Foreign travels", "Hidden expenditure", "Occult interests"],
    },
    "ketu": {
        1: ["Spiritual inclination", "Detachment", "Confusion", "Isolation"],
        2: ["Financial dissatisfaction", "Detachment from family"],
        3: ["Communication blockages", "Spiritual interests", "Travel"],
        4: ["Property disputes", "Detachment from home", "Spiritual pursuits"],
        5: ["Progeny obstacles", "Detachment from children", "Spiritual creativity"],
        6: ["Hidden disease", "Enemies defeated", "Occult interests"],
        7: ["Marriage detachment", "Partnership complications", "Separative tendency"],
        8: ["Occult interests", "Hidden knowledge", "Spiritual transformation"],
        9: ["High spirituality", "Liberation pursuits", "Pilgrimages"],
        10: ["Career confusion", "Detachment from ambitions", "Occult work"],
        11: ["Gains through detachment", "Unusual friendships"],
        12: ["Spiritual seclusion", "Occult practices", "Detachment"],
    },
}

# Use JSON data if available, otherwise use defaults
TRANSIT_EFFECTS = (
    _transit_effects_from_json if _transit_effects_from_json else _DEFAULT_TRANSIT_EFFECTS
)


def _calculate_house_from_moon(natal_moon_rashi: int, transit_rashi: int) -> int:
    """Calculate house position of transit planet relative to natal Moon.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11, where 0=Aries, 11=Pisces)
        transit_rashi: Transit planet's rashi (0-11)

    Returns:
        House number from Moon (1-12, where 1 = same sign as Moon)
    """
    house = ((transit_rashi - natal_moon_rashi) % 12) + 1
    return house


def _get_transit_effects_for_house(planet: str, house_from_moon: int) -> list[str]:
    """Get the effects of a planet in a specific house from Moon.

    Args:
        planet: Planet name (lowercase)
        house_from_moon: House number (1-12)

    Returns:
        List of effect descriptions
    """
    if planet in TRANSIT_EFFECTS and house_from_moon in TRANSIT_EFFECTS[planet]:
        return TRANSIT_EFFECTS[planet][house_from_moon]
    return []


def check_sade_sati(natal_moon_rashi: int, saturn_rashi: int) -> dict[str, Any]:
    """Check if Sade Sati (7.5-year Saturn transit) is active and determine phase.

    Sade Sati occurs when Saturn transits:
    - 12th from Moon (Rising phase) - approximately 2.5 years
    - 1st from Moon (Peak phase) - approximately 2.5 years
    - 2nd from Moon (Setting phase) - approximately 2.5 years

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        saturn_rashi: Current transiting Saturn's rashi (0-11)

    Returns:
        Dictionary containing:
            - active (bool): Whether Sade Sati is currently active
            - phase (str|None): "rising", "peak", or "setting" if active
            - house_from_moon (int): Saturn's house position from Moon (1-12)
            - description (str): Human-readable description
            - effects (list): List of expected effects during this phase
    """
    house_from_moon = _calculate_house_from_moon(natal_moon_rashi, saturn_rashi)

    if house_from_moon == 12:  # noqa: SIM116
        return {
            "active": True,
            "phase": "rising",
            "house_from_moon": 12,
            "description": "Sade Sati - Rising Phase (Saturn entering 12th from Moon)",
            "effects": [
                "Mental stress and anxiety",
                "Financial pressure increasing",
                "Hidden enemies becoming active",
                "Unexpected expenses",
                "Sleep disturbances",
            ],
            "duration_years": 2.5,
            "remedies": [
                "Recite Hanuman Chalisa",
                "Donate mustard oil on Saturdays",
                "Worship Lord Shiva",
                "Practice meditation",
            ],
        }
    elif house_from_moon == 1:
        return {
            "active": True,
            "phase": "peak",
            "house_from_moon": 1,
            "description": "Sade Sati - Peak Phase (Saturn conjunct natal Moon)",
            "effects": [
                "Maximum challenges and obstacles",
                "Health concerns may arise",
                "Emotional turbulence and depression",
                "Career disruptions possible",
                "Relationships strained",
            ],
            "duration_years": 2.5,
            "remedies": [
                "Perform Saturn puja",
                "Donate to the underprivileged",
                "Chant Shani Mantras",
                "Serve the elderly",
            ],
        }
    elif house_from_moon == 2:
        return {
            "active": True,
            "phase": "setting",
            "house_from_moon": 2,
            "description": "Sade Sati - Setting Phase (Saturn departing 2nd from Moon)",
            "effects": [
                "Financial concerns and constraints",
                "Family relationship issues",
                "Gradual relief from previous phases",
                "Continued caution needed",
                "Slow recovery beginning",
            ],
            "duration_years": 2.5,
            "remedies": [
                "Continue Saturn worship",
                "Give alms on Saturdays",
                "Build helping attitude",
                "Patience and acceptance",
            ],
        }
    else:
        return {
            "active": False,
            "phase": None,
            "house_from_moon": house_from_moon,
            "description": f"Sade Sati not active (Saturn in house {house_from_moon} from Moon)",
            "effects": [],
            "duration_years": None,
            "remedies": [],
        }


def check_dhaiya(natal_moon_rashi: int, saturn_rashi: int) -> dict[str, Any]:
    """Check for Dhaiya (Small Panoti / Kantaka Shani).

    Dhaiya occurs when Saturn transits the 4th or 8th house from the natal Moon.
    Each phase lasts approximately 2.5 years.

    This is a subset of challenges within Sade Sati but also occurs separately
    when Saturn is in 4th or 8th from Moon.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        saturn_rashi: Current transiting Saturn's rashi (0-11)

    Returns:
        Dictionary containing:
            - active (bool): Whether Dhaiya is active
            - type (str|None): "kantaka_shani" if in 4th, "ashtama_shani" if in 8th
            - house_from_moon (int): Saturn's house position (1-12)
            - description (str): Human-readable description
            - effects (list): List of expected effects
    """
    house_from_moon = _calculate_house_from_moon(natal_moon_rashi, saturn_rashi)

    if house_from_moon == 4:
        return {
            "active": True,
            "type": "kantaka_shani",
            "house_from_moon": 4,
            "description": "Kantaka Shani (Saturn in 4th from Moon) - Dhaiya Period",
            "effects": [
                "Domestic troubles and family discord",
                "Vehicle problems and accidents",
                "Mother's health issues",
                "Property and land disputes",
                "Mental restlessness",
                "Home-related financial losses",
            ],
            "duration_years": 2.5,
            "remedies": [
                "Perform Saturn rituals",
                "Care for mother's wellbeing",
                "Avoid rash decisions",
                "Practice equanimity",
            ],
        }
    elif house_from_moon == 8:
        return {
            "active": True,
            "type": "ashtama_shani",
            "house_from_moon": 8,
            "description": "Ashtama Shani (Saturn in 8th from Moon) - Dhaiya Period",
            "effects": [
                "Sudden obstacles and blockages",
                "Health issues and medical concerns",
                "Hidden problems surfacing",
                "Longevity concerns (psychological)",
                "Financial losses possible",
                "Accidents and injuries risk",
                "Mysterious troubles",
            ],
            "duration_years": 2.5,
            "remedies": [
                "Strengthen health practices",
                "Perform protective rituals",
                "Avoid risky activities",
                "Seek medical advice proactively",
            ],
        }
    else:
        return {
            "active": False,
            "type": None,
            "house_from_moon": house_from_moon,
            "description": f"Dhaiya not active (Saturn in house {house_from_moon} from Moon)",
            "effects": [],
            "duration_years": None,
            "remedies": [],
        }


def get_sade_sati_dates(
    natal_moon_rashi: int,
    current_saturn_rashi: int,  # noqa: ARG001
) -> dict[str, Any]:
    """Compute approximate start/end dates for each Sade Sati phase.

    Uses ephemeris binary search to find when Saturn enters the 12th, 1st,
    and 2nd rashis from the natal Moon.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11).
        current_saturn_rashi: Current Saturn's rashi (0-11).

    Returns:
        Dictionary with ``phase_dates`` mapping phase names to
        ``{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}``.
    """
    from datetime import UTC, datetime, timedelta

    from packages.cosmos.src.ephemeris import find_planet_rashi_ingress, get_julian_day

    now = datetime.now(tz=UTC)
    # Search window: 5 years back to 5 years forward
    start_jd = get_julian_day(now - timedelta(days=5 * 365))
    end_jd = get_julian_day(now + timedelta(days=5 * 365))

    # The three rashis for Sade Sati
    rashi_12th = (natal_moon_rashi - 1) % 12  # rising
    rashi_1st = natal_moon_rashi  # peak
    rashi_2nd = (natal_moon_rashi + 1) % 12  # setting
    rashi_3rd = (natal_moon_rashi + 2) % 12  # end of Sade Sati

    phase_dates: dict[str, dict[str, str]] = {}

    def _jd_to_date_str(jd: float) -> str:
        """Convert JD to ISO date string."""
        import swisseph as swe

        y, m, d, _h = swe.revjul(jd)
        return f"{y:04d}-{m:02d}-{int(d):02d}"

    # Build continuous timeline: each phase ends where the next begins
    # Find start of first phase (rising = Saturn enters 12th from Moon)
    rising_start = find_planet_rashi_ingress(
        "saturn", rashi_12th, start_jd, end_jd, find_first=True
    )
    if rising_start is None:
        return {"phase_dates": phase_dates}

    # Peak start = first time Saturn enters Moon's rashi after rising start
    peak_start = find_planet_rashi_ingress(
        "saturn", rashi_1st, rising_start, end_jd, find_first=True
    )

    # Setting start = first time Saturn enters 2nd from Moon after peak start
    setting_start = (
        find_planet_rashi_ingress("saturn", rashi_2nd, peak_start, end_jd, find_first=True)
        if peak_start
        else None
    )

    # Setting end = first time Saturn enters 3rd from Moon after setting start
    setting_end = (
        find_planet_rashi_ingress("saturn", rashi_3rd, setting_start, end_jd, find_first=True)
        if setting_start
        else None
    )

    phase_dates["rising"] = {
        "start": _jd_to_date_str(rising_start),
        "end": _jd_to_date_str(peak_start) if peak_start else "",
    }
    if peak_start:
        phase_dates["peak"] = {
            "start": _jd_to_date_str(peak_start),
            "end": _jd_to_date_str(setting_start) if setting_start else "",
        }
    if setting_start:
        phase_dates["setting"] = {
            "start": _jd_to_date_str(setting_start),
            "end": _jd_to_date_str(setting_end) if setting_end else "",
        }

    return {"phase_dates": phase_dates}


def get_dhaiya_dates(
    natal_moon_rashi: int,
    current_saturn_rashi: int,
) -> dict[str, Any]:
    """Compute approximate start/end dates for an active Dhaiya phase.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11).
        current_saturn_rashi: Current Saturn's rashi (0-11).

    Returns:
        Dictionary with ``phase_dates`` mapping the dhaiya type to
        ``{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}``.
    """
    from datetime import UTC, datetime, timedelta

    from packages.cosmos.src.ephemeris import find_planet_rashi_ingress, get_julian_day

    house_from_moon = _calculate_house_from_moon(natal_moon_rashi, current_saturn_rashi)
    if house_from_moon not in (4, 8):
        return {"phase_dates": {}}

    now = datetime.now(tz=UTC)
    start_jd = get_julian_day(now - timedelta(days=5 * 365))
    end_jd = get_julian_day(now + timedelta(days=5 * 365))

    import swisseph as swe

    def _jd_to_date_str(jd: float) -> str:
        y, m, d, _h = swe.revjul(jd)
        return f"{y:04d}-{m:02d}-{int(d):02d}"

    phase_name = "kantaka_shani" if house_from_moon == 4 else "ashtama_shani"
    target_rashi = current_saturn_rashi
    next_rashi = (current_saturn_rashi + 1) % 12

    ingress_jd = find_planet_rashi_ingress("saturn", target_rashi, start_jd, end_jd)
    end_jd_phase = (
        find_planet_rashi_ingress("saturn", next_rashi, ingress_jd, end_jd, find_first=True)
        if ingress_jd
        else None
    )

    phase_dates: dict[str, dict[str, str]] = {}
    if ingress_jd:
        phase_dates[phase_name] = {
            "start": _jd_to_date_str(ingress_jd),
            "end": _jd_to_date_str(end_jd_phase) if end_jd_phase else "",
        }

    return {"phase_dates": phase_dates}


def get_gochara(
    natal_moon_rashi: int,
    transit_planet: str,
    transit_rashi: int,
    all_transit_rashis: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Analyze a single planet's transit (Gochara) effects.

    This function determines whether a transiting planet is in a favorable,
    unfavorable, or obstructed position relative to the natal Moon.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        transit_planet: Planet name in lowercase (sun, moon, mars, mercury,
            jupiter, venus, saturn, rahu, ketu)
        transit_rashi: Current transit planet's rashi (0-11)
        all_transit_rashis: Optional dict of all transit planet positions for
            vedha (obstruction) analysis. Format: {planet_name: rashi_number}

    Returns:
        Dictionary containing:
            - planet (str): Planet name
            - transit_sign (int): Transit rashi (0-11)
            - house_from_moon (int): Position relative to Moon (1-12)
            - is_favorable (bool): Whether house is favorable for this planet
            - has_vedha (bool): Whether favorable position is obstructed
            - vedha_by (str|None): Planet causing obstruction, if any
            - net_effect (str): "favorable" or "unfavorable" after vedha analysis
            - effects (list): Description of expected effects
    """
    house_from_moon = _calculate_house_from_moon(natal_moon_rashi, transit_rashi)

    # Normalize planet name to lowercase
    planet_lower = transit_planet.lower()

    # Check if position is naturally favorable for this planet
    favorable_houses = GOCHARA_FAVORABLE.get(planet_lower, [])
    is_favorable = house_from_moon in favorable_houses

    # Check for Vedha (obstruction) of favorable position
    has_vedha = False
    vedha_by = None

    if is_favorable and all_transit_rashis:
        # Get the vedha house for this planet in this position
        vedha_house = VEDHA_POINTS.get(planet_lower, {}).get(house_from_moon)

        if vedha_house is not None:
            # Check if any other planet is in the vedha house
            for other_planet, other_rashi in all_transit_rashis.items():
                if other_planet.lower() == planet_lower:
                    continue

                other_house = _calculate_house_from_moon(natal_moon_rashi, other_rashi)

                if other_house == vedha_house:
                    # Sun-Saturn don't cause vedha to each other
                    planet_lower_normalized = planet_lower.lower()
                    other_planet_normalized = other_planet.lower()

                    sun_saturn_exception = (
                        planet_lower_normalized == "sun" and other_planet_normalized == "saturn"
                    ) or (planet_lower_normalized == "saturn" and other_planet_normalized == "sun")

                    if not sun_saturn_exception:
                        has_vedha = True
                        vedha_by = other_planet_normalized
                        break

    # Determine net effect
    net_effect = "favorable" if (is_favorable and not has_vedha) else "unfavorable"

    # Get effects list
    effects = _get_transit_effects_for_house(planet_lower, house_from_moon)

    return {
        "planet": planet_lower,
        "transit_sign": transit_rashi,
        "house_from_moon": house_from_moon,
        "is_favorable": is_favorable,
        "has_vedha": has_vedha,
        "vedha_by": vedha_by,
        "net_effect": net_effect,
        "effects": effects,
    }


def get_full_transit_analysis(
    natal_moon_rashi: int, transit_positions: dict[str, int]
) -> dict[str, Any]:
    """Complete transit analysis for all planets.

    This provides a comprehensive analysis of current transits, including
    Sade Sati, Dhaiya, and individual planet transits with vedha analysis.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        transit_positions: Dictionary mapping planet names to current rashis
            Format: {planet_name: rashi_0_to_11}

    Returns:
        Dictionary containing:
            - natal_moon_sign (int): Natal Moon rashi for reference
            - sade_sati (dict): Sade Sati analysis
            - dhaiya (dict): Dhaiya analysis
            - planet_transits (dict): Individual planet analyses
            - summary (dict): Overall transit summary
    """
    # Validate input
    if not isinstance(transit_positions, dict):
        raise ValueError("transit_positions must be a dictionary")

    if not all(isinstance(v, int) and 0 <= v <= 11 for v in transit_positions.values()):
        raise ValueError("All rashi values must be integers 0-11")

    # Saturn-specific analyses
    saturn_rashi = transit_positions.get("saturn")
    sade_sati_analysis = (
        check_sade_sati(natal_moon_rashi, saturn_rashi)
        if saturn_rashi is not None
        else {"active": False, "phase": None}
    )
    dhaiya_analysis = (
        check_dhaiya(natal_moon_rashi, saturn_rashi)
        if saturn_rashi is not None
        else {"active": False, "type": None}
    )

    # Analyze each planet's transit
    planet_transits = {}
    favorable_count = 0
    unfavorable_count = 0

    for planet, rashi in transit_positions.items():
        gochara = get_gochara(natal_moon_rashi, planet, rashi, transit_positions)
        planet_transits[planet] = gochara

        if gochara["net_effect"] == "favorable":
            favorable_count += 1
        else:
            unfavorable_count += 1

    # Determine overall trend
    trend = _determine_overall_trend(favorable_count, unfavorable_count)

    summary = {
        "favorable_count": favorable_count,
        "unfavorable_count": unfavorable_count,
        "total_planets_analyzed": len(planet_transits),
        "overall_trend": trend,
        "saturn_active": saturn_rashi is not None
        and (sade_sati_analysis["active"] or dhaiya_analysis["active"]),
    }

    return {
        "natal_moon_sign": natal_moon_rashi,
        "sade_sati": sade_sati_analysis,
        "dhaiya": dhaiya_analysis,
        "planet_transits": planet_transits,
        "summary": summary,
    }


def _determine_overall_trend(favorable: int, unfavorable: int) -> str:
    """Determine overall transit trend based on planet counts.

    Args:
        favorable: Number of favorable planet transits
        unfavorable: Number of unfavorable planet transits

    Returns:
        Trend string: "highly_favorable", "favorable", "mixed",
                      "unfavorable", or "challenging"
    """
    if favorable > unfavorable + 2:
        return "highly_favorable"
    elif favorable > unfavorable:
        return "favorable"
    elif unfavorable > favorable + 2:
        return "challenging"
    elif unfavorable > favorable:
        return "unfavorable"
    else:
        return "mixed"


def get_transiting_planet_house(
    natal_moon_rashi: int,
    transit_planet: str,  # noqa: ARG001
    transit_rashi: int,
) -> int:
    """Get the house position of a transiting planet from natal Moon.

    Convenience function for simple house position calculation.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        transit_planet: Planet name (not used, for consistency with other functions)
        transit_rashi: Transit planet's rashi (0-11)

    Returns:
        House number from Moon (1-12)
    """
    return _calculate_house_from_moon(natal_moon_rashi, transit_rashi)


def is_planet_favorable_in_house(planet: str, house_from_moon: int) -> bool:
    """Check if a planet is in a naturally favorable house from Moon.

    Args:
        planet: Planet name (lowercase)
        house_from_moon: House position (1-12)

    Returns:
        True if house is favorable for this planet, False otherwise
    """
    favorable_houses = GOCHARA_FAVORABLE.get(planet.lower(), [])
    return house_from_moon in favorable_houses


def validate_transit_data(
    natal_moon_rashi: int, transit_positions: dict[str, int]
) -> tuple[bool, str]:
    """Validate transit data for consistency and validity.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        transit_positions: Dictionary of transit planet positions

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not isinstance(natal_moon_rashi, int):
        return False, "natal_moon_rashi must be an integer"

    if not (0 <= natal_moon_rashi <= 11):
        return False, "natal_moon_rashi must be between 0 and 11"

    if not isinstance(transit_positions, dict):
        return False, "transit_positions must be a dictionary"

    if not transit_positions:
        return False, "transit_positions cannot be empty"

    for planet, rashi in transit_positions.items():
        if not isinstance(planet, str):
            return False, f"Planet name must be string, got {type(planet)}"

        if not isinstance(rashi, int):
            return False, f"Rashi for {planet} must be integer, got {type(rashi)}"

        if not (0 <= rashi <= 11):
            return (False, f"Rashi for {planet} must be between 0 and 11, got {rashi}")

    return True, "Data is valid"


def get_transit_positions(julian_day: float, ayanamsa: str = "lahiri") -> dict[str, dict[str, Any]]:
    """Get current planetary transit positions.

    This is a convenience function that wraps cosmos.get_all_planets
    to provide transit positions with additional transit-specific metadata.

    Args:
        julian_day: Julian Day Number for the transit moment
        ayanamsa: Ayanamsa system to use (default: lahiri)

    Returns:
        Dictionary of planet positions with longitude, rashi, and degree

    Example:
        >>> from datetime import datetime
        >>> jd = get_julian_day(2026, 2, 4, 12.0)
        >>> transits = get_transit_positions(jd)
        >>> print(transits["saturn"]["rashi"])
    """
    # Import cosmos functions (lazy import to avoid circular dependency)
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from packages.cosmos.src import get_all_planets, get_ayanamsa

    # Convert ayanamsa string to float value
    ayanamsa_value = get_ayanamsa(julian_day, ayanamsa) if isinstance(ayanamsa, str) else ayanamsa

    # Get raw planetary positions
    planets_raw = get_all_planets(julian_day, ayanamsa=ayanamsa_value)

    # Add rashi information
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

    transit_positions = {}
    for planet_id, data in planets_raw.items():
        longitude = data["longitude"]
        rashi_idx = int(longitude // 30)
        transit_positions[planet_id] = {
            "longitude": longitude,
            "rashi": RASHI_NAMES[rashi_idx],
            "rashi_num": rashi_idx,
            "degree_in_rashi": longitude % 30,
            "is_retrograde": data.get("is_retrograde", False),
            "speed": data.get("speed", 0.0),
        }

    return transit_positions


# ============================================================================
# Nakshatra Transit Effects
# ============================================================================

_nakshatra_transit_cache: dict[str, Any] | None = None


def _get_nakshatra_transit_rules() -> dict[str, Any]:
    """Get cached nakshatra transit rules from JSON."""
    global _nakshatra_transit_cache
    if _nakshatra_transit_cache is None:
        _nakshatra_transit_cache = get_nakshatra_transit_rules()
    return _nakshatra_transit_cache


def get_nakshatra_transit_effect(planet: str, nakshatra: str) -> dict[str, Any]:
    """Get transit effects for a planet in a specific nakshatra.

    Args:
        planet: Planet name (lowercase)
        nakshatra: Nakshatra name (e.g., "ashwini", "bharani")

    Returns:
        Dictionary with theme, positive, negative, best_for, avoid.
    """
    rules = _get_nakshatra_transit_rules()
    transits = rules.get("transits", {})
    planet_data = transits.get(planet.lower(), {})
    nak_data = planet_data.get(nakshatra.lower(), {})

    if not nak_data:
        return {"planet": planet.lower(), "nakshatra": nakshatra.lower(), "found": False}

    return {
        "planet": planet.lower(),
        "nakshatra": nakshatra.lower(),
        "found": True,
        "theme": nak_data.get("theme", ""),
        "positive": nak_data.get("positive", []),
        "negative": nak_data.get("negative", []),
        "best_for": nak_data.get("best_for", []),
        "avoid": nak_data.get("avoid", []),
    }


def get_enriched_transit_analysis(
    natal_moon_rashi: int,
    transit_data: dict[str, dict[str, Any]],
    chart: Any = None,
) -> dict[str, Any]:
    """Enriched transit analysis with nakshatra, combustion, retrograde, and ashtakavarga.

    This wraps get_full_transit_analysis and adds extra layers of information per planet.

    Args:
        natal_moon_rashi: Natal Moon's rashi (0-11)
        transit_data: Dict mapping planet name -> {rashi: int, nakshatra: str,
                      longitude: float, is_retrograde: bool}
        chart: Optional BirthChart for ashtakavarga scoring

    Returns:
        Enriched transit analysis dictionary.
    """
    # Build rashi-only dict for existing full transit analysis
    rashi_only: dict[str, int] = {}
    for planet, data in transit_data.items():
        rashi_val = data.get("rashi")
        if rashi_val is not None:
            rashi_only[planet.lower()] = rashi_val

    # Get base transit analysis
    base = get_full_transit_analysis(natal_moon_rashi, rashi_only)

    # Extract Sun longitude for combustion checks
    sun_data = transit_data.get("sun", {})
    sun_lon = sun_data.get("longitude", 0.0)

    # Lazy imports to avoid circular dependency
    from packages.self.src.combustion import check_combustion
    from packages.self.src.retrograde import get_retrograde_effects

    # Enrich each planet's transit
    for planet, data in transit_data.items():
        planet_lower = planet.lower()
        planet_transit = base.get("planet_transits", {}).get(planet_lower, {})
        if not planet_transit:
            continue

        # 1. Nakshatra transit effects
        nakshatra = data.get("nakshatra", "")
        if nakshatra:
            nak_effect = get_nakshatra_transit_effect(planet_lower, nakshatra)
            planet_transit["nakshatra_effects"] = nak_effect
        else:
            planet_transit["nakshatra_effects"] = {}

        # 2. Combustion check
        planet_lon = data.get("longitude", 0.0)
        is_retro = data.get("is_retrograde", False)
        if planet_lower != "sun":
            comb = check_combustion(planet_lower, planet_lon, sun_lon, is_retro)
            planet_transit["combustion"] = {
                "is_combust": comb["is_combust"],
                "is_deep_combust": comb["is_deep_combust"],
                "angular_distance": comb["angular_distance"],
            }
        else:
            planet_transit["combustion"] = {"is_combust": False, "is_deep_combust": False}

        # 3. Retrograde effects
        if is_retro and planet_lower in ("mars", "mercury", "jupiter", "venus", "saturn"):
            retro = get_retrograde_effects(planet_lower, is_natal=False)
            planet_transit["retrograde_effects"] = {
                "general": retro.get("general", [])[:3],
                "positive": retro.get("positive", [])[:2],
                "negative": retro.get("negative", [])[:2],
            }
        else:
            planet_transit["retrograde_effects"] = {}

        # 4. Ashtakavarga (if chart provided)
        if chart is not None and planet_lower not in ("rahu", "ketu"):
            try:
                from packages.core.src.constants import Planet
                from packages.self.src.ashtakavarga import get_transit_ashtakavarga_analysis

                planet_enum = Planet(planet_lower)
                transit_sign = data.get("rashi", 0)
                av_analysis = get_transit_ashtakavarga_analysis(planet_enum, transit_sign, chart)
                planet_transit["ashtakavarga"] = {
                    "bav_score": av_analysis["bav_score"],
                    "sav_score": av_analysis["sav_score"],
                    "strength_modifier": av_analysis["strength_modifier"],
                    "interpretation": av_analysis["bav_interpretation"],
                }
            except Exception:
                planet_transit["ashtakavarga"] = {}
        else:
            planet_transit["ashtakavarga"] = {}

    return base


# Standard Parashari aspects: all planets aspect 7th house from themselves.
# Mars also aspects 4th and 8th. Jupiter also aspects 5th and 9th. Saturn also aspects 3rd and 10th.
_SPECIAL_ASPECTS: dict[str, list[int]] = {
    "mars": [4, 8],
    "jupiter": [5, 9],
    "saturn": [3, 10],
}


def get_transit_aspects(
    transit_positions: dict[str, dict[str, Any]],
    natal_positions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Check if transiting planets aspect natal planets.

    Uses standard Parashari aspects:
    - All planets: 7th house aspect
    - Mars: additional 4th and 8th aspects
    - Jupiter: additional 5th and 9th aspects
    - Saturn: additional 3rd and 10th aspects

    Args:
        transit_positions: Dict mapping planet name -> {rashi: int, longitude: float, ...}
        natal_positions: Dict mapping planet name -> {rashi: int, longitude: float, ...}

    Returns:
        List of dicts with transit_planet, natal_planet, aspect_type, house_distance,
        and significance rating.

    Example:
        >>> aspects = get_transit_aspects(
        ...     {"saturn": {"rashi": 10}},
        ...     {"moon": {"rashi": 3}}
        ... )
        >>> len(aspects) > 0
        True
    """
    aspects: list[dict[str, Any]] = []

    for t_planet, t_data in transit_positions.items():
        t_rashi = t_data.get("rashi")
        if t_rashi is None:
            continue
        if isinstance(t_rashi, str):
            continue
        t_lower = t_planet.lower()

        # Build list of houses this planet aspects
        aspect_houses = [7]  # All planets aspect 7th
        if t_lower in _SPECIAL_ASPECTS:
            aspect_houses.extend(_SPECIAL_ASPECTS[t_lower])

        for n_planet, n_data in natal_positions.items():
            n_rashi = n_data.get("rashi")
            if n_rashi is None:
                continue
            if isinstance(n_rashi, str):
                continue

            # House distance from transit planet to natal planet
            house_dist = ((n_rashi - t_rashi) % 12) or 12

            if house_dist in aspect_houses:
                # Determine aspect type name
                aspect_type = {
                    7: "opposition",
                    4: "4th_aspect",
                    8: "8th_aspect",
                    5: "5th_aspect",
                    9: "9th_aspect",
                    3: "3rd_aspect",
                    10: "10th_aspect",
                }.get(house_dist, f"{house_dist}th")

                # Significance based on planets involved
                significance = _rate_aspect_significance(t_lower, n_planet.lower())

                aspects.append(
                    {
                        "transit_planet": t_lower,
                        "natal_planet": n_planet.lower(),
                        "aspect_type": aspect_type,
                        "house_distance": house_dist,
                        "transit_rashi": t_rashi,
                        "natal_rashi": n_rashi,
                        "significance": significance,
                    }
                )

    return aspects


def _rate_aspect_significance(transit_planet: str, natal_planet: str) -> str:
    """Rate the significance of a transit aspect.

    Args:
        transit_planet: Transiting planet name
        natal_planet: Natal planet name

    Returns:
        Significance string: "high", "medium", or "low"
    """
    # High significance: slow planets (Saturn, Jupiter, Rahu) aspecting personal planets
    slow_planets = {"saturn", "jupiter", "rahu", "ketu"}
    personal_planets = {"sun", "moon", "mars", "mercury", "venus"}

    if transit_planet in slow_planets and natal_planet in personal_planets:
        # Saturn/Jupiter on Moon/Sun is especially significant
        if transit_planet in ("saturn", "jupiter") and natal_planet in ("sun", "moon"):
            return "high"
        return "medium"

    if transit_planet in slow_planets and natal_planet in slow_planets:
        return "medium"

    return "low"


# Define public API
__all__ = [
    # Constants
    "GOCHARA_FAVORABLE",
    "TRANSIT_EFFECTS",
    "VEDHA_POINTS",
    "check_dhaiya",
    "check_sade_sati",
    "get_dhaiya_dates",
    "get_enriched_transit_analysis",
    "get_full_transit_analysis",
    # Main analysis functions
    "get_gochara",
    "get_nakshatra_transit_effect",
    "get_sade_sati_dates",
    "get_transit_aspects",
    "get_transit_positions",
    # Helper functions
    "get_transiting_planet_house",
    "is_planet_favorable_in_house",
    "validate_transit_data",
]
