"""
Chandra Kala Nadi (CKN) — classical Nadi Jyotish prediction engine.

Based on Deva Keralam / Chandra Kala Nadi by Achyuta.
Reads planet combinations in natal signs to predict life events.
Jupiter's transit over each sign activates the planets therein.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any

# Sign names
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

PLANET_NAMES = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]


def _load_ckn_rules() -> dict[str, Any]:
    """Load Chandra Kala Nadi rules from knowledge base."""
    rules_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "knowledge"
        / "rules"
        / "chandra_kala_nadi_rules.json"
    )
    if rules_path.exists():
        with rules_path.open() as f:
            data = json.load(f)
            return data.get("chandra_kala_nadi_rules", {})
    return {}


def get_planet_sign_map(natal_planets: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """
    Group planets by their natal sign.

    Args:
        natal_planets: {planet_name: {longitude: float, rashi: str, ...}}

    Returns:
        {sign_name: [list of planet names in that sign]}
    """
    sign_map: dict[str, list[str]] = {sign: [] for sign in SIGNS}

    for planet, data in natal_planets.items():
        if planet.lower() not in PLANET_NAMES:
            continue
        # Get sign from rashi field or compute from longitude
        if "rashi" in data:
            rashi = data["rashi"].title()
            if rashi in sign_map:
                sign_map[rashi].append(planet.lower())
        elif "longitude" in data:
            sign_idx = int(float(data["longitude"]) / 30) % 12
            sign_map[SIGNS[sign_idx]].append(planet.lower())

    return sign_map


def get_conjunctions(sign_map: dict[str, list[str]]) -> list[dict[str, Any]]:
    """
    Find all planets conjunct in the same sign.

    Returns:
        List of conjunction dicts with sign, planets, and pair count.
    """
    conjunctions = []
    for sign, planets in sign_map.items():
        if len(planets) >= 2:
            pairs = list(combinations(sorted(planets), 2))
            triplets = list(combinations(sorted(planets), 3)) if len(planets) >= 3 else []
            conjunctions.append(
                {
                    "sign": sign,
                    "planets": planets,
                    "pairs": [list(p) for p in pairs],
                    "triplets": [list(t) for t in triplets],
                    "count": len(planets),
                }
            )
    return conjunctions


def _get_pair_key(p1: str, p2: str) -> str:
    """Generate canonical pair key (alphabetical order)."""
    ordered = sorted([p1, p2])
    return f"{ordered[0]}_{ordered[1]}"


def get_ckn_reading(
    natal_planets: dict[str, dict[str, Any]],
    current_jupiter_sign: str,
    moon_rashi: str | None = None,
) -> dict[str, Any]:
    """
    Generate a Chandra Kala Nadi reading for a birth chart.

    Args:
        natal_planets: Birth chart planet positions {name: {longitude, rashi, house}}
        current_jupiter_sign: Current transit Jupiter's sign (e.g. "gemini")
        moon_rashi: Natal Moon sign for reference counting

    Returns:
        CKN reading with conjunctions, active activations, upcoming triggers,
        and Jupiter timeline.
    """
    rules = _load_ckn_rules()
    pair_rules = rules.get("planet_pairs_same_sign", {})
    single_rules = rules.get("single_planet_in_sign", {})

    # Build sign map
    sign_map = get_planet_sign_map(natal_planets)
    conjunctions = get_conjunctions(sign_map)

    # Jupiter current index
    jupiter_sign_idx = SIGN_TO_INDEX.get(current_jupiter_sign.lower(), -1)
    current_jupiter_sign_title = (
        SIGNS[jupiter_sign_idx] if jupiter_sign_idx >= 0 else current_jupiter_sign.title()
    )

    # Build reading for each conjunction
    conjunction_readings = []
    for conj in conjunctions:
        sign = conj["sign"]
        planets = conj["planets"]
        pair_interpretations = []

        for pair in conj["pairs"]:
            key = _get_pair_key(pair[0], pair[1])
            rule = pair_rules.get(key, {})
            if rule:
                pair_interpretations.append(
                    {
                        "planets": pair,
                        "life_prediction": rule.get("life_prediction", ""),
                        "timing": rule.get("timing", ""),
                        "yoga": rule.get("yoga"),
                        "positive": rule.get("positive", []),
                        "challenging": rule.get("challenging", []),
                        "health": rule.get("health"),
                        "remedies": rule.get("remedies", []),
                    }
                )

        conjunction_readings.append(
            {
                "sign": sign,
                "planets": planets,
                "interpretations": pair_interpretations,
            }
        )

    # Single planets in their signs
    single_planet_readings = []
    for sign, planets in sign_map.items():
        if len(planets) == 1:
            planet = planets[0]
            key = f"{planet}_alone"
            rule = single_rules.get(key, {})
            if rule:
                single_planet_readings.append(
                    {
                        "planet": planet,
                        "sign": sign,
                        "life_areas": rule.get("life_areas", []),
                        "when_jupiter_transits": rule.get("when_jupiter_transits", ""),
                        "positive": rule.get("positive", []),
                        "challenging": rule.get("challenging", []),
                    }
                )

    # Active activations — Jupiter currently transiting which natal planets?
    active_activations = []
    currently_activated_sign = current_jupiter_sign_title
    activated_planets = sign_map.get(currently_activated_sign, [])

    if activated_planets:
        if len(activated_planets) == 1:
            planet = activated_planets[0]
            key = f"{planet}_alone"
            rule = single_rules.get(key, {})
            active_activations.append(
                {
                    "type": "single",
                    "sign": currently_activated_sign,
                    "planets": activated_planets,
                    "activation": rule.get(
                        "when_jupiter_transits",
                        f"Jupiter activating natal {planet} in {currently_activated_sign}",
                    ),
                    "positive": rule.get("positive", []),
                    "challenging": rule.get("challenging", []),
                }
            )
        elif len(activated_planets) >= 2:
            interp_list = []
            for pair in combinations(sorted(activated_planets), 2):
                key = _get_pair_key(pair[0], pair[1])
                rule = pair_rules.get(key, {})
                if rule:
                    interp_list.append(
                        {
                            "planets": list(pair),
                            "timing": rule.get("timing", ""),
                            "life_prediction": rule.get("life_prediction", ""),
                        }
                    )
            active_activations.append(
                {
                    "type": "conjunction",
                    "sign": currently_activated_sign,
                    "planets": activated_planets,
                    "activations": interp_list,
                }
            )

    # Jupiter timeline — next 12 signs = 12-year preview
    jupiter_timeline = []
    for i in range(1, 13):
        future_sign_idx = (jupiter_sign_idx + i) % 12
        future_sign = SIGNS[future_sign_idx]
        future_planets = sign_map.get(future_sign, [])
        years_from_now = i  # approx 1 year per sign

        if future_planets:
            timeline_entry: dict[str, Any] = {
                "sign": future_sign,
                "years_from_now": years_from_now,
                "planets_activated": future_planets,
                "theme": "",
            }
            if len(future_planets) == 1:
                planet = future_planets[0]
                rule = single_rules.get(f"{planet}_alone", {})
                timeline_entry["theme"] = rule.get("when_jupiter_transits", "")
            else:
                themes = []
                for pair in combinations(sorted(future_planets), 2):
                    key = _get_pair_key(pair[0], pair[1])
                    rule = pair_rules.get(key, {})
                    if rule:
                        themes.append(rule.get("timing", ""))
                timeline_entry["theme"] = "; ".join(t for t in themes if t)
            jupiter_timeline.append(timeline_entry)

    # Moon-based house counting (Chandra Kala)
    moon_analysis = None
    if moon_rashi:
        moon_idx = SIGN_TO_INDEX.get(moon_rashi.lower(), -1)
        if moon_idx >= 0:
            house_from_moon = {
                sign: ((SIGN_TO_INDEX[sign.lower()] - moon_idx) % 12) + 1 for sign in SIGNS
            }
            jupiter_house_from_moon = house_from_moon.get(current_jupiter_sign_title, 0)
            moon_analysis = {
                "natal_moon_sign": moon_rashi.title(),
                "jupiter_house_from_moon": jupiter_house_from_moon,
                "jupiter_activation_context": _jupiter_house_from_moon_meaning(
                    jupiter_house_from_moon
                ),
            }

    return {
        "success": True,
        "system": "Chandra Kala Nadi",
        "source": "Deva Keralam",
        "natal_sign_map": {k: v for k, v in sign_map.items() if v},
        "conjunctions": conjunction_readings,
        "single_planet_readings": single_planet_readings,
        "active_activations": active_activations,
        "current_jupiter_sign": current_jupiter_sign_title,
        "moon_analysis": moon_analysis,
        "jupiter_12_year_timeline": jupiter_timeline,
        "methodology": rules.get("ckn_reading_methodology", {}),
    }


def _jupiter_house_from_moon_meaning(house: int) -> str:
    """Classical meaning of Jupiter transiting each house from natal Moon."""
    meanings = {
        1: "Jupiter on natal Moon — peak emotional wisdom, spiritual clarity, faith renewal",
        2: "Jupiter in 2nd from Moon — financial gains through wisdom, family prosperity",
        3: "Jupiter in 3rd from Moon — courage through wisdom, sibling support, short journeys",
        4: "Jupiter in 4th from Moon — domestic happiness, property gains, mother's wellbeing",
        5: "Jupiter in 5th from Moon — children events, creative intelligence peaks, speculation gains",
        6: "Jupiter in 6th from Moon — victory over enemies through wisdom, service expansion",
        7: "Jupiter in 7th from Moon — partnership wisdom, marriage events, dharmic relationships",
        8: "Jupiter in 8th from Moon — hidden knowledge revealed, transformation through wisdom",
        9: "Jupiter in 9th from Moon — peak dharma year, guru connection, foreign spiritual journey",
        10: "Jupiter in 10th from Moon — career recognition, public wisdom, authority elevation",
        11: "Jupiter in 11th from Moon — peak gains year, network expansion, desires fulfilled",
        12: "Jupiter in 12th from Moon — spiritual expenses, foreign spiritual journey, moksha preparation",
    }
    return meanings.get(house, "")
