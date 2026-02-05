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

from .divisional import (
    DIVISIONAL_NAMES,
    ELEMENT_MAP,
    # Constants
    RASHI_NAMES,
    DivisionalChart,
    # Type definitions
    DivisionalPosition,
    VargaStrength,
    get_akshavedamsha,
    get_bhamsha,
    get_chaturthamsha,
    get_chaturvimshamsha,
    # Core divisional position functions
    get_d1_position,
    get_dashamsha,
    get_divisional_chart,
    # Dispatcher functions
    get_divisional_position,
    get_drekkana,
    get_dwadashamsha,
    get_hora,
    get_khavedamsha,
    get_navamsha,
    get_saptamsha,
    get_shashtiamsha,
    get_shodashamsha,
    get_trimshamsha,
    get_varga_vimshopaka,
    get_vimshamsha,
)
from .ephemeris import (
    AYANAMSA_MAP,
    HOUSE_SYSTEM_MAP,
    # Constants
    PLANET_MAP,
    close_ephemeris,
    datetime_to_jd,
    get_all_planets,
    get_ascendant,
    get_ayanamsa,
    get_house_cusps,
    # Core functions
    get_julian_day,
    get_planet_position,
)
from .houses import (
    get_all_planets_by_house,
    get_house_analysis,
    get_house_categories,
    get_house_category,
    # Core BUILD_SPEC functions
    get_house_for_longitude,
    get_house_from_reference,
    get_house_karaka,
    get_house_lord,
    # Additional house functions
    get_house_significations,
    get_kendras_from,
    get_planets_in_house,
    get_trinal_houses,
    is_benefic_house,
)
from .nakshatras import (
    # Type definitions
    NakshatraResult,
    PadaNavamshaResult,
    TarabalaResult,
    get_all_nakshatras,
    get_nakshatra_lord,
    # Utility functions
    get_nakshatra_name_by_number,
    get_nakshatra_number_by_name,
    get_pada_navamsha,
    get_tarabala,
    # Core functions
    longitude_to_nakshatra,
    validate_nakshatra_name,
)
from .panchanga import (
    KARANA_NAMES,
    # Constants
    TITHI_NAMES,
    VARA_NAMES,
    YOGA_NAMES,
    get_karana,
    # Additional panchanga functions
    get_karana_advanced,
    get_panchanga,
    # Core BUILD_SPEC functions
    get_tithi,
    get_vara,
    get_yoga,
)

__all__ = [
    "AYANAMSA_MAP",
    "DIVISIONAL_NAMES",
    "ELEMENT_MAP",
    "HOUSE_SYSTEM_MAP",
    "KARANA_NAMES",
    # Ephemeris constants
    "PLANET_MAP",
    # Divisional chart constants
    "RASHI_NAMES",
    # Panchanga constants
    "TITHI_NAMES",
    "VARA_NAMES",
    "YOGA_NAMES",
    "DivisionalChart",
    # Divisional chart type definitions
    "DivisionalPosition",
    # Nakshatra type definitions
    "NakshatraResult",
    "PadaNavamshaResult",
    "TarabalaResult",
    "VargaStrength",
    "close_ephemeris",
    "datetime_to_jd",
    "get_akshavedamsha",
    "get_all_nakshatras",
    "get_all_planets",
    "get_all_planets_by_house",
    "get_ascendant",
    "get_ayanamsa",
    "get_bhamsha",
    "get_chaturthamsha",
    "get_chaturvimshamsha",
    # Divisional chart functions (D1-D60)
    "get_d1_position",
    "get_dashamsha",
    "get_divisional_chart",
    # Divisional chart dispatcher functions
    "get_divisional_position",
    "get_drekkana",
    "get_dwadashamsha",
    "get_hora",
    "get_house_analysis",
    "get_house_categories",
    "get_house_category",
    "get_house_cusps",
    # House functions
    "get_house_for_longitude",
    "get_house_from_reference",
    "get_house_karaka",
    "get_house_lord",
    "get_house_significations",
    # Ephemeris functions
    "get_julian_day",
    "get_karana",
    "get_karana_advanced",
    "get_kendras_from",
    "get_khavedamsha",
    "get_nakshatra_lord",
    # Nakshatra utility functions
    "get_nakshatra_name_by_number",
    "get_nakshatra_number_by_name",
    "get_navamsha",
    "get_pada_navamsha",
    "get_panchanga",
    "get_planet_position",
    "get_planets_in_house",
    "get_saptamsha",
    "get_shashtiamsha",
    "get_shodashamsha",
    "get_tarabala",
    # Panchanga functions
    "get_tithi",
    "get_trimshamsha",
    "get_trinal_houses",
    "get_vara",
    "get_varga_vimshopaka",
    "get_vimshamsha",
    "get_yoga",
    "is_benefic_house",
    # Nakshatra functions
    "longitude_to_nakshatra",
    "validate_nakshatra_name",
]

__version__ = "2.0.0"
__package_name__ = "one-zero-eight-cosmos"
