"""
108 Patterns MCP Server

Provides yoga detection, dosha detection, and strength calculation tools
for the 108 Vedic Astrology application via Model Context Protocol.

Includes:
- Yoga detection (Raja, Dhana, Pancha Mahapurusha, etc.)
- Dosha detection (Mangal, Kaal Sarp, Pitra, etc.)
- Shadbala (six-fold strength) calculations
- Ashtakavarga (eight-fold classification) analysis
"""

import sys
from pathlib import Path
from typing import Any

# Add packages to path
SERVICES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERVICES_ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from packages.core.src import (  # noqa: E402
    BirthChart,
    BirthData,
    HouseCusps,
    Planet,
    PlanetPosition,
    Rashi,
)
from packages.cosmos.src.divisional import (  # noqa: E402
    calculate_vimshopaka_bala,
    get_all_vimshopaka,
)
from packages.self.src import (  # noqa: E402
    DoshaDetector,
    StrengthCalculator,
    YogaDetector,
    calculate_ashta_kuta,
    get_compatibility_verdict,
)
from packages.self.src.combustion import check_combustion as _check_combustion  # noqa: E402
from packages.self.src.jaimini import (  # noqa: E402
    calculate_all_arudha_padas,
    calculate_chara_dasha,
    calculate_chara_karakas,
    get_jaimini_aspects,
    interpret_upapada,
)
from packages.self.src.planetary_war import (  # noqa: E402
    detect_planetary_wars as _detect_planetary_wars,
)
from packages.self.src.planetary_war import get_war_effects as _get_war_effects  # noqa: E402
from packages.self.src.prashna import (  # noqa: E402
    analyze_prashna as _analyze_prashna,
)
from packages.self.src.remedies import (  # noqa: E402
    recommend_remedies as _recommend_remedies,
)
from packages.self.src.retrograde import (  # noqa: E402
    get_retrograde_effects as _get_retrograde_effects,
)
from packages.self.src.yoga_cancellation import (  # noqa: E402
    apply_cancellations_to_chart as _apply_cancellations_to_chart,
)
from packages.self.src.yoga_detector import (  # noqa: E402
    detect_neecha_bhanga as _detect_neecha_bhanga,
)

# Initialize MCP server
mcp = FastMCP("108-patterns")

# Initialize detectors
yoga_detector = YogaDetector()
dosha_detector = DoshaDetector()
strength_calc = StrengthCalculator()


