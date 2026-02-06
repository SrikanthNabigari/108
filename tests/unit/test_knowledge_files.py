"""Tests for knowledge files and their loader functions.

Validates JSON structure, key counts, and loader integration for:
- combustion_rules.json
- retrograde_rules.json
- nakshatra_transit_rules.json
- varshaphal_rules.json
- divisional_interpretation.json
- tithis.json, karanas.json, nitya_yogas.json, varas.json, avasthas.json
- planet_in_house.json, planet_in_sign.json, planet_in_nakshatra.json
- house_lord_in_house.json, dasha_guide.json
"""

from packages.core.src.knowledge_loader import (
    get_avastha_definitions,
    get_combustion_rules,
    get_dasha_guide,
    get_divisional_interpretation,
    get_house_lord_in_house_interpretations,
    get_karana_definitions,
    get_nakshatra_transit_rules,
    get_nitya_yoga_definitions,
    get_planet_in_house_interpretations,
    get_planet_in_nakshatra_interpretations,
    get_planet_in_sign_interpretations,
    get_retrograde_rules,
    get_tithi_definitions,
    get_vara_definitions,
    get_varshaphal_rules,
    load_definition,
    load_interpretation,
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


# =============================================================================
# Panchanga Definition Tests
# =============================================================================


class TestTithiDefinitions:
    """Tests for knowledge/definitions/tithis.json."""

    def test_loads_successfully(self):
        data = get_tithi_definitions()
        assert data, "tithis should not be empty"

    def test_has_30_tithis(self):
        data = get_tithi_definitions()
        tithis = data.get("tithis", [])
        assert len(tithis) == 30, f"Expected 30 tithis, got {len(tithis)}"

    def test_15_shukla_and_15_krishna(self):
        data = get_tithi_definitions()
        tithis = data.get("tithis", [])
        shukla = [t for t in tithis if t["paksha"] == "shukla"]
        krishna = [t for t in tithis if t["paksha"] == "krishna"]
        assert len(shukla) == 15, f"Expected 15 Shukla tithis, got {len(shukla)}"
        assert len(krishna) == 15, f"Expected 15 Krishna tithis, got {len(krishna)}"

    def test_tithi_numbers_sequential(self):
        data = get_tithi_definitions()
        tithis = data.get("tithis", [])
        numbers = [t["number"] for t in tithis]
        assert numbers == list(range(1, 31))

    def test_tithi_has_required_fields(self):
        data = get_tithi_definitions()
        required = [
            "number",
            "name",
            "sanskrit",
            "paksha",
            "lord",
            "deity",
            "nature",
            "good_for",
            "avoid",
            "health_indication",
            "lunar_day_angle",
        ]
        for tithi in data.get("tithis", []):
            for field in required:
                assert field in tithi, f"Tithi {tithi['number']} missing '{field}'"

    def test_tithi_groups_present(self):
        data = get_tithi_definitions()
        groups = data.get("tithi_groups", {})
        expected_groups = {"nanda", "bhadra", "jaya", "rikta", "purna"}
        assert set(groups.keys()) == expected_groups

    def test_tithi_group_counts(self):
        data = get_tithi_definitions()
        groups = data.get("tithi_groups", {})
        for group_name, group_data in groups.items():
            tithis_list = group_data.get("tithis", [])
            assert len(tithis_list) == 3, f"Group {group_name} should have 3 tithis"

    def test_special_tithis_present(self):
        data = get_tithi_definitions()
        special = data.get("special_tithis", {})
        assert "purnima" in special
        assert "amavasya" in special
        assert "ekadashi" in special

    def test_has_calculation_info(self):
        data = get_tithi_definitions()
        calc = data.get("calculation", {})
        assert "formula" in calc
        assert calc.get("total_tithis") == 30

    def test_purnima_is_tithi_15_shukla(self):
        data = get_tithi_definitions()
        tithis = data.get("tithis", [])
        purnima = [t for t in tithis if t["name"] == "Purnima"]
        assert len(purnima) == 1
        assert purnima[0]["number"] == 15
        assert purnima[0]["paksha"] == "shukla"

    def test_amavasya_is_tithi_30_krishna(self):
        data = get_tithi_definitions()
        tithis = data.get("tithis", [])
        amavasya = [t for t in tithis if t["name"] == "Amavasya"]
        assert len(amavasya) == 1
        assert amavasya[0]["number"] == 30
        assert amavasya[0]["paksha"] == "krishna"

    def test_loader_integration(self):
        raw = load_definition("tithis")
        assert "tithis" in raw


class TestKaranaDefinitions:
    """Tests for knowledge/definitions/karanas.json."""

    def test_loads_successfully(self):
        data = get_karana_definitions()
        assert data, "karanas should not be empty"

    def test_has_7_movable_karanas(self):
        data = get_karana_definitions()
        movable = data.get("karanas", {}).get("movable", [])
        assert len(movable) == 7, f"Expected 7 movable karanas, got {len(movable)}"

    def test_has_4_fixed_karanas(self):
        data = get_karana_definitions()
        fixed = data.get("karanas", {}).get("fixed", [])
        assert len(fixed) == 4, f"Expected 4 fixed karanas, got {len(fixed)}"

    def test_total_11_karanas(self):
        data = get_karana_definitions()
        karanas = data.get("karanas", {})
        total = len(karanas.get("movable", [])) + len(karanas.get("fixed", []))
        assert total == 11, f"Expected 11 total karanas, got {total}"

    def test_movable_karana_has_required_fields(self):
        data = get_karana_definitions()
        required = ["number", "name", "sanskrit", "lord", "nature", "good_for"]
        for karana in data.get("karanas", {}).get("movable", []):
            for field in required:
                assert field in karana, f"Movable karana {karana.get('name')} missing '{field}'"

    def test_fixed_karana_has_required_fields(self):
        data = get_karana_definitions()
        required = ["number", "name", "sanskrit", "nature", "position"]
        for karana in data.get("karanas", {}).get("fixed", []):
            for field in required:
                assert field in karana, f"Fixed karana {karana.get('name')} missing '{field}'"

    def test_vishti_is_bhadra(self):
        data = get_karana_definitions()
        movable = data.get("karanas", {}).get("movable", [])
        vishti = [k for k in movable if k["name"] == "Vishti"]
        assert len(vishti) == 1
        assert vishti[0].get("also_called") == "Bhadra"
        assert vishti[0]["nature"] == "bad"

    def test_has_calculation_info(self):
        data = get_karana_definitions()
        calc = data.get("calculation", {})
        assert "formula" in calc
        assert calc.get("total_karanas_per_month") == 60

    def test_karana_numbers_sequential(self):
        data = get_karana_definitions()
        karanas = data.get("karanas", {})
        all_nums = [k["number"] for k in karanas.get("movable", [])]
        all_nums += [k["number"] for k in karanas.get("fixed", [])]
        assert all_nums == list(range(1, 12))

    def test_loader_integration(self):
        raw = load_definition("karanas")
        assert "karanas" in raw


class TestNityaYogaDefinitions:
    """Tests for knowledge/definitions/nitya_yogas.json."""

    def test_loads_successfully(self):
        data = get_nitya_yoga_definitions()
        assert data, "nitya_yogas should not be empty"

    def test_has_27_yogas(self):
        data = get_nitya_yoga_definitions()
        yogas = data.get("nitya_yogas", [])
        assert len(yogas) == 27, f"Expected 27 nitya yogas, got {len(yogas)}"

    def test_yoga_numbers_sequential(self):
        data = get_nitya_yoga_definitions()
        yogas = data.get("nitya_yogas", [])
        numbers = [y["number"] for y in yogas]
        assert numbers == list(range(1, 28))

    def test_yoga_has_required_fields(self):
        data = get_nitya_yoga_definitions()
        required = [
            "number",
            "name",
            "sanskrit",
            "meaning",
            "nature",
            "lord",
            "deity",
            "good_for",
            "description",
        ]
        for yoga in data.get("nitya_yogas", []):
            for field in required:
                assert (
                    field in yoga
                ), f"Yoga {yoga['number']} ({yoga.get('name')}) missing '{field}'"

    def test_first_yoga_is_vishkambha(self):
        data = get_nitya_yoga_definitions()
        yogas = data.get("nitya_yogas", [])
        assert yogas[0]["name"] == "Vishkambha"

    def test_last_yoga_is_vaidhriti(self):
        data = get_nitya_yoga_definitions()
        yogas = data.get("nitya_yogas", [])
        assert yogas[-1]["name"] == "Vaidhriti"

    def test_nature_summary_present(self):
        data = get_nitya_yoga_definitions()
        summary = data.get("nature_summary", {})
        assert "good" in summary
        assert "bad" in summary
        good_count = len(summary.get("good", []))
        bad_count = len(summary.get("bad", []))
        mixed_count = len(summary.get("mixed", []))
        assert good_count + bad_count + mixed_count == 27

    def test_has_calculation_info(self):
        data = get_nitya_yoga_definitions()
        calc = data.get("calculation", {})
        assert "formula" in calc
        assert calc.get("total_yogas") == 27

    def test_loader_integration(self):
        raw = load_definition("nitya_yogas")
        assert "nitya_yogas" in raw


class TestVaraDefinitions:
    """Tests for knowledge/definitions/varas.json."""

    def test_loads_successfully(self):
        data = get_vara_definitions()
        assert data, "varas should not be empty"

    def test_has_7_varas(self):
        data = get_vara_definitions()
        varas = data.get("varas", [])
        assert len(varas) == 7, f"Expected 7 varas, got {len(varas)}"

    def test_vara_numbers_sequential(self):
        data = get_vara_definitions()
        varas = data.get("varas", [])
        numbers = [v["number"] for v in varas]
        assert numbers == list(range(0, 7))

    def test_vara_has_required_fields(self):
        data = get_vara_definitions()
        required = [
            "number",
            "name",
            "sanskrit",
            "english",
            "lord",
            "nature",
            "good_for",
            "avoid",
            "rahu_kaal",
            "hora_sequence",
            "color",
        ]
        for vara in data.get("varas", []):
            for field in required:
                assert field in vara, f"Vara {vara.get('english')} missing '{field}'"

    def test_correct_english_day_names(self):
        data = get_vara_definitions()
        varas = data.get("varas", [])
        expected_days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        actual_days = [v["english"] for v in varas]
        assert actual_days == expected_days

    def test_correct_lords(self):
        data = get_vara_definitions()
        varas = data.get("varas", [])
        expected_lords = [
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
        ]
        actual_lords = [v["lord"] for v in varas]
        assert actual_lords == expected_lords

    def test_hora_sequence_has_7_planets(self):
        data = get_vara_definitions()
        for vara in data.get("varas", []):
            seq = vara.get("hora_sequence", [])
            assert len(seq) == 7, f"{vara['english']} hora_sequence should have 7 entries"

    def test_hora_system_present(self):
        data = get_vara_definitions()
        hora = data.get("hora_system", {})
        assert "chaldean_order" in hora
        assert len(hora.get("chaldean_order", [])) == 7

    def test_vara_nature_categories(self):
        data = get_vara_definitions()
        vara_nature = data.get("vara_nature", {})
        assert "saumya" in vara_nature
        assert "krura" in vara_nature

    def test_sunday_first_hora_is_sun(self):
        data = get_vara_definitions()
        varas = data.get("varas", [])
        sunday = varas[0]
        assert sunday["english"] == "Sunday"
        assert sunday["hora_sequence"][0] == "sun"

    def test_loader_integration(self):
        raw = load_definition("varas")
        assert "varas" in raw


class TestAvasthaDefinitions:
    """Tests for knowledge/definitions/avasthas.json."""

    def test_loads_successfully(self):
        data = get_avastha_definitions()
        assert data, "avasthas should not be empty"

    def test_has_baladi_avasthas(self):
        data = get_avastha_definitions()
        baladi = data.get("avasthas", {}).get("baladi_avasthas", {})
        states = baladi.get("states", [])
        assert len(states) == 5, f"Expected 5 Baladi avasthas, got {len(states)}"

    def test_baladi_names(self):
        data = get_avastha_definitions()
        baladi = data.get("avasthas", {}).get("baladi_avasthas", {})
        states = baladi.get("states", [])
        expected = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]
        actual = [s["name"] for s in states]
        assert actual == expected

    def test_baladi_strength_percentages(self):
        data = get_avastha_definitions()
        baladi = data.get("avasthas", {}).get("baladi_avasthas", {})
        states = baladi.get("states", [])
        expected_strengths = [25, 50, 100, 50, 0]
        actual = [s["strength_percent"] for s in states]
        assert actual == expected_strengths

    def test_baladi_has_required_fields(self):
        data = get_avastha_definitions()
        baladi = data.get("avasthas", {}).get("baladi_avasthas", {})
        required = ["name", "sanskrit", "meaning", "strength_percent", "effect"]
        for state in baladi.get("states", []):
            for field in required:
                assert field in state, f"Baladi state {state.get('name')} missing '{field}'"

    def test_has_shayanaadi_avasthas(self):
        data = get_avastha_definitions()
        shayanaadi = data.get("avasthas", {}).get("shayanaadi_avasthas", {})
        states = shayanaadi.get("states", [])
        assert len(states) == 12, f"Expected 12 Shayanaadi avasthas, got {len(states)}"

    def test_shayanaadi_has_required_fields(self):
        data = get_avastha_definitions()
        shayanaadi = data.get("avasthas", {}).get("shayanaadi_avasthas", {})
        required = ["name", "sanskrit", "meaning", "effect", "result_quality"]
        for state in shayanaadi.get("states", []):
            for field in required:
                assert field in state, f"Shayanaadi state {state.get('name')} missing '{field}'"

    def test_has_jagradaadi_avasthas(self):
        data = get_avastha_definitions()
        jagradaadi = data.get("avasthas", {}).get("jagradaadi_avasthas", {})
        states = jagradaadi.get("states", [])
        assert len(states) == 3, f"Expected 3 Jagradaadi avasthas, got {len(states)}"

    def test_jagradaadi_names(self):
        data = get_avastha_definitions()
        jagradaadi = data.get("avasthas", {}).get("jagradaadi_avasthas", {})
        states = jagradaadi.get("states", [])
        expected = ["Jagrat", "Swapna", "Sushupti"]
        actual = [s["name"] for s in states]
        assert actual == expected

    def test_has_deeptaadi_avasthas(self):
        data = get_avastha_definitions()
        deeptaadi = data.get("avasthas", {}).get("deeptaadi_avasthas", {})
        states = deeptaadi.get("states", [])
        assert len(states) == 9, f"Expected 9 Deeptaadi avasthas, got {len(states)}"

    def test_deeptaadi_first_is_deepta(self):
        data = get_avastha_definitions()
        deeptaadi = data.get("avasthas", {}).get("deeptaadi_avasthas", {})
        states = deeptaadi.get("states", [])
        assert states[0]["name"] == "Deepta"
        assert states[0]["condition"] == "Planet in exaltation sign"

    def test_yuva_is_strongest_baladi(self):
        data = get_avastha_definitions()
        baladi = data.get("avasthas", {}).get("baladi_avasthas", {})
        states = baladi.get("states", [])
        yuva = [s for s in states if s["name"] == "Yuva"]
        assert len(yuva) == 1
        assert yuva[0]["strength_percent"] == 100

    def test_loader_integration(self):
        raw = load_definition("avasthas")
        assert "avasthas" in raw


