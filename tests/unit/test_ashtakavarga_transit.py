"""Tests for ashtakavarga transit prediction rules JSON file."""

import json
from pathlib import Path

import pytest

RULES_PATH = (
    Path(__file__).parent.parent.parent / "knowledge" / "rules" / "ashtakavarga_transit_rules.json"
)

BAV_PLANETS = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]


@pytest.fixture(scope="module")
def transit_data():
    """Load ashtakavarga transit rules data."""
    with RULES_PATH.open(encoding="utf-8") as f:
        return json.load(f)["ashtakavarga_transit_rules"]


class TestAshtakavargaTransitJSON:
    """Test that the JSON file is valid and well-structured."""

    def test_json_loads_successfully(self, transit_data):
        assert isinstance(transit_data, dict)

    def test_has_all_required_sections(self, transit_data):
        assert "sav_thresholds" in transit_data
        assert "bav_interpretations" in transit_data
        assert "transit_modifiers" in transit_data
        assert "kaksha_effects" in transit_data


class TestSAVThresholds:
    """Tests for Sarvashtakavarga score thresholds."""

    def test_has_5_threshold_ranges(self, transit_data):
        thresholds = transit_data["sav_thresholds"]
        assert len(thresholds) == 5

    def test_thresholds_cover_0_to_56(self, transit_data):
        thresholds = transit_data["sav_thresholds"]
        # First should start at 0
        assert thresholds[0]["min_bindus"] == 0
        # Last should go up to 56
        assert thresholds[-1]["max_bindus"] == 56

    def test_thresholds_have_required_fields(self, transit_data):
        for threshold in transit_data["sav_thresholds"]:
            assert "type" in threshold
            assert "min_bindus" in threshold
            assert "max_bindus" in threshold
            assert "quality" in threshold
            assert "interpretation" in threshold
            assert threshold["type"] == "sav_threshold"

    def test_quality_values_are_valid(self, transit_data):
        valid = {"very_unfavorable", "unfavorable", "neutral", "favorable", "very_favorable"}
        for threshold in transit_data["sav_thresholds"]:
            assert threshold["quality"] in valid

    def test_no_gaps_in_ranges(self, transit_data):
        thresholds = transit_data["sav_thresholds"]
        for i in range(1, len(thresholds)):
            assert thresholds[i]["min_bindus"] == thresholds[i - 1]["max_bindus"] + 1


class TestBAVInterpretations:
    """Tests for Bhinnashtakavarga planet interpretations."""

    def test_has_all_7_planets(self, transit_data):
        bav = transit_data["bav_interpretations"]
        for planet in BAV_PLANETS:
            assert planet in bav, f"Missing planet {planet} in BAV"

    def test_each_planet_has_8_score_ranges(self, transit_data):
        bav = transit_data["bav_interpretations"]
        for planet in BAV_PLANETS:
            assert len(bav[planet]) == 8, f"Expected 8 ranges for {planet}, got {len(bav[planet])}"

    def test_score_ranges_cover_0_to_8(self, transit_data):
        bav = transit_data["bav_interpretations"]
        for planet in BAV_PLANETS:
            ranges = bav[planet]
            assert ranges[0]["min_bindus"] == 0
            assert ranges[-1]["max_bindus"] == 8

    def test_entries_have_required_fields(self, transit_data):
        bav = transit_data["bav_interpretations"]
        for planet in BAV_PLANETS:
            for entry in bav[planet]:
                assert "min_bindus" in entry
                assert "max_bindus" in entry
                assert "quality" in entry
                assert "interpretation" in entry
                assert len(entry["interpretation"]) > 20

    def test_total_bav_rules(self, transit_data):
        bav = transit_data["bav_interpretations"]
        total = sum(len(entries) for entries in bav.values())
        assert total == 56, f"Expected 56 BAV rules, got {total}"


class TestTransitModifiers:
    """Tests for transit condition modifiers."""

    def test_has_modifiers(self, transit_data):
        modifiers = transit_data["transit_modifiers"]
        assert len(modifiers) >= 5

    def test_modifiers_have_required_fields(self, transit_data):
        for mod in transit_data["transit_modifiers"]:
            assert "type" in mod
            assert "condition" in mod
            assert "modifier" in mod
            assert "description" in mod
            assert isinstance(mod["modifier"], int | float)

    def test_modifier_values_reasonable(self, transit_data):
        for mod in transit_data["transit_modifiers"]:
            assert 0.0 < mod["modifier"] < 2.0, f"Modifier {mod['modifier']} out of range"


class TestKakshaEffects:
    """Tests for Kaksha (8 divisions per sign) effects."""

    def test_has_8_kakshas(self, transit_data):
        kakshas = transit_data["kaksha_effects"]
        assert len(kakshas) == 8

    def test_kakshas_have_required_fields(self, transit_data):
        for kaksha in transit_data["kaksha_effects"]:
            assert "type" in kaksha
            assert "division" in kaksha
            assert "ruler" in kaksha
            assert "degrees" in kaksha
            assert "effect" in kaksha
            assert "nature" in kaksha

    def test_kakshas_are_numbered_1_to_8(self, transit_data):
        kakshas = transit_data["kaksha_effects"]
        divisions = [k["division"] for k in kakshas]
        assert divisions == list(range(1, 9))


class TestTotalRuleCount:
    """Verify total rule count is approximately 100."""

    def test_total_rules_approximately_100(self, transit_data):
        total = 0
        total += len(transit_data["sav_thresholds"])  # 5
        total += sum(len(v) for v in transit_data["bav_interpretations"].values())  # 56
        total += len(transit_data["transit_modifiers"])  # 8
        total += len(transit_data["kaksha_effects"])  # 8
        total += len(transit_data.get("combined_analysis", {}).get("rules", []))  # 6
        assert total >= 80, f"Expected >= 80 total rules, got {total}"
