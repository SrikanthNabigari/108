"""
108 FastAPI Gateway - Main API entry point.

This is the unified REST API that orchestrates all packages:
- COSMOS (ephemeris calculations)
- SELF (yoga/dosha detection)
- CONTEXT (dasha, transits, muhurta)
- GUIDE (LangGraph agent)
- MEMORY (user profiles, conversations)

Routes:
- /health - Health check
- /api/v1/chart - Birth chart calculations
- /api/v1/analysis - Yogas, doshas, strengths
- /api/v1/timing - Dashas, transits, muhurta
- /api/v1/chat - Agent conversation
- /api/v1/users - User profile management
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime as dt
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add packages to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from our packages
from packages.context.src import (
    calculate_rahu_kaal,
    check_dhaiya,
    check_sade_sati,
    evaluate_muhurta,
    get_current_dasha,
    get_mahadasha_sequence,
    get_transit_positions,
)
from packages.core.src import (
    BirthData,
    CurrentDasha,
    DetectedDosha,
    DetectedYoga,
    HouseCusps,
    NakshatraInfo,
    Panchanga,
    PlanetPosition,
)
from packages.cosmos.src import (
    RASHI_NAMES,
    get_all_planets,
    get_divisional_chart,
    get_house_cusps,
    get_julian_day,
    get_panchanga,
    longitude_to_nakshatra,
)

# ============================================================================
# Helper Functions
# ============================================================================


def request_to_jd(request: "BirthDataRequest") -> float:
    """Convert BirthDataRequest to Julian Day Number.

    Handles timezone conversion properly by adjusting the datetime to UTC
    before passing to get_julian_day.
    """
    from datetime import timedelta

    utc_dt = request.datetime - timedelta(hours=request.timezone_offset)
    return get_julian_day(utc_dt)


def datetime_to_jd_utc(dt_obj: dt) -> float:
    """Convert a datetime to Julian Day, assuming already in UTC."""
    return get_julian_day(dt_obj)


def get_ayanamsa_value(jd: float, ayanamsa_name: str) -> float:
    """Convert ayanamsa name to float value for a given Julian Day."""
    from packages.cosmos.src import get_ayanamsa

    return get_ayanamsa(jd, ayanamsa_name)


# ============================================================================
# Configuration
# ============================================================================


class Settings(BaseModel):
    """Application settings."""

    app_name: str = "108 Vedic Astrology API"
    app_version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    cors_origins: list[str] = Field(default=["*"])
    default_ayanamsa: str = "lahiri"
    default_house_system: str = "whole_sign"


settings = Settings()


# ============================================================================
# Request/Response Models
# ============================================================================


class BirthDataRequest(BaseModel):
    """Request model for birth data input."""

    datetime: dt = Field(..., description="Birth date and time (ISO format)")
    latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude")
    timezone_offset: float = Field(default=0, description="Timezone offset in hours from UTC")
    name: str | None = Field(default=None, description="Person's name (optional)")
    ayanamsa: str = Field(default="lahiri", description="Ayanamsa system")
    house_system: str = Field(default="whole_sign", description="House system")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "datetime": "1992-12-03T03:00:00",
                    "latitude": 15.8281,
                    "longitude": 78.0373,
                    "timezone_offset": 5.5,
                    "name": "Srikanth",
                    "ayanamsa": "lahiri",
                    "house_system": "whole_sign",
                }
            ]
        }
    }


class ChartResponse(BaseModel):
    """Response model for birth chart."""

    birth_data: BirthData
    planets: dict[str, PlanetPosition]
    houses: HouseCusps
    ascendant: NakshatraInfo
    moon_nakshatra: NakshatraInfo
    panchanga: Panchanga


class AnalysisResponse(BaseModel):
    """Response model for chart analysis."""

    yogas: list[DetectedYoga]
    doshas: list[DetectedDosha]
    strengths: dict[str, Any]
    navamsha: dict[str, Any]


class TimingResponse(BaseModel):
    """Response model for timing analysis."""

    current_dasha: CurrentDasha
    mahadasha_sequence: list[dict[str, Any]]
    sade_sati: dict[str, Any] | None
    dhaiya: dict[str, Any] | None
    current_transits: dict[str, Any]


class MuhurtaRequest(BaseModel):
    """Request for muhurta analysis."""

    datetime: dt
    latitude: float
    longitude: float
    activity: str = Field(
        ..., description="Activity type: marriage, travel, business, education, etc."
    )


class MuhurtaResponse(BaseModel):
    """Response for muhurta analysis."""

    datetime: dt
    activity: str
    is_auspicious: bool
    score: float
    rahu_kaal: dict[str, Any]
    panchanga: Panchanga
    recommendations: list[str]


class CreateUserRequest(BaseModel):
    """Request model for creating a user with birth data."""

    email: str = Field(..., description="User email address")
    name: str | None = Field(default=None, description="User display name")
    birth_datetime: dt = Field(..., description="Birth date and time (ISO format)")
    latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude")
    timezone_offset: float = Field(default=0, description="Timezone offset in hours from UTC")
    timezone: str = Field(default="UTC", description="Timezone name (e.g. Asia/Kolkata)")
    place_name: str | None = Field(default=None, description="Birth place name")
    ayanamsa: str = Field(default="lahiri", description="Ayanamsa system")


class ChatRequest(BaseModel):
    """Request for agent chat."""

    message: str
    user_id: str | None = None
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    """Response from agent chat."""

    response: str
    user_id: str | None
    metadata: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: dt


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str | None = None
    status_code: int


# ============================================================================
# Lifespan Management
# ============================================================================


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage application lifecycle."""
    import logging

    logger = logging.getLogger(__name__)

    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize memory store if DATABASE_URL is configured
    _app.state.memory_store = None
    if settings.database_url:
        try:
            from packages.memory.src.store import MemoryStore

            store = MemoryStore(settings.database_url)
            await store.connect()
            _app.state.memory_store = store
            logger.info("MemoryStore connected")
        except Exception as e:
            logger.warning(f"Could not connect MemoryStore: {e}")

    # Guide agent — lazy init (requires ANTHROPIC_API_KEY)
    _app.state.guide = None

    yield

    # Shutdown
    logger.info("Shutting down 108 API...")
    if _app.state.memory_store:
        await _app.state.memory_store.close()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description="""
    108 - Personal Life Operating System powered by Vedic Astrology.

    This API provides:
    - **Birth Chart Calculations** - Planetary positions, houses, nakshatras
    - **Pattern Detection** - Yogas, doshas, planetary strengths
    - **Timing Analysis** - Vimshottari dasha, transits, muhurta
    - **AI Assistant** - Personalized guidance based on your chart

    All calculations use the Swiss Ephemeris with Lahiri ayanamsa (sidereal zodiac).
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail, status_code=exc.status_code).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    detail = str(exc) if settings.debug else "An unexpected error occurred"

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error", detail=detail, status_code=500
        ).model_dump(),
    )


# ============================================================================
# Health Check Routes
# ============================================================================


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    return HealthResponse(status="healthy", version=settings.app_version, timestamp=dt.utcnow())


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# Birth Chart Routes
# ============================================================================


@app.post("/api/v1/chart", tags=["Chart"])
async def calculate_birth_chart(request: BirthDataRequest):
    """
    Calculate complete birth chart from birth data.

    Returns planetary positions, house cusps, ascendant nakshatra,
    and moon nakshatra for the birth moment.
    """
    try:
        # Convert to Julian Day
        jd = request_to_jd(request)

        # Calculate planetary positions
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)

        # Calculate house cusps and ascendant
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Get ascendant details
        asc_longitude = houses_raw["ascendant"]
        asc_nakshatra = longitude_to_nakshatra(asc_longitude)

        # Get moon nakshatra
        moon_longitude = planets_raw["moon"]["longitude"]
        moon_nakshatra = longitude_to_nakshatra(moon_longitude)

        # Convert planets to response format
        planets = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            nak = longitude_to_nakshatra(data["longitude"])
            planets[planet_id] = {
                "longitude": data["longitude"],
                "latitude": data.get("latitude", 0.0),
                "speed": data.get("speed", 0.0),
                "rashi": RASHI_NAMES[rashi_idx],
                "rashi_num": rashi_idx,
                "degree_in_rashi": data["longitude"] % 30,
                "is_retrograde": data.get("is_retrograde", False),
                "nakshatra": nak.get("nakshatra_name", ""),
                "nakshatra_pada": nak.get("pada", 0),
            }

        # Get lagna rashi
        lagna_rashi_idx = int(asc_longitude // 30)
        lagna_rashi = RASHI_NAMES[lagna_rashi_idx]

        return {
            "birth_data": {
                "datetime": request.datetime.isoformat(),
                "latitude": request.latitude,
                "longitude": request.longitude,
                "timezone_offset": request.timezone_offset,
                "name": request.name,
            },
            "ascendant": {
                "longitude": asc_longitude,
                "rashi": lagna_rashi,
                "name": asc_nakshatra.get("nakshatra_name", ""),
                "pada": asc_nakshatra.get("pada", 0),
                "lord": asc_nakshatra.get("lord", ""),
                "degree_in_nakshatra": asc_nakshatra.get("degree_in_nakshatra", 0.0),
            },
            "moon_nakshatra": {
                "longitude": moon_longitude,
                "name": moon_nakshatra.get("nakshatra_name", ""),
                "pada": moon_nakshatra.get("pada", 0),
                "lord": moon_nakshatra.get("lord", ""),
                "degree_in_nakshatra": moon_nakshatra.get("degree_in_nakshatra", 0.0),
            },
            "planets": planets,
            "houses": {
                "ascendant": houses_raw["ascendant"],
                "mc": houses_raw.get("mc", 0.0),
                "cusps": houses_raw["cusps"],
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating chart: {e!s}"
        ) from e


@app.post("/api/v1/chart/divisional/{division}", tags=["Chart"])
async def calculate_divisional_chart(division: int, request: BirthDataRequest):
    """
    Calculate a specific divisional chart (D1-D60).

    Common divisional charts:
    - D1: Rashi (main chart)
    - D2: Hora (wealth)
    - D3: Drekkana (siblings)
    - D4: Chaturthamsha (fortune)
    - D7: Saptamsha (children)
    - D9: Navamsha (marriage, dharma)
    - D10: Dashamsha (career)
    - D12: Dwadashamsha (parents)
    - D16: Shodashamsha (vehicles, comforts)
    - D20: Vimshamsha (spiritual progress)
    - D24: Chaturvimshamsha (education)
    - D27: Bhamsha (strengths)
    - D30: Trimshamsha (misfortunes)
    - D40: Khavedamsha (auspiciousness)
    - D45: Akshavedamsha (general indications)
    - D60: Shashtiamsha (past karma)
    """
    if division < 1 or division > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Division must be between 1 and 60"
        )

    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)

        # Convert to simple dict for divisional calculation
        planets_dict = {p: {"longitude": d["longitude"]} for p, d in planets_raw.items()}

        divisional_chart = get_divisional_chart(planets_dict, division)

        return {
            "division": division,
            "chart": divisional_chart,
            "description": f"D{division} divisional chart",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating D{division}: {e!s}"
        ) from e


# ============================================================================
# Analysis Routes
# ============================================================================


@app.post("/api/v1/analysis", tags=["Analysis"])
async def analyze_chart(request: BirthDataRequest):
    """
    Perform complete chart analysis including yogas, doshas, and planetary strengths.

    Note: This is a simplified analysis. Full detection requires BirthChart model integration.
    """
    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Build planets dict
        planets_dict = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            planets_dict[planet_id] = {
                "longitude": data["longitude"],
                "rashi": RASHI_NAMES[rashi_idx],
                "rashi_num": rashi_idx,
                "degree": data["longitude"] % 30,
                "is_retrograde": data.get("is_retrograde", False),
            }

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx]

        # Calculate navamsha
        planets_simple = {p: {"longitude": d["longitude"]} for p, d in planets_raw.items()}
        navamsha = get_divisional_chart(planets_simple, 9)

        return {
            "lagna_rashi": lagna_rashi,
            "planets": planets_dict,
            "navamsha": navamsha,
            "message": "Use /api/v1/analysis/yogas, /api/v1/analysis/doshas, or /api/v1/analysis/strength for detailed analysis",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error analyzing chart: {e!s}"
        ) from e


@app.post("/api/v1/analysis/yogas", tags=["Analysis"])
async def detect_yogas(request: BirthDataRequest):
    """Detect all yogas in the birth chart.

    Note: Full yoga detection requires BirthChart model integration.
    This endpoint provides basic planetary positions for manual analysis.
    """
    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Build planet positions dict
        planets_dict = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            planets_dict[planet_id] = {
                "longitude": data["longitude"],
                "rashi": RASHI_NAMES[rashi_idx],
                "rashi_num": rashi_idx,
                "degree": data["longitude"] % 30,
                "is_retrograde": data.get("is_retrograde", False),
            }

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx]

        # Basic yoga detection (simplified - full detection requires BirthChart)
        yogas = []

        # Check for Pancha Mahapurusha Yogas (planet in own/exalted sign in kendra)
        kendras = [1, 4, 7, 10]
        mahapurusha_planets = {
            "mars": {"own": ["Aries", "Scorpio"], "exalted": "Capricorn", "yoga": "Ruchaka"},
            "mercury": {"own": ["Gemini", "Virgo"], "exalted": "Virgo", "yoga": "Bhadra"},
            "jupiter": {"own": ["Sagittarius", "Pisces"], "exalted": "Cancer", "yoga": "Hamsa"},
            "venus": {"own": ["Taurus", "Libra"], "exalted": "Pisces", "yoga": "Malavya"},
            "saturn": {"own": ["Capricorn", "Aquarius"], "exalted": "Libra", "yoga": "Shasha"},
        }

        lagna_rashi_idx = lagna_idx

        for planet, data in mahapurusha_planets.items():
            if planet in planets_dict:
                planet_rashi = planets_dict[planet]["rashi"]
                planet_rashi_idx = planets_dict[planet]["rashi_num"]
                # Calculate house from lagna
                house_from_lagna = ((planet_rashi_idx - lagna_rashi_idx) % 12) + 1

                if house_from_lagna in kendras and (
                    planet_rashi in data["own"] or planet_rashi == data["exalted"]
                ):
                    yogas.append(
                        {
                            "name": data["yoga"] + " Yoga",
                            "category": "Pancha Mahapurusha",
                            "planets_involved": [planet],
                            "description": f"{planet.title()} in {planet_rashi} (house {house_from_lagna})",
                            "is_present": True,
                        }
                    )

        return {
            "yogas": yogas,
            "count": len(yogas),
            "lagna_rashi": lagna_rashi,
            "note": "Basic yoga detection. Full analysis requires complete BirthChart integration.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error detecting yogas: {e!s}"
        ) from e


@app.post("/api/v1/analysis/doshas", tags=["Analysis"])
async def detect_doshas(request: BirthDataRequest):
    """Detect all doshas in the birth chart.

    Note: Full dosha detection requires BirthChart model integration.
    This endpoint provides basic Manglik and Kaal Sarp checks.
    """
    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Build planet positions dict
        planets_dict = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            planets_dict[planet_id] = {
                "longitude": data["longitude"],
                "rashi": RASHI_NAMES[rashi_idx],
                "rashi_num": rashi_idx,
                "degree": data["longitude"] % 30,
                "is_retrograde": data.get("is_retrograde", False),
            }

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx]

        # Basic dosha detection (simplified)
        doshas = []

        # Check Mangal Dosha (Mars in 1, 2, 4, 7, 8, 12 from Lagna/Moon/Venus)
        if "mars" in planets_dict:
            mars_rashi_idx = planets_dict["mars"]["rashi_num"]
            house_from_lagna = ((mars_rashi_idx - lagna_idx) % 12) + 1
            manglik_houses = [1, 2, 4, 7, 8, 12]

            if house_from_lagna in manglik_houses:
                # Check for cancellation
                cancellation = []
                # Mars in own sign (Aries, Scorpio) or exalted (Capricorn)
                if planets_dict["mars"]["rashi"] in ["Aries", "Scorpio", "Capricorn"]:
                    cancellation.append("Mars in own/exalted sign")
                # Jupiter aspect on Mars
                if "jupiter" in planets_dict:
                    jupiter_house = ((planets_dict["jupiter"]["rashi_num"] - lagna_idx) % 12) + 1
                    jupiter_aspects = [
                        (jupiter_house + 4) % 12 + 1,
                        (jupiter_house + 6) % 12 + 1,
                        (jupiter_house + 8) % 12 + 1,
                    ]
                    if house_from_lagna in jupiter_aspects:
                        cancellation.append("Jupiter aspects Mars")

                doshas.append(
                    {
                        "name": "Mangal Dosha (Kuja Dosha)",
                        "is_present": len(cancellation) == 0,
                        "severity": "high" if len(cancellation) == 0 else "cancelled",
                        "description": f"Mars in house {house_from_lagna} from Lagna",
                        "cancellation": cancellation if cancellation else None,
                        "remedies": ["Worship Hanuman on Tuesdays", "Recite Mangal mantra"],
                    }
                )

        # Check Kaal Sarp Dosha (all planets between Rahu-Ketu axis)
        if "rahu" in planets_dict and "ketu" in planets_dict:
            rahu_lon = planets_dict["rahu"]["longitude"]
            ketu_lon = planets_dict["ketu"]["longitude"]

            # Check if all 7 planets are on one side of Rahu-Ketu axis
            planets_between = 0
            for planet in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
                if planet in planets_dict:
                    p_lon = planets_dict[planet]["longitude"]
                    # Check if planet is between Rahu and Ketu (going one direction)
                    if rahu_lon < ketu_lon:
                        if rahu_lon <= p_lon <= ketu_lon:
                            planets_between += 1
                    else:
                        if p_lon >= rahu_lon or p_lon <= ketu_lon:
                            planets_between += 1

            if planets_between == 7 or planets_between == 0:
                doshas.append(
                    {
                        "name": "Kaal Sarp Dosha",
                        "is_present": True,
                        "severity": "high",
                        "description": "All planets hemmed between Rahu-Ketu axis",
                        "remedies": ["Rahu-Ketu shanti puja", "Worship Lord Shiva"],
                    }
                )

        return {
            "doshas": doshas,
            "count": len([d for d in doshas if d.get("is_present", True)]),
            "lagna_rashi": lagna_rashi,
            "note": "Basic dosha detection. Full analysis requires complete BirthChart integration.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error detecting doshas: {e!s}"
        ) from e


@app.post("/api/v1/analysis/strength", tags=["Analysis"])
async def calculate_planetary_strengths(request: BirthDataRequest):
    """Calculate planetary strengths (dignity assessment).

    Note: Full Shadbala requires BirthChart model integration.
    This endpoint provides basic dignity analysis.
    """
    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Planet dignity data
        PLANET_DIGNITY = {
            "sun": {"own": ["Leo"], "exalted": "Aries", "debilitated": "Libra", "moola": "Leo"},
            "moon": {
                "own": ["Cancer"],
                "exalted": "Taurus",
                "debilitated": "Scorpio",
                "moola": "Taurus",
            },
            "mars": {
                "own": ["Aries", "Scorpio"],
                "exalted": "Capricorn",
                "debilitated": "Cancer",
                "moola": "Aries",
            },
            "mercury": {
                "own": ["Gemini", "Virgo"],
                "exalted": "Virgo",
                "debilitated": "Pisces",
                "moola": "Virgo",
            },
            "jupiter": {
                "own": ["Sagittarius", "Pisces"],
                "exalted": "Cancer",
                "debilitated": "Capricorn",
                "moola": "Sagittarius",
            },
            "venus": {
                "own": ["Taurus", "Libra"],
                "exalted": "Pisces",
                "debilitated": "Virgo",
                "moola": "Libra",
            },
            "saturn": {
                "own": ["Capricorn", "Aquarius"],
                "exalted": "Libra",
                "debilitated": "Aries",
                "moola": "Aquarius",
            },
        }

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx]

        # Calculate basic dignity for each planet
        strengths = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            rashi = RASHI_NAMES[rashi_idx]
            degree = data["longitude"] % 30

            # Determine dignity
            dignity = "neutral"
            dignity_score = 50  # Base score

            if planet_id in PLANET_DIGNITY:
                p_data = PLANET_DIGNITY[planet_id]
                if rashi == p_data.get("exalted"):
                    dignity = "exalted"
                    dignity_score = 100
                elif rashi == p_data.get("debilitated"):
                    dignity = "debilitated"
                    dignity_score = 10
                elif rashi in p_data.get("own", []):
                    dignity = "own_sign"
                    dignity_score = 80
                elif rashi == p_data.get("moola"):
                    dignity = "moolatrikona"
                    dignity_score = 90

            # Adjust for retrograde
            is_retrograde = data.get("is_retrograde", False)
            if is_retrograde:
                dignity_score *= 0.9  # 10% reduction for retrograde

            # Calculate house from lagna
            house_from_lagna = ((rashi_idx - lagna_idx) % 12) + 1

            strengths[planet_id] = {
                "longitude": data["longitude"],
                "rashi": rashi,
                "degree_in_rashi": degree,
                "dignity": dignity,
                "dignity_score": round(dignity_score),
                "is_retrograde": is_retrograde,
                "house_from_lagna": house_from_lagna,
                "in_kendra": house_from_lagna in [1, 4, 7, 10],
                "in_trikona": house_from_lagna in [1, 5, 9],
                "in_dusthana": house_from_lagna in [6, 8, 12],
            }

        return {
            "strengths": strengths,
            "lagna_rashi": lagna_rashi,
            "note": "Basic dignity analysis. Full Shadbala requires complete BirthChart integration.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating strengths: {e!s}"
        ) from e


# ============================================================================
# Timing Routes
# ============================================================================


@app.post("/api/v1/timing", response_model=TimingResponse, tags=["Timing"])
async def get_timing_analysis(request: BirthDataRequest):
    """
    Get complete timing analysis including dasha, transits, and Sade Sati status.
    """
    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)

        # Get moon longitude for dasha calculation
        moon_longitude = planets_raw["moon"]["longitude"]

        # Get current dasha
        current_dasha = get_current_dasha(request.datetime, moon_longitude, dt.now())

        # Get mahadasha sequence
        mahadasha_sequence = get_mahadasha_sequence(request.datetime, moon_longitude)

        # Get current transits
        current_jd = datetime_to_jd_utc(dt.utcnow())
        current_transits = get_transit_positions(current_jd, ayanamsa=request.ayanamsa)

        # Check Sade Sati
        natal_moon_rashi = int(moon_longitude // 30)
        transit_saturn_rashi = int(current_transits.get("saturn", {}).get("longitude", 0) // 30)
        sade_sati = check_sade_sati(natal_moon_rashi, transit_saturn_rashi)

        # Check Dhaiya
        dhaiya = check_dhaiya(natal_moon_rashi, transit_saturn_rashi)

        return TimingResponse(
            current_dasha=current_dasha,
            mahadasha_sequence=mahadasha_sequence,
            sade_sati=sade_sati if sade_sati.get("active") else None,
            dhaiya=dhaiya if dhaiya.get("active") else None,
            current_transits=current_transits,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error analyzing timing: {e!s}"
        ) from e


@app.post("/api/v1/timing/dasha", tags=["Timing"])
async def get_dasha_periods(request: BirthDataRequest):
    """Get Vimshottari dasha periods for the birth chart."""
    try:
        jd = request_to_jd(request)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        moon_longitude = planets_raw["moon"]["longitude"]

        current_dasha = get_current_dasha(request.datetime, moon_longitude, dt.now())

        mahadasha_sequence = get_mahadasha_sequence(request.datetime, moon_longitude)

        return {"current": current_dasha, "mahadasha_sequence": mahadasha_sequence}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating dasha: {e!s}"
        ) from e


@app.get("/api/v1/timing/transits", tags=["Timing"])
async def get_current_transits(ayanamsa: str = "lahiri"):
    """Get current planetary transits."""
    try:
        now = dt.utcnow()
        jd = datetime_to_jd_utc(now)

        transits = get_transit_positions(jd, ayanamsa=ayanamsa)

        return {"datetime": now.isoformat(), "transits": transits}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error getting transits: {e!s}"
        ) from e


@app.post("/api/v1/timing/muhurta", response_model=MuhurtaResponse, tags=["Timing"])
async def check_muhurta(request: MuhurtaRequest):
    """
    Evaluate a specific time for an activity (muhurta analysis).

    Activities: marriage, travel, business_start, education, medical, property, legal
    """
    try:
        jd = datetime_to_jd_utc(request.datetime)

        # Get panchanga for the time
        panchanga = get_panchanga(jd, request.latitude, request.longitude)

        # Evaluate muhurta
        muhurta_result = evaluate_muhurta(jd, request.latitude, request.longitude, request.activity)

        # Calculate Rahu Kaal
        rahu_kaal = calculate_rahu_kaal(
            request.datetime.date(), request.latitude, request.longitude
        )

        return MuhurtaResponse(
            datetime=request.datetime,
            activity=request.activity,
            is_auspicious=muhurta_result.get("is_auspicious", False),
            score=muhurta_result.get("score", 0.0),
            rahu_kaal=rahu_kaal,
            panchanga=Panchanga(
                tithi=panchanga.get("tithi", {}),
                nakshatra=panchanga.get("nakshatra", {}),
                yoga=panchanga.get("yoga", {}),
                karana=panchanga.get("karana", {}),
                vara=panchanga.get("vara", ""),
            ),
            recommendations=muhurta_result.get("recommendations", []),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error evaluating muhurta: {e!s}"
        ) from e


# ============================================================================
# Chat/Agent Routes
# ============================================================================


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_agent(request: ChatRequest, req: Request):
    """
    Chat with the 108 AI assistant.

    The agent uses your birth chart context (if available) to provide
    personalized astrological guidance.

    Requires ANTHROPIC_API_KEY to be set for full agent responses.
    """
    # Check for API key
    if not settings.anthropic_api_key:
        return ChatResponse(
            response="The AI assistant requires an ANTHROPIC_API_KEY to be configured. "
            "Please set the ANTHROPIC_API_KEY environment variable. "
            "In the meantime, you can use the chart, analysis, and timing endpoints.",
            user_id=request.user_id,
            metadata={"status": "no_api_key", "agent_available": False},
        )

    try:
        # Lazy-init Guide agent
        if req.app.state.guide is None:
            from packages.guide.src.agent import Guide

            req.app.state.guide = Guide(api_key=settings.anthropic_api_key)

        guide = req.app.state.guide

        # Load birth chart from memory store if user_id provided
        birth_chart = None
        if request.user_id and req.app.state.memory_store:
            store = req.app.state.memory_store
            chart_record = await store.get_birth_chart(request.user_id)
            if chart_record:
                birth_chart = chart_record.get("chart_data", {})

        # Call the async guide agent
        result = await guide.chat_async(
            user_input=request.message,
            user_id=request.user_id or "anonymous",
            birth_chart=birth_chart,
        )

        return ChatResponse(
            response=result.get("response", ""),
            user_id=request.user_id,
            metadata={
                "status": "ok",
                "agent_available": True,
                "intent": result.get("intent"),
                "personality_style": result.get("personality_style"),
                "analysis_results": result.get("analysis_results", {}),
            },
        )

    except ImportError:
        return ChatResponse(
            response="The AI agent requires LangGraph and LangChain dependencies. "
            "Install with: uv pip install langgraph langchain-anthropic langchain-core",
            user_id=request.user_id,
            metadata={"status": "missing_dependencies", "agent_available": False},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {e!s}",
        ) from e


# ============================================================================
# User Routes (placeholder for user management)
# ============================================================================


@app.get("/api/v1/users/{user_id}", tags=["Users"])
async def get_user_profile(user_id: str, req: Request):
    """Get user profile including birth chart and detected patterns."""
    store = req.app.state.memory_store
    if not store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured. Set DATABASE_URL environment variable.",
        )

    try:
        # Get user
        user = await store.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
            )

        # Get birth chart
        birth_chart = await store.get_birth_chart(user_id)

        # Get detected patterns
        patterns = await store.get_user_patterns(user_id)

        return {
            "user": user,
            "birth_chart": birth_chart,
            "patterns": patterns,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {e!s}",
        ) from e


@app.post("/api/v1/users", tags=["Users"])
async def create_user_profile(request: CreateUserRequest, req: Request):
    """
    Create a new user profile with birth data.

    Calculates the birth chart, detects yogas/doshas, and stores everything.
    """
    store = req.app.state.memory_store
    if not store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured. Set DATABASE_URL environment variable.",
        )

    try:
        from datetime import timedelta

        # Create user
        user = await store.create_user(email=request.email, name=request.name)
        user_id = user["id"]

        # Calculate birth chart
        utc_dt = request.birth_datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_dt)

        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system="whole_sign",
            ayanamsa=request.ayanamsa,
        )

        # Build chart data dict
        asc_longitude = houses_raw["ascendant"]
        lagna_rashi_idx = int(asc_longitude // 30)
        lagna_rashi = RASHI_NAMES[lagna_rashi_idx]

        moon_longitude = planets_raw["moon"]["longitude"]
        moon_rashi_idx = int(moon_longitude // 30)
        moon_rashi = RASHI_NAMES[moon_rashi_idx]
        moon_nak = longitude_to_nakshatra(moon_longitude)

        planets_dict = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            nak = longitude_to_nakshatra(data["longitude"])
            house = ((rashi_idx - lagna_rashi_idx) % 12) + 1
            planets_dict[planet_id] = {
                "longitude": data["longitude"],
                "latitude": data.get("latitude", 0.0),
                "speed": data.get("speed", 0.0),
                "rashi": RASHI_NAMES[rashi_idx],
                "rashi_num": rashi_idx,
                "degree_in_rashi": data["longitude"] % 30,
                "is_retrograde": data.get("is_retrograde", False),
                "nakshatra": nak.get("nakshatra_name", ""),
                "nakshatra_pada": nak.get("pada", 0),
                "nakshatra_lord": nak.get("lord", ""),
                "house": house,
            }

        chart_data = {
            "planets": planets_dict,
            "houses": {
                "ascendant": asc_longitude,
                "mc": houses_raw.get("mc", 0.0),
                "cusps": houses_raw["cusps"],
            },
            "lagna_rashi": lagna_rashi,
            "moon_rashi": moon_rashi,
            "moon_longitude": moon_longitude,
            "moon_nakshatra": moon_nak.get("nakshatra_name", ""),
            "birth_datetime": request.birth_datetime.isoformat(),
            "latitude": request.latitude,
            "longitude": request.longitude,
            "timezone": request.timezone,
            "ayanamsa": request.ayanamsa,
        }

        # Save birth chart
        await store.save_birth_chart(
            user_id=user_id,
            birth_datetime=request.birth_datetime,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone,
            place_name=request.place_name,
            chart_data=chart_data,
            ayanamsa=request.ayanamsa,
        )

        return {
            "user_id": user_id,
            "user": user,
            "chart_summary": {
                "lagna_rashi": lagna_rashi,
                "moon_rashi": moon_rashi,
                "moon_nakshatra": moon_nak.get("nakshatra_name", ""),
                "planet_count": len(planets_dict),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {e!s}",
        ) from e


# ============================================================================
# Aspects & Bhava Bala Routes
# ============================================================================


@app.post("/api/v1/analysis/aspects", tags=["Analysis"])
async def calculate_aspects(request: BirthDataRequest):
    """Calculate Parashari Graha Drishti (planetary aspects) for the birth chart."""
    try:
        from packages.cosmos.src.aspects import get_all_aspects, get_houses_aspected_by

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)

        # Build planet -> house mapping
        planet_houses = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            house = ((rashi_idx - lagna_idx) % 12) + 1
            planet_houses[planet_id] = house

        aspects = get_all_aspects(planet_houses)
        houses_aspected = get_houses_aspected_by(planet_houses)

        return {
            "aspects": aspects,
            "houses_aspected": {str(k): v for k, v in houses_aspected.items()},
            "planet_houses": planet_houses,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating aspects: {e!s}",
        ) from e


@app.post("/api/v1/analysis/bhava-bala", tags=["Analysis"])
async def calculate_bhava_bala_endpoint(request: BirthDataRequest):
    """Calculate Bhava Bala (house strength) for all 12 houses."""
    try:
        from packages.self.src import StrengthCalculator

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Build a BirthChart for strength calculation
        from packages.core.src import (
            BirthChart,
            BirthData,
            HouseCusps,
            Planet,
            PlanetPosition,
            Rashi,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = Rashi(RASHI_NAMES[lagna_idx].lower())

        planet_positions = {}
        for planet_id, data in planets_raw.items():
            try:
                p_enum = Planet(planet_id.lower())
                rashi_idx = int(data["longitude"] // 30)
                r_enum = Rashi(RASHI_NAMES[rashi_idx].lower())
                nak = longitude_to_nakshatra(data["longitude"])
                house = ((rashi_idx - lagna_idx) % 12) + 1

                planet_positions[p_enum] = PlanetPosition(
                    planet=p_enum,
                    longitude=data["longitude"],
                    latitude=data.get("latitude", 0.0),
                    speed=data.get("speed", 0.0),
                    rashi=r_enum,
                    rashi_degree=data["longitude"] % 30,
                    nakshatra=nak.get("name", "ashwini"),
                    nakshatra_pada=nak.get("pada", 1),
                    nakshatra_lord=Planet.KETU,
                    is_retrograde=data.get("is_retrograde", False),
                    house=house,
                )
            except (ValueError, KeyError):
                continue

        moon_pos = planet_positions.get(Planet.MOON)
        moon_rashi = moon_pos.rashi if moon_pos else lagna_rashi
        moon_nak = moon_pos.nakshatra if moon_pos else "ashwini"

        chart = BirthChart(
            user_id="api_query",
            birth_data=BirthData(
                datetime_utc=request.datetime,
                latitude=request.latitude,
                longitude=request.longitude,
                timezone="UTC",
            ),
            planets=planet_positions,
            houses=HouseCusps(
                ascendant=houses_raw["ascendant"],
                mc=houses_raw.get("mc", 0.0),
                cusps=houses_raw["cusps"],
            ),
            lagna_rashi=lagna_rashi,
            moon_rashi=moon_rashi,
            moon_nakshatra=moon_nak,
            ayanamsa=23.85,
            calculated_at=dt.utcnow(),
        )

        calc = StrengthCalculator()
        all_balas = calc.get_all_bhava_balas(chart)

        return {
            "lagna_rashi": lagna_rashi.value,
            "houses": {str(k): v for k, v in all_balas.items()},
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating bhava bala: {e!s}",
        ) from e


# ============================================================================
# Muhurta & Eclipse Routes
# ============================================================================


@app.get("/api/v1/timing/abhijit-muhurta", tags=["Timing"])
async def get_abhijit(lat: float, lon: float, date: str | None = None):
    """Get Abhijit Muhurta (most universally auspicious time) for a date/location."""
    try:
        from packages.context.src.muhurta import get_abhijit_muhurta as _get_abhijit
        from packages.cosmos.src.sunrise_sunset import get_sunrise_sunset as _get_sr

        query_dt = dt.fromisoformat(date) if date else dt.utcnow()
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        sr_data = _get_sr(query_dt, lat, lon)
        sunrise = sr_data["sunrise"]
        sunset = sr_data["sunset"]
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        start, end = _get_abhijit(sunrise, sunset)

        return {
            "date": query_dt.date().isoformat(),
            "abhijit_start": start.isoformat(),
            "abhijit_end": end.isoformat(),
            "duration_minutes": round((end - start).total_seconds() / 60, 1),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating Abhijit muhurta: {e!s}",
        ) from e


@app.get("/api/v1/timing/brahma-muhurta", tags=["Timing"])
async def get_brahma(lat: float, lon: float, date: str | None = None):
    """Get Brahma Muhurta (best time for spiritual practices) for a date/location."""
    try:
        from packages.context.src.muhurta import get_brahma_muhurta as _get_brahma
        from packages.cosmos.src.sunrise_sunset import get_sunrise_sunset as _get_sr

        query_dt = dt.fromisoformat(date) if date else dt.utcnow()
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        sr_data = _get_sr(query_dt, lat, lon)
        sunrise = sr_data["sunrise"]
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        start, end = _get_brahma(sunrise)

        return {
            "date": query_dt.date().isoformat(),
            "brahma_start": start.isoformat(),
            "brahma_end": end.isoformat(),
            "duration_minutes": 48,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating Brahma muhurta: {e!s}",
        ) from e


@app.get("/api/v1/timing/eclipses/{year}/{month}", tags=["Timing"])
async def get_eclipses(year: int, month: int):
    """Check for solar and lunar eclipses in a given month."""
    try:
        from packages.context.src.muhurta import get_eclipse_periods as _get_eclipses

        eclipses = _get_eclipses(year, month)

        formatted = []
        for eclipse in eclipses:
            formatted.append(
                {
                    "type": eclipse["type"],
                    "start": eclipse["start"].isoformat()
                    if hasattr(eclipse["start"], "isoformat")
                    else str(eclipse["start"]),
                    "maximum": eclipse["maximum"].isoformat()
                    if hasattr(eclipse["maximum"], "isoformat")
                    else str(eclipse["maximum"]),
                    "end": eclipse["end"].isoformat()
                    if hasattr(eclipse["end"], "isoformat")
                    else str(eclipse["end"]),
                    "description": eclipse.get("description", ""),
                }
            )

        return {
            "year": year,
            "month": month,
            "eclipse_count": len(formatted),
            "eclipses": formatted,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error checking eclipses: {e!s}",
        ) from e


# ============================================================================
# Ashtottari Dasha & Progressions Routes
# ============================================================================


class DashaRequest(BaseModel):
    """Request model for dasha calculations."""

    birth_datetime: dt = Field(..., description="Birth datetime (ISO format)")
    moon_nakshatra: int = Field(..., ge=1, le=27, description="Moon nakshatra number (1-27)")
    degree_in_nakshatra: float = Field(..., ge=0, le=14, description="Degrees in nakshatra")
    rahu_house: int = Field(default=0, ge=0, le=12, description="Rahu house (1-12), 0 to skip")
    lagna_lord_house: int = Field(
        default=0, ge=0, le=12, description="Lagna lord house (1-12), 0 to skip"
    )
    query_datetime: dt | None = Field(default=None, description="Query datetime")


@app.post("/api/v1/dasha/ashtottari", tags=["Timing"])
async def get_ashtottari(request: DashaRequest):
    """Calculate Ashtottari Dasha (108-year planetary period system)."""
    try:
        from packages.context.src.ashtottari_dasha import (
            calculate_ashtottari_sequence as _calc_seq,
        )
        from packages.context.src.ashtottari_dasha import (
            get_current_ashtottari as _get_current,
        )
        from packages.context.src.ashtottari_dasha import (
            is_ashtottari_applicable as _is_applicable,
        )

        birth_dt = request.birth_datetime
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        query_dt = request.query_datetime
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        applicable = True
        if request.rahu_house > 0 and request.lagna_lord_house > 0:
            applicable = _is_applicable(request.rahu_house, request.lagna_lord_house)

        current = _get_current(
            birth_dt, request.moon_nakshatra, request.degree_in_nakshatra, query_dt
        )
        periods = _calc_seq(birth_dt, request.moon_nakshatra, request.degree_in_nakshatra)

        return {
            "system": "ashtottari",
            "applicable": applicable,
            "current": {
                "mahadasha_lord": current["mahadasha"]["lord"],
                "antardasha_lord": current["antardasha"]["lord"],
                "remaining_days_maha": current["remaining_days_maha"],
                "remaining_days_antar": current["remaining_days_antar"],
            },
            "periods": [
                {
                    "lord": p["lord"],
                    "start_date": p["start_date"].isoformat(),
                    "end_date": p["end_date"].isoformat(),
                    "years": round(p["years"], 2),
                }
                for p in periods
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating Ashtottari: {e!s}",
        ) from e


@app.post("/api/v1/progressions/current", tags=["Timing"])
async def get_progressions(request: BirthDataRequest):
    """Get current Secondary Progressions (day-for-a-year technique)."""
    try:
        from packages.context.src.progressions import get_current_progressions as _get_prog

        birth_dt = request.datetime
        # NOTE: Do NOT strip timezone — get_julian_day handles conversion to UTC

        result = _get_prog(birth_dt, request.latitude, request.longitude)

        return {
            "system": "secondary_progressions",
            "age_years": result.get("age"),
            "progressed_positions": result.get("progressed_positions", {}),
            "active_aspects": result.get("active_aspects", []),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating progressions: {e!s}",
        ) from e


# ============================================================================
# Panchanga Knowledge Routes (New)
# ============================================================================


@app.get("/api/v1/knowledge/tithis/{number}", tags=["Knowledge"])
async def get_tithi(number: int):
    """Get tithi (lunar day) definition by number."""
    try:
        from packages.core.src.knowledge_loader import get_tithi_definitions

        data = get_tithi_definitions()
        tithis = data.get("tithis", data)

        tithi_key = str(number)
        if isinstance(tithis, dict) and tithi_key in tithis:
            return tithis[tithi_key]

        if isinstance(tithis, list):
            for t in tithis:
                if isinstance(t, dict) and t.get("number") == number:
                    return t

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tithi {number} not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error looking up tithi: {e!s}"
        ) from e


@app.get("/api/v1/knowledge/karanas/{name}", tags=["Knowledge"])
async def get_karana(name: str):
    """Get karana (half-tithi) definition by name."""
    try:
        from packages.core.src.knowledge_loader import get_karana_definitions

        data = get_karana_definitions()
        karanas = data.get("karanas", data)

        search = name.lower().replace(" ", "_")
        if isinstance(karanas, dict):
            if search in karanas:
                return karanas[search]
            for key, val in karanas.items():
                if search in key.lower():
                    return val

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Karana '{name}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error looking up karana: {e!s}"
        ) from e


@app.get("/api/v1/knowledge/varas/{name}", tags=["Knowledge"])
async def get_vara(name: str):
    """Get vara (weekday) definition by name."""
    try:
        from packages.core.src.knowledge_loader import get_vara_definitions

        data = get_vara_definitions()
        varas = data.get("varas", data)

        search = name.lower().replace(" ", "_")
        if isinstance(varas, dict):
            if search in varas:
                return varas[search]
            for key, val in varas.items():
                if search in key.lower():
                    return val

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Vara '{name}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error looking up vara: {e!s}"
        ) from e


@app.get("/api/v1/knowledge/avasthas/{planet}", tags=["Knowledge"])
async def get_avastha(planet: str, longitude: float = 0.0):
    """Get avastha (planetary state) for a planet."""
    try:
        from packages.core.src.knowledge_loader import get_avastha_definitions

        data = get_avastha_definitions()
        avasthas = data.get("avasthas", data)

        result: dict[str, Any] = {"planet": planet.lower(), "avasthas": avasthas}

        if longitude > 0:
            degree_in_sign = longitude % 30
            if degree_in_sign < 6:
                result["baladi_avastha"] = "bala"
            elif degree_in_sign < 12:
                result["baladi_avastha"] = "kumara"
            elif degree_in_sign < 18:
                result["baladi_avastha"] = "yuva"
            elif degree_in_sign < 24:
                result["baladi_avastha"] = "vridha"
            else:
                result["baladi_avastha"] = "mrita"

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error looking up avastha: {e!s}"
        ) from e


@app.get("/api/v1/knowledge/nitya-yogas/{number}", tags=["Knowledge"])
async def get_nitya_yoga(number: int):
    """Get Nitya Yoga definition by number (1-27)."""
    try:
        from packages.core.src.knowledge_loader import get_nitya_yoga_definitions

        data = get_nitya_yoga_definitions()
        yogas = data.get("nitya_yogas", data)

        yoga_key = str(number)
        if isinstance(yogas, dict) and yoga_key in yogas:
            return yogas[yoga_key]

        if isinstance(yogas, list):
            for y in yogas:
                if isinstance(y, dict) and y.get("number") == number:
                    return y

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Nitya Yoga {number} not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error looking up nitya yoga: {e!s}"
        ) from e


# ============================================================================
# Knowledge Routes
# ============================================================================


@app.get("/api/v1/knowledge/planets/{planet_id}", tags=["Knowledge"])
async def get_planet_info(planet_id: str):
    """Get detailed information about a planet."""
    import json

    try:
        knowledge_path = (
            Path(__file__).parent.parent.parent / "knowledge" / "definitions" / "planets.json"
        )

        with knowledge_path.open() as f:
            planets_data = json.load(f)

        planet_key = planet_id.lower()
        if planet_key not in planets_data.get("planets", {}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Planet '{planet_id}' not found"
            )

        return planets_data["planets"][planet_key]

    except FileNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Planets knowledge base not found"
        ) from err


@app.get("/api/v1/knowledge/nakshatras/{nakshatra_name}", tags=["Knowledge"])
async def get_nakshatra_info(nakshatra_name: str):
    """Get detailed information about a nakshatra."""
    import json

    try:
        knowledge_path = (
            Path(__file__).parent.parent.parent / "knowledge" / "definitions" / "nakshatras.json"
        )

        with knowledge_path.open() as f:
            nakshatras_data = json.load(f)

        nakshatra_key = nakshatra_name.lower()
        if nakshatra_key not in nakshatras_data.get("nakshatras", {}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nakshatra '{nakshatra_name}' not found",
            )

        return nakshatras_data["nakshatras"][nakshatra_key]

    except FileNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nakshatras knowledge base not found"
        ) from err


@app.get("/api/v1/knowledge/rashis/{rashi_name}", tags=["Knowledge"])
async def get_rashi_info(rashi_name: str):
    """Get detailed information about a rashi (zodiac sign)."""
    import json

    try:
        knowledge_path = (
            Path(__file__).parent.parent.parent / "knowledge" / "definitions" / "rashis.json"
        )

        with knowledge_path.open() as f:
            rashis_data = json.load(f)

        rashi_key = rashi_name.lower()
        if rashi_key not in rashis_data.get("rashis", {}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Rashi '{rashi_name}' not found"
            )

        return rashis_data["rashis"][rashi_key]

    except FileNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rashis knowledge base not found"
        ) from err


# ============================================================================
# Session 21 Routes: Yoga Cancellation, Planetary War, Bhava Chalit, Remedies,
# Dasha-Transit, Transit Aspects, Event Correlation, Transit Triggers, Varshaphal
# ============================================================================


class EventCorrelationRequest(BaseModel):
    """Request model for event correlation."""

    event_date: str = Field(..., description="Event date in ISO format (e.g., 2020-03-15)")
    event_type: str = Field(
        ..., description="Event category (career, marriage, health, money, education, travel, loss)"
    )
    event_description: str = Field(..., description="Brief description of the event")
    birth_datetime: dt = Field(..., description="Birth datetime in ISO format")
    latitude: float = Field(..., ge=-90, le=90, description="Birth latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth longitude")
    timezone_offset: float = Field(default=5.5, description="Timezone offset from UTC")
    ayanamsa: str = Field(default="lahiri", description="Ayanamsa system")


class TransitTriggersRequest(BaseModel):
    """Request model for upcoming transit triggers."""

    birth_datetime: dt = Field(..., description="Birth datetime")
    latitude: float = Field(..., ge=-90, le=90, description="Birth latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth longitude")
    timezone_offset: float = Field(default=5.5, description="Timezone offset")
    ayanamsa: str = Field(default="lahiri", description="Ayanamsa")
    start_date: str | None = Field(default=None, description="Start date (ISO), defaults to today")
    days_ahead: int = Field(default=30, ge=1, le=365, description="Days to look ahead")


class RemediesRequest(BaseModel):
    """Request model for remedy recommendations."""

    current_dasha: dict[str, str] = Field(
        ..., description="Active dasha lords {mahadasha_lord, antardasha_lord}"
    )
    active_doshas: list[dict[str, Any]] = Field(
        default=[], description="List of doshas [{name, severity}]"
    )
    weak_planets: list[dict[str, Any]] = Field(
        default=[], description="List of weak planets [{planet, shadbala}]"
    )
    lagna_rashi: str = Field(default="", description="Ascendant sign name")


@app.post("/api/v1/analysis/yoga-cancellations", tags=["Analysis"])
async def check_yoga_cancellations(request: BirthDataRequest):
    """Check if detected yogas are cancelled by classical rules (Yoga Bhanga)."""
    try:
        from packages.self.src.yoga_cancellation import apply_cancellations_to_chart

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        sun_longitude = planets_raw["sun"]["longitude"]

        # Build planet dict
        planets_dict: dict[str, Any] = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            house = ((rashi_idx - lagna_idx) % 12) + 1
            planets_dict[planet_id] = {
                "longitude": data["longitude"],
                "rashi": RASHI_NAMES[rashi_idx].lower(),
                "house": house,
                "is_retrograde": data.get("is_retrograde", False),
            }

        # Detect basic yogas first (simplified)
        yogas: list[dict[str, Any]] = []
        kendras = [1, 4, 7, 10]
        mp_planets = {
            "mars": {
                "own": ["aries", "scorpio"],
                "exalted": "capricorn",
                "cat": "pancha_mahapurusha",
            },
            "mercury": {
                "own": ["gemini", "virgo"],
                "exalted": "virgo",
                "cat": "pancha_mahapurusha",
            },
            "jupiter": {
                "own": ["sagittarius", "pisces"],
                "exalted": "cancer",
                "cat": "pancha_mahapurusha",
            },
            "venus": {"own": ["taurus", "libra"], "exalted": "pisces", "cat": "pancha_mahapurusha"},
            "saturn": {
                "own": ["capricorn", "aquarius"],
                "exalted": "libra",
                "cat": "pancha_mahapurusha",
            },
        }
        for planet, mp_data in mp_planets.items():
            if planet in planets_dict:
                p = planets_dict[planet]
                if p["house"] in kendras and (
                    p["rashi"] in mp_data["own"] or p["rashi"] == mp_data["exalted"]
                ):
                    yogas.append(
                        {
                            "category": mp_data["cat"],
                            "involved_planets": [planet],
                            "name": f"{planet.title()} Mahapurusha",
                            "strength": 1.0,
                        }
                    )

        results = apply_cancellations_to_chart(yogas, planets_dict, lagna_rashi, sun_longitude)

        cancelled_count = sum(1 for r in results if r.get("cancellation", {}).get("cancelled"))

        return {
            "total_yogas": len(results),
            "cancelled_count": cancelled_count,
            "active_count": len(results) - cancelled_count,
            "yogas": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error checking yoga cancellations: {e!s}",
        ) from e


@app.post("/api/v1/analysis/neecha-bhanga", tags=["Analysis"])
async def check_neecha_bhanga(request: BirthDataRequest):
    """Check Neecha Bhanga Raja Yoga for all debilitated planets in the chart."""
    try:
        from packages.self.src.yoga_detector import detect_neecha_bhanga

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()

        planets_dict: dict[str, Any] = {}
        for planet_id, data in planets_raw.items():
            rashi_idx = int(data["longitude"] // 30)
            house = ((rashi_idx - lagna_idx) % 12) + 1
            planets_dict[planet_id] = {
                "longitude": data["longitude"],
                "sign": RASHI_NAMES[rashi_idx].lower(),
                "rashi": RASHI_NAMES[rashi_idx].lower(),
                "house": house,
                "is_retrograde": data.get("is_retrograde", False),
            }

        # Check each planet for neecha bhanga
        debilitation_map = {
            "sun": "libra",
            "moon": "scorpio",
            "mars": "cancer",
            "mercury": "pisces",
            "jupiter": "capricorn",
            "venus": "virgo",
            "saturn": "aries",
        }

        results = []
        for planet, debil_sign in debilitation_map.items():
            if planet in planets_dict and planets_dict[planet]["rashi"] == debil_sign:
                result = detect_neecha_bhanga(
                    planet, planets_dict[planet], planets_dict, lagna_rashi
                )
                results.append({"planet": planet, **result})

        return {
            "debilitated_planets": len(results),
            "neecha_bhanga_results": results,
            "lagna_rashi": lagna_rashi,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error checking neecha bhanga: {e!s}",
        ) from e


@app.post("/api/v1/analysis/planetary-wars", tags=["Analysis"])
async def check_planetary_wars(request: BirthDataRequest):
    """Detect Graha Yuddha (planetary wars) in the birth chart."""
    try:
        from packages.core.src.constants import Planet
        from packages.self.src.planetary_war import detect_planetary_wars

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)

        planet_dict = {}
        for planet_id, data in planets_raw.items():
            try:
                p_enum = Planet(planet_id.lower())
                planet_dict[p_enum] = {
                    "longitude": data["longitude"],
                    "latitude": data.get("latitude", 0.0),
                    "is_retrograde": data.get("is_retrograde", False),
                }
            except (ValueError, KeyError):
                continue

        wars = detect_planetary_wars(planet_dict)

        return {
            "wars_found": len(wars),
            "wars": wars,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error detecting planetary wars: {e!s}",
        ) from e


@app.post("/api/v1/analysis/bhava-chalit", tags=["Analysis"])
async def calculate_bhava_chalit(request: BirthDataRequest):
    """Calculate Bhava Chalit chart showing house shifts."""
    try:
        from packages.cosmos.src.bhava_chalit import calculate_bhava_chalit as calc_chalit
        from packages.cosmos.src.bhava_chalit import get_shifted_planets

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        result = calc_chalit(planets_raw, houses_raw["cusps"], houses_raw["ascendant"])
        shifted = get_shifted_planets(result)

        return {
            "planets": result,
            "shifted_planets": shifted,
            "shift_count": len(shifted),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating bhava chalit: {e!s}",
        ) from e


@app.post("/api/v1/analysis/navamsha-spouse", tags=["Analysis"])
async def navamsha_spouse(request: BirthDataRequest):
    """Analyze spouse characteristics from Navamsha (D9) chart."""
    try:
        import json

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        # Calculate D9
        planets_simple = {p: {"longitude": d["longitude"]} for p, d in planets_raw.items()}
        d9 = get_divisional_chart(planets_simple, 9)

        # D9 lagna
        d9_asc_lon = (houses_raw["ascendant"] % 30) * 3 + (int(houses_raw["ascendant"] / 30) * 30)
        d9_lagna_idx = int(d9_asc_lon % 360 // 30)

        # D9 7th house sign
        d9_7th_idx = (d9_lagna_idx + 6) % 12
        d9_7th_sign = RASHI_NAMES[d9_7th_idx].lower()

        # D9 7th lord sign
        rashi_lords = {
            "aries": "mars",
            "taurus": "venus",
            "gemini": "mercury",
            "cancer": "moon",
            "leo": "sun",
            "virgo": "mercury",
            "libra": "venus",
            "scorpio": "mars",
            "sagittarius": "jupiter",
            "capricorn": "saturn",
            "aquarius": "saturn",
            "pisces": "jupiter",
        }
        d9_7th_lord = rashi_lords.get(d9_7th_sign, "")
        d9_7th_lord_sign = ""
        if d9_7th_lord and d9_7th_lord in d9:
            lord_lon = d9[d9_7th_lord].get("longitude", 0)
            d9_7th_lord_sign = RASHI_NAMES[int(lord_lon // 30)].lower()

        # Venus in D9
        d9_venus_sign = ""
        if "venus" in d9:
            venus_lon = d9["venus"].get("longitude", 0)
            d9_venus_sign = RASHI_NAMES[int(venus_lon // 30)].lower()

        # Planets in D9 7th house
        d9_7th_planets = []
        for planet_id, pdata in d9.items():
            p_lon = pdata.get("longitude", 0)
            p_rashi_idx = int(p_lon // 30)
            if p_rashi_idx == d9_7th_idx:
                d9_7th_planets.append(planet_id)

        # Load navamsha spouse rules
        rules_path = (
            Path(__file__).parent.parent.parent
            / "knowledge"
            / "rules"
            / "navamsha_spouse_rules.json"
        )
        with rules_path.open() as f:
            rules = json.load(f)

        spouse_rules = rules.get("navamsha_spouse_rules", rules)
        result: dict[str, Any] = {"d9_7th_sign": d9_7th_sign, "d9_7th_lord": d9_7th_lord}

        # Interpret 7th lord sign
        for rule in spouse_rules.get("d9_7th_lord_in_sign", []):
            if rule.get("sign", "").lower() == d9_7th_lord_sign:
                result["d9_7th_lord_interpretation"] = rule
                break

        # Venus interpretation
        for rule in spouse_rules.get("venus_in_d9_sign", []):
            if rule.get("sign", "").lower() == d9_venus_sign:
                result["d9_venus_interpretation"] = rule
                break

        # 7th house planets
        result["d9_7th_house_planets"] = d9_7th_planets

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error analyzing navamsha spouse: {e!s}",
        ) from e


@app.post("/api/v1/analysis/remedies", tags=["Analysis"])
async def get_remedies(request: RemediesRequest):
    """Get prioritized remedy recommendations based on chart conditions."""
    try:
        from packages.self.src.remedies import recommend_remedies

        result = recommend_remedies(
            current_dasha=request.current_dasha,
            active_doshas=request.active_doshas,
            weak_planets=request.weak_planets,
            lagna_rashi=request.lagna_rashi,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error recommending remedies: {e!s}",
        ) from e


@app.post("/api/v1/timing/dasha-transit", tags=["Timing"])
async def dasha_transit_analysis(request: BirthDataRequest):
    """Cross-analyze dasha periods with current transits for timing insights."""
    try:
        from packages.context.src.dasha_transit import cross_analyze

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        moon_longitude = planets_raw["moon"]["longitude"]
        moon_rashi = RASHI_NAMES[int(moon_longitude // 30)].lower()

        # Get current dasha
        current_dasha_data = get_current_dasha(request.datetime, moon_longitude, dt.now())
        dasha_info = {
            "mahadasha": current_dasha_data["mahadasha"]["lord"],
            "antardasha": current_dasha_data["antardasha"]["lord"],
        }
        pd = current_dasha_data.get("pratyantardasha")
        if pd:
            dasha_info["pratyantardasha"] = pd.get("lord", "")

        # Get current transits
        current_jd = datetime_to_jd_utc(dt.utcnow())
        current_transits = {}
        transit_raw = get_all_planets(current_jd, ayanamsa=request.ayanamsa)
        for planet_id, data in transit_raw.items():
            current_transits[planet_id] = {
                "longitude": data["longitude"],
                "rashi": int(data["longitude"] // 30),
            }

        # Build natal planet positions
        natal_planets: dict[str, Any] = {}
        for planet_id, data in planets_raw.items():
            natal_planets[planet_id] = {
                "longitude": data["longitude"],
                "rashi": int(data["longitude"] // 30),
            }

        result = cross_analyze(natal_planets, current_transits, dasha_info, lagna_rashi, moon_rashi)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in dasha-transit analysis: {e!s}",
        ) from e


@app.post("/api/v1/timing/transit-aspects", tags=["Timing"])
async def transit_natal_aspects(request: BirthDataRequest):
    """Calculate all aspects between current transits and natal planets."""
    try:
        from packages.context.src.transit_aspects import get_transit_natal_aspects

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)

        natal_planets: dict[str, Any] = {}
        for planet_id, data in planets_raw.items():
            natal_planets[planet_id] = {
                "longitude": data["longitude"],
                "rashi": int(data["longitude"] // 30),
            }

        # Get current transits
        current_jd = datetime_to_jd_utc(dt.utcnow())
        transit_raw = get_all_planets(current_jd, ayanamsa=request.ayanamsa)
        transit_planets: dict[str, Any] = {}
        for planet_id, data in transit_raw.items():
            transit_planets[planet_id] = {
                "longitude": data["longitude"],
                "rashi": int(data["longitude"] // 30),
                "speed": data.get("speed", 0),
            }

        aspects = get_transit_natal_aspects(natal_planets, transit_planets)

        return {
            "total_aspects": len(aspects),
            "aspects": aspects,
            "tightest": aspects[:5] if aspects else [],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating transit aspects: {e!s}",
        ) from e


@app.post("/api/v1/timing/event-correlation", tags=["Timing"])
async def correlate_event(request: EventCorrelationRequest):
    """Correlate a past life event with dasha and transit configurations."""
    try:
        from datetime import timedelta

        from packages.context.src.event_correlator import correlate_event as _correlate

        utc_birth = request.birth_datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_birth)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system="whole_sign",
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        moon_longitude = planets_raw["moon"]["longitude"]

        natal_planets: dict[str, Any] = {}
        for planet_id, data in planets_raw.items():
            natal_planets[planet_id] = {
                "longitude": data["longitude"],
                "rashi": int(data["longitude"] // 30),
            }

        result = _correlate(
            event_date=request.event_date,
            event_type=request.event_type,
            event_description=request.event_description,
            birth_datetime=request.birth_datetime,
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error correlating event: {e!s}",
        ) from e


@app.post("/api/v1/timing/upcoming-triggers", tags=["Timing"])
async def get_upcoming_triggers(request: TransitTriggersRequest):
    """Find the next significant transit events for the birth chart."""
    try:
        from datetime import timedelta

        from packages.context.src.transit_tracker import get_upcoming_triggers as _get_triggers

        utc_birth = request.birth_datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_birth)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system="whole_sign",
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        moon_longitude = planets_raw["moon"]["longitude"]
        moon_rashi = RASHI_NAMES[int(moon_longitude // 30)].lower()

        natal_planets: dict[str, Any] = {}
        for planet_id, data in planets_raw.items():
            natal_planets[planet_id] = {
                "longitude": data["longitude"],
                "rashi": int(data["longitude"] // 30),
            }

        start_date = request.start_date or dt.utcnow().isoformat()

        triggers = _get_triggers(
            natal_planets=natal_planets,
            lagna_rashi=lagna_rashi,
            moon_rashi=moon_rashi,
            start_date=start_date,
            days_ahead=request.days_ahead,
            birth_datetime=request.birth_datetime,
            moon_longitude=moon_longitude,
        )

        return {
            "total_triggers": len(triggers),
            "triggers": triggers,
            "high_significance": [t for t in triggers if t.get("significance") == "high"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error finding upcoming triggers: {e!s}",
        ) from e


@app.post("/api/v1/timing/varshaphal", tags=["Timing"])
async def get_varshaphal(request: BirthDataRequest):
    """Get current Varshaphal (solar return / Tajika annual horoscope)."""
    try:
        from packages.context.src.varshaphal import get_current_varshaphal

        result = get_current_varshaphal(
            birth_datetime=request.datetime,
            birth_lat=request.latitude,
            birth_lon=request.longitude,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating varshaphal: {e!s}",
        ) from e


# ============================================================================
# Session 22 - Synastry, Gem Recommendation, Atmakaraka, Forecasts
# ============================================================================


class SynastryRequest(BaseModel):
    """Request model for synastry (relationship) analysis."""

    native_datetime: dt = Field(..., description="First person birth datetime")
    native_latitude: float = Field(..., ge=-90, le=90)
    native_longitude: float = Field(..., ge=-180, le=180)
    partner_datetime: dt = Field(..., description="Second person birth datetime")
    partner_latitude: float = Field(..., ge=-90, le=90)
    partner_longitude: float = Field(..., ge=-180, le=180)
    timezone_offset: float = Field(default=5.5, description="Timezone offset (hours)")
    partner_timezone_offset: float = Field(default=5.5, description="Partner timezone offset")
    ayanamsa: str = Field(default="lahiri")
    house_system: str = Field(default="whole_sign")


class GemRequest(BaseModel):
    """Request model for gemstone recommendation."""

    datetime: dt = Field(..., description="Birth datetime")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone_offset: float = Field(default=5.5)
    ayanamsa: str = Field(default="lahiri")
    house_system: str = Field(default="whole_sign")
    gem_planet: str | None = Field(
        default=None,
        description="Specific planet gem to check (omit for full recommendation)",
    )


class ForecastRequest(BaseModel):
    """Request model for daily/weekly/monthly forecast."""

    datetime: dt = Field(..., description="Birth datetime")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone_offset: float = Field(default=5.5)
    ayanamsa: str = Field(default="lahiri")
    house_system: str = Field(default="whole_sign")
    query_date: str | None = Field(default=None, description="Target date (ISO format)")
    location_lat: float | None = Field(default=None, description="Current location latitude")
    location_lon: float | None = Field(default=None, description="Current location longitude")
    month: int | None = Field(default=None, ge=1, le=12, description="Month (for monthly)")
    year: int | None = Field(default=None, description="Year (for monthly)")


def _build_planets_dict(planets_raw: dict, lagna_idx: int) -> dict[str, Any]:
    """Build a standard planets dict from raw ephemeris output."""
    planets_dict: dict[str, Any] = {}
    for planet_id, data in planets_raw.items():
        rashi_idx = int(data["longitude"] // 30)
        house = ((rashi_idx - lagna_idx) % 12) + 1
        planets_dict[planet_id] = {
            "longitude": data["longitude"],
            "rashi": RASHI_NAMES[rashi_idx].lower(),
            "house": house,
            "is_retrograde": data.get("is_retrograde", False),
        }
    return planets_dict


@app.post("/api/v1/analysis/synastry", tags=["Analysis"])
async def get_synastry(request: SynastryRequest):
    """Analyze relationship compatibility through synastry chart overlay."""
    try:
        from datetime import timedelta

        from packages.self.src.synastry import get_synastry_report

        # Calculate native chart
        native_utc = request.native_datetime - timedelta(hours=request.timezone_offset)
        native_jd = get_julian_day(native_utc)
        native_planets_raw = get_all_planets(native_jd, ayanamsa=request.ayanamsa)
        native_houses_raw = get_house_cusps(
            native_jd,
            request.native_latitude,
            request.native_longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )
        native_lagna_idx = int(native_houses_raw["ascendant"] // 30)
        native_planets = _build_planets_dict(native_planets_raw, native_lagna_idx)
        native_cusps = native_houses_raw["cusps"]
        native_moon_nak = int((native_planets_raw["moon"]["longitude"] * 27) / 360) + 1

        # Calculate partner chart
        partner_utc = request.partner_datetime - timedelta(hours=request.partner_timezone_offset)
        partner_jd = get_julian_day(partner_utc)
        partner_planets_raw = get_all_planets(partner_jd, ayanamsa=request.ayanamsa)
        partner_houses_raw = get_house_cusps(
            partner_jd,
            request.partner_latitude,
            request.partner_longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )
        partner_lagna_idx = int(partner_houses_raw["ascendant"] // 30)
        partner_planets = _build_planets_dict(partner_planets_raw, partner_lagna_idx)
        partner_cusps = partner_houses_raw["cusps"]
        partner_moon_nak = int((partner_planets_raw["moon"]["longitude"] * 27) / 360) + 1

        result = get_synastry_report(
            native_planets=native_planets,
            native_cusps=native_cusps,
            partner_planets=partner_planets,
            partner_cusps=partner_cusps,
            native_ascendant=native_houses_raw["ascendant"],
            partner_ascendant=partner_houses_raw["ascendant"],
            native_moon_nakshatra=native_moon_nak,
            partner_moon_nakshatra=partner_moon_nak,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating synastry: {e!s}",
        ) from e


@app.post("/api/v1/analysis/gem-recommendation", tags=["Analysis"])
async def get_gem_recommendation(request: GemRequest):
    """Get personalized gemstone recommendations based on birth chart."""
    try:
        from datetime import timedelta

        from packages.self.src.gem_recommender import (
            check_gem_compatibility,
            recommend_gems,
        )

        utc_dt = request.datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_dt)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        planets_dict = _build_planets_dict(planets_raw, lagna_idx)

        if request.gem_planet:
            result = check_gem_compatibility(
                gem_planet=request.gem_planet,
                lagna_rashi=lagna_rashi,
                planets=planets_dict,
            )
        else:
            result = recommend_gems(
                lagna_rashi=lagna_rashi,
                planets=planets_dict,
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating gem recommendation: {e!s}",
        ) from e


@app.post("/api/v1/analysis/atmakaraka", tags=["Analysis"])
async def get_atmakaraka_details(request: BirthDataRequest):
    """Get comprehensive Atmakaraka (soul indicator) analysis."""
    try:
        from packages.core.src import BirthChart, Planet, Rashi
        from packages.self.src.jaimini import get_atmakaraka_analysis

        jd = request_to_jd(request)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()

        sign_map = {
            "aries": Rashi.ARIES,
            "taurus": Rashi.TAURUS,
            "gemini": Rashi.GEMINI,
            "cancer": Rashi.CANCER,
            "leo": Rashi.LEO,
            "virgo": Rashi.VIRGO,
            "libra": Rashi.LIBRA,
            "scorpio": Rashi.SCORPIO,
            "sagittarius": Rashi.SAGITTARIUS,
            "capricorn": Rashi.CAPRICORN,
            "aquarius": Rashi.AQUARIUS,
            "pisces": Rashi.PISCES,
        }
        planet_map = {
            "sun": Planet.SUN,
            "moon": Planet.MOON,
            "mars": Planet.MARS,
            "mercury": Planet.MERCURY,
            "jupiter": Planet.JUPITER,
            "venus": Planet.VENUS,
            "saturn": Planet.SATURN,
            "rahu": Planet.RAHU,
            "ketu": Planet.KETU,
        }

        planet_positions = {}
        for pname, data in planets_raw.items():
            pname_lower = pname.lower()
            if pname_lower not in planet_map:
                continue
            rashi_idx = int(data["longitude"] // 30)
            house = ((rashi_idx - lagna_idx) % 12) + 1
            planet_positions[planet_map[pname_lower]] = PlanetPosition(
                planet=planet_map[pname_lower],
                longitude=data["longitude"],
                latitude=data.get("latitude", 0.0),
                speed=data.get("speed", 0.0),
                rashi=sign_map.get(RASHI_NAMES[rashi_idx].lower(), Rashi.ARIES),
                rashi_degree=data["longitude"] % 30,
                nakshatra="ashwini",
                nakshatra_pada=1,
                nakshatra_lord=Planet.KETU,
                is_retrograde=data.get("is_retrograde", False),
                house=house,
            )

        house_cusps = HouseCusps(
            ascendant=houses_raw["ascendant"],
            mc=houses_raw.get("mc", 0.0),
            cusps=houses_raw["cusps"],
        )

        moon_rashi_idx = int(planets_raw["moon"]["longitude"] // 30)
        chart = BirthChart(
            user_id="api_request",
            birth_data=BirthData(
                datetime_utc=request.datetime,
                latitude=request.latitude,
                longitude=request.longitude,
                timezone="UTC",
            ),
            planets=planet_positions,
            houses=house_cusps,
            lagna_rashi=sign_map.get(lagna_rashi, Rashi.ARIES),
            moon_rashi=sign_map.get(RASHI_NAMES[moon_rashi_idx].lower(), Rashi.ARIES),
            moon_nakshatra="ashwini",
            ayanamsa=23.85,
            calculated_at=request.datetime,
        )

        result = get_atmakaraka_analysis(chart)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating atmakaraka analysis: {e!s}",
        ) from e


@app.post("/api/v1/forecast/daily", tags=["Forecast"])
async def get_daily_forecast_endpoint(request: ForecastRequest):
    """Generate a comprehensive daily forecast with day rating and recommendations."""
    try:
        from datetime import timedelta

        from packages.context.src.daily_forecast import get_daily_forecast

        utc_dt = request.datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_dt)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        planets_dict = _build_planets_dict(planets_raw, lagna_idx)
        moon_longitude = planets_raw["moon"]["longitude"]

        result = get_daily_forecast(
            birth_datetime=request.datetime.isoformat(),
            birth_lat=request.latitude,
            birth_lon=request.longitude,
            natal_planets=planets_dict,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
            query_date=request.query_date,
            location_lat=request.location_lat,
            location_lon=request.location_lon,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating daily forecast: {e!s}",
        ) from e


@app.post("/api/v1/forecast/weekly", tags=["Forecast"])
async def get_weekly_forecast_endpoint(request: ForecastRequest):
    """Generate a 7-day forecast with area-wise ratings."""
    try:
        from datetime import timedelta

        from packages.context.src.weekly_forecast import get_weekly_forecast

        utc_dt = request.datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_dt)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        planets_dict = _build_planets_dict(planets_raw, lagna_idx)
        moon_longitude = planets_raw["moon"]["longitude"]

        result = get_weekly_forecast(
            birth_datetime=request.datetime.isoformat(),
            birth_lat=request.latitude,
            birth_lon=request.longitude,
            natal_planets=planets_dict,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
            start_date=request.query_date,
            location_lat=request.location_lat,
            location_lon=request.location_lon,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating weekly forecast: {e!s}",
        ) from e


@app.post("/api/v1/forecast/monthly", tags=["Forecast"])
async def get_monthly_forecast_endpoint(request: ForecastRequest):
    """Generate a month-long forecast with major transits and area analysis."""
    try:
        from datetime import timedelta

        from packages.context.src.monthly_forecast import get_monthly_forecast

        utc_dt = request.datetime - timedelta(hours=request.timezone_offset)
        jd = get_julian_day(utc_dt)
        planets_raw = get_all_planets(jd, ayanamsa=request.ayanamsa)
        houses_raw = get_house_cusps(
            jd,
            request.latitude,
            request.longitude,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa,
        )

        lagna_idx = int(houses_raw["ascendant"] // 30)
        lagna_rashi = RASHI_NAMES[lagna_idx].lower()
        planets_dict = _build_planets_dict(planets_raw, lagna_idx)
        moon_longitude = planets_raw["moon"]["longitude"]

        result = get_monthly_forecast(
            birth_datetime=request.datetime.isoformat(),
            birth_lat=request.latitude,
            birth_lon=request.longitude,
            natal_planets=planets_dict,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
            month=request.month,
            year=request.year,
            location_lat=request.location_lat,
            location_lon=request.location_lon,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating monthly forecast: {e!s}",
        ) from e


# ============================================================================
# KP (Krishnamurti Paddhati) Analysis Endpoints
# ============================================================================


@app.get("/api/v1/analysis/kp-sublord", tags=["KP Analysis"])
async def get_kp_sublord_endpoint(longitude: float):
    """Get KP sign/star/sub-lord for a longitude."""
    try:
        from packages.self.src.kp import get_kp_sublord

        return get_kp_sublord(longitude)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in KP sub-lord calculation: {e!s}",
        ) from e


@app.post("/api/v1/analysis/kp-significators", tags=["KP Analysis"])
async def get_kp_significators_endpoint(request: dict):
    """Get KP significators for all houses."""
    try:
        from packages.self.src.kp import get_kp_significators

        planets = request.get("planets", {})
        cusps = [float(c) for c in request.get("cusps", [])]
        return get_kp_significators(planets, cusps)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in KP significator calculation: {e!s}",
        ) from e


@app.post("/api/v1/analysis/kp-prediction", tags=["KP Analysis"])
async def get_kp_prediction_endpoint(request: dict):
    """Get full KP prediction for a life question."""
    try:
        from packages.self.src.kp import get_kp_prediction

        planets = request.get("planets", {})
        cusps = [float(c) for c in request.get("cusps", [])]
        query_type = request.get("query_type", "career")
        return get_kp_prediction(planets, cusps, query_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in KP prediction: {e!s}",
        ) from e


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