# =============================================================================
# Interpretation File Tests
# =============================================================================


class TestPlanetInHouseInterpretations:
    """Tests for knowledge/interpretations/planet_in_house.json."""

    def test_loads_successfully(self):
        data = get_planet_in_house_interpretations()
        assert data, "planet_in_house should not be empty"

    def test_has_wrapper_key(self):
        data = get_planet_in_house_interpretations()
        assert "planet_in_house" in data

    def test_has_108_combinations(self):
        data = get_planet_in_house_interpretations()
        inner = data["planet_in_house"]
        combo_keys = [k for k in inner if k != "description"]
        assert len(combo_keys) == 108, f"Expected 108 combinations, got {len(combo_keys)}"

    def test_all_9_planets_covered(self):
        data = get_planet_in_house_interpretations()
        inner = data["planet_in_house"]
        planets = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        }
        for planet in planets:
            count = sum(1 for k in inner if k.startswith(f"{planet}_in_house_"))
            assert count == 12, f"{planet} should have 12 house entries, got {count}"

    def test_entry_has_required_fields(self):
        data = get_planet_in_house_interpretations()
        inner = data["planet_in_house"]
        required = [
            "summary",
            "positive",
            "negative",
            "career",
            "relationships",
            "health",
        ]
        sample = inner["sun_in_house_1"]
        for field in required:
            assert field in sample, f"sun_in_house_1 missing '{field}'"

    def test_positive_is_list(self):
        data = get_planet_in_house_interpretations()
        inner = data["planet_in_house"]
        sample = inner["sun_in_house_1"]
        assert isinstance(sample["positive"], list)
        assert len(sample["positive"]) > 0

    def test_loader_integration(self):
        raw = load_interpretation("planet_in_house")
        assert "planet_in_house" in raw


