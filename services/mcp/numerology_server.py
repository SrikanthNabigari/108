"""
108 Numerology MCP Server

Provides numerology calculation tools for the 108 Vedic Astrology application
via Model Context Protocol.

Includes:
- Full numerology profile (psychic, destiny, name numbers)
- Psychic (driver) number calculation
- Destiny (life path) number calculation
- Name analysis (Chaldean and Pythagorean systems)
- Personal cycles (year, month, day)
- Lo Shu magic square grid analysis
- Number compatibility
- Numerology-Jyotish cross-referencing
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any

# Add packages to path
SERVICES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERVICES_ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from packages.self.src.numerology import (  # noqa: E402
    NUMBER_PLANET_MAP,
    analyze_name,
    calculate_destiny_number,
    calculate_full_profile,
    calculate_lo_shu_grid,
    calculate_psychic_number,
    cross_reference_jyotish,
    get_number_compatibility,
    get_personal_cycles,
)

# Initialize MCP server
mcp = FastMCP("108-numerology")


@mcp.tool()
def numerology_profile(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    name: str | None = None,
) -> dict[str, Any]:
    """
    Calculate complete numerology profile from birth date and optional name.

    Computes psychic number (driver), destiny number (life path), name number
    (if provided), personal year/month/day cycles, Lo Shu grid analysis,
    missing/repeated numbers, and psychic-destiny harmony assessment.

    Args:
        birth_year: Year of birth (e.g., 1992)
        birth_month: Month of birth (1-12)
        birth_day: Day of birth (1-31)
        name: Full name for name number calculation (optional)

    Returns:
        Dictionary containing complete NumerologyProfile with psychic_number,
        destiny_number, name_number, compound numbers, ruling planets,
        personal cycles, lo_shu_grid analysis, missing_numbers,
        repeated_numbers, and psychic_destiny_harmony.

    Example:
        numerology_profile(1992, 12, 3, "Srikanth")
    """
    try:
        birth_date = date(birth_year, birth_month, birth_day)
        profile = calculate_full_profile(birth_date, name)
        return {"success": True, **profile.model_dump()}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def psychic_number(
    birth_day: int,
) -> dict[str, Any]:
    """
    Calculate psychic (driver) number from the day of birth.

    The psychic number reveals personality, how you see yourself, and your
    natural tendencies. It is derived by reducing the birth day to a single
    digit (1-9). For example, birth day 28 -> 2+8 = 10 -> 1+0 = 1.

    Each number maps to a Vedic planet:
    1=Sun, 2=Moon, 3=Jupiter, 4=Rahu, 5=Mercury, 6=Venus, 7=Ketu, 8=Saturn, 9=Mars

    Args:
        birth_day: Day of birth (1-31)

    Returns:
        Dictionary with psychic_number (1-9), compound_number (original day
        if >= 10, else null), and ruling_planet name.

    Example:
        psychic_number(28)  -> {"psychic_number": 1, "compound_number": 28, "ruling_planet": "sun"}
    """
    try:
        psychic, compound = calculate_psychic_number(birth_day)
        return {
            "success": True,
            "psychic_number": psychic,
            "compound_number": compound,
            "ruling_planet": NUMBER_PLANET_MAP.get(psychic, "unknown"),
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def destiny_number(
    birth_year: int,
    birth_month: int,
    birth_day: int,
) -> dict[str, Any]:
    """
    Calculate destiny (life path) number from full date of birth.

    The destiny number shows your life's purpose, the path you must walk,
    and what the universe has in store. It is computed by summing all digits
    of the full date (DD+MM+YYYY) and reducing to a single digit.
    Master numbers (11, 22, 33) are noted before final reduction.

    Args:
        birth_year: Year of birth (e.g., 1992)
        birth_month: Month of birth (1-12)
        birth_day: Day of birth (1-31)

    Returns:
        Dictionary with destiny_number (1-9), compound_number (sum before
        reduction), master_numbers_found (list of 11/22/33 encountered),
        and ruling_planet.

    Example:
        destiny_number(1992, 12, 3)  -> {"destiny_number": 9, ...}
    """
    try:
        birth_date = date(birth_year, birth_month, birth_day)
        destiny, compound, masters = calculate_destiny_number(birth_date)
        return {
            "success": True,
            "destiny_number": destiny,
            "compound_number": compound,
            "master_numbers_found": masters,
            "ruling_planet": NUMBER_PLANET_MAP.get(destiny, "unknown"),
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def name_analysis(
    name: str,
) -> dict[str, Any]:
    """
    Analyze a name's numerological value in both Chaldean and Pythagorean systems.

    Chaldean (Vedic, primary): Maps letters to numbers based on sound vibration.
    Pythagorean (Western): Maps letters by alphabetical order.

    Returns values from both systems along with a letter-by-letter breakdown
    and the ruling planet based on the Chaldean reduced value.

    Args:
        name: Full name to analyze (e.g., "Srikanth Kumar")

    Returns:
        Dictionary with full_name, chaldean_value, chaldean_reduced,
        pythagorean_value, pythagorean_reduced, ruling_planet, and
        letter_breakdown (list of letter-value pairs).

    Example:
        name_analysis("Srikanth")
    """
    try:
        result = analyze_name(name)
        return {"success": True, **result.model_dump()}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def personal_cycles(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    target_year: int | None = None,
    target_month: int | None = None,
    target_day: int | None = None,
) -> dict[str, Any]:
    """
    Get personal year, month, and day cycles for a given date.

    Personal cycles reveal the numerological theme for each time period.
    Each cycle number (1-9) maps to a Vedic planet and carries specific
    meanings about the opportunities and challenges of that period.

    Also includes the current pinnacle number (major life phase) and
    challenge number (obstacle to overcome) based on age.

    Args:
        birth_year: Year of birth
        birth_month: Month of birth (1-12)
        birth_day: Day of birth (1-31)
        target_year: Year to analyze (defaults to current year)
        target_month: Month to analyze (defaults to current month)
        target_day: Day to analyze (defaults to today)

    Returns:
        Dictionary with personal_year, personal_month, personal_day,
        their ruling planets, year_meaning interpretation,
        pinnacle_number, and challenge_number.

    Example:
        personal_cycles(1992, 12, 3, 2026, 3, 6)
    """
    try:
        birth_date = date(birth_year, birth_month, birth_day)
        today = date.today()
        target_date = date(
            target_year if target_year is not None else today.year,
            target_month if target_month is not None else today.month,
            target_day if target_day is not None else today.day,
        )
        cycles = get_personal_cycles(birth_date, target_date)
        return {"success": True, **cycles.model_dump()}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def lo_shu_grid(
    birth_year: int,
    birth_month: int,
    birth_day: int,
) -> dict[str, Any]:
    """
    Calculate Lo Shu magic square grid analysis from birth date.

    The Lo Shu grid maps digits 1-9 into a 3x3 magic square. Each digit
    from the birth date is placed in its grid position. Numbers present
    indicate strengths; missing numbers indicate areas to develop.

    Arrows form when all numbers in a row, column, or diagonal are present
    (arrow of strength) or all absent (arrow of weakness). The dominant
    plane (mental/emotional/practical) is determined by digit concentration.

    Args:
        birth_year: Year of birth (e.g., 1992)
        birth_month: Month of birth (1-12)
        birth_day: Day of birth (1-31)

    Returns:
        Dictionary with grid (3x3 with count/present flags),
        present_numbers, missing_numbers, repeated_numbers,
        arrows_present, arrows_missing, and dominant_plane.

    Example:
        lo_shu_grid(1992, 12, 3)
    """
    try:
        birth_date = date(birth_year, birth_month, birth_day)
        grid = calculate_lo_shu_grid(birth_date)
        return {"success": True, **grid.model_dump()}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def number_compatibility(
    number_1: int,
    number_2: int,
) -> dict[str, Any]:
    """
    Check compatibility between two numerology numbers (1-9).

    Based on the traditional Vedic numerology compatibility matrix, which
    aligns with planetary friendships (since each number maps to a Vedic
    planet). Returns a compatibility score, nature, and description.

    Args:
        number_1: First number (1-9)
        number_2: Second number (1-9)

    Returns:
        Dictionary with number_1, number_2, score (0-100), nature
        (excellent/good/moderate/neutral/challenging/difficult),
        description, planet_1, and planet_2.

    Example:
        number_compatibility(1, 9)  -> {"score": 90, "nature": "excellent", ...}
    """
    try:
        compat = get_number_compatibility(number_1, number_2)
        return {"success": True, **compat.model_dump()}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


@mcp.tool()
def numerology_jyotish_bridge(
    birth_year: int,
    birth_month: int,
    birth_day: int,
    name: str | None = None,
    natal_planets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Cross-reference numerology numbers with Jyotish birth chart data.

    Each numerology number maps to a Vedic planet. This function checks
    whether the ruling planets of the psychic and destiny numbers are
    strong or weak in the actual birth chart, providing a bridge between
    numerology and Jyotish analysis.

    When natal_planets are provided, evaluates planet dignity (exalted,
    own sign, debilitated, etc.) to determine alignment quality and
    generates specific recommendations for remedial measures.

    Args:
        birth_year: Year of birth
        birth_month: Month of birth (1-12)
        birth_day: Day of birth (1-31)
        name: Full name for name number (optional)
        natal_planets: Planet positions from birth chart (optional).
            Format: {"sun": {"house": 10, "sign": "aries", "dignity": "exalted"}, ...}

    Returns:
        Dictionary with numerology_profile (full profile) and
        jyotish_cross_reference (alignment analysis with planet strengths
        and recommendations).

    Example:
        numerology_jyotish_bridge(
            1992, 12, 3, "Srikanth",
            {"sun": {"house": 2, "sign": "scorpio", "dignity": "neutral"}}
        )
    """
    try:
        birth_date = date(birth_year, birth_month, birth_day)
        profile = calculate_full_profile(birth_date, name)

        cross_ref = cross_reference_jyotish(
            psychic=profile.psychic_number,
            destiny=profile.destiny_number,
            birth_chart_planets=natal_planets,
        )

        return {
            "success": True,
            "numerology_profile": profile.model_dump(),
            "jyotish_cross_reference": cross_ref,
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__, "success": False}


# Main entry point for MCP server
if __name__ == "__main__":
    mcp.run()
