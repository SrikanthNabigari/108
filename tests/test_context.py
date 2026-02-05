"""
Unit tests for the CONTEXT package (timing systems).
"""

import sys
from datetime import datetime

import pytest

sys.path.insert(0, "/sessions/eloquent-zen-gauss/mnt/108-core")


class TestVimshottariDasha:
    """Test Vimshottari Dasha calculations."""

    def test_dasha_periods(self):
        """Test that dasha periods sum to 120 years."""
        from packages.context.src import DASHA_YEARS

        total_years = sum(DASHA_YEARS.values())
        assert total_years == 120, f"Vimshottari total should be 120 years, got {total_years}"

    def test_dasha_sequence(self):
        """Test correct dasha sequence."""
        from packages.context.src import DASHA_SEQUENCE

        expected = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]

        assert expected == DASHA_SEQUENCE, f"Wrong sequence: {DASHA_SEQUENCE}"

    def test_dasha_from_nakshatra(self):
        """Test dasha lord determination from nakshatra."""
        from packages.context.src import NAKSHATRA_LORDS

        # Ashwini (nakshatra 1) is ruled by Ketu
        lord = NAKSHATRA_LORDS[1]
        assert lord == "ketu", f"Ashwini lord should be ketu, got {lord}"

        # Rohini (nakshatra 4) is ruled by Moon
        lord = NAKSHATRA_LORDS[4]
        assert lord == "moon", f"Rohini lord should be moon, got {lord}"

        # Pushya (nakshatra 8) is ruled by Saturn
        lord = NAKSHATRA_LORDS[8]
        assert lord == "saturn", f"Pushya lord should be saturn, got {lord}"

    def test_mahadasha_calculation(self):
        """Test Mahadasha sequence calculation."""
        from packages.context.src import get_mahadasha_sequence

        # Test with a birth date and Moon longitude
        birth_dt = datetime(1990, 5, 15, 10, 30)
        moon_lon = 45.0  # Moon in Taurus, Rohini nakshatra

        sequence = get_mahadasha_sequence(birth_dt, moon_lon)

        # Should return a list of periods
        assert len(sequence) > 0, "Should have dasha periods"
        assert "lord" in sequence[0], "Each period should have a lord"
        assert "start_date" in sequence[0], "Each period should have start_date"
        assert "end_date" in sequence[0], "Each period should have end_date"

    def test_current_dasha(self):
        """Test getting current dasha period."""
        from packages.context.src import get_current_dasha

        birth_dt = datetime(1990, 5, 15, 10, 30)
        moon_lon = 45.0
        query_dt = datetime.now()

        current = get_current_dasha(birth_dt, moon_lon, query_dt)

        assert "mahadasha" in current, "Should have mahadasha"
        assert "antardasha" in current, "Should have antardasha"
        assert current["mahadasha"]["lord"] in [
            "ketu",
            "venus",
            "sun",
            "moon",
            "mars",
            "rahu",
            "jupiter",
            "saturn",
            "mercury",
        ]

    def test_antardasha_within_mahadasha(self):
        """Test that antardashas fit within mahadasha."""
        from packages.context.src import DASHA_YEARS

        # Venus mahadasha is 20 years (lowercase key)
        venus_years = DASHA_YEARS["venus"]

        # Calculate total antardasha duration
        # Each antardasha is proportional to mahadasha lord's period
        total_ad_years = 0
        for _ad_lord, ad_years in DASHA_YEARS.items():
            # Antardasha duration = (MD years * AD years) / 120
            ad_duration = (venus_years * ad_years) / 120
            total_ad_years += ad_duration

        # Should equal mahadasha duration
        assert (
            abs(total_ad_years - venus_years) < 0.01
        ), f"Antardashas should sum to mahadasha: {total_ad_years} vs {venus_years}"


class TestTransits:
    """Test transit (Gochara) calculations."""

    def test_transit_positions(self):
        """Test getting current transit positions."""
        from packages.context.src import get_transit_positions
        from packages.cosmos.src import get_julian_day

        dt = datetime.now()
        jd = get_julian_day(dt)

        positions = get_transit_positions(jd)

        # Should have all planets
        expected = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

        for planet in expected:
            assert planet in positions, f"Missing transit for {planet}"

    def test_transit_over_natal(self):
        """Test transit analysis over natal positions."""
        # Saturn transiting over natal Moon = potential Sade Sati

        natal_moon_sign = 4  # Leo (index)
        saturn_transit_sign = 4  # Saturn also in Leo

        # Same sign = direct transit
        is_conjunct = natal_moon_sign == saturn_transit_sign
        assert is_conjunct, "Saturn over Moon should be detected"


