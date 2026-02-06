"""Tests for divisional chart interpretation rules (D2/D4/D7/D24) in knowledge base."""

import json
from pathlib import Path

import pytest

RULES_PATH = (
    Path(__file__).parent.parent.parent / "knowledge" / "rules" / "divisional_interpretation.json"
)

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
def div_data():
    """Load divisional interpretation data once for all tests."""
    with RULES_PATH.open(encoding="utf-8") as f:
        return json.load(f)["divisional_interpretation"]


class TestDivisionalInterpretationJSON:
    """Test that the JSON file is valid and well-structured."""

    def test_json_loads_successfully(self, div_data):
        assert isinstance(div_data, dict)
        assert "d9_navamsha" in div_data
        assert "d10_dashamsha" in div_data

    def test_has_d2_hora_section(self, div_data):
        assert "d2_hora" in div_data
        d2 = div_data["d2_hora"]
        assert "planet_in_signs" in d2

    def test_has_d4_chaturthamsha_section(self, div_data):
        assert "d4_chaturthamsha" in div_data
        d4 = div_data["d4_chaturthamsha"]
        assert "planet_in_signs" in d4

    def test_has_d7_saptamsha_section(self, div_data):
        assert "d7_saptamsha" in div_data
        d7 = div_data["d7_saptamsha"]
        assert "planet_in_signs" in d7

    def test_has_d24_chaturvimshamsha_section(self, div_data):
        assert "d24_chaturvimshamsha" in div_data
        d24 = div_data["d24_chaturvimshamsha"]
        assert "planet_in_signs" in d24


