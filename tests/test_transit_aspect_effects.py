"""Tests for transit aspect effect interpretations (knowledge + code integration)."""

from packages.context.src.transit_aspects import _get_effect, get_transit_natal_aspects
from packages.core.src.knowledge_loader import get_transit_aspect_effects, load_rules

PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
ASPECT_TYPES = ["conjunction", "opposition", "trine", "square", "sextile"]
VALID_NATURES = {"harmonious", "tense", "intense", "challenging", "neutral"}


class TestKnowledgeFileStructure:
    """Verify the transit_aspect_effects.json file loads and has correct structure."""

    def test_file_loads(self):
        data = get_transit_aspect_effects()
        assert data, "transit_aspect_effects.json should load non-empty data"

    def test_all_transit_planets_present(self):
        data = get_transit_aspect_effects()
        for planet in PLANETS:
            assert planet in data, f"Missing transit planet: {planet}"

    def test_all_natal_planets_present_for_each_transit(self):
        data = get_transit_aspect_effects()
        for t_planet in PLANETS:
            for n_planet in PLANETS:
                assert (
                    n_planet in data[t_planet]
                ), f"Missing natal planet {n_planet} under transit {t_planet}"

    def test_all_aspect_types_present(self):
        data = get_transit_aspect_effects()
        for t_planet in PLANETS:
            for n_planet in PLANETS:
                for aspect in ASPECT_TYPES:
                    assert (
                        aspect in data[t_planet][n_planet]
                    ), f"Missing aspect {aspect} for {t_planet}-{n_planet}"

    def test_entry_has_effect_and_nature(self):
        data = get_transit_aspect_effects()
        for t_planet in PLANETS:
            for n_planet in PLANETS:
                for aspect in ASPECT_TYPES:
                    entry = data[t_planet][n_planet][aspect]
                    assert "effect" in entry, f"Missing 'effect' for {t_planet}-{n_planet}-{aspect}"
                    assert "nature" in entry, f"Missing 'nature' for {t_planet}-{n_planet}-{aspect}"

    def test_nature_values_valid(self):
        data = get_transit_aspect_effects()
        for t_planet in PLANETS:
            for n_planet in PLANETS:
                for aspect in ASPECT_TYPES:
                    nature = data[t_planet][n_planet][aspect]["nature"]
                    assert (
                        nature in VALID_NATURES
                    ), f"Invalid nature '{nature}' for {t_planet}-{n_planet}-{aspect}"

    def test_effects_are_nonempty_strings(self):
        data = get_transit_aspect_effects()
        for t_planet in PLANETS:
            for n_planet in PLANETS:
                for aspect in ASPECT_TYPES:
                    effect = data[t_planet][n_planet][aspect]["effect"]
                    assert (
                        isinstance(effect, str) and len(effect) > 5
                    ), f"Effect too short for {t_planet}-{n_planet}-{aspect}: '{effect}'"

    def test_total_entry_count(self):
        data = get_transit_aspect_effects()
        count = sum(len(data[t][n]) for t in PLANETS for n in PLANETS)
        assert count >= 405, f"Expected >= 405 entries, got {count}"

    def test_aspect_type_general_section(self):
        raw = load_rules("transit_aspect_effects")
        general = raw.get("aspect_type_general", {})
        assert general, "aspect_type_general section should exist"
        for aspect in ASPECT_TYPES:
            assert aspect in general, f"Missing {aspect} in aspect_type_general"
            assert "keyword" in general[aspect]
            assert "quality" in general[aspect]


class TestGetEffectFunction:
    """Verify _get_effect returns aspect-type-specific effects."""

    def test_returns_dict(self):
        result = _get_effect("sun", "moon", "conjunction")
        assert isinstance(result, dict)
        assert "effect" in result
        assert "nature" in result

    def test_aspect_type_differentiates(self):
        conj = _get_effect("saturn", "sun", "conjunction")
        trine = _get_effect("saturn", "sun", "trine")
        # Different aspects should give different effects
        assert (
            conj["effect"] != trine["effect"]
        ), "conjunction and trine should return different effects"

    def test_nature_field_populated(self):
        result = _get_effect("jupiter", "venus", "trine")
        assert result["nature"] in VALID_NATURES

    def test_fallback_for_unknown_aspect(self):
        result = _get_effect("sun", "moon", "nonexistent_aspect")
        assert result["effect"], "Should fallback gracefully for unknown aspect type"

    def test_fallback_for_unknown_planet(self):
        result = _get_effect("pluto", "sun", "conjunction")
        assert result["effect"], "Should fallback gracefully for unknown planet"


class TestAspectResultsIncludeNature:
    """Verify get_transit_natal_aspects returns nature field."""

    def test_aspects_have_nature_field(self):
        natal = {
            "sun": {"longitude": 100.0, "rashi": 3},
            "moon": {"longitude": 220.0, "rashi": 7},
        }
        transit = {
            "jupiter": {"longitude": 100.5, "rashi": 3, "speed": 0.08},
        }
        aspects = get_transit_natal_aspects(natal, transit, orb=5.0)
        assert len(aspects) > 0, "Should find at least one aspect"
        for asp in aspects:
            assert "nature" in asp, f"Aspect missing 'nature' field: {asp}"
            assert asp["nature"] in VALID_NATURES