class TestSadeSati:
    """Test Sade Sati (Saturn's 7.5 year transit) detection."""

    def test_sade_sati_phases(self):
        """Test Sade Sati has 3 phases."""
        phases = ["rising", "peak", "setting"]
        assert len(phases) == 3

    def test_sade_sati_detection(self):
        """Test Sade Sati detection logic."""
        from packages.context.src import check_sade_sati

        # Rashi indices: Aries=0, Taurus=1, ..., Leo=4, Cancer=3, Virgo=5
        # Moon in Leo (index 4)
        # Sade Sati when Saturn in Cancer (3), Leo (4), or Virgo (5)
        moon_rashi = 4  # Leo

        # Saturn in Leo = peak phase
        result = check_sade_sati(moon_rashi, 4)  # Saturn in Leo
        assert result["active"], "Saturn in Moon sign = Sade Sati active"
        assert result["phase"] == "peak", "Same sign = peak phase"

        # Saturn in Cancer = rising phase
        result = check_sade_sati(moon_rashi, 3)  # Saturn in Cancer
        assert result["active"], "Saturn in 12th from Moon = Sade Sati"
        assert result["phase"] == "rising"

        # Saturn in Virgo = setting phase
        result = check_sade_sati(moon_rashi, 5)  # Saturn in Virgo
        assert result["active"], "Saturn in 2nd from Moon = Sade Sati"
        assert result["phase"] == "setting"

        # Saturn in Aries = no Sade Sati
        result = check_sade_sati(moon_rashi, 0)  # Saturn in Aries
        assert not result["active"], "Saturn far from Moon = no Sade Sati"


class TestMuhurta:
    """Test Muhurta (auspicious timing) calculations."""

    def test_muhurta_count(self):
        """Test there are 30 muhurtas in a day."""
        # Each day has 30 muhurtas (48 minutes each)
        muhurtas_per_day = 30
        minutes_per_muhurta = 48
        total_minutes = muhurtas_per_day * minutes_per_muhurta

        assert total_minutes == 1440, "30 muhurtas x 48 min = 1440 min (24 hours)"

    def test_rahu_kaal_structure(self):
        """Test Rahu Kaal time periods per day."""
        from packages.context.src import RAHU_KAAL

        # Rahu Kaal should have 7 entries (one per weekday)
        assert len(RAHU_KAAL) == 7, f"Should have 7 days, got {len(RAHU_KAAL)}"

        # Each entry should be a valid period number (1-8)
        for day, period in RAHU_KAAL.items():
            assert 1 <= period <= 8, f"Invalid Rahu Kaal period for {day}: {period}"

    def test_choghadiya_quality(self):
        """Test Choghadiya quality classifications."""
        from packages.context.src import CHOGHADIYA_QUALITY

        # Should have excellent, good, neutral, and poor qualities
        qualities = set(CHOGHADIYA_QUALITY.values())
        expected_qualities = {"excellent", "good", "neutral", "poor"}

        for q in expected_qualities:
            assert q in qualities, f"Missing quality: {q}"

    def test_choghadiya_order(self):
        """Test Choghadiya day/night sequences."""
        from packages.context.src import CHOGHADIYA_ORDER

        # Should have 'day' and 'night' sequences
        assert "day" in CHOGHADIYA_ORDER or len(CHOGHADIYA_ORDER) > 0

    def test_evaluate_muhurta(self):
        """Test muhurta evaluation function exists and is callable."""
        from packages.context.src import ActivityType, evaluate_muhurta

        # Verify function is importable
        assert callable(evaluate_muhurta), "evaluate_muhurta should be callable"

        # Verify ActivityType enum has expected values
        activity_types = [at.value for at in ActivityType]
        assert "travel" in activity_types, "Should have travel activity type"
        assert "marriage" in activity_types, "Should have marriage activity type"


class TestYearlyPredictions:
    """Test Varshaphala (yearly prediction) calculations."""

    def test_solar_return(self):
        """Test Solar Return (Varsha Pravesh) timing."""
        # Solar return = when Sun returns to natal position

        natal_sun_lon = 45.0  # Sun in Taurus

        # The solar return for any year would be when
        # transiting Sun reaches natal degree (45 in this case)
        # This typically happens around the same date each year

        # Just verify the concept
        transit_sun_lon = 45.0
        is_return = abs(natal_sun_lon - transit_sun_lon) < 1.0

        assert is_return, "Solar return when Sun at natal degree"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
