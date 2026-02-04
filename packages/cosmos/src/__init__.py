"""108 cosmos package - ephemeris calculations for Vedic astrology.

This package provides Swiss Ephemeris-based calculations for planetary positions,
house cusps, nakshatras, and divisional charts (vargas) needed for Vedic astrology.

All positions are calculated in the sidereal/Vedic zodiac using Lahiri ayanamsa
by default, though other ayanamsa systems are supported.

Main Modules:
    - ephemeris: Planetary positions, house cusps, and time calculations
    - nakshatras: Lunar mansion (27 nakshatras) calculations
    - divisional: Divisional charts (D1-D60) for detailed analysis

Main Ephemeris Functions:
    - get_julian_day(): Convert datetime to Julian Day Number
    - get_ayanamsa(): Get precession correction for a given date
    - get_planet_position(): Calculate sidereal position of a planet
    - get_all_planets(): Calculate positions of all 9 Vedic planets
    - get_house_cusps(): Calculate house cusps and angles
    - get_ascendant(): Get the Ascendant (Lagna) for a location/time

Main Nakshatra Functions:
    - longitude_to_nakshatra(): Find nakshatra from longitude
    - get_nakshatra_lord(): Get Vimshottari lord of nakshatra
    - get_pada_navamsha(): Calculate pada Navamsha position

Main Divisional Chart Functions:
    - get_navamsha(): D9 (most important - marriage, dharma)
    - get_divisional_chart(): Get full divisional chart for all planets
    - get_divisional_position(): Get position in any D1-D60 chart
    - get_varga_vimshopaka(): Strength across multiple vargas

Constants:
    - PLANET_MAP: Swiss Ephemeris planet IDs
    - AYANAMSA_MAP: Supported ayanamsa systems
    - HOUSE_SYSTEM_MAP: Supported house systems
    - RASHI_NAMES: Names of 12 zodiacal signs
    - DIVISIONAL_NAMES: Names of all divisional charts

Example:
    >>> from cosmos import get_all_planets, get_house_cusps, get_julian_day, get_navamsha
    >>> from datetime import datetime
    >>>
    >>> # Calculate planetary positions for a specific date/time
    >>> dt = datetime(2000, 1, 1, 12, 0, 0)
    >>> jd = get_julian_day(dt)
    >>> planets = get_all_planets(jd)
    >>> houses = get_house_cusps(jd, 12.9716, 77.5946)  # Delhi coordinates
    >>>
    >>> # Get D9 (Navamsha) positions
    >>> navamsha_sun = get_navamsha(planets['sun']['longitude'])
    >>> navamsha_chart = get_divisional_chart(planets, 9)
    >>>
    >>> print(f"Sun in {planets['sun']['longitude']:.2f}°")
    >>> print(f"Sun in Navamsha: {navamsha_sun['rashi_name']}")
"""

from .ephemeris import (
    # Core functions
    get_julian_day,
    get_ayanamsa,
    get_planet_position,
    get_all_planets,
    get_house_cusps,
    get_ascendant,
    datetime_to_jd,
    close_ephemeris,
    # Constants
    PLANET_MAP,
    AYANAMSA_MAP,
    HOUSE_SYSTEM_MAP,
)

from .nakshatras import (
    # Core functions
    longitude_to_nakshatra,
    get_nakshatra_lord,
    get_pada_navamsha,
    get_tarabala,
    # Utility functions
    get_nakshatra_name_by_number,
    get_nakshatra_number_by_name,
    get_all_nakshatras,
    validate_nakshatra_name,
    # Type definitions
    NakshatraResult,
    PadaNavamshaResult,
    TarabalaResult,
)

