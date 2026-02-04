"""Unit tests for the transits (Gochara) module.

Tests cover:
- Sade Sati detection and phases
- Dhaiya (Kantaka/Ashtama Shani) detection
- Gochara planet transit analysis
- Vedha (obstruction) detection
- Full transit analysis with multiple planets
"""

import pytest
from packages.context.src.transits import (
    check_sade_sati,
    check_dhaiya,
    get_gochara,
    get_full_transit_analysis,
    get_transiting_planet_house,
    is_planet_favorable_in_house,
    validate_transit_data,
    GOCHARA_FAVORABLE,
    VEDHA_POINTS,
)


class TestSadeSati:
    """Test Sade Sati detection and phase identification."""

    def test_sade_sati_rising_phase(self):
        """Test Sade Sati rising phase (Saturn in 12th from Moon)."""
        # Moon in Aquarius (10), Saturn in Capricorn (9)
        # 9 to 10 = -1, becomes 11 (12th house)
        result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=9)

        assert result["active"] is True
        assert result["phase"] == "rising"
        assert result["house_from_moon"] == 12
        assert "mental stress" in str(result["effects"]).lower()

    def test_sade_sati_peak_phase(self):
        """Test Sade Sati peak phase (Saturn conjunct Moon)."""
        # Moon in Aquarius (10), Saturn in Aquarius (10)
        result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=10)

        assert result["active"] is True
        assert result["phase"] == "peak"
        assert result["house_from_moon"] == 1
        assert "maximum challenges" in str(result["effects"]).lower()

    def test_sade_sati_setting_phase(self):
        """Test Sade Sati setting phase (Saturn in 2nd from Moon)."""
        # Moon in Aquarius (10), Saturn in Pisces (11)
        result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=11)

        assert result["active"] is True
        assert result["phase"] == "setting"
        assert result["house_from_moon"] == 2
        assert "financial concerns" in str(result["effects"]).lower()

    def test_sade_sati_inactive(self):
        """Test when Sade Sati is not active."""
        # Moon in Aquarius (10), Saturn in Gemini (2)
        # 2 to 10 = 8 (8th house - not Sade Sati)
        result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=2)

        assert result["active"] is False
        assert result["phase"] is None
        assert result["house_from_moon"] == 8
        assert result["effects"] == []

    def test_sade_sati_duration(self):
        """Test that Sade Sati phases have duration info."""
        result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=10)

        assert "duration_years" in result
        assert result["duration_years"] == 2.5

    def test_sade_sati_remedies(self):
        """Test that active Sade Sati includes remedies."""
        result = check_sade_sati(natal_moon_rashi=10, saturn_rashi=10)

        assert "remedies" in result
        assert len(result["remedies"]) > 0
        assert isinstance(result["remedies"], list)


