"""Tests for remedies recommendation engine."""

from packages.self.src.remedies import (
    PLANETS,
    get_planet_remedies,
    prioritize_remedies,
    recommend_remedies,
)


class TestGetPlanetRemedies:
    """Tests for get_planet_remedies function."""

    def test_sun_remedies(self):
        result = get_planet_remedies("sun")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert "gemstone" in result["remedies"]
        assert "mantra" in result["remedies"]

    def test_all_9_planets_have_remedies(self):
        for planet in PLANETS:
            result = get_planet_remedies(planet)
            assert result["found"] is True, f"No remedies for {planet}"
            assert len(result["remedies"]) > 0, f"Empty remedies for {planet}"

    def test_gemstone_data_present(self):
        result = get_planet_remedies("sun")
        gem = result["remedies"]["gemstone"]
        assert gem["primary"] == "ruby"
        assert gem["finger"] == "ring"
        assert gem["metal"] == "gold"

    def test_mantra_data_present(self):
        result = get_planet_remedies("jupiter")
        mantra = result["remedies"]["mantra"]
        assert "beej_mantra" in mantra
        assert "repetitions" in mantra
        assert mantra["repetitions"]["minimum"] == 108

    def test_charity_data_present(self):
        result = get_planet_remedies("saturn")
        charity = result["remedies"]["charity"]
        assert "items" in charity
        assert "day" in charity
        assert charity["day"] == "saturday"

    def test_worship_data_present(self):
        result = get_planet_remedies("mars")
        worship = result["remedies"]["worship"]
        assert worship["primary"] == "Hanuman"

    def test_general_remedies_present(self):
        result = get_planet_remedies("venus")
        general = result["remedies"]["general"]
        assert "color_therapy" in general
        assert "mudras" in general

    def test_invalid_planet_returns_not_found(self):
        result = get_planet_remedies("pluto")
        assert result["found"] is False

    def test_case_insensitive(self):
        result = get_planet_remedies("MOON")
        assert result["found"] is True
        assert result["planet"] == "moon"


class TestPrioritizeRemedies:
    """Tests for prioritize_remedies function."""

    def test_urgent_for_dasha_lord_with_dosha(self):
        remedies = [
            {"planet": "saturn", "reason": "test", "severity": "high"},
        ]
        conditions = {
            "dasha_lords": ["saturn"],
            "dosha_planets": ["saturn"],
            "weak_planets": [],
            "transit_afflictions": [],
        }
        result = prioritize_remedies(remedies, conditions)
        assert len(result["urgent"]) == 1
        assert len(result["recommended"]) == 0

    def test_urgent_for_high_severity_dosha(self):
        remedies = [
            {"planet": "rahu", "reason": "test", "severity": "high"},
        ]
        conditions = {
            "dasha_lords": [],
            "dosha_planets": ["rahu"],
            "weak_planets": [],
            "transit_afflictions": [],
        }
        result = prioritize_remedies(remedies, conditions)
        assert len(result["urgent"]) == 1

    def test_recommended_for_dasha_lord(self):
        remedies = [
            {"planet": "mercury", "reason": "test", "severity": "low"},
        ]
        conditions = {
            "dasha_lords": ["mercury"],
            "dosha_planets": [],
            "weak_planets": [],
            "transit_afflictions": [],
        }
        result = prioritize_remedies(remedies, conditions)
        assert len(result["recommended"]) == 1

    def test_recommended_for_weak_planet(self):
        remedies = [
            {"planet": "venus", "reason": "test", "severity": "low"},
        ]
        conditions = {
            "dasha_lords": [],
            "dosha_planets": [],
            "weak_planets": ["venus"],
            "transit_afflictions": [],
        }
        result = prioritize_remedies(remedies, conditions)
        assert len(result["recommended"]) == 1

    def test_optional_for_unrelated_planet(self):
        remedies = [
            {"planet": "jupiter", "reason": "test", "severity": "low"},
        ]
        conditions = {
            "dasha_lords": ["mercury"],
            "dosha_planets": [],
            "weak_planets": [],
            "transit_afflictions": [],
        }
        result = prioritize_remedies(remedies, conditions)
        assert len(result["optional"]) == 1

    def test_empty_input(self):
        result = prioritize_remedies(
            [],
            {"dasha_lords": [], "dosha_planets": [], "weak_planets": [], "transit_afflictions": []},
        )
        assert result["urgent"] == []
        assert result["recommended"] == []
        assert result["optional"] == []


