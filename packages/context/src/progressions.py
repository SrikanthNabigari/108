"""Secondary Progressions module for 108 Vedic Astrology app.

Secondary progressions use the principle: 1 day after birth = 1 year of life.
To find the progressed positions for a given age, calculate planetary positions
for birth_date + age_in_days.

This is a widely used predictive technique in both Western and Vedic astrology
for understanding long-term life themes and timing of events.
"""

from datetime import datetime, timedelta
from typing import Any

from packages.cosmos.src.ephemeris import get_all_planets, get_julian_day

# Aspect definitions: (name, angle, orb)
ASPECTS = [
    ("conjunction", 0, 1.0),
    ("opposition", 180, 1.0),
    ("trine", 120, 1.0),
    ("square", 90, 1.0),
    ("sextile", 60, 1.0),
]

# Rashi names by longitude range
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

# Planets to track in progressions
PROGRESSION_PLANETS = [
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
    "rahu",
    "ketu",
]


def _longitude_to_sign(longitude: float) -> str:
    """Convert a sidereal longitude to its rashi name.

    Args:
        longitude: Sidereal longitude (0-360)

    Returns:
        Rashi name string
    """
    index = int(longitude / 30) % 12
    return RASHI_NAMES[index]


def _angle_diff(lon1: float, lon2: float) -> float:
    """Calculate the shortest angular difference between two longitudes.

    Args:
        lon1: First longitude (0-360)
        lon2: Second longitude (0-360)

    Returns:
        Shortest difference in degrees (0-180)
    """
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def calculate_progressed_positions(
    birth_datetime: datetime,
    birth_lat: float,  # noqa: ARG001
    birth_lon: float,  # noqa: ARG001
    target_age: float,
) -> dict[str, dict[str, Any]]:
    """Calculate progressed planetary positions for a given age.

    Uses the day-for-a-year principle: birth_date + age_days gives the
    ephemeris date whose positions represent the progressed chart.

    Args:
        birth_datetime: Birth datetime (UTC or timezone-aware)
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        target_age: Age in years (can be fractional, e.g., 32.5)

    Returns:
        Dictionary keyed by planet name, each containing:
            - longitude: Progressed sidereal longitude
            - latitude: Progressed latitude
            - speed: Daily motion (progressed)
            - is_retrograde: Whether progressed planet is retrograde
            - sign: Rashi name for the progressed position

    Example:
        >>> from datetime import datetime
        >>> positions = calculate_progressed_positions(
        ...     datetime(1992, 12, 3), 16.72, 81.29, 32.0
        ... )
        >>> 'sun' in positions
        True
    """
    # Day-for-a-year: add target_age days to birth datetime
    progressed_dt = birth_datetime + timedelta(days=target_age)

    # Get Julian Day for the progressed date
    jd = get_julian_day(progressed_dt)

    # Get planetary positions at the progressed date
    raw_positions = get_all_planets(jd)

    # Format the result
    result = {}
    for planet in PROGRESSION_PLANETS:
        if planet in raw_positions:
            pos = raw_positions[planet]
            lon = pos["longitude"]
            result[planet] = {
                "longitude": lon,
                "latitude": pos.get("latitude", 0.0),
                "speed": pos.get("speed", 0.0),
                "is_retrograde": pos.get("is_retrograde", False),
                "sign": _longitude_to_sign(lon),
            }

    return result


