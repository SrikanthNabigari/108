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
            lagna_sign = longitude_to_rashi(ascendant)
            lagna_nak = longitude_to_nakshatra(ascendant)

            # Build planets dictionary with rashi information
            planets_data = {}
            for planet_name, position in planets.items():
                planet_sign = longitude_to_rashi(position["longitude"])
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
                    house_sign = longitude_to_rashi(house_long)
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
                planet_sign = longitude_to_rashi(position["longitude"])
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

            divisional_data = {}
            for d_num in charts:
                d_chart = get_divisional_chart(planets, d_num)
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
            query_date = query_date or datetime.utcnow()

            # Get current dasha
            current = get_current_dasha(birth_datetime, moon_longitude, query_date)

            # Get timeline of mahadashas
            timeline = get_mahadasha_sequence(birth_datetime, moon_longitude)

            # Calculate how far into current dasha we are
            maha_start = current.get("mahadasha_start")
            maha_end = current.get("mahadasha_end")
            anta_start = current.get("antardasha_start")
            anta_end = current.get("antardasha_end")

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
                    "lord": current.get("mahadasha_lord"),
                    "start": maha_start.isoformat() if maha_start else None,
                    "end": maha_end.isoformat() if maha_end else None,
                    "years": current.get("mahadasha_years"),
                    "progress_percent": round(maha_percent, 1),
                },
                "current_antardasha": {
                    "lord": current.get("antardasha_lord"),
                    "start": anta_start.isoformat() if anta_start else None,
                    "end": anta_end.isoformat() if anta_end else None,
                    "years": current.get("antardasha_years"),
                    "progress_percent": round(anta_percent, 1),
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

            # Filter to next N years
            start_date = datetime.utcnow()
            cutoff_date = start_date + timedelta(days=365 * years)

            filtered = [
                period for period in timeline if period.get("end_date", datetime.max) <= cutoff_date
            ]

            return {
                "start_date": start_date.isoformat(),
                "end_date": cutoff_date.isoformat(),
                "dasha_periods": filtered,
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

            # Extract natal moon sign
            natal_moon = natal_chart.get("planets", {}).get("moon", {})
            natal_moon_rashi = natal_moon.get("sign")

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
                    planet_sign = longitude_to_rashi(planet_long)
                    transit_idx = sign_to_idx.get(planet_sign.value, 0)
                    house_from_moon = ((transit_idx - natal_moon_idx) % 12) + 1

                    transit_analysis["transits"][planet] = {
                        "sign": planet_sign.value,
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
            planets = natal_chart.get("planets", {})
            lagna = natal_chart.get("lagna", {})
            lagna_sign = Rashi(lagna.get("sign", "aries").lower())

            # Extract planet data for detector
            chart_data = {
                "planets": planets,
                "lagna_rashi": lagna_sign,
            }

            detected = self.yoga_detector.detect_all(chart_data)

            return {
                "yogas": detected,
                "yoga_count": len(detected),
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
            planets = natal_chart.get("planets", {})
            lagna = natal_chart.get("lagna", {})
            lagna_sign = Rashi(lagna.get("sign", "aries").lower())
            moon = natal_chart.get("planets", {}).get("moon", {})
            moon_sign = Rashi(moon.get("sign", "aries").lower())

            chart_data = {
                "planets": planets,
                "lagna_rashi": lagna_sign,
                "moon_rashi": moon_sign,
            }

            detected = self.dosha_detector.detect_all(chart_data)

            return {
                "doshas": detected,
                "dosha_count": len(detected),
                "remedies_available": any(d.get("remedy") for d in detected),
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
            longitude = position.get("longitude", 0)

            shadbala = self.strength_calc.calculate_shadbala(
                planet=planet_enum, longitude=longitude, house=house_num, rashi=rashi_enum
            )

            dignity = self.strength_calc.get_planet_dignity(planet_enum, rashi_enum)

            return {
                "planet": planet,
                "house": house_num,
                "sign": lagna_sign,
                "dignity": dignity,
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
            jd = get_julian_day(datetime_to_check)
            planets = get_all_planets(jd)

            # Get panchanga
            sun_lon = planets["sun"]["longitude"]
            moon_lon = planets["moon"]["longitude"]

            panchanga = get_panchanga(sun_lon, moon_lon)

            # Evaluate muhurta
            result = evaluate_muhurta(activity, panchanga, datetime_to_check)

            # Check inauspicious periods
            inauspicious = calculate_all_inauspicious(datetime_to_check, latitude, longitude)

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

            jd = get_julian_day(date)
            planets = get_all_planets(jd)

            sun_lon = planets["sun"]["longitude"]
            moon_lon = planets["moon"]["longitude"]

            panchanga = get_panchanga(sun_lon, moon_lon)

            # Get sunrise/sunset
            from packages.cosmos.src import get_sunrise_sunset

            sunrise_sunset = get_sunrise_sunset(date.strftime("%Y-%m-%d"), latitude, longitude)

            return {
                "date": date.strftime("%Y-%m-%d"),
                "tithi": panchanga.get("tithi"),
                "nakshatra": panchanga.get("nakshatra"),
                "yoga": panchanga.get("yoga"),
                "karana": panchanga.get("karana"),
                "vara": panchanga.get("vara"),
                "sunrise": sunrise_sunset.get("sunrise"),
                "sunset": sunrise_sunset.get("sunset"),
                "sun_sign": panchanga.get("sun_sign", self._lon_to_sign(sun_lon)),
                "moon_sign": panchanga.get("moon_sign", self._lon_to_sign(moon_lon)),
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


__all__ = [
    "ActivityType",
    "AstrologyTools",
    "ChartCache",
    "check_muhurta",
    "check_yoga_cancellations",
    "detect_doshas",
    "detect_yogas",
    "get_birth_chart",
    "get_current_positions",
    "get_dasha_info",
    "get_dasha_transit_analysis",
    "get_remedies",
    "get_today_panchanga",
    "get_tools",
    "get_transit_analysis",
    "get_upcoming_triggers",
]
