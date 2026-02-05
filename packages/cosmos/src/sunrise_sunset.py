"""Sunrise and sunset calculations using Swiss Ephemeris.

This module provides accurate sunrise and sunset times for any location and date
using the Swiss Ephemeris `swe.rise_trans()` function. These calculations are
essential for:
- Muhurta (auspicious timing) calculations
- Upagraha (sub-planet) calculations
- Choghadiya and other time-division systems
- Panchanga (daily almanac) generation

All times are returned in UTC.
"""

from datetime import UTC, datetime
from typing import Any

import swisseph as swe

from .ephemeris import get_julian_day


def _jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day number to UTC datetime.

    Args:
        jd: Julian Day number

    Returns:
        datetime: UTC datetime object
    """
    year, month, day, hour_decimal = swe.revjul(jd)
    hours = int(hour_decimal)
    remainder = (hour_decimal - hours) * 60
    minutes = int(remainder)
    seconds = int((remainder - minutes) * 60)
    return datetime(year, month, day, hours, minutes, seconds, tzinfo=UTC)


def get_sunrise_sunset(
    date: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> dict[str, Any]:
    """Calculate sunrise and sunset for a given date and location.

    Uses Swiss Ephemeris `swe.rise_trans()` for accurate astronomical
    sunrise/sunset calculations accounting for atmospheric refraction.

    Args:
        date: Date for calculation (time component is ignored, uses date only)
        latitude: Geographic latitude (-90 to 90, positive North)
        longitude: Geographic longitude (-180 to 180, positive East)
        altitude: Altitude above sea level in meters (default: 0)

    Returns:
        Dictionary containing:
            - sunrise: datetime (UTC)
            - sunset: datetime (UTC)
            - sunrise_jd: float (Julian Day of sunrise)
            - sunset_jd: float (Julian Day of sunset)
            - day_duration_hours: float
            - night_duration_hours: float

    Raises:
        ValueError: If location is at extreme latitude where sun doesn't rise/set
    """
    # Get JD for start of the day (midnight UTC)
    day_start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=UTC)
    jd_start = get_julian_day(day_start)

    # Geographic position: (longitude, latitude, altitude)
    geopos = (longitude, latitude, altitude)

    # Calculate sunrise
    # swe.rise_trans returns (result_flag, jd_result)
    # rsmi flags: CALC_RISE for sunrise, CALC_SET for sunset
    # BIT_DISC_CENTER uses disc center, BIT_NO_REFRACTION skips refraction
    try:
        rise_result = swe.rise_trans(
            jd_start,
            swe.SUN,
            geopos=geopos,
            rsmi=swe.CALC_RISE | swe.BIT_DISC_CENTER,
        )
        sunrise_jd = rise_result[1][0]
    except Exception as e:
        raise ValueError(
            f"Cannot calculate sunrise for lat={latitude}, lon={longitude}: {e}"
        ) from e

    try:
        set_result = swe.rise_trans(
            jd_start,
            swe.SUN,
            geopos=geopos,
            rsmi=swe.CALC_SET | swe.BIT_DISC_CENTER,
        )
        sunset_jd = set_result[1][0]
    except Exception as e:
        raise ValueError(f"Cannot calculate sunset for lat={latitude}, lon={longitude}: {e}") from e

    # If sunset JD is before sunrise JD, we need next day's sunset
    if sunset_jd < sunrise_jd:
        try:
            set_result = swe.rise_trans(
                sunrise_jd + 0.01,
                swe.SUN,
                geopos=geopos,
                rsmi=swe.CALC_SET | swe.BIT_DISC_CENTER,
            )
            sunset_jd = set_result[1][0]
        except Exception as e:
            raise ValueError(f"Cannot calculate sunset: {e}") from e

    sunrise_dt = _jd_to_datetime(sunrise_jd)
    sunset_dt = _jd_to_datetime(sunset_jd)

    day_duration = (sunset_jd - sunrise_jd) * 24.0
    night_duration = 24.0 - day_duration

    return {
        "sunrise": sunrise_dt,
        "sunset": sunset_dt,
        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
        "day_duration_hours": round(day_duration, 4),
        "night_duration_hours": round(night_duration, 4),
    }


def get_sunrise(
    date: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> datetime:
    """Get sunrise time for a given date and location.

    Convenience function that returns only the sunrise datetime.

    Args:
        date: Date for calculation
        latitude: Geographic latitude
        longitude: Geographic longitude
        altitude: Altitude in meters (default: 0)

    Returns:
        datetime: Sunrise time in UTC
    """
    result = get_sunrise_sunset(date, latitude, longitude, altitude)
    return result["sunrise"]


def get_sunset(
    date: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> datetime:
    """Get sunset time for a given date and location.

    Convenience function that returns only the sunset datetime.

    Args:
        date: Date for calculation
        latitude: Geographic latitude
        longitude: Geographic longitude
        altitude: Altitude in meters (default: 0)

    Returns:
        datetime: Sunset time in UTC
    """
    result = get_sunrise_sunset(date, latitude, longitude, altitude)
    return result["sunset"]


__all__ = [
    "get_sunrise",
    "get_sunrise_sunset",
    "get_sunset",
]