class TestDhaiya:
    """Test Dhaiya (Kantaka/Ashtama Shani) detection."""

    def test_dhaiya_kantaka_shani(self):
        """Test Kantaka Shani (Saturn in 4th from Moon)."""
        # Moon in Aquarius (10), Saturn in Taurus (1)
        # 1 to 10 = -9, becomes 3 (4th house)
        result = check_dhaiya(natal_moon_rashi=10, saturn_rashi=1)

        assert result["active"] is True
        assert result["type"] == "kantaka_shani"
        assert result["house_from_moon"] == 4
        assert "domestic" in str(result["effects"]).lower()
        assert "vehicle" in str(result["effects"]).lower()

    def test_dhaiya_ashtama_shani(self):
        """Test Ashtama Shani (Saturn in 8th from Moon)."""
        # Moon in Aquarius (10), Saturn in Gemini (2)
        # 2 to 10 = -8, becomes 4 (wait, that's wrong)
        # Let me recalculate: (2 - 10) % 12 + 1 = (-8 % 12) + 1 = 4 + 1 = 5
        # Actually: (2 - 10) % 12 + 1 = (-8) % 12 + 1 = 4 + 1 = 5 (5th house)
        # For 8th house: Moon at 10, need Saturn at (10 + 7) % 12 = 5 (Gemini is 2)
        # Saturn at 5, Moon at 10: (5-10)%12+1 = (-5)%12+1 = 7+1 = 8 ✓
        result = check_dhaiya(natal_moon_rashi=10, saturn_rashi=5)

        assert result["active"] is True
        assert result["type"] == "ashtama_shani"
        assert result["house_from_moon"] == 8
        assert "sudden obstacles" in str(result["effects"]).lower()
        assert "health" in str(result["effects"]).lower()

    def test_dhaiya_inactive(self):
        """Test when Dhaiya is not active."""
        # Saturn not in 4th or 8th from Moon
        result = check_dhaiya(natal_moon_rashi=10, saturn_rashi=0)

        assert result["active"] is False
        assert result["type"] is None
        assert result["effects"] == []

    def test_dhaiya_remedies(self):
        """Test that active Dhaiya includes remedies."""
        result = check_dhaiya(natal_moon_rashi=10, saturn_rashi=1)

        assert "remedies" in result
        assert len(result["remedies"]) > 0


class TestGochara:
    """Test individual planet Gochara (transit) analysis."""

    def test_jupiter_favorable_position(self):
        """Test Jupiter in favorable position (5th from Moon)."""
        # Moon in Aquarius (10), Jupiter in Gemini (2)
        # (2-10)%12+1 = (-8)%12+1 = 4+1 = 5 ✓
        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="jupiter",
            transit_rashi=2,
        )

        assert result["planet"] == "jupiter"
        assert result["house_from_moon"] == 5
        assert result["is_favorable"] is True
        assert result["net_effect"] == "favorable"
        assert len(result["effects"]) > 0

    def test_saturn_favorable_position(self):
        """Test Saturn in favorable position (3rd from Moon)."""
        # Moon in Aquarius (10), Saturn in Scorpio (7)
        # (7-10)%12+1 = (-3)%12+1 = 9+1 = 10... wait
        # Actually: (7-10)%12 = -3 % 12 = 9, +1 = 10 (10th house, favorable)
        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="saturn",
            transit_rashi=7,
        )

        assert result["planet"] == "saturn"
        assert result["is_favorable"] is True

    def test_mars_unfavorable_position(self):
        """Test Mars in unfavorable position."""
        # Moon in Aquarius (10), Mars in Aries (0)
        # (0-10)%12+1 = (-10)%12+1 = 2+1 = 3 (3rd house, favorable for Mars)
        # Let's put Mars in 1st house instead: same sign
        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="mars",
            transit_rashi=10,  # Same as Moon
        )

        assert result["planet"] == "mars"
        assert result["house_from_moon"] == 1
        assert result["is_favorable"] is False
        assert result["net_effect"] == "unfavorable"

    def test_venus_highly_favorable(self):
        """Test Venus which has many favorable houses."""
        # Venus in 5th from Moon should be favorable
        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="venus",
            transit_rashi=2,
        )

        assert result["is_favorable"] is True
        assert result["net_effect"] == "favorable"

    def test_moon_self_position_favorable(self):
        """Test Moon with Sun same as natal Moon is favorable."""
        # The Sun in the same house as Moon
        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="moon",
            transit_rashi=10,
        )

        assert result["house_from_moon"] == 1
        assert result["is_favorable"] is True