class TestPlanetInSignInterpretations:
    """Tests for knowledge/interpretations/planet_in_sign.json."""

    def test_loads_successfully(self):
        data = get_planet_in_sign_interpretations()
        assert data, "planet_in_sign should not be empty"

    def test_has_wrapper_key(self):
        data = get_planet_in_sign_interpretations()
        assert "planet_in_sign" in data

    def test_has_108_combinations(self):
        data = get_planet_in_sign_interpretations()
        inner = data["planet_in_sign"]
        combo_keys = [k for k in inner if k != "description"]
        assert len(combo_keys) == 108, f"Expected 108 combinations, got {len(combo_keys)}"

    def test_all_9_planets_and_12_signs_covered(self):
        data = get_planet_in_sign_interpretations()
        inner = data["planet_in_sign"]
        planets = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        }
        signs = [
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
        for planet in planets:
            for sign in signs:
                key = f"{planet}_in_{sign}"
                assert key in inner, f"Missing {key}"

    def test_entry_has_required_fields(self):
        data = get_planet_in_sign_interpretations()
        inner = data["planet_in_sign"]
        required = [
            "summary",
            "positive",
            "negative",
            "career",
            "relationships",
            "health",
        ]
        sample = inner["sun_in_aries"]
        for field in required:
            assert field in sample, f"sun_in_aries missing '{field}'"

    def test_loader_integration(self):
        raw = load_interpretation("planet_in_sign")
        assert "planet_in_sign" in raw


class TestPlanetInNakshatraInterpretations:
    """Tests for knowledge/interpretations/planet_in_nakshatra.json."""

    def test_loads_successfully(self):
        data = get_planet_in_nakshatra_interpretations()
        assert data, "planet_in_nakshatra should not be empty"

    def test_has_243_combinations(self):
        data = get_planet_in_nakshatra_interpretations()
        wrapper_key = next(iter(data.keys()))
        inner = data[wrapper_key]
        combo_keys = [k for k in inner if k != "description"]
        assert len(combo_keys) == 243, f"Expected 243 combinations, got {len(combo_keys)}"

    def test_all_9_planets_present(self):
        data = get_planet_in_nakshatra_interpretations()
        wrapper_key = next(iter(data.keys()))
        inner = data[wrapper_key]
        combo_keys = [k for k in inner if k != "description"]
        planets = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        }
        for planet in planets:
            count = sum(1 for k in combo_keys if k.startswith(f"{planet}_in_"))
            assert count == 27, f"{planet} should have 27 nakshatra entries, got {count}"

    def test_entry_has_required_fields(self):
        data = get_planet_in_nakshatra_interpretations()
        wrapper_key = next(iter(data.keys()))
        inner = data[wrapper_key]
        combo_keys = [k for k in inner if k != "description"]
        sample = inner[combo_keys[0]]
        required = ["summary", "qualities"]
        for field in required:
            assert field in sample, f"{combo_keys[0]} missing '{field}'"

    def test_loader_integration(self):
        raw = load_interpretation("planet_in_nakshatra")
        assert raw


