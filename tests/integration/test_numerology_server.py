"""Tests for the 108-numerology MCP server.

Tests verify that all 8 MCP tools are properly defined, importable,
and return correct results for known inputs.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402

from services.mcp.numerology_server import (  # noqa: E402
    destiny_number,
    lo_shu_grid,
    name_analysis,
    number_compatibility,
    numerology_jyotish_bridge,
    numerology_profile,
    personal_cycles,
    psychic_number,
)

# =====================================================================
# Test: numerology_profile
# =====================================================================


class TestNumerologyProfile:
    """Tests for the numerology_profile MCP tool."""

    def test_basic_profile_without_name(self) -> None:
        result = numerology_profile(1992, 12, 3)
        assert result["success"] is True
        assert "psychic_number" in result
        assert "destiny_number" in result
        assert "personal_year" in result
        assert "lo_shu_grid" in result
        assert "missing_numbers" in result
        assert "psychic_destiny_harmony" in result

    def test_profile_with_name(self) -> None:
        result = numerology_profile(1992, 12, 3, name="Srikanth")
        assert result["success"] is True
        assert result["name_number"] is not None
        assert result["name_planet"] is not None

    def test_psychic_number_value(self) -> None:
        # Day 3 -> psychic 3
        result = numerology_profile(1992, 12, 3)
        assert result["psychic_number"] == 3

    def test_destiny_number_value(self) -> None:
        # 1+9+9+2+1+2+0+3 = 27 -> 2+7 = 9
        result = numerology_profile(1992, 12, 3)
        assert result["destiny_number"] == 9

    def test_psychic_planet_mapping(self) -> None:
        result = numerology_profile(1992, 12, 3)
        # psychic 3 -> jupiter
        assert result["psychic_planet"] == "jupiter"

    def test_invalid_date_returns_error(self) -> None:
        result = numerology_profile(1992, 13, 3)
        assert result["success"] is False
        assert "error" in result

    def test_profile_contains_compound_numbers(self) -> None:
        # Day 28 -> compound 28, psychic 1
        result = numerology_profile(1990, 1, 28)
        assert result["success"] is True
        assert result["compound_psychic"] == 28
        assert result["psychic_number"] == 1


# =====================================================================
# Test: psychic_number
# =====================================================================


class TestPsychicNumber:
    """Tests for the psychic_number MCP tool."""

    def test_single_digit_day(self) -> None:
        result = psychic_number(3)
        assert result["success"] is True
        assert result["psychic_number"] == 3
        assert result["compound_number"] is None
        assert result["ruling_planet"] == "jupiter"

    def test_double_digit_day(self) -> None:
        result = psychic_number(28)
        assert result["success"] is True
        assert result["psychic_number"] == 1  # 2+8=10 -> 1+0=1
        assert result["compound_number"] == 28
        assert result["ruling_planet"] == "sun"

    def test_day_9(self) -> None:
        result = psychic_number(9)
        assert result["success"] is True
        assert result["psychic_number"] == 9
        assert result["ruling_planet"] == "mars"

    def test_day_31(self) -> None:
        result = psychic_number(31)
        assert result["success"] is True
        assert result["psychic_number"] == 4  # 3+1=4
        assert result["compound_number"] == 31

    def test_invalid_day_zero(self) -> None:
        result = psychic_number(0)
        assert result["success"] is False
        assert "error" in result

    def test_invalid_day_32(self) -> None:
        result = psychic_number(32)
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.parametrize(
        "day,expected",
        [
            (1, 1),
            (10, 1),
            (19, 1),
            (28, 1),
            (2, 2),
            (11, 2),
            (20, 2),
            (29, 2),
            (3, 3),
            (12, 3),
            (21, 3),
            (30, 3),
            (4, 4),
            (13, 4),
            (22, 4),
            (31, 4),
            (5, 5),
            (14, 5),
            (23, 5),
            (6, 6),
            (15, 6),
            (24, 6),
            (7, 7),
            (16, 7),
            (25, 7),
            (8, 8),
            (17, 8),
            (26, 8),
            (9, 9),
            (18, 9),
            (27, 9),
        ],
    )
    def test_all_days(self, day: int, expected: int) -> None:
        result = psychic_number(day)
        assert result["success"] is True
        assert result["psychic_number"] == expected


# =====================================================================
# Test: destiny_number
# =====================================================================


class TestDestinyNumber:
    """Tests for the destiny_number MCP tool."""

    def test_basic_calculation(self) -> None:
        result = destiny_number(1992, 12, 3)
        assert result["success"] is True
        assert result["destiny_number"] == 9
        assert result["ruling_planet"] == "mars"

    def test_compound_number_present(self) -> None:
        result = destiny_number(1992, 12, 3)
        assert result["success"] is True
        assert result["compound_number"] is not None

    def test_master_numbers_detected(self) -> None:
        # 29-11-2000: 2+9+1+1+2+0+0+0 = 15 -> not a master number path
        # We just verify master_numbers_found is a list
        result = destiny_number(2000, 11, 29)
        assert result["success"] is True
        assert isinstance(result["master_numbers_found"], list)

    def test_invalid_date(self) -> None:
        result = destiny_number(2000, 2, 30)
        assert result["success"] is False
        assert "error" in result


# =====================================================================
# Test: name_analysis
# =====================================================================


class TestNameAnalysis:
    """Tests for the name_analysis MCP tool."""

    def test_basic_name(self) -> None:
        result = name_analysis("Srikanth")
        assert result["success"] is True
        assert result["full_name"] == "Srikanth"
        assert "chaldean_value" in result
        assert "chaldean_reduced" in result
        assert "pythagorean_value" in result
        assert "pythagorean_reduced" in result
        assert "ruling_planet" in result
        assert "letter_breakdown" in result

    def test_reduced_values_in_range(self) -> None:
        result = name_analysis("Srikanth")
        assert 1 <= result["chaldean_reduced"] <= 9
        assert 1 <= result["pythagorean_reduced"] <= 9

    def test_letter_breakdown_has_entries(self) -> None:
        result = name_analysis("Ram")
        assert result["success"] is True
        breakdown = result["letter_breakdown"]
        assert len(breakdown) == 3
        for entry in breakdown:
            assert "letter" in entry
            assert "value" in entry

    def test_empty_name_returns_error(self) -> None:
        result = name_analysis("123")
        assert result["success"] is False
        assert "error" in result

    def test_name_with_spaces(self) -> None:
        result = name_analysis("Srikanth Kumar")
        assert result["success"] is True
        assert result["full_name"] == "Srikanth Kumar"


# =====================================================================
# Test: personal_cycles
# =====================================================================


class TestPersonalCycles:
    """Tests for the personal_cycles MCP tool."""

    def test_with_explicit_target(self) -> None:
        result = personal_cycles(1992, 12, 3, 2026, 3, 6)
        assert result["success"] is True
        assert "personal_year" in result
        assert "personal_month" in result
        assert "personal_day" in result
        assert "year_planet" in result
        assert "month_planet" in result
        assert "day_planet" in result
        assert "year_meaning" in result
        assert "pinnacle_number" in result
        assert "challenge_number" in result

    def test_values_in_range(self) -> None:
        result = personal_cycles(1992, 12, 3, 2026, 3, 6)
        assert 1 <= result["personal_year"] <= 9
        assert 1 <= result["personal_month"] <= 9
        assert 1 <= result["personal_day"] <= 9

    def test_defaults_to_today(self) -> None:
        result = personal_cycles(1992, 12, 3)
        assert result["success"] is True
        assert "personal_year" in result

    def test_year_meaning_not_empty(self) -> None:
        result = personal_cycles(1992, 12, 3, 2026, 1, 1)
        assert result["success"] is True
        assert len(result["year_meaning"]) > 0

    def test_invalid_birth_date(self) -> None:
        result = personal_cycles(1992, 13, 3, 2026, 3, 6)
        assert result["success"] is False
        assert "error" in result


# =====================================================================
# Test: lo_shu_grid
# =====================================================================


class TestLoShuGrid:
    """Tests for the lo_shu_grid MCP tool."""

    def test_basic_grid(self) -> None:
        result = lo_shu_grid(1992, 12, 3)
        assert result["success"] is True
        assert "grid" in result
        assert "present_numbers" in result
        assert "missing_numbers" in result
        assert "repeated_numbers" in result
        assert "arrows_present" in result
        assert "arrows_missing" in result

    def test_grid_is_3x3(self) -> None:
        result = lo_shu_grid(1992, 12, 3)
        grid = result["grid"]
        assert len(grid) == 3
        for row in grid:
            assert len(row) == 3

    def test_grid_cell_structure(self) -> None:
        result = lo_shu_grid(1992, 12, 3)
        cell = result["grid"][0][0]
        assert "number" in cell
        assert "count" in cell
        assert "present" in cell

    def test_present_and_missing_are_disjoint(self) -> None:
        result = lo_shu_grid(1992, 12, 3)
        present = set(result["present_numbers"])
        missing = set(result["missing_numbers"])
        assert present.isdisjoint(missing)
        assert present | missing == set(range(1, 10))

    def test_dominant_plane(self) -> None:
        result = lo_shu_grid(1992, 12, 3)
        plane = result["dominant_plane"]
        assert plane is None or plane in ("mental", "emotional", "practical")

    def test_invalid_date(self) -> None:
        result = lo_shu_grid(2000, 2, 30)
        assert result["success"] is False
        assert "error" in result


# =====================================================================
# Test: number_compatibility
# =====================================================================


class TestNumberCompatibility:
    """Tests for the number_compatibility MCP tool."""

    def test_excellent_compatibility(self) -> None:
        result = number_compatibility(1, 9)
        assert result["success"] is True
        assert result["score"] == 90
        assert result["nature"] == "excellent"
        assert result["planet_1"] == "sun"
        assert result["planet_2"] == "mars"

    def test_difficult_compatibility(self) -> None:
        result = number_compatibility(1, 8)
        assert result["success"] is True
        assert result["nature"] == "difficult"
        assert result["score"] == 40

    def test_symmetry(self) -> None:
        result_1 = number_compatibility(1, 9)
        result_2 = number_compatibility(9, 1)
        assert result_1["score"] == result_2["score"]
        assert result_1["nature"] == result_2["nature"]

    def test_same_number(self) -> None:
        result = number_compatibility(5, 5)
        assert result["success"] is True
        assert "score" in result

    def test_has_description(self) -> None:
        result = number_compatibility(3, 6)
        assert result["success"] is True
        assert len(result["description"]) > 0

    def test_invalid_number_zero(self) -> None:
        result = number_compatibility(0, 5)
        assert result["success"] is False
        assert "error" in result

    def test_invalid_number_ten(self) -> None:
        result = number_compatibility(10, 3)
        assert result["success"] is False
        assert "error" in result


# =====================================================================
# Test: numerology_jyotish_bridge
# =====================================================================


class TestNumerologyJyotishBridge:
    """Tests for the numerology_jyotish_bridge MCP tool."""

    def test_without_natal_planets(self) -> None:
        result = numerology_jyotish_bridge(1992, 12, 3)
        assert result["success"] is True
        assert "numerology_profile" in result
        assert "jyotish_cross_reference" in result
        profile = result["numerology_profile"]
        assert profile["psychic_number"] == 3
        assert profile["destiny_number"] == 9

    def test_with_name(self) -> None:
        result = numerology_jyotish_bridge(1992, 12, 3, name="Srikanth")
        assert result["success"] is True
        assert result["numerology_profile"]["name_number"] is not None

    def test_with_natal_planets(self) -> None:
        natal = {
            "sun": {"house": 2, "sign": "scorpio", "dignity": "neutral"},
            "jupiter": {"house": 3, "sign": "virgo", "dignity": "debilitated"},
            "mars": {"house": 10, "sign": "cancer", "dignity": "debilitated"},
        }
        result = numerology_jyotish_bridge(1992, 12, 3, natal_planets=natal)
        assert result["success"] is True
        cross = result["jyotish_cross_reference"]
        assert cross["psychic_planet"] == "jupiter"
        assert cross["destiny_planet"] == "mars"
        assert "alignment" in cross
        assert "recommendations" in cross

    def test_cross_reference_alignment_values(self) -> None:
        natal = {
            "jupiter": {"house": 1, "sign": "sagittarius", "dignity": "own_sign"},
            "mars": {"house": 10, "sign": "capricorn", "dignity": "exalted"},
        }
        result = numerology_jyotish_bridge(1992, 12, 3, natal_planets=natal)
        assert result["success"] is True
        cross = result["jyotish_cross_reference"]
        assert cross["alignment"] == "excellent"

    def test_weak_alignment(self) -> None:
        natal = {
            "jupiter": {"house": 6, "sign": "gemini", "dignity": "neutral"},
            "mars": {"house": 8, "sign": "cancer", "dignity": "debilitated"},
        }
        result = numerology_jyotish_bridge(1992, 12, 3, natal_planets=natal)
        assert result["success"] is True
        cross = result["jyotish_cross_reference"]
        assert cross["alignment"] == "weak"

    def test_invalid_date(self) -> None:
        result = numerology_jyotish_bridge(2000, 13, 1)
        assert result["success"] is False
        assert "error" in result


# =====================================================================
# Test: All tools importable and callable
# =====================================================================


class TestToolsImportable:
    """Verify all 8 MCP tools are importable and return dict results."""

    def test_all_tools_exist(self) -> None:
        from services.mcp.numerology_server import mcp as numerology_mcp

        assert numerology_mcp.name == "108-numerology"

    def test_numerology_profile_callable(self) -> None:
        assert callable(numerology_profile)

    def test_psychic_number_callable(self) -> None:
        assert callable(psychic_number)

    def test_destiny_number_callable(self) -> None:
        assert callable(destiny_number)

    def test_name_analysis_callable(self) -> None:
        assert callable(name_analysis)

    def test_personal_cycles_callable(self) -> None:
        assert callable(personal_cycles)

    def test_lo_shu_grid_callable(self) -> None:
        assert callable(lo_shu_grid)

    def test_number_compatibility_callable(self) -> None:
        assert callable(number_compatibility)

    def test_numerology_jyotish_bridge_callable(self) -> None:
        assert callable(numerology_jyotish_bridge)
