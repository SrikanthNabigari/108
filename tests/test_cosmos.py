"""
Unit tests for the COSMOS package (ephemeris calculations).
"""
import pytest
from datetime import datetime
import sys
sys.path.insert(0, '/sessions/eloquent-zen-gauss/mnt/108-core')


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
        from packages.cosmos.src import get_all_planets, get_julian_day, get_ayanamsa

        dt = datetime(2000, 1, 1, 12, 0)
        jd = get_julian_day(dt)
        ayanamsa = get_ayanamsa(jd, "lahiri")

        planets = get_all_planets(jd, ayanamsa)

        # Should have all 9 Vedic planets
        expected_planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter',
                          'venus', 'saturn', 'rahu', 'ketu']

        for planet in expected_planets:
            assert planet in planets, f"Missing planet: {planet}"
            assert 'longitude' in planets[planet], f"Missing longitude for {planet}"
            assert 0 <= planets[planet]['longitude'] < 360, \
                f"Invalid longitude for {planet}: {planets[planet]['longitude']}"

    def test_house_cusps(self):
        """Test house cusp calculation."""
        from packages.cosmos.src import get_house_cusps, get_julian_day, get_ayanamsa

        dt = datetime(2000, 1, 1, 12, 0)
        jd = get_julian_day(dt)
        ayanamsa = get_ayanamsa(jd, "lahiri")
        lat, lon = 28.6139, 77.2090  # Delhi

        houses = get_house_cusps(jd, lat, lon, ayanamsa)

        # Should have 12 houses
        assert len(houses) == 12, f"Expected 12 houses, got {len(houses)}"

        # Each house should have valid longitude
        for i, house in enumerate(houses):
            assert 0 <= house < 360, f"Invalid cusp for house {i+1}: {house}"


class TestNakshatra:
    """Test nakshatra calculations."""

    def test_longitude_to_nakshatra(self):
        """Test nakshatra determination from longitude."""
        from packages.cosmos.src import longitude_to_nakshatra

        # Ashwini spans 0° - 13°20' Aries
        nakshatra = longitude_to_nakshatra(5.0)
        assert nakshatra['name'] == 'Ashwini', f"Expected Ashwini, got {nakshatra['name']}"
        assert nakshatra['pada'] == 1 or nakshatra['pada'] == 2

        # Bharani spans 13°20' - 26°40' Aries
        nakshatra = longitude_to_nakshatra(20.0)
        assert nakshatra['name'] == 'Bharani', f"Expected Bharani, got {nakshatra['name']}"

    def test_nakshatra_lord(self):
        """Test nakshatra lord determination."""
        from packages.cosmos.src import get_nakshatra_lord

        # Ashwini is ruled by Ketu
        lord = get_nakshatra_lord('Ashwini')
        assert lord == 'Ketu', f"Expected Ketu, got {lord}"

        # Rohini is ruled by Moon
        lord = get_nakshatra_lord('Rohini')
        assert lord == 'Moon', f"Expected Moon, got {lord}"


class TestRashi:
    """Test rashi (zodiac sign) calculations."""

    def test_longitude_to_rashi(self):
        """Test rashi determination from longitude."""
        from packages.cosmos.src import RASHI_NAMES

        # 0-30° = Aries, 30-60° = Taurus, etc.
        assert RASHI_NAMES[0] == 'Aries'
        assert RASHI_NAMES[1] == 'Taurus'
        assert RASHI_NAMES[11] == 'Pisces'

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
        from packages.cosmos.src import get_julian_day

        dt = datetime(2024, 1, 11, 12, 0)  # Known Purnima (full moon) day
        jd = get_julian_day(dt)

        tithi = get_tithi(jd)
        assert 'tithi_number' in tithi
        assert 1 <= tithi['tithi_number'] <= 30

    def test_vara_calculation(self):
        """Test vara (weekday) calculation."""
        from packages.cosmos.src.panchanga import get_vara
        from packages.cosmos.src import get_julian_day

        # January 1, 2024 was a Monday
        dt = datetime(2024, 1, 1, 12, 0)
        jd = get_julian_day(dt)

        vara = get_vara(jd)
        assert vara['vara_name'] == 'Monday', f"Expected Monday, got {vara['vara_name']}"


class TestDivisionalCharts:
    """Test divisional chart calculations."""

    def test_navamsa_calculation(self):
        """Test Navamsa (D9) chart calculation."""
        from packages.cosmos.src import get_divisional_chart

        # 15° Aries should give specific navamsa position
        navamsa = get_divisional_chart(15.0, 9)
        assert 0 <= navamsa < 360

    def test_dasamsa_calculation(self):
        """Test Dasamsa (D10) chart calculation."""
        from packages.cosmos.src import get_divisional_chart

        dasamsa = get_divisional_chart(45.0, 10)
        assert 0 <= dasamsa < 360


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
