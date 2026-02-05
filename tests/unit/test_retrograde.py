"""Tests for packages/self/src/retrograde.py."""

from packages.self.src.retrograde import (
    RETROGRADE_PLANETS,
    get_retrograde_analysis,
    get_retrograde_effects,
)


class TestGetRetrogradeEffects:
    """Tests for get_retrograde_effects."""

    def test_mars_natal_effects(self):
        result = get_retrograde_effects("mars", is_natal=True)
        assert result["planet"] == "mars"
        assert result["is_natal"] is True
        assert len(result["general"]) > 0
        assert len(result["positive"]) > 0
        assert len(result["negative"]) > 0
        assert result["karmic_indication"] != ""

    def test_mercury_transit_effects(self):
        result = get_retrograde_effects("mercury", is_natal=False)
        assert result["planet"] == "mercury"
        assert result["is_natal"] is False
        assert len(result["general"]) > 0
        assert "karmic_indication" not in result

    def test_transit_with_house(self):
        result = get_retrograde_effects("jupiter", is_natal=False, house=5)
        assert result["house_effects"] != {}
        assert "theme" in result["house_effects"]

    def test_transit_without_house(self):
        result = get_retrograde_effects("saturn", is_natal=False)
        assert result["house_effects"] == {}

    def test_all_retrograde_planets_have_effects(self):
        for planet in RETROGRADE_PLANETS:
            result = get_retrograde_effects(planet, is_natal=True)
            assert len(result["general"]) > 0, f"No natal effects for {planet}"
            result = get_retrograde_effects(planet, is_natal=False)
            assert len(result["general"]) > 0, f"No transit effects for {planet}"

    def test_sun_not_retrograde(self):
        result = get_retrograde_effects("sun", is_natal=True)
        assert result["effects"] == {}

    def test_moon_not_retrograde(self):
        result = get_retrograde_effects("moon", is_natal=True)
        assert result["effects"] == {}

    def test_remedies_returned(self):
        result = get_retrograde_effects("venus", is_natal=True)
        assert len(result["remedies"]) > 0

    def test_all_12_houses_for_transit(self):
        for house in range(1, 13):
            result = get_retrograde_effects("mars", is_natal=False, house=house)
            assert result["house_effects"] != {}, f"No house effects for house {house}"

    def test_unknown_planet(self):
        result = get_retrograde_effects("pluto", is_natal=True)
        assert result["effects"] == {}


class TestGetRetrogradeAnalysis:
    """Tests for get_retrograde_analysis."""

    def test_no_retrogrades(self):
        result = get_retrograde_analysis(
            {
                "mars": {"is_retrograde": False, "house": 1},
                "mercury": {"is_retrograde": False, "house": 3},
            }
        )
        assert result["count"] == 0
        assert result["retrograde_planets"] == []

    def test_one_retrograde(self):
        result = get_retrograde_analysis(
            {
                "mars": {"is_retrograde": True, "house": 5},
                "mercury": {"is_retrograde": False, "house": 3},
            }
        )
        assert result["count"] == 1
        assert result["retrograde_planets"][0]["planet"] == "mars"

    def test_multiple_retrogrades(self):
        result = get_retrograde_analysis(
            {
                "mars": {"is_retrograde": True, "house": 5},
                "jupiter": {"is_retrograde": True, "house": 9},
                "saturn": {"is_retrograde": True, "house": 7},
            }
        )
        assert result["count"] == 3

    def test_natal_karmic_themes(self):
        result = get_retrograde_analysis(
            {"mars": {"is_retrograde": True, "house": 5}},
            is_natal=True,
        )
        assert len(result["karmic_themes"]) > 0

    def test_transit_no_karmic_themes(self):
        result = get_retrograde_analysis(
            {"mars": {"is_retrograde": True, "house": 5}},
            is_natal=False,
        )
        assert result["karmic_themes"] == []

    def test_skips_non_retrograde_planets(self):
        result = get_retrograde_analysis(
            {
                "sun": {"is_retrograde": False, "house": 1},
                "moon": {"is_retrograde": False, "house": 4},
                "rahu": {"is_retrograde": True, "house": 6},
            }
        )
        # Sun, Moon, Rahu are not in RETROGRADE_PLANETS
        assert result["count"] == 0
