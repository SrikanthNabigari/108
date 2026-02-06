"""Tests for Planetary War (Graha Yuddha) detection.

Tests the planetary_war.py module: detect_planetary_wars() and get_war_effects().
"""

from packages.core.src.constants import Planet
from packages.self.src.planetary_war import (
    detect_planetary_wars,
    get_war_effects,
)


def _make_planets(**kwargs):
    """Create planet dict. Each kwarg: name=(lon, lat, retro, house)."""
    planets = {}
    for name, vals in kwargs.items():
        lon = vals[0]
        lat = vals[1] if len(vals) > 1 else 0.0
        retro = vals[2] if len(vals) > 2 else False
        house = vals[3] if len(vals) > 3 else 1
        planets[Planet(name)] = {
            "longitude": lon,
            "latitude": lat,
            "is_retrograde": retro,
            "house": house,
        }
    return planets


class TestDetectPlanetaryWars:
    """Test detect_planetary_wars() function."""

    def test_no_war_planets_far_apart(self):
        """No war when planets are more than 1 degree apart."""
        planets = _make_planets(
            mars=(45.0,),
            jupiter=(60.0,),
            venus=(120.0,),
            mercury=(200.0,),
            saturn=(300.0,),
        )
        wars = detect_planetary_wars(planets)
        assert wars == []

    def test_war_two_planets_within_1_degree(self):
        """War detected when two planets are within 1 degree."""
        planets = _make_planets(
            mars=(100.0, 1.5),
            jupiter=(100.5, 0.5),  # 0.5 degrees from Mars
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1
        assert wars[0]["planet1"] in ("mars", "jupiter")
        assert wars[0]["planet2"] in ("mars", "jupiter")
        assert wars[0]["separation_degrees"] <= 1.0

    def test_war_winner_higher_latitude(self):
        """Planet with higher latitude wins."""
        planets = _make_planets(
            mars=(100.0, 2.0),  # Higher latitude
            jupiter=(100.3, 0.5),  # Lower latitude
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1
        assert wars[0]["winner"] == "mars"
        assert wars[0]["loser"] == "jupiter"

    def test_venus_retrograde_always_wins(self):
        """Venus always wins when retrograde."""
        planets = _make_planets(
            venus=(100.0, 0.1, True),  # Retrograde Venus, low latitude
            mars=(100.5, 5.0, False),  # High latitude but Venus is retro
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1
        assert wars[0]["winner"] == "venus"
        assert wars[0]["loser"] == "mars"

    def test_venus_not_retrograde_normal_rules(self):
        """Non-retrograde Venus follows normal latitude rules."""
        planets = _make_planets(
            venus=(100.0, 0.1, False),  # Low latitude, not retrograde
            mars=(100.5, 5.0),  # Higher latitude
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1
        assert wars[0]["winner"] == "mars"
        assert wars[0]["loser"] == "venus"

    def test_sun_excluded_from_war(self):
        """Sun cannot participate in planetary war."""
        planets = _make_planets(
            sun=(100.0,),
            mars=(100.5,),
        )
        # Sun should be excluded, no wars
        wars = detect_planetary_wars(planets)
        assert wars == []

    def test_moon_excluded_from_war(self):
        """Moon cannot participate in planetary war."""
        planets = _make_planets(
            moon=(100.0,),
            jupiter=(100.5,),
        )
        wars = detect_planetary_wars(planets)
        assert wars == []

    def test_rahu_excluded_from_war(self):
        """Rahu cannot participate in planetary war."""
        planets = _make_planets(
            rahu=(100.0,),
            mercury=(100.5,),
        )
        wars = detect_planetary_wars(planets)
        assert wars == []

    def test_ketu_excluded_from_war(self):
        """Ketu cannot participate in planetary war."""
        planets = _make_planets(
            ketu=(100.0,),
            saturn=(100.5,),
        )
        wars = detect_planetary_wars(planets)
        assert wars == []

    def test_multiple_wars_detected(self):
        """Multiple simultaneous wars should be detected."""
        planets = _make_planets(
            mars=(100.0, 2.0),
            jupiter=(100.3, 0.5),
            venus=(200.0, 1.0),
            saturn=(200.5, 3.0),
            mercury=(50.0,),  # Far from everyone
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 2

    def test_war_effects_have_required_keys(self):
        """War result dict should have all required keys."""
        planets = _make_planets(
            mars=(100.0, 2.0),
            mercury=(100.5, 0.5),
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1
        war = wars[0]
        assert "planet1" in war
        assert "planet2" in war
        assert "winner" in war
        assert "loser" in war
        assert "separation_degrees" in war
        assert "effects" in war
        assert war["effects"]["loser_weakened"] is True
        assert war["effects"]["winner_strengthened"] is True

    def test_exactly_1_degree_is_war(self):
        """Exactly 1 degree separation should be a war (<=1.0)."""
        planets = _make_planets(
            mars=(100.0, 1.0),
            saturn=(101.0, 0.5),
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1

    def test_just_over_1_degree_no_war(self):
        """Slightly over 1 degree = no war."""
        planets = _make_planets(
            mars=(100.0, 1.0),
            saturn=(101.1, 0.5),
        )
        wars = detect_planetary_wars(planets)
        assert wars == []

    def test_longitude_wrap_around(self):
        """War detection works across the 360/0 boundary."""
        planets = _make_planets(
            mars=(359.5, 2.0),
            jupiter=(0.3, 0.5),  # 0.8 degrees from Mars (wrapping)
        )
        wars = detect_planetary_wars(planets)
        assert len(wars) == 1

    def test_empty_chart_no_wars(self):
        """Empty planet dict returns no wars."""
        wars = detect_planetary_wars({})
        assert wars == []

    def test_single_planet_no_war(self):
        """Single planet cannot have a war."""
        planets = _make_planets(mars=(100.0,))
        wars = detect_planetary_wars(planets)
        assert wars == []


class TestGetWarEffects:
    """Test get_war_effects() function."""

    def test_basic_effects(self):
        result = get_war_effects("mars", "mercury")
        assert result["winner"] == "mars"
        assert result["loser"] == "mercury"
        assert len(result["loser_significations"]) > 0
        assert "intellect" in result["loser_significations"]

    def test_effects_with_lagna_houses(self):
        """Test house effects when lagna_rashi is provided."""
        result = get_war_effects("mars", "mercury", houses="aries")
        assert result["winner"] == "mars"
        assert result["loser"] == "mercury"
        # Mercury rules Gemini (house 3 from Aries) and Virgo (house 6)
        assert 3 in result["affected_houses"]
        assert 6 in result["affected_houses"]

    def test_effects_with_dict_houses(self):
        """Test house effects with house-sign dict."""
        houses = {3: "gemini", 6: "virgo"}
        result = get_war_effects("jupiter", "mercury", houses=houses)
        assert 3 in result["affected_houses"]
        assert 6 in result["affected_houses"]

    def test_remedial_notes_present(self):
        result = get_war_effects("saturn", "venus")
        assert len(result["remedial_notes"]) > 0

    def test_invalid_planet_name(self):
        result = get_war_effects("invalid", "also_invalid")
        assert result["loser_significations"] == []
        assert result["affected_houses"] == []

    def test_mars_significations(self):
        result = get_war_effects("jupiter", "mars")
        assert "courage" in result["loser_significations"]

    def test_no_houses_provided(self):
        result = get_war_effects("mars", "venus")
        assert result["affected_houses"] == []
        assert result["house_effects"] == []