class TestHouseLordInHouseInterpretations:
    """Tests for knowledge/interpretations/house_lord_in_house.json."""

    def test_loads_successfully(self):
        data = get_house_lord_in_house_interpretations()
        assert data, "house_lord_in_house should not be empty"

    def test_has_144_combinations(self):
        data = get_house_lord_in_house_interpretations()
        wrapper_key = next(iter(data.keys()))
        inner = data[wrapper_key]
        combo_keys = [k for k in inner if k != "description"]
        assert len(combo_keys) == 144, f"Expected 144 combinations, got {len(combo_keys)}"

    def test_all_12_lords_covered(self):
        data = get_house_lord_in_house_interpretations()
        wrapper_key = next(iter(data.keys()))
        inner = data[wrapper_key]
        combo_keys = [k for k in inner if k != "description"]
        for lord_num in range(1, 13):
            count = sum(1 for k in combo_keys if k.startswith(f"lord_{lord_num}_in_house_"))
            assert count == 12, f"Lord {lord_num} should have 12 house placements, got {count}"

    def test_entry_has_required_fields(self):
        data = get_house_lord_in_house_interpretations()
        wrapper_key = next(iter(data.keys()))
        inner = data[wrapper_key]
        sample = inner["lord_1_in_house_1"]
        required = ["summary", "positive", "negative", "specific_effects"]
        for field in required:
            assert field in sample, f"lord_1_in_house_1 missing '{field}'"

    def test_loader_integration(self):
        raw = load_interpretation("house_lord_in_house")
        assert raw


