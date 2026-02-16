"""BPHS Chart-Specific Dasha Interpreter for 108 Vedic Astrology.

Replaces generic dasha text with birth-chart-personalized predictions
using the BPHS method: lordship + placement + dignity + aspects +
conjunctions + yogas.

Key BPHS principle: "The dasha lord gives results of the houses it
RULES and the house it OCCUPIES, modified by dignity, aspects, and
conjunctions."
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from packages.cosmos.src.aspects import get_houses_aspected_by
from packages.cosmos.src.houses import (
    HOUSE_SIGNIFICATIONS,
    RASHI_NAMES,
    SIGN_RULERS,
    get_house_from_reference,
)
from packages.self.src.transit_lordship import classify_planet_role

logger = logging.getLogger(__name__)

# ── Dignity constants ──

_EXALTATION: dict[str, int] = {
    "sun": 0,
    "moon": 1,
    "mars": 9,
    "mercury": 5,
    "jupiter": 3,
    "venus": 11,
    "saturn": 6,
    "rahu": 1,
    "ketu": 7,
}

_DEBILITATION: dict[str, int] = {
    "sun": 6,
    "moon": 7,
    "mars": 3,
    "mercury": 11,
    "jupiter": 9,
    "venus": 5,
    "saturn": 0,
    "rahu": 7,
    "ketu": 1,
}

_OWN_SIGNS: dict[str, list[int]] = {
    "sun": [4],
    "moon": [3],
    "mars": [0, 7],
    "mercury": [2, 5],
    "jupiter": [8, 11],
    "venus": [1, 6],
    "saturn": [9, 10],
    "rahu": [10],
    "ketu": [7],
}

# ── House label map (ordinal + primary themes) ──

_HOUSE_LABELS: dict[int, str] = {
    1: "1st (Self, Body, Personality)",
    2: "2nd (Wealth, Family, Speech)",
    3: "3rd (Siblings, Courage, Communication)",
    4: "4th (Home, Education, Mother)",
    5: "5th (Children, Intelligence, Creativity)",
    6: "6th (Enemies, Disease, Service)",
    7: "7th (Marriage, Partnership, Business)",
    8: "8th (Longevity, Transformation, Occult)",
    9: "9th (Dharma, Fortune, Higher Learning)",
    10: "10th (Career, Status, Karma)",
    11: "11th (Gains, Friends, Aspirations)",
    12: "12th (Moksha, Foreign Lands, Spirituality)",
}

# ── Positional relationship categories (BPHS) ──

_DISTANCE_RELATIONSHIP: dict[int, tuple[str, str]] = {
    1: ("conjunction", "blend"),
    2: ("dwirdwadash", "strained"),
    3: ("upachaya", "growing"),
    4: ("kendra", "active"),
    5: ("trine", "harmonious"),
    6: ("shadashtak", "challenging"),
    7: ("opposition", "tense"),
    8: ("shadashtak", "challenging"),
    9: ("trine", "harmonious"),
    10: ("kendra", "active"),
    11: ("upachaya", "growing"),
    12: ("dwirdwadash", "strained"),
}

# Lagna name map
_LAGNA_NAMES: dict[int, str] = {
    0: "Aries",
    1: "Taurus",
    2: "Gemini",
    3: "Cancer",
    4: "Leo",
    5: "Virgo",
    6: "Libra",
    7: "Scorpio",
    8: "Sagittarius",
    9: "Capricorn",
    10: "Aquarius",
    11: "Pisces",
}

# ── Knowledge loader ──

_lord_interp_cache: dict[str, Any] | None = None


def _load_lord_interpretations() -> dict[str, Any]:
    global _lord_interp_cache
    if _lord_interp_cache is not None:
        return _lord_interp_cache
    path = (
        Path(__file__).parent.parent.parent.parent
        / "knowledge"
        / "interpretations"
        / "house_lord_in_house.json"
    )
    try:
        with path.open() as f:
            data = json.load(f)
        _lord_interp_cache = data.get("house_lord_in_house", data)
    except (FileNotFoundError, json.JSONDecodeError):
        _lord_interp_cache = {}
    return _lord_interp_cache


# ── Private helpers ──


def _house_label(house_num: int) -> str:
    return _HOUSE_LABELS.get(house_num, f"{house_num}th")


def _dignity_label(lord: str, rashi_idx: int) -> tuple[str, str]:
    """Return (dignity_key, human_label) for a planet in a given rashi."""
    lord = lord.lower()
    rashi_name = RASHI_NAMES[rashi_idx].title() if 0 <= rashi_idx < 12 else "Unknown"

    if _EXALTATION.get(lord) == rashi_idx:
        return "exalted", f"Exalted in {rashi_name} -- very strong"
    if rashi_idx in _OWN_SIGNS.get(lord, []):
        return "own_sign", f"In own sign {rashi_name} -- strong"
    if _DEBILITATION.get(lord) == rashi_idx:
        return "debilitated", f"Debilitated in {rashi_name} -- weak"

    # Check friendship with sign ruler
    sign_ruler = SIGN_RULERS.get(rashi_idx, "")
    if sign_ruler == lord:
        return "own_sign", f"In own sign {rashi_name} -- strong"

    return "neutral", f"In {rashi_name} -- neutral dignity"


def _nature_explanation(role_data: dict[str, Any], lagna_index: int) -> str:
    """Build a human explanation of functional nature."""
    nature = role_data["functional_nature"]
    houses = role_data["houses_ruled"]
    lagna_name = _LAGNA_NAMES.get(lagna_index, "Unknown")

    if not houses:
        return f"Shadow planet -- no classical house lordship for {lagna_name} lagna"

    house_strs = []
    for h in houses:
        sigs = HOUSE_SIGNIFICATIONS.get(h, [])
        first_sig = sigs[0] if sigs else ""
        house_strs.append(f"{h}th ({first_sig})" if first_sig else str(h))

    rules_text = f"Rules {', '.join(house_strs)}"
    nature_label = nature.replace("_", " ").title()

    return f"{rules_text} -- {nature_label} for {lagna_name} lagna"


def _get_natal_house(lord: str, natal_planets: dict[str, Any], lagna_index: int) -> int:
    """Get the house number where a planet is placed natally."""
    p_data = natal_planets.get(lord, {})
    if not p_data:
        return 0
    lon = p_data.get("longitude", 0.0) if isinstance(p_data, dict) else float(p_data)
    rashi_idx = int(lon % 360 / 30)
    return get_house_from_reference(rashi_idx, lagna_index)


def _get_natal_rashi(lord: str, natal_planets: dict[str, Any]) -> int:
    """Get the rashi index of a planet from natal data."""
    p_data = natal_planets.get(lord, {})
    if not p_data:
        return -1
    lon = p_data.get("longitude", 0.0) if isinstance(p_data, dict) else float(p_data)
    return int(lon % 360 / 30)


def _is_retrograde(lord: str, natal_planets: dict[str, Any]) -> bool:
    """Check if planet is retrograde from natal data."""
    p_data = natal_planets.get(lord, {})
    if isinstance(p_data, dict):
        return bool(p_data.get("is_retrograde", False))
    return False


def _check_combustion(lord: str, natal_planets: dict[str, Any]) -> bool:
    """Check if planet is combust (within standard orbs of Sun)."""
    if lord in ("sun", "rahu", "ketu"):
        return False
    sun_data = natal_planets.get("sun", {})
    lord_data = natal_planets.get(lord, {})
    if not sun_data or not lord_data:
        return False

    sun_lon = sun_data.get("longitude", 0.0) if isinstance(sun_data, dict) else float(sun_data)
    lord_lon = lord_data.get("longitude", 0.0) if isinstance(lord_data, dict) else float(lord_data)

    dist = abs(sun_lon - lord_lon) % 360
    dist = min(dist, 360 - dist)

    # Standard combustion orbs
    orbs: dict[str, float] = {
        "moon": 12.0,
        "mars": 17.0,
        "mercury": 14.0,
        "jupiter": 11.0,
        "venus": 10.0,
        "saturn": 15.0,
    }
    return dist <= orbs.get(lord, 15.0)


def _find_aspects_received(
    lord: str, natal_house: int, natal_planets: dict[str, Any], lagna_index: int
) -> list[dict[str, Any]]:
    """Find which planets aspect the lord's natal house."""
    if natal_house < 1 or natal_house > 12:
        return []

    # Build planet -> house map
    planet_houses: dict[str, int] = {}
    for pname, pdata in natal_planets.items():
        if pname.lower() == lord.lower():
            continue
        lon = pdata.get("longitude", 0.0) if isinstance(pdata, dict) else float(pdata)
        rashi_idx = int(lon % 360 / 30)
        planet_houses[pname.lower()] = get_house_from_reference(rashi_idx, lagna_index)

    houses_aspected = get_houses_aspected_by(planet_houses)
    aspects_on_lord_house = houses_aspected.get(natal_house, [])

    result: list[dict[str, Any]] = []
    for asp in aspects_on_lord_house:
        planet = asp["planet"]
        role = classify_planet_role(planet, lagna_index)
        nature = role["functional_nature"]
        if nature in ("yogakaraka", "benefic"):
            asp_nature = "benefic"
        elif nature in ("malefic", "maraka"):
            asp_nature = "malefic"
        else:
            asp_nature = "neutral"
        result.append(
            {
                "planet": planet,
                "from_house": asp["from_house"],
                "nature": asp_nature,
            }
        )

    return result