class TestVedha:
    """Test Vedha (obstruction) detection in favorable positions."""

    def test_vedha_obstructing_favorable_position(self):
        """Test vedha when planet in favorable but obstructed."""
        # Jupiter in 5th (favorable) from Moon
        # But if Saturn is in 4th (vedha point for Jupiter 5th), it obstructs
        transit_positions = {
            "jupiter": 2,  # 5th from Moon (10)
            "saturn": 1,   # 4th from Moon (10) - vedha point
        }

        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="jupiter",
            transit_rashi=2,
            all_transit_rashis=transit_positions,
        )

        # Jupiter's vedha point in 5th is 4th (per VEDHA_POINTS)
        assert result["has_vedha"] is True
        assert result["vedha_by"] == "saturn"
        assert result["net_effect"] == "unfavorable"

    def test_no_vedha_when_no_planets_in_vedha_house(self):
        """Test no vedha when vedha house is empty."""
        transit_positions = {
            "jupiter": 2,  # 5th from Moon (10)
            "saturn": 0,   # Different house
        }

        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="jupiter",
            transit_rashi=2,
            all_transit_rashis=transit_positions,
        )

        assert result["has_vedha"] is False
        assert result["vedha_by"] is None
        assert result["net_effect"] == "favorable"

    def test_sun_saturn_exception_no_vedha(self):
        """Test that Sun and Saturn don't cause vedha to each other."""
        transit_positions = {
            "sun": 2,  # 5th from Moon
            "saturn": 1,  # 4th from Moon (vedha point for Sun)
        }

        result = get_gochara(
            natal_moon_rashi=10,
            transit_planet="sun",
            transit_rashi=2,
            all_transit_rashis=transit_positions,
        )

        # Sun-Saturn exception - no vedha
        assert result["has_vedha"] is False
        assert result["net_effect"] == "favorable"


class TestFullTransitAnalysis:
    """Test complete transit analysis for all planets."""

    def test_full_analysis_with_all_planets(self):
        """Test analysis with all 9 planets."""
        transit_positions = {
            "sun": 0,
            "moon": 1,
            "mars": 2,
            "mercury": 3,
            "jupiter": 4,
            "venus": 5,
            "saturn": 6,
            "rahu": 7,
            "ketu": 8,
        }

        result = get_full_transit_analysis(
            natal_moon_rashi=10,
            transit_positions=transit_positions,
        )

        assert result["natal_moon_sign"] == 10
        assert "sade_sati" in result
        assert "dhaiya" in result
        assert "planet_transits" in result
        assert "summary" in result
        assert len(result["planet_transits"]) == 9

    def test_full_analysis_summary(self):
        """Test summary calculations in full analysis."""
        transit_positions = {
            "sun": 0,  # 3rd from Moon 10 - favorable
            "moon": 2,  # 5th from Moon - favorable
            "mars": 3,  # 6th from Moon - favorable
            "mercury": 4,
            "jupiter": 5,
            "venus": 6,
            "saturn": 7,
            "rahu": 8,
            "ketu": 9,
        }

        result = get_full_transit_analysis(
            natal_moon_rashi=10,
            transit_positions=transit_positions,
        )

        assert "favorable_count" in result["summary"]
        assert "unfavorable_count" in result["summary"]
        assert "overall_trend" in result["summary"]
        assert result["summary"]["total_planets_analyzed"] == 9

    def test_overall_trend_highly_favorable(self):
        """Test overall trend when most planets are favorable."""
        # Setup: most planets in favorable positions
        transit_positions = {
            "jupiter": 2,  # 5th - favorable
            "venus": 3,    # 6th - favorable
            "mercury": 4,  # 7th - favorable
            "moon": 5,     # 8th - favorable
            "mars": 6,     # 9th - unfavorable
            "saturn": 7,   # 10th - favorable
        }

        result = get_full_transit_analysis(
            natal_moon_rashi=10,
            transit_positions=transit_positions,
        )

        # 5 favorable, 1 unfavorable -> favorable trend
        assert result["summary"]["overall_trend"] in ["favorable", "highly_favorable"]

    def test_overall_trend_challenging(self):
        """Test overall trend when most planets are unfavorable."""
        transit_positions = {
            "sun": 10,      # unfavorable
            "moon": 0,      # unfavorable
            "mars": 1,      # unfavorable
            "mercury": 11,  # unfavorable
            "jupiter": 2,   # 5th - favorable
        }

        result = get_full_transit_analysis(
            natal_moon_rashi=10,
            transit_positions=transit_positions,
        )

        # 4 unfavorable, 1 favorable
        assert result["summary"]["overall_trend"] in ["unfavorable", "challenging"]

    def test_sade_sati_in_full_analysis(self):
        """Test Sade Sati is included in full analysis."""
        transit_positions = {
            "sun": 0,
            "saturn": 10,  # Peak phase
        }

        result = get_full_transit_analysis(
            natal_moon_rashi=10,
            transit_positions=transit_positions,
        )

        assert result["sade_sati"]["active"] is True
        assert result["sade_sati"]["phase"] == "peak"


