"""Tests for synastry_rules.json knowledge file.

Validates JSON structure, key counts, and interpretation quality for:
- Cross aspects (10 planet pairs x 5 aspect types = 50)
- House overlay (6 planets x 12 houses = 72)
- Composite planets in signs (7 planets x 12 signs = 84)
"""

import json
from pathlib import Path

import pytest

RULES_DIR = Path(__file__).parent.parent.parent / "knowledge" / "rules"

SIGNS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]

ASPECT_TYPES = ["conjunction", "sextile", "square", "trine", "opposition"]

CROSS_ASPECT_PAIRS = [
    "sun_moon",
    "sun_venus",
    "sun_mars",
    "sun_jupiter",
    "sun_saturn",
    "moon_venus",
    "moon_mars",
    "moon_jupiter",
    "venus_mars",
    "venus_jupiter",
]

HOUSE_OVERLAY_PLANETS = ["sun", "moon", "venus", "mars", "jupiter", "saturn"]

COMPOSITE_PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]

HOUSE_NUMBERS = [str(i) for i in range(1, 13)]


@pytest.fixture(scope="module")
def synastry_data():
    """Load synastry rules data."""
    filepath = RULES_DIR / "synastry_rules.json"
    assert filepath.exists(), f"File not found: {filepath}"
    with filepath.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["synastry_rules"]


class TestSynastryRulesStructure:
    def test_file_loads_successfully(self, synastry_data):
        assert synastry_data, "synastry_rules should not be empty"

    def test_has_all_top_level_sections(self, synastry_data):
        expected_sections = {
            "description",
            "version",
            "cross_aspects",
            "house_overlay",
            "composite_planets_in_signs",
        }
        assert expected_sections.issubset(set(synastry_data.keys()))

    def test_has_description_and_version(self, synastry_data):
        assert len(synastry_data["description"]) > 30
        assert synastry_data["version"] == "1.0"


class TestCrossAspects:
    def test_has_all_ten_pairs(self, synastry_data):
        pairs = synastry_data["cross_aspects"]
        assert set(pairs.keys()) == set(
            CROSS_ASPECT_PAIRS
        ), f"Missing pairs: {set(CROSS_ASPECT_PAIRS) - set(pairs.keys())}"

    def test_each_pair_has_five_aspects(self, synastry_data):
        for pair, data in synastry_data["cross_aspects"].items():
            assert set(data.keys()) == set(
                ASPECT_TYPES
            ), f"{pair} missing aspects: {set(ASPECT_TYPES) - set(data.keys())}"

    def test_each_aspect_has_quality_and_interpretation(self, synastry_data):
        for pair, aspects in synastry_data["cross_aspects"].items():
            for aspect_type, aspect_data in aspects.items():
                assert "quality" in aspect_data, f"{pair}.{aspect_type} missing 'quality'"
                assert (
                    "interpretation" in aspect_data
                ), f"{pair}.{aspect_type} missing 'interpretation'"

    def test_interpretations_are_substantial(self, synastry_data):
        for pair, aspects in synastry_data["cross_aspects"].items():
            for aspect_type, aspect_data in aspects.items():
                interp = aspect_data["interpretation"]
                assert (
                    len(interp) > 80
                ), f"{pair}.{aspect_type} interpretation too short: {len(interp)} chars"

    def test_quality_values_are_valid(self, synastry_data):
        valid_qualities = {
            "very_harmonious",
            "harmonious",
            "mildly_challenging",
            "challenging",
            "very_challenging",
            "complex",
            "dynamic",
        }
        for pair, aspects in synastry_data["cross_aspects"].items():
            for aspect_type, aspect_data in aspects.items():
                assert (
                    aspect_data["quality"] in valid_qualities
                ), f"{pair}.{aspect_type} has invalid quality: {aspect_data['quality']}"

    def test_cross_aspect_total_count(self, synastry_data):
        total = sum(len(aspects) for aspects in synastry_data["cross_aspects"].values())
        assert total == 50, f"Expected 50 cross aspects, got {total}"


