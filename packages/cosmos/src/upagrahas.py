"""Upagraha (sub-planet) calculations for Vedic astrology.

Upagrahas are sensitive points calculated from the Sun's position or from
time-based divisions of the day. They provide additional layers of chart
interpretation, particularly for timing events and identifying challenges.

Two types of upagrahas:
1. Time-based: Gulika, Mandi, Yamaghanda, Kala, Mrityu, Ardhaprahara
   - Require sunrise/sunset to divide the day into 8 equal portions
   - The rising sign at the relevant portion gives the upagraha's longitude

2. Mathematical: Dhooma, Vyatipata, Parivesha, Indrachapa, Upaketu
   - Calculated directly from the Sun's longitude using fixed formulas
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from packages.core.src.constants import Rashi, Upagraha
from packages.core.src.models import UpagrahaAnalysis, UpagrahaPosition

from .ephemeris import get_house_cusps, get_julian_day
from .sunrise_sunset import get_sunrise_sunset

RASHI_LIST = list(Rashi)

# Portion numbers (1-indexed) for time-based upagrahas by weekday (0=Sunday..6=Saturday)
# Each day is divided into 8 equal portions. The planet ruling each portion varies by weekday.
# The value is which portion number (1-8) belongs to the upagraha's lord planet.
GULIKA_PORTIONS = {
    0: 7,
    1: 6,
    2: 5,
    3: 4,
    4: 3,
    5: 2,
    6: 1,  # Saturn's portion
}

MANDI_PORTIONS = GULIKA_PORTIONS  # Same portion, but uses END instead of START

YAMAGHANDA_PORTIONS = {
    0: 5,
    1: 4,
    2: 3,
    3: 2,
    4: 1,
    5: 7,
    6: 6,  # Jupiter's portion
}

KALA_PORTIONS = {
    0: 1,
    1: 7,
    2: 6,
    3: 5,
    4: 4,
    5: 3,
    6: 2,  # Sun's portion
}

MRITYU_PORTIONS = {
    0: 2,
    1: 1,
    2: 7,
    3: 6,
    4: 5,
    5: 4,
    6: 3,  # Mars' portion
}

ARDHAPRAHARA_PORTIONS = {
    0: 3,
    1: 2,
    2: 1,
    3: 7,
    4: 6,
    5: 5,
    6: 4,  # Mercury's portion
}


def _longitude_to_rashi(longitude: float) -> Rashi:
    """Convert longitude to Rashi enum."""
    idx = int(longitude % 360 / 30)
    return RASHI_LIST[idx]


def _get_house_from_lagna(longitude: float, lagna_longitude: float) -> int:
    """Determine house number (1-12) based on lagna longitude."""
    diff = (longitude - lagna_longitude) % 360
    return int(diff / 30) + 1


def _get_rising_sign_at_time(
    dt: datetime,
    latitude: float,
    longitude: float,
) -> float:
    """Get the ascendant (rising sign) longitude at a specific time.

    Args:
        dt: Datetime for calculation
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        Sidereal ascendant longitude (0-360)
    """
    jd = get_julian_day(dt)
    houses = get_house_cusps(jd, latitude, longitude)
    return houses["ascendant"]


def _calculate_time_based_upagraha(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
    portion_table: dict[int, int],
    use_end: bool = False,
) -> UpagrahaPosition | None:
    """Calculate a time-based upagraha position.

    Time-based upagrahas divide the daytime into 8 equal portions.
    The rising sign at the start (or end) of the relevant portion
    gives the upagraha's longitude.

    Args:
        birth_dt: Birth datetime
        latitude: Geographic latitude
        longitude: Geographic longitude
        lagna_longitude: Ascendant longitude for house calculation
        portion_table: Weekday-to-portion mapping
        use_end: If True, use end of portion instead of start

    Returns:
        UpagrahaPosition or None if calculation fails
    """
    sr_data = get_sunrise_sunset(birth_dt, latitude, longitude)
    sunrise_dt = sr_data["sunrise"]
    sunset_dt = sr_data["sunset"]

    # Strip timezone for timedelta calculations
    sunrise_naive = sunrise_dt.replace(tzinfo=None)
    sunset_naive = sunset_dt.replace(tzinfo=None)

    day_duration = (sunset_naive - sunrise_naive).total_seconds()
    portion_duration = day_duration / 8.0

    # Get weekday (0=Monday in Python, but we need 0=Sunday)
    # Python: Monday=0, Sunday=6. We need: Sunday=0, Monday=1, ..., Saturday=6
    py_weekday = birth_dt.weekday()
    weekday = (py_weekday + 1) % 7  # Convert to Sunday=0

    portion_num = portion_table.get(weekday, 1)

    # Calculate the time at start or end of the portion
    if use_end:
        offset_seconds = portion_num * portion_duration
    else:
        offset_seconds = (portion_num - 1) * portion_duration

    portion_time = sunrise_naive + timedelta(seconds=offset_seconds)

    # Get the rising sign at this time
    asc_longitude = _get_rising_sign_at_time(portion_time, latitude, longitude)

    rashi = _longitude_to_rashi(asc_longitude)
    degree_in_sign = asc_longitude % 30
    house = _get_house_from_lagna(asc_longitude, lagna_longitude)

    return UpagrahaPosition(
        upagraha=Upagraha.GULIKA,  # Will be overwritten by caller
        longitude=round(asc_longitude, 4),
        rashi=rashi,
        degree_in_sign=round(degree_in_sign, 4),
        house=house,
        calculation_method="time_based",
    )


def calculate_gulika(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Calculate Gulika position.

    Gulika is the most important upagraha, calculated from the START
    of Saturn's portion of the day.

    Args:
        birth_dt: Birth datetime
        latitude: Geographic latitude
        longitude: Geographic longitude
        lagna_longitude: Ascendant longitude

    Returns:
        UpagrahaPosition for Gulika
    """
    pos = _calculate_time_based_upagraha(
        birth_dt, latitude, longitude, lagna_longitude, GULIKA_PORTIONS, use_end=False
    )
    return UpagrahaPosition(
        upagraha=Upagraha.GULIKA,
        longitude=pos.longitude,
        rashi=pos.rashi,
        degree_in_sign=pos.degree_in_sign,
        house=pos.house,
        calculation_method="time_based_start_of_saturn_portion",
    )