def _find_conjunctions(
    lord: str,
    natal_planets: dict[str, Any],
    lagna_index: int,  # noqa: ARG001
) -> list[dict[str, Any]]:
    """Find planets in the same rashi as the lord."""
    lord_rashi = _get_natal_rashi(lord, natal_planets)
    if lord_rashi < 0:
        return []

    result: list[dict[str, Any]] = []
    for pname, pdata in natal_planets.items():
        if pname.lower() == lord.lower():
            continue
        lon = pdata.get("longitude", 0.0) if isinstance(pdata, dict) else float(pdata)
        p_rashi = int(lon % 360 / 30)
        if p_rashi == lord_rashi:
            # Get relationship
            try:
                from packages.core.src.knowledge_loader import get_planet_relationship

                rel = get_planet_relationship(lord, pname.lower())
            except Exception:
                rel = "neutral"
            result.append({"planet": pname.lower(), "relationship": rel})

    return result


def _find_yogas_for_planet(lord: str, birth_chart: Any) -> list[dict[str, Any]]:
    """Filter detected yogas to those involving the lord planet."""
    try:
        from packages.self.src.yoga_detector import detect_all_yogas

        yogas = detect_all_yogas(birth_chart)
    except Exception:
        return []

    result: list[dict[str, Any]] = []
    lord_lower = lord.lower()
    for yoga in yogas:
        involved = [
            p.value if hasattr(p, "value") else str(p).lower() for p in yoga.involved_planets
        ]
        if lord_lower in involved:
            result.append(
                {
                    "name": yoga.name,
                    "strength": yoga.strength,
                }
            )

    return result


