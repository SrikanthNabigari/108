"""Nakshatra (lunar mansion) calculations for Vedic astrology.

This module provides calculations for nakshatras, which are 27 lunar mansions
used in Vedic astrology. Each nakshatra spans 13°20' (13.333°) and is divided
into 4 padas (quarters) of 3°20' (3.333°) each.

The module supports:
- Finding nakshatra from longitude (0-360°)
- Retrieving nakshatra lords (Vimshottari sequence)
- Calculating pada Navamsha (divisional chart position)
- Computing Tarabala (star transit strength)

All planetary lords follow the Vimshottari Dasha sequence.
"""

import json
from pathlib import Path
from typing import Dict, Optional, TypedDict, Literal
from dataclasses import dataclass, asdict


# Type definitions
class NakshatraResult(TypedDict):
    """Result from longitude_to_nakshatra function."""
    name: str
    number: int
    pada: int
    lord: str
    degree_in_nakshatra: float


class PadaNavamshaResult(TypedDict):
    """Result from get_pada_navamsha function."""
    rashi: str
    rashi_number: int


class TarabalaResult(TypedDict):
    """Result from get_tarabala function."""
    tara: str
    tara_number: int
    effect: str


@dataclass
class NakshatraData:
    """Internal data structure for a single nakshatra."""
    number: int
    id: str
    name: str
    ruler: str
    padas: Dict[int, Dict[str, any]]


# Vimshottari Dasha sequence - planetary lords of nakshatras
NAKSHATRA_LORDS = {
    1: "ketu",
    2: "venus",
    3: "sun",
    4: "moon",
    5: "mars",
    6: "rahu",
    7: "jupiter",
    8: "saturn",
    9: "mercury",
    10: "ketu",
    11: "venus",
    12: "sun",
    13: "moon",
    14: "mars",
    15: "rahu",
    16: "jupiter",
    17: "saturn",
    18: "mercury",
    19: "ketu",
    20: "venus",
    21: "sun",
    22: "moon",
    23: "mars",
    24: "rahu",
    25: "jupiter",
    26: "saturn",
    27: "mercury",
}

# Tarabala (9-fold star) strength classification
TARABALA_NAMES = [
    "",  # 0 is unused (tara starts at 1)
    "Janma",
    "Sampat",
    "Vipat",
    "Kshema",
    "Pratyak",
    "Sadhana",
    "Naidhana",
    "Mitra",
    "Parama Mitra",
]

TARABALA_EFFECTS = [
    "",  # 0 is unused
    "Moderate",      # Janma (Birth)
    "Good",          # Sampat (Wealth)
    "Bad",           # Vipat (Danger)
    "Good",          # Kshema (Prosperity)
    "Bad",           # Pratyak (Obstacles)
    "Good",          # Sadhana (Achievement)
    "Bad",           # Naidhana (Death)
    "Good",          # Mitra (Friend)
    "Excellent",     # Parama Mitra (Best Friend)
]

# Global cache for nakshatra data
_NAKSHATRA_DATA_CACHE: Optional[Dict[str, any]] = None
_NAKSHATRA_BY_NUMBER: Optional[Dict[int, Dict[str, any]]] = None


def _load_nakshatra_data() -> Dict[str, any]:
    """Load nakshatra definitions from JSON file.

    Returns:
        Dictionary containing all nakshatra data from the JSON file.

    Raises:
        FileNotFoundError: If the nakshatras.json file cannot be found.
        json.JSONDecodeError: If the JSON file is malformed.
    """
    global _NAKSHATRA_DATA_CACHE, _NAKSHATRA_BY_NUMBER

    if _NAKSHATRA_DATA_CACHE is not None:
        return _NAKSHATRA_DATA_CACHE

    # Find the JSON file relative to this module
    module_path = Path(__file__).parent
    json_path = module_path.parent.parent.parent / "knowledge" / "definitions" / "nakshatras.json"

    if not json_path.exists():
        raise FileNotFoundError(
            f"Nakshatras data file not found at {json_path}. "
            "Ensure knowledge/definitions/nakshatras.json exists."
        )

    with open(json_path, 'r', encoding='utf-8') as f:
        _NAKSHATRA_DATA_CACHE = json.load(f)

    # Build index by number for fast lookup
    _NAKSHATRA_BY_NUMBER = {}
    for nak in _NAKSHATRA_DATA_CACHE["nakshatras"]:
        _NAKSHATRA_BY_NUMBER[nak["number"]] = nak

    return _NAKSHATRA_DATA_CACHE


def _get_nakshatra_by_number(number: int) -> Optional[Dict[str, any]]:
    """Get nakshatra data by number (1-27).

    Args:
        number: Nakshatra number (1-27).

    Returns:
        Nakshatra data dictionary or None if not found.
    """
    if _NAKSHATRA_BY_NUMBER is None:
        _load_nakshatra_data()

    return _NAKSHATRA_BY_NUMBER.get(number)


