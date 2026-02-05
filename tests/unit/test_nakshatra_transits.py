"""Tests for nakshatra transit effects in packages/context/src/transits.py."""

from packages.context.src.transits import get_nakshatra_transit_effect


class TestGetNakshatraTransitEffect:
    """Tests for get_nakshatra_transit_effect."""

    def test_sun_in_ashwini(self):
        result = get_nakshatra_transit_effect("sun", "ashwini")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert result["nakshatra"] == "ashwini"
        assert result["theme"] != ""
        assert len(result["positive"]) > 0

    def test_moon_in_rohini(self):
        result = get_nakshatra_transit_effect("moon", "rohini")
        assert result["found"] is True

    def test_jupiter_in_punarvasu(self):
        result = get_nakshatra_transit_effect("jupiter", "punarvasu")
        assert result["found"] is True
        assert "best_for" in result

    def test_invalid_nakshatra(self):
        result = get_nakshatra_transit_effect("sun", "nonexistent")
        assert result["found"] is False

    def test_invalid_planet(self):
        result = get_nakshatra_transit_effect("pluto", "ashwini")
        assert result["found"] is False

    def test_case_insensitive(self):
        result = get_nakshatra_transit_effect("Sun", "Ashwini")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert result["nakshatra"] == "ashwini"

    def test_all_nine_planets_have_ashwini(self):
        planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
        for planet in planets:
            result = get_nakshatra_transit_effect(planet, "ashwini")
            assert result["found"] is True, f"Missing ashwini data for {planet}"

    def test_has_avoid_field(self):
        result = get_nakshatra_transit_effect("sun", "ashwini")
        assert "avoid" in result

    def test_saturn_in_pushya(self):
        # Saturn rules Pushya - should be a meaningful combination
        result = get_nakshatra_transit_effect("saturn", "pushya")
        assert result["found"] is True
        assert result["theme"] != ""

    def test_mars_in_mrigashira(self):
        # Mars rules Mrigashira
        result = get_nakshatra_transit_effect("mars", "mrigashira")
        assert result["found"] is True
