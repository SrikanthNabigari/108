"""Constants, enums, and configuration for 108 core package."""

from enum import StrEnum


class Planet(StrEnum):
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


class Rashi(StrEnum):
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


class HouseCategory(StrEnum):
    """Categories of houses in Vedic astrology."""

    KENDRA = "kendra"  # 1, 4, 7, 10 - quadrants
    TRIKONA = "trikona"  # 1, 5, 9 - triangles
    DUSTHANA = "dusthana"  # 6, 8, 12 - evil houses
    UPACHAYA = "upachaya"  # 3, 6, 10, 11 - growth houses
    MARAKA = "maraka"  # 2, 7 - death-inflicting houses


class Gana(StrEnum):
    """Nakshatra Gana (nature/temperament)."""

    DEVA = "deva"  # Divine/benevolent
    MANUSHYA = "manushya"  # Human/balanced
    RAKSHASA = "rakshasa"  # Demonic/fierce


class YogaCategory(StrEnum):
    """Categories of yogas (planetary combinations)."""

    PANCHA_MAHAPURUSHA = "pancha_mahapurusha"  # Five great-person yogas
    RAJA = "raja"  # Royal yogas
    DHANA = "dhana"  # Wealth yogas
    ARISHTA = "arishta"  # Misery yogas
    CHANDRA = "chandra"  # Moon-related yogas
    SURYA = "surya"  # Sun-related yogas
    NABHASA = "nabhasa"  # Planetary configuration yogas
    NABHAS = "nabhas"  # Nabhas yogas (alternate spelling in rules)
    SPECIAL = "special"  # Special/miscellaneous yogas
    OTHER = "other"
    DARIDRA = "daridra"  # Poverty yogas
    DASHA = "dasha"  # Dasha-triggered yogas
    NAKSHATRA = "nakshatra"  # Nakshatra-based yogas
    NEECHA_BHANGA = "neecha_bhanga"  # Debilitation cancellation yogas
    PARIVARTANA = "parivartana"  # Mutual exchange yogas
    SANYASA = "sanyasa"  # Renunciation yogas
    TRANSIT = "transit"  # Transit-activated yogas
    VIPARITA_RAJA = "viparita_raja"  # Reversal of fortune yogas


class AyanamsaType(StrEnum):
    """Ayanamsa (precession correction) systems."""

    LAHIRI = "lahiri"  # Most commonly used in Indian astrology
    RAMAN = "raman"
    KRISHNAMURTI = "krishnamurti"


class HouseSystem(StrEnum):
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


class CharaKaraka(StrEnum):
    """Jaimini Chara (movable) Karakas - determined by degree in sign."""

    ATMAKARAKA = "atmakaraka"  # AK - highest degree planet
    AMATYAKARAKA = "amatyakaraka"  # AmK - 2nd highest
    BHRATRIKARAKA = "bhratrikaraka"  # BK - 3rd highest
    MATRIKARAKA = "matrikaraka"  # MK - 4th highest
    PUTRAKARAKA = "putrakaraka"  # PK - 5th highest
    GNATIKARAKA = "gnatikaraka"  # GK - 6th highest
    DARAKARAKA = "darakaraka"  # DK - lowest degree


class SignMobility(StrEnum):
    """Jaimini sign classification by mobility."""

    MOVABLE = "movable"  # Aries, Cancer, Libra, Capricorn
    FIXED = "fixed"  # Taurus, Leo, Scorpio, Aquarius
    DUAL = "dual"  # Gemini, Virgo, Sagittarius, Pisces


class DashaSystem(StrEnum):
    """Dasha calculation systems."""

    VIMSHOTTARI = "vimshottari"
    YOGINI = "yogini"
    NARAYANA = "narayana"
    CHARA = "chara"


class YoginiName(StrEnum):
    """Eight Yogini names for Yogini Dasha system."""

    MANGALA = "mangala"  # 1yr, Moon
    PINGALA = "pingala"  # 2yr, Sun
    DHANYA = "dhanya"  # 3yr, Jupiter
    BHRAMARI = "bhramari"  # 4yr, Mars
    BHADRIKA = "bhadrika"  # 5yr, Mercury
    ULKA = "ulka"  # 6yr, Saturn
    SIDDHA = "siddha"  # 7yr, Venus
    SANKATA = "sankata"  # 8yr, Rahu


class PrashnaCategory(StrEnum):
    """Question categories for Prashna (Horary) astrology."""

    HEALTH = "health"
    MARRIAGE = "marriage"
    CAREER = "career"
    TRAVEL = "travel"
    LOST_OBJECTS = "lost_objects"
    LEGAL = "legal"
    SPIRITUAL = "spiritual"
    CHILDREN = "children"
    WEALTH = "wealth"
    EDUCATION = "education"


class PrashnaJudgment(StrEnum):
    """Judgment outcomes for Prashna analysis."""

    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"
    DELAYED = "delayed"


class Upagraha(StrEnum):
    """Sub-planets (Upagrahas) used in Vedic astrology."""

    GULIKA = "gulika"  # Saturn's day portion
    MANDI = "mandi"  # End of Saturn's portion
    YAMAGHANDA = "yamaghanda"  # Jupiter's portion (some: Mars)
    KALA = "kala"  # Sun's portion
    MRITYU = "mrityu"  # Mars-based death point
    ARDHAPRAHARA = "ardhaprahara"  # Half-prahar
    DHOOMA = "dhooma"  # Sun + 133°20'
    VYATIPATA = "vyatipata"  # 360 - Dhooma
    PARIVESHA = "parivesha"  # 180 + Vyatipata
    INDRACHAPA = "indrachapa"  # 360 - Parivesha
    UPAKETU = "upaketu"  # Sun - 30°