class TestRecommendRemedies:
    """Tests for recommend_remedies main function."""

    def test_basic_recommendation(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "mercury"},
            active_doshas=[],
            weak_planets=[],
        )
        assert "urgent" in result
        assert "recommended" in result
        assert "optional" in result
        assert "summary" in result
        assert "planets_needing_remedies" in result

    def test_dasha_lord_gets_remedies(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "saturn"},
            active_doshas=[],
            weak_planets=[],
        )
        assert "saturn" in result["planets_needing_remedies"]
        total = result["summary"]["total_remedies"]
        assert total >= 1

    def test_dosha_planets_get_remedies(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "mercury"},
            active_doshas=[{"name": "mangal_dosha"}],
            weak_planets=[],
        )
        assert "mars" in result["planets_needing_remedies"]

    def test_weak_planets_get_remedies(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "mercury"},
            active_doshas=[],
            weak_planets=[{"planet": "venus", "shadbala": 0.4}],
        )
        assert "venus" in result["planets_needing_remedies"]

    def test_sade_sati_gives_saturn_remedies(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "saturn"},
            active_doshas=[{"name": "sade_sati", "severity": "high"}],
            weak_planets=[],
        )
        assert "saturn" in result["planets_needing_remedies"]
        # Saturn should be urgent (dasha lord + dosha)
        urgent_planets = [r["planet"] for r in result["urgent"]]
        assert "saturn" in urgent_planets

    def test_kaal_sarp_gives_rahu_ketu_remedies(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "mercury"},
            active_doshas=[{"name": "kaal_sarp_dosha"}],
            weak_planets=[],
        )
        assert "rahu" in result["planets_needing_remedies"]
        assert "ketu" in result["planets_needing_remedies"]

    def test_multiple_conditions_combined(self):
        result = recommend_remedies(
            current_dasha={
                "mahadasha_lord": "saturn",
                "antardasha_lord": "rahu",
            },
            active_doshas=[{"name": "sade_sati", "severity": "high"}],
            weak_planets=[{"planet": "moon"}],
        )
        assert "saturn" in result["planets_needing_remedies"]
        assert "rahu" in result["planets_needing_remedies"]
        assert "moon" in result["planets_needing_remedies"]
        assert result["summary"]["total_remedies"] >= 3

    def test_transit_afflictions(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "mercury"},
            active_doshas=[],
            weak_planets=[],
            current_transits={"mars": {"afflicted": True}},
        )
        assert "mars" in result["planets_needing_remedies"]

    def test_lagna_rashi_included(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "mercury"},
            active_doshas=[],
            weak_planets=[],
            lagna_rashi="libra",
        )
        assert result["lagna_rashi"] == "libra"

    def test_empty_conditions(self):
        result = recommend_remedies(
            current_dasha={},
            active_doshas=[],
            weak_planets=[],
        )
        assert result["summary"]["total_remedies"] == 0
        assert result["planets_needing_remedies"] == []

    def test_remedy_entry_has_mantra(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "sun"},
            active_doshas=[],
            weak_planets=[],
        )
        # Sun should be in recommended
        all_remedies = result["urgent"] + result["recommended"] + result["optional"]
        sun_remedies = [r for r in all_remedies if r["planet"] == "sun"]
        assert len(sun_remedies) == 1
        assert "remedy" in sun_remedies[0]  # mantra text

    def test_remedy_entry_has_gemstone(self):
        result = recommend_remedies(
            current_dasha={"mahadasha_lord": "jupiter"},
            active_doshas=[],
            weak_planets=[],
        )
        all_remedies = result["urgent"] + result["recommended"] + result["optional"]
        jupiter_remedies = [r for r in all_remedies if r["planet"] == "jupiter"]
        assert len(jupiter_remedies) == 1
        assert "gemstone" in jupiter_remedies[0]
        assert jupiter_remedies[0]["gemstone"]["primary"] == "yellow_sapphire"