def _get_shadbala(lord: str, birth_chart: Any) -> float | None:
    """Get Shadbala score for a planet (0-10 scale)."""
    try:
        from packages.self.src.strength import StrengthCalculator

        calc = StrengthCalculator()
        strengths = calc.get_all_planet_strengths(birth_chart)
        p_strength = strengths.get(lord, {})
        if isinstance(p_strength, dict):
            return round(p_strength.get("total_score", 5.0), 1)
    except Exception:
        pass
    return None


def _lookup_house_lord_reading(houses_ruled: list[int], natal_house: int) -> dict[str, Any]:
    """Look up house_lord_in_house.json for each ruled house."""
    interp = _load_lord_interpretations()
    if not interp or natal_house < 1:
        return {}

    combined: dict[str, Any] = {"summary": "", "positive": [], "negative": []}
    summaries: list[str] = []

    for ruled_house in houses_ruled:
        key = f"lord_{ruled_house}_in_house_{natal_house}"
        reading = interp.get(key, {})
        if reading:
            s = reading.get("summary", "")
            if s:
                summaries.append(s)
            combined["positive"].extend(reading.get("positive", []))
            combined["negative"].extend(reading.get("negative", []))

    combined["summary"] = "; ".join(summaries)
    return combined


def _build_summary(lord_data: dict[str, Any]) -> str:
    """Build a narrative summary from all BPHS factors."""
    lord = lord_data.get("lord", "").title()
    houses = lord_data.get("houses_ruled", [])
    natal_house = lord_data.get("natal_house", 0)
    dignity = lord_data.get("dignity", "neutral")
    aspects = lord_data.get("aspects_received", [])
    conjunctions = lord_data.get("conjunctions", [])
    is_retro = lord_data.get("is_retrograde", False)
    is_combust = lord_data.get("is_combust", False)

    parts: list[str] = []

    # Lordship
    if houses:
        house_labels = lord_data.get("house_labels", [])
        abbrev = [hl.split("(")[0].strip() for hl in house_labels]
        themes = []
        for h in houses:
            sigs = HOUSE_SIGNIFICATIONS.get(h, [])
            if sigs:
                # Use top 2 significations for richer context
                themes.append("/".join(sigs[:2]))
        if themes:
            parts.append(f"{lord} rules your {' and '.join(abbrev)} ({', '.join(themes)}).")
        else:
            parts.append(f"{lord} rules houses {', '.join(str(h) for h in houses)}.")
    else:
        parts.append(f"{lord} is a shadow planet with no classical house lordship.")

    # Placement + dignity
    if natal_house:
        dignity_text = dignity.replace("_", " ")
        natal_label = _house_label(natal_house)
        parts.append(f"Placed in {natal_label} in {dignity_text}.")

    # Retrograde / combust
    if is_retro:
        parts.append("Retrograde -- intensified, internalized energy.")
    if is_combust:
        parts.append("Combust by Sun -- reduced visibility of results.")

    # Aspects
    benefic_aspects = [a for a in aspects if a["nature"] == "benefic"]
    malefic_aspects = [a for a in aspects if a["nature"] == "malefic"]
    if benefic_aspects:
        names = [a["planet"].title() for a in benefic_aspects[:2]]
        parts.append(f"Benefic aspect from {', '.join(names)} strengthens results.")
    if malefic_aspects:
        names = [a["planet"].title() for a in malefic_aspects[:2]]
        parts.append(f"Malefic aspect from {', '.join(names)} creates challenges.")

    # Conjunctions
    if conjunctions:
        names = [c["planet"].title() for c in conjunctions[:2]]
        parts.append(f"Conjunct with {', '.join(names)}.")

    return " ".join(parts)


