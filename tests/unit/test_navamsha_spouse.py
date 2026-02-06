"""Tests for navamsha spouse prediction rules JSON file."""

import json
from pathlib import Path

import pytest

RULES_PATH = (
    Path(__file__).parent.parent.parent / "knowledge" / "rules" / "navamsha_spouse_rules.json"
)

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
def spouse_data():
    """Load navamsha spouse rules data."""
    with RULES_PATH.open(encoding="utf-8") as f:
        return json.load(f)["navamsha_spouse_rules"]


class TestNavamshaSpouseJSON:
    """Test that the JSON file is valid and well-structured."""

    def test_json_loads_successfully(self, spouse_data):
        assert isinstance(spouse_data, dict)

    def test_has_all_required_sections(self, spouse_data):
        assert "d9_7th_lord_in_sign" in spouse_data
        assert "venus_in_d9_sign" in spouse_data
        assert "jupiter_in_d9_sign" in spouse_data
        assert "d9_lagna_in_sign" in spouse_data
        assert "planet_in_d9_7th" in spouse_data
        assert "upapada_cross_reference" in spouse_data
        assert "planet_combinations_in_d9_7th" in spouse_data


class TestD9SeventhLordInSign:
    """Tests for 7th lord of D9 in 12 signs (12 rules)."""

    def test_has_12_rules(self, spouse_data):
        rules = spouse_data["d9_7th_lord_in_sign"]
        assert len(rules) == 12

    def test_covers_all_12_signs(self, spouse_data):
        rules = spouse_data["d9_7th_lord_in_sign"]
        signs_covered = {r["sign"] for r in rules}
        assert signs_covered == set(SIGNS)

    def test_each_rule_has_required_fields(self, spouse_data):
        for rule in spouse_data["d9_7th_lord_in_sign"]:
            assert "category" in rule
            assert "sign" in rule
            assert "interpretation" in rule
            assert "keywords" in rule
            assert rule["category"] == "d9_7th_lord_sign"
            assert len(rule["interpretation"]) > 20


class TestVenusInD9Sign:
    """Tests for Venus in D9 signs (12 rules for male charts)."""

    def test_has_12_rules(self, spouse_data):
        rules = spouse_data["venus_in_d9_sign"]
        assert len(rules) == 12

    def test_covers_all_12_signs(self, spouse_data):
        rules = spouse_data["venus_in_d9_sign"]
        signs_covered = {r["sign"] for r in rules}
        assert signs_covered == set(SIGNS)

    def test_all_for_male_chart(self, spouse_data):
        for rule in spouse_data["venus_in_d9_sign"]:
            assert rule["applicable_for"] == "male_chart"
            assert rule["planet"] == "venus"


class TestJupiterInD9Sign:
    """Tests for Jupiter in D9 signs (12 rules for female charts)."""

    def test_has_12_rules(self, spouse_data):
        rules = spouse_data["jupiter_in_d9_sign"]
        assert len(rules) == 12

    def test_covers_all_12_signs(self, spouse_data):
        rules = spouse_data["jupiter_in_d9_sign"]
        signs_covered = {r["sign"] for r in rules}
        assert signs_covered == set(SIGNS)

    def test_all_for_female_chart(self, spouse_data):
        for rule in spouse_data["jupiter_in_d9_sign"]:
            assert rule["applicable_for"] == "female_chart"
            assert rule["planet"] == "jupiter"


class TestD9LagnaInSign:
    """Tests for D9 Lagna in 12 signs (12 rules)."""

    def test_has_12_rules(self, spouse_data):
        rules = spouse_data["d9_lagna_in_sign"]
        assert len(rules) == 12

    def test_covers_all_12_signs(self, spouse_data):
        rules = spouse_data["d9_lagna_in_sign"]
        signs_covered = {r["sign"] for r in rules}
        assert signs_covered == set(SIGNS)

    def test_each_rule_has_marriage_quality(self, spouse_data):
        for rule in spouse_data["d9_lagna_in_sign"]:
            assert "marriage_quality" in rule
            assert len(rule["marriage_quality"]) > 5


class TestPlanetInD9Seventh:
    """Tests for planets in 7th house of D9 (9 rules)."""

    def test_has_9_rules(self, spouse_data):
        rules = spouse_data["planet_in_d9_7th"]
        assert len(rules) == 9

    def test_covers_all_9_planets(self, spouse_data):
        rules = spouse_data["planet_in_d9_7th"]
        planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
        planets_covered = {r["planet"] for r in rules}
        assert planets_covered == set(planets)

    def test_each_rule_has_spouse_characteristics(self, spouse_data):
        for rule in spouse_data["planet_in_d9_7th"]:
            assert "spouse_characteristics" in rule


class TestUpapadaCrossReference:
    """Tests for Upapada cross-reference rules (12 rules)."""

    def test_has_12_rules(self, spouse_data):
        rules = spouse_data["upapada_cross_reference"]
        assert len(rules) == 12

    def test_covers_all_12_signs(self, spouse_data):
        rules = spouse_data["upapada_cross_reference"]
        signs_covered = {r["sign"] for r in rules}
        assert signs_covered == set(SIGNS)


class TestPlanetCombinationsInD9Seventh:
    """Tests for planet-in-sign combinations in D9 7th house."""

    def test_has_many_rules(self, spouse_data):
        rules = spouse_data["planet_combinations_in_d9_7th"]
        # Should have combos for sun(12) + moon(12) + venus(12) + jupiter(12) + mars(12) + saturn(12) + mercury(12) = 84
        assert len(rules) >= 84

    def test_each_rule_has_required_fields(self, spouse_data):
        for rule in spouse_data["planet_combinations_in_d9_7th"]:
            assert "category" in rule
            assert "planet" in rule
            assert "sign" in rule
            assert "interpretation" in rule
            assert "strength" in rule
            assert "keywords" in rule
            assert rule["strength"] in ("strong", "moderate", "weak")


class TestTotalRuleCount:
    """Verify the total number of rules."""

    def test_total_rules_approximately_141(self, spouse_data):
        total = 0
        total += len(spouse_data["d9_7th_lord_in_sign"])  # 12
        total += len(spouse_data["venus_in_d9_sign"])  # 12
        total += len(spouse_data["jupiter_in_d9_sign"])  # 12
        total += len(spouse_data["d9_lagna_in_sign"])  # 12
        total += len(spouse_data["planet_in_d9_7th"])  # 9
        total += len(spouse_data["upapada_cross_reference"])  # 12
        total += len(spouse_data["planet_combinations_in_d9_7th"])  # 84+
        assert total >= 141, f"Expected >= 141 total rules, got {total}"
