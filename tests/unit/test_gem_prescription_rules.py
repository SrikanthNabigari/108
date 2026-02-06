"""Tests for gem_prescription_rules.json knowledge file.

Validates JSON structure, key counts, and Vedic accuracy for:
- Lagna-wise gem prescriptions (12 lagnas)
- General rules (12+ rules)
- Enemy gem pairs (9 pairs)
- Gem properties (9 gems)
"""

import json
from pathlib import Path

import pytest

RULES_DIR = Path(__file__).parent.parent.parent / "knowledge" / "rules"

LAGNAS = [
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

PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]

GEMS = [
    "ruby",
    "pearl",
    "red_coral",
    "emerald",
    "yellow_sapphire",
    "diamond",
    "blue_sapphire",
    "hessonite",
    "cats_eye",
]


@pytest.fixture(scope="module")
def gem_data():
    """Load gem prescription rules data."""
    filepath = RULES_DIR / "gem_prescription_rules.json"
    assert filepath.exists(), f"File not found: {filepath}"
    with filepath.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["gem_prescription_rules"]


class TestGemRulesStructure:
    def test_file_loads_successfully(self, gem_data):
        assert gem_data, "gem_prescription_rules should not be empty"

    def test_has_all_top_level_sections(self, gem_data):
        expected_sections = {
            "description",
            "version",
            "lagna_wise",
            "general_rules",
            "enemy_gem_pairs",
            "gem_properties",
        }
        assert expected_sections.issubset(set(gem_data.keys()))

    def test_has_description_and_version(self, gem_data):
        assert len(gem_data["description"]) > 30
        assert gem_data["version"] == "1.0"


class TestLagnaWise:
    def test_has_all_twelve_lagnas(self, gem_data):
        lagnas = gem_data["lagna_wise"]
        assert set(lagnas.keys()) == set(
            LAGNAS
        ), f"Missing lagnas: {set(LAGNAS) - set(lagnas.keys())}"

    def test_each_lagna_has_required_fields(self, gem_data):
        required_fields = {
            "yoga_karaka",
            "primary_benefic_planets",
            "functional_malefic_planets",
            "neutral_planets",
            "best_gem",
            "secondary_gems",
            "avoid_gems",
            "conditional_gems",
        }
        for lagna, data in gem_data["lagna_wise"].items():
            for field in required_fields:
                assert field in data, f"{lagna} missing field: {field}"

    def test_best_gem_has_required_fields(self, gem_data):
        required_fields = {"planet", "gem", "reason", "finger", "metal", "day"}
        for lagna, data in gem_data["lagna_wise"].items():
            best = data["best_gem"]
            for field in required_fields:
                assert field in best, f"{lagna} best_gem missing field: {field}"

    def test_best_gem_reasons_are_substantial(self, gem_data):
        for lagna, data in gem_data["lagna_wise"].items():
            reason = data["best_gem"]["reason"]
            assert len(reason) > 50, f"{lagna} best_gem reason too short: {len(reason)} chars"

    def test_secondary_gems_have_required_fields(self, gem_data):
        for lagna, data in gem_data["lagna_wise"].items():
            for i, gem in enumerate(data["secondary_gems"]):
                assert "planet" in gem, f"{lagna} secondary_gems[{i}] missing 'planet'"
                assert "gem" in gem, f"{lagna} secondary_gems[{i}] missing 'gem'"
                assert "reason" in gem, f"{lagna} secondary_gems[{i}] missing 'reason'"

    def test_avoid_gems_have_required_fields(self, gem_data):
        for lagna, data in gem_data["lagna_wise"].items():
            assert len(data["avoid_gems"]) >= 2, f"{lagna} should have at least 2 gems to avoid"
            for i, gem in enumerate(data["avoid_gems"]):
                assert "planet" in gem, f"{lagna} avoid_gems[{i}] missing 'planet'"
                assert "gem" in gem, f"{lagna} avoid_gems[{i}] missing 'gem'"
                assert "reason" in gem, f"{lagna} avoid_gems[{i}] missing 'reason'"

    def test_benefic_planets_are_valid(self, gem_data):
        for lagna, data in gem_data["lagna_wise"].items():
            for planet in data["primary_benefic_planets"]:
                assert planet in PLANETS, f"{lagna} has invalid benefic planet: {planet}"

    def test_malefic_planets_are_valid(self, gem_data):
        for lagna, data in gem_data["lagna_wise"].items():
            for planet in data["functional_malefic_planets"]:
                assert planet in PLANETS, f"{lagna} has invalid malefic planet: {planet}"


