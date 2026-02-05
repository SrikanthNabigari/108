"""Tests for packages/context/src/varshaphal.py."""

from packages.context.src.varshaphal import (
    RASHI_LORDS,
    calculate_muntha,
    calculate_sahams,
    detect_tajika_yogas,
    determine_varshesha,
    get_varshaphal_analysis,
)


class TestCalculateMuntha:
    """Tests for calculate_muntha."""

    def test_age_zero(self):
        # At age 0, Muntha is in the same sign as lagna
        result = calculate_muntha(0, 0)  # Aries lagna
        assert result["muntha_rashi"] == 0
        assert result["house_from_lagna"] == 1

    def test_age_one(self):
        result = calculate_muntha(0, 1)
        assert result["muntha_rashi"] == 1  # Taurus

    def test_wraps_around_12(self):
        result = calculate_muntha(0, 12)
        assert result["muntha_rashi"] == 0  # Back to Aries

    def test_libra_lagna_age_33(self):
        # Libra=6, age 33 -> (6 + 33%12) = (6 + 9) % 12 = 3 (Cancer)
        result = calculate_muntha(6, 33)
        assert result["muntha_rashi"] == 3

    def test_house_from_lagna(self):
        # Aries lagna, age 5 -> Muntha in Virgo (5)
        # House = (5 - 0) % 12 + 1 = 6
        result = calculate_muntha(0, 5)
        assert result["house_from_lagna"] == 6

    def test_returns_effects(self):
        result = calculate_muntha(0, 0)
        assert "theme" in result
        assert "effects" in result
        assert "overall" in result

    def test_all_12_houses_have_effects(self):
        for age in range(12):
            result = calculate_muntha(0, age)
            assert result["theme"] != "", f"No theme for age {age}"

    def test_favorable_house(self):
        # House 1 should be favorable
        result = calculate_muntha(0, 0)
        assert result["overall"] == "favorable"

    def test_challenging_house(self):
        # House 6 should be challenging
        result = calculate_muntha(0, 5)
        assert result["overall"] == "challenging"


class TestDetermineVarshesha:
    """Tests for determine_varshesha."""

    def test_aries_lagna(self):
        result = determine_varshesha(0)
        assert result["year_lord"] == "mars"

    def test_cancer_lagna(self):
        result = determine_varshesha(3)
        assert result["year_lord"] == "moon"

    def test_leo_lagna(self):
        result = determine_varshesha(4)
        assert result["year_lord"] == "sun"

    def test_returns_effects(self):
        result = determine_varshesha(0)
        assert "theme" in result
        assert "favorable" in result
        assert "unfavorable" in result

    def test_all_12_signs(self):
        for rashi in range(12):
            result = determine_varshesha(rashi)
            lord = result["year_lord"]
            assert lord == RASHI_LORDS[rashi], f"Wrong lord for rashi {rashi}"


class TestDetectTajikaYogas:
    """Tests for detect_tajika_yogas."""

    def test_empty_positions(self):
        result = detect_tajika_yogas({})
        assert result == []

    def test_induvara_all_kendra(self):
        # All planets in kendra houses -> Induvara Yoga
        positions = {
            "sun": {"house": 1, "longitude": 10.0},
            "moon": {"house": 4, "longitude": 100.0},
            "mars": {"house": 7, "longitude": 190.0},
            "jupiter": {"house": 10, "longitude": 280.0},
        }
        result = detect_tajika_yogas(positions)
        yoga_ids = [y["yoga_id"] for y in result]
        assert "induvara" in yoga_ids

    def test_returns_yoga_details(self):
        positions = {
            "sun": {"house": 1, "longitude": 10.0},
            "moon": {"house": 4, "longitude": 100.0},
            "mars": {"house": 7, "longitude": 190.0},
            "jupiter": {"house": 10, "longitude": 280.0},
        }
        result = detect_tajika_yogas(positions)
        if result:
            assert "name" in result[0]
            assert "type" in result[0]
            assert "effect" in result[0]


class TestCalculateSahams:
    """Tests for calculate_sahams."""

    def test_returns_10_sahams(self):
        longitudes = {
            "sun": 100.0,
            "moon": 200.0,
            "mars": 50.0,
            "mercury": 120.0,
            "jupiter": 250.0,
            "venus": 300.0,
            "saturn": 320.0,
        }
        result = calculate_sahams(longitudes, lagna_lon=15.0)
        assert len(result) == 10

    def test_punya_saham_day(self):
        longitudes = {"sun": 100.0, "moon": 200.0}
        result = calculate_sahams(longitudes, lagna_lon=0.0, is_day_chart=True)
        # Punya = Asc + Moon - Sun = 0 + 200 - 100 = 100
        assert result["punya_saham"]["longitude"] == 100.0

    def test_punya_saham_night(self):
        longitudes = {"sun": 100.0, "moon": 200.0}
        result = calculate_sahams(longitudes, lagna_lon=0.0, is_day_chart=False)
        # Punya_night = Asc + Sun - Moon = 0 + 100 - 200 = -100 % 360 = 260
        assert result["punya_saham"]["longitude"] == 260.0

    def test_saham_wraps_around(self):
        longitudes = {"sun": 300.0, "moon": 50.0, "jupiter": 200.0, "mercury": 100.0}
        result = calculate_sahams(longitudes, lagna_lon=350.0)
        # All should be 0-360
        for saham in result.values():
            assert 0 <= saham["longitude"] < 360

    def test_saham_has_rashi(self):
        longitudes = {"sun": 100.0, "moon": 200.0}
        result = calculate_sahams(longitudes, lagna_lon=0.0)
        for saham in result.values():
            assert 0 <= saham["rashi"] <= 11

    def test_saham_has_signifies(self):
        longitudes = {"sun": 100.0, "moon": 200.0, "jupiter": 250.0, "mercury": 120.0}
        result = calculate_sahams(longitudes, lagna_lon=0.0)
        assert result["punya_saham"]["signifies"] != ""


class TestGetVarshaphalAnalysis:
    """Tests for get_varshaphal_analysis."""

    def test_basic_analysis(self):
        result = get_varshaphal_analysis(6, 33)  # Libra lagna, age 33
        assert result["age"] == 33
        assert result["birth_lagna_rashi"] == 6
        assert "muntha" in result
        assert "varshesha" in result

    def test_with_planet_longitudes(self):
        longitudes = {
            "sun": 100.0,
            "moon": 200.0,
            "mars": 50.0,
            "mercury": 120.0,
            "jupiter": 250.0,
            "venus": 300.0,
            "saturn": 320.0,
        }
        result = get_varshaphal_analysis(6, 33, planet_longitudes=longitudes, lagna_lon=15.0)
        assert len(result["sahams"]) == 10

    def test_without_planet_longitudes(self):
        result = get_varshaphal_analysis(0, 25)
        assert result["sahams"] == {}

    def test_annual_outlook(self):
        result = get_varshaphal_analysis(0, 0)
        assert result["annual_outlook"] in ("favorable", "challenging", "mixed")

    def test_muntha_annual_themes(self):
        result = get_varshaphal_analysis(0, 0)
        assert isinstance(result["muntha_annual_themes"], list)

    def test_custom_varshaphal_lagna(self):
        result = get_varshaphal_analysis(0, 25, varshaphal_lagna_rashi=4)
        assert result["varshaphal_lagna_rashi"] == 4
        assert result["varshesha"]["year_lord"] == "sun"  # Leo lord is Sun