class TestHelperFunctions:
    """Test utility and helper functions."""

    def test_get_transiting_planet_house(self):
        """Test house position calculation."""
        house = get_transiting_planet_house(
            natal_moon_rashi=10,
            transit_planet="jupiter",
            transit_rashi=2,
        )

        assert house == 5

    def test_is_planet_favorable_in_house(self):
        """Test favorable house check."""
        # Jupiter in 5th from Moon is favorable
        assert is_planet_favorable_in_house("jupiter", 5) is True

        # Jupiter in 1st from Moon is unfavorable
        assert is_planet_favorable_in_house("jupiter", 1) is False

    def test_is_planet_favorable_case_insensitive(self):
        """Test that planet names are case-insensitive."""
        assert is_planet_favorable_in_house("JUPITER", 5) is True
        assert is_planet_favorable_in_house("JuPiTeR", 5) is True

    def test_validate_transit_data_valid(self):
        """Test validation of valid transit data."""
        valid_data = {
            "sun": 0,
            "moon": 1,
        }

        is_valid, message = validate_transit_data(
            natal_moon_rashi=10,
            transit_positions=valid_data,
        )

        assert is_valid is True
        assert message == "Data is valid"

    def test_validate_transit_data_invalid_moon_rashi(self):
        """Test validation rejects invalid Moon rashi."""
        is_valid, message = validate_transit_data(
            natal_moon_rashi=12,  # Invalid: > 11
            transit_positions={"sun": 0},
        )

        assert is_valid is False
        assert "natal_moon_rashi" in message

    def test_validate_transit_data_invalid_transit_rashi(self):
        """Test validation rejects invalid transit rashi."""
        is_valid, message = validate_transit_data(
            natal_moon_rashi=10,
            transit_positions={"sun": 15},  # Invalid: > 11
        )

        assert is_valid is False
        assert "rashi" in message.lower()

    def test_validate_transit_data_empty_positions(self):
        """Test validation rejects empty transit positions."""
        is_valid, message = validate_transit_data(
            natal_moon_rashi=10,
            transit_positions={},  # Empty
        )

        assert is_valid is False
        assert "empty" in message.lower()


class TestConstantsAndData:
    """Test that constants and data are well-formed."""

    def test_gochara_favorable_structure(self):
        """Test GOCHARA_FAVORABLE data structure."""
        assert isinstance(GOCHARA_FAVORABLE, dict)

        expected_planets = [
            "sun", "moon", "mars", "mercury",
            "jupiter", "venus", "saturn", "rahu", "ketu"
        ]
        for planet in expected_planets:
            assert planet in GOCHARA_FAVORABLE
            assert isinstance(GOCHARA_FAVORABLE[planet], list)
            # All houses should be 1-12
            for house in GOCHARA_FAVORABLE[planet]:
                assert 1 <= house <= 12

    def test_vedha_points_structure(self):
        """Test VEDHA_POINTS data structure."""
        assert isinstance(VEDHA_POINTS, dict)

        for planet, vedha_map in VEDHA_POINTS.items():
            assert isinstance(vedha_map, dict)
            for favorable_house, vedha_house in vedha_map.items():
                assert 1 <= favorable_house <= 12
                assert 1 <= vedha_house <= 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