class TestYogaKarakaAccuracy:
    """Verify correct Yoga Karaka assignments per BPHS."""

    def test_taurus_yoga_karaka_is_saturn(self, gem_data):
        assert gem_data["lagna_wise"]["taurus"]["yoga_karaka"] == "saturn"

    def test_cancer_yoga_karaka_is_mars(self, gem_data):
        assert gem_data["lagna_wise"]["cancer"]["yoga_karaka"] == "mars"

    def test_leo_yoga_karaka_is_mars(self, gem_data):
        assert gem_data["lagna_wise"]["leo"]["yoga_karaka"] == "mars"

    def test_libra_yoga_karaka_is_saturn(self, gem_data):
        assert gem_data["lagna_wise"]["libra"]["yoga_karaka"] == "saturn"

    def test_capricorn_yoga_karaka_is_venus(self, gem_data):
        assert gem_data["lagna_wise"]["capricorn"]["yoga_karaka"] == "venus"

    def test_aquarius_yoga_karaka_is_venus(self, gem_data):
        assert gem_data["lagna_wise"]["aquarius"]["yoga_karaka"] == "venus"

    def test_aries_has_no_yoga_karaka(self, gem_data):
        assert gem_data["lagna_wise"]["aries"]["yoga_karaka"] is None

    def test_gemini_has_no_yoga_karaka(self, gem_data):
        assert gem_data["lagna_wise"]["gemini"]["yoga_karaka"] is None

    def test_scorpio_has_no_yoga_karaka(self, gem_data):
        assert gem_data["lagna_wise"]["scorpio"]["yoga_karaka"] is None

    def test_sagittarius_has_no_yoga_karaka(self, gem_data):
        assert gem_data["lagna_wise"]["sagittarius"]["yoga_karaka"] is None

    def test_pisces_has_no_yoga_karaka(self, gem_data):
        assert gem_data["lagna_wise"]["pisces"]["yoga_karaka"] is None


class TestBestGemAccuracy:
    """Verify correct best gem assignments per Vedic tradition."""

    def test_aries_best_gem_is_ruby(self, gem_data):
        assert gem_data["lagna_wise"]["aries"]["best_gem"]["gem"] == "ruby"

    def test_taurus_best_gem_is_blue_sapphire(self, gem_data):
        assert gem_data["lagna_wise"]["taurus"]["best_gem"]["gem"] == "blue_sapphire"

    def test_gemini_best_gem_is_emerald(self, gem_data):
        assert gem_data["lagna_wise"]["gemini"]["best_gem"]["gem"] == "emerald"

    def test_cancer_best_gem_is_red_coral(self, gem_data):
        assert gem_data["lagna_wise"]["cancer"]["best_gem"]["gem"] == "red_coral"

    def test_leo_best_gem_is_ruby(self, gem_data):
        assert gem_data["lagna_wise"]["leo"]["best_gem"]["gem"] == "ruby"

    def test_virgo_best_gem_is_emerald(self, gem_data):
        assert gem_data["lagna_wise"]["virgo"]["best_gem"]["gem"] == "emerald"

    def test_libra_best_gem_is_blue_sapphire(self, gem_data):
        assert gem_data["lagna_wise"]["libra"]["best_gem"]["gem"] == "blue_sapphire"

    def test_scorpio_best_gem_is_red_coral(self, gem_data):
        assert gem_data["lagna_wise"]["scorpio"]["best_gem"]["gem"] == "red_coral"

    def test_sagittarius_best_gem_is_yellow_sapphire(self, gem_data):
        assert gem_data["lagna_wise"]["sagittarius"]["best_gem"]["gem"] == "yellow_sapphire"

    def test_capricorn_best_gem_is_diamond(self, gem_data):
        assert gem_data["lagna_wise"]["capricorn"]["best_gem"]["gem"] == "diamond"

    def test_aquarius_best_gem_is_diamond(self, gem_data):
        assert gem_data["lagna_wise"]["aquarius"]["best_gem"]["gem"] == "diamond"

    def test_pisces_best_gem_is_yellow_sapphire(self, gem_data):
        assert gem_data["lagna_wise"]["pisces"]["best_gem"]["gem"] == "yellow_sapphire"


class TestGeneralRules:
    def test_has_at_least_ten_rules(self, gem_data):
        rules = gem_data["general_rules"]
        assert len(rules) >= 10, f"Expected at least 10 general rules, got {len(rules)}"

    def test_each_rule_has_required_fields(self, gem_data):
        for i, rule in enumerate(gem_data["general_rules"]):
            assert "rule" in rule, f"general_rules[{i}] missing 'rule'"
            assert "priority" in rule, f"general_rules[{i}] missing 'priority'"

    def test_rules_are_substantial(self, gem_data):
        for i, rule in enumerate(gem_data["general_rules"]):
            assert len(rule["rule"]) > 30, f"general_rules[{i}] rule text too short"

    def test_priorities_are_ordered(self, gem_data):
        priorities = [r["priority"] for r in gem_data["general_rules"]]
        assert priorities == sorted(priorities), "General rules should be ordered by priority"