class TestHouseOverlay:
    def test_has_all_six_planets(self, synastry_data):
        planets = synastry_data["house_overlay"]
        assert set(planets.keys()) == set(
            HOUSE_OVERLAY_PLANETS
        ), f"Missing planets: {set(HOUSE_OVERLAY_PLANETS) - set(planets.keys())}"

    def test_each_planet_has_twelve_houses(self, synastry_data):
        for planet, houses in synastry_data["house_overlay"].items():
            assert set(houses.keys()) == set(
                HOUSE_NUMBERS
            ), f"{planet} missing houses: {set(HOUSE_NUMBERS) - set(houses.keys())}"

    def test_each_interpretation_is_substantial(self, synastry_data):
        for planet, houses in synastry_data["house_overlay"].items():
            for house, interp in houses.items():
                assert isinstance(interp, str), f"{planet} house {house} should be a string"
                assert (
                    len(interp) > 50
                ), f"{planet} house {house} interpretation too short: {len(interp)} chars"

    def test_house_overlay_total_count(self, synastry_data):
        total = sum(len(houses) for houses in synastry_data["house_overlay"].values())
        assert total == 72, f"Expected 72 house overlays, got {total}"

    def test_interpretations_mention_partner(self, synastry_data):
        """House overlays should reference the partner's planet effect."""
        for planet, houses in synastry_data["house_overlay"].items():
            partner_mentions = sum(
                1
                for interp in houses.values()
                if "partner" in interp.lower() or "Partner" in interp
            )
            assert partner_mentions >= 6, (
                f"{planet} should mention 'partner' in at least half the houses, "
                f"found {partner_mentions}"
            )


class TestCompositePlanetsInSigns:
    def test_has_all_seven_planets(self, synastry_data):
        planets = synastry_data["composite_planets_in_signs"]
        assert set(planets.keys()) == set(
            COMPOSITE_PLANETS
        ), f"Missing planets: {set(COMPOSITE_PLANETS) - set(planets.keys())}"

    def test_each_planet_has_twelve_signs(self, synastry_data):
        for planet, signs in synastry_data["composite_planets_in_signs"].items():
            assert set(signs.keys()) == set(
                SIGNS
            ), f"{planet} missing signs: {set(SIGNS) - set(signs.keys())}"

    def test_each_interpretation_is_substantial(self, synastry_data):
        for planet, signs in synastry_data["composite_planets_in_signs"].items():
            for sign, interp in signs.items():
                assert isinstance(interp, str), f"{planet} in {sign} should be a string"
                assert (
                    len(interp) > 50
                ), f"{planet} in {sign} interpretation too short: {len(interp)} chars"

    def test_composite_total_count(self, synastry_data):
        total = sum(len(signs) for signs in synastry_data["composite_planets_in_signs"].values())
        assert total == 84, f"Expected 84 composite interpretations, got {total}"

    def test_interpretations_describe_relationship(self, synastry_data):
        """Composite interpretations should describe the relationship, not individuals."""
        relationship_words = [
            "relationship",
            "couple",
            "partner",
            "together",
            "bond",
            "connection",
            "union",
        ]
        for planet, signs in synastry_data["composite_planets_in_signs"].items():
            for sign, interp in signs.items():
                has_relationship_word = any(word in interp.lower() for word in relationship_words)
                assert (
                    has_relationship_word
                ), f"{planet} in {sign} should describe the relationship, not individual planets"


class TestOverallRuleCount:
    def test_total_rule_count(self, synastry_data):
        """Verify total rule count is approximately 206."""
        cross_aspects = sum(len(aspects) for aspects in synastry_data["cross_aspects"].values())
        house_overlays = sum(len(houses) for houses in synastry_data["house_overlay"].values())
        composites = sum(
            len(signs) for signs in synastry_data["composite_planets_in_signs"].values()
        )
        total = cross_aspects + house_overlays + composites
        assert total >= 200, f"Expected at least 200 rules, got {total}"
