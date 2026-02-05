"""Ashtakavarga transit scoring and interpretation.

Wraps StrengthCalculator's base Ashtakavarga calculations and adds
transit-specific interpretations and scoring modifiers.
"""

from typing import Any

from packages.core.src.constants import Planet, Rashi
from packages.core.src.models import BirthChart

from .strength import StrengthCalculator


def calculate_bhinnashtakavarga(planet: Planet, chart: BirthChart) -> list[int]:
    """Calculate BAV for a planet across 12 signs (0-8 bindus each)."""
    calculator = StrengthCalculator()
    return calculator.calculate_ashtakavarga(planet, chart)


def calculate_sarvashtakavarga(chart: BirthChart) -> list[int]:
    """Calculate SAV - sum of all planet BAVs per sign (0-56 each)."""
    calculator = StrengthCalculator()
    return calculator.calculate_sarvashtakavarga(chart)


def get_transit_ashtakavarga_score(
    planet: Planet,
    transit_sign: int,
    chart: BirthChart,
) -> int:
    """Get BAV score for a planet transiting a particular sign.

    Args:
        planet: The transiting planet
        transit_sign: Sign index (0=Aries to 11=Pisces)
        chart: Natal birth chart

    Returns:
        Score 0-8 representing benefic points in the transit sign
    """
    if not (0 <= transit_sign <= 11):
        raise ValueError(f"transit_sign must be 0-11, got {transit_sign}")
    bav = calculate_bhinnashtakavarga(planet, chart)
    return bav[transit_sign]


def get_sarvashtakavarga_score(transit_sign: int, chart: BirthChart) -> int:
    """Get SAV score for a sign (0-56)."""
    if not (0 <= transit_sign <= 11):
        raise ValueError(f"transit_sign must be 0-11, got {transit_sign}")
    sav = calculate_sarvashtakavarga(chart)
    return sav[transit_sign]


def interpret_ashtakavarga_score(score: int, max_score: int) -> str:
    """Interpret score as strength label.

    Returns: "very_strong", "strong", "moderate", "weak", or "very_weak"
    """
    if max_score <= 0:
        return "unknown"
    pct = (score / max_score) * 100
    if pct >= 75:
        return "very_strong"
    if pct >= 60:
        return "strong"
    if pct >= 40:
        return "moderate"
    if pct >= 25:
        return "weak"
    return "very_weak"


def get_transit_strength_modifier(score: int, max_score: int = 8) -> float:
    """Calculate multiplier for transit effects based on Ashtakavarga score.

    Returns float in 0.5-1.5 range (1.0 = neutral).
    """
    if max_score <= 0:
        return 1.0
    return 0.5 + (score / max_score)


def get_transit_ashtakavarga_analysis(
    planet: Planet,
    transit_sign: int,
    chart: BirthChart,
) -> dict[str, Any]:
    """Complete Ashtakavarga analysis for a transiting planet.

    Returns BAV score, SAV score, interpretations, and strength modifier.
    """
    bav_score = get_transit_ashtakavarga_score(planet, transit_sign, chart)
    sav_score = get_sarvashtakavarga_score(transit_sign, chart)

    bav_interp = interpret_ashtakavarga_score(bav_score, 8)
    sav_interp = interpret_ashtakavarga_score(sav_score, 56)
    modifier = get_transit_strength_modifier(bav_score, 8)

    rashi_names = [r.value for r in Rashi]
    sign_name = rashi_names[transit_sign] if 0 <= transit_sign < 12 else "Unknown"

    return {
        "planet": planet.value,
        "transit_sign": transit_sign,
        "transit_sign_name": sign_name,
        "bav_score": bav_score,
        "bav_max": 8,
        "bav_interpretation": bav_interp,
        "sav_score": sav_score,
        "sav_max": 56,
        "sav_interpretation": sav_interp,
        "strength_modifier": round(modifier, 2),
        "summary": (
            f"{planet.value.title()} transiting {sign_name}: "
            f"{bav_score}/8 BAV ({bav_interp}), "
            f"{sav_score}/56 SAV ({sav_interp})"
        ),
    }