from .divisional import (
    # Core divisional position functions
    get_d1_position,
    get_hora,
    get_drekkana,
    get_chaturthamsha,
    get_saptamsha,
    get_navamsha,
    get_dashamsha,
    get_dwadashamsha,
    get_shodashamsha,
    get_vimshamsha,
    get_chaturvimshamsha,
    get_bhamsha,
    get_trimshamsha,
    get_khavedamsha,
    get_akshavedamsha,
    get_shashtiamsha,
    # Dispatcher functions
    get_divisional_position,
    get_divisional_chart,
    get_varga_vimshopaka,
    # Type definitions
    DivisionalPosition,
    DivisionalChart,
    VargaStrength,
    # Constants
    RASHI_NAMES,
    ELEMENT_MAP,
    DIVISIONAL_NAMES,
)

from .houses import (
    # Core BUILD_SPEC functions
    get_house_for_longitude,
    get_house_lord,
    get_planets_in_house,
    get_house_from_reference,
    # Additional house functions
    get_house_significations,
    get_house_karaka,
    is_benefic_house,
    get_house_category,
    get_trinal_houses,
    get_kendras_from,
    get_house_categories,
    get_all_planets_by_house,
    get_house_analysis,
)

from .panchanga import (
    # Core BUILD_SPEC functions
    get_tithi,
    get_yoga,
    get_karana,
    get_vara,
    get_panchanga,
    # Additional panchanga functions
    get_karana_advanced,
    # Constants
    TITHI_NAMES,
    YOGA_NAMES,
    KARANA_NAMES,
    VARA_NAMES,
)

__all__ = [
    # Ephemeris functions
    "get_julian_day",
    "get_ayanamsa",
    "get_planet_position",
    "get_all_planets",
    "get_house_cusps",
    "get_ascendant",
    "datetime_to_jd",
    "close_ephemeris",
    # Ephemeris constants
    "PLANET_MAP",
    "AYANAMSA_MAP",
    "HOUSE_SYSTEM_MAP",
    # Nakshatra functions
    "longitude_to_nakshatra",
    "get_nakshatra_lord",
    "get_pada_navamsha",
    "get_tarabala",
    # Nakshatra utility functions
    "get_nakshatra_name_by_number",
    "get_nakshatra_number_by_name",
    "get_all_nakshatras",
    "validate_nakshatra_name",
    # Nakshatra type definitions
    "NakshatraResult",
    "PadaNavamshaResult",
    "TarabalaResult",
    # Divisional chart functions (D1-D60)
    "get_d1_position",
    "get_hora",
    "get_drekkana",
    "get_chaturthamsha",
    "get_saptamsha",
    "get_navamsha",
    "get_dashamsha",
    "get_dwadashamsha",
    "get_shodashamsha",
    "get_vimshamsha",
    "get_chaturvimshamsha",
    "get_bhamsha",
    "get_trimshamsha",
    "get_khavedamsha",
    "get_akshavedamsha",
    "get_shashtiamsha",
    # Divisional chart dispatcher functions
    "get_divisional_position",
    "get_divisional_chart",
    "get_varga_vimshopaka",
    # Divisional chart type definitions
    "DivisionalPosition",
    "DivisionalChart",
    "VargaStrength",
    # Divisional chart constants
    "RASHI_NAMES",
    "ELEMENT_MAP",
    "DIVISIONAL_NAMES",
    # House functions
    "get_house_for_longitude",
    "get_house_lord",
    "get_planets_in_house",
    "get_house_from_reference",
    "get_house_significations",
    "get_house_karaka",
    "is_benefic_house",
    "get_house_category",
    "get_trinal_houses",
    "get_kendras_from",
    "get_house_categories",
    "get_all_planets_by_house",
    "get_house_analysis",
    # Panchanga functions
    "get_tithi",
    "get_yoga",
    "get_karana",
    "get_vara",
    "get_panchanga",
    "get_karana_advanced",
    # Panchanga constants
    "TITHI_NAMES",
    "YOGA_NAMES",
    "KARANA_NAMES",
    "VARA_NAMES",
]

__version__ = "2.0.0"
__package_name__ = "one-zero-eight-cosmos"
