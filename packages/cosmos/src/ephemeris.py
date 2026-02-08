"""Swiss Ephemeris wrapper for Vedic astrology calculations.

This module provides sidereal (Vedic) planetary positions using pyswisseph.
Always uses Lahiri ayanamsa by default.

All positions are calculated in sidereal/Vedic zodiac.
"""

from datetime import UTC, datetime
from typing import Any

import swisseph as swe

# Swiss Ephemeris planet constants
PLANET_MAP = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mars": swe.MARS,
    "mercury": swe.MERCURY,
    "jupiter": swe.JUPITER,
    "venus": swe.VENUS,
    "saturn": swe.SATURN,
    "rahu": swe.MEAN_NODE,  # Use mean node for Rahu
    # Ketu is calculated as Rahu + 180°
}

# Ayanamsa constants (precession correction systems)
AYANAMSA_MAP = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar": swe.SIDM_YUKTESHWAR,
}

# House system constants
HOUSE_SYSTEM_MAP = {
    "placidus": b"P",
    "koch": b"K",
    "whole_sign": b"W",
    "equal": b"E",
    "campanus": b"C",
}


def get_julian_day(dt: datetime) -> float:
    """Convert datetime to Julian Day Number.

    Converts a datetime object to Julian Day Number (JD) used for all
    ephemeris calculations. Automatically handles timezone conversion to UTC.

    Args:
        dt: datetime object (can be timezone-aware or naive, naive assumes UTC)

    Returns:
        float: Julian Day Number

    Raises:
        TypeError: If dt is not a datetime object

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2000, 1, 1, 12, 0, 0)
        >>> jd = get_julian_day(dt)
        >>> jd
        2451545.0
    """
    if not isinstance(dt, datetime):
        raise TypeError(f"Expected datetime object, got {type(dt)}")

    # Ensure UTC timezone
    dt = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)

    # Calculate Julian Day with decimal hours
    hour_decimal = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    jd = swe.julday(dt.year, dt.month, dt.day, hour_decimal)

    return float(jd)


def get_ayanamsa(jd: float, system: str = "lahiri") -> float:
    """Get ayanamsa (precession correction) for a given Julian Day.

    Ayanamsa is the difference between the tropical and sidereal zodiac.
    This value is subtracted from tropical coordinates to get sidereal positions.

    Args:
        jd: Julian Day number
        system: Ayanamsa system to use. Options:
            - "lahiri" (default, most common for Vedic astrology)
            - "raman"
            - "krishnamurti"
            - "yukteshwar"

    Returns:
        float: Ayanamsa value in degrees

    Raises:
        ValueError: If system is not recognized

    Example:
        >>> jd = 2451545.0
        >>> ayan = get_ayanamsa(jd, "lahiri")
        >>> ayan
        24.37...
    """
    system_lower = system.lower()
    sid_mode = AYANAMSA_MAP.get(system_lower)

    if sid_mode is None:
        raise ValueError(
            f"Unknown ayanamsa system: {system}. Valid options: {', '.join(AYANAMSA_MAP.keys())}"
        )

    swe.set_sid_mode(sid_mode)
    ayan = swe.get_ayanamsa(jd)

    return float(ayan)


def _validate_jd(jd: float) -> None:
    """Validate Julian Day number is in reasonable range.

    Acceptable range corresponds to approximately 1000 CE to 3000 CE.
    JD 2086302.5 ~ 1000-01-01, JD 2816788.5 ~ 3000-01-01.

    Args:
        jd: Julian Day number

    Raises:
        ValueError: If jd is outside the valid range
    """
    jd_min = 2086302.5  # ~1000 CE
    jd_max = 2816788.5  # ~3000 CE
    if not isinstance(jd, int | float) or jd < jd_min or jd > jd_max:
        raise ValueError(
            f"Julian Day must be between {jd_min} (~1000 CE) and {jd_max} (~3000 CE), got {jd}"
        )


