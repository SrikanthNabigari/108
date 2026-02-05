"""Pydantic models for 108 core package."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .constants import (
    CharaKaraka,
    Planet,
    PrashnaCategory,
    PrashnaJudgment,
    Rashi,
    Upagraha,
    YogaCategory,
    YoginiName,
)


class BirthData(BaseModel):
    """Birth information for chart calculation."""

    datetime_utc: datetime = Field(description="Birth datetime in UTC timezone")
    latitude: float = Field(ge=-90, le=90, description="Geographic latitude (-90 to 90)")
    longitude: float = Field(ge=-180, le=180, description="Geographic longitude (-180 to 180)")
    timezone: str = Field(description="IANA timezone identifier (e.g., 'UTC', 'Asia/Kolkata')")
    place_name: str | None = Field(default=None, description="Name of birth location")

    model_config = {
        "json_schema_extra": {
            "example": {
                "datetime_utc": "1990-05-15T12:00:00Z",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timezone": "Asia/Kolkata",
                "place_name": "Delhi, India",
            }
        }
    }


class PlanetPosition(BaseModel):
    """Position of a planet in the birth chart."""

    planet: Planet = Field(description="Planet identifier")
    longitude: float = Field(ge=0, lt=360, description="Ecliptic longitude (0-360 degrees)")
    latitude: float = Field(default=0.0, description="Ecliptic latitude (declination)")
    speed: float = Field(default=0.0, description="Daily motion in degrees")
    rashi: Rashi = Field(description="Zodiac sign")
    rashi_degree: float = Field(ge=0, lt=30, description="Degree within the rashi (0-30)")
    nakshatra: str = Field(description="Lunar mansion name")
    nakshatra_pada: int = Field(ge=1, le=4, description="Quarter within the nakshatra (1-4)")
    nakshatra_lord: Planet = Field(description="Planet ruling this nakshatra")
    is_retrograde: bool = Field(default=False, description="Whether planet is retrograde")
    house: int = Field(ge=1, le=12, description="House number (1-12)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "planet": "sun",
                "longitude": 52.5,
                "latitude": 0.0,
                "speed": 1.0,
                "rashi": "taurus",
                "rashi_degree": 22.5,
                "nakshatra": "krittika",
                "nakshatra_pada": 1,
                "nakshatra_lord": "sun",
                "is_retrograde": False,
                "house": 10,
            }
        }
    }


class HouseCusps(BaseModel):
    """House cusps and important angles in the chart."""

    ascendant: float = Field(ge=0, lt=360, description="Ascendant (Lagna) longitude")
    mc: float = Field(ge=0, lt=360, description="Midheaven (MC) longitude")
    cusps: list[float] = Field(min_length=12, max_length=12, description="Cusps of all 12 houses")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ascendant": 15.0,
                "mc": 285.0,
                "cusps": [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345],
            }
        }
    }


class NakshatraInfo(BaseModel):
    """Detailed information about a nakshatra (lunar mansion)."""

    number: int = Field(ge=1, le=27, description="Nakshatra number (1-27)")
    name: str = Field(description="Nakshatra name")
    pada: int = Field(ge=1, le=4, description="Quarter within nakshatra (1-4)")
    lord: Planet = Field(description="Ruling planet")
    degree_in_nakshatra: float = Field(
        ge=0, lt=13.333334, description="Degree within the nakshatra"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "number": 1,
                "name": "ashwini",
                "pada": 1,
                "lord": "ketu",
                "degree_in_nakshatra": 2.5,
            }
        }
    }


class BirthChart(BaseModel):
    """Complete natal birth chart with all calculated positions."""

    user_id: str = Field(description="User identifier")
    birth_data: BirthData = Field(description="Birth location and time data")
    planets: dict[Planet, PlanetPosition] = Field(
        description="Dictionary of planet positions keyed by planet enum"
    )
    houses: HouseCusps = Field(description="House cusps and angles")
    lagna_rashi: Rashi = Field(description="Ascendant (Lagna) rashi")
    moon_rashi: Rashi = Field(description="Moon sign (Chandra Rashi)")
    moon_nakshatra: str = Field(description="Moon's nakshatra")
    ayanamsa: float = Field(description="Applied ayanamsa correction in degrees")
    calculated_at: datetime = Field(description="Calculation timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user123",
                "birth_data": {
                    "datetime_utc": "1990-05-15T12:00:00Z",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata",
                    "place_name": "Delhi, India",
                },
                "planets": {},
                "houses": {
                    "ascendant": 15.0,
                    "mc": 285.0,
                    "cusps": [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345],
                },
                "lagna_rashi": "aries",
                "moon_rashi": "cancer",
                "moon_nakshatra": "pushya",
                "ayanamsa": 23.45,
                "calculated_at": "2024-02-04T10:00:00Z",
            }
        }
    }


class DetectedYoga(BaseModel):
    """A yoga (planetary combination) detected in the chart."""

    yoga_id: str = Field(description="Unique yoga identifier")
    name: str = Field(description="Yoga name")
    category: YogaCategory = Field(description="Category of yoga")
    is_present: bool = Field(default=True, description="Whether yoga is present in chart")
    strength: float = Field(ge=0, le=1, default=1.0, description="Strength factor (0-1)")
    involved_planets: list[Planet] = Field(
        default_factory=list, description="Planets involved in yoga"
    )
    description: str = Field(default="", description="Interpretation and significance")

    model_config = {
        "json_schema_extra": {
            "example": {
                "yoga_id": "raja_yoga_001",
                "name": "Gaj Kesari Yoga",
                "category": "raja",
                "is_present": True,
                "strength": 0.8,
                "involved_planets": ["jupiter", "moon"],
                "description": "Indicates prosperity and intelligence",
            }
        }
    }


class DetectedDosha(BaseModel):
    """A dosha (affliction/challenge) detected in the chart."""

    dosha_id: str = Field(description="Unique dosha identifier")
    name: str = Field(description="Dosha name")
    is_present: bool = Field(default=True, description="Whether dosha is present")
    severity: str = Field(default="moderate", description="Severity level (mild, moderate, severe)")
    involved_planets: list[Planet] = Field(default_factory=list, description="Planets involved")
    description: str = Field(default="", description="Explanation of the dosha")
    remedies: list[str] = Field(default_factory=list, description="Suggested remedial measures")

    model_config = {
        "json_schema_extra": {
            "example": {
                "dosha_id": "mangal_dosha_001",
                "name": "Mangal Dosha",
                "is_present": True,
                "severity": "mild",
                "involved_planets": ["mars"],
                "description": "Mars is in 7th from Moon",
                "remedies": ["Chant Mangala Stotram", "Donate red items"],
            }
        }
    }


class DashaPeriod(BaseModel):
    """A dasha (planetary period) in the Vimshottari system."""

    lord: Planet = Field(description="Ruling planet of this dasha")
    start_date: datetime = Field(description="Start date of dasha period")
    end_date: datetime = Field(description="End date of dasha period")
    level: str = Field(description="Level of dasha (maha, antar, pratyantar)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "lord": "jupiter",
                "start_date": "2024-01-15T00:00:00Z",
                "end_date": "2040-01-15T00:00:00Z",
                "level": "maha",
            }
        }
    }


class CurrentDasha(BaseModel):
    """Current active dasha periods for a native."""

    mahadasha: DashaPeriod = Field(description="Current major dasha")
    antardasha: DashaPeriod = Field(description="Current sub-dasha")
    pratyantardasha: DashaPeriod | None = Field(
        default=None, description="Current sub-sub-dasha (if applicable)"
    )
    days_remaining_in_antar: int = Field(description="Days remaining in current antardasha")

    model_config = {
        "json_schema_extra": {
            "example": {
                "mahadasha": {
                    "lord": "jupiter",
                    "start_date": "2024-01-15T00:00:00Z",
                    "end_date": "2040-01-15T00:00:00Z",
                    "level": "maha",
                },
                "antardasha": {
                    "lord": "mercury",
                    "start_date": "2024-01-15T00:00:00Z",
                    "end_date": "2025-06-15T00:00:00Z",
                    "level": "antar",
                },
                "days_remaining_in_antar": 131,
            }
        }
    }


class Panchanga(BaseModel):
    """Five limbs of the Vedic calendar (Panchanga)."""

    tithi: dict[str, Any] = Field(description="Lunar day - number, name, paksha (phase)")
    nakshatra: dict[str, Any] = Field(description="Lunar mansion - name, pada, lord")
    yoga: dict[str, Any] = Field(description="Planetary union - number, name")
    karana: dict[str, Any] = Field(description="Half-tithi - number, name")
    vara: dict[str, Any] = Field(description="Weekday - day name, ruling planet")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tithi": {"number": 7, "name": "Saptami", "paksha": "Shukla"},
                "nakshatra": {"name": "Pushya", "pada": 2, "lord": "saturn"},
                "yoga": {"number": 15, "name": "Ayushman"},
                "karana": {"number": 13, "name": "Vanija"},
                "vara": {"weekday": "Tuesday", "lord": "mars"},
            }
        }
    }


class TransitPosition(BaseModel):
    """Transit planet position for predictions."""

    planet: Planet = Field(description="Planet identifier")
    longitude: float = Field(ge=0, lt=360, description="Current longitude (0-360)")
    rashi: Rashi = Field(description="Current rashi")
    nakshatra: str = Field(description="Current nakshatra")
    is_retrograde: bool = Field(default=False, description="Whether planet is retrograde")

    model_config = {
        "json_schema_extra": {
            "example": {
                "planet": "saturn",
                "longitude": 125.5,
                "rashi": "leo",
                "nakshatra": "magha",
                "is_retrograde": False,
            }
        }
    }


class UserProfile(BaseModel):
    """User profile containing birth data and chart interpretation."""

    user_id: str = Field(description="Unique user identifier")
    name: str | None = Field(default=None, description="User's name")
    email: str | None = Field(default=None, description="User's email address")
    birth_data: BirthData = Field(description="Birth location and time")
    birth_chart: BirthChart | None = Field(default=None, description="Calculated birth chart")
    detected_yogas: list[DetectedYoga] = Field(
        default_factory=list, description="List of detected yogas"
    )
    detected_doshas: list[DetectedDosha] = Field(
        default_factory=list, description="List of detected doshas"
    )
    personality_type: str | None = Field(
        default=None, description="Astrological personality classification"
    )
    preferences: dict[str, Any] = Field(
        default_factory=dict, description="User preferences and settings"
    )
    created_at: datetime = Field(description="Profile creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "user123",
                "name": "John Doe",
                "email": "john@example.com",
                "birth_data": {
                    "datetime_utc": "1990-05-15T12:00:00Z",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata",
                    "place_name": "Delhi, India",
                },
                "birth_chart": None,
                "detected_yogas": [],
                "detected_doshas": [],
                "personality_type": "Pitta",
                "preferences": {"language": "en", "theme": "light"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-02-04T10:00:00Z",
            }
        }
    }


# ===================
# Jaimini System Models
# ===================


class CharaKarakaResult(BaseModel):
    """Result of Chara Karaka calculation for one planet."""

    karaka: CharaKaraka = Field(description="Chara Karaka designation")
    planet: Planet = Field(description="Planet assigned this karaka")
    degree_in_sign: float = Field(ge=0, lt=30, description="Degree within sign")
    rashi: Rashi = Field(description="Sign the planet occupies")


class ArudhaPada(BaseModel):
    """Arudha Pada position for a house."""

    house_number: int = Field(ge=1, le=12, description="House number (1-12)")
    rashi: Rashi = Field(description="Sign where the pada falls")
    house_lord: Planet = Field(description="Lord of the house")
    calculation_note: str = Field(default="", description="Note about calculation")


class CharaDashaPeriod(BaseModel):
    """One period in the Chara Dasha system."""

    rashi: Rashi = Field(description="Dasha sign")
    start_date: datetime = Field(description="Period start date")
    end_date: datetime = Field(description="Period end date")
    duration_years: int = Field(ge=1, le=12, description="Duration in years")


class KarakamshaResult(BaseModel):
    """Result of Karakamsha analysis."""

    atmakaraka: Planet = Field(description="Atmakaraka planet")
    navamsha_rashi: Rashi = Field(description="AK's Navamsha sign position")
    planets_in_karakamsha: list[Planet] = Field(
        default_factory=list, description="Planets in karakamsha sign"
    )
    interpretation: str = Field(default="", description="Karakamsha interpretation")


# ===================
# Alternative Dasha Models
# ===================


class YoginiDashaPeriod(BaseModel):
    """One period in the Yogini Dasha system."""

    yogini: YoginiName = Field(description="Yogini name")
    planet_lord: Planet = Field(description="Planet lord of this yogini")
    start_date: datetime = Field(description="Period start date")
    end_date: datetime = Field(description="Period end date")
    duration_years: int = Field(ge=1, le=8, description="Duration in years")


class NarayanaDashaPeriod(BaseModel):
    """One period in the Narayana Dasha system."""

    rashi: Rashi = Field(description="Dasha sign")
    start_date: datetime = Field(description="Period start date")
    end_date: datetime = Field(description="Period end date")
    duration_years: int = Field(ge=1, le=12, description="Duration in years")
    is_forward: bool = Field(description="Whether progression is forward")


# ===================
# Prashna (Horary) Models
# ===================


class PrashnaChart(BaseModel):
    """Chart erected for a Prashna (horary) question."""

    question: str = Field(description="The question asked")
    question_datetime: datetime = Field(description="Time the question was asked")
    category: PrashnaCategory = Field(description="Question category")
    latitude: float = Field(ge=-90, le=90, description="Location latitude")
    longitude: float = Field(ge=-180, le=180, description="Location longitude")
    lagna_rashi: Rashi = Field(description="Ascendant sign at question time")
    lagna_degree: float = Field(ge=0, lt=360, description="Ascendant longitude")
    moon_position: PlanetPosition = Field(description="Moon position at question time")
    significator: Planet = Field(description="Primary significator for this category")
    planets: dict[Planet, PlanetPosition] = Field(description="All planet positions")
    houses: HouseCusps = Field(description="House cusps")


class PrashnaResult(BaseModel):
    """Complete result of a Prashna analysis."""

    chart: PrashnaChart = Field(description="The Prashna chart")
    judgment: PrashnaJudgment = Field(description="Overall judgment")
    strength_score: float = Field(ge=0, le=100, description="Strength score 0-100")
    favorable_factors: list[str] = Field(
        default_factory=list, description="Favorable factors found"
    )
    unfavorable_factors: list[str] = Field(
        default_factory=list, description="Unfavorable factors found"
    )
    timing: dict[str, Any] = Field(default_factory=dict, description="Timing predictions")
    recommendation: str = Field(default="", description="Overall recommendation")


# ===================
# Upagraha Models
# ===================


class UpagrahaPosition(BaseModel):
    """Position of an Upagraha (sub-planet)."""

    upagraha: Upagraha = Field(description="Upagraha identifier")
    longitude: float = Field(ge=0, lt=360, description="Ecliptic longitude")
    rashi: Rashi = Field(description="Zodiac sign")
    degree_in_sign: float = Field(ge=0, lt=30, description="Degree within sign")
    house: int = Field(ge=1, le=12, description="House placement")
    calculation_method: str = Field(
        default="", description="Method used (time-based or mathematical)"
    )


class UpagrahaAnalysis(BaseModel):
    """Complete upagraha analysis for a chart."""

    positions: dict[str, UpagrahaPosition] = Field(description="Upagraha positions keyed by name")
    sunrise: datetime = Field(description="Sunrise time used")
    sunset: datetime = Field(description="Sunset time used")
    day_duration_hours: float = Field(description="Day duration in hours")
    effects: list[dict[str, Any]] = Field(
        default_factory=list, description="Effects for each upagraha"
    )
