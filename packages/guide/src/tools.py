"""
108 Agent Tools

Tools that the Guide agent can invoke for calculations, lookups, and memory operations.
These wrap the underlying packages and MCP servers.

This module provides a unified interface to all astrological calculation and data
retrieval capabilities needed by the LangGraph-based Guide agent.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path
import sys

# Setup package imports
PACKAGES_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PACKAGES_ROOT))

# Import cosmos package functions
from packages.cosmos.src import (
    get_julian_day,
    get_planet_position,
    get_all_planets,
    get_house_cusps,
    get_ascendant,
    get_ayanamsa,
    PLANET_MAP,
    AYANAMSA_MAP,
    HOUSE_SYSTEM_MAP,
    # Nakshatra functions
    longitude_to_nakshatra,
    get_nakshatra_lord,
    get_pada_navamsha,
    get_tarabala,
    get_all_nakshatras,
    # Divisional chart functions
    get_navamsha,
    get_dashamsha,
    get_divisional_position,
    get_divisional_chart,
    get_varga_vimshopaka,
    RASHI_NAMES,
    DIVISIONAL_NAMES,
    # House functions
    get_house_for_longitude,
    get_house_lord,
    get_planets_in_house,
    get_house_analysis,
    # Panchanga functions
    get_tithi,
    get_yoga,
    get_karana,
    get_vara,
    get_panchanga,
    TITHI_NAMES,
    YOGA_NAMES,
    VARA_NAMES,
)

# Import context package functions
from packages.context.src import (
    get_dasha_balance_at_birth,
    get_mahadasha_sequence,
    get_antardasha_sequence,
    get_pratyantardasha_sequence,
    get_current_dasha,
    get_dasha_periods_for_year,
    # Transit functions
    get_gochara,
    check_sade_sati,
    check_dhaiya,
    get_full_transit_analysis,
    get_transiting_planet_house,
    is_planet_favorable_in_house,
    GOCHARA_FAVORABLE,
    VEDHA_POINTS,
    TRANSIT_EFFECTS,
    # Muhurta functions
    calculate_rahu_kaal,
    calculate_yamaghanda,
    calculate_gulika,
    calculate_all_inauspicious,
    calculate_choghadiya,
    evaluate_muhurta,
    evaluate_with_inauspicious_check,
    find_next_good_muhurta,
    get_choghadiya_at_time,
    RAHU_KAAL,
    YAMAGHANDA,
    GULIKA,
    ACTIVITY_RULES,
    CHOGHADIYA_ORDER,
    CHOGHADIYA_QUALITY,
    DASHA_YEARS,
    DASHA_SEQUENCE,
    NAKSHATRA_LORDS,
)

# Import self package modules
from packages.self.src import (
    YogaDetector,
    DoshaDetector,
    StrengthCalculator,
    detect_all_yogas,
    detect_yoga,
    get_yoga_strength,
)

# Import core package types and utilities
from packages.core.src import (
    BirthChart,
    BirthData,
    CurrentDasha,
    DetectedYoga,
    DetectedDosha,
    Planet,
    Rashi,
    HouseSystem,
    AyanamsaType,
    longitude_to_rashi,
    normalize_degrees,
    is_kendra,
    is_trikona,
    is_dusthana,
    is_upachaya,
    get_opposite_sign,
)

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
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
        house_system: str = "placidus"
    ) -> Dict[str, Any]:
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
            logger.error(f"Error calculating birth chart: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_current_positions(
        self,
        ayanamsa: str = "lahiri"
    ) -> Dict[str, Any]:
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
            logger.error(f"Error getting current positions: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # DIVISIONAL CHART TOOLS
    # ===================

    def get_navamsha_chart(
        self,
        planets: Dict[str, Dict]
    ) -> Dict[str, Any]:
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
            logger.error(f"Error calculating Navamsha: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_divisional_charts(
        self,
        planets: Dict[str, Dict],
        charts: List[int] = None
    ) -> Dict[str, Any]:
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
            logger.error(f"Error calculating divisional charts: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_varga_strength(
        self,
        planets: Dict[str, Dict],
        planet_name: str,
        charts: List[int] = None
    ) -> Dict[str, Any]:
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
            logger.error(f"Error calculating Varga strength: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # DASHA (TIMING) TOOLS
    # ===================

    def get_dasha_info(
        self,
        birth_datetime: datetime,
        moon_longitude: float,
        query_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
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
            logger.error(f"Error calculating dasha info: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_dasha_timeline(
        self,
        birth_datetime: datetime,
        moon_longitude: float,
        years: int = 50
    ) -> Dict[str, Any]:
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
            cutoff_date = start_date + timedelta(days=365*years)

            filtered = [
                period for period in timeline
                if period.get("end_date", datetime.max) <= cutoff_date
            ]

            return {
                "start_date": start_date.isoformat(),
                "end_date": cutoff_date.isoformat(),
                "dasha_periods": filtered,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error calculating dasha timeline: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # TRANSIT (GOCHARA) TOOLS
    # ===================

    def get_transit_analysis(
        self,
        natal_chart: Dict[str, Any],
        transit_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
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
                "Aries": 0, "Taurus": 1, "Gemini": 2, "Cancer": 3,
                "Leo": 4, "Virgo": 5, "Libra": 6, "Scorpio": 7,
                "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11
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
                transit_analysis["transits"].get("saturn", {}).get("sign", ""),
                0
            )
            sade_sati = check_sade_sati(natal_moon_idx, saturn_idx)
            transit_analysis["sade_sati"] = sade_sati

            # Check Dhaiya
            dhaiya = check_dhaiya(natal_moon_idx, saturn_idx)
            transit_analysis["dhaiya"] = dhaiya

            transit_analysis["success"] = True
            return transit_analysis
        except Exception as e:
            logger.error(f"Error analyzing transits: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # YOGA (AUSPICIOUS COMBINATIONS) TOOLS
    # ===================

    def detect_yogas(
        self,
        natal_chart: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            logger.error(f"Error detecting yogas: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_yoga_details(
        self,
        yoga_name: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific yoga.

        Args:
            yoga_name: Name of yoga (e.g., "Gajakesari", "Rajayoga")

        Returns:
            Details about the yoga, its benefits, and conditions
        """
        try:
            # This would lookup yoga information from a knowledge base
            # For now, return structure for future implementation
            return {
                "yoga": yoga_name,
                "description": f"Details for {yoga_name} yoga",
                "benefits": [],
                "conditions": [],
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting yoga details: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # DOSHA (CHALLENGING COMBINATIONS) TOOLS
    # ===================

    def detect_doshas(
        self,
        natal_chart: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            logger.error(f"Error detecting doshas: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # PLANETARY STRENGTH TOOLS
    # ===================

    def get_planet_strength(
        self,
        planet: str,
        position: Dict[str, Any],
        house_num: int,
        lagna_sign: str
    ) -> Dict[str, Any]:
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
                planet=planet_enum,
                longitude=longitude,
                house=house_num,
                rashi=rashi_enum
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
            logger.error(f"Error calculating planet strength: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # MUHURTA (AUSPICIOUS TIMING) TOOLS
    # ===================

    def check_muhurta(
        self,
        activity: str,
        datetime_to_check: datetime,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
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
            inauspicious = calculate_all_inauspicious(
                datetime_to_check,
                latitude,
                longitude
            )

            result["inauspicious_periods"] = inauspicious
            result["success"] = True
            return result
        except Exception as e:
            logger.error(f"Error checking muhurta: {str(e)}")
            return {"success": False, "error": str(e)}

    def find_good_muhurta(
        self,
        activity: str,
        start_date: datetime,
        end_date: datetime,
        latitude: float,
        longitude: float,
        max_results: int = 5
    ) -> Dict[str, Any]:
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
            good_dates = find_next_good_muhurta(
                activity,
                start_date,
                end_date,
                latitude,
                longitude
            )

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
            logger.error(f"Error finding good muhurta: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # PANCHANGA (DAILY ALMANAC) TOOLS
    # ===================

    def get_today_panchanga(
        self,
        date: Optional[datetime] = None,
        latitude: float = 28.6139,
        longitude: float = 77.2090
    ) -> Dict[str, Any]:
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
            logger.error(f"Error getting panchanga: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_choghadiya_timings(
        self,
        date: Optional[datetime] = None,
        latitude: float = 28.6139,
        longitude: float = 77.2090
    ) -> Dict[str, Any]:
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

            daytime = calculate_choghadiya(
                sunrise,
                sunset,
                is_night=False
            )

            nighttime = calculate_choghadiya(
                sunset,
                next_sunrise,
                is_night=True
            )

            return {
                "date": date.strftime("%Y-%m-%d"),
                "sunrise": sunrise.isoformat(),
                "sunset": sunset.isoformat(),
                "daytime_choghadiya": daytime,
                "nighttime_choghadiya": nighttime,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Error getting choghadiya: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_rahu_kaal(
        self,
        date: Optional[datetime] = None,
        latitude: float = 28.6139,
        longitude: float = 77.2090
    ) -> Dict[str, Any]:
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
            logger.error(f"Error getting Rahu Kaal: {str(e)}")
            return {"success": False, "error": str(e)}

    # ===================
    # UTILITY METHODS
    # ===================

    def _lon_to_sign(self, longitude: float) -> str:
        """Convert longitude to sign name."""
        return RASHI_NAMES[int(longitude / 30)]

    def get_version(self) -> Dict[str, str]:
        """Get version information of tools."""
        return {
            "tools_version": "2.0.0",
            "cosmos_version": "2.0.0",
            "context_version": "2.0.0",
            "self_version": "2.0.0",
        }


# Global tools instance
_tools_instance: Optional[AstrologyTools] = None


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
    house_system: str = "placidus"
) -> Dict[str, Any]:
    """Get birth chart."""
    return get_tools().get_birth_chart(birth_datetime, latitude, longitude, ayanamsa, house_system)


def get_current_positions(ayanamsa: str = "lahiri") -> Dict[str, Any]:
    """Get current planetary positions."""
    return get_tools().get_current_positions(ayanamsa)


def get_dasha_info(
    birth_datetime: datetime,
    moon_longitude: float,
    query_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get dasha information."""
    return get_tools().get_dasha_info(birth_datetime, moon_longitude, query_date)


def get_transit_analysis(natal_chart: Dict[str, Any]) -> Dict[str, Any]:
    """Get transit analysis."""
    return get_tools().get_transit_analysis(natal_chart)


def detect_yogas(natal_chart: Dict[str, Any]) -> Dict[str, Any]:
    """Detect yogas in birth chart."""
    return get_tools().detect_yogas(natal_chart)


def detect_doshas(natal_chart: Dict[str, Any]) -> Dict[str, Any]:
    """Detect doshas in birth chart."""
    return get_tools().detect_doshas(natal_chart)


def check_muhurta(
    activity: str,
    datetime_to_check: datetime,
    latitude: float,
    longitude: float
) -> Dict[str, Any]:
    """Check muhurta for an activity."""
    return get_tools().check_muhurta(activity, datetime_to_check, latitude, longitude)


def get_today_panchanga(
    date: Optional[datetime] = None,
    latitude: float = 28.6139,
    longitude: float = 77.2090
) -> Dict[str, Any]:
    """Get today's panchanga."""
    return get_tools().get_today_panchanga(date, latitude, longitude)


__all__ = [
    "AstrologyTools",
    "ActivityType",
    "get_tools",
    "get_birth_chart",
    "get_current_positions",
    "get_dasha_info",
    "get_transit_analysis",
    "detect_yogas",
    "detect_doshas",
    "check_muhurta",
    "get_today_panchanga",
]
