"""Tests for packages/self/src/combustion.py."""

from packages.self.src.combustion import (
    _angular_distance,
    check_combustion,
    get_combustion_analysis,
    get_combustion_house_effects,
)


class TestAngularDistance:
    """Tests for _angular_distance helper."""

    def test_same_longitude(self):
        assert _angular_distance(100.0, 100.0) == 0.0

    def test_simple_distance(self):
        assert _angular_distance(100.0, 110.0) == 10.0

    def test_reverse_order(self):
        assert _angular_distance(110.0, 100.0) == 10.0

    def test_wrapping_around_360(self):
        assert _angular_distance(5.0, 355.0) == 10.0

    def test_wrapping_other_direction(self):
        assert _angular_distance(355.0, 5.0) == 10.0

    def test_opposite_180(self):
        assert _angular_distance(0.0, 180.0) == 180.0


class TestCheckCombustion:
    """Tests for check_combustion."""

    def test_sun_cannot_be_combust(self):
        result = check_combustion("sun", 100.0, 100.0)
        assert result["is_combust"] is False
        assert result["angular_distance"] is None

    def test_rahu_cannot_be_combust(self):
        result = check_combustion("rahu", 100.0, 100.0)
        assert result["is_combust"] is False

    def test_ketu_cannot_be_combust(self):
        result = check_combustion("ketu", 100.0, 100.0)
        assert result["is_combust"] is False

    def test_moon_combust_within_12_degrees(self):
        # Moon combustion degree is 12
        result = check_combustion("moon", 100.0, 110.0)
        assert result["is_combust"] is True
        assert result["is_deep_combust"] is False
        assert result["angular_distance"] == 10.0
        assert result["strength_loss"] > 0

    def test_moon_deep_combust_within_6_degrees(self):
        result = check_combustion("moon", 100.0, 105.0)
        assert result["is_combust"] is True
        assert result["is_deep_combust"] is True
        assert result["strength_loss"] == 0.825

    def test_moon_not_combust_beyond_12_degrees(self):
        result = check_combustion("moon", 100.0, 115.0)
        assert result["is_combust"] is False
        assert result["strength_loss"] == 0.0

    def test_mars_combust_within_17_degrees(self):
        result = check_combustion("mars", 100.0, 115.0)
        assert result["is_combust"] is True

    def test_mars_not_combust_beyond_17(self):
        result = check_combustion("mars", 100.0, 120.0)
        assert result["is_combust"] is False

    def test_mercury_retrograde_uses_12_degrees(self):
        # Mercury direct: 14 degrees, retrograde: 12 degrees
        # At 13 degrees: combust if direct, NOT combust if retrograde
        result_direct = check_combustion("mercury", 100.0, 113.0, is_retrograde=False)
        result_retro = check_combustion("mercury", 100.0, 113.0, is_retrograde=True)
        assert result_direct["is_combust"] is True
        assert result_retro["is_combust"] is False

    def test_venus_retrograde_uses_8_degrees(self):
        # Venus direct: 10 degrees, retrograde: 8 degrees
        result_direct = check_combustion("venus", 100.0, 109.0, is_retrograde=False)
        result_retro = check_combustion("venus", 100.0, 109.0, is_retrograde=True)
        assert result_direct["is_combust"] is True
        assert result_retro["is_combust"] is False

    def test_combust_returns_effects(self):
        result = check_combustion("jupiter", 100.0, 105.0)
        assert result["is_combust"] is True
        assert "general" in result["effects"]
        assert len(result["remedies"]) > 0

    def test_not_combust_returns_empty_effects(self):
        result = check_combustion("jupiter", 100.0, 200.0)
        assert result["is_combust"] is False
        assert result["effects"] == {}
        assert result["remedies"] == []

    def test_saturn_combust_at_boundary(self):
        # Saturn combustion degree is 15
        result_exact = check_combustion("saturn", 100.0, 115.0)
        result_beyond = check_combustion("saturn", 100.0, 116.0)
        assert result_exact["is_combust"] is True
        assert result_beyond["is_combust"] is False

    def test_unknown_planet_returns_not_combust(self):
        result = check_combustion("pluto", 100.0, 100.0)
        assert result["is_combust"] is False


class TestGetCombustionAnalysis:
    """Tests for get_combustion_analysis."""

    def test_no_sun_returns_empty(self):
        result = get_combustion_analysis({"moon": {"longitude": 100.0}})
        assert result["total_count"] == 0

    def test_no_combust_planets(self):
        result = get_combustion_analysis(
            {
                "sun": {"longitude": 100.0},
                "moon": {"longitude": 200.0},
                "mars": {"longitude": 300.0},
            }
        )
        assert result["total_count"] == 0

    def test_one_combust_planet(self):
        result = get_combustion_analysis(
            {
                "sun": {"longitude": 100.0},
                "moon": {"longitude": 105.0},  # Within 12 degrees
                "mars": {"longitude": 300.0},  # Far away
            }
        )
        assert result["total_count"] == 1
        assert result["combust_planets"][0]["planet"] == "moon"

    def test_deep_combustion_tracked(self):
        result = get_combustion_analysis(
            {
                "sun": {"longitude": 100.0},
                "moon": {"longitude": 103.0},  # Deep: within 6
            }
        )
        assert "moon" in result["critical_combustions"]

    def test_multiple_combust(self):
        result = get_combustion_analysis(
            {
                "sun": {"longitude": 100.0},
                "moon": {"longitude": 105.0},
                "mercury": {"longitude": 108.0},
                "venus": {"longitude": 106.0},
            }
        )
        assert result["total_count"] == 3


class TestGetCombustionHouseEffects:
    """Tests for get_combustion_house_effects."""

    def test_valid_house_returns_data(self):
        result = get_combustion_house_effects("moon", 1)
        assert result["house"] == 1
        assert result["planet"] == "moon"
        assert result["description"] != ""

    def test_planet_specific_effects(self):
        result = get_combustion_house_effects("mars", 4)
        assert result["planet_specific"] != ""

    def test_invalid_house_returns_empty(self):
        result = get_combustion_house_effects("moon", 99)
        assert result["effects"] == {}

    def test_all_houses_have_data(self):
        for house in range(1, 13):
            result = get_combustion_house_effects("jupiter", house)
            assert result["house"] == house
