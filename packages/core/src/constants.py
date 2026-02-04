"""Constants, enums, and configuration for 108 core package."""
from enum import Enum


class Planet(str, Enum):
    """Vedic planets (Grahas)."""
    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    MERCURY = "mercury"
    JUPITER = "jupiter"
    VENUS = "venus"
    SATURN = "saturn"
    RAHU = "rahu"
    KETU = "ketu"


class Rashi(str, Enum):
    """Zodiac signs (Rashis)."""
    ARIES = "aries"
    TAURUS = "taurus"
    GEMINI = "gemini"
    CANCER = "cancer"
    LEO = "leo"
    VIRGO = "virgo"
    LIBRA = "libra"
    SCORPIO = "scorpio"
    SAGITTARIUS = "sagittarius"
    CAPRICORN = "capricorn"
    AQUARIUS = "aquarius"
    PISCES = "pisces"


class HouseCategory(str, Enum):
    """Categories of houses in Vedic astrology."""
    KENDRA = "kendra"  # 1, 4, 7, 10 - quadrants
    TRIKONA = "trikona"  # 1, 5, 9 - triangles
    DUSTHANA = "dusthana"  # 6, 8, 12 - evil houses
    UPACHAYA = "upachaya"  # 3, 6, 10, 11 - growth houses
    MARAKA = "maraka"  # 2, 7 - death-inflicting houses


class Gana(str, Enum):
    """Nakshatra Gana (nature/temperament)."""
    DEVA = "deva"  # Divine/benevolent
    MANUSHYA = "manushya"  # Human/balanced
    RAKSHASA = "rakshasa"  # Demonic/fierce


class YogaCategory(str, Enum):
    """Categories of yogas (planetary combinations)."""
    PANCHA_MAHAPURUSHA = "pancha_mahapurusha"  # Five great-person yogas
    RAJA = "raja"  # Royal yogas
    DHANA = "dhana"  # Wealth yogas
    ARISHTA = "arishta"  # Misery yogas
    CHANDRA = "chandra"  # Moon-related yogas
    SURYA = "surya"  # Sun-related yogas
    NABHASA = "nabhasa"  # Planetary configuration yogas
    OTHER = "other"


class AyanamsaType(str, Enum):
    """Ayanamsa (precession correction) systems."""
    LAHIRI = "lahiri"  # Most commonly used in Indian astrology
    RAMAN = "raman"
    KRISHNAMURTI = "krishnamurti"


class HouseSystem(str, Enum):
    """House calculation systems."""
    PLACIDUS = "placidus"
    WHOLE_SIGN = "whole_sign"
    EQUAL = "equal"
    KOCH = "koch"


# Vimshottari Dasha planetary period years
DASHA_YEARS = {
    Planet.KETU: 7,
    Planet.VENUS: 20,
    Planet.SUN: 6,
    Planet.MOON: 10,
    Planet.MARS: 7,
    Planet.RAHU: 18,
    Planet.JUPITER: 16,
    Planet.SATURN: 19,
    Planet.MERCURY: 17,
}

# Dasha sequence (starting from Ketu)
DASHA_SEQUENCE = [
    Planet.KETU,
    Planet.VENUS,
    Planet.SUN,
    Planet.MOON,
    Planet.MARS,
    Planet.RAHU,
    Planet.JUPITER,
    Planet.SATURN,
    Planet.MERCURY,
]

# Total Vimshottari cycle duration in years
TOTAL_DASHA_YEARS = 120

# Nakshatra span in degrees (13°20')
NAKSHATRA_SPAN = 13.333333333

# Pada (quarter) span in degrees (3°20')
PADA_SPAN = 3.333333333
