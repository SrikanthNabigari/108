"""Tests for Chandra Kala Nadi and Nadi Amsha systems."""
from packages.self.src.chandra_kala_nadi import (
    get_ckn_reading,
    get_conjunctions,
    get_planet_sign_map,
)
from packages.self.src.nadi_amsha_interpreter import (
    calculate_nadi_amsha_position,
    get_kp_sublord,
    get_nadi_amsha_chart,
)

# User's natal chart
USER_PLANETS = {
    "sun": {"longitude": 227.2154, "rashi": "scorpio", "house": 2},
    "moon": {"longitude": 324.1124, "rashi": "aquarius", "house": 5},
    "mars": {"longitude": 93.7587, "rashi": "cancer", "house": 10},
    "mercury": {"longitude": 208.6609, "rashi": "libra", "house": 1},
    "jupiter": {"longitude": 166.2399, "rashi": "virgo", "house": 12},
    "venus": {"longitude": 269.3543, "rashi": "sagittarius", "house": 3},
    "saturn": {"longitude": 289.9336, "rashi": "capricorn", "house": 4},
    "rahu": {"longitude": 238.2083, "rashi": "scorpio", "house": 2},
    "ketu": {"longitude": 58.2083, "rashi": "taurus", "house": 8},
}


class TestCKNSignMap:
    def test_sign_map_builds(self):
        sign_map = get_planet_sign_map(USER_PLANETS)
        assert "Scorpio" in sign_map
        assert "sun" in sign_map["Scorpio"]
        assert "rahu" in sign_map["Scorpio"]

    def test_conjunction_detected(self):
        sign_map = get_planet_sign_map(USER_PLANETS)
        conjunctions = get_conjunctions(sign_map)
        scorpio_conj = next((c for c in conjunctions if c["sign"] == "Scorpio"), None)
        assert scorpio_conj is not None
        assert "sun" in scorpio_conj["planets"]
        assert "rahu" in scorpio_conj["planets"]


class TestCKNReading:
    def test_reading_returns_success(self):
        result = get_ckn_reading(USER_PLANETS, "gemini", "aquarius")
        assert result["success"] is True
        assert "conjunctions" in result
        assert "jupiter_12_year_timeline" in result

    def test_moon_analysis(self):
        result = get_ckn_reading(USER_PLANETS, "gemini", "aquarius")
        assert result["moon_analysis"] is not None
        assert result["moon_analysis"]["natal_moon_sign"] == "Aquarius"

    def test_jupiter_house_from_moon(self):
        # Jupiter in Gemini = 5th from Aquarius Moon
        result = get_ckn_reading(USER_PLANETS, "gemini", "aquarius")
        assert result["moon_analysis"]["jupiter_house_from_moon"] == 5


class TestNadiAmsha:
    def test_basic_position(self):
        pos = calculate_nadi_amsha_position(0.0)
        assert pos["amsha_number"] == 0
        assert pos["nadi_type"] == "Adi"

    def test_nadi_types(self):
        # amsha 0 = Adi
        pos = calculate_nadi_amsha_position(0.0)
        assert pos["nadi_type"] == "Adi"
        # amsha 50 = Madhya (at 10.0° in sign 0)
        pos = calculate_nadi_amsha_position(10.0)
        assert pos["nadi_type"] == "Madhya"
        # amsha 100 = Antya (at 20.0° in sign 0)
        pos = calculate_nadi_amsha_position(20.0)
        assert pos["nadi_type"] == "Antya"

    def test_user_moon_d150(self):
        # Moon at 324.1124° — Aquarius 24.11°
        pos = calculate_nadi_amsha_position(324.1124)
        assert pos["natal_sign"] == "Aquarius"
        assert pos["amsha_number"] == 120  # int(24.11/0.2)
        assert pos["nadi_type"] == "Antya"  # 120 >= 100

    def test_full_chart(self):
        result = get_nadi_amsha_chart(USER_PLANETS)
        assert result["success"] is True
        assert "planet_positions" in result
        assert "moon" in result["planet_positions"]
        assert "dominant_nadi" in result

    def test_kp_sublord(self):
        result = get_kp_sublord(324.1124, house_num=5)
        assert "sublord" in result
        assert result["house"] == 5