def _build_prediction(lord_data: dict[str, Any]) -> str:
    """Build a forward-looking prediction from BPHS factors."""
    nature = lord_data.get("functional_nature", "neutral")
    houses = lord_data.get("houses_ruled", [])
    natal_house = lord_data.get("natal_house", 0)
    dignity = lord_data.get("dignity", "neutral")
    yogas = lord_data.get("yogas", [])

    themes: list[str] = []

    # Gather themes from ruled houses
    for h in houses:
        sigs = HOUSE_SIGNIFICATIONS.get(h, [])
        themes.extend(sigs[:2])

    # Natal house themes
    if natal_house:
        natal_sigs = HOUSE_SIGNIFICATIONS.get(natal_house, [])
        themes.extend(natal_sigs[:2])

    # Deduplicate
    seen: set[str] = set()
    unique_themes: list[str] = []
    for t in themes:
        if t not in seen:
            seen.add(t)
            unique_themes.append(t)

    if not unique_themes:
        return "This period brings subtle karmic influences."

    theme_str = ", ".join(unique_themes[:4])

    if nature in ("yogakaraka", "benefic"):
        qualifier = "favors growth in"
        if dignity == "exalted":
            qualifier = "strongly blesses"
        elif dignity == "own_sign":
            qualifier = "supports steady progress in"
    elif nature in ("malefic", "maraka"):
        qualifier = "brings challenges and transformation in"
        if dignity == "exalted":
            qualifier = "brings disciplined lessons in"
    else:
        qualifier = "activates themes of"

    pred = f"This period {qualifier} {theme_str}."

    if yogas:
        yoga_names = [y["name"] for y in yogas[:2]]
        pred += f" {', '.join(yoga_names)} yoga(s) amplify results."

    return pred


# ── Public API ──


