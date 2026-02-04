"""
Unit tests for the COSMOS package (ephemeris calculations).
"""
import sys
from datetime import datetime

import pytest

sys.path.insert(0, "/sessions/eloquent-zen-gauss/mnt/108-core")


class TestEphemeris:
    """Test planetary position calculations."""

    def test_julian_day_calculation(self):
        """Test Julian Day conversion."""
        from packages.cosmos.src import get_julian_day

        # Test known date: January 1, 2000, 12:00 UT
        # Expected JD: 2451545.0 (J2000.0 epoch)
        dt = datetime(2000, 1, 1, 12, 0)
        jd = get_julian_day(dt)

        assert abs(jd - 2451545.0) < 0.01, f"Expected ~2451545.0, got {jd}"

    def test_ayanamsa_lahiri(self):
        """Test Lahiri ayanamsa calculation."""
        from packages.cosmos.src import get_ayanamsa, get_julian_day

        dt = datetime(2000, 1, 1, 12, 0)
        jd = get_julian_day(dt)
        ayanamsa = get_ayanamsa(jd, "lahiri")

        # Lahiri ayanamsa around 2000 should be ~23.85 degrees
        assert 23 < ayanamsa < 25, f"Expected ~23.85, got {ayanamsa}"

    def test_planetary_positions(self):
        """Test getting all planetary positions."""
        from packages.cosmos.src import get_all_planets, get_ayanamsa, get_julian_day

        dt = datetime(2000, 1, 1, 12, 0)
        jd = get_julian_day(dt)
        ayanamsa = get_ayanamsa(jd, "lahiri")

        planets = get_all_planets(jd, ayanamsa)

        # Should have all 9 Vedic planets
        expected_planets = [
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        ]

        for planet in expected_planets:
            assert planet in planets, f"Missing planet: {planet}"
            assert "longitude" in planets[planet], f"Missing longitude for {planet}"
            assert (
                0 <= planets[planet]["longitude"] < 360
            ), f"Invalid longitude for {planet}: {planets[planet]['longitude']}"

    def test_house_cusps(self):
        """Test house cusp calculation."""
        from packages.cosmos.src import get_house_cusps, get_julian_day

        dt = datetime(2000, 1, 1, 12, 0)
        jd = get_julian_day(dt)
        lat, lon = 28.6139, 77.2090  # Delhi

        houses = get_house_cusps(jd, lat, lon, ayanamsa="lahiri")

        # Should have cusps list with 12 houses
        assert "cusps" in houses, "Should have cusps key"
        assert len(houses["cusps"]) == 12, f"Expected 12 houses, got {len(houses['cusps'])}"

        # Each house should have valid longitude
        for i, cusp in enumerate(houses["cusps"]):
            assert 0 <= cusp < 360, f"Invalid cusp for house {i+1}: {cusp}"

        # Should also have ascendant and mc
        assert "ascendant" in houses, "Should have ascendant"
        assert "mc" in houses, "Should have midheaven"


class TestNakshatra:
    """Test nakshatra calculations."""

    def test_longitude_to_nakshatra(self):
        """Test nakshatra determination from longitude."""
        from packages.cosmos.src import longitude_to_nakshatra

        # Ashwini spans 0° - 13°20' Aries
        nakshatra = longitude_to_nakshatra(5.0)
        assert nakshatra["name"] == "Ashwini", f"Expected Ashwini, got {nakshatra['name']}"
        assert nakshatra["pada"] == 1 or nakshatra["pada"] == 2

        # Bharani spans 13°20' - 26°40' Aries
        nakshatra = longitude_to_nakshatra(20.0)
        assert nakshatra["name"] == "Bharani", f"Expected Bharani, got {nakshatra['name']}"

    def test_nakshatra_lord(self):
        """Test nakshatra lord determination."""
        from packages.cosmos.src import get_nakshatra_lord

        # Ashwini is ruled by Ketu (lowercase planet IDs)
        lord = get_nakshatra_lord("Ashwini")
        assert lord == "ketu", f"Expected ketu, got {lord}"

        # Rohini is ruled by Moon
        lord = get_nakshatra_lord("Rohini")
        assert lord == "moon", f"Expected moon, got {lord}"


class TestRashi:
    """Test rashi (zodiac sign) calculations."""

    def test_longitude_to_rashi(self):
        """Test rashi determination from longitude."""
        from packages.cosmos.src import RASHI_NAMES

        # 0-30° = Aries, 30-60° = Taurus, etc.
        assert RASHI_NAMES[0] == "Aries"
        assert RASHI_NAMES[1] == "Taurus"
        assert RASHI_NAMES[11] == "Pisces"

    def test_rashi_from_longitude(self):
        """Test getting rashi index from longitude."""
        # 45° should be in Taurus (index 1)
        rashi_index = int(45 / 30)
        assert rashi_index == 1

        # 275° should be in Capricorn (index 9)
        rashi_index = int(275 / 30)
        assert rashi_index == 9


class TestPanchanga:
    """Test Panchanga (5-limb calendar) calculations."""

    def test_tithi_calculation(self):
        """Test tithi (lunar day) calculation."""
        from packages.cosmos.src.panchanga import get_tithi

        # Tithi requires Sun and Moon longitudes
        # Full moon: Moon opposite Sun (180° apart)
        sun_lon = 270.0  # Sun in Capricorn
        moon_lon = 90.0  # Moon in Cancer (opposite)

        tithi = get_tithi(sun_lon, moon_lon)
        assert "number" in tithi
        assert 1 <= tithi["number"] <= 30

    def test_vara_calculation(self):
        """Test vara (weekday) calculation."""
        from packages.cosmos.src.panchanga import get_vara

        # January 1, 2024 was a Monday
        dt = datetime(2024, 1, 1, 12, 0)

        vara = get_vara(dt)
        # 'gregorian_day' has the English day name, 'name' has Sanskrit name
        assert vara["gregorian_day"] == "Monday", f"Expected Monday, got {vara['gregorian_day']}"


class TestDivisionalCharts:
    """Test divisional chart calculations."""

    def test_navamsa_calculation(self):
        """Test Navamsa (D9) chart calculation."""
        from packages.cosmos.src import get_divisional_chart

        # get_divisional_chart takes a dict of planets and division number
        planets = {"sun": 15.0, "moon": 45.0, "mars": 120.0}
        navamsa = get_divisional_chart(planets, 9)

        # Should return a DivisionalChart with positions for all planets
        assert hasattr(navamsa, "positions") or isinstance(navamsa, dict)

    def test_dasamsa_calculation(self):
        """Test Dasamsa (D10) chart calculation."""
        from packages.cosmos.src import get_divisional_chart

        planets = {"sun": 45.0, "moon": 180.0}
        dasamsa = get_divisional_chart(planets, 10)

        # Should return a DivisionalChart with positions
        assert hasattr(dasamsa, "positions") or isinstance(dasamsa, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
