"""Tests for packages/self/src/divisional_interpreter.py."""

import pytest

from packages.cosmos.src.divisional import get_divisional_chart
from packages.self.src.divisional_interpreter import (
    get_divisional_analysis,
    interpret_d2_position,
    interpret_d3_position,
    interpret_d4_position,
    interpret_d7_position,
    interpret_d9_chart,
    interpret_d9_position,
    interpret_d10_chart,
    interpret_d10_position,
    interpret_d12_position,
    interpret_d16_position,
    interpret_d20_position,
    interpret_d24_position,
    interpret_d27_position,
    interpret_d30_position,
    interpret_d60_position,
)

SAMPLE_LONGITUDES = {
    "sun": 125.5,  # Leo ~5.5
    "moon": 215.3,  # Scorpio ~5.3
    "mars": 45.2,  # Taurus ~15.2
    "mercury": 130.0,  # Leo ~10
    "jupiter": 250.0,  # Sagittarius ~10
    "venus": 100.0,  # Cancer ~10
    "saturn": 320.0,  # Aquarius ~20
}


class TestInterpretD9Position:
    """Tests for interpret_d9_position."""

    def test_sun_in_aries(self):
        result = interpret_d9_position("sun", "aries")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert result["rashi"] == "aries"
        assert result["theme"] != ""
        assert result["marriage"] != ""
        assert result["dharma"] != ""
        assert result["strength"] == "exalted"

    def test_sun_in_libra_debilitated(self):
        result = interpret_d9_position("sun", "libra")
        assert result["found"] is True
        assert result["strength"] == "debilitated"

    def test_all_12_signs_for_sun(self):
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
        for sign in signs:
            result = interpret_d9_position("sun", sign)
            assert result["found"] is True, f"Missing D9 data for Sun in {sign}"

    def test_moon_position(self):
        result = interpret_d9_position("moon", "cancer")
        assert result["found"] is True

    def test_invalid_planet_returns_not_found(self):
        result = interpret_d9_position("pluto", "aries")
        assert result["found"] is False

    def test_invalid_sign_returns_not_found(self):
        result = interpret_d9_position("sun", "ophiuchus")
        assert result["found"] is False


class TestInterpretD10Position:
    """Tests for interpret_d10_position."""

    def test_sun_in_aries(self):
        result = interpret_d10_position("sun", "aries")
        assert result["found"] is True
        assert "career" in result
        assert "leadership" in result

    def test_mars_in_capricorn(self):
        result = interpret_d10_position("mars", "capricorn")
        assert result["found"] is True

    def test_invalid_combo(self):
        result = interpret_d10_position("pluto", "aries")
        assert result["found"] is False


class TestInterpretD9Chart:
    """Tests for interpret_d9_chart."""

    def test_full_chart_interpretation(self):
        d9 = get_divisional_chart(SAMPLE_LONGITUDES, 9)
        result = interpret_d9_chart(d9)
        assert result["division"] == 9
        assert result["division_name"] == "Navamsha"
        assert len(result["planets"]) > 0

    def test_each_planet_interpreted(self):
        d9 = get_divisional_chart(SAMPLE_LONGITUDES, 9)
        result = interpret_d9_chart(d9)
        for planet_name in SAMPLE_LONGITUDES:
            assert planet_name in result["planets"]


class TestInterpretD10Chart:
    """Tests for interpret_d10_chart."""

    def test_full_chart_interpretation(self):
        d10 = get_divisional_chart(SAMPLE_LONGITUDES, 10)
        result = interpret_d10_chart(d10)
        assert result["division"] == 10
        assert result["division_name"] == "Dashamsha"
        assert len(result["planets"]) > 0


