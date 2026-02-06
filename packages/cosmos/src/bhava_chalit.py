"""Bhava Chalit (house-cusp-based) chart calculations for Vedic Astrology.

In the Rashi chart, planets are placed by zodiac sign (whole-sign houses).
In the Bhava Chalit chart, planets are placed by actual house cusp degree
ranges. A planet near a cusp boundary may shift to an adjacent house.

This is important because a planet's Rashi-chart house placement tells us
about sign-based results, while Bhava Chalit tells us about actual house-based
results (bhava phala).

References: BPHS, Saravali, Jataka Parijata
"""

import logging

logger = logging.getLogger(__name__)


def _normalize_longitude(lon: float) -> float:
    """Normalize longitude to 0-360 range."""
    return lon % 360.0


def _rashi_house(longitude: float, ascendant: float) -> int:
    """Calculate whole-sign house from longitude and ascendant.

    In whole-sign house system, the sign containing the ascendant is
    house 1, the next sign is house 2, etc.
    """
    asc_sign = int(_normalize_longitude(ascendant) / 30)
    planet_sign = int(_normalize_longitude(longitude) / 30)
    return ((planet_sign - asc_sign) % 12) + 1


def _cusp_house(longitude: float, cusps: list[float]) -> int:
    """Determine which Bhava Chalit house a longitude falls into.

    Uses the midpoints between consecutive cusps as house boundaries.
    The cusp of house N is the center of house N, so the boundaries
    are midpoints between consecutive cusps.

    Args:
        longitude: Planet's sidereal longitude (0-360)
        cusps: List of 12 house cusp longitudes (0-360)

    Returns:
        House number (1-12)
    """
    lon = _normalize_longitude(longitude)

    # Calculate midpoints between consecutive cusps
    # Midpoint between cusp[i] and cusp[i+1] is the boundary between house i and house i+1
    midpoints = []
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]

        if c2 < c1:
            # Wraps around 360
            mid = (c1 + c2 + 360) / 2.0
            if mid >= 360:
                mid -= 360
        else:
            mid = (c1 + c2) / 2.0

        midpoints.append(_normalize_longitude(mid))

    # Find which house the longitude falls into
    # A planet is in house N if it's between midpoint[N-1] and midpoint[N]
    for i in range(12):
        prev_mid = midpoints[(i - 1) % 12] if i > 0 else midpoints[11]
        curr_mid = midpoints[i]

        if curr_mid < prev_mid:
            # Wraps around 360
            if lon >= prev_mid or lon < curr_mid:
                return i + 1
        else:
            if prev_mid <= lon < curr_mid:
                return i + 1

    # Fallback
    return 1


def calculate_bhava_chalit(
    planets: dict,
    cusps: dict | list,
    ascendant: float,
) -> dict:
    """Calculate Bhava Chalit chart, comparing Rashi and cusp-based house placements.

    In the Rashi chart, houses are determined by whole-sign (sign = house).
    In the Bhava Chalit, houses are determined by actual cusp degree ranges,
    so planets near a house cusp boundary may shift to an adjacent house.

    Args:
        planets: Dictionary of planet positions. Keys are planet names (str)
                 or Planet enums. Values should have a 'longitude' attribute/key.
        cusps: Either a list of 12 cusp longitudes, or a dict with a 'cusps'
               key containing such a list. Cusps should be 0-360 degrees.
        ascendant: Ascendant (Lagna) longitude in degrees (0-360).

    Returns:
        Dictionary mapping planet names to:
        - rashi_house (int): House in whole-sign (Rashi) chart
        - bhava_chalit_house (int): House in Bhava Chalit chart
        - shifted (bool): Whether the planet shifted houses
    """
    # Normalize cusps input
    if isinstance(cusps, dict):
        cusp_list = cusps.get("cusps", [])
    elif isinstance(cusps, list):
        cusp_list = cusps
    elif hasattr(cusps, "cusps"):
        cusp_list = cusps.cusps
    else:
        logger.warning("Invalid cusps format, returning empty result")
        return {}

    if len(cusp_list) != 12:
        logger.warning(f"Expected 12 cusps, got {len(cusp_list)}")
        return {}

    result = {}

    for planet_key, planet_data in planets.items():
        # Extract longitude
        if isinstance(planet_data, dict):
            lon = planet_data.get("longitude", 0.0)
        elif hasattr(planet_data, "longitude"):
            lon = planet_data.longitude
        else:
            continue

        # Get planet name as string
        name = planet_key.value if hasattr(planet_key, "value") else str(planet_key)

        rashi_h = _rashi_house(lon, ascendant)
        chalit_h = _cusp_house(lon, cusp_list)

        result[name] = {
            "rashi_house": rashi_h,
            "bhava_chalit_house": chalit_h,
            "shifted": rashi_h != chalit_h,
        }

    return result


def get_shifted_planets(bhava_chalit: dict) -> list[dict]:
    """Get only the planets that shifted houses between Rashi and Bhava Chalit.

    Args:
        bhava_chalit: Output from calculate_bhava_chalit()

    Returns:
        List of dicts for shifted planets, each containing:
        - planet (str): Planet name
        - rashi_house (int): House in Rashi chart
        - bhava_chalit_house (int): House in Bhava Chalit chart
        - description (str): Human-readable description of the shift
    """
    shifted = []

    for planet_name, data in bhava_chalit.items():
        if data.get("shifted", False):
            rh = data["rashi_house"]
            ch = data["bhava_chalit_house"]
            shifted.append(
                {
                    "planet": planet_name,
                    "rashi_house": rh,
                    "bhava_chalit_house": ch,
                    "description": (
                        f"{planet_name.title()} shifts from house {rh} (Rashi) "
                        f"to house {ch} (Bhava Chalit)"
                    ),
                }
            )

    return shifted