def _validate_coordinates(latitude: float, longitude: float) -> None:
    """Validate geographic coordinates.

    Args:
        latitude: Geographic latitude in degrees (-90 to 90)
        longitude: Geographic longitude in degrees (-180 to 180)

    Raises:
        ValueError: If coordinates are out of range
    """
    if not isinstance(latitude, int | float) or latitude < -90 or latitude > 90:
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not isinstance(longitude, int | float) or longitude < -180 or longitude > 180:
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")


def get_planet_position(planet: str, jd: float, ayanamsa: float | None = None) -> dict[str, Any]:
    """Calculate sidereal (Vedic) position of a planet.

    Calculates the position of a planet in the sidereal zodiac, accounting for
    ayanamsa correction. Returns longitude, latitude, speed, and retrograde status.

    Args:
        planet: Planet name. Valid values:
            - "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"
            - "rahu" (mean node, always retrograde)
            - "ketu" (calculated as Rahu + 180°)
        jd: Julian Day number
        ayanamsa: Ayanamsa value in degrees (if None, calculates Lahiri ayanamsa)

    Returns:
        dict: Contains:
            - "longitude": Sidereal longitude in degrees (0-360)
            - "latitude": Ecliptic latitude in degrees
            - "speed": Daily motion in degrees/day (negative if retrograde)
            - "is_retrograde": Boolean indicating retrograde motion

    Raises:
        ValueError: If planet name is not recognized or jd is out of range

    Example:
        >>> pos = get_planet_position("sun", 2451545.0)
        >>> pos["longitude"]
        280.3...
        >>> pos["is_retrograde"]
        False
    """
    _validate_jd(jd)
    planet_lower = planet.lower()

    # Handle Ketu specially (opposite to Rahu)
    if planet_lower == "ketu":
        rahu_pos = get_planet_position("rahu", jd, ayanamsa)
        ketu_lon = (rahu_pos["longitude"] + 180.0) % 360.0
        return {
            "longitude": ketu_lon,
            "latitude": -rahu_pos["latitude"],  # Opposite latitude
            "speed": rahu_pos["speed"],
            "is_retrograde": True,  # Ketu is always retrograde
        }

    # Get Swiss Ephemeris planet ID
    swe_planet = PLANET_MAP.get(planet_lower)
    if swe_planet is None:
        raise ValueError(
            f"Unknown planet: {planet}. Valid planets: {', '.join(sorted(PLANET_MAP.keys()))}, ketu"
        )

    # Calculate tropical position using Swiss Ephemeris
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result, _ret_flags = swe.calc_ut(jd, swe_planet, flags)

    tropical_lon = result[0]
    latitude = result[1]
    speed = result[3]

    # Get ayanamsa if not provided
    if ayanamsa is None:
        ayanamsa = get_ayanamsa(jd, "lahiri")

    # Convert tropical to sidereal longitude
    sidereal_lon = (tropical_lon - ayanamsa) % 360.0

    # Determine retrograde status
    is_retrograde = speed < 0

    # Rahu is always retrograde (by definition)
    if planet_lower == "rahu":
        is_retrograde = True

    return {
        "longitude": float(sidereal_lon),
        "latitude": float(latitude),
        "speed": float(speed),
        "is_retrograde": bool(is_retrograde),
    }


def get_all_planets(jd: float, ayanamsa: float | str | None = None) -> dict[str, dict[str, Any]]:
    """Calculate sidereal positions of all 9 Vedic planets.

    Calculates positions for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn,
    Rahu, and Ketu using a single ayanamsa correction.

    Args:
        jd: Julian Day number
        ayanamsa: Ayanamsa value in degrees, or name string (e.g., "lahiri").
                  If None, uses Lahiri ayanamsa.

    Returns:
        dict: Mapping of planet names to position dicts, each containing:
            - "longitude": Sidereal longitude in degrees (0-360)
            - "latitude": Ecliptic latitude in degrees
            - "speed": Daily motion in degrees/day
            - "is_retrograde": Boolean

    Example:
        >>> planets = get_all_planets(2451545.0)
        >>> planets["sun"]["longitude"]
        280.3...
        >>> planets["moon"]["is_retrograde"]
        False
        >>> planets["rahu"]["is_retrograde"]
        True
    """
    # Handle string ayanamsa names by converting to float
    if ayanamsa is None:
        ayanamsa = get_ayanamsa(jd, "lahiri")
    elif isinstance(ayanamsa, str):
        ayanamsa = get_ayanamsa(jd, ayanamsa)

    # All 9 Vedic planets
    planet_list = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

    positions = {}
    for planet in planet_list:
        positions[planet] = get_planet_position(planet, jd, ayanamsa)

    return positions


