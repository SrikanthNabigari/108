"""House Activation Engine for Vedic Astrology.

Calculates composite activation scores for each of the 12 houses based on
current transits, aspects, double transit (Jupiter-Saturn), Ashtakavarga,
and Gochara analysis.

The key concept is the Jupiter-Saturn double transit: when both Jupiter and
Saturn influence the same house (through occupation or aspect), that house
becomes strongly activated for significant life events.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from packages.context.src.transits import get_gochara, get_transit_positions
from packages.cosmos.src.aspects import get_planet_aspects
from packages.cosmos.src.houses import (
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    get_house_from_reference,
    get_house_lord,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

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

HOUSE_THEMES: dict[int, list[str]] = {
    1: ["self", "health", "personality", "new beginnings"],
    2: ["wealth", "family", "speech", "savings"],
    3: ["siblings", "courage", "communication", "short travel"],
    4: ["home", "mother", "happiness", "property", "vehicles"],
    5: ["children", "creativity", "romance", "education", "speculation"],
    6: ["health challenges", "enemies", "debts", "service", "competition"],
    7: ["marriage", "partnerships", "business", "contracts"],
    8: ["transformation", "longevity", "occult", "inheritance", "sudden events"],
    9: ["fortune", "dharma", "father", "higher learning", "long travel"],
    10: ["career", "status", "authority", "public image", "karma"],
    11: ["gains", "friends", "aspirations", "income", "networking"],
    12: ["losses", "spirituality", "foreign lands", "isolation", "moksha"],
}

SLOW_PLANETS = {"jupiter", "saturn", "rahu", "ketu"}
FAST_PLANETS = {"sun", "moon", "mars", "mercury", "venus"}


# ---------------------------------------------------------------------------
# Function 1: Double Transit
# ---------------------------------------------------------------------------


def check_double_transit(
    jupiter_rashi: int,
    saturn_rashi: int,
    lagna_rashi: int,
) -> dict[int, dict[str, str]]:
    """Determine which houses receive the Jupiter-Saturn double transit.

    The double transit of Jupiter and Saturn is a fundamental timing tool in
    Vedic astrology.  An event signified by a house can only manifest when
    both Jupiter and Saturn simultaneously influence that house -- either by
    occupation or by aspect.

    Args:
        jupiter_rashi: Jupiter's current rashi (0-11).
        saturn_rashi:  Saturn's current rashi (0-11).
        lagna_rashi:   Ascendant rashi (0-11).

    Returns:
        Dict keyed by house number (1-12) for every house that is influenced
        by *both* Jupiter and Saturn.  Each value is a dict with keys:
            - jupiter_influence: "occupies" | "aspects"
            - saturn_influence:  "occupies" | "aspects"
            - strength:          "strong" | "moderate"
        "strong" means at least one planet occupies while the other aspects
        (or both occupy).  "moderate" means both only aspect.
    """
    jupiter_house = get_house_from_reference(jupiter_rashi, lagna_rashi)
    saturn_house = get_house_from_reference(saturn_rashi, lagna_rashi)

    # Jupiter influence map: house -> "occupies" | "aspects"
    jupiter_influence: dict[int, str] = {jupiter_house: "occupies"}
    for h in get_planet_aspects("jupiter", jupiter_house):
        if h not in jupiter_influence:
            jupiter_influence[h] = "aspects"

    # Saturn influence map
    saturn_influence: dict[int, str] = {saturn_house: "occupies"}
    for h in get_planet_aspects("saturn", saturn_house):
        if h not in saturn_influence:
            saturn_influence[h] = "aspects"

    # Intersection
    common_houses = set(jupiter_influence) & set(saturn_influence)

    result: dict[int, dict[str, str]] = {}
    for house in sorted(common_houses):
        j_inf = jupiter_influence[house]
        s_inf = saturn_influence[house]

        strength = "strong" if j_inf == "occupies" or s_inf == "occupies" else "moderate"

        result[house] = {
            "jupiter_influence": j_inf,
            "saturn_influence": s_inf,
            "strength": strength,
        }

    return result


# ---------------------------------------------------------------------------
# Function 2: House Activations
# ---------------------------------------------------------------------------


def _get_planet_rashi(planet_data: dict[str, Any]) -> int:
    """Extract rashi index (0-11) from a planet data dict."""
    if "rashi_num" in planet_data:
        return int(planet_data["rashi_num"])
    if "rashi" in planet_data and isinstance(planet_data["rashi"], int):
        return int(planet_data["rashi"])
    # Fallback: derive from longitude
    longitude = planet_data.get("longitude", 0.0)
    return int(float(longitude) // 30)


def get_house_activations(
    transit_positions: dict[str, dict[str, Any]],
    lagna_rashi: int,
    moon_rashi: int,
    chart: Any | None = None,
) -> list[dict[str, Any]]:
    """Build composite activation score (0-100) for each of the 12 houses.

    The score is composed of six components:
    - Presence score (0-25): planets occupying the house
    - Aspect score (0-20): planets aspecting the house
    - Double transit score (0-20): Jupiter-Saturn double transit
    - Ashtakavarga score (0-15): SAV bindus for the house sign
    - Gochara score (0-10): favorability from Moon
    - Lordship bonus (0-10): quality of house lord placement

    Args:
        transit_positions: Dict of planet name -> dict with at least
            "longitude" and "rashi_num" (or "rashi" as int 0-11).
        lagna_rashi: Ascendant rashi (0-11).
        moon_rashi:  Moon rashi (0-11).
        chart:       Optional BirthChart for Ashtakavarga lookup.

    Returns:
        List of 12 dicts (one per house) sorted by house number ascending.
    """
    # Step 1: Map planets to houses from lagna
    planets_in_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    planets_aspecting_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}

    planet_house_map: dict[str, int] = {}
    planet_rashi_map: dict[str, int] = {}

    for planet, data in transit_positions.items():
        rashi = _get_planet_rashi(data)
        planet_rashi_map[planet] = rashi
        house = get_house_from_reference(rashi, lagna_rashi)
        planet_house_map[planet] = house
        planets_in_house[house].append(planet)

    # Step 2: Build aspect map
    for planet, house in planet_house_map.items():
        aspected_houses = get_planet_aspects(planet, house)
        for ah in aspected_houses:
            if planet not in planets_aspecting_house[ah]:
                planets_aspecting_house[ah].append(planet)

    # Step 3: Compute double transit once
    jupiter_rashi = planet_rashi_map.get("jupiter")
    saturn_rashi = planet_rashi_map.get("saturn")
    double_transit_map: dict[int, dict[str, str]] = {}
    if jupiter_rashi is not None and saturn_rashi is not None:
        double_transit_map = check_double_transit(jupiter_rashi, saturn_rashi, lagna_rashi)

    # Step 4: Precompute SAV if chart is available
    sav_scores: list[int] | None = None
    if chart is not None:
        try:
            from packages.self.src.ashtakavarga import calculate_sarvashtakavarga

            sav_scores = calculate_sarvashtakavarga(chart)
        except Exception:
            sav_scores = None

    # Build all transit rashis dict for gochara calls
    all_transit_rashis: dict[str, int] = {p: planet_rashi_map[p] for p in planet_rashi_map}

    # Step 5: Score each house
    activations: list[dict[str, Any]] = []

    for house in range(1, 13):
        # --- Presence score (0-25) ---
        presence = 0
        for p in planets_in_house[house]:
            if p.lower() in SLOW_PLANETS:
                presence += 15
            else:
                presence += 8
        presence = min(presence, 25)

        # --- Aspect score (0-20) ---
        aspect = 0
        for p in planets_aspecting_house[house]:
            if p.lower() in SLOW_PLANETS:
                aspect += 10
            else:
                aspect += 5
        aspect = min(aspect, 20)

        # --- Double transit score (0-20) ---
        dt_info = double_transit_map.get(house)
        has_double_transit = dt_info is not None
        dt_score = 0
        if dt_info is not None:
            dt_score = 20 if dt_info["strength"] == "strong" else 12

        # --- Ashtakavarga score (0-15) ---
        house_sign = (lagna_rashi + house - 1) % 12
        sav_value: int | None = None
        if sav_scores is not None:
            sav_value = sav_scores[house_sign]
            if sav_value >= 30:
                ashta_score = 15
            elif sav_value >= 25:
                ashta_score = 10
            else:
                ashta_score = 3
        else:
            ashta_score = 7  # neutral

        # --- Gochara score (0-10) ---
        favorable_count = 0
        total_count = 0
        for p in planets_in_house[house]:
            p_rashi = planet_rashi_map.get(p)
            if p_rashi is not None:
                try:
                    gochara_result = get_gochara(moon_rashi, p, p_rashi, all_transit_rashis)
                    total_count += 1
                    if gochara_result.get("is_favorable"):
                        favorable_count += 1
                except Exception:
                    pass
        favorable_ratio = favorable_count / total_count if total_count > 0 else 0.5
        gochara_score = round(favorable_ratio * 10)

        # --- Lordship bonus (0-10) ---
        lordship_bonus = 5  # default
        try:
            lord = get_house_lord(house, lagna_rashi)
            lord_rashi = planet_rashi_map.get(lord)
            if lord_rashi is not None:
                lord_house = get_house_from_reference(lord_rashi, lagna_rashi)
                if lord_house in KENDRA_HOUSES or lord_house in TRIKONA_HOUSES:
                    lordship_bonus = 10
                elif lord_house in UPACHAYA_HOUSES:
                    lordship_bonus = 6
                elif lord_house in DUSTHANA_HOUSES:
                    lordship_bonus = 2
                else:
                    lordship_bonus = 5
        except Exception:
            pass

        # --- Total ---
        total = presence + aspect + dt_score + ashta_score + gochara_score + lordship_bonus
        total = min(total, 100)

        # Grade
        if total >= 70:
            grade = "highly_active"
        elif total >= 40:
            grade = "active"
        elif total >= 20:
            grade = "moderate"
        else:
            grade = "quiet"

        # Summary
        present_names = planets_in_house[house]
        if present_names:
            planets_str = ", ".join(present_names)
            summary = f"House {house} is {grade} with {planets_str} present"
        else:
            summary = f"House {house} is {grade} with no planets present"
        if has_double_transit:
            summary += " (double transit active)"

        activations.append(
            {
                "house": house,
                "sign": house_sign,
                "score": total,
                "grade": grade,
                "planets_present": list(present_names),
                "planets_aspecting": list(planets_aspecting_house[house]),
                "double_transit": has_double_transit,
                "ashtakavarga_sav": sav_value,
                "themes": HOUSE_THEMES[house],
                "summary": summary,
            }
        )

    return activations


# ---------------------------------------------------------------------------
# Function 3: Transit Snapshot
# ---------------------------------------------------------------------------


def get_transit_snapshot(
    julian_day: float,
    lagna_rashi: int,
    moon_rashi: int,
    natal_planets: dict[str, dict[str, Any]],
    chart: Any | None = None,
) -> dict[str, Any]:
    """Top-level combiner: transit snapshot with house activations.

    Fetches current transit positions, computes house activations, extracts
    double-transit houses, and determines the overall trend.

    Args:
        julian_day:    Julian Day Number for the transit moment.
        lagna_rashi:   Ascendant rashi (0-11).
        moon_rashi:    Moon rashi (0-11).
        natal_planets: Natal planet positions dict (for aspect calculation).
        chart:         Optional BirthChart for Ashtakavarga lookup.

    Returns:
        Dict with keys: timestamp, transit_positions, house_activations,
        double_transit_houses, most_active_houses, most_quiet_houses,
        active_aspects, overall_trend, summary.
    """
    # 1. Get transit positions
    transit_positions = get_transit_positions(julian_day)

    # 2. Compute house activations
    house_activations = get_house_activations(transit_positions, lagna_rashi, moon_rashi, chart)

    # 3. Extract double transit houses
    double_transit_houses = [h["house"] for h in house_activations if h["double_transit"]]

    # 4. Sort by score descending
    sorted_houses = sorted(house_activations, key=lambda h: h["score"], reverse=True)
    most_active = [h["house"] for h in sorted_houses[:3]]
    most_quiet = [h["house"] for h in sorted_houses[-2:]]

    # 5. Get transit-natal aspects
    active_aspects: list[dict[str, Any]] = []
    try:
        from packages.context.src.transit_aspects import get_transit_natal_aspects

        active_aspects = get_transit_natal_aspects(natal_planets, transit_positions)
    except Exception:
        pass

    # 5b. Build gochara summary for each transit planet
    gochara_summary: list[dict[str, Any]] = []
    transit_rashis: dict[str, int] = {}
    for p_name, p_data in transit_positions.items():
        transit_rashis[p_name] = int(p_data.get("longitude", 0)) // 30

    for p_name, p_data in transit_positions.items():
        t_rashi = int(p_data.get("longitude", 0)) // 30
        try:
            gochara = get_gochara(moon_rashi, p_name, t_rashi, transit_rashis)
        except Exception:
            continue

        entry: dict[str, Any] = {
            "planet": p_name,
            "sign": RASHI_NAMES[t_rashi],
            "house_from_moon": gochara["house_from_moon"],
            "is_favorable": gochara["is_favorable"],
            "has_vedha": gochara["has_vedha"],
            "vedha_by": gochara.get("vedha_by"),
            "net_effect": gochara["net_effect"],
            "effects": gochara.get("effects", []),
            "is_retrograde": p_data.get("is_retrograde", False),
            "degree_in_sign": round(p_data.get("longitude", 0) % 30, 1),
        }

        # Add BAV score if chart is provided (skip Rahu/Ketu — no BAV)
        if chart is not None and p_name.lower() not in ("rahu", "ketu"):
            try:
                from packages.core.src.constants import Planet
                from packages.self.src.ashtakavarga import (
                    get_transit_ashtakavarga_analysis,
                )

                planet_enum = Planet(p_name.lower())
                av_analysis = get_transit_ashtakavarga_analysis(planet_enum, t_rashi, chart)
                entry["bav_score"] = av_analysis["bav_score"]
            except Exception:
                entry["bav_score"] = None
        else:
            entry["bav_score"] = None

        gochara_summary.append(entry)

    # 6. Overall trend from average of top 3 scores
    top_3_scores = [h["score"] for h in sorted_houses[:3]]
    avg_top = sum(top_3_scores) / len(top_3_scores) if top_3_scores else 0

    if avg_top >= 60:
        overall_trend = "favorable"
    elif avg_top >= 35:
        overall_trend = "mixed"
    else:
        overall_trend = "challenging"

    # 7. Summary
    if double_transit_houses:
        dt_str = ", ".join(str(h) for h in double_transit_houses)
        summary = f"Jupiter-Saturn double transit activating houses {dt_str}. Overall trend is {overall_trend}."
    else:
        summary = f"No double transit active. Overall trend is {overall_trend}."

    return {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "transit_positions": transit_positions,
        "house_activations": house_activations,
        "double_transit_houses": double_transit_houses,
        "most_active_houses": most_active,
        "most_quiet_houses": most_quiet,
        "active_aspects": active_aspects,
        "gochara_summary": gochara_summary,
        "overall_trend": overall_trend,
        "summary": summary,
    }


__all__ = [
    "FAST_PLANETS",
    "HOUSE_THEMES",
    "SLOW_PLANETS",
    "check_double_transit",
    "get_house_activations",
    "get_transit_snapshot",
]