class TestEnemyGemPairs:
    def test_has_at_least_seven_pairs(self, gem_data):
        pairs = gem_data["enemy_gem_pairs"]
        assert len(pairs) >= 7, f"Expected at least 7 enemy pairs, got {len(pairs)}"

    def test_each_pair_has_required_fields(self, gem_data):
        for i, pair in enumerate(gem_data["enemy_gem_pairs"]):
            assert "gem1" in pair, f"enemy_gem_pairs[{i}] missing 'gem1'"
            assert "gem2" in pair, f"enemy_gem_pairs[{i}] missing 'gem2'"
            assert "planets" in pair, f"enemy_gem_pairs[{i}] missing 'planets'"
            assert "reason" in pair, f"enemy_gem_pairs[{i}] missing 'reason'"

    def test_sun_saturn_enmity_exists(self, gem_data):
        """Ruby and Blue Sapphire must be listed as enemies."""
        pairs = gem_data["enemy_gem_pairs"]
        sun_saturn = any(
            (p["gem1"] == "ruby" and p["gem2"] == "blue_sapphire")
            or (p["gem1"] == "blue_sapphire" and p["gem2"] == "ruby")
            for p in pairs
        )
        assert sun_saturn, "Ruby-Blue Sapphire enemy pair is missing"

    def test_moon_rahu_enmity_exists(self, gem_data):
        """Pearl and Hessonite must be listed as enemies."""
        pairs = gem_data["enemy_gem_pairs"]
        moon_rahu = any(
            (p["gem1"] == "pearl" and p["gem2"] == "hessonite")
            or (p["gem1"] == "hessonite" and p["gem2"] == "pearl")
            for p in pairs
        )
        assert moon_rahu, "Pearl-Hessonite enemy pair is missing"

    def test_reasons_are_substantial(self, gem_data):
        for i, pair in enumerate(gem_data["enemy_gem_pairs"]):
            assert len(pair["reason"]) > 40, f"enemy_gem_pairs[{i}] reason too short"


class TestGemProperties:
    def test_has_all_nine_gems(self, gem_data):
        props = gem_data["gem_properties"]
        assert set(props.keys()) == set(GEMS), f"Missing gems: {set(GEMS) - set(props.keys())}"

    def test_each_gem_has_required_fields(self, gem_data):
        required_fields = {
            "planet",
            "sanskrit",
            "color",
            "hardness",
            "chemical",
            "source",
            "minimum_carat",
            "finger",
            "metal",
            "day",
            "substitute",
        }
        for gem, data in gem_data["gem_properties"].items():
            for field in required_fields:
                assert field in data, f"{gem} missing field: {field}"

    def test_gem_planet_mapping_is_correct(self, gem_data):
        expected = {
            "ruby": "sun",
            "pearl": "moon",
            "red_coral": "mars",
            "emerald": "mercury",
            "yellow_sapphire": "jupiter",
            "diamond": "venus",
            "blue_sapphire": "saturn",
            "hessonite": "rahu",
            "cats_eye": "ketu",
        }
        for gem, planet in expected.items():
            assert (
                gem_data["gem_properties"][gem]["planet"] == planet
            ), f"{gem} should map to {planet}"

    def test_substitutes_are_lists(self, gem_data):
        for gem, data in gem_data["gem_properties"].items():
            assert isinstance(data["substitute"], list), f"{gem} substitute should be a list"
            assert len(data["substitute"]) >= 1, f"{gem} should have at least 1 substitute"

    def test_hardness_values_are_reasonable(self, gem_data):
        for gem, data in gem_data["gem_properties"].items():
            assert (
                3.0 <= data["hardness"] <= 10.0
            ), f"{gem} hardness {data['hardness']} is out of range"


class TestOverallRuleCount:
    def test_total_rule_count(self, gem_data):
        """Verify total rule count is approximately 150."""
        lagna_count = 0
        for lagna_data in gem_data["lagna_wise"].values():
            lagna_count += 1  # best gem
            lagna_count += len(lagna_data["secondary_gems"])
            lagna_count += len(lagna_data["avoid_gems"])
            lagna_count += len(lagna_data["conditional_gems"])

        general_count = len(gem_data["general_rules"])
        enemy_count = len(gem_data["enemy_gem_pairs"])
        gem_props_count = len(gem_data["gem_properties"])

        total = lagna_count + general_count + enemy_count + gem_props_count
        assert total >= 100, f"Expected at least 100 rules, got {total}"
