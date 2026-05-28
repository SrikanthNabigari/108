"""
Nadi Amsha (D-150) Interpreter — Nadi Jyotish divisional chart analysis.

The D-150 divides each sign into 150 parts of 0.2° (12 arc minutes) each.
Used in KP (Krishnamurti Paddhati) as the sublord foundation.
Requires accurate birth time (±30 seconds) for reliable results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SIGNS = [
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

SIGN_TO_INDEX = {s.lower(): i for i, s in enumerate(SIGNS)}

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

NADI_AMSHA_SIZE = 0.2  # degrees


def _load_nadi_rules() -> dict[str, Any]:
    rules_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "knowledge"
        / "rules"
        / "nadi_amsha_interpretation.json"
    )
    if rules_path.exists():
        with rules_path.open() as f:
            data = json.load(f)
            return data.get("nadi_amsha_interpretation", {})
    return {}


def calculate_nadi_amsha_position(longitude: float) -> dict[str, Any]:
    """
    Calculate D-150 Nadi Amsha position for a single longitude.

    Args:
        longitude: Sidereal longitude (0-360°)

    Returns:
        Dict with amsha_number, nadi_amsha_sign, nadi_type, sign_lord, degree
    """
    longitude = longitude % 360
    rashi_idx = int(longitude / 30)
    degree_in_sign = longitude % 30
    amsha_num = int(degree_in_sign / NADI_AMSHA_SIZE)  # 0-149
    amsha_num = min(amsha_num, 149)  # clamp edge case at exactly 30°

    result_rashi_idx = (rashi_idx * 150 + amsha_num) % 12
    result_sign = SIGNS[result_rashi_idx]

    # Nadi type
    if amsha_num < 50:
        nadi_type = "Adi"
    elif amsha_num < 100:
        nadi_type = "Madhya"
    else:
        nadi_type = "Antya"

    return {
        "natal_sign": SIGNS[rashi_idx],
        "degree_in_sign": round(degree_in_sign, 4),
        "amsha_number": amsha_num,
        "nadi_amsha_sign": result_sign,
        "nadi_amsha_sign_lord": SIGN_LORDS[result_sign],
        "nadi_type": nadi_type,
    }


def get_nadi_amsha_chart(
    natal_planets: dict[str, dict[str, Any]],
    lagna_longitude: float | None = None,
) -> dict[str, Any]:
    """
    Calculate full Nadi Amsha (D-150) chart.

    Args:
        natal_planets: {planet: {longitude: float, ...}}
        lagna_longitude: Ascendant longitude (optional)

    Returns:
        Complete D-150 chart with all planet positions and interpretation
    """
    rules = _load_nadi_rules()
    nadi_types_info = rules.get("nadi_types", {})

    planet_positions = {}
    for planet, data in natal_planets.items():
        if "longitude" not in data:
            continue
        lon = float(data["longitude"])
        pos = calculate_nadi_amsha_position(lon)
        planet_positions[planet.lower()] = pos

    # Lagna if provided
    lagna_position = None
    if lagna_longitude is not None:
        lagna_position = calculate_nadi_amsha_position(lagna_longitude)

    # Nadi distribution — count how many planets in each nadi type
    nadi_distribution = {"Adi": [], "Madhya": [], "Antya": []}
    for planet, pos in planet_positions.items():
        nadi_distribution[pos["nadi_type"]].append(planet)

    dominant_nadi = max(nadi_distribution, key=lambda k: len(nadi_distribution[k]))
    dominant_nadi_info = nadi_types_info.get(dominant_nadi.lower(), {})

    # Check triple alignment: if D-150 Lagna sign = D-1 natal Lagna sign
    alignment_notes = []
    if lagna_position:
        d150_lagna_sign = lagna_position["nadi_amsha_sign"]
        # Note for user to compare with D-1 and D-9 lagna
        alignment_notes.append(
            f"D-150 Lagna falls in {d150_lagna_sign} — compare with D-1 and D-9 Lagna for triple alignment"
        )

    # Moon sublord analysis
    moon_analysis = None
    if "moon" in planet_positions:
        moon_pos = planet_positions["moon"]
        moon_sublord = moon_pos["nadi_amsha_sign_lord"]
        moon_analysis = {
            "moon_nadi_amsha_sign": moon_pos["nadi_amsha_sign"],
            "moon_sublord": moon_sublord,
            "moon_nadi_type": moon_pos["nadi_type"],
            "interpretation": f"Natal Moon's sublord is {moon_sublord} — the finest emotional karma operates through {moon_sublord}'s significations",
        }

    return {
        "success": True,
        "division": 150,
        "system": "Nadi Amsha",
        "planet_positions": planet_positions,
        "lagna_position": lagna_position,
        "nadi_distribution": nadi_distribution,
        "dominant_nadi": dominant_nadi,
        "dominant_nadi_qualities": {
            "quality": dominant_nadi_info.get("quality", ""),
            "life_themes": dominant_nadi_info.get("life_themes", []),
            "personality": dominant_nadi_info.get("personality", ""),
        },
        "moon_sublord_analysis": moon_analysis,
        "alignment_notes": alignment_notes,
        "birth_time_warning": "D-150 requires birth time accurate to ±30 seconds. Each minute of error shifts positions by ~0.85 amshas.",
    }


def get_kp_sublord(longitude: float, house_num: int | None = None) -> dict[str, Any]:
    """
    Get KP sublord for any longitude (house cusp or planet).

    In KP, the sublord is the sign lord of the Nadi Amsha position.

    Args:
        longitude: Sidereal longitude (0-360°)
        house_num: Optional house number for context

    Returns:
        Dict with sublord, sub-sublord context, and KP interpretation
    """
    pos = calculate_nadi_amsha_position(longitude)
    sublord = pos["nadi_amsha_sign_lord"]

    result: dict[str, Any] = {
        "longitude": longitude,
        "nadi_amsha_sign": pos["nadi_amsha_sign"],
        "sublord": sublord,
        "nadi_type": pos["nadi_type"],
        "amsha_number": pos["amsha_number"],
    }
    if house_num is not None:
        result["house"] = house_num
        result[
            "kp_interpretation"
        ] = f"House {house_num} sublord is {sublord} — {sublord}'s natal house positions determine this house's true operation"

    return result