class TestD2HoraRules:
    """Tests for D2 Hora chart interpretation rules."""

    def test_d2_has_all_9_planets(self, div_data):
        d2 = div_data["d2_hora"]["planet_in_signs"]
        for planet in PLANETS:
            assert planet in d2, f"Missing planet {planet} in D2 hora"

    def test_d2_each_planet_has_cancer_and_leo(self, div_data):
        d2 = div_data["d2_hora"]["planet_in_signs"]
        for planet in PLANETS:
            assert "cancer" in d2[planet], f"Missing cancer for {planet} in D2"
            assert "leo" in d2[planet], f"Missing leo for {planet} in D2"

    def test_d2_entries_have_required_fields(self, div_data):
        d2 = div_data["d2_hora"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in ["cancer", "leo"]:
                entry = d2[planet][sign]
                assert "theme" in entry, f"Missing theme for {planet}/{sign} in D2"
                assert "significance" in entry, f"Missing significance for {planet}/{sign} in D2"
                assert "strength" in entry, f"Missing strength for {planet}/{sign} in D2"

    def test_d2_total_rules_count(self, div_data):
        d2 = div_data["d2_hora"]["planet_in_signs"]
        count = sum(len(signs) for signs in d2.values())
        assert count == 18, f"Expected 18 D2 rules, got {count}"


class TestD4ChaturthamshaPlanetInSigns:
    """Tests for D4 Chaturthamsha planet_in_signs rules (108 combos)."""

    def test_d4_has_all_9_planets(self, div_data):
        d4 = div_data["d4_chaturthamsha"]["planet_in_signs"]
        for planet in PLANETS:
            assert planet in d4, f"Missing planet {planet} in D4"

    def test_d4_each_planet_has_12_signs(self, div_data):
        d4 = div_data["d4_chaturthamsha"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in SIGNS:
                assert sign in d4[planet], f"Missing {sign} for {planet} in D4"

    def test_d4_entries_have_required_fields(self, div_data):
        d4 = div_data["d4_chaturthamsha"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in SIGNS:
                entry = d4[planet][sign]
                assert "interpretation" in entry, f"Missing interpretation for {planet}/{sign}"
                assert "strength" in entry, f"Missing strength for {planet}/{sign}"
                assert "keywords" in entry, f"Missing keywords for {planet}/{sign}"
                assert isinstance(entry["keywords"], list)
                assert entry["strength"] in ("strong", "moderate", "weak")

    def test_d4_total_108_rules(self, div_data):
        d4 = div_data["d4_chaturthamsha"]["planet_in_signs"]
        count = sum(len(signs) for signs in d4.values())
        assert count == 108, f"Expected 108 D4 rules, got {count}"

    def test_d4_property_keywords(self, div_data):
        """Ensure D4 rules contain property-related keywords."""
        d4 = div_data["d4_chaturthamsha"]["planet_in_signs"]
        # Check a sample
        sun_aries = d4["sun"]["aries"]
        assert "property" in sun_aries["keywords"]


class TestD7SaptamshaPlanetInSigns:
    """Tests for D7 Saptamsha planet_in_signs rules (108 combos)."""

    def test_d7_has_all_9_planets(self, div_data):
        d7 = div_data["d7_saptamsha"]["planet_in_signs"]
        for planet in PLANETS:
            assert planet in d7, f"Missing planet {planet} in D7"

    def test_d7_each_planet_has_12_signs(self, div_data):
        d7 = div_data["d7_saptamsha"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in SIGNS:
                assert sign in d7[planet], f"Missing {sign} for {planet} in D7"

    def test_d7_entries_have_required_fields(self, div_data):
        d7 = div_data["d7_saptamsha"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in SIGNS:
                entry = d7[planet][sign]
                assert "interpretation" in entry
                assert "strength" in entry
                assert "keywords" in entry
                assert isinstance(entry["keywords"], list)
                assert entry["strength"] in ("strong", "moderate", "weak")

    def test_d7_total_108_rules(self, div_data):
        d7 = div_data["d7_saptamsha"]["planet_in_signs"]
        count = sum(len(signs) for signs in d7.values())
        assert count == 108, f"Expected 108 D7 rules, got {count}"

    def test_d7_children_keywords(self, div_data):
        """Ensure D7 rules contain children-related keywords."""
        d7 = div_data["d7_saptamsha"]["planet_in_signs"]
        sun_aries = d7["sun"]["aries"]
        assert "children" in sun_aries["keywords"]


class TestD24ChaturvimsamshaPlanetInSigns:
    """Tests for D24 Chaturvimshamsha planet_in_signs rules (108 combos)."""

    def test_d24_has_all_9_planets(self, div_data):
        d24 = div_data["d24_chaturvimshamsha"]["planet_in_signs"]
        for planet in PLANETS:
            assert planet in d24, f"Missing planet {planet} in D24"

    def test_d24_each_planet_has_12_signs(self, div_data):
        d24 = div_data["d24_chaturvimshamsha"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in SIGNS:
                assert sign in d24[planet], f"Missing {sign} for {planet} in D24"

    def test_d24_entries_have_required_fields(self, div_data):
        d24 = div_data["d24_chaturvimshamsha"]["planet_in_signs"]
        for planet in PLANETS:
            for sign in SIGNS:
                entry = d24[planet][sign]
                assert "interpretation" in entry
                assert "strength" in entry
                assert "keywords" in entry
                assert isinstance(entry["keywords"], list)
                assert entry["strength"] in ("strong", "moderate", "weak")

    def test_d24_total_108_rules(self, div_data):
        d24 = div_data["d24_chaturvimshamsha"]["planet_in_signs"]
        count = sum(len(signs) for signs in d24.values())
        assert count == 108, f"Expected 108 D24 rules, got {count}"

    def test_d24_education_keywords(self, div_data):
        """Ensure D24 rules contain education-related keywords."""
        d24 = div_data["d24_chaturvimshamsha"]["planet_in_signs"]
        sun_aries = d24["sun"]["aries"]
        assert "education" in sun_aries["keywords"]


class TestTotalDivisionalRuleCount:
    """Verify total rule counts across all chart types."""

    def test_total_new_rules_at_least_342(self, div_data):
        """D2 (18) + D4 (108) + D7 (108) + D24 (108) = 342 new rules."""
        d2_count = sum(len(signs) for signs in div_data["d2_hora"]["planet_in_signs"].values())
        d4_count = sum(
            len(signs) for signs in div_data["d4_chaturthamsha"]["planet_in_signs"].values()
        )
        d7_count = sum(len(signs) for signs in div_data["d7_saptamsha"]["planet_in_signs"].values())
        d24_count = sum(
            len(signs) for signs in div_data["d24_chaturvimshamsha"]["planet_in_signs"].values()
        )
        total = d2_count + d4_count + d7_count + d24_count
        assert total >= 342, f"Expected >= 342 rules, got {total}"

    def test_strength_values_are_valid(self, div_data):
        """Verify all strength values are from allowed set."""
        valid_strengths = {
            "strong",
            "moderate",
            "weak",
            "exalted",
            "debilitated",
            "own_sign",
            "friendly",
            "neutral",
        }
        for chart_key in ["d4_chaturthamsha", "d7_saptamsha", "d24_chaturvimshamsha"]:
            chart = div_data[chart_key]["planet_in_signs"]
            for planet, signs in chart.items():
                for sign, entry in signs.items():
                    strength = entry.get("strength", "")
                    assert (
                        strength in valid_strengths
                    ), f"Invalid strength '{strength}' for {planet}/{sign} in {chart_key}"