class TestDashaGuide:
    """Tests for knowledge/interpretations/dasha_guide.json."""

    def test_loads_successfully(self):
        data = get_dasha_guide()
        assert data, "dasha_guide should not be empty"

    def test_has_wrapper_key(self):
        data = get_dasha_guide()
        assert "dasha_guide" in data

    def test_has_9_planets(self):
        data = get_dasha_guide()
        inner = data["dasha_guide"]
        planets = [k for k in inner if k != "description"]
        expected = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        }
        assert set(planets) == expected

    def test_entry_has_required_fields(self):
        data = get_dasha_guide()
        inner = data["dasha_guide"]
        required = [
            "duration_years",
            "theme",
            "focus_areas",
            "career",
            "health",
            "relationships",
            "spiritual",
            "practical_advice",
            "challenges",
            "opportunities",
        ]
        all_planets = [
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        ]
        for planet in all_planets:
            entry = inner[planet]
            for field in required:
                assert field in entry, f"Dasha guide for {planet} missing '{field}'"

    def test_correct_dasha_durations(self):
        data = get_dasha_guide()
        inner = data["dasha_guide"]
        expected_durations = {
            "sun": 6,
            "moon": 10,
            "mars": 7,
            "mercury": 17,
            "jupiter": 16,
            "venus": 20,
            "saturn": 19,
            "rahu": 18,
            "ketu": 7,
        }
        for planet, expected_years in expected_durations.items():
            actual = inner[planet]["duration_years"]
            assert (
                actual == expected_years
            ), f"{planet} dasha should be {expected_years} years, got {actual}"

    def test_practical_advice_is_list(self):
        data = get_dasha_guide()
        inner = data["dasha_guide"]
        for planet in ["sun", "moon", "mars"]:
            advice = inner[planet].get("practical_advice", [])
            assert isinstance(advice, list)
            assert len(advice) > 0

    def test_loader_integration(self):
        raw = load_interpretation("dasha_guide")
        assert "dasha_guide" in raw


