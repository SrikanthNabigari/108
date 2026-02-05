"""Tests for new knowledge files and their loader functions.

Validates JSON structure, key counts, and loader integration for:
- combustion_rules.json
- retrograde_rules.json
- nakshatra_transit_rules.json
- varshaphal_rules.json
- divisional_interpretation.json
"""

from packages.core.src.knowledge_loader import (
    get_combustion_rules,
    get_divisional_interpretation,
    get_nakshatra_transit_rules,
    get_retrograde_rules,
    get_varshaphal_rules,
    load_rules,
)


class TestCombustionRules:
    def test_loads_successfully(self):
        data = get_combustion_rules()
        assert data, "combustion_rules should not be empty"

    def test_has_six_planets(self):
        data = get_combustion_rules()
        planets = data.get("planets", {})
        expected = {"moon", "mars", "mercury", "jupiter", "venus", "saturn"}
        assert set(planets.keys()) == expected

    def test_planet_has_degrees(self):
        data = get_combustion_rules()
        for planet_name, planet_data in data.get("planets", {}).items():
            assert "combustion_degree" in planet_data, f"{planet_name} missing combustion_degree"
            assert (
                "deep_combustion_degree" in planet_data
            ), f"{planet_name} missing deep_combustion_degree"
            assert planet_data["deep_combustion_degree"] < planet_data["combustion_degree"]

    def test_has_12_house_effects(self):
        data = get_combustion_rules()
        houses = data.get("house_wise_effects", {})
        assert len(houses) == 12, f"Expected 12 houses, got {len(houses)}"

    def test_has_special_rules(self):
        data = get_combustion_rules()
        assert "special_rules" in data

    def test_has_general_principles(self):
        data = get_combustion_rules()
        assert "general_principles" in data


class TestRetrogradeRules:
    def test_loads_successfully(self):
        data = get_retrograde_rules()
        assert data, "retrograde_rules should not be empty"

    def test_has_five_planets(self):
        data = get_retrograde_rules()
        planets = data.get("planets", {})
        expected = {"mars", "mercury", "jupiter", "venus", "saturn"}
        assert set(planets.keys()) == expected

    def test_planet_has_effects(self):
        data = get_retrograde_rules()
        for planet_name, planet_data in data.get("planets", {}).items():
            assert (
                "natal_effects" in planet_data or "effects" in planet_data
            ), f"{planet_name} missing effects"

    def test_has_special_rules(self):
        data = get_retrograde_rules()
        assert "special_rules" in data

    def test_has_interpretation_guidelines(self):
        data = get_retrograde_rules()
        assert "interpretation_guidelines" in data


class TestNakshatraTransitRules:
    def test_loads_successfully(self):
        data = get_nakshatra_transit_rules()
        assert data, "nakshatra_transit_rules should not be empty"

    def test_has_nine_planets(self):
        data = get_nakshatra_transit_rules()
        transits = data.get("transits", {})
        assert len(transits) == 9, f"Expected 9 planets, got {len(transits)}"
        expected = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}
        assert set(transits.keys()) == expected

    def test_each_planet_has_27_nakshatras(self):
        data = get_nakshatra_transit_rules()
        for planet_name, planet_data in data.get("transits", {}).items():
            # Nakshatras are keyed by name, not in a list
            nakshatra_count = len(planet_data)
            assert (
                nakshatra_count == 27
            ), f"{planet_name}: expected 27 nakshatras, got {nakshatra_count}"

    def test_total_243_combinations(self):
        data = get_nakshatra_transit_rules()
        total = sum(len(p) for p in data.get("transits", {}).values())
        assert total == 243, f"Expected 243 combinations (9x27), got {total}"

    def test_nakshatra_entry_has_required_fields(self):
        data = get_nakshatra_transit_rules()
        sun_transits = data.get("transits", {}).get("sun", {})
        first_nak = next(iter(sun_transits.values()))
        for field in ["theme", "positive", "negative"]:
            assert field in first_nak, f"Nakshatra entry missing '{field}'"

    def test_has_general_principles(self):
        data = get_nakshatra_transit_rules()
        assert "general_principles" in data


