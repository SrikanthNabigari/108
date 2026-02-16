"""Krishnamurti Paddhati (KP) system for Vedic astrology.

Implements the complete KP system including:
- Sign lords and star lords (Nakshatra) for any longitude
- Sub-lords and sub-sub-lords derived from Vimshottari proportions
- House cusp analysis using sign/star/sub-lord trilogy
- KP significators (4-level hierarchy: occupants of house, planets in star of occupants, etc.)
- Ruling planets at a given moment (Lagna, Moon, day lord)
- House promise analysis (fulfilled or denied based on sub-lord significates)
- Life prediction for all major query types (marriage, career, wealth, health, etc.)

The KP system's core innovation is the sub-lord table where each nakshatra is
divided into 9 unequal subdivisions proportional to Vimshottari dasha years (120 years total).
The sequence of sub-lords follows Vimshottari, starting from the star lord.

Key Principle: The SUB-LORD of a house cusp determines whether that house's promise
will be FULFILLED or DENIED. If the sub-lord significates houses supporting the matter,
the answer is favorable. If it significates denying houses, the answer is unfavorable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from packages.core.src.constants import (
    NAKSHATRA_SPAN,
)
from packages.cosmos.src.nakshatras import NAKSHATRA_LORDS, longitude_to_nakshatra
from packages.self.src.combustion import check_combustion

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class KPSublordInfo(TypedDict):
    """Information about sign, star, and sub-lord for a longitude."""

    longitude: float
    sign: str
    sign_lord: str
    star: str
    star_number: int
    star_lord: str
    sub_lord: str
    sub_sub_lord: str
    degree_in_sub: float
    sub_span: float


class KPHouseAnalysis(TypedDict):
    """KP analysis for a single house."""

    house: int
    cusp_longitude: float
    cusp_sign: str
    sign_lord: str
    star_lord: str
    sub_lord: str
    sub_lord_significates: list[int]
    supporting_houses: list[int]
    denying_houses: list[int]
    judgment: str
    strength: float
    explanation: str


class KPRulingPlanets(TypedDict):
    """KP ruling planets at a given moment."""

    lagna_sign_lord: str
    lagna_star_lord: str
    moon_sign_lord: str
    moon_star_lord: str
    day_lord: str
    ruling_planets: list[str]
    strongest: str
    frequencies: dict[str, int]


class KPSignificators(TypedDict):
    """KP significators for a house."""

    level_1: list[str]
    level_2: list[str]
    level_3: list[str]
    level_4: list[str]
    all_significators: list[str]


class KPSublordEntry(TypedDict):
    """Single entry in KP sub-lord table."""

    start_degree: float
    end_degree: float
    star: str
    star_lord: str
    sub_lord: str
    sign: str
    sign_lord: str


class KPPredictionResult(TypedDict):
    """Complete KP prediction result."""

    query_type: str
    primary_house: int
    cusp_analysis: KPHouseAnalysis
    significator_analysis: dict[str, Any]
    ruling_planet_confirmation: bool
    judgment: str
    confidence: float
    timing_hints: dict[str, Any]
    explanation: str


# ============================================================================
# CONSTANTS
# ============================================================================

# Vimshottari dasha years (same as DASHA_YEARS but as dict for easy access)
VIMSHOTTARI_YEARS: dict[str, int] = {
    "ketu": 7,
    "venus": 20,
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "rahu": 18,
    "jupiter": 16,
    "saturn": 19,
    "mercury": 17,
}
TOTAL_VIMSHOTTARI = 120

# Vimshottari sequence (9 planets)
VIMSHOTTARI_SEQUENCE = [
    "ketu",
    "venus",
    "sun",
    "moon",
    "mars",
    "rahu",
    "jupiter",
    "saturn",
    "mercury",
]

# Sign rulers (lowercase)
SIGN_RULERS: dict[str, str] = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

# All rashi names in order
RASHI_NAMES = [
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

# Day lords (Python weekday convention: 0=Monday, 6=Sunday)
DAY_LORDS: dict[int, str] = {
    0: "moon",
    1: "mars",
    2: "mercury",
    3: "jupiter",
    4: "venus",
    5: "saturn",
    6: "sun",
}

# KP house groups for different life queries
KP_HOUSE_GROUPS: dict[str, dict[str, Any]] = {
    "marriage": {"primary": 7, "support": [2, 7, 11], "deny": [1, 6, 10, 12]},
    "career": {"primary": 10, "support": [2, 6, 10, 11], "deny": [1, 5, 9, 12]},
    "children": {"primary": 5, "support": [2, 5, 11], "deny": [1, 4, 10, 12]},
    "wealth": {"primary": 2, "support": [2, 6, 10, 11], "deny": [1, 5, 8, 12]},
    "health": {"primary": 1, "support": [1, 5, 9, 11], "deny": [6, 8, 12]},
    "education": {"primary": 4, "support": [4, 9, 11], "deny": [3, 8, 12]},
    "travel_short": {"primary": 3, "support": [3, 9, 12], "deny": [1, 4, 10]},
    "travel_foreign": {"primary": 9, "support": [3, 9, 12], "deny": [1, 4, 10]},
    "property": {"primary": 4, "support": [4, 11], "deny": [3, 5, 12]},
    "legal": {"primary": 6, "support": [6, 11], "deny": [7, 12]},
    "spiritual": {"primary": 12, "support": [5, 9, 12], "deny": [1, 3, 10]},
}

# KP significator level weights (KP Reader 6 standard)
_SIG_WEIGHTS: dict[str, int] = {
    "level_1": 4,  # Planets in stars of occupants (strongest)
    "level_2": 3,  # Occupants
    "level_3": 2,  # Planets in stars of house lord
    "level_4": 1,  # House lord (weakest)
}

# House labels for rich explanations
_HOUSE_LABELS: dict[int, str] = {
    1: "self/personality",
    2: "family/wealth",
    3: "siblings/short travel",
    4: "home/mother/education",
    5: "children/creativity",
    6: "enemies/service/health issues",
    7: "marriage/partnerships",
    8: "longevity/obstacles",
    9: "fortune/father/higher learning",
    10: "career/status",
    11: "gains/income/friends",
    12: "losses/foreign/spirituality",
}

# Cache for sub-lord table
_SUBLORD_TABLE_CACHE: list[KPSublordEntry] | None = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _get_sign_number(sign: str) -> int:
    """Convert sign name to number (0-11)."""
    sign_lower = sign.lower()
    try:
        return RASHI_NAMES.index(sign_lower)
    except ValueError as err:
        raise ValueError(f"Invalid sign: {sign}") from err


def _get_sign_from_number(num: int) -> str:
    """Convert sign number (0-11) to name."""
    if not 0 <= num <= 11:
        raise ValueError(f"Sign number must be 0-11, got {num}")
    return RASHI_NAMES[num]


def _normalize_longitude(lon: float) -> float:
    """Normalize longitude to 0-360 range."""
    lon = lon % 360
    return lon if lon >= 0 else lon + 360


def _get_next_sublord(current_sublord: str) -> str:
    """Get the next sublord in Vimshottari sequence."""
    idx = VIMSHOTTARI_SEQUENCE.index(current_sublord)
    return VIMSHOTTARI_SEQUENCE[(idx + 1) % 9]


def _build_sublord_table() -> list[KPSublordEntry]:
    """Build the complete KP sub-lord table for all 360 degrees.

    Each nakshatra (13°20') is divided into 9 sub-lords proportional to
    Vimshottari years. The sub-lord sequence starts from the star lord.

    Returns:
        List of sub-lord entries covering the entire zodiac.
    """
    if _SUBLORD_TABLE_CACHE is not None:
        return _SUBLORD_TABLE_CACHE

    table: list[KPSublordEntry] = []

    # Iterate through all 27 nakshatras
    for star_num in range(1, 28):
        star_lord = NAKSHATRA_LORDS[star_num]
        star_start = (star_num - 1) * NAKSHATRA_SPAN
        star_end = star_num * NAKSHATRA_SPAN

        # Get star name
        star_info = longitude_to_nakshatra(star_start + 0.1)
        star_name = star_info["name"]

        # Build 9 sub-divisions within this nakshatra
        sublord_idx = VIMSHOTTARI_SEQUENCE.index(star_lord)
        current_degree = star_start

        for _sub_idx in range(9):
            # Get current and next sub-lord
            current_sublord = VIMSHOTTARI_SEQUENCE[sublord_idx]
            years = VIMSHOTTARI_YEARS[current_sublord]
            sub_span = (years / TOTAL_VIMSHOTTARI) * NAKSHATRA_SPAN

            sub_start = current_degree
            sub_end = min(current_degree + sub_span, star_end)

            # Determine sign for this sub-division
            sub_sign_num = int(sub_start // 30)
            sub_sign = _get_sign_from_number(sub_sign_num)
            sub_sign_lord = SIGN_RULERS[sub_sign]

            # Add entry to table
            table.append(
                KPSublordEntry(
                    start_degree=sub_start,
                    end_degree=sub_end,
                    star=star_name,
                    star_lord=star_lord,
                    sub_lord=current_sublord,
                    sign=sub_sign,
                    sign_lord=sub_sign_lord,
                )
            )

            current_degree = sub_end
            sublord_idx = (sublord_idx + 1) % 9

        # Handle any rounding gap and move to next nakshatra
        if current_degree < star_end:
            remaining = star_end - current_degree
            if remaining > 0.001:  # Not just floating point noise
                current_sublord = VIMSHOTTARI_SEQUENCE[sublord_idx]
                sub_sign_num = int(current_degree // 30)
                sub_sign = _get_sign_from_number(sub_sign_num)
                sub_sign_lord = SIGN_RULERS[sub_sign]

                table.append(
                    KPSublordEntry(
                        start_degree=current_degree,
                        end_degree=star_end,
                        star=star_name,
                        star_lord=star_lord,
                        sub_lord=current_sublord,
                        sign=sub_sign,
                        sign_lord=sub_sign_lord,
                    )
                )

    return table


# ============================================================================
# CORE KP FUNCTIONS
# ============================================================================


def get_kp_sublord(longitude: float) -> KPSublordInfo:
    """Get sign lord, star lord, and sub-lord for any longitude.

    Args:
        longitude: Ecliptic longitude in degrees (0-360).

    Returns:
        Dictionary with sign, sign_lord, star, star_lord, sub_lord, sub_sub_lord,
        and degree information.

    Raises:
        ValueError: If longitude is invalid.
    """
    if longitude < 0:
        raise ValueError(f"Longitude must be non-negative, got {longitude}")
    lon = _normalize_longitude(longitude)

    # Get star information
    star_info = longitude_to_nakshatra(lon)
    star_name = star_info["name"]
    star_num = star_info["number"]
    star_lord = NAKSHATRA_LORDS[star_num]

    # Get sign information
    sign_num = int(lon // 30)
    sign = _get_sign_from_number(sign_num)
    sign_lord = SIGN_RULERS[sign]

    # Find sub-lord using the sub-lord table
    table = _build_sublord_table()
    sub_lord = "ketu"  # default
    sub_sub_lord = "venus"  # default
    degree_in_sub = 0.0
    sub_span = 0.0

    for entry in table:
        if entry["start_degree"] <= lon < entry["end_degree"]:
            sub_lord = entry["sub_lord"]
            degree_in_sub = lon - entry["start_degree"]
            sub_span = entry["end_degree"] - entry["start_degree"]

            # Get sub-sub-lord (next in sequence after sub-lord)
            sub_idx = VIMSHOTTARI_SEQUENCE.index(sub_lord)
            sub_sub_lord = VIMSHOTTARI_SEQUENCE[(sub_idx + 1) % 9]
            break

    return KPSublordInfo(
        longitude=lon,
        sign=sign,
        sign_lord=sign_lord,
        star=star_name,
        star_number=star_num,
        star_lord=star_lord,
        sub_lord=sub_lord,
        sub_sub_lord=sub_sub_lord,
        degree_in_sub=round(degree_in_sub, 4),
        sub_span=round(sub_span, 4),
    )


def get_cuspal_sublords(cusps: list[float]) -> list[dict[str, Any]]:
    """Get sub-lord information for each of 12 house cusps.

    Args:
        cusps: List of 12 cusp longitudes (0-360).

    Returns:
        List of 12 dicts, each with sign_lord, star_lord, sub_lord for that cusp.

    Raises:
        ValueError: If cusps list is not exactly 12 elements.
    """
    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    result = []
    for house_num, cusp_lon in enumerate(cusps, start=1):
        kp_info = get_kp_sublord(cusp_lon)
        result.append(
            {
                "house": house_num,
                "cusp_longitude": kp_info["longitude"],
                "sign": kp_info["sign"],
                "sign_lord": kp_info["sign_lord"],
                "star": kp_info["star"],
                "star_lord": kp_info["star_lord"],
                "sub_lord": kp_info["sub_lord"],
            }
        )

    return result


def get_kp_significators(
    planets: dict[str, dict[str, Any]],
    cusps: list[float],
) -> dict[int, KPSignificators]:
    """Determine KP significators for each house (1-12).

    KP Significator hierarchy (strongest to weakest):
    Level 1: Planets in the STAR of occupants of the house
    Level 2: Occupants of the house
    Level 3: Planets in the STAR of the lord of the house
    Level 4: The lord of the house itself

    Args:
        planets: Dict mapping planet_name to {"longitude": float, "sign": str, ...}
        cusps: List of 12 house cusp longitudes.

    Returns:
        Dict mapping house_number to significators at each level.

    Raises:
        ValueError: If cusps length is not 12.
    """
    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    result: dict[int, KPSignificators] = {}

    # Get house lords and occupants
    house_lords: dict[int, str] = {}
    house_occupants: dict[int, list[str]] = {i: [] for i in range(1, 13)}

    # Determine which planets occupy which houses
    for planet_name, planet_data in planets.items():
        if not isinstance(planet_data, dict):
            continue
        lon = planet_data.get("longitude")
        if lon is None:
            continue

        # Find which house contains this longitude
        for house_num in range(1, 13):
            cusp_idx = house_num - 1
            next_cusp_idx = house_num % 12
            cusp1 = cusps[cusp_idx]
            cusp2 = cusps[next_cusp_idx]

            # Handle wrapping around 0/360
            in_house = cusp1 <= lon < cusp2 if cusp1 < cusp2 else lon >= cusp1 or lon < cusp2

            if in_house:
                house_occupants[house_num].append(planet_name)
                break

    # Determine house lords (from cusp sub-lord)
    for house_num in range(1, 13):
        cusp_lon = cusps[house_num - 1]
        kp_info = get_kp_sublord(cusp_lon)
        house_lords[house_num] = kp_info["sub_lord"]

    # Build significators for each house
    for house_num in range(1, 13):
        level_1: list[str] = []
        level_2 = list(house_occupants[house_num])
        level_3: list[str] = []
        level_4 = [house_lords[house_num]]

        # Level 1: planets in star of occupants
        for occupant in level_2:
            occupant_lon = planets[occupant].get("longitude", 0)
            occupant_star = longitude_to_nakshatra(occupant_lon)
            occupant_star_lord = NAKSHATRA_LORDS[occupant_star["number"]]

            # Find planets in this star
            for planet_name, planet_data in planets.items():
                if not isinstance(planet_data, dict):
                    continue
                p_lon = planet_data.get("longitude")
                if p_lon is None:
                    continue
                p_star = longitude_to_nakshatra(p_lon)
                if (
                    NAKSHATRA_LORDS[p_star["number"]] == occupant_star_lord
                    and planet_name not in level_1
                ):
                    level_1.append(planet_name)

        # Level 3: planets in star of house lord
        house_lord = house_lords[house_num]
        for planet_name, planet_data in planets.items():
            if not isinstance(planet_data, dict):
                continue
            p_lon = planet_data.get("longitude")
            if p_lon is None:
                continue
            p_star = longitude_to_nakshatra(p_lon)
            if NAKSHATRA_LORDS[p_star["number"]] == house_lord and planet_name not in level_3:
                level_3.append(planet_name)

        # Compile all unique significators
        all_sigs = list(dict.fromkeys(level_1 + level_2 + level_3 + level_4))

        result[house_num] = KPSignificators(
            level_1=level_1,
            level_2=level_2,
            level_3=level_3,
            level_4=level_4,
            all_significators=all_sigs,
        )

    return result


def get_ruling_planets(
    datetime_iso: str,
    latitude: float,
    longitude: float,
) -> KPRulingPlanets:
    """Get KP Ruling Planets at a given moment.

    The 5 ruling planets are:
    1. Lagna sign lord (ascendant sign ruler)
    2. Lagna star lord (nakshatra lord of ascendant degree)
    3. Moon sign lord
    4. Moon star lord
    5. Day lord (planet ruling the weekday)

    A planet appearing multiple times is STRONGER.

    Args:
        datetime_iso: ISO format datetime string.
        latitude: Location latitude.
        longitude: Location longitude.

    Returns:
        Dict with individual ruling planets, unique list, strongest, and frequencies.

    Raises:
        ValueError: If datetime cannot be parsed or location is invalid.
    """
    try:
        dt = datetime.fromisoformat(datetime_iso)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid datetime format: {datetime_iso}") from e

    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError(f"Invalid coordinates: lat={latitude}, lon={longitude}")

    # Import ephemeris functions
    try:
        from packages.cosmos.src.ephemeris import get_all_planets, get_house_cusps, get_julian_day
    except ImportError as err:
        raise ImportError("Cannot import ephemeris functions") from err

    # Convert datetime to Julian Day
    jd = get_julian_day(dt)

    # Calculate positions (KP mandates Placidus houses)
    planets = get_all_planets(jd)
    cusps_result = get_house_cusps(jd, latitude, longitude, house_system="placidus")
    cusps = cusps_result["cusps"]

    # Get lagna (1st house cusp)
    lagna_lon = cusps[0]
    lagna_info = get_kp_sublord(lagna_lon)
    lagna_sign_lord = lagna_info["sign_lord"]
    lagna_star_lord = lagna_info["star_lord"]

    # Get Moon sign and star lord
    moon_lon = planets.get("moon", {}).get("longitude", 0)
    moon_info = get_kp_sublord(moon_lon)
    moon_sign_lord = moon_info["sign_lord"]
    moon_star_lord = moon_info["star_lord"]

    # Get day lord
    weekday = dt.weekday()  # 0=Monday, 6=Sunday
    day_lord = DAY_LORDS[weekday]

    # Compile ruling planets and count frequencies
    ruling_planets_list = [
        lagna_sign_lord,
        lagna_star_lord,
        moon_sign_lord,
        moon_star_lord,
        day_lord,
    ]
    unique_ruling = list(dict.fromkeys(ruling_planets_list))

    frequencies: dict[str, int] = {}
    for planet in ruling_planets_list:
        frequencies[planet] = frequencies.get(planet, 0) + 1

    # Find strongest (most frequent)
    strongest = max(unique_ruling, key=lambda p: frequencies.get(p, 0))

    return KPRulingPlanets(
        lagna_sign_lord=lagna_sign_lord,
        lagna_star_lord=lagna_star_lord,
        moon_sign_lord=moon_sign_lord,
        moon_star_lord=moon_star_lord,
        day_lord=day_lord,
        ruling_planets=unique_ruling,
        strongest=strongest,
        frequencies=frequencies,
    )


def _get_planet_modifiers(
    planet_name: str,
    planets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Get retrograde and combustion modifiers for a planet.

    Per KP doctrine, retrograde means "delayed but not denied" (no confidence
    penalty). Combustion reduces effectiveness by up to 15%.

    Args:
        planet_name: Planet name (lowercase).
        planets: Dict of planet positions.

    Returns:
        Dict with is_retrograde, is_combust, combustion_strength_loss, and notes.
    """
    pdata = planets.get(planet_name, {})
    if not isinstance(pdata, dict):
        return {
            "is_retrograde": False,
            "is_combust": False,
            "combustion_strength_loss": 0,
            "notes": [],
        }

    is_retro = pdata.get("is_retrograde", False)
    notes: list[str] = []

    if is_retro:
        notes.append(f"{planet_name.title()} is retrograde — delayed but not denied")

    # Check combustion (requires Sun position)
    sun_data = planets.get("sun", {})
    sun_lon = sun_data.get("longitude") if isinstance(sun_data, dict) else None
    planet_lon = pdata.get("longitude")
    is_combust = False
    strength_loss = 0

    if (
        planet_lon is not None
        and sun_lon is not None
        and planet_name not in ("sun", "rahu", "ketu")
    ):
        comb_result = check_combustion(
            planet=planet_name,
            planet_lon=planet_lon,
            sun_lon=sun_lon,
            is_retrograde=is_retro,
        )
        is_combust = comb_result.get("is_combust", False)
        if is_combust:
            # strength_loss from combustion is 0-1 scale; map to 0-15% confidence reduction
            raw_loss = comb_result.get("strength_loss", 0)
            strength_loss = min(15, round(raw_loss * 15))
            deep = " (deep)" if comb_result.get("is_deep_combust") else ""
            notes.append(f"{planet_name.title()} is combust{deep} — delays possible")

    return {
        "is_retrograde": is_retro,
        "is_combust": is_combust,
        "combustion_strength_loss": strength_loss,
        "notes": notes,
    }


def _build_rich_explanation(
    sub_lord: str,
    star_lord: str,
    sub_lord_significates: list[int],
    supporting_houses: list[int],
    denying_houses: list[int],
    overlap_support: int,
    overlap_deny: int,
    star_lord_used: bool = False,
    star_lord_significates: list[int] | None = None,
    modifier_notes: list[str] | None = None,
) -> str:
    """Build a rich explanation with house labels.

    Args:
        sub_lord: Sub-lord planet name.
        star_lord: Star lord planet name.
        sub_lord_significates: Houses the sub-lord significates.
        supporting_houses: Houses that support the matter.
        denying_houses: Houses that deny the matter.
        overlap_support: Count of supporting overlap.
        overlap_deny: Count of denying overlap.
        star_lord_used: Whether star lord was used as backup.
        star_lord_significates: Houses the star lord significates (if used).
        modifier_notes: Notes about retrograde/combustion modifiers.

    Returns:
        Rich explanation string with house labels.
    """

    def _house_list(houses: list[int]) -> str:
        parts = []
        for h in houses:
            label = _HOUSE_LABELS.get(h, "")
            parts.append(f"{h} ({label})" if label else str(h))
        return ", ".join(parts)

    # Sub-lord significates with labels
    sup_overlap = sorted(set(sub_lord_significates) & set(supporting_houses))
    den_overlap = sorted(set(sub_lord_significates) & set(denying_houses))

    parts: list[str] = []

    if sup_overlap:
        parts.append(
            f"Sub-lord {sub_lord.title()} significates houses {_house_list(sup_overlap)} — "
            f"{'strong' if overlap_support >= 2 else 'moderate'} support."
        )
    if den_overlap:
        deny_strength = "strong" if overlap_deny >= 2 else "some"
        parts.append(
            f"Sub-lord {sub_lord.title()} also significates denying houses "
            f"{_house_list(den_overlap)} — {deny_strength} opposition."
        )
    if not sup_overlap and not den_overlap:
        parts.append(
            f"Sub-lord {sub_lord.title()} significates houses {sub_lord_significates} "
            f"with no direct overlap to supporting or denying houses."
        )

    # Star lord backup
    if star_lord_used and star_lord_significates:
        star_sup = sorted(set(star_lord_significates) & set(supporting_houses))
        star_den = sorted(set(star_lord_significates) & set(denying_houses))
        if star_sup:
            parts.append(f"Star lord {star_lord.title()} backs via houses {_house_list(star_sup)}.")
        if star_den:
            parts.append(
                f"Star lord {star_lord.title()} also indicates houses {_house_list(star_den)}."
            )

    # Modifier notes (retrograde, combustion)
    if modifier_notes:
        parts.extend(modifier_notes)

    return " ".join(parts)


def analyze_kp_house(
    house_number: int,
    planets: dict[str, dict[str, Any]],
    cusps: list[float],
    question: str | None = None,
) -> KPHouseAnalysis:
    """Analyze a specific house using KP method.

    The KEY KP principle: The SUB-LORD of a house cusp determines whether
    that house's promise will be fulfilled or denied. If the sub-lord of a cusp
    is a significator of houses that SUPPORT the matter → YES (favorable).
    If significator of houses that DENY the matter → NO (unfavorable).

    Args:
        house_number: House to analyze (1-12).
        planets: Dict of planet positions.
        cusps: List of 12 house cusp longitudes.
        question: Optional question type for context (e.g., "marriage").

    Returns:
        Complete KP house analysis with judgment and strength.

    Raises:
        ValueError: If house_number is invalid or cusps length is wrong.
    """
    if not 1 <= house_number <= 12:
        raise ValueError(f"House number must be 1-12, got {house_number}")
    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    # Get cusp information
    cusp_lon = cusps[house_number - 1]
    kp_info = get_kp_sublord(cusp_lon)

    # Get significators for this house
    significators = get_kp_significators(planets, cusps)
    # Determine which houses the sub-lord significates
    sub_lord = kp_info["sub_lord"]
    sub_lord_significates: list[int] = []

    for check_house in range(1, 13):
        check_sigs = significators.get(check_house, {}).get("all_significators", [])
        if sub_lord in check_sigs:
            sub_lord_significates.append(check_house)

    # Default supporting/denying houses based on question
    supporting_houses: list[int] = []
    denying_houses: list[int] = []

    if question and question in KP_HOUSE_GROUPS:
        groups = KP_HOUSE_GROUPS[question]
        supporting_houses = groups.get("support", [])
        denying_houses = groups.get("deny", [])
    else:
        # Default to generic house meanings
        supporting_houses = [house_number, 2, 11]  # Self, 2nd, 11th usually support
        denying_houses = [1, 6, 10, 12]  # Dusthana and upachaya can deny

    # Calculate overlap and judgment
    overlap_support = len(set(sub_lord_significates) & set(supporting_houses))
    overlap_deny = len(set(sub_lord_significates) & set(denying_houses))
    total_overlap = overlap_support + overlap_deny

    # Phase 1: Star lord backup when sub-lord has zero overlap
    star_lord_used = False
    star_lord_name = kp_info["star_lord"]
    star_lord_significates: list[int] = []
    _STAR_LORD_DAMPENING = 0.7  # Star lord is less precise than sub-lord

    if total_overlap == 0:
        # Check star lord's significations as backup judge (classical KP)
        for check_house in range(1, 13):
            check_sigs = significators.get(check_house, {}).get("all_significators", [])
            if star_lord_name in check_sigs:
                star_lord_significates.append(check_house)

        star_support = len(set(star_lord_significates) & set(supporting_houses))
        star_deny = len(set(star_lord_significates) & set(denying_houses))
        star_total = star_support + star_deny

        if star_total > 0:
            star_lord_used = True
            raw_strength = star_support / star_total
            # Apply 70% dampening since star lord is less precise
            strength = 0.5 + (raw_strength - 0.5) * _STAR_LORD_DAMPENING
            if raw_strength > 0.6:
                judgment = "favorable"
            elif raw_strength < 0.4:
                judgment = "unfavorable"
            else:
                judgment = "mixed"
        else:
            # Neither sub-lord nor star lord have overlap — truly neutral
            strength = 0.5
            judgment = "mixed"
    else:
        strength = overlap_support / total_overlap
        if strength > 0.6:
            judgment = "favorable"
        elif strength < 0.4:
            judgment = "unfavorable"
        else:
            judgment = "mixed"

    # Phase 4: Retrograde & combustion modifiers for sub-lord
    modifiers = _get_planet_modifiers(sub_lord, planets)
    if modifiers["combustion_strength_loss"] > 0:
        # Combustion reduces confidence — shift strength toward 0.5
        penalty = modifiers["combustion_strength_loss"] / 100.0
        strength = strength + (0.5 - strength) * penalty

    # Phase 6: Rich explanation with house labels
    explanation = _build_rich_explanation(
        sub_lord=sub_lord,
        star_lord=star_lord_name,
        sub_lord_significates=sub_lord_significates,
        supporting_houses=supporting_houses,
        denying_houses=denying_houses,
        overlap_support=overlap_support,
        overlap_deny=overlap_deny,
        star_lord_used=star_lord_used,
        star_lord_significates=star_lord_significates if star_lord_used else None,
        modifier_notes=modifiers["notes"] if modifiers["notes"] else None,
    )

    return KPHouseAnalysis(
        house=house_number,
        cusp_longitude=cusp_lon,
        cusp_sign=kp_info["sign"],
        sign_lord=kp_info["sign_lord"],
        star_lord=kp_info["star_lord"],
        sub_lord=kp_info["sub_lord"],
        sub_lord_significates=sub_lord_significates,
        supporting_houses=supporting_houses,
        denying_houses=denying_houses,
        judgment=judgment,
        strength=round(strength, 2),
        explanation=explanation,
    )


def _compute_weighted_score(
    significators: dict[int, KPSignificators],
    houses: list[int],
) -> float:
    """Compute weighted significator score for a set of houses.

    Uses KP Reader 6 standard weights:
    - Level 1 (planets in stars of occupants) = 4
    - Level 2 (occupants) = 3
    - Level 3 (planets in stars of house lord) = 2
    - Level 4 (house lord) = 1

    Args:
        significators: Dict of house number to KPSignificators.
        houses: List of house numbers to score.

    Returns:
        Total weighted score.
    """
    score = 0.0
    counted: set[str] = set()
    for house in houses:
        sigs = significators.get(house)
        if not sigs:
            continue
        for level_key, weight in _SIG_WEIGHTS.items():
            for planet in sigs.get(level_key, []):
                # Count each planet only once per house group at its highest weight
                key = f"{planet}:{house}"
                if key not in counted:
                    counted.add(key)
                    score += weight
    return score


def get_kp_prediction(
    planets: dict[str, dict[str, Any]],
    cusps: list[float],
    query_type: str,
    ruling_planets: KPRulingPlanets | None = None,
) -> KPPredictionResult:
    """Full KP prediction for a life question.

    Args:
        planets: Dict of planet positions with longitude, sign, house, etc.
        cusps: List of 12 house cusp longitudes.
        query_type: Query type ('marriage', 'career', 'children', 'wealth', 'health',
                   'education', 'travel_short', 'travel_foreign', 'property', 'legal', 'spiritual').
        ruling_planets: Optional ruling planets at query time for confirmation.

    Returns:
        Complete KP prediction with judgment, confidence, and timing hints.

    Raises:
        ValueError: If query_type is invalid or cusps length is wrong.
    """
    if query_type not in KP_HOUSE_GROUPS:
        raise ValueError(f"Invalid query_type: {query_type}")
    if len(cusps) != 12:
        raise ValueError(f"Expected 12 cusps, got {len(cusps)}")

    groups = KP_HOUSE_GROUPS[query_type]
    primary_house = groups["primary"]
    supporting_houses = groups["support"]
    denying_houses = groups["deny"]

    # Analyze primary house
    house_analysis = analyze_kp_house(primary_house, planets, cusps, query_type)

    # Get significators
    significators = get_kp_significators(planets, cusps)

    # Collect unique supporting/denying significators for response
    supporting_significators: list[str] = []
    denying_significators: list[str] = []

    for house in supporting_houses:
        house_sigs = significators.get(house, {}).get("all_significators", [])
        for sig in house_sigs:
            if sig not in supporting_significators:
                supporting_significators.append(sig)

    for house in denying_houses:
        house_sigs = significators.get(house, {}).get("all_significators", [])
        for sig in house_sigs:
            if sig not in denying_significators:
                denying_significators.append(sig)

    # Phase 2: Weighted significator scoring (KP Reader 6)
    support_score = _compute_weighted_score(significators, supporting_houses)
    deny_score = _compute_weighted_score(significators, denying_houses)
    total_score = support_score + deny_score

    balance = 0.5 if total_score == 0 else support_score / total_score

    # Determine judgment and confidence with graduated ranges
    if house_analysis["judgment"] == "favorable":
        judgment = "favorable"
        # Range: 0.65 - 0.95
        confidence = 0.65 + (balance * 0.30)
    elif house_analysis["judgment"] == "unfavorable":
        judgment = "unfavorable"
        # Range: 0.65 - 0.95 (inverted)
        confidence = 0.65 + ((1 - balance) * 0.30)
    else:
        judgment = "mixed"
        # Range: 0.35 - 0.65 (spectrum instead of flat 0.50)
        confidence = 0.35 + (balance * 0.30)

    # Phase 3: Ruling planet confirmation
    rp_confirmed = False
    rp_match_count = 0
    if ruling_planets is not None:
        rp_list = ruling_planets.get("ruling_planets", [])
        rp_freq = ruling_planets.get("frequencies", {})
        for sig in supporting_significators:
            if sig in rp_list:
                rp_confirmed = True
                freq = rp_freq.get(sig, 1)
                rp_match_count += freq
                confidence += 0.03 * freq  # Boost per frequency
        if not rp_confirmed:
            confidence -= 0.05  # Slight reduction when no match

    # Phase 4: Combustion modifier on key significators
    modifier_notes: list[str] = []
    for sig_planet in supporting_significators[:3]:
        mods = _get_planet_modifiers(sig_planet, planets)
        if mods["combustion_strength_loss"] > 0:
            penalty = mods["combustion_strength_loss"] / 100.0
            confidence -= penalty
        modifier_notes.extend(mods["notes"])

    confidence = min(0.95, max(0.1, confidence))

    # Get timing hints (planets to watch)
    dasha_lords_to_watch = supporting_significators[:3] if supporting_significators else []
    transit_triggers = [
        f"{planet.title()} transit over {primary_house}th cusp" for planet in dasha_lords_to_watch
    ]

    # Build explanation — append modifier notes to house analysis explanation
    explanation = house_analysis["explanation"]
    if modifier_notes:
        explanation += " " + " ".join(modifier_notes)

    return KPPredictionResult(
        query_type=query_type,
        primary_house=primary_house,
        cusp_analysis=house_analysis,
        significator_analysis={
            "supporting_significators": supporting_significators,
            "denying_significators": denying_significators,
            "balance": round(balance, 2),
            "support_score": round(support_score, 1),
            "deny_score": round(deny_score, 1),
        },
        ruling_planet_confirmation=rp_confirmed,
        judgment=judgment,
        confidence=round(confidence, 2),
        timing_hints={
            "dasha_lords_to_watch": dasha_lords_to_watch,
            "transit_triggers": transit_triggers,
        },
        explanation=explanation,
    )


def get_kp_sublord_table() -> list[KPSublordEntry]:
    """Generate the complete KP sub-lord table for all 360°.

    Returns a list of entries, each representing one sub-division:
    27 nakshatras x 9 sub-lords = ~243 entries (actual count may vary due to rounding).

    Returns:
        List of sub-lord table entries covering the entire zodiac.
    """
    return _build_sublord_table()


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "KP_HOUSE_GROUPS",
    "SIGN_RULERS",
    "VIMSHOTTARI_SEQUENCE",
    "VIMSHOTTARI_YEARS",
    "KPHouseAnalysis",
    "KPPredictionResult",
    "KPRulingPlanets",
    "KPSignificators",
    "KPSublordEntry",
    "KPSublordInfo",
    "analyze_kp_house",
    "get_cuspal_sublords",
    "get_kp_prediction",
    "get_kp_significators",
    "get_kp_sublord",
    "get_kp_sublord_table",
    "get_ruling_planets",
]