def longitude_to_nakshatra(lon: float) -> NakshatraResult:
    """Convert ecliptic longitude to nakshatra information.

    Given a longitude in the ecliptic (0-360°), returns the nakshatra
    it falls in, along with the pada (quarter), planet lord, and
    remaining degrees within the nakshatra.

    Args:
        lon: Ecliptic longitude in degrees (0-360).

    Returns:
        Dictionary containing:
            - name: Nakshatra name (e.g., "Ashwini")
            - number: Nakshatra number (1-27)
            - pada: Pada number (1-4)
            - lord: Planetary lord (e.g., "ketu", "venus")
            - degree_in_nakshatra: Degrees within the nakshatra (0-13.333)

    Raises:
        ValueError: If longitude is outside 0-360 range.
    """
    if not 0 <= lon <= 360:
        raise ValueError(f"Longitude must be between 0-360, got {lon}")

    # Normalize to 0-360 if exactly 360
    if lon == 360:
        lon = 0

    # Load data first to access accurate boundaries
    data = _load_nakshatra_data()

    # Find nakshatra by checking data boundaries
    # This is more reliable than calculating, due to floating point precision
    nakshatra_number = None
    for nak in data["nakshatras"]:
        nak_start = nak["degrees"]["start"]
        nak_end = nak["degrees"]["end"]
        # Use < for upper bound so exact boundary goes to next nakshatra
        if nak_start <= lon < nak_end:
            nakshatra_number = nak["number"]
            break

    # Edge case: exactly at the end (360° = 0° of next cycle)
    if nakshatra_number is None:
        nakshatra_number = 27

    # Get nakshatra data (already loaded above)
    nak_data = _get_nakshatra_by_number(nakshatra_number)

    if not nak_data:
        raise ValueError(f"Invalid nakshatra number: {nakshatra_number}")

    # Calculate position within nakshatra
    nak_start = nak_data["degrees"]["start"]
    degree_in_nakshatra = lon - nak_start

    # Find pada by checking against exact data boundaries
    pada = 1
    for p in nak_data["padas"]:
        p_start = p["degrees"]["start"]
        p_end = p["degrees"]["end"]
        # Use <= for start and < for end to handle boundaries correctly
        # At exact boundary, include in the higher pada
        if p_start <= lon < p_end:
            pada = p["number"]
            break
    else:
        # If not found in loop (e.g., exactly at end), use last pada
        pada = 4

    # Clamp degree_in_nakshatra to valid range
    degree_in_nakshatra = max(0, min(13.333, degree_in_nakshatra))

    return NakshatraResult(
        name=nak_data["name"],
        number=nakshatra_number,
        pada=pada,
        lord=nak_data["ruler"],
        degree_in_nakshatra=round(degree_in_nakshatra, 6),
    )


def get_nakshatra_lord(nakshatra: str) -> str:
    """Get the planetary lord of a nakshatra.

    Returns the Vimshottari Dasha lord for a given nakshatra name.

    Args:
        nakshatra: Nakshatra name (e.g., "Ashwini", "Bharani").

    Returns:
        Planet ID of the lord (e.g., "ketu", "venus", "sun").

    Raises:
        ValueError: If nakshatra name is not found.
    """
    data = _load_nakshatra_data()

    # Find nakshatra by name (case-insensitive)
    for nak in data["nakshatras"]:
        if nak["name"].lower() == nakshatra.lower():
            return nak["ruler"]

    raise ValueError(
        f"Nakshatra '{nakshatra}' not found. "
        f"Valid nakshatras: {', '.join(n['name'] for n in data['nakshatras'])}"
    )


def get_pada_navamsha(nakshatra: str, pada: int) -> PadaNavamshaResult:
    """Get the Navamsha rashi for a nakshatra pada.

    The Navamsha (D-9 divisional chart) divides each sign into 9 parts,
    but in relation to nakshatras, each pada (quarter of a nakshatra)
    is assigned a rashi based on its position in the zodiac.

    Args:
        nakshatra: Nakshatra name (e.g., "Ashwini", "Bharani").
        pada: Pada number (1-4).

    Returns:
        Dictionary containing:
            - rashi: Rashi name (e.g., "aries", "taurus")
            - rashi_number: Rashi number (0-11, where Aries=0)

    Raises:
        ValueError: If nakshatra not found or pada not in 1-4.
    """
    if not 1 <= pada <= 4:
        raise ValueError(f"Pada must be between 1-4, got {pada}")

    data = _load_nakshatra_data()

    # Find nakshatra by name
    nak_data = None
    for nak in data["nakshatras"]:
        if nak["name"].lower() == nakshatra.lower():
            nak_data = nak
            break

    if not nak_data:
        raise ValueError(
            f"Nakshatra '{nakshatra}' not found. "
            f"Valid nakshatras: {', '.join(n['name'] for n in data['nakshatras'])}"
        )

    # Find pada data
    pada_data = None
    for p in nak_data["padas"]:
        if p["number"] == pada:
            pada_data = p
            break

    if not pada_data:
        raise ValueError(f"Pada {pada} not found in nakshatra {nakshatra}")

    # Map rashi names to numbers
    rashi_name = pada_data["navamsha_sign"].lower()
    rashi_map = {
        "aries": 0, "taurus": 1, "gemini": 2, "cancer": 3,
        "leo": 4, "virgo": 5, "libra": 6, "scorpio": 7,
        "sagittarius": 8, "capricorn": 9, "aquarius": 10, "pisces": 11,
    }

    rashi_number = rashi_map.get(rashi_name, -1)
    if rashi_number == -1:
        raise ValueError(f"Invalid rashi: {rashi_name}")

    return PadaNavamshaResult(
        rashi=rashi_name,
        rashi_number=rashi_number,
    )


