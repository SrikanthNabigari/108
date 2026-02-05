"""Tests for enriched transit analysis in packages/context/src/transits.py."""

from packages.context.src.transits import get_enriched_transit_analysis

SAMPLE_TRANSIT_DATA = {
    "sun": {"rashi": 10, "nakshatra": "shatabhisha", "longitude": 310.0, "is_retrograde": False},
    "moon": {"rashi": 3, "nakshatra": "pushya", "longitude": 100.0, "is_retrograde": False},
    "mars": {"rashi": 5, "nakshatra": "chitra", "longitude": 170.0, "is_retrograde": False},
    "mercury": {"rashi": 10, "nakshatra": "dhanishta", "longitude": 305.0, "is_retrograde": True},
    "jupiter": {"rashi": 1, "nakshatra": "rohini", "longitude": 45.0, "is_retrograde": False},
    "venus": {
        "rashi": 11,
        "nakshatra": "purva_bhadrapada",
        "longitude": 330.0,
        "is_retrograde": False,
    },
    "saturn": {"rashi": 10, "nakshatra": "shatabhisha", "longitude": 315.0, "is_retrograde": True},
}


class TestGetEnrichedTransitAnalysis:
    """Tests for get_enriched_transit_analysis."""

    def test_returns_base_analysis(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA)
        assert "sade_sati" in result
        assert "dhaiya" in result
        assert "planet_transits" in result
        assert "summary" in result

    def test_nakshatra_effects_present(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA)
        for planet in SAMPLE_TRANSIT_DATA:
            transit = result["planet_transits"].get(planet, {})
            assert "nakshatra_effects" in transit, f"Missing nakshatra_effects for {planet}"

    def test_combustion_present(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA)
        # Mercury at 305, Sun at 310 = within 14 degrees (combust)
        mercury_transit = result["planet_transits"]["mercury"]
        assert "combustion" in mercury_transit
        assert mercury_transit["combustion"]["is_combust"] is True

    def test_sun_not_combust(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA)
        sun_transit = result["planet_transits"]["sun"]
        assert sun_transit["combustion"]["is_combust"] is False

    def test_retrograde_effects_for_retrograde_planet(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA)
        # Mercury and Saturn are retrograde in sample data
        mercury_transit = result["planet_transits"]["mercury"]
        assert mercury_transit["retrograde_effects"] != {}
        assert "general" in mercury_transit["retrograde_effects"]

    def test_no_retrograde_effects_for_direct_planet(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA)
        mars_transit = result["planet_transits"]["mars"]
        assert mars_transit["retrograde_effects"] == {}

    def test_ashtakavarga_empty_without_chart(self):
        result = get_enriched_transit_analysis(10, SAMPLE_TRANSIT_DATA, chart=None)
        for planet in SAMPLE_TRANSIT_DATA:
            transit = result["planet_transits"].get(planet, {})
            assert transit.get("ashtakavarga") == {}

    def test_minimal_transit_data(self):
        minimal = {
            "sun": {"rashi": 0, "nakshatra": "ashwini", "longitude": 5.0, "is_retrograde": False},
        }
        result = get_enriched_transit_analysis(0, minimal)
        assert "planet_transits" in result
        assert "sun" in result["planet_transits"]
