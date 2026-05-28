"""
108 Agent Tools

Tools that the Guide agent can invoke for calculations, lookups, and memory operations.
These wrap the underlying packages and MCP servers.

This module provides a unified interface to all astrological calculation and data
retrieval capabilities needed by the LangGraph-based Guide agent.
"""

import logging
import sys
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar

# Setup package imports
PACKAGES_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PACKAGES_ROOT))

# Import context package functions
from packages.context.src import (  # noqa: E402
    calculate_all_inauspicious,
    calculate_choghadiya,
    calculate_rahu_kaal,
    check_dhaiya,
    check_sade_sati,
    evaluate_muhurta,
    find_next_good_muhurta,
    get_current_dasha,
    get_mahadasha_sequence,
    is_planet_favorable_in_house,
)
from packages.core.src import (  # noqa: E402
    Planet,
    Rashi,
    longitude_to_rashi,
)
from packages.cosmos.src import (  # noqa: E402
    RASHI_NAMES,
    get_all_planets,
    get_ayanamsa,
    get_divisional_chart,
    get_house_cusps,
    get_house_lord,
    get_julian_day,
    get_navamsha,
    get_panchanga,
    get_planets_in_house,
    get_varga_vimshopaka,
    longitude_to_nakshatra,
)
from packages.self.src import (  # noqa: E402
    DoshaDetector,
    StrengthCalculator,
    YogaDetector,
)

logger = logging.getLogger(__name__)