def get_tarabala(birth_nakshatra: str, transit_nakshatra: str) -> TarabalaResult:
    """Calculate Tarabala (9-fold star strength) for transit analysis.

    Tarabala measures the strength of a transiting planet based on which
    nakshatra it's in relative to the birth nakshatra. The count from birth
    nakshatra to transit nakshatra (1-27) is divided by 9 to get the Tara.

    Formula: ((transit_nak_number - birth_nak_number) % 27) / 9 + 1

    Args:
        birth_nakshatra: Birth nakshatra name (e.g., "Ashwini").
        transit_nakshatra: Current transit nakshatra name.

    Returns:
        Dictionary containing:
            - tara: Tara name (e.g., "Janma", "Sampat")
            - tara_number: Tara number (1-9)
            - effect: Effect classification ("Bad", "Good", "Excellent")

    Raises:
        ValueError: If either nakshatra name is not found.
    """
    data = _load_nakshatra_data()

    # Find nakshatra numbers
    birth_number = None
    transit_number = None

    for nak in data["nakshatras"]:
        if nak["name"].lower() == birth_nakshatra.lower():
            birth_number = nak["number"]
        if nak["name"].lower() == transit_nakshatra.lower():
            transit_number = nak["number"]

    if birth_number is None:
        raise ValueError(
            f"Birth nakshatra '{birth_nakshatra}' not found. "
            f"Valid nakshatras: {', '.join(n['name'] for n in data['nakshatras'])}"
        )

    if transit_number is None:
        raise ValueError(
            f"Transit nakshatra '{transit_nakshatra}' not found. "
            f"Valid nakshatras: {', '.join(n['name'] for n in data['nakshatras'])}"
        )

    # Calculate Tara: count from birth to transit, modulo 27
    # If same nakshatra, count is 0, which maps to Janma (tara 1)
    count = (transit_number - birth_number) % 27

    # Map count to tara number (1-9)
    # count 0 = Janma (1), count 1-2 = Sampat (2), count 3-5 = Vipat (3), etc.
    tara_number = (count // 3) + 1

    # Handle edge case where count is 26 (previous nakshatra)
    if tara_number > 9:
        tara_number = 9

    # Ensure tara_number is in valid range 1-9
    tara_number = max(1, min(9, tara_number))

    return TarabalaResult(
        tara=TARABALA_NAMES[tara_number],
        tara_number=tara_number,
        effect=TARABALA_EFFECTS[tara_number],
    )


def get_nakshatra_name_by_number(number: int) -> str:
    """Get nakshatra name by its number.

    Args:
        number: Nakshatra number (1-27).

    Returns:
        Nakshatra name (e.g., "Ashwini").

    Raises:
        ValueError: If number is not in valid range 1-27.
    """
    if not 1 <= number <= 27:
        raise ValueError(f"Nakshatra number must be 1-27, got {number}")

    data = _get_nakshatra_by_number(number)
    if not data:
        raise ValueError(f"Nakshatra number {number} not found")

    return data["name"]


def get_nakshatra_number_by_name(name: str) -> int:
    """Get nakshatra number by its name.

    Args:
        name: Nakshatra name (e.g., "Ashwini", case-insensitive).

    Returns:
        Nakshatra number (1-27).

    Raises:
        ValueError: If name is not found.
    """
    data = _load_nakshatra_data()

    for nak in data["nakshatras"]:
        if nak["name"].lower() == name.lower():
            return nak["number"]

    raise ValueError(
        f"Nakshatra '{name}' not found. "
        f"Valid nakshatras: {', '.join(n['name'] for n in data['nakshatras'])}"
    )


def get_all_nakshatras() -> list[Dict[str, any]]:
    """Get list of all 27 nakshatras with their data.

    Returns:
        List of nakshatra dictionaries, each containing:
            - number: 1-27
            - name: Nakshatra name
            - id: Lowercase identifier
            - ruler: Planetary lord
            - padas: List of pada data with navamsha signs
    """
    data = _load_nakshatra_data()
    return data["nakshatras"]


def validate_nakshatra_name(name: str) -> bool:
    """Check if a nakshatra name is valid.

    Args:
        name: Nakshatra name to validate.

    Returns:
        True if valid, False otherwise.
    """
    try:
        get_nakshatra_number_by_name(name)
        return True
    except ValueError:
        return False
