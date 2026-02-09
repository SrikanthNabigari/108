"""Tests for transit knowledge rule files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge" / "rules"


@pytest.fixture
def double_transit_rules():
    with (KNOWLEDGE_DIR / "double_transit_rules.json").open() as f:
        return json.load(f)


@pytest.fixture
def transit_lordship_rules():
    with (KNOWLEDGE_DIR / "transit_lordship_rules.json").open() as f:
        return json.load(f)


class TestDoubleTransitRules:
    def test_has_description(self, double_transit_rules):
        assert "description" in double_transit_rules
        assert len(double_transit_rules["description"]) > 20

    def test_has_12_rules(self, double_transit_rules):
        assert len(double_transit_rules["rules"]) == 12

    def test_all_houses_covered(self, double_transit_rules):
        houses = {r["house"] for r in double_transit_rules["rules"]}
        assert houses == set(range(1, 13))

    def test_rule_fields_complete(self, double_transit_rules):
        required = {
            "house",
            "themes",
            "effect",
            "strength_factors",
            "typical_events",
            "duration_note",
        }
        for rule in double_transit_rules["rules"]:
            assert required.issubset(rule.keys()), f"House {rule.get('house')} missing fields"

    def test_strength_factors_complete(self, double_transit_rules):
        required_factors = {"both_occupy", "one_occupy_one_aspect", "both_aspect"}
        for rule in double_transit_rules["rules"]:
            assert required_factors.issubset(rule["strength_factors"].keys())

    def test_themes_nonempty(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            assert len(rule["themes"]) >= 2

    def test_typical_events_nonempty(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            assert len(rule["typical_events"]) >= 3

    def test_effect_is_string(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            assert isinstance(rule["effect"], str)
            assert len(rule["effect"]) > 20

    def test_houses_in_order(self, double_transit_rules):
        houses = [r["house"] for r in double_transit_rules["rules"]]
        assert houses == list(range(1, 13))

    def test_duration_note_present(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            assert isinstance(rule["duration_note"], str)
            assert len(rule["duration_note"]) > 10

    def test_strength_factors_are_strings(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            for key, value in rule["strength_factors"].items():
                assert isinstance(
                    value, str
                ), f"House {rule['house']} strength_factor '{key}' is not a string"
                assert len(value) > 10

    def test_themes_are_strings(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            for theme in rule["themes"]:
                assert isinstance(theme, str)
                assert len(theme) > 0

    def test_typical_events_are_strings(self, double_transit_rules):
        for rule in double_transit_rules["rules"]:
            for event in rule["typical_events"]:
                assert isinstance(event, str)
                assert len(event) > 0


class TestTransitLordshipRules:
    def test_has_description(self, transit_lordship_rules):
        assert "description" in transit_lordship_rules

    def test_functional_nature_rules_present(self, transit_lordship_rules):
        assert "functional_nature_rules" in transit_lordship_rules
        assert len(transit_lordship_rules["functional_nature_rules"]) == 5

    def test_all_natures_covered(self, transit_lordship_rules):
        natures = {r["nature"] for r in transit_lordship_rules["functional_nature_rules"]}
        expected = {"yogakaraka", "benefic", "neutral", "malefic", "maraka"}
        assert natures == expected

    def test_nature_fields_complete(self, transit_lordship_rules):
        required = {"nature", "description", "transit_boost", "interpretation", "examples"}
        for rule in transit_lordship_rules["functional_nature_rules"]:
            assert required.issubset(rule.keys())

    def test_transit_boost_range(self, transit_lordship_rules):
        for rule in transit_lordship_rules["functional_nature_rules"]:
            assert 0.5 <= rule["transit_boost"] <= 2.0

    def test_lord_transit_house_rules_present(self, transit_lordship_rules):
        assert "lord_transit_house_rules" in transit_lordship_rules
        assert len(transit_lordship_rules["lord_transit_house_rules"]) == 5

    def test_lord_transit_conditions(self, transit_lordship_rules):
        conditions = {r["condition"] for r in transit_lordship_rules["lord_transit_house_rules"]}
        expected = {"own_house", "exaltation", "debilitation", "friend_sign", "enemy_sign"}
        assert conditions == expected

    def test_score_modifier_present(self, transit_lordship_rules):
        for rule in transit_lordship_rules["lord_transit_house_rules"]:
            assert "score_modifier" in rule
            assert isinstance(rule["score_modifier"], int | float)

    def test_score_modifier_range(self, transit_lordship_rules):
        for rule in transit_lordship_rules["lord_transit_house_rules"]:
            assert -25 <= rule["score_modifier"] <= 25

    def test_special_transit_rules_present(self, transit_lordship_rules):
        assert "special_transit_rules" in transit_lordship_rules
        assert len(transit_lordship_rules["special_transit_rules"]) == 4

    def test_special_conditions(self, transit_lordship_rules):
        conditions = {r["condition"] for r in transit_lordship_rules["special_transit_rules"]}
        expected = {"retrograde", "combust", "with_benefic", "with_malefic"}
        assert conditions == expected

    def test_special_rules_fields(self, transit_lordship_rules):
        required = {
            "condition",
            "description",
            "score_modifier",
            "interpretation",
            "additional_notes",
        }
        for rule in transit_lordship_rules["special_transit_rules"]:
            assert required.issubset(rule.keys())

    def test_all_interpretations_nonempty(self, transit_lordship_rules):
        for rule in transit_lordship_rules["functional_nature_rules"]:
            assert len(rule["interpretation"]) > 10
        for rule in transit_lordship_rules["lord_transit_house_rules"]:
            assert len(rule["interpretation"]) > 10
        for rule in transit_lordship_rules["special_transit_rules"]:
            assert len(rule["interpretation"]) > 10

    def test_examples_are_lists(self, transit_lordship_rules):
        for rule in transit_lordship_rules["functional_nature_rules"]:
            assert isinstance(rule["examples"], list)
            assert len(rule["examples"]) >= 2

    def test_additional_notes_nonempty(self, transit_lordship_rules):
        for rule in transit_lordship_rules["special_transit_rules"]:
            assert isinstance(rule["additional_notes"], str)
            assert len(rule["additional_notes"]) > 10

    def test_lagna_specific_lords_present(self, transit_lordship_rules):
        assert "lagna_specific_lords" in transit_lordship_rules
        lords = transit_lordship_rules["lagna_specific_lords"]
        assert "description" in lords
        expected_lagnas = {
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
        }
        actual_lagnas = {k for k in lords if k != "description"}
        assert actual_lagnas == expected_lagnas

    def test_lagna_lords_have_all_categories(self, transit_lordship_rules):
        lords = transit_lordship_rules["lagna_specific_lords"]
        required_categories = {"yogakaraka", "benefic", "neutral", "malefic", "maraka"}
        for lagna in lords:
            if lagna == "description":
                continue
            assert required_categories.issubset(lords[lagna].keys()), f"{lagna} missing categories"

    def test_transit_boost_ordering(self, transit_lordship_rules):
        rules = transit_lordship_rules["functional_nature_rules"]
        boosts = {r["nature"]: r["transit_boost"] for r in rules}
        assert boosts["yogakaraka"] > boosts["benefic"]
        assert boosts["benefic"] > boosts["neutral"]
        assert boosts["neutral"] > boosts["maraka"]
        assert boosts["maraka"] > boosts["malefic"]

    def test_score_modifier_signs(self, transit_lordship_rules):
        rules = transit_lordship_rules["lord_transit_house_rules"]
        modifiers = {r["condition"]: r["score_modifier"] for r in rules}
        assert modifiers["exaltation"] > 0
        assert modifiers["own_house"] > 0
        assert modifiers["friend_sign"] > 0
        assert modifiers["debilitation"] < 0
        assert modifiers["enemy_sign"] < 0
