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
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"   Debug mode: {settings.debug}")

    # Initialize database connection pool if needed
    # (would use asyncpg pool here in production)

    yield

    # Shutdown
    print("🛑 Shutting down 108 API...")
    # Close database connections, cleanup resources


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
async def chat_with_agent(request: ChatRequest):
    """
    Chat with the 108 AI assistant.

    The agent uses your birth chart context (if available) to provide
    personalized astrological guidance.
    """
    try:
        # For now, return a placeholder response
        # In production, this would invoke the LangGraph agent

        # TODO: Integrate with packages/guide/agent.py when langgraph is available

        return ChatResponse(
            response=f"I received your message: '{request.message}'. "
            "The full AI agent integration is coming soon. "
            "For now, you can use the chart and analysis endpoints.",
            user_id=request.user_id,
            metadata={"status": "placeholder", "agent_available": False},
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
async def get_user_profile(_user_id: str):
    """Get user profile and birth chart."""
    # TODO: Implement with memory package
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="User management coming soon"
    )


@app.post("/api/v1/users", tags=["Users"])
async def create_user_profile(_birth_data: BirthDataRequest):
    """Create a new user profile with birth data."""
    # TODO: Implement with memory package
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="User management coming soon"
    )


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
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
