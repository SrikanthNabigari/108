"""Tests for packages/self/src/divisional_interpreter.py."""

from packages.cosmos.src.divisional import get_divisional_chart
from packages.self.src.divisional_interpreter import (
    get_divisional_analysis,
    interpret_d9_chart,
    interpret_d9_position,
    interpret_d10_chart,
    interpret_d10_position,
)

SAMPLE_LONGITUDES = {
    "sun": 125.5,  # Leo ~5.5
    "moon": 215.3,  # Scorpio ~5.3
    "mars": 45.2,  # Taurus ~15.2
    "mercury": 130.0,  # Leo ~10
    "jupiter": 250.0,  # Sagittarius ~10
    "venus": 100.0,  # Cancer ~10
    "saturn": 320.0,  # Aquarius ~20
}


class TestInterpretD9Position:
    """Tests for interpret_d9_position."""

    def test_sun_in_aries(self):
        result = interpret_d9_position("sun", "aries")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert result["rashi"] == "aries"
        assert result["theme"] != ""
        assert result["marriage"] != ""
        assert result["dharma"] != ""
        assert result["strength"] == "exalted"

    def test_sun_in_libra_debilitated(self):
        result = interpret_d9_position("sun", "libra")
        assert result["found"] is True
        assert result["strength"] == "debilitated"

    def test_all_12_signs_for_sun(self):
        signs = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]
        for sign in signs:
            result = interpret_d9_position("sun", sign)
            assert result["found"] is True, f"Missing D9 data for Sun in {sign}"

    def test_moon_position(self):
        result = interpret_d9_position("moon", "cancer")
        assert result["found"] is True

    def test_invalid_planet_returns_not_found(self):
        result = interpret_d9_position("pluto", "aries")
        assert result["found"] is False

    def test_invalid_sign_returns_not_found(self):
        result = interpret_d9_position("sun", "ophiuchus")
        assert result["found"] is False


class TestInterpretD10Position:
    """Tests for interpret_d10_position."""

    def test_sun_in_aries(self):
        result = interpret_d10_position("sun", "aries")
        assert result["found"] is True
        assert "career" in result
        assert "leadership" in result

    def test_mars_in_capricorn(self):
        result = interpret_d10_position("mars", "capricorn")
        assert result["found"] is True

    def test_invalid_combo(self):
        result = interpret_d10_position("pluto", "aries")
        assert result["found"] is False


class TestInterpretD9Chart:
    """Tests for interpret_d9_chart."""

    def test_full_chart_interpretation(self):
        d9 = get_divisional_chart(SAMPLE_LONGITUDES, 9)
        result = interpret_d9_chart(d9)
        assert result["division"] == 9
        assert result["division_name"] == "Navamsha"
        assert len(result["planets"]) > 0

    def test_each_planet_interpreted(self):
        d9 = get_divisional_chart(SAMPLE_LONGITUDES, 9)
        result = interpret_d9_chart(d9)
        for planet_name in SAMPLE_LONGITUDES:
            assert planet_name in result["planets"]


class TestInterpretD10Chart:
    """Tests for interpret_d10_chart."""

    def test_full_chart_interpretation(self):
        d10 = get_divisional_chart(SAMPLE_LONGITUDES, 10)
        result = interpret_d10_chart(d10)
        assert result["division"] == 10
        assert result["division_name"] == "Dashamsha"
        assert len(result["planets"]) > 0


class TestGetDivisionalAnalysis:
    """Tests for get_divisional_analysis."""

    def test_returns_both_d9_d10(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        assert "d9_navamsha" in result
        assert "d10_dashamsha" in result

    def test_d9_has_planets(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        assert len(result["d9_navamsha"]["planets"]) > 0

    def test_d10_has_planets(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        assert len(result["d10_dashamsha"]["planets"]) > 0
