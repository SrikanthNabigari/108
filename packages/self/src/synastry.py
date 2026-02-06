"""Synastry & Composite Chart Analysis for 108 Vedic Astrology.

Provides relationship analysis beyond Ashta Kuta by overlaying two charts,
analyzing cross-chart aspects, and computing midpoint composite charts.

Three analysis modes:
1. House Overlay -- place partner's planets in native's house framework
2. Cross-Chart Aspects -- find aspects between one person's planets and another's
3. Composite Chart -- midpoint chart representing the relationship itself
"""

from typing import Any

from packages.core.src.knowledge_loader import load_rules

# Ptolemaic aspects with their exact degrees and quality
ASPECT_DEFINITIONS: list[dict[str, Any]] = [
    {"name": "conjunction", "degree": 0, "quality": "variable"},
    {"name": "sextile", "degree": 60, "quality": "harmonious"},
    {"name": "square", "degree": 90, "quality": "challenging"},
    {"name": "trine", "degree": 120, "quality": "harmonious"},
    {"name": "opposition", "degree": 180, "quality": "challenging"},
]

# Parashari special aspects (additional to Ptolemaic)
# Mars: full aspect on 4th and 8th houses (90 and 210 degrees from itself)
# Jupiter: full aspect on 5th and 9th (120 and 240 degrees)
# Saturn: full aspect on 3rd and 10th (60 and 270 degrees)
PARASHARI_SPECIAL_ASPECTS: dict[str, list[dict[str, Any]]] = {
    "mars": [
        {"degree": 90, "name": "mars_4th_aspect", "quality": "challenging"},
        {"degree": 210, "name": "mars_8th_aspect", "quality": "challenging"},
    ],
    "jupiter": [
        {"degree": 120, "name": "jupiter_5th_aspect", "quality": "harmonious"},
        {"degree": 240, "name": "jupiter_9th_aspect", "quality": "harmonious"},
    ],
    "saturn": [
        {"degree": 60, "name": "saturn_3rd_aspect", "quality": "challenging"},
        {"degree": 270, "name": "saturn_10th_aspect", "quality": "challenging"},
    ],
}

# Luminaries get wider orbs in synastry
LUMINARY_PLANETS = {"sun", "moon"}