class ChartCache:
    """Cache birth chart calculations to avoid expensive recalculation.

    Uses user_id + birth datetime as cache key. Thread-safe via dict operations.
    """

    _cache: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def get_or_calculate(
        cls,
        user_id: str,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
        house_system: str = "placidus",
    ) -> dict[str, Any]:
        """Get cached chart or calculate and cache it.

        Args:
            user_id: User identifier
            birth_datetime: Birth date and time
            latitude: Birth location latitude
            longitude: Birth location longitude
            ayanamsa: Ayanamsa system
            house_system: House system

        Returns:
            Birth chart dictionary
        """
        cache_key = f"{user_id}:{birth_datetime.isoformat()}:{latitude}:{longitude}"
        if cache_key in cls._cache:
            logger.debug(f"Chart cache hit for {user_id}")
            return cls._cache[cache_key]

        # Calculate chart
        tools = get_tools()
        chart = tools.get_birth_chart(birth_datetime, latitude, longitude, ayanamsa, house_system)

        if chart.get("success"):
            cls._cache[cache_key] = chart
            logger.debug(f"Chart cached for {user_id}")

        return chart

    @classmethod
    def invalidate(cls, user_id: str) -> None:
        """Remove cached charts for a user."""
        keys_to_remove = [k for k in cls._cache if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del cls._cache[key]

    @classmethod
    def clear(cls) -> None:
        """Clear entire cache."""
        cls._cache.clear()


class ActivityType(StrEnum):
    """Types of activities for muhurta evaluation."""

    MARRIAGE = "marriage"
    TRAVEL = "travel"
    BUSINESS_START = "business_start"
    SURGERY = "surgery"
    VEHICLE_PURCHASE = "vehicle_purchase"
    HOME_ENTRY = "home_entry"
    EDUCATION_START = "education_start"
    INVESTMENT = "investment"
    MEETING = "meeting"
    CEREMONY = "ceremony"


class AstrologyTools:
    """
    Collection of astrological calculation tools for the Guide agent.

    This class provides a unified interface to all computational astrological functions,
    organizing them into logical groups:

    - Ephemeris & Birth Chart: Core planetary positions and chart calculations
    - Divisional Charts: D2-D60 detailed analysis
    - Dasha (Timing): Vimshottari dasha periods and predictions
    - Transits: Transit analysis (Gochara), Sade Sati, Dhaiya
    - Yogas: Auspicious combinations and patterns
    - Doshas: Challenging combinations and remedies
    - Muhurta: Timing analysis for activities
    - Panchanga: Daily astrological almanac
    - Strength: Planetary strength calculations
    """

    def __init__(self):
        """Initialize astrological tools with detectors and calculators."""
        self.yoga_detector = YogaDetector()
        self.dosha_detector = DoshaDetector()
        self.strength_calc = StrengthCalculator()
        logger.info("AstrologyTools initialized")

    # ===================
    # EPHEMERIS & BIRTH CHART TOOLS
    # ===================

    def get_birth_chart(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
        house_system: str = "placidus",
    ) -> dict[str, Any]:
        """
        Calculate complete birth chart for a person.

        This is the foundational calculation that provides:
        - Planetary positions in zodiacal signs
        - House placements and lords
        - Nakshatra information
        - Lagna (Ascendant) details

        Args:
            birth_datetime: Birth date and time (should be in UTC)
            latitude: Birth location latitude (-90 to 90)
            longitude: Birth location longitude (-180 to 180)
            ayanamsa: Ayanamsa system - "lahiri" (default), "raman", "krishnamurti", etc.
            house_system: House system - "placidus" (default), "koch", "whole_sign", etc.

        Returns:
            Dictionary containing:
            {
                "birth_datetime": ISO format string,
                "location": {"latitude": float, "longitude": float},
                "ayanamsa": str,
                "house_system": str,
                "lagna": {"sign": str, "degree": float, "nakshatra": str, "pada": int},
                "sun": {...planet details...},
                "moon": {...planet details...},
                ... all 9 planets,
                "houses": {"1": {...}, "2": {...}, ..., "12": {...}},
                "planetary_aspects": {...}
            }
        """
        try:
            jd = get_julian_day(birth_datetime)
            ayanamsa_value = get_ayanamsa(jd, ayanamsa)

            # Get all planetary positions
            planets = get_all_planets(jd)

            # Get house cusps and ascendant
            houses = get_house_cusps(jd, latitude, longitude, house_system=house_system)
            ascendant = houses.get("ascendant", 0)

            # Determine lagna details
            lagna_sign, _ = longitude_to_rashi(ascendant)
            lagna_nak = longitude_to_nakshatra(ascendant)

            # Build planets dictionary with rashi information
            planets_data = {}
            for planet_name, position in planets.items():
                planet_sign, _ = longitude_to_rashi(position["longitude"])
                nakshatra = longitude_to_nakshatra(position["longitude"])

                planets_data[planet_name] = {
                    "longitude": round(position["longitude"], 2),
                    "latitude": round(position.get("latitude", 0), 2),
                    "sign": planet_sign.value,
                    "sign_number": planet_sign.value.lower(),
                    "degree_in_sign": round(position["longitude"] % 30, 2),
                    "nakshatra": nakshatra["name"],
                    "nakshatra_number": nakshatra["number"],
                    "nakshatra_pada": nakshatra["pada"],
                    "retrograde": position.get("retrograde", False),
                    "speed": round(position.get("speed", 0), 4),
                }

            # Build houses dictionary with lord information
            houses_data = {}
            for house_num in range(1, 13):
                cusps_key = f"house_{house_num}"
                if cusps_key in houses:
                    house_long = houses[cusps_key]
                    house_sign, _ = longitude_to_rashi(house_long)
                    house_lord_planet = get_house_lord(house_num, lagna_sign)
                    planets_in_house = get_planets_in_house(house_num, planets_data)

                    houses_data[str(house_num)] = {
                        "cusp_longitude": round(house_long, 2),
                        "sign": house_sign.value,
                        "lord": house_lord_planet.value,
                        "planets": planets_in_house,
                    }

            return {
                "birth_datetime": birth_datetime.isoformat(),
                "location": {"latitude": latitude, "longitude": longitude},
                "ayanamsa_value": round(ayanamsa_value, 4),
                "ayanamsa_system": ayanamsa,
                "house_system": house_system,
                "lagna": {
                    "sign": lagna_sign.value,
                    "degree": round(ascendant, 2),
                    "degree_in_sign": round(ascendant % 30, 2),
                    "nakshatra": lagna_nak["name"],
                    "nakshatra_pada": lagna_nak["pada"],
                },
                "planets": planets_data,
                "houses": houses_data,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating birth chart: {e!s}")
            return {"success": False, "error": str(e)}

    def get_current_positions(self, ayanamsa: str = "lahiri") -> dict[str, Any]:  # noqa: ARG002
        """
        Get current planetary positions.

        Useful for transit analysis and real-time queries.

        Args:
            ayanamsa: Ayanamsa system (default: lahiri)

        Returns:
            Dictionary with timestamp and current planet positions
        """
        try:
            now = datetime.utcnow()
            jd = get_julian_day(now)
            planets = get_all_planets(jd)

            planets_data = {}
            for planet_name, position in planets.items():
                planet_sign, _ = longitude_to_rashi(position["longitude"])
                planets_data[planet_name] = {
                    "longitude": round(position["longitude"], 2),
                    "sign": planet_sign.value,
                    "degree_in_sign": round(position["longitude"] % 30, 2),
                    "retrograde": position.get("retrograde", False),
                }

            return {
                "timestamp": now.isoformat(),
                "planets": planets_data,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting current positions: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # DIVISIONAL CHART TOOLS
    # ===================

    def get_navamsha_chart(self, planets: dict[str, dict]) -> dict[str, Any]:
        """
        Calculate Navamsha (D9) chart - most important divisional chart.

        D9 shows marriage, spouse, dharma, and soul's purpose.

        Args:
            planets: Dictionary of planet positions with "longitude" key

        Returns:
            Dictionary with Navamsha positions for each planet
        """
        try:
            navamsha_data = {}
            for planet_name, data in planets.items():
                if isinstance(data, dict) and "longitude" in data:
                    nav = get_navamsha(data["longitude"])
                    navamsha_data[planet_name] = {
                        "rashi": nav["rashi_name"],
                        "degree_in_sign": round(nav["degree_in_sign"], 2),
                        "lord": nav.get("lord", ""),
                    }

            return {
                "navamsha": navamsha_data,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating Navamsha: {e!s}")
            return {"success": False, "error": str(e)}

    def get_divisional_charts(
        self, planets: dict[str, dict], charts: list[int] | None = None
    ) -> dict[str, Any]:
        """
        Calculate multiple divisional charts (D2, D3, D9, D10, etc.).

        Args:
            planets: Dictionary of planet positions with "longitude" key
            charts: List of divisional chart numbers to calculate (default: [2, 3, 9, 10, 12, 24, 30, 60])

        Returns:
            Dictionary with positions in requested divisional charts
        """
        try:
            if charts is None:
                charts = [2, 3, 9, 10, 12, 24, 30, 60]  # Most commonly used

            # Normalize input: cosmos.get_divisional_chart wants {planet: longitude_float}
            # but callers may pass {planet: {longitude, ...}}. Flatten if dict-of-dicts.
            normalized: dict[str, float] = {}
            for name, data in planets.items():
                if isinstance(data, dict):
                    normalized[name] = float(data.get("longitude", 0))
                else:
                    normalized[name] = float(data)

            divisional_data = {}
            for d_num in charts:
                d_chart = get_divisional_chart(normalized, d_num)
                divisional_data[f"D{d_num}"] = d_chart

            return {
                "divisional_charts": divisional_data,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating divisional charts: {e!s}")
            return {"success": False, "error": str(e)}

    def get_varga_strength(
        self, planets: dict[str, dict], planet_name: str, charts: list[int] | None = None
    ) -> dict[str, Any]:
        """
        Calculate planetary strength across multiple divisional charts (Vimshopaka).

        Shows how strong a planet is when viewed across different aspects of life.

        Args:
            planets: Dictionary of planet positions
            planet_name: Name of planet to analyze
            charts: List of divisional charts to consider

        Returns:
            Vimshopaka strength analysis
        """
        try:
            if charts is None:
                charts = [1, 2, 3, 9, 12, 24, 27, 30, 60]

            if planet_name in planets and "longitude" in planets[planet_name]:
                strength = get_varga_vimshopaka(planets, planet_name, charts)
                return {
                    "planet": planet_name,
                    "vimshopaka_strength": strength,
                    "success": True,
                }
            else:
                return {"success": False, "error": f"Planet {planet_name} not found"}
        except Exception as e:
            logger.error(f"Error calculating Varga strength: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # DASHA (TIMING) TOOLS
    # ===================

    def get_dasha_info(
        self, birth_datetime: datetime, moon_longitude: float, query_date: datetime | None = None
    ) -> dict[str, Any]:
        """
        Get current dasha information for a person.

        Dasha (timing periods) are the primary tool for predictions in Vedic astrology.
        Returns the current Mahadasha, Antardasha, and Pratyantardasha (3-level timing).

        Args:
            birth_datetime: Birth date and time (UTC)
            moon_longitude: Moon's longitude at birth
            query_date: Date to check (default: now)

        Returns:
            Dictionary with:
            {
                "current_mahadasha": {"lord": str, "start": datetime, "end": datetime, "years": int},
                "current_antardasha": {...},
                "current_pratyantardasha": {...},
                "dasha_timeline": [...next 5 mahadashas...],
                "time_in_current": {"mahadasha_percent": float, "antardasha_percent": float}
            }
        """
        try:
            # Normalize tz: if birth has tz but query doesn't (or vice versa), align them.
            if query_date is None:
                query_date = (
                    datetime.now(tz=birth_datetime.tzinfo)
                    if birth_datetime.tzinfo
                    else datetime.utcnow()
                )
            if birth_datetime.tzinfo is not None and query_date.tzinfo is None:
                query_date = query_date.replace(tzinfo=birth_datetime.tzinfo)
            elif birth_datetime.tzinfo is None and query_date.tzinfo is not None:
                query_date = query_date.replace(tzinfo=None)

            # Get current dasha — returns nested dicts: {"mahadasha": {"lord", "start_date", "end_date", ...}}
            current = get_current_dasha(birth_datetime, moon_longitude, query_date)

            # Get timeline of mahadashas
            timeline = get_mahadasha_sequence(birth_datetime, moon_longitude)

            # Extract nested dasha data
            maha = current.get("mahadasha", {}) if current else {}
            antar = current.get("antardasha", {}) if current else {}
            pratyantar = current.get("pratyantardasha", {}) if current else {}

            maha_start = maha.get("start_date")
            maha_end = maha.get("end_date")
            anta_start = antar.get("start_date")
            anta_end = antar.get("end_date")

            # Calculate progress percentages
            maha_percent = 0.0
            anta_percent = 0.0

            if maha_start and maha_end:
                total_days = (maha_end - maha_start).days
                elapsed = (query_date - maha_start).days
                maha_percent = (elapsed / total_days * 100) if total_days > 0 else 0

            if anta_start and anta_end:
                total_days = (anta_end - anta_start).days
                elapsed = (query_date - anta_start).days
                anta_percent = (elapsed / total_days * 100) if total_days > 0 else 0

            return {
                "query_date": query_date.isoformat(),
                "current_mahadasha": {
                    "lord": maha.get("lord", ""),
                    "start": maha_start.isoformat() if maha_start else None,
                    "end": maha_end.isoformat() if maha_end else None,
                    "years": maha.get("years", 0),
                    "progress_percent": round(maha_percent, 1),
                },
                "current_antardasha": {
                    "lord": antar.get("lord", ""),
                    "start": anta_start.isoformat() if anta_start else None,
                    "end": anta_end.isoformat() if anta_end else None,
                    "years": antar.get("years", 0),
                    "progress_percent": round(anta_percent, 1),
                },
                "current_pratyantardasha": {
                    "lord": pratyantar.get("lord", ""),
                    "start": pratyantar.get("start_date", "").isoformat()
                    if pratyantar.get("start_date")
                    else None,
                    "end": pratyantar.get("end_date", "").isoformat()
                    if pratyantar.get("end_date")
                    else None,
                },
                "current_sookshma": {
                    "lord": current.get("sookshma_dasha", {}).get("lord", "") if current else "",
                    "start": current.get("sookshma_dasha", {}).get("start_date", "").isoformat()
                    if current and current.get("sookshma_dasha", {}).get("start_date")
                    else None,
                    "end": current.get("sookshma_dasha", {}).get("end_date", "").isoformat()
                    if current and current.get("sookshma_dasha", {}).get("end_date")
                    else None,
                    "days_remaining": round(
                        current.get("sookshma_dasha", {}).get("days_remaining", 0), 1
                    )
                    if current and current.get("sookshma_dasha")
                    else None,
                },
                "current_prana": {
                    "lord": current.get("prana_dasha", {}).get("lord", "") if current else "",
                    "start": current.get("prana_dasha", {}).get("start_date", "").isoformat()
                    if current and current.get("prana_dasha", {}).get("start_date")
                    else None,
                    "end": current.get("prana_dasha", {}).get("end_date", "").isoformat()
                    if current and current.get("prana_dasha", {}).get("end_date")
                    else None,
                    "days_remaining": round(
                        current.get("prana_dasha", {}).get("days_remaining", 0), 1
                    )
                    if current and current.get("prana_dasha")
                    else None,
                },
                "current_deha": {
                    "lord": current.get("deha_dasha", {}).get("lord", "") if current else "",
                    "start": current.get("deha_dasha", {}).get("start_date", "").isoformat()
                    if current and current.get("deha_dasha", {}).get("start_date")
                    else None,
                    "end": current.get("deha_dasha", {}).get("end_date", "").isoformat()
                    if current and current.get("deha_dasha", {}).get("end_date")
                    else None,
                    "hours_remaining": current.get("deha_dasha", {}).get("hours_remaining")
                    if current and current.get("deha_dasha")
                    else None,
                },
                "dasha_timeline": timeline[:10] if timeline else [],
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating dasha info: {e!s}")
            return {"success": False, "error": str(e)}

    def get_dasha_timeline(
        self, birth_datetime: datetime, moon_longitude: float, years: int = 50
    ) -> dict[str, Any]:
        """
        Get full dasha timeline for specified years ahead.

        Useful for long-term planning and understanding life timing.

        Args:
            birth_datetime: Birth date and time (UTC)
            moon_longitude: Moon's longitude at birth
            years: Years ahead to calculate (default: 50)

        Returns:
            List of dasha periods with dates and details
        """
        try:
            timeline = get_mahadasha_sequence(birth_datetime, moon_longitude)

            # Filter to next N years (align tz with birth_datetime to compare end_dates)
            if birth_datetime.tzinfo is not None:
                start_date = datetime.now(tz=birth_datetime.tzinfo)
            else:
                start_date = datetime.utcnow()
            cutoff_date = start_date + timedelta(days=365 * years)

            filtered = []
            for period in timeline:
                end = period.get("end_date")
                if end is None:
                    continue
                # Normalize tz of period end vs cutoff
                if end.tzinfo and not cutoff_date.tzinfo:
                    cutoff_cmp = cutoff_date.replace(tzinfo=end.tzinfo)
                elif not end.tzinfo and cutoff_date.tzinfo:
                    end_cmp = end.replace(tzinfo=cutoff_date.tzinfo)
                    if end_cmp <= cutoff_date:
                        filtered.append(period)
                    continue
                else:
                    cutoff_cmp = cutoff_date
                if end <= cutoff_cmp:
                    filtered.append(period)

            return {
                "start_date": start_date.isoformat(),
                "end_date": cutoff_date.isoformat(),
                "dasha_periods": [
                    {
                        "lord": p["lord"],
                        "start_date": p["start_date"].isoformat()
                        if hasattr(p["start_date"], "isoformat")
                        else str(p["start_date"]),
                        "end_date": p["end_date"].isoformat()
                        if hasattr(p["end_date"], "isoformat")
                        else str(p["end_date"]),
                        "years": p.get("years", 0),
                    }
                    for p in filtered
                ],
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating dasha timeline: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # TRANSIT (GOCHARA) TOOLS
    # ===================

    def get_transit_analysis(
        self, natal_chart: dict[str, Any], transit_date: datetime | None = None
    ) -> dict[str, Any]:
        """
        Analyze current transits relative to natal chart.

        Includes:
        - Gochara (house transits relative to Moon)
        - Sade Sati (Saturn 7.5-year cycle)
        - Dhaiya (Saturn in 4th/8th from Moon)
        - Key planet transits (Jupiter, Saturn, Rahu)

        Args:
            natal_chart: Natal birth chart dictionary
            transit_date: Date to analyze (default: now)

        Returns:
            Dictionary with transit analysis
        """
        try:
            transit_date = transit_date or datetime.utcnow()

            # Get current positions
            jd = get_julian_day(transit_date)
            transit_planets = get_all_planets(jd)

            # Extract natal moon sign (check "sign", "rashi_name", or compute from longitude)
            natal_moon = natal_chart.get("planets", {}).get("moon", {})
            natal_moon_rashi = natal_moon.get("sign") or natal_moon.get("rashi_name")
            if not natal_moon_rashi and natal_moon.get("longitude") is not None:
                natal_moon_rashi = RASHI_NAMES[int(float(natal_moon["longitude"]) / 30) % 12]
            if natal_moon_rashi:
                natal_moon_rashi = natal_moon_rashi.title()

            if not natal_moon_rashi:
                return {"success": False, "error": "Natal moon sign not found"}

            # Convert sign name to index
            sign_to_idx = {
                "Aries": 0,
                "Taurus": 1,
                "Gemini": 2,
                "Cancer": 3,
                "Leo": 4,
                "Virgo": 5,
                "Libra": 6,
                "Scorpio": 7,
                "Sagittarius": 8,
                "Capricorn": 9,
                "Aquarius": 10,
                "Pisces": 11,
            }
            natal_moon_idx = sign_to_idx.get(natal_moon_rashi, 0)

            # Analyze key transits
            transit_analysis = {
                "transit_date": transit_date.isoformat(),
                "natal_moon": natal_moon_rashi,
                "transits": {},
            }

            for planet in ["saturn", "jupiter", "rahu"]:
                if planet in transit_planets:
                    planet_long = transit_planets[planet]["longitude"]
                    planet_sign, _ = longitude_to_rashi(planet_long)
                    sign_name = planet_sign.value.title()
                    transit_idx = sign_to_idx.get(sign_name, 0)
                    house_from_moon = ((transit_idx - natal_moon_idx) % 12) + 1

                    transit_analysis["transits"][planet] = {
                        "sign": sign_name,
                        "house_from_moon": house_from_moon,
                        "degree": round(planet_long, 2),
                        "favorable": is_planet_favorable_in_house(planet, house_from_moon),
                    }

            # Check Sade Sati
            saturn_idx = sign_to_idx.get(
                transit_analysis["transits"].get("saturn", {}).get("sign", ""), 0
            )
            sade_sati = check_sade_sati(natal_moon_idx, saturn_idx)
            transit_analysis["sade_sati"] = sade_sati

            # Check Dhaiya
            dhaiya = check_dhaiya(natal_moon_idx, saturn_idx)
            transit_analysis["dhaiya"] = dhaiya

            transit_analysis["success"] = True
            return transit_analysis
        except Exception as e:
            logger.error(f"Error analyzing transits: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # YOGA (AUSPICIOUS COMBINATIONS) TOOLS
    # ===================

    def _dict_to_birth_chart(self, natal_chart: dict[str, Any]) -> Any:
        """Convert a natal_chart dict to a BirthChart model for detectors.

        Args:
            natal_chart: Dict with "planets" and "lagna" keys.

        Returns:
            BirthChart pydantic model.
        """
        from packages.core.src.models import BirthChart, BirthData, HouseCusps, PlanetPosition

        planets_raw = natal_chart.get("planets", {})
        lagna_info = natal_chart.get("lagna", {})
        lagna_str = (lagna_info.get("sign") or "aries").lower()
        lagna_rashi = Rashi(lagna_str)
        lagna_idx = list(Rashi).index(lagna_rashi)

        planet_positions: dict[Planet, PlanetPosition] = {}
        for name, data in planets_raw.items():
            if not isinstance(data, dict):
                continue
            try:
                planet_enum = Planet(name.lower())
                lon = float(data.get("longitude", 0))
                rashi_idx = int(lon // 30) % 12
                rashi_enum = list(Rashi)[rashi_idx]
                house = data.get("house", ((rashi_idx - lagna_idx) % 12) + 1)
                nak = data.get("nakshatra", "")
                nak_pada = data.get("nakshatra_pada", 1)
                try:
                    nak_lord = Planet(data.get("nakshatra_lord", name).lower())
                except (ValueError, AttributeError):
                    nak_lord = planet_enum

                planet_positions[planet_enum] = PlanetPosition(
                    planet=planet_enum,
                    longitude=lon,
                    latitude=float(data.get("latitude", 0.0)),
                    speed=float(data.get("speed", 0.0)),
                    rashi=rashi_enum,
                    rashi_degree=lon % 30,
                    nakshatra=nak if isinstance(nak, str) else str(nak),
                    nakshatra_pada=max(1, min(4, int(nak_pada))),
                    nakshatra_lord=nak_lord,
                    is_retrograde=bool(data.get("is_retrograde", False)),
                    house=int(house),
                )
            except (ValueError, KeyError):
                continue

        moon_pos = planet_positions.get(Planet.MOON)
        moon_rashi = moon_pos.rashi if moon_pos else lagna_rashi
        moon_nak = moon_pos.nakshatra if moon_pos else ""

        return BirthChart(
            user_id="tool_call",
            birth_data=BirthData(
                datetime_utc=datetime.utcnow(),
                latitude=0.0,
                longitude=0.0,
                timezone="UTC",
            ),
            planets=planet_positions,
            houses=HouseCusps(
                ascendant=lagna_idx * 30.0,
                mc=0.0,
                cusps=[(lagna_idx * 30 + i * 30) % 360 for i in range(12)],
            ),
            lagna_rashi=lagna_rashi,
            moon_rashi=moon_rashi,
            moon_nakshatra=moon_nak,
            ayanamsa=23.85,
            calculated_at=datetime.utcnow(),
        )

    def detect_yogas(self, natal_chart: dict[str, Any]) -> dict[str, Any]:
        """
        Detect all auspicious yogas (planetary combinations) in birth chart.

        Includes:
        - Pancha Mahapurusha yogas (exalted planets in kendras)
        - Raja yogas (lord of trine and kendra conjunction)
        - Dhana yogas (wealth combinations)
        - Yogas related to career, intelligence, relationships, etc.

        Args:
            natal_chart: Complete birth chart dictionary

        Returns:
            Dictionary with detected yogas and their interpretations
        """
        try:
            chart = self._dict_to_birth_chart(natal_chart)
            detected = self.yoga_detector.detect_all_yogas(chart)

            # Convert pydantic models to dicts for JSON serialization
            yogas_list = []
            for y in detected:
                yogas_list.append(
                    {
                        "yoga_id": y.yoga_id,
                        "name": y.name,
                        "category": y.category.value
                        if hasattr(y.category, "value")
                        else str(y.category),
                        "is_present": y.is_present,
                        "strength": y.strength,
                        "involved_planets": [p.value for p in y.involved_planets],
                        "description": y.description,
                    }
                )

            return {
                "yogas": yogas_list,
                "yoga_count": len(yogas_list),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error detecting yogas: {e!s}")
            return {"success": False, "error": str(e)}

    def get_yoga_details(self, yoga_name: str) -> dict[str, Any]:
        """
        Get detailed information about a specific yoga from the knowledge base.

        Args:
            yoga_name: Name of yoga (e.g., "Gajakesari", "Rajayoga")

        Returns:
            Details about the yoga, its benefits, and conditions
        """
        try:
            from packages.core.src.knowledge_loader import get_yoga_rules

            yoga_rules = get_yoga_rules()
            yoga_name_lower = yoga_name.lower().strip()

            # Search through yoga categories for matching name
            for category, yoga_list in yoga_rules.items():
                if not isinstance(yoga_list, list):
                    continue
                for yoga in yoga_list:
                    if not isinstance(yoga, dict):
                        continue
                    name = yoga.get("name", "")
                    if name.lower() == yoga_name_lower:
                        return {
                            "yoga": name,
                            "category": category,
                            "description": yoga.get("description", ""),
                            "conditions": yoga.get("conditions", yoga.get("rules", [])),
                            "effects": yoga.get("effects", []),
                            "planets_involved": yoga.get("planets_involved", []),
                            "strength": yoga.get("strength", "medium"),
                            "success": True,
                        }

            # Not found in structured data - return basic info
            return {
                "yoga": yoga_name,
                "description": f"Yoga '{yoga_name}' not found in knowledge base",
                "conditions": [],
                "effects": [],
                "success": True,
                "found": False,
            }
        except Exception as e:
            logger.error(f"Error getting yoga details: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # DOSHA (CHALLENGING COMBINATIONS) TOOLS
    # ===================

    def detect_doshas(self, natal_chart: dict[str, Any]) -> dict[str, Any]:
        """
        Detect challenging combinations (doshas) in birth chart.

        Includes:
        - Mangal Dosha (Mars affliction on marriage)
        - Kaal Sarp Dosha (planets between Rahu-Ketu)
        - Pitra Dosha (ancestral afflictions)
        - Combustion (planets too close to Sun)
        - Planetary wars

        Args:
            natal_chart: Complete birth chart dictionary

        Returns:
            Dictionary with detected doshas and remedies
        """
        try:
            chart = self._dict_to_birth_chart(natal_chart)
            detected = self.dosha_detector.detect_all(chart)

            # Convert pydantic models to dicts for JSON serialization
            doshas_list = []
            for d in detected:
                doshas_list.append(
                    {
                        "dosha_id": d.dosha_id,
                        "name": d.name,
                        "is_present": d.is_present,
                        "severity": d.severity,
                        "involved_planets": [p.value for p in d.involved_planets],
                        "description": d.description,
                        "remedies": d.remedies,
                    }
                )

            return {
                "doshas": doshas_list,
                "dosha_count": len(doshas_list),
                "remedies_available": any(d.get("remedies") for d in doshas_list),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error detecting doshas: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # PLANETARY STRENGTH TOOLS
    # ===================

    def get_planet_strength(
        self, planet: str, position: dict[str, Any], house_num: int, lagna_sign: str
    ) -> dict[str, Any]:
        """
        Calculate comprehensive planetary strength (Shadbala).

        Components:
        - Sthana Bala (positional strength)
        - Dig Bala (directional strength)
        - Kala Bala (temporal strength)
        - Chesta Bala (motional strength)
        - Naisargika Bala (natural strength)
        - Drik Bala (aspectual strength)

        Args:
            planet: Planet name
            position: Planet position dict with longitude, sign, etc.
            house_num: House number (1-12)
            lagna_sign: Lagna sign name

        Returns:
            Dictionary with strength components and overall strength
        """
        try:
            planet_enum = Planet(planet.lower())
            rashi_enum = Rashi(lagna_sign.lower())

            # Reuse _dict_to_birth_chart helper which fills in all required
            # BirthChart fields (user_id, birth_data, houses, etc.) with defaults.
            chart_dict = {
                "planets": {planet: position},
                "lagna": {"sign": lagna_sign},
            }
            natal = self._dict_to_birth_chart(chart_dict)

            shadbala = self.strength_calc.calculate_shadbala(planet_enum, natal)
            dignity_obj = natal.planets.get(planet_enum)
            dignity = self.strength_calc.get_planet_dignity(
                planet_enum, dignity_obj.rashi if dignity_obj else rashi_enum
            )

            return {
                "planet": planet,
                "house": house_num,
                "sign": lagna_sign,
                "dignity": dignity.value if hasattr(dignity, "value") else str(dignity),
                "shadbala": shadbala,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating planet strength: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # MUHURTA (AUSPICIOUS TIMING) TOOLS
    # ===================

    def check_muhurta(
        self, activity: str, datetime_to_check: datetime, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """
        Evaluate muhurta (auspicious timing) for an activity.

        Checks:
        - Tithi (lunar day)
        - Nakshatra (lunar mansion)
        - Yoga (Sun-Moon combination)
        - Karana (half lunar day)
        - Vara (weekday)
        - Rahu Kaal and other inauspicious periods
        - Choghadiya (8 periods per day)

        Args:
            activity: Activity type (marriage, travel, business_start, surgery, etc.)
            datetime_to_check: Date and time to evaluate
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Dictionary with muhurta evaluation and score
        """
        try:
            # cosmos.get_panchanga expects (datetime, latitude, longitude)
            panchanga = get_panchanga(datetime_to_check, latitude, longitude)

            # Evaluate muhurta
            result = evaluate_muhurta(activity, panchanga, datetime_to_check)

            # Check inauspicious periods — needs sunrise/sunset datetimes + weekday string
            try:
                from packages.cosmos.src import get_sunrise_sunset

                ss = get_sunrise_sunset(datetime_to_check.strftime("%Y-%m-%d"), latitude, longitude)
                sunrise_dt = ss.get("sunrise") if isinstance(ss.get("sunrise"), datetime) else None
                sunset_dt = ss.get("sunset") if isinstance(ss.get("sunset"), datetime) else None
                # Fallback: parse strings if needed
                if sunrise_dt is None and isinstance(ss.get("sunrise"), str):
                    sunrise_dt = datetime.fromisoformat(ss["sunrise"])
                if sunset_dt is None and isinstance(ss.get("sunset"), str):
                    sunset_dt = datetime.fromisoformat(ss["sunset"])
                weekday = datetime_to_check.strftime("%A").lower()
                if sunrise_dt and sunset_dt:
                    inauspicious = calculate_all_inauspicious(sunrise_dt, sunset_dt, weekday)
                else:
                    inauspicious = {}
            except Exception as inner_e:
                logger.warning(f"Inauspicious calc skipped: {inner_e}")
                inauspicious = {}

            result["inauspicious_periods"] = inauspicious
            result["success"] = True
            return result
        except Exception as e:
            logger.error(f"Error checking muhurta: {e!s}")
            return {"success": False, "error": str(e)}

    def find_good_muhurta(
        self,
        activity: str,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """
        Find good muhurta dates within a range for an activity.

        Args:
            activity: Activity type
            start_date: Start of search range
            end_date: End of search range
            latitude: Location latitude
            longitude: Location longitude
            max_results: Maximum number of results to return

        Returns:
            List of good muhurta times with scores
        """
        try:
            good_dates = find_next_good_muhurta(activity, start_date, end_date, latitude, longitude)

            return {
                "activity": activity,
                "search_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "good_muhurtas": good_dates[:max_results],
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error finding good muhurta: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # PANCHANGA (DAILY ALMANAC) TOOLS
    # ===================

    def get_today_panchanga(
        self, date: datetime | None = None, latitude: float = 28.6139, longitude: float = 77.2090
    ) -> dict[str, Any]:
        """
        Get today's Panchanga (5-part day system).

        Panchanga components:
        - Tithi: Lunar day (15 tithis per lunar fortnight)
        - Nakshatra: Lunar mansion (27 nakshatras)
        - Yoga: Sun-Moon combination (27 yogas)
        - Karana: Half lunar day (60 karanas)
        - Vara: Weekday (7 varas)

        Args:
            date: Date to get panchanga for (default: today)
            latitude: Location latitude (default: Delhi)
            longitude: Location longitude (default: Delhi)

        Returns:
            Complete Panchanga for the day
        """
        try:
            if date is None:
                date = datetime.utcnow()

            # cosmos.get_panchanga expects (datetime, latitude, longitude)
            panchanga = get_panchanga(date, latitude, longitude)

            # Get sunrise/sunset
            from packages.cosmos.src import get_sunrise_sunset

            try:
                sunrise_sunset = get_sunrise_sunset(date.strftime("%Y-%m-%d"), latitude, longitude)
            except Exception:
                sunrise_sunset = {}

            # Pull sun/moon longs for sign labels
            jd = get_julian_day(date)
            planets = get_all_planets(jd)
            sun_lon = planets["sun"]["longitude"]
            moon_lon = planets["moon"]["longitude"]

            return {
                "date": date.strftime("%Y-%m-%d"),
                "tithi": panchanga.get("tithi"),
                "nakshatra": panchanga.get("nakshatra"),
                "yoga": panchanga.get("yoga"),
                "karana": panchanga.get("karana"),
                "vara": panchanga.get("vara"),
                "sunrise": sunrise_sunset.get("sunrise"),
                "sunset": sunrise_sunset.get("sunset"),
                "sun_sign": self._lon_to_sign(sun_lon),
                "moon_sign": self._lon_to_sign(moon_lon),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting panchanga: {e!s}")
            return {"success": False, "error": str(e)}

    def get_choghadiya_timings(
        self, date: datetime | None = None, latitude: float = 28.6139, longitude: float = 77.2090
    ) -> dict[str, Any]:
        """
        Get Choghadiya timings (8 periods per day and night).

        Each Choghadiya has a lord and quality (auspicious, inauspicious, mixed).

        Args:
            date: Date to get choghadiya for
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Choghadiya periods with timings and qualities
        """
        try:
            if date is None:
                date = datetime.utcnow()

            # Get sunrise/sunset
            from packages.cosmos.src import get_sunrise_sunset

            sunrise_sunset = get_sunrise_sunset(date.strftime("%Y-%m-%d"), latitude, longitude)

            sunrise = datetime.fromisoformat(sunrise_sunset["sunrise"])
            sunset = datetime.fromisoformat(sunrise_sunset["sunset"])
            next_sunrise = sunrise + timedelta(days=1)

            daytime = calculate_choghadiya(sunrise, sunset, is_night=False)

            nighttime = calculate_choghadiya(sunset, next_sunrise, is_night=True)

            return {
                "date": date.strftime("%Y-%m-%d"),
                "sunrise": sunrise.isoformat(),
                "sunset": sunset.isoformat(),
                "daytime_choghadiya": daytime,
                "nighttime_choghadiya": nighttime,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting choghadiya: {e!s}")
            return {"success": False, "error": str(e)}

    def get_rahu_kaal(
        self, date: datetime | None = None, latitude: float = 28.6139, longitude: float = 77.2090
    ) -> dict[str, Any]:
        """
        Get Rahu Kaal timing (most inauspicious period of the day).

        Rahu Kaal is different for each weekday and lasts approximately 1.5 hours.

        Args:
            date: Date to get Rahu Kaal for
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Rahu Kaal start and end times
        """
        try:
            if date is None:
                date = datetime.utcnow()

            # Get sunrise/sunset
            from packages.cosmos.src import get_sunrise_sunset

            sunrise_sunset = get_sunrise_sunset(date.strftime("%Y-%m-%d"), latitude, longitude)

            sunrise = datetime.fromisoformat(sunrise_sunset["sunrise"])
            sunset = datetime.fromisoformat(sunrise_sunset["sunset"])
            weekday = date.strftime("%A").lower()

            rahu_kaal = calculate_rahu_kaal(sunrise, sunset, weekday)

            return {
                "date": date.strftime("%Y-%m-%d"),
                "weekday": weekday,
                "rahu_kaal_start": rahu_kaal["start"].isoformat(),
                "rahu_kaal_end": rahu_kaal["end"].isoformat(),
                "duration_minutes": rahu_kaal.get("duration_minutes", 0),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting Rahu Kaal: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # UTILITY METHODS
    # ===================

    # ===================
    # YOGA CANCELLATION & NEECHA BHANGA TOOLS
    # ===================

    def check_yoga_cancellations(
        self,
        yogas: list[dict[str, Any]],
        planets: dict[str, dict],
        lagna_rashi: str,
        sun_longitude: float,
    ) -> dict[str, Any]:
        """Check which detected yogas are cancelled by classical rules.

        Args:
            yogas: List of detected yoga dicts
            planets: Planet positions with longitude, sign, etc.
            lagna_rashi: Ascendant sign name
            sun_longitude: Sun's longitude

        Returns:
            Dictionary with original yogas, cancelled list, and surviving yogas
        """
        try:
            from packages.self.src.yoga_cancellation import apply_cancellations_to_chart

            result = apply_cancellations_to_chart(yogas, planets, lagna_rashi, sun_longitude)
            cancelled = [y for y in result if y.get("cancelled")]
            surviving = [y for y in result if not y.get("cancelled")]
            return {
                "total_yogas": len(yogas),
                "cancelled_count": len(cancelled),
                "surviving_count": len(surviving),
                "cancelled_yogas": cancelled,
                "surviving_yogas": surviving,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error checking yoga cancellations: {e!s}")
            return {"success": False, "error": str(e)}

    def detect_neecha_bhanga_yogas(
        self, planets: dict[str, dict], lagna_rashi: str
    ) -> dict[str, Any]:
        """Detect Neecha Bhanga Raja Yoga (cancellation of debilitation).

        Args:
            planets: Planet positions with longitude, sign, etc.
            lagna_rashi: Ascendant sign name

        Returns:
            Dictionary with debilitated planets and neecha bhanga results
        """
        try:
            from packages.self.src.yoga_detector import detect_neecha_bhanga

            results = []
            for planet_name, planet_data in planets.items():
                nb = detect_neecha_bhanga(planet_name, planet_data, planets, lagna_rashi)
                if nb.get("is_debilitated") or nb.get("has_neecha_bhanga"):
                    results.append(nb)
            return {
                "neecha_bhanga_results": results,
                "count": len(results),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error detecting neecha bhanga: {e!s}")
            return {"success": False, "error": str(e)}

    def detect_planetary_wars(self, planets: dict[str, dict]) -> dict[str, Any]:
        """Detect planetary wars (Graha Yuddha) between planets within 1 degree.

        Args:
            planets: Planet positions with longitude, sign, etc.

        Returns:
            Dictionary with detected wars and their effects
        """
        try:
            from packages.self.src.planetary_war import detect_planetary_wars as _detect_wars
            from packages.self.src.planetary_war import get_war_effects

            wars = _detect_wars(planets)
            war_details = []
            for war in wars:
                effects = get_war_effects(war.get("winner", ""), war.get("loser", ""))
                war_details.append({**war, "effects": effects})
            return {
                "planetary_wars": war_details,
                "war_count": len(war_details),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error detecting planetary wars: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # BHAVA CHALIT TOOL
    # ===================

    def get_bhava_chalit(
        self, planets: dict[str, dict], cusps: list[float], ascendant: float
    ) -> dict[str, Any]:
        """Calculate Bhava Chalit chart showing house-cusp-based placements.

        Args:
            planets: Planet positions with longitude
            cusps: House cusp longitudes (12 values)
            ascendant: Ascendant longitude

        Returns:
            Dictionary with bhava chalit data and shifted planets
        """
        try:
            from packages.cosmos.src.bhava_chalit import (
                calculate_bhava_chalit,
                get_shifted_planets,
            )

            chalit = calculate_bhava_chalit(planets, cusps, ascendant)
            shifted = get_shifted_planets(chalit)
            return {
                "bhava_chalit": chalit,
                "shifted_planets": shifted,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating bhava chalit: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # DASHA-TRANSIT CROSS ANALYSIS TOOLS
    # ===================

    def get_dasha_transit_analysis(
        self,
        natal_planets: dict[str, dict],
        current_transits: dict[str, dict],
        current_dasha: dict[str, Any],
        lagna_rashi: str,
        moon_rashi: str,
    ) -> dict[str, Any]:
        """Cross-analyze dasha periods with current transits.

        Args:
            natal_planets: Birth chart positions
            current_transits: Current transit positions
            current_dasha: Current dasha info (mahadasha, antardasha, pratyantardasha)
            lagna_rashi: Ascendant sign name
            moon_rashi: Moon sign name

        Returns:
            Dictionary with active themes, strongest house, period quality, score
        """
        try:
            from packages.context.src.dasha_transit import cross_analyze

            result = cross_analyze(
                natal_planets, current_transits, current_dasha, lagna_rashi, moon_rashi
            )
            return {"dasha_transit": result, "success": True}
        except Exception as e:
            logger.error(f"Error in dasha-transit analysis: {e!s}")
            return {"success": False, "error": str(e)}

    def get_transit_natal_aspects(
        self,
        natal_planets: dict[str, dict],
        transit_planets: dict[str, dict],
        orb: float = 5.0,
    ) -> dict[str, Any]:
        """Get aspects between transit and natal planets.

        Args:
            natal_planets: Birth chart positions
            transit_planets: Current transit positions
            orb: Aspect orb in degrees (default 5.0)

        Returns:
            Dictionary with list of transit-natal aspects
        """
        try:
            from packages.context.src.transit_aspects import (
                get_transit_natal_aspects as _get_aspects,
            )

            aspects = _get_aspects(natal_planets, transit_planets, orb)
            return {
                "transit_aspects": aspects,
                "aspect_count": len(aspects),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting transit-natal aspects: {e!s}")
            return {"success": False, "error": str(e)}

    def correlate_life_event(
        self,
        event_date: str,
        event_type: str,
        event_description: str,
        birth_datetime: str,
        natal_planets: dict[str, dict],
        moon_longitude: float,
        lagna_rashi: str,
    ) -> dict[str, Any]:
        """Correlate a life event with dasha and transit data.

        Args:
            event_date: ISO date of the event
            event_type: Type (career, marriage, health, money, etc.)
            event_description: User's description
            birth_datetime: ISO birth datetime
            natal_planets: Birth chart positions
            moon_longitude: Moon longitude at birth
            lagna_rashi: Ascendant sign name

        Returns:
            Dictionary with correlation score, dasha/transit at event, explanation
        """
        try:
            from packages.context.src.event_correlator import correlate_event

            result = correlate_event(
                event_date=event_date,
                event_type=event_type,
                event_description=event_description,
                birth_datetime=birth_datetime,
                natal_planets=natal_planets,
                moon_longitude=moon_longitude,
                lagna_rashi=lagna_rashi,
            )
            return {"correlation": result, "success": True}
        except Exception as e:
            logger.error(f"Error correlating event: {e!s}")
            return {"success": False, "error": str(e)}

    def get_upcoming_triggers(
        self,
        natal_planets: dict[str, dict],
        lagna_rashi: str,
        moon_rashi: str,
        start_date: str | None = None,
        days_ahead: int = 30,
        birth_datetime: str | None = None,
        moon_longitude: float | None = None,
    ) -> dict[str, Any]:
        """Find upcoming significant transit triggers.

        Args:
            natal_planets: Birth chart positions
            lagna_rashi: Ascendant sign name
            moon_rashi: Moon sign name
            start_date: ISO start date (default: today)
            days_ahead: Days to look ahead (default 30)
            birth_datetime: ISO birth datetime (for dasha changes)
            moon_longitude: Moon longitude (for dasha calculation)

        Returns:
            Dictionary with upcoming trigger events sorted by date
        """
        try:
            from packages.context.src.transit_tracker import (
                get_upcoming_triggers as _get_triggers,
            )

            sd = start_date or datetime.utcnow().isoformat()
            triggers = _get_triggers(
                natal_planets=natal_planets,
                lagna_rashi=lagna_rashi,
                moon_rashi=moon_rashi,
                start_date=sd,
                days_ahead=days_ahead,
                birth_datetime=birth_datetime,
                moon_longitude=moon_longitude,
            )
            return {
                "triggers": triggers,
                "trigger_count": len(triggers),
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting upcoming triggers: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # REMEDIES TOOL
    # ===================

    def get_remedies(
        self,
        current_dasha: str,
        active_doshas: list[str],
        weak_planets: list[str],
        lagna_rashi: str = "",
    ) -> dict[str, Any]:
        """Get prioritized remedy recommendations.

        Args:
            current_dasha: Current mahadasha lord name
            active_doshas: List of active dosha names
            weak_planets: List of weak planet names
            lagna_rashi: Ascendant sign name

        Returns:
            Dictionary with prioritized remedies
        """
        try:
            from packages.self.src.remedies import recommend_remedies

            # Convert simple strings to dicts expected by recommend_remedies
            dasha_dict = {"mahadasha_lord": current_dasha}
            dosha_dicts = [{"name": d} for d in active_doshas]
            planet_dicts = [{"planet": p} for p in weak_planets]

            result = recommend_remedies(
                current_dasha=dasha_dict,
                active_doshas=dosha_dicts,
                weak_planets=planet_dicts,
                lagna_rashi=lagna_rashi,
            )
            return {"remedies": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting remedies: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # SESSION 22 METHODS
    # ===================

    def get_synastry_report(
        self,
        native_birth_dt: datetime,
        native_lat: float,
        native_lon: float,
        partner_birth_dt: datetime,
        partner_lat: float,
        partner_lon: float,
        ayanamsa: str = "lahiri",
    ) -> dict[str, Any]:
        """Generate a synastry (relationship compatibility) report.

        Args:
            native_birth_dt: First person's birth datetime
            native_lat: First person's birth latitude
            native_lon: First person's birth longitude
            partner_birth_dt: Second person's birth datetime
            partner_lat: Second person's birth latitude
            partner_lon: Second person's birth longitude
            ayanamsa: Ayanamsa system

        Returns:
            Full synastry report with house overlays, cross aspects, composite chart
        """
        try:
            from packages.self.src.synastry import get_synastry_report as _synastry

            native_chart = self.get_birth_chart(native_birth_dt, native_lat, native_lon, ayanamsa)
            partner_chart = self.get_birth_chart(
                partner_birth_dt, partner_lat, partner_lon, ayanamsa
            )

            native_planets = native_chart.get("planets", {})
            partner_planets = partner_chart.get("planets", {})
            native_cusps = native_chart.get("houses", {}).get("cusps", [i * 30 for i in range(12)])
            partner_cusps = partner_chart.get("houses", {}).get(
                "cusps", [i * 30 for i in range(12)]
            )
            native_asc = native_chart.get("houses", {}).get("ascendant", 0.0)
            partner_asc = partner_chart.get("houses", {}).get("ascendant", 0.0)

            native_moon_nak = 1
            partner_moon_nak = 1
            if "moon" in native_planets:
                native_moon_nak = int((native_planets["moon"].get("longitude", 0) * 27) / 360) + 1
            if "moon" in partner_planets:
                partner_moon_nak = int((partner_planets["moon"].get("longitude", 0) * 27) / 360) + 1

            result = _synastry(
                native_planets=native_planets,
                native_cusps=native_cusps,
                partner_planets=partner_planets,
                partner_cusps=partner_cusps,
                native_ascendant=native_asc,
                partner_ascendant=partner_asc,
                native_moon_nakshatra=native_moon_nak,
                partner_moon_nakshatra=partner_moon_nak,
            )
            return {"synastry": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting synastry report: {e!s}")
            return {"success": False, "error": str(e)}

    def get_gem_recommendation(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
        gem_planet: str | None = None,
    ) -> dict[str, Any]:
        """Get personalized gemstone recommendation.

        Args:
            birth_datetime: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude
            ayanamsa: Ayanamsa system
            gem_planet: Specific planet gem to check (None for full recommendation)

        Returns:
            Gem recommendation with primary gem, supporting gems, contraindications
        """
        try:
            from packages.self.src.gem_recommender import (
                check_gem_compatibility,
                recommend_gems,
            )

            chart = self.get_birth_chart(birth_datetime, latitude, longitude, ayanamsa)
            planets = chart.get("planets", {})
            lagna_rashi = chart.get("lagna_rashi", "aries")

            if gem_planet:
                result = check_gem_compatibility(gem_planet, lagna_rashi, planets)
            else:
                result = recommend_gems(lagna_rashi, planets)

            return {"gems": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting gem recommendation: {e!s}")
            return {"success": False, "error": str(e)}

    def get_atmakaraka_analysis(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
    ) -> dict[str, Any]:
        """Get comprehensive Atmakaraka (soul indicator) analysis.

        Args:
            birth_datetime: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude
            ayanamsa: Ayanamsa system

        Returns:
            Atmakaraka details, Karakamsha, Ishta Devata, soul purpose
        """
        try:
            from packages.core.src import BirthChart, BirthData, HouseCusps, PlanetPosition
            from packages.self.src.jaimini import get_atmakaraka_analysis as _ak_analysis

            jd = get_julian_day(birth_datetime)
            planets_raw = get_all_planets(jd, ayanamsa=ayanamsa)
            houses_raw = get_house_cusps(jd, latitude, longitude, ayanamsa=ayanamsa)
            lagna_idx = int(houses_raw["ascendant"] // 30)

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
                pl = pname.lower()
                if pl not in planet_map:
                    continue
                rashi_idx = int(data["longitude"] // 30)
                house = ((rashi_idx - lagna_idx) % 12) + 1
                planet_positions[planet_map[pl]] = PlanetPosition(
                    planet=planet_map[pl],
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

            house_cusps_obj = HouseCusps(
                ascendant=houses_raw["ascendant"],
                mc=houses_raw.get("mc", 0.0),
                cusps=houses_raw["cusps"],
            )
            moon_rashi_idx = int(planets_raw["moon"]["longitude"] // 30)

            chart = BirthChart(
                user_id="guide_agent",
                birth_data=BirthData(
                    datetime_utc=birth_datetime,
                    latitude=latitude,
                    longitude=longitude,
                    timezone="UTC",
                ),
                planets=planet_positions,
                houses=house_cusps_obj,
                lagna_rashi=sign_map.get(RASHI_NAMES[lagna_idx].lower(), Rashi.ARIES),
                moon_rashi=sign_map.get(RASHI_NAMES[moon_rashi_idx].lower(), Rashi.ARIES),
                moon_nakshatra="ashwini",
                ayanamsa=23.85,
                calculated_at=birth_datetime,
            )

            result = _ak_analysis(chart)
            return {"atmakaraka": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting atmakaraka analysis: {e!s}")
            return {"success": False, "error": str(e)}

    def get_daily_forecast(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
        query_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate a comprehensive daily forecast.

        Args:
            birth_datetime: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude
            ayanamsa: Ayanamsa system
            query_date: Date to forecast (defaults to today)

        Returns:
            Day rating, panchanga, transit aspects, recommendations
        """
        try:
            from packages.context.src.daily_forecast import get_daily_forecast as _daily

            chart = self.get_birth_chart(birth_datetime, latitude, longitude, ayanamsa)
            planets = chart.get("planets", {})
            moon_lon = planets.get("moon", {}).get("longitude", 0.0)
            lagna_rashi = chart.get("lagna_rashi", "aries")

            q_date_str = query_date.isoformat() if query_date else None
            result = _daily(
                birth_datetime=birth_datetime.isoformat(),
                birth_lat=latitude,
                birth_lon=longitude,
                natal_planets=planets,
                moon_longitude=moon_lon,
                lagna_rashi=lagna_rashi,
                query_date=q_date_str,
            )
            return {"forecast": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting daily forecast: {e!s}")
            return {"success": False, "error": str(e)}

    def get_weekly_forecast(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
        start_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate a 7-day forecast with area-wise ratings.

        Args:
            birth_datetime: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude
            ayanamsa: Ayanamsa system
            start_date: Week start date (defaults to today)

        Returns:
            Weekly rating, daily forecasts, area ratings, key transits
        """
        try:
            from packages.context.src.weekly_forecast import get_weekly_forecast as _weekly

            chart = self.get_birth_chart(birth_datetime, latitude, longitude, ayanamsa)
            planets = chart.get("planets", {})
            moon_lon = planets.get("moon", {}).get("longitude", 0.0)
            lagna_rashi = chart.get("lagna_rashi", "aries")

            s_date_str = start_date.isoformat() if start_date else None
            result = _weekly(
                birth_datetime=birth_datetime.isoformat(),
                birth_lat=latitude,
                birth_lon=longitude,
                natal_planets=planets,
                moon_longitude=moon_lon,
                lagna_rashi=lagna_rashi,
                start_date=s_date_str,
            )
            return {"forecast": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting weekly forecast: {e!s}")
            return {"success": False, "error": str(e)}

    def get_monthly_forecast(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        ayanamsa: str = "lahiri",
        month: int | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        """Generate a month-long forecast with major transits and area analysis.

        Args:
            birth_datetime: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude
            ayanamsa: Ayanamsa system
            month: Month number (1-12, defaults to current)
            year: Year (defaults to current)

        Returns:
            Monthly rating, major transits, area ratings, weekly summaries
        """
        try:
            from packages.context.src.monthly_forecast import get_monthly_forecast as _monthly

            chart = self.get_birth_chart(birth_datetime, latitude, longitude, ayanamsa)
            planets = chart.get("planets", {})
            moon_lon = planets.get("moon", {}).get("longitude", 0.0)
            lagna_rashi = chart.get("lagna_rashi", "aries")

            result = _monthly(
                birth_datetime=birth_datetime.isoformat(),
                birth_lat=latitude,
                birth_lon=longitude,
                natal_planets=planets,
                moon_longitude=moon_lon,
                lagna_rashi=lagna_rashi,
                month=month,
                year=year,
            )
            return {"forecast": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting monthly forecast: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # STATE ENGINE TOOLS
    # ===================

    def get_state_vector(
        self,
        birth_datetime: datetime,
        birth_lat: float,
        birth_lon: float,
        natal_planets: dict[str, Any],
        moon_longitude: float,
        lagna_rashi: str,
        moon_rashi: str | None = None,
        query_datetime: datetime | None = None,
    ) -> dict[str, Any]:
        """Compute the full state vector (7 factors + 8 areas + composite).

        Args:
            birth_datetime: Birth date/time
            birth_lat: Birth latitude
            birth_lon: Birth longitude
            natal_planets: Dict of natal planet positions
            moon_longitude: Moon's longitude at birth (0-360)
            lagna_rashi: Ascendant rashi name
            moon_rashi: Moon rashi name (optional)
            query_datetime: Moment to evaluate (default: now)

        Returns:
            State vector with factors, areas, composite, mental_state
        """
        try:
            from packages.context.src.state_engine import compute_state_vector

            birth_dt_str = (
                birth_datetime.isoformat()
                if isinstance(birth_datetime, datetime)
                else str(birth_datetime)
            )
            query_dt_str = query_datetime.isoformat() if query_datetime else None

            result = compute_state_vector(
                birth_datetime=birth_dt_str,
                birth_lat=birth_lat,
                birth_lon=birth_lon,
                natal_planets=natal_planets,
                moon_longitude=moon_longitude,
                lagna_rashi=lagna_rashi,
                moon_rashi=moon_rashi,
                query_datetime=query_dt_str,
            )
            return {"state_vector": result, "success": True}
        except Exception as e:
            logger.error(f"Error computing state vector: {e!s}")
            return {"success": False, "error": str(e)}

    def get_life_area_score(
        self,
        area_id: str,
        birth_datetime: datetime,
        birth_lat: float,
        birth_lon: float,
        natal_planets: dict[str, Any],
        moon_longitude: float,
        lagna_rashi: str,
        moon_rashi: str | None = None,
        query_datetime: datetime | None = None,
    ) -> dict[str, Any]:
        """Get the score for a specific life area.

        Args:
            area_id: One of career, relationships, health, finance,
                     spiritual, family, education, travel
            birth_datetime: Birth date/time
            birth_lat: Birth latitude
            birth_lon: Birth longitude
            natal_planets: Dict of natal planet positions
            moon_longitude: Moon's longitude at birth
            lagna_rashi: Ascendant rashi name
            moon_rashi: Moon rashi name (optional)
            query_datetime: Moment to evaluate (default: now)

        Returns:
            Single area score with composite and mental_state
        """
        sv = self.get_state_vector(
            birth_datetime=birth_datetime,
            birth_lat=birth_lat,
            birth_lon=birth_lon,
            natal_planets=natal_planets,
            moon_longitude=moon_longitude,
            lagna_rashi=lagna_rashi,
            moon_rashi=moon_rashi,
            query_datetime=query_datetime,
        )
        if not sv.get("success"):
            return sv

        vector = sv["state_vector"]
        areas = vector.get("areas", [])
        area = None
        for a in areas:
            if isinstance(a, dict) and a.get("id") == area_id:
                area = a
                break
        if area is None:
            return {"success": False, "error": f"Unknown area: {area_id}"}

        return {
            "area": area,
            "area_id": area_id,
            "composite": vector.get("composite", 0.0),
            "mental_state": vector.get("mental_state", "unknown"),
            "success": True,
        }

    # ===================
    # KP (KRISHNAMURTI PADDHATI) TOOLS
    # ===================

    def get_kp_sublord(
        self,
        longitude: float,
    ) -> dict[str, Any]:
        """Get KP sub-lord for a given longitude.

        Args:
            longitude: Sidereal longitude (0-360)

        Returns:
            Sub-lord details with nakshatra lord, sub-lord, and sub-sub-lord
        """
        try:
            from packages.self.src.kp import get_kp_sublord as _kp_sublord

            result = _kp_sublord(longitude)
            return {"kp_sublord": result, "success": True}
        except Exception as e:
            logger.error(f"Error getting KP sub-lord: {e!s}")
            return {"success": False, "error": str(e)}

    def get_kp_analysis(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        query_type: str = "career",
        ayanamsa: str = "krishnamurti",
    ) -> dict[str, Any]:
        """Get complete KP analysis for a life query.

        Uses Krishnamurti Paddhati sub-lord system for precise yes/no predictions.
        Automatically uses Placidus houses and Krishnamurti ayanamsa.

        Args:
            birth_datetime: Birth datetime
            latitude: Birth latitude
            longitude: Birth longitude
            query_type: Life area to analyze (career, marriage, children, wealth,
                       health, education, travel, property, legal, spiritual, longevity)
            ayanamsa: Ayanamsa system (default: krishnamurti)

        Returns:
            KP prediction with verdict, significators, ruling planets, and analysis
        """
        try:
            from packages.self.src.kp import (
                get_cuspal_sublords,
                get_kp_prediction,
                get_kp_significators,
                get_ruling_planets,
            )

            # Calculate chart with Placidus (KP requirement)
            chart = self.get_birth_chart(
                birth_datetime, latitude, longitude, ayanamsa, house_system="placidus"
            )
            if not chart.get("success"):
                return chart

            planets = chart.get("planets", {})
            houses = chart.get("houses", {})

            # Extract cusp longitudes
            cusps = []
            for i in range(1, 13):
                house_data = houses.get(str(i), {})
                cusps.append(house_data.get("cusp_longitude", (i - 1) * 30))

            # Get KP components — fix calling conventions:
            # get_ruling_planets expects (datetime_iso, latitude, longitude)
            # get_kp_significators expects (planets, cusps) and returns per-planet data
            cuspal_sublords = get_cuspal_sublords(cusps)
            significators = get_kp_significators(planets, cusps)
            birth_iso = (
                birth_datetime.isoformat()
                if hasattr(birth_datetime, "isoformat")
                else str(birth_datetime)
            )
            try:
                ruling = get_ruling_planets(birth_iso, latitude, longitude)
            except Exception as e:
                logger.warning(f"Ruling planets calc failed: {e}")
                ruling = {}

            # Get prediction — signature varies, pass best-effort
            try:
                prediction = get_kp_prediction(planets, cusps, query_type)
            except TypeError:
                # Some implementations may take birth_iso instead
                try:
                    prediction = get_kp_prediction(planets, cusps, birth_iso, query_type)
                except Exception as e:
                    logger.warning(f"KP prediction failed: {e}")
                    prediction = {"verdict": "indeterminate", "note": str(e)}

            return {
                "kp_analysis": {
                    "query_type": query_type,
                    "prediction": prediction,
                    "cuspal_sublords": cuspal_sublords,
                    "significators": significators,
                    "ruling_planets": ruling,
                    "ayanamsa": ayanamsa,
                    "house_system": "placidus",
                },
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error in KP analysis: {e!s}")
            return {"success": False, "error": str(e)}

    # ===================
    # UTILITY METHODS
    # ===================

    def _lon_to_sign(self, longitude: float) -> str:
        """Convert longitude to sign name."""
        return RASHI_NAMES[int(longitude / 30)]

    def get_version(self) -> dict[str, str]:
        """Get version information of tools."""
        return {
            "tools_version": "2.1.0",
            "cosmos_version": "2.0.0",
            "context_version": "2.1.0",
            "self_version": "2.1.0",
        }


# Global tools instance
_tools_instance: AstrologyTools | None = None


def get_tools() -> AstrologyTools:
    """Get or create the global AstrologyTools instance."""
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = AstrologyTools()
    return _tools_instance


# Convenience functions for direct access
def get_birth_chart(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "lahiri",
    house_system: str = "placidus",
) -> dict[str, Any]:
    """Get birth chart."""
    return get_tools().get_birth_chart(birth_datetime, latitude, longitude, ayanamsa, house_system)


def get_current_positions(ayanamsa: str = "lahiri") -> dict[str, Any]:
    """Get current planetary positions."""
    return get_tools().get_current_positions(ayanamsa)


def get_dasha_info(
    birth_datetime: datetime, moon_longitude: float, query_date: datetime | None = None
) -> dict[str, Any]:
    """Get dasha information."""
    return get_tools().get_dasha_info(birth_datetime, moon_longitude, query_date)


def get_transit_analysis(natal_chart: dict[str, Any]) -> dict[str, Any]:
    """Get transit analysis."""
    return get_tools().get_transit_analysis(natal_chart)


def detect_yogas(natal_chart: dict[str, Any]) -> dict[str, Any]:
    """Detect yogas in birth chart."""
    return get_tools().detect_yogas(natal_chart)


def detect_doshas(natal_chart: dict[str, Any]) -> dict[str, Any]:
    """Detect doshas in birth chart."""
    return get_tools().detect_doshas(natal_chart)


def check_muhurta(
    activity: str, datetime_to_check: datetime, latitude: float, longitude: float
) -> dict[str, Any]:
    """Check muhurta for an activity."""
    return get_tools().check_muhurta(activity, datetime_to_check, latitude, longitude)


def get_today_panchanga(
    date: datetime | None = None, latitude: float = 28.6139, longitude: float = 77.2090
) -> dict[str, Any]:
    """Get today's panchanga."""
    return get_tools().get_today_panchanga(date, latitude, longitude)


def check_yoga_cancellations(
    yogas: list[dict[str, Any]],
    planets: dict[str, dict],
    lagna_rashi: str,
    sun_longitude: float,
) -> dict[str, Any]:
    """Check yoga cancellations."""
    return get_tools().check_yoga_cancellations(yogas, planets, lagna_rashi, sun_longitude)


def get_dasha_transit_analysis(
    natal_planets: dict[str, dict],
    current_transits: dict[str, dict],
    current_dasha: dict[str, Any],
    lagna_rashi: str,
    moon_rashi: str,
) -> dict[str, Any]:
    """Get dasha-transit cross analysis."""
    return get_tools().get_dasha_transit_analysis(
        natal_planets, current_transits, current_dasha, lagna_rashi, moon_rashi
    )


def get_upcoming_triggers(
    natal_planets: dict[str, dict],
    lagna_rashi: str,
    moon_rashi: str,
    start_date: str | None = None,
    days_ahead: int = 30,
) -> dict[str, Any]:
    """Get upcoming transit triggers."""
    return get_tools().get_upcoming_triggers(
        natal_planets, lagna_rashi, moon_rashi, start_date, days_ahead
    )


def get_remedies(
    current_dasha: str,
    active_doshas: list[str],
    weak_planets: list[str],
    lagna_rashi: str = "",
) -> dict[str, Any]:
    """Get remedy recommendations."""
    return get_tools().get_remedies(current_dasha, active_doshas, weak_planets, lagna_rashi)


def get_synastry_report_fn(
    native_birth_dt: datetime,
    native_lat: float,
    native_lon: float,
    partner_birth_dt: datetime,
    partner_lat: float,
    partner_lon: float,
    ayanamsa: str = "lahiri",
) -> dict[str, Any]:
    """Get synastry report."""
    return get_tools().get_synastry_report(
        native_birth_dt,
        native_lat,
        native_lon,
        partner_birth_dt,
        partner_lat,
        partner_lon,
        ayanamsa,
    )


def get_gem_recommendation(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "lahiri",
    gem_planet: str | None = None,
) -> dict[str, Any]:
    """Get gem recommendation."""
    return get_tools().get_gem_recommendation(
        birth_datetime, latitude, longitude, ayanamsa, gem_planet
    )


def get_atmakaraka_analysis(
    birth_datetime: datetime, latitude: float, longitude: float, ayanamsa: str = "lahiri"
) -> dict[str, Any]:
    """Get atmakaraka analysis."""
    return get_tools().get_atmakaraka_analysis(birth_datetime, latitude, longitude, ayanamsa)


def get_daily_forecast(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "lahiri",
    query_date: datetime | None = None,
) -> dict[str, Any]:
    """Get daily forecast."""
    return get_tools().get_daily_forecast(birth_datetime, latitude, longitude, ayanamsa, query_date)


def get_weekly_forecast(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "lahiri",
    start_date: datetime | None = None,
) -> dict[str, Any]:
    """Get weekly forecast."""
    return get_tools().get_weekly_forecast(
        birth_datetime, latitude, longitude, ayanamsa, start_date
    )


def get_monthly_forecast(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    ayanamsa: str = "lahiri",
    month: int | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    """Get monthly forecast."""
    return get_tools().get_monthly_forecast(
        birth_datetime,
        latitude,
        longitude,
        ayanamsa,
        month,
        year,
    )


def get_kp_sublord_info(longitude: float) -> dict[str, Any]:
    """Get KP sub-lord for a longitude."""
    return get_tools().get_kp_sublord(longitude)


def get_kp_analysis(
    birth_datetime: datetime,
    latitude: float,
    longitude: float,
    query_type: str = "career",
    ayanamsa: str = "krishnamurti",
) -> dict[str, Any]:
    """Get KP analysis for a life query."""
    return get_tools().get_kp_analysis(birth_datetime, latitude, longitude, query_type, ayanamsa)


__all__ = [
    "ActivityType",
    "AstrologyTools",
    "ChartCache",
    "check_muhurta",
    "check_yoga_cancellations",
    "detect_doshas",
    "detect_yogas",
    "get_atmakaraka_analysis",
    "get_birth_chart",
    "get_current_positions",
    "get_daily_forecast",
    "get_dasha_info",
    "get_dasha_transit_analysis",
    "get_gem_recommendation",
    "get_kp_analysis",
    "get_kp_sublord_info",
    "get_monthly_forecast",
    "get_remedies",
    "get_synastry_report_fn",
    "get_today_panchanga",
    "get_tools",
    "get_transit_analysis",
    "get_upcoming_triggers",
    "get_weekly_forecast",
]