def calculate_progressed_to_natal_aspects(
    progressed: dict[str, dict[str, Any]],
    natal: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find aspects between progressed and natal planet positions.

    Checks all combinations of progressed planets aspecting natal planets
    using standard aspects (conjunction, opposition, trine, square, sextile)
    with 1-degree orb.

    Args:
        progressed: Progressed positions dict (planet -> {longitude, ...})
        natal: Natal positions dict (planet -> {longitude, ...})

    Returns:
        List of aspect dicts with:
            - progressed_planet: str
            - natal_planet: str
            - aspect: str (e.g., "conjunction", "trine")
            - angle: float (exact angle of the aspect)
            - orb: float (how far from exact)
            - progressed_longitude: float
            - natal_longitude: float

    Example:
        >>> aspects = calculate_progressed_to_natal_aspects(progressed, natal)
        >>> aspects[0]['aspect']
        'conjunction'
    """
    aspects_found = []

    for p_planet, p_data in progressed.items():
        p_lon = p_data["longitude"]

        for n_planet, n_data in natal.items():
            n_lon = n_data["longitude"]

            diff = _angle_diff(p_lon, n_lon)

            for aspect_name, aspect_angle, orb in ASPECTS:
                if abs(diff - aspect_angle) <= orb:
                    aspects_found.append(
                        {
                            "progressed_planet": p_planet,
                            "natal_planet": n_planet,
                            "aspect": aspect_name,
                            "angle": aspect_angle,
                            "orb": round(abs(diff - aspect_angle), 4),
                            "progressed_longitude": round(p_lon, 4),
                            "natal_longitude": round(n_lon, 4),
                        }
                    )

    return aspects_found


def get_current_progressions(
    birth_datetime: datetime,
    birth_lat: float,
    birth_lon: float,
    query_datetime: datetime | None = None,
) -> dict[str, Any]:
    """Get current progressed positions and active aspects to natal chart.

    Args:
        birth_datetime: Birth datetime
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        query_datetime: Datetime to query (defaults to now)

    Returns:
        Dictionary with:
            - age: Current age in years
            - progressed_positions: Dict of planet -> position data
            - natal_positions: Dict of natal planet positions
            - active_aspects: List of active progressed-to-natal aspects
            - progressed_moon_sign: Current progressed Moon sign
            - progressed_sun_sign: Current progressed Sun sign

    Example:
        >>> from datetime import datetime
        >>> result = get_current_progressions(
        ...     datetime(1992, 12, 3), 16.72, 81.29,
        ...     query_datetime=datetime(2025, 1, 1)
        ... )
        >>> result['progressed_moon_sign']
        'aries'
    """
    if query_datetime is None:
        query_datetime = datetime.now()

    # Calculate age in years
    birth_naive = birth_datetime.replace(tzinfo=None) if birth_datetime.tzinfo else birth_datetime
    query_naive = query_datetime.replace(tzinfo=None) if query_datetime.tzinfo else query_datetime
    age_days = (query_naive - birth_naive).days
    age_years = age_days / 365.25

    # Get natal positions (positions at birth)
    natal_jd = get_julian_day(birth_datetime)
    natal_raw = get_all_planets(natal_jd)
    natal_positions = {}
    for planet in PROGRESSION_PLANETS:
        if planet in natal_raw:
            pos = natal_raw[planet]
            lon = pos["longitude"]
            natal_positions[planet] = {
                "longitude": lon,
                "latitude": pos.get("latitude", 0.0),
                "speed": pos.get("speed", 0.0),
                "is_retrograde": pos.get("is_retrograde", False),
                "sign": _longitude_to_sign(lon),
            }

    # Get progressed positions
    progressed_positions = calculate_progressed_positions(
        birth_datetime, birth_lat, birth_lon, age_years
    )

    # Calculate aspects between progressed and natal
    active_aspects = calculate_progressed_to_natal_aspects(progressed_positions, natal_positions)

    # Get Moon and Sun signs
    progressed_moon_sign = progressed_positions.get("moon", {}).get("sign", "unknown")
    progressed_sun_sign = progressed_positions.get("sun", {}).get("sign", "unknown")

    return {
        "age": round(age_years, 2),
        "progressed_positions": progressed_positions,
        "natal_positions": natal_positions,
        "active_aspects": active_aspects,
        "progressed_moon_sign": progressed_moon_sign,
        "progressed_sun_sign": progressed_sun_sign,
    }


def get_progression_timeline(
    birth_datetime: datetime,
    birth_lat: float,
    birth_lon: float,
    start_age: int,
    end_age: int,
) -> list[dict[str, Any]]:
    """Generate a timeline of key progressed aspects across a range of ages.

    Calculates progressed positions for each year in the range and finds
    all active aspects to the natal chart.

    Args:
        birth_datetime: Birth datetime
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        start_age: Starting age in years
        end_age: Ending age in years (inclusive)

    Returns:
        List of dicts with:
            - age: int
            - progressed_sun_sign: str
            - progressed_moon_sign: str
            - aspects: list of active aspects

    Raises:
        ValueError: If start_age > end_age or ages are negative

    Example:
        >>> from datetime import datetime
        >>> timeline = get_progression_timeline(
        ...     datetime(1992, 12, 3), 16.72, 81.29, 30, 35
        ... )
        >>> len(timeline)
        6
    """
    if start_age < 0:
        raise ValueError(f"start_age must be >= 0, got {start_age}")
    if end_age < start_age:
        raise ValueError(f"end_age ({end_age}) must be >= start_age ({start_age})")

    # Get natal positions once
    natal_jd = get_julian_day(birth_datetime)
    natal_raw = get_all_planets(natal_jd)
    natal_positions = {}
    for planet in PROGRESSION_PLANETS:
        if planet in natal_raw:
            pos = natal_raw[planet]
            lon = pos["longitude"]
            natal_positions[planet] = {
                "longitude": lon,
                "latitude": pos.get("latitude", 0.0),
                "speed": pos.get("speed", 0.0),
                "is_retrograde": pos.get("is_retrograde", False),
                "sign": _longitude_to_sign(lon),
            }

    timeline = []

    for age in range(start_age, end_age + 1):
        progressed = calculate_progressed_positions(
            birth_datetime, birth_lat, birth_lon, float(age)
        )

        aspects = calculate_progressed_to_natal_aspects(progressed, natal_positions)

        moon_sign = progressed.get("moon", {}).get("sign", "unknown")
        sun_sign = progressed.get("sun", {}).get("sign", "unknown")

        timeline.append(
            {
                "age": age,
                "progressed_sun_sign": sun_sign,
                "progressed_moon_sign": moon_sign,
                "aspects": aspects,
            }
        )

    return timeline
