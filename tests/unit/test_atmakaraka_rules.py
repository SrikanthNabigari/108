"""Tests for atmakaraka_rules.json knowledge file.

Validates JSON structure, key counts, and interpretation quality for:
- Atmakaraka by planet (9 planets)
- Karakamsha by sign (12 signs)
- Planets in Karakamsha (9 planets)
- Planets aspecting Karakamsha (9 planets)
- Ishta Devata by planet (9 planets)
- Ishta Devata by sign (12 signs)
"""

import json
from pathlib import Path

import pytest

RULES_DIR = Path(__file__).parent.parent.parent / "knowledge" / "rules"

PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
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


@pytest.fixture(scope="module")
def atmakaraka_data():
    """Load atmakaraka rules data."""
    filepath = RULES_DIR / "atmakaraka_rules.json"
    assert filepath.exists(), f"File not found: {filepath}"
    with filepath.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["atmakaraka_rules"]


class TestAtmakarakaRulesStructure:
    def test_file_loads_successfully(self, atmakaraka_data):
        assert atmakaraka_data, "atmakaraka_rules should not be empty"

    def test_has_all_top_level_sections(self, atmakaraka_data):
        expected_sections = {
            "description",
            "version",
            "ak_by_planet",
            "karakamsha_by_sign",
            "planets_in_karakamsha",
            "planets_aspecting_karakamsha",
            "ishta_devata_by_planet",
            "ishta_devata_by_sign",
        }
        assert expected_sections.issubset(set(atmakaraka_data.keys()))

    def test_has_description_and_version(self, atmakaraka_data):
        assert len(atmakaraka_data["description"]) > 50
        assert atmakaraka_data["version"] == "1.0"


class TestAkByPlanet:
    def test_has_all_nine_planets(self, atmakaraka_data):
        ak_planets = atmakaraka_data["ak_by_planet"]
        assert set(ak_planets.keys()) == set(PLANETS)

    def test_each_planet_has_required_fields(self, atmakaraka_data):
        required_fields = {
            "soul_lesson",
            "karmic_focus",
            "spiritual_path",
            "strengths",
            "challenges",
        }
        for planet, data in atmakaraka_data["ak_by_planet"].items():
            for field in required_fields:
                assert field in data, f"{planet} missing field: {field}"

    def test_soul_lesson_is_substantial(self, atmakaraka_data):
        for planet, data in atmakaraka_data["ak_by_planet"].items():
            assert (
                len(data["soul_lesson"]) > 50
            ), f"{planet} soul_lesson too short: {len(data['soul_lesson'])} chars"

    def test_strengths_and_challenges_are_lists(self, atmakaraka_data):
        for planet, data in atmakaraka_data["ak_by_planet"].items():
            assert isinstance(data["strengths"], list), f"{planet} strengths not a list"
            assert isinstance(data["challenges"], list), f"{planet} challenges not a list"
            assert len(data["strengths"]) >= 3, f"{planet} needs at least 3 strengths"
            assert len(data["challenges"]) >= 3, f"{planet} needs at least 3 challenges"


class TestKarakamshaBySign:
    def test_has_all_twelve_signs(self, atmakaraka_data):
        km_signs = atmakaraka_data["karakamsha_by_sign"]
        assert set(km_signs.keys()) == set(SIGNS)

    def test_each_sign_has_required_fields(self, atmakaraka_data):
        required_fields = {
            "soul_purpose",
            "career_direction",
            "spiritual_expression",
            "relationship_approach",
        }
        for sign, data in atmakaraka_data["karakamsha_by_sign"].items():
            for field in required_fields:
                assert field in data, f"{sign} missing field: {field}"

    def test_soul_purpose_is_substantial(self, atmakaraka_data):
        for sign, data in atmakaraka_data["karakamsha_by_sign"].items():
            assert (
                len(data["soul_purpose"]) > 50
            ), f"{sign} soul_purpose too short: {len(data['soul_purpose'])} chars"

    def test_career_direction_is_substantial(self, atmakaraka_data):
        for sign, data in atmakaraka_data["karakamsha_by_sign"].items():
            assert len(data["career_direction"]) > 30, f"{sign} career_direction too short"