def calculate_mandi(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Calculate Mandi position.

    Mandi uses the END of Saturn's portion (same portion as Gulika).

    Args:
        birth_dt: Birth datetime
        latitude: Geographic latitude
        longitude: Geographic longitude
        lagna_longitude: Ascendant longitude

    Returns:
        UpagrahaPosition for Mandi
    """
    pos = _calculate_time_based_upagraha(
        birth_dt, latitude, longitude, lagna_longitude, MANDI_PORTIONS, use_end=True
    )
    return UpagrahaPosition(
        upagraha=Upagraha.MANDI,
        longitude=pos.longitude,
        rashi=pos.rashi,
        degree_in_sign=pos.degree_in_sign,
        house=pos.house,
        calculation_method="time_based_end_of_saturn_portion",
    )


def calculate_yamaghanda_upagraha(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Calculate Yamaghanda upagraha position.

    Args:
        birth_dt: Birth datetime
        latitude: Geographic latitude
        longitude: Geographic longitude
        lagna_longitude: Ascendant longitude

    Returns:
        UpagrahaPosition for Yamaghanda
    """
    pos = _calculate_time_based_upagraha(
        birth_dt, latitude, longitude, lagna_longitude, YAMAGHANDA_PORTIONS, use_end=False
    )
    return UpagrahaPosition(
        upagraha=Upagraha.YAMAGHANDA,
        longitude=pos.longitude,
        rashi=pos.rashi,
        degree_in_sign=pos.degree_in_sign,
        house=pos.house,
        calculation_method="time_based_jupiter_portion",
    )


def calculate_kala(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Calculate Kala upagraha position (Sun's portion)."""
    pos = _calculate_time_based_upagraha(
        birth_dt, latitude, longitude, lagna_longitude, KALA_PORTIONS, use_end=False
    )
    return UpagrahaPosition(
        upagraha=Upagraha.KALA,
        longitude=pos.longitude,
        rashi=pos.rashi,
        degree_in_sign=pos.degree_in_sign,
        house=pos.house,
        calculation_method="time_based_sun_portion",
    )


def calculate_mrityu(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Calculate Mrityu upagraha position (Mars' portion)."""
    pos = _calculate_time_based_upagraha(
        birth_dt, latitude, longitude, lagna_longitude, MRITYU_PORTIONS, use_end=False
    )
    return UpagrahaPosition(
        upagraha=Upagraha.MRITYU,
        longitude=pos.longitude,
        rashi=pos.rashi,
        degree_in_sign=pos.degree_in_sign,
        house=pos.house,
        calculation_method="time_based_mars_portion",
    )


def calculate_ardhaprahara(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Calculate Ardhaprahara upagraha position (Mercury's portion)."""
    pos = _calculate_time_based_upagraha(
        birth_dt, latitude, longitude, lagna_longitude, ARDHAPRAHARA_PORTIONS, use_end=False
    )
    return UpagrahaPosition(
        upagraha=Upagraha.ARDHAPRAHARA,
        longitude=pos.longitude,
        rashi=pos.rashi,
        degree_in_sign=pos.degree_in_sign,
        house=pos.house,
        calculation_method="time_based_mercury_portion",
    )


# ============================================
# Mathematical Upagrahas (Sun-derived)
# ============================================


def _make_math_upagraha(
    upagraha: Upagraha,
    longitude: float,
    lagna_longitude: float,
) -> UpagrahaPosition:
    """Create UpagrahaPosition for a mathematical upagraha."""
    lon = longitude % 360
    rashi = _longitude_to_rashi(lon)
    degree_in_sign = lon % 30
    house = _get_house_from_lagna(lon, lagna_longitude)

    return UpagrahaPosition(
        upagraha=upagraha,
        longitude=round(lon, 4),
        rashi=rashi,
        degree_in_sign=round(degree_in_sign, 4),
        house=house,
        calculation_method="mathematical",
    )


def calculate_dhooma(sun_longitude: float, lagna_longitude: float = 0.0) -> UpagrahaPosition:
    """Calculate Dhooma position.

    Formula: (Sun longitude + 133°20') % 360

    Args:
        sun_longitude: Sun's sidereal longitude
        lagna_longitude: Ascendant longitude for house calculation

    Returns:
        UpagrahaPosition for Dhooma
    """
    lon = (sun_longitude + 133.3333) % 360
    return _make_math_upagraha(Upagraha.DHOOMA, lon, lagna_longitude)


def calculate_vyatipata(dhooma_longitude: float, lagna_longitude: float = 0.0) -> UpagrahaPosition:
    """Calculate Vyatipata position.

    Formula: (360 - Dhooma longitude) % 360

    Args:
        dhooma_longitude: Dhooma's longitude
        lagna_longitude: Ascendant longitude for house calculation

    Returns:
        UpagrahaPosition for Vyatipata
    """
    lon = (360 - dhooma_longitude) % 360
    return _make_math_upagraha(Upagraha.VYATIPATA, lon, lagna_longitude)


def calculate_parivesha(
    vyatipata_longitude: float, lagna_longitude: float = 0.0
) -> UpagrahaPosition:
    """Calculate Parivesha position.

    Formula: (Vyatipata longitude + 180) % 360

    Args:
        vyatipata_longitude: Vyatipata's longitude
        lagna_longitude: Ascendant longitude for house calculation

    Returns:
        UpagrahaPosition for Parivesha
    """
    lon = (vyatipata_longitude + 180) % 360
    return _make_math_upagraha(Upagraha.PARIVESHA, lon, lagna_longitude)


def calculate_indrachapa(
    parivesha_longitude: float, lagna_longitude: float = 0.0
) -> UpagrahaPosition:
    """Calculate Indrachapa position.

    Formula: (360 - Parivesha longitude) % 360

    Args:
        parivesha_longitude: Parivesha's longitude
        lagna_longitude: Ascendant longitude for house calculation

    Returns:
        UpagrahaPosition for Indrachapa
    """
    lon = (360 - parivesha_longitude) % 360
    return _make_math_upagraha(Upagraha.INDRACHAPA, lon, lagna_longitude)


def calculate_upaketu(sun_longitude: float, lagna_longitude: float = 0.0) -> UpagrahaPosition:
    """Calculate Upaketu position.

    Formula: (Sun longitude - 30) % 360

    Args:
        sun_longitude: Sun's sidereal longitude
        lagna_longitude: Ascendant longitude for house calculation

    Returns:
        UpagrahaPosition for Upaketu
    """
    lon = (sun_longitude - 30) % 360
    return _make_math_upagraha(Upagraha.UPAKETU, lon, lagna_longitude)


# ============================================
# Complete calculation
# ============================================


def calculate_all_upagrahas(
    birth_dt: datetime,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
    sun_longitude: float,
) -> UpagrahaAnalysis:
    """Calculate all 11 upagraha positions.

    Args:
        birth_dt: Birth datetime
        latitude: Geographic latitude
        longitude: Geographic longitude
        lagna_longitude: Ascendant longitude
        sun_longitude: Sun's sidereal longitude

    Returns:
        UpagrahaAnalysis with all positions and effects
    """
    sr_data = get_sunrise_sunset(birth_dt, latitude, longitude)

    positions: dict[str, UpagrahaPosition] = {}

    # Time-based upagrahas
    positions["gulika"] = calculate_gulika(birth_dt, latitude, longitude, lagna_longitude)
    positions["mandi"] = calculate_mandi(birth_dt, latitude, longitude, lagna_longitude)
    positions["yamaghanda"] = calculate_yamaghanda_upagraha(
        birth_dt, latitude, longitude, lagna_longitude
    )
    positions["kala"] = calculate_kala(birth_dt, latitude, longitude, lagna_longitude)
    positions["mrityu"] = calculate_mrityu(birth_dt, latitude, longitude, lagna_longitude)
    positions["ardhaprahara"] = calculate_ardhaprahara(
        birth_dt, latitude, longitude, lagna_longitude
    )

    # Mathematical upagrahas (chain from Sun)
    dhooma = calculate_dhooma(sun_longitude, lagna_longitude)
    positions["dhooma"] = dhooma

    vyatipata = calculate_vyatipata(dhooma.longitude, lagna_longitude)
    positions["vyatipata"] = vyatipata

    parivesha = calculate_parivesha(vyatipata.longitude, lagna_longitude)
    positions["parivesha"] = parivesha

    indrachapa = calculate_indrachapa(parivesha.longitude, lagna_longitude)
    positions["indrachapa"] = indrachapa

    upaketu = calculate_upaketu(sun_longitude, lagna_longitude)
    positions["upaketu"] = upaketu

    # Get effects for each position
    effects = []
    for _name, pos in positions.items():
        effect = get_upagraha_effects(pos)
        if effect:
            effects.append(effect)

    return UpagrahaAnalysis(
        positions=positions,
        sunrise=sr_data["sunrise"],
        sunset=sr_data["sunset"],
        day_duration_hours=sr_data["day_duration_hours"],
        effects=effects,
    )


def get_upagraha_effects(position: UpagrahaPosition) -> dict[str, Any]:
    """Get effects for an upagraha based on its house placement.

    Args:
        position: UpagrahaPosition with house information

    Returns:
        Dictionary with upagraha name, house, and effects description
    """
    definitions_path = (
        Path(__file__).parent.parent.parent.parent
        / "knowledge"
        / "definitions"
        / "upagraha_definitions.json"
    )

    try:
        with definitions_path.open() as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "upagraha": position.upagraha.value,
            "house": position.house,
            "rashi": position.rashi.value,
            "effects": "Effects data unavailable",
        }

    upagraha_name = position.upagraha.value
    upagraha_data = data.get("upagrahas", {}).get(upagraha_name, {})
    house_effects = upagraha_data.get("house_effects", {})
    house_str = str(position.house)

    return {
        "upagraha": upagraha_name,
        "house": position.house,
        "rashi": position.rashi.value,
        "longitude": position.longitude,
        "nature": upagraha_data.get("nature", "malefic"),
        "effects": house_effects.get(house_str, upagraha_data.get("effects", "")),
    }


__all__ = [
    "calculate_all_upagrahas",
    "calculate_ardhaprahara",
    "calculate_dhooma",
    "calculate_gulika",
    "calculate_indrachapa",
    "calculate_kala",
    "calculate_mandi",
    "calculate_mrityu",
    "calculate_parivesha",
    "calculate_upaketu",
    "calculate_vyatipata",
    "calculate_yamaghanda_upagraha",
    "get_upagraha_effects",
]