# =============================================================================
# Expanded Divisional Interpretation Tests
# =============================================================================


class TestExpandedDivisionalInterpretations:
    """Tests for D2-D60 in divisional_interpretation.json."""

    def test_has_all_divisional_charts(self):
        data = get_divisional_interpretation()
        expected_charts = [
            "d9_navamsha",
            "d10_dashamsha",
            "d2_hora",
            "d3_drekkana",
            "d4_chaturthamsha",
            "d7_saptamsha",
            "d12_dwadashamsha",
            "d16_shodashamsha",
            "d20_vimshamsha",
            "d24_chaturvimshamsha",
            "d27_nakshatramsha",
            "d30_trimshamsha",
            "d60_shashtiamsha",
        ]
        for chart in expected_charts:
            assert chart in data, f"Missing {chart}"

    def test_each_chart_has_description(self):
        data = get_divisional_interpretation()
        for key, chart_data in data.items():
            if key.startswith("d") and key[1:].split("_")[0].isdigit():
                assert "description" in chart_data, f"{key} missing description"

    def test_each_chart_has_significance(self):
        data = get_divisional_interpretation()
        for key, chart_data in data.items():
            if key.startswith("d") and key[1:].split("_")[0].isdigit():
                assert "significance" in chart_data, f"{key} missing significance"

    def test_d9_has_12_house_meanings(self):
        data = get_divisional_interpretation()
        d9 = data["d9_navamsha"]
        houses = d9.get("house_meanings", {})
        assert len(houses) >= 12, f"D9 should have 12 house meanings, got {len(houses)}"

    def test_d2_has_planet_in_signs(self):
        data = get_divisional_interpretation()
        d2 = data["d2_hora"]
        pis = d2.get("planet_in_signs", {})
        assert len(pis) >= 9, f"D2 should have 9+ planet entries, got {len(pis)}"

    def test_d3_has_planet_in_signs(self):
        data = get_divisional_interpretation()
        d3 = data["d3_drekkana"]
        pis = d3.get("planet_in_signs", {})
        assert len(pis) >= 9, f"D3 should have 9+ planet entries, got {len(pis)}"

    def test_d4_through_d60_have_content(self):
        data = get_divisional_interpretation()
        charts_to_check = [
            "d4_chaturthamsha",
            "d7_saptamsha",
            "d12_dwadashamsha",
            "d16_shodashamsha",
            "d20_vimshamsha",
            "d24_chaturvimshamsha",
            "d27_nakshatramsha",
            "d30_trimshamsha",
            "d60_shashtiamsha",
        ]
        for chart_key in charts_to_check:
            chart = data.get(chart_key, {})
            total_keys = len(chart)
            assert total_keys >= 3, f"{chart_key} should have at least 3 keys, got {total_keys}"