def get_house_cusps(
    jd: float,
    latitude: float,
    longitude: float,
    house_system: str = "placidus",
    ayanamsa: float | str | None = None,
) -> dict[str, Any]:
    """Calculate house cusps and angles for a given location and time.

    Calculates the 12 house cusps and angles (Ascendant and Midheaven) in
    the sidereal zodiac. Uses geographic coordinates and Julian Day.

    Args:
        jd: Julian Day number
        latitude: Geographic latitude in degrees (negative for South)
        longitude: Geographic longitude in degrees (negative for West)
        house_system: House system to use. Options:
            - "placidus" (default, tropical houses)
            - "koch"
            - "whole_sign"
            - "equal"
            - "campanus"
        ayanamsa: Ayanamsa value in degrees, or name string (e.g., "lahiri").
                  If None, uses Lahiri ayanamsa.

    Returns:
        dict: Contains:
            - "ascendant": Ascendant (1st house cusp) in sidereal degrees
            - "mc": Midheaven (10th house cusp) in sidereal degrees
            - "cusps": List of 12 house cusps (index 0 = 1st house cusp)

    Raises:
        ValueError: If house_system is not recognized

    Note:
        All returned values are in sidereal/Vedic zodiac (ayanamsa-corrected).

    Example:
        >>> houses = get_house_cusps(2451545.0, 12.9716, 77.5946)  # Delhi
        >>> houses["ascendant"]
        123.45...
        >>> len(houses["cusps"])
        12
    """
    _validate_jd(jd)
    _validate_coordinates(latitude, longitude)

    # Validate and get house system code
    hsys_code = HOUSE_SYSTEM_MAP.get(house_system.lower())
    if hsys_code is None:
        raise ValueError(
            f"Unknown house system: {house_system}. "
            f"Valid options: {', '.join(HOUSE_SYSTEM_MAP.keys())}"
        )

    # Calculate houses in tropical zodiac
    cusps, ascmc = swe.houses(jd, latitude, longitude, hsys_code)

    # Handle ayanamsa: convert string to float if needed
    if ayanamsa is None:
        ayanamsa_value = get_ayanamsa(jd, "lahiri")
    elif isinstance(ayanamsa, str):
        ayanamsa_value = get_ayanamsa(jd, ayanamsa)
    else:
        ayanamsa_value = ayanamsa

    # Convert all values to sidereal zodiac
    sidereal_cusps = [float((c - ayanamsa_value) % 360.0) for c in cusps]
    sidereal_asc = float((ascmc[0] - ayanamsa_value) % 360.0)
    sidereal_mc = float((ascmc[1] - ayanamsa_value) % 360.0)

    return {
        "ascendant": sidereal_asc,
        "mc": sidereal_mc,
        "cusps": sidereal_cusps,  # 12 cusps, index 0 = 1st house (Ascendant)
    }


def get_ascendant(jd: float, latitude: float, longitude: float) -> float:
    """Get the sidereal ascendant degree for a given location and time.

    Convenience function to get only the ascendant (Lagna) in the sidereal zodiac.

    Args:
        jd: Julian Day number
        latitude: Geographic latitude in degrees
        longitude: Geographic longitude in degrees

    Returns:
        float: Sidereal ascendant longitude in degrees (0-360)

    Example:
        >>> asc = get_ascendant(2451545.0, 12.9716, 77.5946)
        >>> asc
        123.45...
    """
    houses = get_house_cusps(jd, latitude, longitude)
    return houses["ascendant"]


