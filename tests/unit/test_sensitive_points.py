"""Tests for Jyotish sensitive points — Bhrigu Bindu, Indu Lagna, Sree Lagna."""
from packages.self.src.sensitive_points import (
    calculate_bhrigu_bindu,
    calculate_indu_lagna,
    calculate_sree_lagna,
    get_all_sensitive_points,
)

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


class TestBhriguBindu:
    def test_basic_calculation(self):
        bb = calculate_bhrigu_bindu(238.2083, 324.1124)
        assert "longitude" in bb
        assert "sign" in bb
        assert 0 <= bb["longitude"] < 360

    def test_user_chart_bb(self):
        # Rahu: 238.2083, Moon: 324.1124
        # diff = 85.9 < 180 → midpoint = (238.2083+324.1124)/2 = 281.16
        bb = calculate_bhrigu_bindu(238.2083, 324.1124)
        assert abs(bb["longitude"] - 281.16) < 0.1
        assert bb["sign"] == "Capricorn"

    def test_across_zero(self):
        # Test midpoint crossing 0°
        bb = calculate_bhrigu_bindu(350.0, 10.0)
        assert abs(bb["longitude"] - 0.0) < 1.0 or abs(bb["longitude"] - 360.0) < 1.0

    def test_normalization(self):
        bb = calculate_bhrigu_bindu(0.0, 180.0)
        assert bb["longitude"] == 90.0


class TestInduLagna:
    def test_user_chart_indu_lagna(self):
        # Libra lagna, Jupiter in Virgo (H12), Moon in Aquarius (H5)
        # H12 lord = Mercury, Bindu = 8
        # H5 lord = Saturn, Bindu = 1
        # Sum = 9, count 9 from Libra = Gemini
        il = calculate_indu_lagna(USER_PLANETS, "libra")
        assert il["indu_lagna_sign"] == "Gemini"
        assert il["bindu_sum"] == 9
        assert il["calculation"]["jupiter_bindu"] == 8
        assert il["calculation"]["moon_bindu"] == 1

    def test_indu_lagna_has_lord(self):
        il = calculate_indu_lagna(USER_PLANETS, "libra")
        assert "indu_lagna_lord" in il
        assert il["indu_lagna_lord"] == "mercury"

    def test_bindu_table(self):
        # Verify bindu values: Sun=30, Moon=16, Mars=6, Mercury=8, Jupiter=10, Venus=12, Saturn=1
        from packages.self.src.sensitive_points import INDU_BINDUS

        assert INDU_BINDUS["sun"] == 30
        assert INDU_BINDUS["moon"] == 16
        assert INDU_BINDUS["jupiter"] == 10
        assert INDU_BINDUS["saturn"] == 1


class TestSreeLagna:
    def test_user_chart_sree_lagna(self):
        # Moon: 324.1124, Venus: 269.3543
        # Sum: 593.4667 % 360 = 233.4667 → Scorpio 23.47°
        sl = calculate_sree_lagna(324.1124, 269.3543)
        assert sl["sign"] == "Scorpio"
        assert abs(sl["degree_in_sign"] - 23.47) < 0.1

    def test_normalization(self):
        sl = calculate_sree_lagna(200.0, 200.0)
        assert 0 <= sl["longitude"] < 360

    def test_with_lagna(self):
        # Libra lagna at ~180°, Sree Lagna in Scorpio = H2
        sl = calculate_sree_lagna(324.1124, 269.3543, lagna_longitude=180.9)
        assert sl["house_from_lagna"] == 2


class TestAllSensitivePoints:
    def test_complete_reading(self):
        result = get_all_sensitive_points(USER_PLANETS, "libra", 180.9)
        assert result["success"] is True
        assert "bhrigu_bindu" in result
        assert "indu_lagna" in result
        assert "sree_lagna" in result
        assert "summary" in result

    def test_natal_conjunctions(self):
        result = get_all_sensitive_points(USER_PLANETS, "libra")
        # BB at ~281.16° (Capricorn 11.16°)
        # Saturn at 289.93° (Capricorn 19.93°) — 8.77° away, outside 3° orb
        # No exact natal conjunctions expected
        assert "natal_conjunctions_with_bb" in result
