"""
108 Ephemeris MCP Server

Provides planetary calculation tools for Claude via Model Context Protocol.
Uses the cosmos package for Swiss Ephemeris-based calculations of planetary
positions, house cusps, nakshatras, divisional charts, and panchanga data.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add packages to path
SERVICES_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SERVICES_ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from packages.cosmos.src import (  # noqa: E402
    DIVISIONAL_NAMES,
    RASHI_NAMES,
    TITHI_NAMES,
    VARA_NAMES,
    YOGA_NAMES,
    get_all_planets,
    get_ayanamsa,
    get_divisional_chart,
    get_julian_day,
    get_nakshatra_lord,
    longitude_to_nakshatra,
)
from packages.cosmos.src import (  # noqa: E402
    get_house_cusps as calc_house_cusps,
)
from packages.cosmos.src.panchanga import (  # noqa: E402
    get_karana,
    get_tithi,
    get_vara,
    get_yoga,
)
from packages.cosmos.src.sunrise_sunset import get_sunrise_sunset  # noqa: E402
from packages.cosmos.src.upagrahas import (  # noqa: E402
    calculate_all_upagrahas,
    get_upagraha_effects,
)

# Initialize MCP server
mcp = FastMCP("108-ephemeris")


@mcp.tool()
def planetary_positions(
    datetime_iso: str, latitude: float, longitude: float, ayanamsa: str = "lahiri"
) -> dict[str, Any]:
    """
    Calculate sidereal planetary positions for all 9 Vedic planets.

    Args:
        datetime_iso: ISO format datetime (e.g., "1992-12-03T03:00:00+05:30")
        latitude: Geographic latitude (-90 to 90)
        longitude: Geographic longitude (-180 to 180)
        ayanamsa: Ayanamsa system (lahiri, raman, krishnamurti, yukteshwar)

    Returns:
        Dictionary with positions for Sun, Moon, Mars, Mercury, Jupiter,
        Venus, Saturn, Rahu, Ketu including longitude, sign, nakshatra, etc.
    """
    try:
        # Parse datetime
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))

        # Get Julian day (cosmos handles timezone)
        jd = get_julian_day(dt)

        # Get ayanamsa value
        ayanamsa_val = get_ayanamsa(jd, ayanamsa)

        # Get all planet positions (pass ayanamsa value, not string)
        planets = get_all_planets(jd, ayanamsa_val)

        # Build result with enriched data
        result = {
            "datetime": datetime_iso,
            "julian_day": jd,
            "ayanamsa": ayanamsa,
            "ayanamsa_value": round(ayanamsa_val, 4),
            "location": {"latitude": latitude, "longitude": longitude},
            "planets": {},
        }

        for planet_name, pos in planets.items():
            # Get nakshatra information
            nak_info = longitude_to_nakshatra(pos["longitude"])
            nakshatra_lord = get_nakshatra_lord(nak_info["name"])

            # Calculate sign and degree
            sign_idx = int(pos["longitude"] / 30)
            sign_degree = pos["longitude"] % 30

            result["planets"][planet_name] = {
                "longitude": round(pos["longitude"], 4),
                "latitude": round(pos.get("latitude", 0), 4),
                "speed": round(pos.get("speed", 0), 4),
                "is_retrograde": pos.get("is_retrograde", False),
                "sign": RASHI_NAMES[sign_idx] if sign_idx < 12 else "Unknown",
                "sign_degree": round(sign_degree, 2),
                "nakshatra": nak_info["name"],
                "nakshatra_number": nak_info["number"],
                "nakshatra_pada": nak_info["pada"],
                "nakshatra_lord": nakshatra_lord,
                "degree_in_nakshatra": round(nak_info["degree_in_nakshatra"], 4),
            }

        return result

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def house_cusps(
    datetime_iso: str, latitude: float, longitude: float, house_system: str = "placidus"
) -> dict[str, Any]:
    """
    Calculate house cusps and ascendant.

    Args:
        datetime_iso: ISO format datetime
        latitude: Geographic latitude
        longitude: Geographic longitude
        house_system: House system (placidus, whole_sign, equal, koch, campanus)

    Returns:
        Dictionary with ascendant, MC, and 12 house cusps
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)

        jd = get_julian_day(dt)
        houses_data = calc_house_cusps(jd, latitude, longitude, house_system)

        # Calculate ascendant sign
        asc_longitude = houses_data["ascendant"]
        asc_sign_idx = int(asc_longitude / 30)
        asc_degree = asc_longitude % 30

        # Calculate MC sign
        mc_longitude = houses_data["mc"]
        mc_sign_idx = int(mc_longitude / 30)
        mc_degree = mc_longitude % 30

        return {
            "datetime": datetime_iso,
            "location": {"latitude": latitude, "longitude": longitude},
            "house_system": house_system,
            "ascendant": {
                "longitude": round(asc_longitude, 4),
                "sign": RASHI_NAMES[asc_sign_idx] if asc_sign_idx < 12 else "Unknown",
                "degree": round(asc_degree, 2),
            },
            "mc": {
                "longitude": round(mc_longitude, 4),
                "sign": RASHI_NAMES[mc_sign_idx] if mc_sign_idx < 12 else "Unknown",
                "degree": round(mc_degree, 2),
            },
            "cusps": {
                f"house_{i + 1}": {
                    "longitude": round(houses_data["cusps"][i], 4),
                    "sign": RASHI_NAMES[int(houses_data["cusps"][i] / 30)],
                    "degree": round(houses_data["cusps"][i] % 30, 2),
                }
                for i in range(12)
            },
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def nakshatra_details(longitude: float) -> dict[str, Any]:
    """
    Get nakshatra, pada, and lord for a given longitude.

    Args:
        longitude: Sidereal longitude (0-360)

    Returns:
        Nakshatra name, number, pada, lord, and degree within nakshatra
    """
    try:
        info = longitude_to_nakshatra(longitude)
        lord = get_nakshatra_lord(info["name"])

        return {
            "longitude": round(longitude, 4),
            "nakshatra": {
                "number": info["number"],
                "name": info["name"],
                "pada": info["pada"],
                "lord": lord,
                "degree_in_nakshatra": round(info["degree_in_nakshatra"], 4),
            },
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def divisional_chart(planets: dict[str, float], division: int) -> dict[str, Any]:
    """
    Calculate divisional chart (D1-D60).

    Args:
        planets: Dictionary of planet longitudes {planet_name: longitude}
        division: Division number (1, 2, 3, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)

    Returns:
        Divisional chart positions for all planets with rashi and degree
    """
    try:
        chart_data = get_divisional_chart(planets, division)

        result = {
            "division": chart_data.get("division", division),
            "name": chart_data.get(
                "division_name", DIVISIONAL_NAMES.get(division, f"D-{division}")
            ),
            "positions": {},
        }

        # Process positions from the chart
        positions = chart_data.get("positions", {})
        for planet_name, pos_info in positions.items():
            # Get rashi info from the returned data
            rashi_num = pos_info.get("rashi", 1)
            rashi_name = pos_info.get(
                "rashi_name", RASHI_NAMES[rashi_num - 1] if 1 <= rashi_num <= 12 else "Unknown"
            )
            degree_in_sign = pos_info.get("degree_in_sign", 0)

            # Calculate longitude for consistency
            longitude = (rashi_num - 1) * 30 + degree_in_sign

            result["positions"][planet_name] = {
                "longitude": round(longitude, 4),
                "sign": rashi_name,
                "degree": round(degree_in_sign, 2),
                "rashi_number": rashi_num,
            }

        return result

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def panchanga(datetime_iso: str, latitude: float, longitude: float) -> dict[str, Any]:
    """
    Calculate complete panchanga (5 limbs of Vedic calendar).

    The panchanga consists of:
    - Tithi: Lunar day (30 tithis in a lunar month)
    - Nakshatra: Lunar mansion where Moon is positioned
    - Yoga: Angular relationship between Sun and Moon
    - Karana: Half of a tithi
    - Vara: Day of the week

    Args:
        datetime_iso: ISO format datetime
        latitude: Geographic latitude
        longitude: Geographic longitude

    Returns:
        Complete panchanga with all 5 limbs
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))

        # Get Julian day and calculate planets
        jd = get_julian_day(dt)
        planets = get_all_planets(jd)

        # Extract Sun and Moon longitudes
        sun_lon = planets["sun"]["longitude"]
        moon_lon = planets["moon"]["longitude"]

        # Calculate panchanga components
        tithi_data = get_tithi(sun_lon, moon_lon)
        yoga_data = get_yoga(sun_lon, moon_lon)
        karana_data = get_karana(tithi_data["number"])
        vara_data = get_vara(dt)
        moon_nak = longitude_to_nakshatra(moon_lon)

        # Format tithi name (Shukla/Krishna paksha are listed separately in cosmos)
        tithi_num = tithi_data.get("number", 0)
        tithi_name = TITHI_NAMES[tithi_num - 1] if 1 <= tithi_num <= 15 else "Unknown"

        # Yoga names
        yoga_num = yoga_data.get("number", 0)
        yoga_name = YOGA_NAMES[yoga_num - 1] if 1 <= yoga_num <= 27 else "Unknown"

        # Karana name (KARANA_NAMES is a dictionary)
        karana_num = karana_data.get("number", 0)
        karana_name = karana_data.get("name", "Unknown")

        # Vara name (day of week)
        vara_num = vara_data.get("number", 0)
        vara_name = VARA_NAMES[vara_num] if 0 <= vara_num < len(VARA_NAMES) else "Unknown"

        return {
            "datetime": datetime_iso,
            "location": {"latitude": latitude, "longitude": longitude},
            "tithi": {
                "number": tithi_num,
                "name": tithi_name,
                "progress": round(tithi_data.get("progress", 0), 2),
            },
            "nakshatra": {
                "number": moon_nak.get("number", 0),
                "name": moon_nak.get("name", "Unknown"),
                "pada": moon_nak.get("pada", 0),
                "lord": get_nakshatra_lord(moon_nak.get("name", "Unknown")),
                "degree_in_nakshatra": round(moon_nak.get("degree_in_nakshatra", 0), 4),
            },
            "yoga": {
                "number": yoga_num,
                "name": yoga_name,
                "progress": round(yoga_data.get("progress", 0), 2),
            },
            "karana": {"number": karana_num, "name": karana_name},
            "vara": {
                "number": vara_num,
                "name": vara_name,
                "weekday": vara_data.get("weekday", "Unknown"),
            },
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def sunrise_sunset(datetime_iso: str, latitude: float, longitude: float) -> dict[str, Any]:
    """
    Calculate sunrise and sunset times for a given date and location.

    Uses Swiss Ephemeris for accurate astronomical calculations.

    Args:
        datetime_iso: ISO format datetime (e.g., "2026-02-04T12:00:00+05:30")
        latitude: Geographic latitude (-90 to 90)
        longitude: Geographic longitude (-180 to 180)

    Returns:
        Dictionary with sunrise, sunset, day/night duration in hours

    Example:
        sunrise_sunset("2026-02-04T12:00:00+05:30", 16.726, 81.288)
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
        result = get_sunrise_sunset(dt, latitude, longitude)

        return {
            "datetime": datetime_iso,
            "location": {"latitude": latitude, "longitude": longitude},
            "sunrise": result["sunrise"].isoformat(),
            "sunset": result["sunset"].isoformat(),
            "day_duration_hours": round(result["day_duration_hours"], 2),
            "night_duration_hours": round(result["night_duration_hours"], 2),
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
def upagraha_positions(
    datetime_iso: str,
    latitude: float,
    longitude: float,
    lagna_longitude: float,
    sun_longitude: float,
) -> dict[str, Any]:
    """
    Calculate all 11 upagraha (sub-planet) positions.

    Includes time-based upagrahas (Gulika, Mandi, Yamaghanda, Kala, Mrityu,
    Ardhaprahara) and mathematical upagrahas (Dhooma, Vyatipata, Parivesha,
    Indrachapa, Upaketu).

    Args:
        datetime_iso: Birth/query datetime in ISO format
        latitude: Geographic latitude
        longitude: Geographic longitude
        lagna_longitude: Ascendant longitude (0-360)
        sun_longitude: Sun's sidereal longitude (0-360)

    Returns:
        All 11 upagraha positions with rashi, degree, house, and effects

    Example:
        upagraha_positions("1992-12-03T03:00:00+05:30", 16.726, 81.288, 180.0, 227.0)
    """
    try:
        dt = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))

        result = calculate_all_upagrahas(dt, latitude, longitude, lagna_longitude, sun_longitude)

        positions = {}
        for name, pos in result.positions.items():
            positions[name] = {
                "longitude": round(pos.longitude, 4),
                "rashi": pos.rashi.value,
                "degree_in_sign": round(pos.degree_in_sign, 2),
                "house": pos.house,
                "calculation_method": pos.calculation_method,
            }

        effects = []
        for pos in result.positions.values():
            effect = get_upagraha_effects(pos)
            effects.append(effect)

        return {
            "datetime": datetime_iso,
            "location": {"latitude": latitude, "longitude": longitude},
            "positions": positions,
            "sunrise": result.sunrise.isoformat() if result.sunrise else None,
            "sunset": result.sunset.isoformat() if result.sunset else None,
            "day_duration_hours": round(result.day_duration_hours, 2)
            if result.day_duration_hours
            else None,
            "effects": effects,
        }

    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


# Main entry point for MCP server
if __name__ == "__main__":
    mcp.run()
