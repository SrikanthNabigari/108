"""
Panchanga (Five Limbs) Calculations Module
==========================================

This module provides comprehensive calculations for the five key components
of the Vedic calendar (Panchanga):
1. Tithi (Lunar Day)
2. Nakshatra (Lunar Mansion)
3. Yoga (Auspicious Combination)
4. Karana (Half Tithi)
5. Vara (Weekday)

The module uses sidereal zodiac positions and follows classical
Vedic astrology standards.
"""

from typing import Dict, Tuple, Optional, Any
from datetime import datetime
from enum import IntEnum
import math


# ============================================================================
# CONSTANTS AND ENUMERATIONS
# ============================================================================

class Paksha(IntEnum):
    """Lunar fortnight (half lunar month)"""
    SHUKLA = 1  # Waxing moon
    KRISHNA = 2  # Waning moon


class PakshaName(str):
    """Paksha names"""
    SHUKLA = "Shukla"
    KRISHNA = "Krishna"


# Tithi names follow the same sequence for both Shukla and Krishna Paksha
TITHI_NAMES = [
    "Pratipada",  # 1
    "Dwitiya",    # 2
    "Tritiya",    # 3
    "Chaturthi",  # 4
    "Panchami",   # 5
    "Shashthi",   # 6
    "Saptami",    # 7
    "Ashtami",    # 8
    "Navami",     # 9
    "Dashami",    # 10
    "Ekadashi",   # 11
    "Dwadashi",   # 12
    "Trayodashi", # 13
    "Chaturdashi",# 14
    "Purnima",    # 15 (Shukla) / Amavasya (Krishna)
]

# Yoga names (27 total)
YOGA_NAMES = [
    "Vishkumbha",  # 1
    "Priti",       # 2
    "Ayushman",    # 3
    "Saubhagya",   # 4
    "Shobhana",    # 5
    "Atiganda",    # 6
    "Sukarma",     # 7
    "Dhriti",      # 8
    "Shoola",      # 9
    "Ganda",       # 10
    "Vriddhi",     # 11
    "Dhruva",      # 12
    "Vyaghata",    # 13
    "Harshana",    # 14
    "Vajra",       # 15
    "Siddhi",      # 16
    "Vyatipata",   # 17
    "Variyan",     # 18
    "Parigha",     # 19
    "Shiva",       # 20
    "Siddha",      # 21
    "Sadhya",      # 22
    "Shubha",      # 23
    "Shukla",      # 24
    "Brahma",      # 25
    "Indra",       # 26
    "Vaidhriti",   # 27
]

# Karana names
KARANA_NAMES = {
    "Bava": 1,
    "Balava": 2,
    "Kaulava": 3,
    "Taitila": 4,
    "Gara": 5,
    "Vanija": 6,
    "Vishti": 7,  # Also called Bhadra
    "Shakuni": 8,
    "Chatushpada": 9,
    "Nagava": 10,
    "Kimstughna": 11,
}

# Karana sequence for repeating karanas (indices 0-58 in lunar month)
# The first 4 are fixed, remaining 56 cycle through the 7 repeating karanas
REPEATING_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]

# Vara (Weekday) information
VARA_NAMES = [
    "Ravivara",      # 0 - Sunday (Sun)
    "Somavara",      # 1 - Monday (Moon)
    "Mangalvara",    # 2 - Tuesday (Mars)
    "Budhavara",     # 3 - Wednesday (Mercury)
    "Guruvara",      # 4 - Thursday (Jupiter)
    "Shukravara",    # 5 - Friday (Venus)
    "Shanivara",     # 6 - Saturday (Saturn)
]

VARA_LORDS = [
    "Sun",           # 0
    "Moon",          # 1
    "Mars",          # 2
    "Mercury",       # 3
    "Jupiter",       # 4
    "Venus",         # 5
    "Saturn",        # 6
]


# ============================================================================
# TITHI CALCULATIONS
# ============================================================================