class TestGetDivisionalAnalysis:
    """Tests for get_divisional_analysis."""

    def test_returns_both_d9_d10(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        assert "d9_navamsha" in result
        assert "d10_dashamsha" in result

    def test_d9_has_planets(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        assert len(result["d9_navamsha"]["planets"]) > 0

    def test_d10_has_planets(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        assert len(result["d10_dashamsha"]["planets"]) > 0

    def test_returns_all_divisional_charts(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        expected_keys = [
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
            "d27_bhamsha",
            "d30_trimshamsha",
            "d60_shashtiamsha",
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_all_divisional_charts_have_planets(self):
        result = get_divisional_analysis(SAMPLE_LONGITUDES)
        for key, chart_data in result.items():
            assert "planets" in chart_data, f"{key} missing planets"
            assert len(chart_data["planets"]) > 0, f"{key} has no planets"


ALL_SIGNS = [
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

ALL_PLANETS = [
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


class TestInterpretD2Position:
    """Tests for D2 Hora chart interpretation."""

    def test_basic_found(self):
        result = interpret_d2_position("sun", "leo")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert result["rashi"] == "leo"

    def test_returns_required_keys(self):
        result = interpret_d2_position("jupiter", "cancer")
        assert "summary" in result
        assert "key_themes" in result
        assert "positive" in result
        assert "negative" in result
        assert "specific_effects" in result
        assert "dignity" in result

    def test_exalted_dignity(self):
        result = interpret_d2_position("sun", "aries")
        assert result["dignity"] == "exalted"

    def test_own_sign_dignity(self):
        result = interpret_d2_position("sun", "leo")
        assert result["dignity"] == "own_sign"

    def test_debilitated_dignity(self):
        result = interpret_d2_position("sun", "libra")
        assert result["dignity"] == "debilitated"

    def test_invalid_sign(self):
        result = interpret_d2_position("sun", "invalid")
        assert result["found"] is False

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d2_position(planet, "aries")
            assert result["found"] is True, f"D2 missing data for {planet}"

    def test_all_signs_covered(self):
        for sign in ALL_SIGNS:
            result = interpret_d2_position("venus", sign)
            assert result["found"] is True, f"D2 missing data for Venus in {sign}"


class TestInterpretD3Position:
    """Tests for D3 Drekkana chart interpretation."""

    def test_basic_found(self):
        result = interpret_d3_position("mars", "aries")
        assert result["found"] is True
        assert result["summary"] != ""

    def test_returns_required_keys(self):
        result = interpret_d3_position("mars", "scorpio")
        assert "summary" in result
        assert "key_themes" in result
        assert "positive" in result
        assert "negative" in result
        assert "specific_effects" in result

    def test_mars_courage_theme(self):
        result = interpret_d3_position("mars", "aries")
        assert any("courage" in theme for theme in result["key_themes"])

    def test_invalid_sign(self):
        result = interpret_d3_position("mars", "atlantis")
        assert result["found"] is False

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d3_position(planet, "gemini")
            assert result["found"] is True


class TestInterpretD4Position:
    """Tests for D4 Chaturthamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d4_position("venus", "taurus")
        assert result["found"] is True

    def test_property_themes(self):
        result = interpret_d4_position("mars", "capricorn")
        assert any("property" in theme or "land" in theme for theme in result["key_themes"])

    def test_exalted_planet(self):
        result = interpret_d4_position("mars", "capricorn")
        assert result["dignity"] == "exalted"
        assert "Excellent" in result["specific_effects"]

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d4_position(planet, "cancer")
            assert result["found"] is True


class TestInterpretD7Position:
    """Tests for D7 Saptamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d7_position("jupiter", "cancer")
        assert result["found"] is True

    def test_children_themes(self):
        result = interpret_d7_position("jupiter", "sagittarius")
        assert any("children" in theme or "progeny" in theme for theme in result["key_themes"])

    def test_debilitated_planet(self):
        result = interpret_d7_position("jupiter", "capricorn")
        assert result["dignity"] == "debilitated"
        assert "Challenges" in result["specific_effects"]

    def test_invalid_sign(self):
        result = interpret_d7_position("jupiter", "xyz")
        assert result["found"] is False

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d7_position(planet, "pisces")
            assert result["found"] is True


class TestInterpretD12Position:
    """Tests for D12 Dwadashamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d12_position("sun", "leo")
        assert result["found"] is True

    def test_parent_themes(self):
        result = interpret_d12_position("sun", "aries")
        assert any("father" in theme or "paternal" in theme for theme in result["key_themes"])

    def test_mother_themes(self):
        result = interpret_d12_position("moon", "cancer")
        assert any("mother" in theme or "maternal" in theme for theme in result["key_themes"])

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d12_position(planet, "virgo")
            assert result["found"] is True


class TestInterpretD16Position:
    """Tests for D16 Shodashamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d16_position("venus", "libra")
        assert result["found"] is True

    def test_vehicle_themes(self):
        result = interpret_d16_position("venus", "taurus")
        assert any(
            "luxury" in theme or "vehicles" in theme or "cars" in theme
            for theme in result["key_themes"]
        )

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d16_position(planet, "leo")
            assert result["found"] is True


class TestInterpretD20Position:
    """Tests for D20 Vimshamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d20_position("jupiter", "sagittarius")
        assert result["found"] is True

    def test_spiritual_themes(self):
        result = interpret_d20_position("ketu", "pisces")
        assert any(
            "moksha" in theme or "meditation" in theme or "spiritual" in theme
            for theme in result["key_themes"]
        )

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d20_position(planet, "scorpio")
            assert result["found"] is True


class TestInterpretD24Position:
    """Tests for D24 Chaturvimshamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d24_position("mercury", "virgo")
        assert result["found"] is True

    def test_education_themes(self):
        result = interpret_d24_position("mercury", "gemini")
        assert any(
            "education" in theme or "commerce" in theme or "languages" in theme
            for theme in result["key_themes"]
        )

    def test_exalted_mercury(self):
        result = interpret_d24_position("mercury", "virgo")
        assert result["dignity"] == "exalted"

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d24_position(planet, "aquarius")
            assert result["found"] is True


class TestInterpretD27Position:
    """Tests for D27 Bhamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d27_position("mars", "capricorn")
        assert result["found"] is True

    def test_strength_themes(self):
        result = interpret_d27_position("mars", "aries")
        assert any("strength" in theme or "courage" in theme for theme in result["key_themes"])

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d27_position(planet, "sagittarius")
            assert result["found"] is True


class TestInterpretD30Position:
    """Tests for D30 Trimshamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d30_position("saturn", "capricorn")
        assert result["found"] is True

    def test_misfortune_themes(self):
        result = interpret_d30_position("saturn", "aries")
        assert any(
            "chronic" in theme or "poverty" in theme or "disease" in theme
            for theme in result["key_themes"]
        )

    def test_debilitated_protection(self):
        result = interpret_d30_position("saturn", "aries")
        assert result["dignity"] == "debilitated"
        assert "Vulnerable" in result["specific_effects"]

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d30_position(planet, "taurus")
            assert result["found"] is True


class TestInterpretD60Position:
    """Tests for D60 Shashtiamsha chart interpretation."""

    def test_basic_found(self):
        result = interpret_d60_position("jupiter", "cancer")
        assert result["found"] is True

    def test_pastlife_themes(self):
        result = interpret_d60_position("jupiter", "sagittarius")
        assert any(
            "karma" in theme or "merit" in theme or "guru" in theme
            for theme in result["key_themes"]
        )

    def test_exalted_planet(self):
        result = interpret_d60_position("jupiter", "cancer")
        assert result["dignity"] == "exalted"
        assert "positive past-life karma" in result["specific_effects"]

    def test_all_planets_covered(self):
        for planet in ALL_PLANETS:
            result = interpret_d60_position(planet, "capricorn")
            assert result["found"] is True

    def test_invalid_sign(self):
        result = interpret_d60_position("jupiter", "invalid")
        assert result["found"] is False


class TestAllDivisionalFunctionsConsistency:
    """Cross-cutting tests for all divisional interpretation functions."""

    @pytest.mark.parametrize(
        "interpret_fn",
        [
            interpret_d2_position,
            interpret_d3_position,
            interpret_d4_position,
            interpret_d7_position,
            interpret_d12_position,
            interpret_d16_position,
            interpret_d20_position,
            interpret_d24_position,
            interpret_d27_position,
            interpret_d30_position,
            interpret_d60_position,
        ],
    )
    def test_all_functions_return_found_for_valid_input(self, interpret_fn):
        result = interpret_fn("sun", "aries")
        assert result["found"] is True
        assert result["planet"] == "sun"
        assert result["rashi"] == "aries"

    @pytest.mark.parametrize(
        "interpret_fn",
        [
            interpret_d2_position,
            interpret_d3_position,
            interpret_d4_position,
            interpret_d7_position,
            interpret_d12_position,
            interpret_d16_position,
            interpret_d20_position,
            interpret_d24_position,
            interpret_d27_position,
            interpret_d30_position,
            interpret_d60_position,
        ],
    )
    def test_all_functions_return_not_found_for_invalid_sign(self, interpret_fn):
        result = interpret_fn("sun", "invalid_sign")
        assert result["found"] is False

    @pytest.mark.parametrize(
        "interpret_fn",
        [
            interpret_d2_position,
            interpret_d3_position,
            interpret_d4_position,
            interpret_d7_position,
            interpret_d12_position,
            interpret_d16_position,
            interpret_d20_position,
            interpret_d24_position,
            interpret_d27_position,
            interpret_d30_position,
            interpret_d60_position,
        ],
    )
    def test_all_functions_have_required_keys(self, interpret_fn):
        result = interpret_fn("jupiter", "cancer")
        required_keys = [
            "planet",
            "rashi",
            "found",
            "summary",
            "key_themes",
            "positive",
            "negative",
            "specific_effects",
            "dignity",
        ]
        for key in required_keys:
            assert key in result, f"Missing key {key} in {interpret_fn.__name__}"

    @pytest.mark.parametrize(
        "interpret_fn",
        [
            interpret_d2_position,
            interpret_d3_position,
            interpret_d4_position,
            interpret_d7_position,
            interpret_d12_position,
            interpret_d16_position,
            interpret_d20_position,
            interpret_d24_position,
            interpret_d27_position,
            interpret_d30_position,
            interpret_d60_position,
        ],
    )
    def test_case_insensitive_planet(self, interpret_fn):
        result_lower = interpret_fn("sun", "aries")
        result_upper = interpret_fn("SUN", "aries")
        assert result_lower["found"] == result_upper["found"]