@mcp.tool()
def detect_yogas(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Detect all yogas present in the birth chart.

    Analyzes planetary combinations to identify auspicious yogas including
    Pancha Mahapurusha (5 great-person yogas), Raja Yogas (royal yogas),
    Dhana Yogas (wealth yogas), and other beneficial combinations.

    Args:
        planets: Dictionary of planet positions with format:
                {planet_name: {longitude, sign, house, rashi, is_retrograde}}
                Example: {"sun": {"longitude": 52.5, "sign": "taurus", "house": 10, ...}}
        lagna_rashi: Ascendant sign name (e.g., "libra", "aries", "capricorn")
        moon_rashi: Moon sign (optional, for moon-based yoga calculations)
        houses: House cusps data (optional, for enhanced calculations)

    Returns:
        Dictionary containing:
        - lagna: The ascendant sign
        - total_yogas_found: Count of detected yogas
        - yogas: List of detected yogas with details
        - categories: Breakdown by yoga category
        - error: Error message if computation fails

    Example:
        planets = {
            "sun": {"longitude": 52.5, "sign": "taurus", "house": 10, "rashi": 1},
            "moon": {"longitude": 102.5, "sign": "gemini", "house": 12, "rashi": 2},
            ...
        }
        detect_yogas(planets, "libra", "gemini")
    """
    try:
        # Build a minimal BirthChart for detection
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)

        # Detect yogas using the detector
        detected = yoga_detector.detect_all_yogas(chart)

        # Format results
        yogas = []
        for yoga in detected:
            yogas.append(
                {
                    "id": yoga.id if hasattr(yoga, "id") else "",
                    "name": yoga.name if hasattr(yoga, "name") else "",
                    "category": yoga.category if hasattr(yoga, "category") else "other",
                    "is_present": yoga.is_present if hasattr(yoga, "is_present") else True,
                    "strength": yoga.strength if hasattr(yoga, "strength") else 1.0,
                    "involved_planets": yoga.involved_planets
                    if hasattr(yoga, "involved_planets")
                    else [],
                    "description": yoga.description if hasattr(yoga, "description") else "",
                    "effects": yoga.effects if hasattr(yoga, "effects") else [],
                    "cancellation": yoga.cancellation if hasattr(yoga, "cancellation") else None,
                }
            )

        return {
            "lagna": lagna_rashi.lower(),
            "total_yogas_found": len(yogas),
            "yogas": yogas,
            "categories": _group_by_category(yogas),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def detect_doshas(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    venus_rashi: str | None = None,  # noqa: ARG001
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Detect all doshas (afflictions) present in the birth chart.

    Identifies karmic challenges and afflictions including Mangal Dosha
    (Mars affliction), Kaal Sarp Dosha (Rahu-Ketu axis affliction),
    Pitra Dosha (ancestral karma), and other challenging combinations.

    Args:
        planets: Dictionary of planet positions
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (for Mangal Dosha from Moon)
        venus_rashi: Venus sign (for Mangal Dosha from Venus)
        houses: House cusps data (optional)

    Returns:
        Dictionary containing:
        - lagna: The ascendant sign
        - total_doshas_found: Count of detected doshas
        - doshas: List of detected doshas with details
        - has_mangal_dosha: Whether Mangal Dosha is present
        - has_kaal_sarp: Whether Kaal Sarp Dosha is present
        - error: Error message if computation fails

    Example:
        detect_doshas(planets, "libra", "gemini", "taurus")
    """
    try:
        # Build a minimal BirthChart for detection
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)

        # Detect doshas using the detector
        detected = dosha_detector.detect_all(chart)

        # Format results
        doshas = []
        for dosha in detected:
            doshas.append(
                {
                    "id": dosha.id if hasattr(dosha, "id") else "",
                    "name": dosha.name if hasattr(dosha, "name") else "",
                    "is_present": dosha.is_present if hasattr(dosha, "is_present") else True,
                    "severity": dosha.severity if hasattr(dosha, "severity") else "moderate",
                    "involved_planets": dosha.involved_planets
                    if hasattr(dosha, "involved_planets")
                    else [],
                    "description": dosha.description if hasattr(dosha, "description") else "",
                    "effects": dosha.effects if hasattr(dosha, "effects") else [],
                    "remedies": dosha.remedies if hasattr(dosha, "remedies") else [],
                    "cancellation": dosha.cancellation if hasattr(dosha, "cancellation") else None,
                }
            )

        return {
            "lagna": lagna_rashi.lower(),
            "total_doshas_found": len(doshas),
            "doshas": doshas,
            "has_mangal_dosha": any(d["id"] == "mangal_dosha" for d in doshas),
            "has_kaal_sarp": any(d["id"] == "kaal_sarp_dosha" for d in doshas),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def calculate_strength(
    planet: str, longitude: float, house: int, sign: str, is_retrograde: bool = False
) -> dict[str, Any]:
    """
    Calculate Shadbala (six-fold strength) for a planet.

    Computes comprehensive planetary strength using the traditional
    Shadbala system which measures strength through six dimensions:
    - Sthana Bala: Positional strength (own sign, exaltation, etc.)
    - Dig Bala: Directional strength (angles and quadrants)
    - Kala Bala: Temporal strength (day/night, lunar phase, etc.)
    - Chesta Bala: Motional strength (retrograde or direct motion)
    - Naisargika Bala: Natural strength (planet's inherent power)
    - Drik Bala: Aspectual strength (conjunctions and aspects)

    Args:
        planet: Planet name (sun, moon, mars, mercury, jupiter, venus, saturn)
        longitude: Planet's sidereal longitude (0-360 degrees)
        house: House number (1-12)
        sign: Sign name (aries, taurus, gemini, etc.)
        is_retrograde: Whether planet is retrograde (default: False)

    Returns:
        Dictionary containing:
        - planet: The planet name
        - dignity: Planet's dignity status (exalted, own-sign, debilitated, etc.)
        - shadbala: Components of strength with totals
        - is_strong: Boolean indicating if planet is strong (>300)
        - strength_rating: Qualitative rating (very_strong, strong, moderate, etc.)
        - error: Error message if computation fails

    Example:
        calculate_strength("jupiter", 136.24, 12, "virgo")
    """
    try:
        # Validate and convert planet
        planet_lower = planet.lower()
        if planet_lower not in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
            return {
                "error": f"Invalid planet: {planet}. Must be one of: sun, moon, mars, mercury, jupiter, venus, saturn",
                "success": False,
            }

        planet_enum = Planet(planet_lower)
        rashi_enum = Rashi(sign.lower())

        # Build a temporary chart for strength calculation
        chart = _build_chart_for_strength(planet_enum, longitude, house, rashi_enum, is_retrograde)

        # Calculate Shadbala using the chart
        shadbala_dict = strength_calc.calculate_shadbala(planet_enum, chart)

        # Convert to regular dict if it's a dataclass
        shadbala_data = {}
        if hasattr(shadbala_dict, "__dict__"):
            for key, value in shadbala_dict.__dict__.items():
                shadbala_data[key] = float(value) if isinstance(value, int | float) else value
        else:
            shadbala_data = shadbala_dict

        total_strength = shadbala_data.get(
            "total",
            sum(
                float(shadbala_data.get(k, 0))
                for k in [
                    "sthana_bala",
                    "dig_bala",
                    "kala_bala",
                    "chesta_bala",
                    "naisargika_bala",
                    "drik_bala",
                ]
            ),
        )

        # Get dignity status
        dignity = strength_calc.get_planet_dignity(planet_enum, rashi_enum)

        return {
            "planet": planet_lower,
            "longitude": round(longitude, 4),
            "house": house,
            "sign": sign.lower(),
            "is_retrograde": is_retrograde,
            "dignity": dignity,
            "shadbala": shadbala_data,
            "total_strength": round(total_strength, 2),
            "is_strong": total_strength > 300,
            "strength_rating": _get_strength_rating(total_strength),
            "success": True,
        }

    except ValueError as e:
        return {"error": str(e), "type": "ValueError", "success": False}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def ashtakavarga(planets: dict[str, dict[str, Any]], lagna_rashi: str) -> dict[str, Any]:
    """
    Calculate Ashtakavarga for all planets.

    Ashtakavarga measures the benefic influence (bindus) that planets
    contribute to each sign. It helps identify:
    - Strongest signs for each planet
    - Overall strength of each sign (Sarvashtakavarga)
    - Best times and areas for activity
    - Transiting planet effectiveness

    Each planet contributes 0-8 bindus per sign based on specific rules.
    Sarvashtakavarga (SAV) is the sum of all bindus for each sign.

    Args:
        planets: Dictionary of planet positions with signs
                {planet_name: {sign, longitude, house, ...}}
        lagna_rashi: Ascendant sign name

    Returns:
        Dictionary containing:
        - planets: Ashtakavarga for each planet (bindus by sign)
        - sarvashtakavarga: Total bindus for each sign (0-56 maximum)
        - sarvashtakavarga_with_signs: SAV mapped to sign names
        - error: Error message if computation fails

    Example:
        planets = {
            "sun": {"sign": "taurus", "longitude": 52.5},
            "moon": {"sign": "gemini", "longitude": 102.5},
            ...
        }
        ashtakavarga(planets, "libra")
    """
    try:
        # Sign to number mapping
        signs = [
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

        # Convert planet positions to rashi numbers
        planets_rashi = {}
        for planet_name, data in planets.items():
            planet_lower = planet_name.lower()
            if planet_lower in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
                sign_name = data.get("sign", "").lower()
                if sign_name in signs:
                    planets_rashi[planet_lower] = signs.index(sign_name)

        # Get lagna rashi number
        lagna_lower = lagna_rashi.lower()
        lagna_num = signs.index(lagna_lower) if lagna_lower in signs else 0

        # Calculate individual ashtakavarga
        result = {"planets": {}, "sarvashtakavarga": [0] * 12, "success": True}

        for planet_name in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
            if planet_name in planets_rashi:
                try:
                    planet_enum = Planet(planet_name)
                    av = strength_calc.calculate_ashtakavarga(planet_enum, planets_rashi, lagna_num)

                    # Ensure av is a list
                    if not isinstance(av, list):
                        av = [av] if isinstance(av, int | float) else [0] * 12

                    result["planets"][planet_name] = {
                        "bindus_by_sign": [float(v) for v in av],
                        "total_bindus": float(sum(av)),
                    }

                    # Add to SAV
                    for i in range(12):
                        result["sarvashtakavarga"][i] += av[i]

                except Exception:
                    # Skip planets with calculation errors
                    continue

        # Convert SAV to float and create sign mapping
        result["sarvashtakavarga"] = [float(v) for v in result["sarvashtakavarga"]]
        result["sarvashtakavarga_with_signs"] = {
            signs[i].capitalize(): result["sarvashtakavarga"][i] for i in range(12)
        }

        return result

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def kundali_matching(
    boy_nakshatra: str,
    boy_rashi: str,
    girl_nakshatra: str,
    girl_rashi: str,
) -> dict[str, Any]:
    """
    Calculate Ashta Kuta compatibility score for kundali matching.

    Computes the traditional 8-fold compatibility analysis (36 points total)
    between two birth charts based on Moon nakshatra and rashi.

    Args:
        boy_nakshatra: Boy's Moon nakshatra name (e.g., "ashwini", "bharani")
        boy_rashi: Boy's Moon sign (e.g., "aries", "taurus")
        girl_nakshatra: Girl's Moon nakshatra name
        girl_rashi: Girl's Moon sign

    Returns:
        Dictionary containing total score (out of 36), individual kuta scores,
        verdict, and compatibility assessment

    Example:
        kundali_matching("ashwini", "aries", "bharani", "aries")
    """
    try:
        result = calculate_ashta_kuta(
            boy_nakshatra=boy_nakshatra,
            boy_rashi=boy_rashi,
            girl_nakshatra=girl_nakshatra,
            girl_rashi=girl_rashi,
        )
        verdict = get_compatibility_verdict(result["total_score"])
        return {
            **result,
            "verdict": verdict,
            "success": True,
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def combustion_check(
    planet: str,
    planet_longitude: float,
    sun_longitude: float,
    is_retrograde: bool = False,
) -> dict[str, Any]:
    """
    Check if a planet is combust (too close to the Sun).

    Combustion weakens a planet's significations. Each planet has specific
    degree thresholds. Mercury and Venus have different thresholds when retrograde.

    Args:
        planet: Planet name (moon, mars, mercury, jupiter, venus, saturn)
        planet_longitude: Planet's sidereal longitude (0-360)
        sun_longitude: Sun's sidereal longitude (0-360)
        is_retrograde: Whether the planet is in retrograde motion

    Returns:
        Dictionary with combustion status, angular distance, strength loss,
        effects, and remedies

    Example:
        combustion_check("mercury", 105.0, 100.0, is_retrograde=True)
    """
    try:
        result = _check_combustion(planet, planet_longitude, sun_longitude, is_retrograde)
        return {**result, "success": True}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def retrograde_effects(
    planet: str,
    is_natal: bool = True,
    house: int | None = None,
) -> dict[str, Any]:
    """
    Get retrograde effects for a planet.

    Retrograde planets give internalized, delayed results representing
    karmic patterns. Available for Mars, Mercury, Jupiter, Venus, Saturn.

    Args:
        planet: Planet name (mars, mercury, jupiter, venus, saturn)
        is_natal: True for birth chart retrograde, False for transit retrograde
        house: House number (1-12) for transit house-specific effects

    Returns:
        Dictionary with general, positive, negative effects, house effects,
        karmic indication (natal only), and remedies

    Example:
        retrograde_effects("mercury", is_natal=False, house=7)
    """
    try:
        result = _get_retrograde_effects(planet, is_natal=is_natal, house=house)
        return {**result, "success": True}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def chara_karakas(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate Jaimini Chara Karakas (7 variable significators).

    Ranks 7 planets (Sun through Saturn) by degree in sign to determine
    Atmakaraka (soul), Amatyakaraka (career), etc.

    Args:
        planets: Planet positions {name: {longitude, sign, house, ...}}
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (optional)
        houses: House cusps data (optional)

    Returns:
        7 Chara Karakas ranked from Atmakaraka to Darakaraka

    Example:
        chara_karakas({"sun": {"longitude": 52.5, "sign": "taurus"}, ...}, "libra")
    """
    try:
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)
        karakas = calculate_chara_karakas(chart)

        return {
            "karakas": [
                {
                    "karaka": k.karaka.value,
                    "planet": k.planet.value,
                    "degree_in_sign": round(k.degree_in_sign, 2),
                    "rashi": k.rashi.value,
                }
                for k in karakas
            ],
            "atmakaraka": karakas[0].planet.value if karakas else None,
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def jaimini_aspects(rashi: str) -> dict[str, Any]:
    """
    Get Jaimini sign-based aspects for a rashi.

    Jaimini aspects are sign-based (not degree-based like Parashari):
    - Movable signs aspect Fixed signs (skip adjacent)
    - Fixed signs aspect Movable signs (skip adjacent)
    - Dual signs aspect other Dual signs

    Args:
        rashi: Sign name (e.g., "aries", "taurus")

    Returns:
        List of signs aspected by the given rashi

    Example:
        jaimini_aspects("aries")
    """
    try:
        rashi_enum = Rashi(rashi.lower())
        aspected = get_jaimini_aspects(rashi_enum)

        return {
            "from_rashi": rashi.lower(),
            "aspects": [r.value for r in aspected],
            "count": len(aspected),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def arudha_padas(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate all 12 Arudha Padas (A1 through A12).

    Arudha Pada is the image/perception of a house. Calculated by counting
    from house to its lord, then same distance from lord.

    Args:
        planets: Planet positions {name: {longitude, sign, house, ...}}
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (optional)
        houses: House cusps data (optional)

    Returns:
        All 12 Arudha Padas with rashi placements

    Example:
        arudha_padas({"sun": {"longitude": 52.5, "sign": "taurus"}, ...}, "libra")
    """
    try:
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)
        padas = calculate_all_arudha_padas(chart)

        return {
            "arudha_padas": [
                {
                    "house": p.house_number,
                    "label": f"A{p.house_number}",
                    "rashi": p.rashi.value,
                    "house_lord": p.house_lord.value,
                    "note": p.calculation_note,
                }
                for p in padas
            ],
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def chara_dasha(
    birth_datetime: str,
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
    years: int = 108,
) -> dict[str, Any]:
    """
    Calculate Jaimini Chara Dasha periods (sign-based, 108-year cycle).

    Direction depends on lagna parity: odd lagna = forward (Aries→Pisces),
    even lagna = reverse (Pisces→Aries).

    Args:
        birth_datetime: Birth datetime in ISO format
        planets: Planet positions
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (optional)
        houses: House cusps (optional)
        years: Years to calculate (default 108)

    Returns:
        Chara Dasha periods with signs, dates, and durations

    Example:
        chara_dasha("1992-12-03T03:00:00+05:30",
                    {"sun": {"longitude": 52.5, "sign": "taurus"}, ...}, "libra")
    """
    try:
        from datetime import datetime as dt_class

        birth_dt = dt_class.fromisoformat(birth_datetime.replace("Z", "+00:00"))
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)
        periods = calculate_chara_dasha(birth_dt, chart, years)

        return {
            "system": "chara",
            "birth_datetime": birth_datetime,
            "lagna": lagna_rashi.lower(),
            "periods": [
                {
                    "rashi": p.rashi.value,
                    "start_date": p.start_date.isoformat(),
                    "end_date": p.end_date.isoformat(),
                    "duration_years": p.duration_years,
                }
                for p in periods
            ],
            "total_periods": len(periods),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def prashna_analysis(
    question: str,
    datetime_iso: str,
    latitude: float,
    longitude: float,
    category: str,
) -> dict[str, Any]:
    """
    Perform Prashna (Horary) astrology analysis for a question.

    Creates a chart for the moment the question is asked and analyzes
    lagna strength, Moon condition, and significator placement.

    Args:
        question: The question being asked
        datetime_iso: Question datetime in ISO format
        latitude: Location latitude
        longitude: Location longitude
        category: Question category (health, marriage, career, travel,
                 lost_objects, legal, spiritual, children, wealth, education)

    Returns:
        Complete Prashna analysis with judgment, timing, and recommendations

    Example:
        prashna_analysis("Will I get the job?", "2026-02-04T10:00:00+05:30",
                        16.726, 81.288, "career")
    """
    try:
        from datetime import datetime as dt_cls

        from packages.core.src import PrashnaCategory

        dt = dt_cls.fromisoformat(datetime_iso.replace("Z", "+00:00"))
        cat = PrashnaCategory(category.lower())

        result = _analyze_prashna(question, dt, latitude, longitude, cat)

        return {
            "question": question,
            "datetime": datetime_iso,
            "category": category,
            "judgment": result.judgment.value,
            "strength_score": round(result.strength_score, 1),
            "favorable_factors": result.favorable_factors,
            "unfavorable_factors": result.unfavorable_factors,
            "timing": result.timing,
            "recommendation": result.recommendation,
            "chart": {
                "lagna_rashi": result.chart.lagna_rashi.value,
                "lagna_degree": round(result.chart.lagna_degree, 2),
                "significator": result.chart.significator.value,
            },
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def vimshopaka_strength(
    planet: str,
    longitude: float,
    scheme: str = "shad_varga",
) -> dict[str, Any]:
    """
    Calculate Vimshopaka Bala (strength across divisional charts).

    Evaluates a planet's dignity across multiple divisional charts using
    the proper friendship table and dignity scoring.

    Args:
        planet: Planet name (sun, moon, mars, mercury, jupiter, venus, saturn)
        longitude: Planet's sidereal longitude (0-360)
        scheme: Varga scheme (shad_varga, sapta_varga, dasha_varga, shodasha_varga)

    Returns:
        Vimshopaka score with category and per-varga breakdown

    Example:
        vimshopaka_strength("jupiter", 136.24, "shad_varga")
    """
    try:
        result = calculate_vimshopaka_bala(planet.lower(), longitude, scheme)
        return {**result, "planet": planet.lower(), "success": True}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def all_vimshopaka(
    planets: dict[str, float],
    scheme: str = "shad_varga",
) -> dict[str, Any]:
    """
    Calculate Vimshopaka Bala for all planets in a chart.

    Provides comparative strength analysis across the chosen varga scheme.

    Args:
        planets: Planet longitudes {planet_name: longitude}
        scheme: Varga scheme (shad_varga, sapta_varga, dasha_varga, shodasha_varga)

    Returns:
        Vimshopaka scores for all planets with ranking

    Example:
        all_vimshopaka({"sun": 52.5, "moon": 102.5, "mars": 230.0}, "shad_varga")
    """
    try:
        result = get_all_vimshopaka(
            {k.lower(): v for k, v in planets.items()},
            scheme,
        )

        # Sort by total_points descending for ranking
        ranked = sorted(
            result.items(),
            key=lambda x: x[1].get("total_points", 0),
            reverse=True,
        )

        return {
            "scheme": scheme,
            "planets": result,
            "ranking": [
                {"planet": name, "score": data.get("total_points", 0)} for name, data in ranked
            ],
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def bhava_bala(
    house_number: int,
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate Bhava Bala (house strength) for a specific house.

    Bhava Bala measures the strength of a house through four components:
    - Bhavadhipati Bala: Strength of the house lord
    - Bhava Dig Bala: Directional strength of the house
    - Bhava Drishti Bala: Strength from aspects received
    - Occupant Strength: Strength from planets in the house

    Args:
        house_number: House number (1-12)
        planets: Planet positions {name: {longitude, sign, house, ...}}
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (optional)
        houses: House cusps data (optional)

    Returns:
        Bhava Bala components and total strength for the house

    Example:
        bhava_bala(1, {"sun": {"longitude": 52.5, "sign": "taurus", "house": 8}}, "libra")
    """
    try:
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)
        result = strength_calc.calculate_bhava_bala(house_number, chart)
        return {**result, "success": True}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def all_bhava_balas(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate Bhava Bala for all 12 houses in the chart.

    Provides a comparative strength analysis of all houses, helping identify
    the strongest and weakest areas of the chart.

    Args:
        planets: Planet positions {name: {longitude, sign, house, ...}}
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (optional)
        houses: House cusps data (optional)

    Returns:
        Bhava Bala for all 12 houses with ranking

    Example:
        all_bhava_balas({"sun": {"longitude": 52.5, "sign": "taurus", "house": 8}}, "libra")
    """
    try:
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)
        result = strength_calc.get_all_bhava_balas(chart)

        # Convert int keys to string for JSON and add ranking
        bhava_dict = {str(k): v for k, v in result.items()}
        ranked = sorted(result.items(), key=lambda x: x[1].get("total", 0), reverse=True)

        return {
            "houses": bhava_dict,
            "ranking": [
                {
                    "house": h,
                    "total": data.get("total", 0),
                    "rating": data.get("strength_rating", "unknown"),
                }
                for h, data in ranked
            ],
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def upapada_analysis(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Perform Upapada Lagna (UL) marriage analysis using Jaimini principles.

    The Upapada Lagna is the Arudha Pada of the 12th house and is the primary
    Jaimini indicator for marriage. Analysis includes partner type, marriage
    quality, sustenance, timing, and separation indicators.

    Args:
        planets: Planet positions {name: {longitude, sign, house, ...}}
        lagna_rashi: Ascendant sign
        moon_rashi: Moon sign (optional)
        houses: House cusps data (optional)

    Returns:
        Complete Upapada marriage analysis including partner type, quality,
        sustenance factors, timing, and separation risk

    Example:
        upapada_analysis({"sun": {"longitude": 52.5, "sign": "taurus", "house": 8}}, "libra")
    """
    try:
        chart = _build_chart_for_yoga(planets, lagna_rashi, moon_rashi, houses)
        result = interpret_upapada(chart)
        return {**result, "success": True}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def check_yoga_cancellations(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    yogas: list[dict[str, Any]],
    sun_longitude: float,
) -> dict[str, Any]:
    """
    Check whether detected yogas are cancelled by classical rules (Yoga Bhanga).

    Evaluates cancellation conditions for each yoga:
    - Combustion: planet too close to Sun
    - Debilitation: planet in debilitation without Neecha Bhanga
    - Malefic affliction: planet conjunct 2+ malefics
    - Type-specific: Pancha Mahapurusha, Raja, Dhana, Gajakesari rules

    Args:
        planets: Planet positions {name: {longitude, sign, house, rashi, is_retrograde}}
        lagna_rashi: Ascendant sign name (e.g., "libra")
        yogas: List of detected yoga dicts, each with at least:
               - category (str): Yoga type (e.g., "pancha_mahapurusha", "raja_yoga")
               - involved_planets (list[str]): Planets forming the yoga
               Optional: name, strength, id
        sun_longitude: Sun's sidereal longitude (0-360)

    Returns:
        Dictionary with:
        - total_yogas: Number of yogas checked
        - cancelled_count: Number fully cancelled
        - partial_count: Number partially weakened
        - yogas: List of enriched yoga dicts with cancellation status
        - error: Error message if computation fails

    Example:
        check_yoga_cancellations(
            {"sun": {"longitude": 52.5, "sign": "taurus", "house": 8}, ...},
            "libra",
            [{"category": "raja_yoga", "involved_planets": ["jupiter", "venus"], "strength": 0.8}],
            52.5
        )
    """
    try:
        # Build planet dict with enum keys for cancellation engine
        planet_dict = {}
        for pname, pdata in planets.items():
            try:
                p_enum = Planet(pname.lower())
                planet_dict[p_enum] = pdata
                planet_dict[pname.lower()] = pdata
            except (ValueError, KeyError):
                continue

        results = _apply_cancellations_to_chart(
            yogas, planet_dict, lagna_rashi.lower(), sun_longitude
        )

        cancelled_count = sum(1 for r in results if r.get("cancellation", {}).get("cancelled"))
        partial_count = sum(1 for r in results if r.get("cancellation", {}).get("partial"))

        return {
            "total_yogas": len(results),
            "cancelled_count": cancelled_count,
            "partial_count": partial_count,
            "active_count": len(results) - cancelled_count,
            "yogas": results,
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def detect_neecha_bhanga_yoga(
    planet: str,
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    d9_positions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Check if a debilitated planet has Neecha Bhanga Raja Yoga (cancellation of debilitation).

    Five classical conditions (any one suffices):
    1. Lord of debilitation sign in kendra from Lagna or Moon
    2. Lord of exaltation sign in kendra from Lagna or Moon
    3. Planet exalted in the debilitation sign aspects the debilitated planet
    4. Debilitated planet is retrograde
    5. Debilitated planet in kendra with dignity in Navamsha (D9)

    Args:
        planet: Planet name to check (e.g., "mars", "jupiter")
        planets: All planet positions {name: {longitude, sign, house, rashi, is_retrograde}}
        lagna_rashi: Ascendant sign name
        d9_positions: Optional Navamsha positions for condition 5

    Returns:
        Dictionary with has_neecha_bhanga, conditions_met, strength, and description

    Example:
        detect_neecha_bhanga_yoga("mars", {"mars": {"longitude": 100, "sign": "cancer", "house": 10}}, "libra")
    """
    try:
        planet_lower = planet.lower()
        planet_data = planets.get(planet_lower, {})

        result = _detect_neecha_bhanga(
            planet_lower, planet_data, planets, lagna_rashi.lower(), d9_positions
        )

        return {
            "planet": planet_lower,
            "lagna": lagna_rashi.lower(),
            **result,
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def detect_planetary_wars_tool(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str | None = None,
) -> dict[str, Any]:
    """
    Detect Graha Yuddha (planetary wars) when two planets are within 1 degree.

    Only Mars, Mercury, Jupiter, Venus, and Saturn can engage in planetary war.
    The planet with higher latitude wins. Venus always wins when retrograde.
    The loser's significations and house lordships are weakened.

    Args:
        planets: Planet positions {name: {longitude, latitude, is_retrograde, sign, house}}
        lagna_rashi: Optional ascendant sign for house-based effect analysis

    Returns:
        Dictionary with wars detected, winner/loser for each, effects, and remedial notes

    Example:
        detect_planetary_wars_tool({
            "mars": {"longitude": 120.5, "latitude": 1.2, "is_retrograde": false},
            "mercury": {"longitude": 121.0, "latitude": 0.5, "is_retrograde": false}
        }, "libra")
    """
    try:
        # Build planet dict with enum keys
        planet_dict = {}
        for pname, pdata in planets.items():
            try:
                p_enum = Planet(pname.lower())
                planet_dict[p_enum] = pdata
            except (ValueError, KeyError):
                continue

        wars = _detect_planetary_wars(planet_dict)

        # Enrich with house effects if lagna given
        for war in wars:
            if lagna_rashi:
                effects = _get_war_effects(war["winner"], war["loser"], lagna_rashi.lower())
                war["house_effects"] = effects.get("house_effects", [])
                war["affected_houses"] = effects.get("affected_houses", [])
                war["remedial_notes"] = effects.get("remedial_notes", "")

        return {
            "wars_found": len(wars),
            "wars": wars,
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def bhava_chalit_chart(
    planets: dict[str, dict[str, Any]],
    cusps: list[float],
    ascendant: float,
) -> dict[str, Any]:
    """
    Calculate Bhava Chalit chart showing house shifts from Rashi to cusp-based system.

    In Rashi chart, houses = signs. In Bhava Chalit, house boundaries are midpoints
    between consecutive cusps. Planets near cusp boundaries may shift to adjacent houses,
    affecting their bhava phala (house-based results).

    Args:
        planets: Planet positions {name: {longitude, ...}}
        cusps: List of 12 house cusp longitudes (0-360 degrees)
        ascendant: Ascendant longitude in degrees (0-360)

    Returns:
        Dictionary with per-planet rashi house, chalit house, shift status,
        and list of shifted planets

    Example:
        bhava_chalit_chart(
            {"sun": {"longitude": 52.5}, "moon": {"longitude": 102.5}},
            [180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0],
            180.0
        )
    """
    try:
        from packages.cosmos.src.bhava_chalit import calculate_bhava_chalit as _calc_bhava_chalit
        from packages.cosmos.src.bhava_chalit import get_shifted_planets as _get_shifted

        result = _calc_bhava_chalit(planets, cusps, ascendant)
        shifted = _get_shifted(result)

        return {
            "planets": result,
            "shifted_planets": shifted,
            "shift_count": len(shifted),
            "success": True,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def recommend_chart_remedies(
    current_dasha: dict[str, str],
    active_doshas: list[dict[str, Any]],
    weak_planets: list[dict[str, Any]],
    current_transits: dict[str, Any] | None = None,
    lagna_rashi: str = "",
) -> dict[str, Any]:
    """
    Get prioritized remedy recommendations based on chart conditions.

    Combines active dasha lords, dosha-afflicted planets, weak planets,
    and transit-afflicted planets to recommend mantras, gemstones, charity,
    worship, and general remedies. Prioritizes into urgent/recommended/optional.

    Args:
        current_dasha: Active dasha lords {mahadasha_lord, antardasha_lord, pratyantardasha_lord}
        active_doshas: List of doshas [{name, severity}]
        weak_planets: List of weak planets [{planet, shadbala}]
        current_transits: Optional transit data for transit-based remedies
        lagna_rashi: Ascendant sign name

    Returns:
        Dictionary with urgent/recommended/optional remedy lists,
        summary counts, and planets needing remedies

    Example:
        recommend_chart_remedies(
            {"mahadasha_lord": "mercury", "antardasha_lord": "saturn"},
            [{"name": "sade_sati", "severity": "high"}],
            [{"planet": "moon", "shadbala": 180}]
        )
    """
    try:
        result = _recommend_remedies(
            current_dasha=current_dasha,
            active_doshas=active_doshas,
            weak_planets=weak_planets,
            current_transits=current_transits,
            lagna_rashi=lagna_rashi.lower() if lagna_rashi else "",
        )

        return {**result, "success": True}

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def navamsha_spouse_analysis(
    d9_7th_lord_sign: str,
    d9_venus_sign: str | None = None,
    d9_7th_house_planets: list[str] | None = None,
) -> dict[str, Any]:
    """
    Analyze spouse characteristics from Navamsha (D9) chart using classical rules.

    The D9 chart is the primary indicator for marriage in Vedic astrology.
    Analysis is based on:
    - D9 7th lord sign placement (spouse nature)
    - D9 Venus sign (relationship style)
    - Planets in D9 7th house (spouse personality influences)

    Args:
        d9_7th_lord_sign: Sign where the D9 7th lord is placed (e.g., "aries", "taurus")
        d9_venus_sign: Sign where Venus is placed in D9 (optional)
        d9_7th_house_planets: List of planets in D9 7th house (optional)

    Returns:
        Dictionary with spouse nature, interpretation, relationship style,
        and 7th house planetary influences

    Example:
        navamsha_spouse_analysis("taurus", "pisces", ["jupiter", "venus"])
    """
    try:
        import json
        from pathlib import Path

        rules_path = (
            Path(__file__).parent.parent.parent
            / "knowledge"
            / "rules"
            / "navamsha_spouse_rules.json"
        )
        with rules_path.open() as f:
            rules = json.load(f)

        spouse_rules = rules.get("navamsha_spouse_rules", rules)

        result: dict[str, Any] = {"success": True}

        # 1. D9 7th lord sign interpretation
        sign_lower = d9_7th_lord_sign.lower()
        d9_7th_lord_rules = spouse_rules.get("d9_7th_lord_in_sign", [])
        for rule in d9_7th_lord_rules:
            if rule.get("sign", "").lower() == sign_lower:
                result["d9_7th_lord"] = {
                    "sign": sign_lower,
                    "interpretation": rule.get("interpretation", ""),
                    "spouse_nature": rule.get("spouse_nature", ""),
                }
                break
        else:
            result["d9_7th_lord"] = {"sign": sign_lower, "interpretation": "No data available"}

        # 2. D9 Venus sign interpretation
        if d9_venus_sign:
            venus_lower = d9_venus_sign.lower()
            venus_rules = spouse_rules.get("venus_in_d9_sign", [])
            for rule in venus_rules:
                if rule.get("sign", "").lower() == venus_lower:
                    result["d9_venus"] = {
                        "sign": venus_lower,
                        "interpretation": rule.get("interpretation", ""),
                        "relationship_style": rule.get("relationship_style", ""),
                    }
                    break
            else:
                result["d9_venus"] = {"sign": venus_lower, "interpretation": "No data available"}

        # 3. Planets in D9 7th house
        if d9_7th_house_planets:
            planet_influences = []
            planet_rules = spouse_rules.get("planets_in_d9_7th", [])
            for planet_name in d9_7th_house_planets:
                p_lower = planet_name.lower()
                for rule in planet_rules:
                    if rule.get("planet", "").lower() == p_lower:
                        planet_influences.append(
                            {
                                "planet": p_lower,
                                "interpretation": rule.get("interpretation", ""),
                                "effect": rule.get("effect", ""),
                            }
                        )
                        break
                else:
                    planet_influences.append(
                        {"planet": p_lower, "interpretation": "No specific data"}
                    )
            result["d9_7th_house_planets"] = planet_influences

        return result

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


# Helper functions


def _build_chart_for_strength(
    planet_enum: Planet, longitude: float, house: int, rashi_enum: Rashi, is_retrograde: bool
) -> BirthChart:
    """Build a minimal BirthChart object for strength calculations."""
    from datetime import datetime

    # Create planet position
    planet_positions = {
        planet_enum: PlanetPosition(
            planet=planet_enum,
            longitude=longitude,
            latitude=0.0,
            speed=0.0,
            rashi=rashi_enum,
            rashi_degree=longitude % 30,
            nakshatra="ashwini",
            nakshatra_pada=1,
            nakshatra_lord=Planet.KETU,
            is_retrograde=is_retrograde,
            house=house,
        )
    }

    # Create house cusps
    house_cusps = HouseCusps(ascendant=0.0, mc=270.0, cusps=[i * 30 for i in range(12)])

    # Create minimal BirthChart
    chart = BirthChart(
        user_id="temporary",
        birth_data=BirthData(
            datetime_utc=datetime.utcnow(), latitude=0.0, longitude=0.0, timezone="UTC"
        ),
        planets=planet_positions,
        houses=house_cusps,
        lagna_rashi=Rashi.ARIES,
        moon_rashi=Rashi.CANCER,
        moon_nakshatra="pushya",
        ayanamsa=23.45,
        calculated_at=datetime.utcnow(),
    )

    return chart


def _build_chart_for_yoga(
    planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str | None = None,
    houses: dict[str, Any] | None = None,
) -> BirthChart:
    """Build a minimal BirthChart object for yoga/dosha detection."""
    from datetime import datetime

    # Sign to enum mapping
    sign_map = {
        "aries": Rashi.ARIES,
        "taurus": Rashi.TAURUS,
        "gemini": Rashi.GEMINI,
        "cancer": Rashi.CANCER,
        "leo": Rashi.LEO,
        "virgo": Rashi.VIRGO,
        "libra": Rashi.LIBRA,
        "scorpio": Rashi.SCORPIO,
        "sagittarius": Rashi.SAGITTARIUS,
        "capricorn": Rashi.CAPRICORN,
        "aquarius": Rashi.AQUARIUS,
        "pisces": Rashi.PISCES,
    }

    # Build planet positions
    planet_positions = {}
    for planet_name, data in planets.items():
        planet_lower = planet_name.lower()
        if planet_lower in [
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        ]:
            try:
                planet_enum = Planet(planet_lower)
                sign_str = data.get("sign", "aries").lower()
                rashi_enum = sign_map.get(sign_str, Rashi.ARIES)

                planet_positions[planet_enum] = PlanetPosition(
                    planet=planet_enum,
                    longitude=data.get("longitude", 0.0),
                    latitude=data.get("latitude", 0.0),
                    speed=data.get("speed", 0.0),
                    rashi=rashi_enum,
                    rashi_degree=data.get("rashi_degree", 0.0),
                    nakshatra=data.get("nakshatra", "ashwini"),
                    nakshatra_pada=data.get("nakshatra_pada", 1),
                    nakshatra_lord=Planet(data.get("nakshatra_lord", "ketu").lower()),
                    is_retrograde=data.get("is_retrograde", False),
                    house=data.get("house", 1),
                )
            except (KeyError, ValueError):
                continue

    # Ensure Rahu and Ketu are present (required for dosha detection)
    if Planet.RAHU not in planet_positions:
        planet_positions[Planet.RAHU] = PlanetPosition(
            planet=Planet.RAHU,
            longitude=180.0,
            latitude=0.0,
            speed=0.0,
            rashi=Rashi.LIBRA,
            rashi_degree=0.0,
            nakshatra="vishakha",
            nakshatra_pada=1,
            nakshatra_lord=Planet.JUPITER,
            is_retrograde=False,
            house=7,
        )

    if Planet.KETU not in planet_positions:
        planet_positions[Planet.KETU] = PlanetPosition(
            planet=Planet.KETU,
            longitude=0.0,
            latitude=0.0,
            speed=0.0,
            rashi=Rashi.ARIES,
            rashi_degree=0.0,
            nakshatra="ashwini",
            nakshatra_pada=1,
            nakshatra_lord=Planet.KETU,
            is_retrograde=False,
            house=1,
        )

    # Build house cusps
    lagna_enum = sign_map.get(lagna_rashi.lower(), Rashi.ARIES)
    if houses and "cusps" in houses:
        house_cusps = HouseCusps(
            ascendant=houses.get("ascendant", 0.0),
            mc=houses.get("mc", 270.0),
            cusps=houses.get("cusps", [i * 30 for i in range(12)]),
        )
    else:
        # Create default cusps
        house_cusps = HouseCusps(ascendant=0.0, mc=270.0, cusps=[i * 30 for i in range(12)])

    # Create minimal BirthChart
    moon_enum = sign_map.get((moon_rashi or "cancer").lower(), Rashi.CANCER)

    chart = BirthChart(
        user_id="temporary",
        birth_data=BirthData(
            datetime_utc=datetime.utcnow(), latitude=0.0, longitude=0.0, timezone="UTC"
        ),
        planets=planet_positions,
        houses=house_cusps,
        lagna_rashi=lagna_enum,
        moon_rashi=moon_enum,
        moon_nakshatra="pushya",
        ayanamsa=23.45,
        calculated_at=datetime.utcnow(),
    )

    return chart


def _group_by_category(yogas: list[dict]) -> dict[str, int]:
    """Group yogas by category and count."""
    categories = {}
    for yoga in yogas:
        cat = yoga.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
    return categories


def _get_strength_rating(total: float) -> str:
    """Convert Shadbala total to qualitative rating."""
    if total >= 400:
        return "very_strong"
    elif total >= 300:
        return "strong"
    elif total >= 200:
        return "moderate"
    elif total >= 100:
        return "weak"
    else:
        return "very_weak"


# Main entry point for MCP server
if __name__ == "__main__":
    mcp.run()