def datetime_to_jd(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
) -> float:
    """Convenience function to convert date/time components to Julian Day.

    Alternative to creating a datetime object and using get_julian_day().
    Assumes UTC timezone.

    Args:
        year: Year (e.g., 2000)
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23, default 0)
        minute: Minute (0-59, default 0)
        second: Second (0-59, default 0)

    Returns:
        float: Julian Day Number

    Raises:
        ValueError: If date/time values are invalid

    Example:
        >>> jd = datetime_to_jd(2000, 1, 1, 12, 0, 0)
        >>> jd
        2451545.0
    """
    # Validate ranges
    if not (1 <= month <= 12):
        raise ValueError(f"Month must be 1-12, got {month}")
    if not (1 <= day <= 31):
        raise ValueError(f"Day must be 1-31, got {day}")
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be 0-23, got {hour}")
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute must be 0-59, got {minute}")
    if not (0 <= second <= 59):
        raise ValueError(f"Second must be 0-59, got {second}")

    # Calculate decimal hour
    hour_decimal = hour + minute / 60.0 + second / 3600.0
    jd = swe.julday(year, month, day, hour_decimal)

    return float(jd)


def find_planet_rashi_ingress(
    planet: str,
    target_rashi: int,
    start_jd: float,
    end_jd: float,
    *,
    find_first: bool = False,
) -> float | None:
    """Find when a planet enters a target sidereal rashi between two Julian Days.

    Uses monthly sampling followed by binary search to find the crossing day
    (within ~0.5 day precision).

    Args:
        planet: Planet name (e.g. "saturn", "jupiter").
        target_rashi: Target rashi index (0-11, 0=Aries).
        start_jd: Start of search window (Julian Day).
        end_jd: End of search window (Julian Day).
        find_first: If True, return the *first* ingress. If False (default),
            return the *last* ingress (definitive entry after retrogrades).

    Returns:
        Julian Day of ingress, or None if the planet never enters that rashi
        in the window.
    """
    _validate_jd(start_jd)
    _validate_jd(end_jd)
    if target_rashi < 0 or target_rashi > 11:
        raise ValueError(f"target_rashi must be 0-11, got {target_rashi}")

    step = 30.0  # ~1 month sampling
    samples: list[tuple[float, int]] = []
    jd = start_jd
    while jd <= end_jd:
        pos = get_planet_position(planet, jd)
        rashi = int(pos["longitude"] / 30) % 12
        samples.append((jd, rashi))
        jd += step
    # ensure we include end_jd
    if not samples or samples[-1][0] < end_jd:
        pos = get_planet_position(planet, end_jd)
        rashi = int(pos["longitude"] / 30) % 12
        samples.append((end_jd, rashi))

    # Find crossing pairs where planet enters target_rashi
    crossing_pair: tuple[float, float] | None = None
    for i in range(1, len(samples)):
        prev_rashi = samples[i - 1][1]
        curr_rashi = samples[i][1]
        if curr_rashi == target_rashi and prev_rashi != target_rashi:
            crossing_pair = (samples[i - 1][0], samples[i][0])
            if find_first:
                break  # stop at first crossing

    if crossing_pair is None:
        # Planet may already be in target rashi at start
        if samples and samples[0][1] == target_rashi:
            return start_jd
        return None

    # Binary search to refine crossing to ~0.5 day
    lo, hi = crossing_pair
    while (hi - lo) > 0.5:
        mid = (lo + hi) / 2.0
        pos = get_planet_position(planet, mid)
        mid_rashi = int(pos["longitude"] / 30) % 12
        if mid_rashi == target_rashi:
            hi = mid
        else:
            lo = mid

    return hi


def close_ephemeris() -> None:
    """Close Swiss Ephemeris resources.

    Call this function when finished with ephemeris calculations to properly
    close all open files and free resources. Optional but recommended for
    long-running applications.

    Example:
        >>> # After all calculations
        >>> close_ephemeris()
    """
    swe.close()