# =============================================================================
# Extended Loader Integration Tests
# =============================================================================


class TestPanchangaLoaderIntegration:
    """Test that all panchanga loader functions work correctly."""

    def test_load_tithis_raw(self):
        raw = load_definition("tithis")
        assert "tithis" in raw

    def test_load_karanas_raw(self):
        raw = load_definition("karanas")
        assert "karanas" in raw

    def test_load_nitya_yogas_raw(self):
        raw = load_definition("nitya_yogas")
        assert "nitya_yogas" in raw

    def test_load_varas_raw(self):
        raw = load_definition("varas")
        assert "varas" in raw

    def test_load_avasthas_raw(self):
        raw = load_definition("avasthas")
        assert "avasthas" in raw

    def test_load_planet_in_house_raw(self):
        raw = load_interpretation("planet_in_house")
        assert "planet_in_house" in raw

    def test_load_planet_in_sign_raw(self):
        raw = load_interpretation("planet_in_sign")
        assert "planet_in_sign" in raw

    def test_load_planet_in_nakshatra_raw(self):
        raw = load_interpretation("planet_in_nakshatra")
        assert raw

    def test_load_house_lord_in_house_raw(self):
        raw = load_interpretation("house_lord_in_house")
        assert raw

    def test_load_dasha_guide_raw(self):
        raw = load_interpretation("dasha_guide")
        assert "dasha_guide" in raw