def interpret_dasha_lord(
    lord: str,
    natal_planets: dict[str, Any],
    lagna_index: int,
    birth_chart: Any = None,
) -> dict[str, Any]:
    """Interpret a dasha lord based on the native's birth chart using BPHS method.

    Args:
        lord: Planet name (lowercase, e.g. "mercury", "saturn").
        natal_planets: Dict mapping planet name -> {longitude, is_retrograde, ...}.
        lagna_index: Lagna rashi number (0-11).
        birth_chart: Optional BirthChart object for yoga/shadbala detection.

    Returns:
        Comprehensive BPHS interpretation dict with lordship, dignity,
        aspects, conjunctions, yogas, house-lord reading, summary, and prediction.
    """
    lord = lord.lower()

    # 1. Functional nature + houses ruled
    role = classify_planet_role(lord, lagna_index)
    houses_ruled = role["houses_ruled"]
    functional_nature = role["functional_nature"]

    # 2. House labels
    house_labels = [_house_label(h) for h in houses_ruled]

    # 3. Nature explanation
    nature_explanation = _nature_explanation(role, lagna_index)

    # 4. Natal house / rashi / retrograde
    natal_house = _get_natal_house(lord, natal_planets, lagna_index)
    natal_rashi = _get_natal_rashi(lord, natal_planets)
    natal_house_label = _house_label(natal_house) if natal_house else ""
    is_retro = _is_retrograde(lord, natal_planets)

    # 5. Dignity
    if natal_rashi >= 0:
        dignity, dignity_label_text = _dignity_label(lord, natal_rashi)
    else:
        dignity, dignity_label_text = "unknown", "Position unknown"

    # 6. Combustion
    is_combust = _check_combustion(lord, natal_planets)

    # 7. Aspects received
    aspects_received = _find_aspects_received(lord, natal_house, natal_planets, lagna_index)

    # 8. Conjunctions
    conjunctions = _find_conjunctions(lord, natal_planets, lagna_index)

    # 9. Yogas (only with birth_chart)
    yogas: list[dict[str, Any]] = []
    if birth_chart is not None:
        yogas = _find_yogas_for_planet(lord, birth_chart)

    # 10. Shadbala (only with birth_chart)
    shadbala_score: float | None = None
    if birth_chart is not None:
        shadbala_score = _get_shadbala(lord, birth_chart)

    # 11. House lord reading
    house_lord_reading = _lookup_house_lord_reading(houses_ruled, natal_house)

    # 12. Build summary + prediction
    lord_data = {
        "lord": lord,
        "houses_ruled": houses_ruled,
        "house_labels": house_labels,
        "functional_nature": functional_nature,
        "nature_explanation": nature_explanation,
        "natal_house": natal_house,
        "natal_house_label": natal_house_label,
        "dignity": dignity,
        "dignity_label": dignity_label_text,
        "is_retrograde": is_retro,
        "is_combust": is_combust,
        "aspects_received": aspects_received,
        "conjunctions": conjunctions,
        "yogas": yogas,
        "shadbala_score": shadbala_score,
        "house_lord_reading": house_lord_reading,
    }

    lord_data["summary"] = _build_summary(lord_data)
    lord_data["prediction"] = _build_prediction(lord_data)

    return lord_data


def interpret_dasha_combination(
    md: str,
    ad: str | None,
    pd: str | None,
    natal_planets: dict[str, Any],
    lagna_index: int,
    birth_chart: Any = None,
    sd: str | None = None,
) -> dict[str, Any]:
    """Interpret a dasha combination (MD/AD/PD/SD) using BPHS chart-specific analysis.

    Args:
        md: Mahadasha lord (lowercase).
        ad: Antardasha lord (lowercase) or None.
        pd: Pratyantardasha lord (lowercase) or None.
        natal_planets: Dict mapping planet name -> {longitude, ...}.
        lagna_index: Lagna rashi number (0-11).
        birth_chart: Optional BirthChart object.
        sd: Sookshma Dasha lord (lowercase) or None.

    Returns:
        Dict with full BPHS interpretation for each level plus
        house distance, positional relationship, combination quality,
        and overall summary.
    """
    md_interp = interpret_dasha_lord(md, natal_planets, lagna_index, birth_chart)

    ad_interp = None
    if ad:
        ad_interp = interpret_dasha_lord(ad, natal_planets, lagna_index, birth_chart)

    pd_interp = None
    if pd:
        pd_interp = interpret_dasha_lord(pd, natal_planets, lagna_index, birth_chart)

    sd_interp = None
    if sd:
        sd_interp = interpret_dasha_lord(sd, natal_planets, lagna_index, birth_chart)

    # House distance between MD and AD
    md_house = md_interp.get("natal_house", 0)
    ad_house = ad_interp.get("natal_house", 0) if ad_interp else 0

    if md_house and ad_house:
        distance = ((ad_house - md_house) % 12) or 12
        relationship_name, quality = _DISTANCE_RELATIONSHIP.get(distance, ("other", "mixed"))
    else:
        distance = 0
        relationship_name = "unknown"
        quality = "unknown"

    # Overall summary
    summary_parts: list[str] = []
    md_summary = md_interp.get("summary", "")
    if md_summary:
        summary_parts.append(md_summary)
    if ad_interp:
        ad_lord = ad_interp.get("lord", "").title()
        ad_nature = ad_interp.get("functional_nature", "neutral")
        summary_parts.append(
            f"{ad_lord} AD ({ad_nature}) colors this with {relationship_name} ({quality}) energy."
        )
    if pd_interp:
        pd_lord = pd_interp.get("lord", "").title()
        summary_parts.append(f"{pd_lord} PD triggers specific events.")

    result = {
        "mahadasha": md_interp,
        "antardasha": ad_interp,
        "pratyantardasha": pd_interp,
        "md_ad_house_distance": distance,
        "positional_relationship": relationship_name,
        "combination_quality": quality,
        "overall_summary": " ".join(summary_parts),
    }
    if sd_interp is not None:
        result["sookshma"] = sd_interp
    return result