class TestVarshaphalRules:
    def test_loads_successfully(self):
        data = get_varshaphal_rules()
        assert data, "varshaphal_rules should not be empty"

    def test_has_12_muntha_houses(self):
        data = get_varshaphal_rules()
        muntha = data.get("muntha", {})
        houses = muntha.get("house_effects", [])
        assert len(houses) == 12, f"Muntha should have 12 houses, got {len(houses)}"

    def test_has_16_tajika_yogas(self):
        data = get_varshaphal_rules()
        yogas = data.get("tajika_yogas", {}).get("yogas", {})
        assert len(yogas) == 16, f"Expected 16 Tajika yogas, got {len(yogas)}"

    def test_has_9_varshesha_planets(self):
        data = get_varshaphal_rules()
        planets = data.get("varshesha", {}).get("year_lord_by_planet", {})
        assert len(planets) == 9, f"Varshesha should have 9 planets, got {len(planets)}"

    def test_has_10_sahams(self):
        data = get_varshaphal_rules()
        sahams = data.get("sahams", {}).get("points", [])
        assert len(sahams) == 10, f"Expected 10 Sahams, got {len(sahams)}"

    def test_has_5_pancha_vargiya_bala_components(self):
        data = get_varshaphal_rules()
        pvb = data.get("pancha_vargiya_bala", {})
        components = pvb.get("components", [])
        assert len(components) == 5, f"PVB should have 5 components, got {len(components)}"

    def test_tajika_yoga_has_structure(self):
        data = get_varshaphal_rules()
        yogas = data.get("tajika_yogas", {}).get("yogas", {})
        first = next(iter(yogas.values()))
        assert "name" in first
        assert "condition" in first or "description" in first


class TestDivisionalInterpretation:
    def test_loads_successfully(self):
        data = get_divisional_interpretation()
        assert data, "divisional_interpretation should not be empty"

    def test_has_d9_and_d10(self):
        data = get_divisional_interpretation()
        assert "d9_navamsha" in data, "Missing d9_navamsha"
        assert "d10_dashamsha" in data, "Missing d10_dashamsha"

    def test_d9_has_planet_in_signs(self):
        data = get_divisional_interpretation()
        d9 = data["d9_navamsha"]
        planets_in_signs = d9.get("planet_in_signs", {})
        assert (
            len(planets_in_signs) >= 9
        ), f"D9 should have entries for 9 planets, got {len(planets_in_signs)}"

    def test_d9_has_house_meanings(self):
        data = get_divisional_interpretation()
        d9 = data["d9_navamsha"]
        houses = d9.get("house_meanings", {})
        assert len(houses) >= 12, f"D9 should have 12 house meanings, got {len(houses)}"

    def test_d10_has_planet_in_signs(self):
        data = get_divisional_interpretation()
        d10 = data["d10_dashamsha"]
        planets_in_signs = d10.get("planet_in_signs", {})
        assert (
            len(planets_in_signs) >= 9
        ), f"D10 should have entries for 9 planets, got {len(planets_in_signs)}"

    def test_d10_has_house_meanings(self):
        data = get_divisional_interpretation()
        d10 = data["d10_dashamsha"]
        houses = d10.get("house_meanings", {})
        assert len(houses) >= 12, f"D10 should have 12 house meanings, got {len(houses)}"

    def test_d9_has_special_rules(self):
        data = get_divisional_interpretation()
        d9 = data["d9_navamsha"]
        assert "special_rules" in d9

    def test_d10_has_special_rules(self):
        data = get_divisional_interpretation()
        d10 = data["d10_dashamsha"]
        assert "special_rules" in d10


class TestLoaderIntegration:
    """Test that load_rules works for all new files."""

    def test_load_combustion_raw(self):
        raw = load_rules("combustion_rules")
        assert "combustion_rules" in raw

    def test_load_retrograde_raw(self):
        raw = load_rules("retrograde_rules")
        assert "retrograde_rules" in raw

    def test_load_nakshatra_transit_raw(self):
        raw = load_rules("nakshatra_transit_rules")
        assert "nakshatra_transit_rules" in raw

    def test_load_varshaphal_raw(self):
        raw = load_rules("varshaphal_rules")
        assert "varshaphal_rules" in raw

    def test_load_divisional_raw(self):
        raw = load_rules("divisional_interpretation")
        assert "divisional_interpretation" in raw