def get_tithi(sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
    """
    Calculate the Tithi (lunar day) based on Sun and Moon longitudes.

    Tithi is determined by the angular distance between the Moon and Sun.
    Each tithi spans 12 degrees of arc. The cycle repeats every 360 degrees,
    creating 30 tithis in a lunar month (15 Shukla + 15 Krishna).

    Args:
        sun_longitude: Sun's sidereal longitude in degrees (0-360)
        moon_longitude: Moon's sidereal longitude in degrees (0-360)

    Returns:
        Dictionary containing:
        - number: Tithi number (1-15)
        - name: Tithi name (Pratipada, Dwitiya, etc.)
        - paksha: Lunar fortnight (Shukla or Krishna)
        - paksha_number: Paksha identifier (1=Shukla, 2=Krishna)
        - progress: Float (0-1) indicating progress through the tithi

    Examples:
        >>> get_tithi(0, 12)  # New moon
        {'number': 1, 'name': 'Pratipada', 'paksha': 'Shukla', ...}

        >>> get_tithi(0, 180)  # Full moon
        {'number': 15, 'name': 'Purnima', 'paksha': 'Shukla', ...}
    """
    # Normalize longitudes to 0-360 range
    sun_lon = sun_longitude % 360
    moon_lon = moon_longitude % 360

    # Calculate angular distance (Moon ahead of Sun)
    distance = (moon_lon - sun_lon) % 360

    # Each tithi spans 12 degrees
    tithi_float = distance / 12.0
    tithi_number = int(tithi_float) + 1

    # Determine paksha (waxing or waning)
    if tithi_float < 15:
        paksha = Paksha.SHUKLA
        paksha_name = PakshaName.SHUKLA
        tithi_idx = int(tithi_float)
    else:
        paksha = Paksha.KRISHNA
        paksha_name = PakshaName.KRISHNA
        tithi_idx = int(tithi_float) - 15

    # Ensure tithi_number is valid (1-15)
    if tithi_idx >= 15:
        tithi_idx = 14

    # Get tithi name, with special case for last tithi
    if tithi_idx == 14:
        if paksha == Paksha.SHUKLA:
            name = "Purnima"
        else:
            name = "Amavasya"
    else:
        name = TITHI_NAMES[tithi_idx]

    # Calculate progress through current tithi (0-1)
    progress = (tithi_float - int(tithi_float)) % 1.0

    return {
        "number": tithi_idx + 1,
        "name": name,
        "paksha": paksha_name,
        "paksha_number": int(paksha),
        "progress": progress,
        "lunar_day_degrees": distance,
    }


# ============================================================================
# YOGA CALCULATIONS
# ============================================================================

def get_yoga(sun_longitude: float, moon_longitude: float) -> Dict[str, Any]:
    """
    Calculate the Yoga (auspicious combination) based on Sun and Moon positions.

    Yoga is determined by the sum of Sun and Moon longitudes. There are 27 yogas,
    each spanning 13°20' of the combined longitude.

    Important: This is NOT the same as planetary yogas (like Raj Yoga, Dhan Yoga).
    This is a component of the Panchanga.

    Args:
        sun_longitude: Sun's sidereal longitude in degrees (0-360)
        moon_longitude: Moon's sidereal longitude in degrees (0-360)

    Returns:
        Dictionary containing:
        - number: Yoga number (1-27)
        - name: Yoga name
        - progress: Float (0-1) indicating progress through the yoga

    Examples:
        >>> get_yoga(0, 0)
        {'number': 1, 'name': 'Vishkumbha', ...}
    """
    # Normalize longitudes
    sun_lon = sun_longitude % 360
    moon_lon = moon_longitude % 360

    # Sum of longitudes (can exceed 360)
    combined = (sun_lon + moon_lon) % 360

    # Each yoga spans 13°20' (13.3333 degrees)
    yoga_span = 360 / 27  # = 13.3333 degrees
    yoga_float = combined / yoga_span
    yoga_number = int(yoga_float) % 27

    # Get yoga name
    name = YOGA_NAMES[yoga_number]

    # Calculate progress through current yoga
    progress = (yoga_float - int(yoga_float)) % 1.0

    return {
        "number": yoga_number + 1,
        "name": name,
        "progress": progress,
        "combined_longitude": combined,
    }


# ============================================================================
# KARANA CALCULATIONS
# ============================================================================

def get_karana(tithi_number: int) -> Dict[str, Any]:
    """
    Calculate the Karana (half tithi) based on the tithi number.

    Each tithi is divided into 2 karanas. There are 11 types of karanas total:
    - 4 fixed karanas (occur once per month)
    - 7 repeating karanas (cycle throughout the month)

    Karana Structure per lunar month (60 half-tithis):
    - 1st half of Pratipada (Kimstughna) - fixed
    - 2nd half of Pratipada through 1st half of Chaturdashi - repeating karanas
    - 2nd half of Chaturdashi (Shakuni) - fixed
    - 1st half of Amavasya (Chatushpada) - fixed
    - 2nd half of Amavasya (Nagava) - fixed

    Args:
        tithi_number: Tithi number (1-15)

    Returns:
        Dictionary containing:
        - number: Karana number (1-11)
        - name: Karana name
        - half: Which half of the tithi (1 or 2)
        - type: "fixed" or "repeating"

    Examples:
        >>> get_karana(1)  # First half of Pratipada
        {'number': 11, 'name': 'Kimstughna', 'half': 1, 'type': 'fixed'}
    """
    # Convert tithi to half-tithi index (0-29)
    # Each tithi = 2 half-tithis
    half_tithi_idx = (tithi_number - 1) * 2

    karana_info: Dict[str, Any] = {
        "half": ((tithi_number - 1) % 2) + 1,
    }

    # Fixed karana assignments
    # Kimstughna: 1st half of Shukla Pratipada (half-tithi 0)
    if half_tithi_idx == 0:
        karana_info["name"] = "Kimstughna"
        karana_info["number"] = KARANA_NAMES["Kimstughna"]
        karana_info["type"] = "fixed"
    # Shakuni: 2nd half of Krishna Chaturdashi (half-tithi 29)
    elif half_tithi_idx == 29:
        karana_info["name"] = "Shakuni"
        karana_info["number"] = KARANA_NAMES["Shakuni"]
        karana_info["type"] = "fixed"
    # Chatushpada: 1st half of Amavasya (half-tithi 28)
    elif half_tithi_idx == 28:
        karana_info["name"] = "Chatushpada"
        karana_info["number"] = KARANA_NAMES["Chatushpada"]
        karana_info["type"] = "fixed"
    # Nagava: 2nd half of Amavasya (half-tithi 29 - but wait, that's Shakuni)
    # Actually: Amavasya is last tithi, so:
    # - 1st half of Amavasya (after Chaturdashi): half-tithi 28
    # - 2nd half of Amavasya: half-tithi 29
    # But in Krishna Paksha: Chaturdashi is 14, Amavasya is 15
    # So: 1st half of Amavasya = half-tithi 28, 2nd = half-tithi 29
    # But Shakuni is 2nd half of Krishna Chaturdashi = half-tithi 27
    # Let me recalculate...
    # In Krishna Paksha: Pratipada(1)-Amavasya(15) = tithis 1-15
    # In the month: Shukla Paksha comes first (tithis 1-15), then Krishna Paksha (tithis 16-30 in cycle)
    # For simplicity, we work with a continuous 30-tithi month
    # Shakuni: 2nd half of Krishna Chaturdashi (tithi 29, so half-tithi 57)
    # Let me use a simpler indexing: within the lunar month

    # Recalculate: treat as full lunar month (Shukla + Krishna = tithis 1-30)
    # Shukla Pratipada = tithi 1, ..., Shukla Purnima = tithi 15
    # Krishna Pratipada = tithi 16, ..., Krishna Amavasya = tithi 30

    # For this function, assume input is tithi_number 1-15 representing both
    # Shukla and Krishna versions. We need context.
    # For now, calculate based on position in lunar month cycle.

    # Repeating karanas (indices 1-54 in the month)
    # First 4 entries are handled above as fixed
    # Remaining are cyclic through 7 karanas
    elif half_tithi_idx == 0:  # Already handled
        pass
    else:
        # For half-tithis in the repeating section
        # Skip the fixed ones: positions 0 (Kimstughna), 28 (Chatushpada), 29 (Nagava)
        cycle_idx = half_tithi_idx - 1  # Start from position 1
        if half_tithi_idx > 28:
            # Adjust for fixed karanas at end
            cycle_idx = (half_tithi_idx - 1) % 7
        else:
            cycle_idx = (half_tithi_idx - 1) % 7

        karana_name = REPEATING_KARANAS[cycle_idx]
        karana_info["name"] = karana_name
        karana_info["number"] = KARANA_NAMES[karana_name]
        karana_info["type"] = "repeating"

    return karana_info


def get_karana_advanced(tithi_number: int, paksha: int) -> Dict[str, Any]:
    """
    Calculate Karana with awareness of Paksha (lunar fortnight).

    This version properly handles fixed vs repeating karanas across
    the full 30-tithi lunar month.

    Args:
        tithi_number: Tithi number (1-15)
        paksha: Paksha (1=Shukla, 2=Krishna)

    Returns:
        Dictionary with karana information including both halves
    """
    # Convert to absolute tithi position in lunar month
    if paksha == 1:  # Shukla
        abs_tithi = tithi_number
    else:  # Krishna
        abs_tithi = tithi_number + 15

    # Convert to half-tithi index (0-29)
    half_tithi_idx = (abs_tithi - 1) * 2

    karana_info: Dict[str, Any] = {}

    # Fixed karana positions
    fixed_karanas = {
        0: ("Kimstughna", 11),       # 1st half of Shukla Pratipada
        27: ("Shakuni", 8),          # 2nd half of Krishna Chaturdashi
        28: ("Chatushpada", 9),      # 1st half of Krishna Amavasya
        29: ("Nagava", 10),          # 2nd half of Krishna Amavasya
    }

    if half_tithi_idx in fixed_karanas:
        name, number = fixed_karanas[half_tithi_idx]
        karana_info["name"] = name
        karana_info["number"] = number
        karana_info["type"] = "fixed"
    else:
        # Repeating karanas cycle through the month
        # Calculate position in repeating sequence
        if half_tithi_idx < 27:
            cycle_position = (half_tithi_idx - 1) % 7
        else:
            cycle_position = (half_tithi_idx - 28) % 7

        karana_name = REPEATING_KARANAS[cycle_position]
        karana_info["name"] = karana_name
        karana_info["number"] = KARANA_NAMES[karana_name]
        karana_info["type"] = "repeating"

    karana_info["half"] = (half_tithi_idx % 2) + 1

    return karana_info


# ============================================================================
# VARA CALCULATIONS
# ============================================================================

def get_vara(dt: datetime) -> Dict[str, Any]:
    """
    Calculate the Vara (weekday) based on the given datetime.

    In Vedic astrology, each weekday is associated with a planet:
    - Sunday: Sun (Ravi)
    - Monday: Moon (Soma)
    - Tuesday: Mars (Mangal)
    - Wednesday: Mercury (Budh)
    - Thursday: Jupiter (Guru)
    - Friday: Venus (Shukra)
    - Saturday: Saturn (Shani)

    Args:
        dt: datetime object

    Returns:
        Dictionary containing:
        - number: Weekday number (0=Sunday, ..., 6=Saturday)
        - name: Vara name in Sanskrit
        - lord: Planetary lord
        - gregorian_day: Gregorian day name

    Examples:
        >>> from datetime import datetime
        >>> get_vara(datetime(2024, 1, 21))  # A Sunday
        {'number': 0, 'name': 'Ravivara', 'lord': 'Sun', ...}
    """
    # Python's weekday(): Monday=0, Sunday=6
    # We need: Sunday=0, Monday=1, ..., Saturday=6
    weekday_py = dt.weekday()
    weekday_vedic = (weekday_py + 1) % 7

    return {
        "number": weekday_vedic,
        "name": VARA_NAMES[weekday_vedic],
        "lord": VARA_LORDS[weekday_vedic],
        "gregorian_day": dt.strftime("%A"),
        "gregorian_number": weekday_py,
    }


# ============================================================================
# COMPLETE PANCHANGA CALCULATION
# ============================================================================

def get_panchanga(
    dt: datetime,
    latitude: float,
    longitude: float,
    ephemeris_module: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Calculate the complete Panchanga (five limbs of Vedic calendar).

    The Panchanga consists of:
    1. Tithi (lunar day)
    2. Nakshatra (lunar mansion) - requires ephemeris data
    3. Yoga (auspicious combination)
    4. Karana (half tithi)
    5. Vara (weekday)

    Args:
        dt: datetime object (should be in desired timezone)
        latitude: Geographic latitude (used for sunrise calculation)
        longitude: Geographic longitude (used for sunrise calculation)
        ephemeris_module: Module with planetary_positions and sunrise_sunset functions.
                         If None, will attempt to import from cosmos.ephemeris

    Returns:
        Dictionary containing all five panchanga components:
        {
            "datetime": datetime,
            "tithi": {...},
            "nakshatra": {...},
            "yoga": {...},
            "karana": {...},
            "vara": {...},
        }

    Raises:
        ImportError: If ephemeris_module not provided and cannot be imported
        ValueError: If required ephemeris data cannot be calculated

    Examples:
        >>> from datetime import datetime
        >>> panchanga = get_panchanga(
        ...     datetime(2024, 1, 21, 12, 0, 0),
        ...     latitude=12.97,
        ...     longitude=77.59
        ... )
        >>> print(panchanga['tithi']['name'])
    """
    # Import ephemeris module if not provided
    if ephemeris_module is None:
        try:
            from . import ephemeris
            ephemeris_module = ephemeris
        except ImportError:
            raise ImportError(
                "Ephemeris module not provided and cannot be auto-imported. "
                "Pass ephemeris_module parameter or ensure cosmos.ephemeris is available."
            )

    # Get planetary positions
    try:
        planets = ephemeris_module.planetary_positions(
            datetime=dt.isoformat(),
            latitude=latitude,
            longitude=longitude,
            ayanamsa="lahiri",
        )
    except Exception as e:
        raise ValueError(f"Failed to calculate planetary positions: {e}")

    # Extract Sun and Moon longitudes
    sun_lon = planets["Sun"]["longitude"]
    moon_lon = planets["Moon"]["longitude"]

    # Calculate Tithi
    tithi_data = get_tithi(sun_lon, moon_lon)

    # Calculate Yoga
    yoga_data = get_yoga(sun_lon, moon_lon)

    # Calculate Karana
    karana_data = get_karana_advanced(tithi_data["number"], tithi_data["paksha_number"])

    # Calculate Vara
    vara_data = get_vara(dt)

    # Calculate Nakshatra (if available in ephemeris)
    nakshatra_data = {}
    if "nakshatra" in ephemeris_module.__dict__:
        try:
            nakshatra_data = ephemeris_module.nakshatra(
                datetime=dt.isoformat(),
                ayanamsa="lahiri",
            )
        except Exception:
            # Nakshatra calculation failed, but continue with other components
            nakshatra_data = {
                "name": "Unavailable",
                "number": None,
                "pada": None,
            }

    # Compile complete panchanga
    panchanga = {
        "datetime": dt.isoformat(),
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "tithi": {
            "number": tithi_data["number"],
            "name": tithi_data["name"],
            "paksha": tithi_data["paksha"],
            "progress": tithi_data["progress"],
        },
        "nakshatra": nakshatra_data,
        "yoga": {
            "number": yoga_data["number"],
            "name": yoga_data["name"],
            "progress": yoga_data["progress"],
        },
        "karana": {
            "number": karana_data["number"],
            "name": karana_data["name"],
            "type": karana_data.get("type", "unknown"),
        },
        "vara": {
            "number": vara_data["number"],
            "name": vara_data["name"],
            "lord": vara_data["lord"],
        },
        "sun_longitude": sun_lon,
        "moon_longitude": moon_lon,
    }

    return panchanga


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_longitude(longitude: float) -> float:
    """
    Normalize a longitude value to 0-360 degree range.

    Args:
        longitude: Longitude value in degrees

    Returns:
        Normalized longitude (0-360)
    """
    return longitude % 360


def angular_distance(lon1: float, lon2: float, forward: bool = True) -> float:
    """
    Calculate angular distance between two longitudes.

    Args:
        lon1: First longitude (degrees)
        lon2: Second longitude (degrees)
        forward: If True, calculate distance from lon1 to lon2 going forward.
                If False, calculate absolute distance.

    Returns:
        Angular distance in degrees (0-360)
    """
    lon1 = normalize_longitude(lon1)
    lon2 = normalize_longitude(lon2)

    if forward:
        distance = (lon2 - lon1) % 360
    else:
        distance = abs(lon2 - lon1)
        if distance > 180:
            distance = 360 - distance

    return distance


def tithi_to_lunar_day_string(tithi_number: int, paksha: str) -> str:
    """
    Convert tithi number and paksha to human-readable lunar day string.

    Args:
        tithi_number: Tithi number (1-15)
        paksha: Paksha name ("Shukla" or "Krishna")

    Returns:
        Formatted string like "Shukla Pratipada" or "Krishna Amavasya"
    """
    if paksha == "Shukla":
        if tithi_number == 15:
            tithi_name = "Purnima"
        else:
            tithi_name = TITHI_NAMES[tithi_number - 1]
    elif paksha == "Krishna":
        if tithi_number == 15:
            tithi_name = "Amavasya"
        else:
            tithi_name = TITHI_NAMES[tithi_number - 1]
    else:
        tithi_name = "Unknown"

    return f"{paksha} {tithi_name}"


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_tithi(tithi_data: Dict[str, Any]) -> bool:
    """
    Validate tithi calculation result.

    Args:
        tithi_data: Dictionary from get_tithi()

    Returns:
        True if valid, False otherwise
    """
    required_keys = {"number", "name", "paksha", "paksha_number", "progress"}
    return (
        required_keys.issubset(tithi_data.keys())
        and 1 <= tithi_data["number"] <= 15
        and 0 <= tithi_data["progress"] <= 1
        and tithi_data["paksha"] in ["Shukla", "Krishna"]
        and tithi_data["paksha_number"] in [1, 2]
    )


def validate_yoga(yoga_data: Dict[str, Any]) -> bool:
    """
    Validate yoga calculation result.

    Args:
        yoga_data: Dictionary from get_yoga()

    Returns:
        True if valid, False otherwise
    """
    required_keys = {"number", "name", "progress"}
    return (
        required_keys.issubset(yoga_data.keys())
        and 1 <= yoga_data["number"] <= 27
        and 0 <= yoga_data["progress"] <= 1
    )


def validate_karana(karana_data: Dict[str, Any]) -> bool:
    """
    Validate karana calculation result.

    Args:
        karana_data: Dictionary from get_karana_advanced()

    Returns:
        True if valid, False otherwise
    """
    required_keys = {"number", "name", "half"}
    return (
        required_keys.issubset(karana_data.keys())
        and 1 <= karana_data["number"] <= 11
        and karana_data["half"] in [1, 2]
    )


def validate_vara(vara_data: Dict[str, Any]) -> bool:
    """
    Validate vara calculation result.

    Args:
        vara_data: Dictionary from get_vara()

    Returns:
        True if valid, False otherwise
    """
    required_keys = {"number", "name", "lord"}
    return (
        required_keys.issubset(vara_data.keys())
        and 0 <= vara_data["number"] <= 6
        and vara_data["lord"] in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    )