# Sign names for mapping sign index to name
SIGN_NAMES = [
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

# Planet significance levels for house overlay
PLANET_SIGNIFICANCE: dict[str, str] = {
    "sun": "very_high",
    "moon": "very_high",
    "venus": "very_high",
    "mars": "high",
    "jupiter": "high",
    "saturn": "moderate",
    "mercury": "moderate",
    "rahu": "low",
    "ketu": "low",
}


def _load_synastry_rules() -> dict[str, Any]:
    """Load synastry interpretation rules from knowledge base.

    Returns an empty dict if the file doesn't exist yet (knowledge-agent
    may not have created it).
    """
    data = load_rules("synastry_rules")
    return data.get("synastry_rules", {})


# ---------------------------------------------------------------------------
# Fallback interpretations (used when synastry_rules.json is not available)
# ---------------------------------------------------------------------------

_FALLBACK_HOUSE_OVERLAY: dict[str, dict[str, str]] = {
    "sun": {
        "1": "Partner's Sun in your 1st house -- they energize your identity and self-expression",
        "2": "Partner's Sun in your 2nd house -- they boost your finances and self-worth",
        "3": "Partner's Sun in your 3rd house -- stimulating communication and shared ideas",
        "4": "Partner's Sun in your 4th house -- they feel like home, deep emotional bond",
        "5": "Partner's Sun in your 5th house -- romance, creativity, and fun together",
        "6": "Partner's Sun in your 6th house -- they may push you toward better routines",
        "7": "Partner's Sun in your 7th house -- strong partnership and romantic attraction",
        "8": "Partner's Sun in your 8th house -- deep transformation, shared resources",
        "9": "Partner's Sun in your 9th house -- philosophical alignment, travel together",
        "10": "Partner's Sun in your 10th house -- they enhance your public image and career",
        "11": "Partner's Sun in your 11th house -- friendship, shared goals, social connection",
        "12": "Partner's Sun in your 12th house -- spiritual connection, hidden dynamics",
    },
    "moon": {
        "1": "Partner's Moon in your 1st house -- emotional attunement with your personality",
        "2": "Partner's Moon in your 2nd house -- comfort in shared material security",
        "3": "Partner's Moon in your 3rd house -- easy emotional communication",
        "4": "Partner's Moon in your 4th house -- deeply nurturing, feels like family",
        "5": "Partner's Moon in your 5th house -- emotional creativity, playful bond",
        "6": "Partner's Moon in your 6th house -- supportive in daily life and health",
        "7": "Partner's Moon in your 7th house -- deep emotional partnership",
        "8": "Partner's Moon in your 8th house -- intense emotional intimacy",
        "9": "Partner's Moon in your 9th house -- emotional growth through shared beliefs",
        "10": "Partner's Moon in your 10th house -- emotionally supportive of your ambitions",
        "11": "Partner's Moon in your 11th house -- emotional friendship and group harmony",
        "12": "Partner's Moon in your 12th house -- psychic bond, shared subconscious",
    },
    "venus": {
        "1": "Partner's Venus in your 1st house -- strong physical and romantic attraction",
        "2": "Partner's Venus in your 2nd house -- shared luxury and financial harmony",
        "3": "Partner's Venus in your 3rd house -- sweet communication, literary bonds",
        "4": "Partner's Venus in your 4th house -- love of home life together",
        "5": "Partner's Venus in your 5th house -- romantic bliss, creative harmony",
        "6": "Partner's Venus in your 6th house -- service-oriented love, health focus",
        "7": "Partner's Venus in your 7th house -- ideal romantic placement, strong marriage potential",
        "8": "Partner's Venus in your 8th house -- deeply passionate, financial partnership",
        "9": "Partner's Venus in your 9th house -- love through shared philosophy and travel",
        "10": "Partner's Venus in your 10th house -- public admiration, power couple",
        "11": "Partner's Venus in your 11th house -- friendship-based love, social harmony",
        "12": "Partner's Venus in your 12th house -- secret romance, spiritual love",
    },
    "mars": {
        "1": "Partner's Mars in your 1st house -- magnetic attraction, energy boost",
        "2": "Partner's Mars in your 2nd house -- motivated about shared finances",
        "3": "Partner's Mars in your 3rd house -- spirited debates and communication",
        "4": "Partner's Mars in your 4th house -- passionate home life, some friction",
        "5": "Partner's Mars in your 5th house -- passionate romance, competitive fun",
        "6": "Partner's Mars in your 6th house -- motivated to solve problems together",
        "7": "Partner's Mars in your 7th house -- intense attraction, possible arguments",
        "8": "Partner's Mars in your 8th house -- deeply transformative, sexual chemistry",
        "9": "Partner's Mars in your 9th house -- adventurous pursuits together",
        "10": "Partner's Mars in your 10th house -- career ambition boosted by partner",
        "11": "Partner's Mars in your 11th house -- shared goals and activism",
        "12": "Partner's Mars in your 12th house -- hidden passions, subconscious drives",
    },
    "jupiter": {
        "1": "Partner's Jupiter in your 1st house -- expansion of your personality and luck",
        "2": "Partner's Jupiter in your 2nd house -- financial growth through partnership",
        "3": "Partner's Jupiter in your 3rd house -- intellectual expansion together",
        "4": "Partner's Jupiter in your 4th house -- abundant home life and comfort",
        "5": "Partner's Jupiter in your 5th house -- joyful romance, children blessed",
        "6": "Partner's Jupiter in your 6th house -- helps overcome obstacles together",
        "7": "Partner's Jupiter in your 7th house -- excellent for marriage and partnership",
        "8": "Partner's Jupiter in your 8th house -- spiritual transformation together",
        "9": "Partner's Jupiter in your 9th house -- highest spiritual and philosophical union",
        "10": "Partner's Jupiter in your 10th house -- career blessings through partner",
        "11": "Partner's Jupiter in your 11th house -- gains and wish fulfillment together",
        "12": "Partner's Jupiter in your 12th house -- spiritual liberation through love",
    },
    "saturn": {
        "1": "Partner's Saturn in your 1st house -- serious relationship, maturity required",
        "2": "Partner's Saturn in your 2nd house -- financial discipline from partner",
        "3": "Partner's Saturn in your 3rd house -- serious communication, possible restriction",
        "4": "Partner's Saturn in your 4th house -- structured home life, emotional distance",
        "5": "Partner's Saturn in your 5th house -- restrained romance, delayed children",
        "6": "Partner's Saturn in your 6th house -- disciplined daily routines together",
        "7": "Partner's Saturn in your 7th house -- karmic relationship, long-lasting bond",
        "8": "Partner's Saturn in your 8th house -- deep karmic transformation",
        "9": "Partner's Saturn in your 9th house -- serious philosophical alignment",
        "10": "Partner's Saturn in your 10th house -- career-focused partnership",
        "11": "Partner's Saturn in your 11th house -- long-term friendship and goals",
        "12": "Partner's Saturn in your 12th house -- karmic debt, spiritual lessons",
    },
}

_FALLBACK_CROSS_ASPECTS: dict[str, dict[str, dict[str, str]]] = {
    "sun_moon": {
        "conjunction": {
            "quality": "very_harmonious",
            "interpretation": "Core identity meets emotional nature -- deep soul recognition",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Gentle support between identity and feelings",
        },
        "square": {
            "quality": "challenging",
            "interpretation": "Tension between will and feelings, growth through friction",
        },
        "trine": {
            "quality": "harmonious",
            "interpretation": "Natural understanding between ego and emotions",
        },
        "opposition": {
            "quality": "complex",
            "interpretation": "Magnetic attraction with identity clashes",
        },
    },
    "sun_venus": {
        "conjunction": {
            "quality": "very_harmonious",
            "interpretation": "Love and admiration, natural romantic attraction",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Easy affection and shared aesthetics",
        },
        "square": {"quality": "challenging", "interpretation": "Attraction with value differences"},
        "trine": {
            "quality": "harmonious",
            "interpretation": "Flowing love and mutual appreciation",
        },
        "opposition": {
            "quality": "complex",
            "interpretation": "Magnetic pull with occasional ego conflicts in love",
        },
    },
    "sun_mars": {
        "conjunction": {
            "quality": "dynamic",
            "interpretation": "Energetic and passionate, can be competitive",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Healthy motivation and drive together",
        },
        "square": {
            "quality": "challenging",
            "interpretation": "Power struggles and heated arguments",
        },
        "trine": {
            "quality": "harmonious",
            "interpretation": "Natural teamwork and shared ambition",
        },
        "opposition": {
            "quality": "challenging",
            "interpretation": "Strong attraction with ego battles",
        },
    },
    "moon_venus": {
        "conjunction": {
            "quality": "very_harmonious",
            "interpretation": "Deep emotional love, tenderness and care",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Comfortable affection and domestic harmony",
        },
        "square": {
            "quality": "challenging",
            "interpretation": "Emotional needs vs love expression mismatch",
        },
        "trine": {
            "quality": "very_harmonious",
            "interpretation": "Beautiful emotional and romantic flow",
        },
        "opposition": {
            "quality": "complex",
            "interpretation": "Emotional seesaw in love expression",
        },
    },
    "moon_mars": {
        "conjunction": {
            "quality": "passionate",
            "interpretation": "Intense emotional-physical chemistry",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Balanced emotion and action in the relationship",
        },
        "square": {
            "quality": "challenging",
            "interpretation": "Emotional volatility, arguments, but passion",
        },
        "trine": {
            "quality": "harmonious",
            "interpretation": "Protective and emotionally courageous together",
        },
        "opposition": {
            "quality": "challenging",
            "interpretation": "Push-pull between feelings and actions",
        },
    },
    "venus_mars": {
        "conjunction": {
            "quality": "very_passionate",
            "interpretation": "Powerful sexual and romantic chemistry",
        },
        "sextile": {"quality": "harmonious", "interpretation": "Balanced desire and affection"},
        "square": {
            "quality": "passionate",
            "interpretation": "Intense physical attraction with friction",
        },
        "trine": {
            "quality": "very_harmonious",
            "interpretation": "Natural romantic and physical harmony",
        },
        "opposition": {
            "quality": "magnetic",
            "interpretation": "Irresistible attraction, may struggle with balance",
        },
    },
    "sun_saturn": {
        "conjunction": {
            "quality": "karmic",
            "interpretation": "Serious bond, Saturn person stabilizes or restricts Sun",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Mature and supportive structure in relationship",
        },
        "square": {
            "quality": "difficult",
            "interpretation": "Criticism, restriction, but karmic growth",
        },
        "trine": {
            "quality": "harmonious",
            "interpretation": "Stable, mature, mutually respectful bond",
        },
        "opposition": {
            "quality": "karmic",
            "interpretation": "Authority struggles, but deep lessons",
        },
    },
    "moon_saturn": {
        "conjunction": {
            "quality": "karmic",
            "interpretation": "Emotional restriction but deep loyalty",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Emotional maturity and steady support",
        },
        "square": {
            "quality": "difficult",
            "interpretation": "Emotional coldness or fear of vulnerability",
        },
        "trine": {
            "quality": "harmonious",
            "interpretation": "Stable emotional foundation, lasting bond",
        },
        "opposition": {
            "quality": "karmic",
            "interpretation": "Emotional distance requiring conscious bridging",
        },
    },
    "venus_jupiter": {
        "conjunction": {
            "quality": "very_harmonious",
            "interpretation": "Abundant love, generosity, and joy together",
        },
        "sextile": {
            "quality": "harmonious",
            "interpretation": "Easy-going love with shared optimism",
        },
        "square": {
            "quality": "indulgent",
            "interpretation": "Over-indulgence in pleasure, but generally positive",
        },
        "trine": {
            "quality": "very_harmonious",
            "interpretation": "Expansive love and shared prosperity",
        },
        "opposition": {
            "quality": "complex",
            "interpretation": "Different values about abundance and love",
        },
    },
    "mars_saturn": {
        "conjunction": {
            "quality": "difficult",
            "interpretation": "Controlled energy, frustration vs discipline",
        },
        "sextile": {
            "quality": "productive",
            "interpretation": "Hard work together, practical achievements",
        },
        "square": {
            "quality": "very_challenging",
            "interpretation": "Anger, frustration, power struggles",
        },
        "trine": {
            "quality": "productive",
            "interpretation": "Disciplined action, endurance together",
        },
        "opposition": {
            "quality": "challenging",
            "interpretation": "Stop-and-go energy, patience required",
        },
    },
}

_FALLBACK_COMPOSITE_SIGNS: dict[str, dict[str, str]] = {
    "sun": {
        "aries": "Dynamic, action-oriented relationship with strong initiative",
        "taurus": "Stable, sensual relationship with focus on material security",
        "gemini": "Communicative, intellectually stimulating relationship",
        "cancer": "Nurturing, emotionally deep relationship centered on home",
        "leo": "Creative, expressive relationship with strong presence",
        "virgo": "Service-oriented, practical relationship focused on improvement",
        "libra": "Balanced, harmonious relationship focused on partnership",
        "scorpio": "Intense, transformative relationship with deep bonding",
        "sagittarius": "Adventurous, philosophical relationship with growth focus",
        "capricorn": "Ambitious, structured relationship with long-term goals",
        "aquarius": "Unconventional, progressive relationship with humanitarian ideals",
        "pisces": "Spiritual, compassionate relationship with creative flow",
    },
    "moon": {
        "aries": "Emotionally passionate, impulsive emotional reactions together",
        "taurus": "Emotionally stable and comfortable, shared love of luxury",
        "gemini": "Emotionally intellectual, talking through feelings",
        "cancer": "Deeply nurturing emotional bond, strong family focus",
        "leo": "Dramatic emotions, warmhearted and generous toward each other",
        "virgo": "Emotionally practical, caring through acts of service",
        "libra": "Emotionally balanced, need for harmony and fairness",
        "scorpio": "Intensely emotional, deep psychological bond",
        "sagittarius": "Emotionally optimistic, need for freedom and adventure",
        "capricorn": "Emotionally reserved but deeply committed",
        "aquarius": "Emotionally detached yet intellectually connected",
        "pisces": "Deeply empathic, spiritual emotional connection",
    },
}


def _angular_distance(lon1: float, lon2: float) -> float:
    """Calculate the shortest angular distance between two longitudes.

    Handles 360-degree wraparound correctly.

    Args:
        lon1: First longitude (0-360).
        lon2: Second longitude (0-360).

    Returns:
        Shortest angular distance (0-180).
    """
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _midpoint(lon1: float, lon2: float) -> float:
    """Calculate the midpoint of two longitudes on a 360-degree circle.

    Handles wraparound correctly (e.g., midpoint of 350 and 10 = 0).

    Args:
        lon1: First longitude (0-360).
        lon2: Second longitude (0-360).

    Returns:
        Midpoint longitude (0-360).
    """
    diff = (lon2 - lon1) % 360
    mid = (lon1 + diff / 2 + 180) % 360 if diff > 180 else (lon1 + diff / 2) % 360
    return mid


def _longitude_to_sign(longitude: float) -> str:
    """Convert a longitude to its zodiac sign name.

    Args:
        longitude: Ecliptic longitude (0-360).

    Returns:
        Zodiac sign name (lowercase).
    """
    sign_index = int(longitude / 30) % 12
    return SIGN_NAMES[sign_index]


def _determine_house(longitude: float, cusps: list[float]) -> int:
    """Determine which house a longitude falls in using cusps.

    Uses whole-sign-like logic: compares longitude against sequential cusp
    boundaries.

    Args:
        longitude: The ecliptic longitude to place.
        cusps: List of 12 house cusp longitudes.

    Returns:
        House number (1-12).
    """
    for i in range(12):
        cusp_start = cusps[i] % 360
        cusp_end = cusps[(i + 1) % 12] % 360

        if cusp_start < cusp_end:
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            # Wraparound case
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1

    # Fallback to sign-based house
    return int(longitude / 30) % 12 + 1


def _get_overlay_interpretation(planet: str, house: int, rules: dict[str, Any]) -> str:
    """Get interpretation for a planet in a house from rules or fallback.

    Args:
        planet: Planet name (lowercase).
        house: House number (1-12).
        rules: Loaded synastry rules dict.

    Returns:
        Interpretation string.
    """
    house_overlay_rules = rules.get("house_overlay", {})
    planet_rules = house_overlay_rules.get(planet, {})
    interp = planet_rules.get(str(house), "")
    if interp:
        return interp

    # Fallback
    fallback = _FALLBACK_HOUSE_OVERLAY.get(planet, {})
    return fallback.get(str(house), f"Partner's {planet.title()} in your house {house}")


def _get_cross_aspect_interpretation(
    planet1: str, planet2: str, aspect_name: str, rules: dict[str, Any]
) -> dict[str, str]:
    """Get interpretation for a cross-aspect from rules or fallback.

    Args:
        planet1: First planet (lowercase).
        planet2: Second planet (lowercase).
        aspect_name: Aspect name (conjunction, trine, etc.).
        rules: Loaded synastry rules dict.

    Returns:
        Dict with quality and interpretation.
    """
    cross_rules = rules.get("cross_aspects", {})

    # Try both orderings
    key1 = f"{planet1}_{planet2}"
    key2 = f"{planet2}_{planet1}"
    aspect_data = cross_rules.get(key1, {}).get(aspect_name, {})
    if not aspect_data:
        aspect_data = cross_rules.get(key2, {}).get(aspect_name, {})

    if aspect_data:
        return {
            "quality": aspect_data.get("quality", "neutral"),
            "interpretation": aspect_data.get("interpretation", ""),
        }

    # Fallback
    fb = _FALLBACK_CROSS_ASPECTS.get(key1, {}).get(aspect_name, {})
    if not fb:
        fb = _FALLBACK_CROSS_ASPECTS.get(key2, {}).get(aspect_name, {})

    if fb:
        return {"quality": fb["quality"], "interpretation": fb["interpretation"]}

    # Generic fallback
    return {
        "quality": "neutral",
        "interpretation": f"{planet1.title()}-{planet2.title()} {aspect_name} in synastry",
    }


def calculate_house_overlay(
    native_planets: dict[str, Any],  # noqa: ARG001
    native_cusps: list[float],
    partner_planets: dict[str, Any],
) -> list[dict[str, Any]]:
    """Place partner's planets in native's houses.

    For each of the partner's planets, determine which house it falls in
    within the native's chart framework.

    Args:
        native_planets: Native's birth chart planet data. Each key is a planet
            name (str) and value is a dict with at least 'longitude' (float).
        native_cusps: Native's 12 house cusp longitudes.
        partner_planets: Partner's birth chart planet data (same format).

    Returns:
        List of overlay results, each containing partner_planet, partner_longitude,
        native_house, interpretation, and significance.
    """
    if len(native_cusps) != 12:
        raise ValueError("native_cusps must contain exactly 12 cusp longitudes")

    rules = _load_synastry_rules()
    results: list[dict[str, Any]] = []

    for planet_name, planet_data in partner_planets.items():
        p_name = planet_name.lower() if isinstance(planet_name, str) else str(planet_name).lower()
        longitude = (
            planet_data.get("longitude", 0.0)
            if isinstance(planet_data, dict)
            else getattr(planet_data, "longitude", 0.0)
        )

        house = _determine_house(longitude, native_cusps)
        interpretation = _get_overlay_interpretation(p_name, house, rules)
        significance = PLANET_SIGNIFICANCE.get(p_name, "moderate")

        results.append(
            {
                "partner_planet": p_name,
                "partner_longitude": round(longitude, 2),
                "native_house": house,
                "interpretation": interpretation,
                "significance": significance,
            }
        )

    return results


def calculate_cross_aspects(
    native_planets: dict[str, Any],
    partner_planets: dict[str, Any],
    orb: float = 8.0,
) -> list[dict[str, Any]]:
    """Find all aspects between two charts.

    Checks every pair of (native_planet, partner_planet) for standard
    Ptolemaic aspects plus Parashari special aspects for Mars/Jupiter/Saturn.

    Luminaries (Sun, Moon) receive the full orb; other planets use orb - 2.

    Args:
        native_planets: Native's planet data (dict keyed by planet name with
            'longitude' float).
        partner_planets: Partner's planet data (same format).
        orb: Maximum orb for luminaries (default 8.0). Non-luminaries get orb - 2.

    Returns:
        List of aspect results sorted by orb (tightest first), each containing
        native_planet, partner_planet, aspect_type, exact_degree, orb, quality,
        and interpretation.
    """
    rules = _load_synastry_rules()
    results: list[dict[str, Any]] = []

    for n_name, n_data in native_planets.items():
        n_planet = n_name.lower() if isinstance(n_name, str) else str(n_name).lower()
        n_lon = (
            n_data.get("longitude", 0.0)
            if isinstance(n_data, dict)
            else getattr(n_data, "longitude", 0.0)
        )

        for p_name, p_data in partner_planets.items():
            p_planet = p_name.lower() if isinstance(p_name, str) else str(p_name).lower()
            p_lon = (
                p_data.get("longitude", 0.0)
                if isinstance(p_data, dict)
                else getattr(p_data, "longitude", 0.0)
            )

            # Determine effective orb
            involves_luminary = n_planet in LUMINARY_PLANETS or p_planet in LUMINARY_PLANETS
            effective_orb = orb if involves_luminary else max(orb - 2.0, 1.0)

            distance = _angular_distance(n_lon, p_lon)

            # Check standard Ptolemaic aspects
            for aspect_def in ASPECT_DEFINITIONS:
                aspect_orb = abs(distance - aspect_def["degree"])
                if aspect_orb <= effective_orb:
                    interp = _get_cross_aspect_interpretation(
                        n_planet, p_planet, aspect_def["name"], rules
                    )
                    results.append(
                        {
                            "native_planet": n_planet,
                            "partner_planet": p_planet,
                            "aspect_type": aspect_def["name"],
                            "exact_degree": aspect_def["degree"],
                            "orb": round(aspect_orb, 2),
                            "quality": interp["quality"],
                            "interpretation": interp["interpretation"],
                        }
                    )

            # Check Parashari special aspects
            for special_planet, special_aspects in PARASHARI_SPECIAL_ASPECTS.items():
                if n_planet == special_planet or p_planet == special_planet:
                    for sp_aspect in special_aspects:
                        # Directional: the special-aspecting planet casts the aspect
                        if n_planet == special_planet:
                            directed_diff = (p_lon - n_lon) % 360
                        else:
                            directed_diff = (n_lon - p_lon) % 360

                        sp_orb = abs(directed_diff - sp_aspect["degree"])
                        sp_orb = min(sp_orb, 360 - sp_orb) if sp_orb > 180 else sp_orb

                        if sp_orb <= effective_orb:
                            # Avoid duplicating aspects already found as Ptolemaic
                            already_found = any(
                                r["native_planet"] == n_planet
                                and r["partner_planet"] == p_planet
                                and abs(r["orb"] - sp_orb) < 0.01
                                for r in results
                            )
                            if not already_found:
                                interp = _get_cross_aspect_interpretation(
                                    n_planet, p_planet, sp_aspect["name"], rules
                                )
                                results.append(
                                    {
                                        "native_planet": n_planet,
                                        "partner_planet": p_planet,
                                        "aspect_type": sp_aspect["name"],
                                        "exact_degree": sp_aspect["degree"],
                                        "orb": round(sp_orb, 2),
                                        "quality": interp["quality"],
                                        "interpretation": interp["interpretation"],
                                    }
                                )

    # Sort by tightest orb first
    results.sort(key=lambda x: x["orb"])
    return results


def calculate_composite_chart(
    native_planets: dict[str, Any],
    partner_planets: dict[str, Any],
    native_ascendant: float,
    partner_ascendant: float,
) -> dict[str, Any]:
    """Calculate a midpoint composite chart for the relationship.

    The composite chart takes the midpoint of each matching planet pair
    and the midpoint of the two ascendants. This yields the relationship's
    own chart.

    Args:
        native_planets: Native's planet data (dict with 'longitude').
        partner_planets: Partner's planet data (same format).
        native_ascendant: Native's ascendant longitude (0-360).
        partner_ascendant: Partner's ascendant longitude (0-360).

    Returns:
        Dict with composite_planets, composite_ascendant, relationship_themes,
        strengths, and challenges.
    """
    rules = _load_synastry_rules()
    composite_sign_rules = rules.get("composite_planets_in_signs", {})

    composite_asc = _midpoint(native_ascendant, partner_ascendant)
    composite_asc_sign = _longitude_to_sign(composite_asc)

    # Calculate composite planets
    composite_planets: dict[str, dict[str, Any]] = {}
    all_native_keys = {
        (k.lower() if isinstance(k, str) else str(k).lower()): k for k in native_planets
    }
    all_partner_keys = {
        (k.lower() if isinstance(k, str) else str(k).lower()): k for k in partner_planets
    }

    common_planets = set(all_native_keys.keys()) & set(all_partner_keys.keys())

    for planet_key in sorted(common_planets):
        n_data = native_planets[all_native_keys[planet_key]]
        p_data = partner_planets[all_partner_keys[planet_key]]

        n_lon = (
            n_data.get("longitude", 0.0)
            if isinstance(n_data, dict)
            else getattr(n_data, "longitude", 0.0)
        )
        p_lon = (
            p_data.get("longitude", 0.0)
            if isinstance(p_data, dict)
            else getattr(p_data, "longitude", 0.0)
        )

        mid_lon = _midpoint(n_lon, p_lon)
        sign = _longitude_to_sign(mid_lon)
        # Calculate house from composite ascendant (equal house)
        house = int(((mid_lon - composite_asc) % 360) / 30) + 1

        composite_planets[planet_key] = {
            "longitude": round(mid_lon, 2),
            "sign": sign,
            "house": house,
        }

    # Generate themes, strengths, challenges from composite positions
    themes: list[str] = []
    strengths: list[str] = []
    challenges: list[str] = []

    for planet_key, comp_data in composite_planets.items():
        sign = comp_data["sign"]

        # Look up composite interpretation
        sign_interp = composite_sign_rules.get(planet_key, {}).get(sign, "")
        if not sign_interp:
            sign_interp = _FALLBACK_COMPOSITE_SIGNS.get(planet_key, {}).get(sign, "")

        if sign_interp:
            themes.append(f"{planet_key.title()} in {sign.title()}: {sign_interp}")

        # Sun placement = core relationship theme
        if planet_key == "sun":
            strengths.append(
                f"Composite Sun in {sign.title()} -- {sign_interp or 'core identity of the relationship'}"
            )

        # Venus/Jupiter in good signs = strengths
        if planet_key in ("venus", "jupiter") and sign_interp:
            strengths.append(f"Composite {planet_key.title()} in {sign.title()}")

        # Mars/Saturn placements can be challenges
        if planet_key in ("mars", "saturn"):
            challenges.append(
                f"Composite {planet_key.title()} in {sign.title()} -- requires conscious effort"
            )

    return {
        "composite_planets": composite_planets,
        "composite_ascendant": round(composite_asc, 2),
        "composite_ascendant_sign": composite_asc_sign,
        "relationship_themes": themes,
        "strengths": strengths,
        "challenges": challenges,
    }


def get_synastry_report(
    native_planets: dict[str, Any],
    native_cusps: list[float],
    partner_planets: dict[str, Any],
    partner_cusps: list[float],
    native_ascendant: float,
    partner_ascendant: float,
    native_moon_nakshatra: int,  # noqa: ARG001
    partner_moon_nakshatra: int,  # noqa: ARG001
) -> dict[str, Any]:
    """Generate a full synastry report combining all analysis modes.

    Combines house overlays (both directions), cross-chart aspects, composite
    chart, and optionally Ashta Kuta compatibility if the module is available.

    Args:
        native_planets: Native's planet data.
        native_cusps: Native's 12 house cusps.
        partner_planets: Partner's planet data.
        partner_cusps: Partner's 12 house cusps.
        native_ascendant: Native's ascendant longitude.
        partner_ascendant: Partner's ascendant longitude.
        native_moon_nakshatra: Native's Moon nakshatra index (0-26).
        partner_moon_nakshatra: Partner's Moon nakshatra index (0-26).

    Returns:
        Comprehensive synastry report with all sub-analyses and overall score.
    """
    # 1. House overlays (both directions)
    native_overlay = calculate_house_overlay(native_planets, native_cusps, partner_planets)
    partner_overlay = calculate_house_overlay(partner_planets, partner_cusps, native_planets)

    # 2. Cross aspects
    cross_aspects = calculate_cross_aspects(native_planets, partner_planets)

    # 3. Composite chart
    composite = calculate_composite_chart(
        native_planets, partner_planets, native_ascendant, partner_ascendant
    )

    # 4. Score cross aspects
    harmonious_count = sum(
        1
        for a in cross_aspects
        if a["quality"] in ("harmonious", "very_harmonious", "very_passionate")
    )
    challenging_count = sum(
        1 for a in cross_aspects if a["quality"] in ("challenging", "very_challenging", "difficult")
    )
    total_aspects = len(cross_aspects)

    harmony_ratio = harmonious_count / total_aspects if total_aspects > 0 else 0.5

    # Synastry score: base 50 + ratio contribution
    synastry_score = round(50 + harmony_ratio * 30 - (1 - harmony_ratio) * 10, 1)
    synastry_score = max(0, min(100, synastry_score))

    # Key aspects (tightest 5)
    key_aspects = cross_aspects[:5] if cross_aspects else []

    # 5. Summary
    if synastry_score >= 75:
        overall_verdict = "Excellent synastry -- strong natural compatibility"
    elif synastry_score >= 60:
        overall_verdict = "Good synastry -- positive connection with some growth areas"
    elif synastry_score >= 45:
        overall_verdict = "Mixed synastry -- both harmony and challenge require work"
    else:
        overall_verdict = "Challenging synastry -- significant differences to bridge"

    return {
        "house_overlay": {
            "partner_in_native": native_overlay,
            "native_in_partner": partner_overlay,
        },
        "cross_aspects": {
            "all_aspects": cross_aspects,
            "key_aspects": key_aspects,
            "harmonious_count": harmonious_count,
            "challenging_count": challenging_count,
            "total_count": total_aspects,
        },
        "composite_chart": composite,
        "synastry_score": synastry_score,
        "verdict": overall_verdict,
    }
