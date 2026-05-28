"""
Sudarshana Chakra — Triple-wheel simultaneous chart analysis.

Parasara's rule: verify every prediction from three simultaneous ascendants:
1. Lagna (Ascendant) — the body/outer self
2. Chandra (Moon) — the mind/emotional self
3. Surya (Sun) — the soul/core self

A theme supported by all 3 wheels = certain. 2/3 = likely. 1/3 = weak.
"""
from __future__ import annotations

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

HOUSE_THEMES = {
    1: "self, health, identity, beginnings",
    2: "wealth, speech, family, food",
    3: "siblings, courage, communication, short travel",
    4: "home, mother, property, happiness",
    5: "children, intelligence, creativity, speculation",
    6: "enemies, disease, debt, service",
    7: "partnership, marriage, business",
    8: "transformation, occult, longevity, inheritance",
    9: "dharma, fortune, father, higher learning",
    10: "career, authority, public life, government",
    11: "gains, aspirations, elder siblings, networks",
    12: "losses, foreign, spirituality, liberation",
}

LIFE_AREAS = {
    "career": [10, 6, 2],
    "marriage": [7, 2, 11],
    "wealth": [2, 11, 9],
    "health": [1, 6, 8],
    "children": [5, 9, 11],
    "property": [4, 2, 11],
    "foreign_travel": [12, 9, 3],
    "education": [5, 4, 9],
    "spiritual": [9, 12, 5],
    "mother": [4, 2, 1],
    "father": [9, 4, 10],
}


def _house_from(planet_sign: str, ascendant_sign: str) -> int:
    p_idx = SIGN_TO_INDEX.get(planet_sign.lower(), 0)
    a_idx = SIGN_TO_INDEX.get(ascendant_sign.lower(), 0)
    return ((p_idx - a_idx) % 12) + 1


def _sign_at_house(ascendant_sign: str, house: int) -> str:
    a_idx = SIGN_TO_INDEX.get(ascendant_sign.lower(), 0)
    return SIGNS[(a_idx + house - 1) % 12]


def analyze_house_from_three_wheels(
    house: int,
    lagna_rashi: str,
    moon_rashi: str,
    sun_rashi: str,
    natal_planets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Analyze a single house from all 3 Sudarshana wheels."""

    def _wheel_analysis(wheel_name: str, wheel_sign: str) -> dict[str, Any]:
        house_sign = _sign_at_house(wheel_sign, house)
        planets_in_house = [
            p for p, d in natal_planets.items() if d.get("rashi", "").lower() == house_sign.lower()
        ]
        return {
            "wheel": wheel_name,
            "ascendant": wheel_sign.title(),
            "house_sign": house_sign,
            "planets_in_house": planets_in_house,
            "occupied": len(planets_in_house) > 0,
        }

    wheels = [
        _wheel_analysis("Lagna", lagna_rashi),
        _wheel_analysis("Chandra (Moon)", moon_rashi),
        _wheel_analysis("Surya (Sun)", sun_rashi),
    ]

    occupied_count = sum(1 for w in wheels if w["occupied"])
    all_signs = [w["house_sign"] for w in wheels]
    unique_signs = list(set(all_signs))

    if occupied_count == 3:
        strength = "very_strong"
        strength_note = "All 3 wheels confirm — certain manifestation"
    elif occupied_count == 2:
        strength = "strong"
        strength_note = "2 of 3 wheels confirm — likely manifestation"
    elif occupied_count == 1:
        strength = "moderate"
        strength_note = "1 of 3 wheels activated — possible manifestation"
    else:
        strength = "weak"
        strength_note = "No wheel has planets here — theme is dormant"

    return {
        "house": house,
        "theme": HOUSE_THEMES.get(house, ""),
        "wheels": wheels,
        "confirmation_count": occupied_count,
        "strength": strength,
        "strength_note": strength_note,
        "unique_signs": unique_signs,
    }


def get_sudarshana_chakra(
    natal_planets: dict[str, dict[str, Any]],
    lagna_rashi: str,
    moon_rashi: str,
    sun_rashi: str,
) -> dict[str, Any]:
    """
    Full Sudarshana Chakra analysis — all 12 houses from 3 wheels.

    Args:
        natal_planets: {planet: {longitude, rashi, house}}
        lagna_rashi: Ascendant sign
        moon_rashi: Natal Moon sign
        sun_rashi: Natal Sun sign

    Returns:
        Complete 3-wheel analysis with house strengths and life area scores
    """
    house_analyses = {}
    for h in range(1, 13):
        house_analyses[h] = analyze_house_from_three_wheels(
            h, lagna_rashi, moon_rashi, sun_rashi, natal_planets
        )

    # Life area scores — check primary houses for each area
    life_area_scores = {}
    for area, houses in LIFE_AREAS.items():
        confirmations = []
        for h in houses:
            confirmations.append(house_analyses[h]["confirmation_count"])
        avg = sum(confirmations) / len(confirmations) if confirmations else 0
        primary_strength = house_analyses[houses[0]]["strength"]
        life_area_scores[area] = {
            "primary_house": houses[0],
            "supporting_houses": houses[1:],
            "avg_confirmation": round(avg, 2),
            "primary_house_strength": primary_strength,
            "verdict": _area_verdict(avg),
        }

    # Find strongest and weakest houses
    sorted_houses = sorted(
        house_analyses.values(),
        key=lambda x: x["confirmation_count"],
        reverse=True,
    )
    strongest = [h["house"] for h in sorted_houses if h["confirmation_count"] == 3]
    weakest = [h["house"] for h in sorted_houses if h["confirmation_count"] == 0]

    return {
        "success": True,
        "system": "Sudarshana Chakra",
        "three_ascendants": {
            "lagna": lagna_rashi.title(),
            "moon": moon_rashi.title(),
            "sun": sun_rashi.title(),
        },
        "house_analyses": house_analyses,
        "life_area_scores": life_area_scores,
        "strongest_houses": strongest,
        "weakest_houses": weakest,
        "methodology": "Parasara: verify all predictions from Lagna, Chandra, and Surya simultaneously",
    }


def _area_verdict(avg_confirmation: float) -> str:
    if avg_confirmation >= 2.5:
        return "very_strong"
    elif avg_confirmation >= 1.5:
        return "strong"
    elif avg_confirmation >= 0.8:
        return "moderate"
    else:
        return "weak"
