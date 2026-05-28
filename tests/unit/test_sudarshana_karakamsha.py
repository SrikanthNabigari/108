"""Tests for Sudarshana Chakra and Karakamsha Lagna."""
from packages.self.src.karakamsha import analyze_karakamsha, get_atmakaraka, get_karakamsha_lagna
from packages.self.src.sudarshana_chakra import get_sudarshana_chakra

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


class TestSudarshanaCakra:
    def test_returns_success(self):
        result = get_sudarshana_chakra(USER_PLANETS, "libra", "aquarius", "scorpio")
        assert result["success"] is True
        assert "house_analyses" in result
        assert "life_area_scores" in result

    def test_all_12_houses(self):
        result = get_sudarshana_chakra(USER_PLANETS, "libra", "aquarius", "scorpio")
        assert len(result["house_analyses"]) == 12

    def test_three_ascendants(self):
        result = get_sudarshana_chakra(USER_PLANETS, "libra", "aquarius", "scorpio")
        assert result["three_ascendants"]["lagna"] == "Libra"
        assert result["three_ascendants"]["moon"] == "Aquarius"
        assert result["three_ascendants"]["sun"] == "Scorpio"

    def test_confirmation_counts(self):
        result = get_sudarshana_chakra(USER_PLANETS, "libra", "aquarius", "scorpio")
        for _h, analysis in result["house_analyses"].items():
            assert 0 <= analysis["confirmation_count"] <= 3

    def test_life_areas(self):
        result = get_sudarshana_chakra(USER_PLANETS, "libra", "aquarius", "scorpio")
        assert "career" in result["life_area_scores"]
        assert "marriage" in result["life_area_scores"]
        assert "wealth" in result["life_area_scores"]


class TestKarakamsha:
    def test_atmakaraka_detection(self):
        ak, deg = get_atmakaraka(USER_PLANETS)
        assert ak in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
        assert 0 <= deg <= 30

    def test_karakamsha_lagna(self):
        kl = get_karakamsha_lagna(USER_PLANETS)
        assert "karakamsha_lagna" in kl
        assert kl["karakamsha_lagna"] in [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]

    def test_full_analysis(self):
        result = analyze_karakamsha(USER_PLANETS)
        assert result["success"] is True
        assert "soul_summary" in result
        assert "house_analyses" in result
        assert len(result["house_analyses"]) == 12

    def test_soul_summary_keys(self):
        result = analyze_karakamsha(USER_PLANETS)
        ss = result["soul_summary"]
        assert "soul_nature" in ss
        assert "past_life_merit" in ss
        assert "dharma" in ss
        assert "moksha_potential" in ss