class TestPlanetsInKarakamsha:
    def test_has_all_nine_planets(self, atmakaraka_data):
        planets = atmakaraka_data["planets_in_karakamsha"]
        assert set(planets.keys()) == set(PLANETS)

    def test_each_planet_has_required_fields(self, atmakaraka_data):
        required_fields = {"interpretation", "career_indication", "spiritual_indication"}
        for planet, data in atmakaraka_data["planets_in_karakamsha"].items():
            for field in required_fields:
                assert field in data, f"{planet} missing field: {field}"

    def test_interpretation_is_substantial(self, atmakaraka_data):
        for planet, data in atmakaraka_data["planets_in_karakamsha"].items():
            assert (
                len(data["interpretation"]) > 80
            ), f"{planet} interpretation too short: {len(data['interpretation'])} chars"


class TestPlanetsAspectingKarakamsha:
    def test_has_all_nine_planets(self, atmakaraka_data):
        planets = atmakaraka_data["planets_aspecting_karakamsha"]
        assert set(planets.keys()) == set(PLANETS)

    def test_each_planet_has_required_fields(self, atmakaraka_data):
        required_fields = {"interpretation", "effect_area"}
        for planet, data in atmakaraka_data["planets_aspecting_karakamsha"].items():
            for field in required_fields:
                assert field in data, f"{planet} missing field: {field}"

    def test_interpretation_is_substantial(self, atmakaraka_data):
        for planet, data in atmakaraka_data["planets_aspecting_karakamsha"].items():
            assert len(data["interpretation"]) > 50, f"{planet} interpretation too short"


class TestIshtaDevataByPlanet:
    def test_has_all_nine_planets(self, atmakaraka_data):
        planets = atmakaraka_data["ishta_devata_by_planet"]
        assert set(planets.keys()) == set(PLANETS)

    def test_each_planet_has_required_fields(self, atmakaraka_data):
        required_fields = {"deity", "worship_practice", "mantra", "significance"}
        for planet, data in atmakaraka_data["ishta_devata_by_planet"].items():
            for field in required_fields:
                assert field in data, f"{planet} missing field: {field}"

    def test_mantras_start_with_om(self, atmakaraka_data):
        for planet, data in atmakaraka_data["ishta_devata_by_planet"].items():
            assert data["mantra"].startswith("Om"), f"{planet} mantra should start with 'Om'"

    def test_deities_are_not_empty(self, atmakaraka_data):
        for planet, data in atmakaraka_data["ishta_devata_by_planet"].items():
            assert len(data["deity"]) > 3, f"{planet} deity name too short"


class TestIshtaDevataBySign:
    def test_has_all_twelve_signs(self, atmakaraka_data):
        signs = atmakaraka_data["ishta_devata_by_sign"]
        assert set(signs.keys()) == set(SIGNS)

    def test_each_sign_has_required_fields(self, atmakaraka_data):
        required_fields = {"deity", "significance"}
        for sign, data in atmakaraka_data["ishta_devata_by_sign"].items():
            for field in required_fields:
                assert field in data, f"{sign} missing field: {field}"

    def test_significance_is_substantial(self, atmakaraka_data):
        for sign, data in atmakaraka_data["ishta_devata_by_sign"].items():
            assert len(data["significance"]) > 40, f"{sign} significance too short"


class TestRuleCount:
    def test_total_rule_count(self, atmakaraka_data):
        """Verify total rule count is approximately 66."""
        ak_by_planet = len(atmakaraka_data["ak_by_planet"])  # 9
        karakamsha_by_sign = len(atmakaraka_data["karakamsha_by_sign"])  # 12
        planets_in_km = len(atmakaraka_data["planets_in_karakamsha"])  # 9
        planets_aspecting = len(atmakaraka_data["planets_aspecting_karakamsha"])  # 9
        ishta_by_planet = len(atmakaraka_data["ishta_devata_by_planet"])  # 9
        ishta_by_sign = len(atmakaraka_data["ishta_devata_by_sign"])  # 12

        total = (
            ak_by_planet
            + karakamsha_by_sign
            + planets_in_km
            + planets_aspecting
            + ishta_by_planet
            + ishta_by_sign
        )
        assert total >= 60, f"Expected at least 60 rules, got {total}"
