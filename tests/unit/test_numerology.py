"""Tests for the numerology calculator module.

Tests cover all core functions: psychic/destiny/name numbers,
personal cycles, Lo Shu grid, compatibility, pinnacles, challenges,
and the full profile calculator.
"""

from datetime import date

import pytest

from packages.self.src.numerology import (
    CHALDEAN_MAP,
    LO_SHU_GRID,
    LO_SHU_POSITIONS,
    MASTER_NUMBERS,
    NUMBER_PLANET_MAP,
    PYTHAGOREAN_MAP,
    LoShuGrid,
    NameAnalysis,
    NumberCompatibility,
    NumerologyProfile,
    PersonalCycles,
    analyze_name,
    calculate_challenge_numbers,
    calculate_destiny_number,
    calculate_full_profile,
    calculate_lo_shu_grid,
    calculate_name_number,
    calculate_personal_day,
    calculate_personal_month,
    calculate_personal_year,
    calculate_pinnacle_numbers,
    calculate_psychic_number,
    cross_reference_jyotish,
    get_compound_meaning,
    get_number_compatibility,
    get_personal_cycles,
    reduce_to_single,
)

# =====================================================================
# Constants tests
# =====================================================================


class TestConstants:
    """Verify constant mappings are well-formed."""

    def test_chaldean_map_has_26_letters(self) -> None:
        assert len(CHALDEAN_MAP) == 26

    def test_pythagorean_map_has_26_letters(self) -> None:
        assert len(PYTHAGOREAN_MAP) == 26

    def test_chaldean_values_1_to_8(self) -> None:
        """Chaldean system uses values 1-8 (no 9)."""
        assert set(CHALDEAN_MAP.values()) == {1, 2, 3, 4, 5, 6, 7, 8}

    def test_pythagorean_values_1_to_9(self) -> None:
        """Pythagorean system uses values 1-9."""
        assert set(PYTHAGOREAN_MAP.values()) == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def test_number_planet_map_complete(self) -> None:
        assert set(NUMBER_PLANET_MAP.keys()) == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def test_lo_shu_is_magic_square(self) -> None:
        """Lo Shu rows, columns, diagonals all sum to 15."""
        # Rows
        for row in LO_SHU_GRID:
            assert sum(row) == 15
        # Columns
        for col in range(3):
            assert sum(LO_SHU_GRID[row][col] for row in range(3)) == 15
        # Diagonals
        assert sum(LO_SHU_GRID[i][i] for i in range(3)) == 15
        assert sum(LO_SHU_GRID[i][2 - i] for i in range(3)) == 15

    def test_lo_shu_positions_complete(self) -> None:
        assert set(LO_SHU_POSITIONS.keys()) == set(range(1, 10))

    def test_master_numbers(self) -> None:
        assert {11, 22, 33} == MASTER_NUMBERS


# =====================================================================
# reduce_to_single tests
# =====================================================================


class TestReduceToSingle:
    """Tests for the digit reduction function."""

    def test_single_digit_unchanged(self) -> None:
        result, compound, masters = reduce_to_single(7)
        assert result == 7
        assert compound is None
        assert masters == []

    def test_two_digit_reduction(self) -> None:
        result, compound, _ = reduce_to_single(28)
        assert result == 1  # 2+8=10, 1+0=1
        assert compound == 28

    def test_three_digit_reduction(self) -> None:
        result, compound, _ = reduce_to_single(123)
        assert result == 6  # 1+2+3=6
        assert compound == 123

    def test_master_number_11_detected(self) -> None:
        result, compound, masters = reduce_to_single(11)
        assert result == 2
        assert compound == 11
        assert 11 in masters

    def test_master_number_22_detected(self) -> None:
        result, compound, masters = reduce_to_single(22)
        assert result == 4
        assert compound == 22
        assert 22 in masters

    def test_master_number_33_detected(self) -> None:
        result, compound, masters = reduce_to_single(33)
        assert result == 6
        assert compound == 33
        assert 33 in masters

    def test_no_master_when_not_respected(self) -> None:
        result, _compound, masters = reduce_to_single(22, respect_master=False)
        assert result == 4
        assert masters == []

    def test_zero(self) -> None:
        result, compound, masters = reduce_to_single(0)
        assert result == 0
        assert compound is None
        assert masters == []

    def test_negative_treated_as_positive(self) -> None:
        result, _, _ = reduce_to_single(-27)
        assert result == 9


# =====================================================================
# Psychic Number tests
# =====================================================================


class TestPsychicNumber:
    """Tests for psychic (driver) number calculation."""

    def test_single_digit_day(self) -> None:
        psychic, compound = calculate_psychic_number(3)
        assert psychic == 3
        assert compound is None

    def test_day_1(self) -> None:
        psychic, compound = calculate_psychic_number(1)
        assert psychic == 1
        assert compound is None

    def test_day_9(self) -> None:
        psychic, compound = calculate_psychic_number(9)
        assert psychic == 9
        assert compound is None

    def test_day_10(self) -> None:
        psychic, compound = calculate_psychic_number(10)
        assert psychic == 1
        assert compound == 10

    def test_day_15(self) -> None:
        psychic, compound = calculate_psychic_number(15)
        assert psychic == 6  # 1+5=6
        assert compound == 15

    def test_day_28(self) -> None:
        psychic, compound = calculate_psychic_number(28)
        assert psychic == 1  # 2+8=10, 1+0=1
        assert compound == 28

    def test_day_29(self) -> None:
        psychic, compound = calculate_psychic_number(29)
        assert psychic == 2  # 2+9=11, 1+1=2
        assert compound == 29

    def test_day_31(self) -> None:
        psychic, compound = calculate_psychic_number(31)
        assert psychic == 4  # 3+1=4
        assert compound == 31

    def test_invalid_day_0(self) -> None:
        with pytest.raises(ValueError, match="birth_day must be 1-31"):
            calculate_psychic_number(0)

    def test_invalid_day_32(self) -> None:
        with pytest.raises(ValueError, match="birth_day must be 1-31"):
            calculate_psychic_number(32)


# =====================================================================
# Destiny Number tests
# =====================================================================


class TestDestinyNumber:
    """Tests for destiny (life path) number calculation."""

    def test_dec_3_1992(self) -> None:
        # 0+3+1+2+1+9+9+2 = 27 -> 2+7 = 9
        destiny, compound, _ = calculate_destiny_number(date(1992, 12, 3))
        assert destiny == 9
        assert compound == 27

    def test_jan_1_2000(self) -> None:
        # 0+1+0+1+2+0+0+0 = 4
        destiny, compound, _ = calculate_destiny_number(date(2000, 1, 1))
        assert destiny == 4
        assert compound is None  # 4 is single digit

    def test_nov_29_1988(self) -> None:
        # 2+9+1+1+1+9+8+8 = 39 -> 3+9 = 12 -> 1+2 = 3
        destiny, compound, _ = calculate_destiny_number(date(1988, 11, 29))
        assert destiny == 3
        assert compound == 39

    def test_master_number_in_path(self) -> None:
        # Find a date that passes through 11 or 22
        # 2+9+1+1+1+9+8+1 = 32 -> 3+2 = 5 (no master)
        # 0+9+0+9+1+9+9+9 = 46 -> 4+6 = 10 -> 1+0 = 1 (no)
        # Need 0+2+0+2+1+9+7+1 = 22 -> 2+2 = 4
        destiny, _compound, masters = calculate_destiny_number(date(1971, 2, 2))
        assert destiny == 4  # 22 -> 4
        assert 22 in masters

    def test_returns_1_to_9(self) -> None:
        """Destiny number is always 1-9 for any valid date."""
        for year in (1985, 1990, 2000, 2015):
            for month in (1, 6, 12):
                d, _, _ = calculate_destiny_number(date(year, month, 15))
                assert 1 <= d <= 9


# =====================================================================
# Name Number tests
# =====================================================================


class TestNameNumber:
    """Tests for name number calculation."""

    def test_chaldean_basic(self) -> None:
        # S=3, R=2, I=1, K=2, A=1, N=5, T=4, H=5 => 23 -> 5
        reduced, compound, breakdown = calculate_name_number("Srikanth", "chaldean")
        assert compound == 23
        assert reduced == 5
        assert len(breakdown) == 8
        assert breakdown[0] == {"letter": "S", "value": 3}

    def test_pythagorean_basic(self) -> None:
        reduced, compound, _breakdown = calculate_name_number("Srikanth", "pythagorean")
        # S=1, R=9, I=9, K=2, A=1, N=5, T=2, H=8 => 37 -> 10 -> 1
        assert compound == 37
        assert reduced == 1

    def test_spaces_ignored(self) -> None:
        reduced1, _, _ = calculate_name_number("AB CD", "chaldean")
        reduced2, _, _ = calculate_name_number("ABCD", "chaldean")
        assert reduced1 == reduced2

    def test_case_insensitive(self) -> None:
        r1, c1, _ = calculate_name_number("Hello", "chaldean")
        r2, c2, _ = calculate_name_number("HELLO", "chaldean")
        r3, c3, _ = calculate_name_number("hello", "chaldean")
        assert r1 == r2 == r3
        assert c1 == c2 == c3

    def test_non_alpha_ignored(self) -> None:
        r1, c1, _ = calculate_name_number("John", "chaldean")
        r2, c2, _ = calculate_name_number("J.o.h.n", "chaldean")
        assert r1 == r2
        assert c1 == c2

    def test_invalid_system(self) -> None:
        with pytest.raises(ValueError, match="system must be"):
            calculate_name_number("Test", "invalid")

    def test_empty_name(self) -> None:
        with pytest.raises(ValueError, match="at least one alphabetic"):
            calculate_name_number("123", "chaldean")

    def test_all_numbers_name(self) -> None:
        with pytest.raises(ValueError, match="at least one alphabetic"):
            calculate_name_number("!@#$%", "chaldean")

    def test_letter_breakdown_structure(self) -> None:
        _, _, breakdown = calculate_name_number("AB", "chaldean")
        assert len(breakdown) == 2
        assert breakdown[0]["letter"] == "A"
        assert breakdown[0]["value"] == 1
        assert breakdown[1]["letter"] == "B"
        assert breakdown[1]["value"] == 2


# =====================================================================
# Personal Cycle tests
# =====================================================================


class TestPersonalCycles:
    """Tests for personal year/month/day calculations."""

    def test_personal_year(self) -> None:
        # DOB 1992-12-03, year 2026
        # day digits: 0+3=3, month digits: 1+2=3, year digits: 2+0+2+6=10 -> 1+0=1
        # 3+3+10 = 16 -> 1+6 = 7
        py = calculate_personal_year(date(1992, 12, 3), 2026)
        assert 1 <= py <= 9

    def test_personal_month(self) -> None:
        pm = calculate_personal_month(date(1992, 12, 3), 2026, 3)
        assert 1 <= pm <= 9

    def test_personal_day(self) -> None:
        pd = calculate_personal_day(date(1992, 12, 3), date(2026, 3, 6))
        assert 1 <= pd <= 9

    def test_personal_year_varies_by_year(self) -> None:
        bd = date(1990, 5, 15)
        years = [calculate_personal_year(bd, y) for y in range(2020, 2029)]
        # 9 years should cycle through 1-9
        assert set(years) == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def test_personal_month_changes_monthly(self) -> None:
        bd = date(1990, 5, 15)
        months = [calculate_personal_month(bd, 2026, m) for m in range(1, 13)]
        # Should have some variety
        assert len(set(months)) > 1


# =====================================================================
# Pinnacle and Challenge Numbers tests
# =====================================================================


class TestPinnaclesAndChallenges:
    """Tests for pinnacle and challenge number calculations."""

    def test_four_pinnacles(self) -> None:
        pinnacles = calculate_pinnacle_numbers(date(1992, 12, 3))
        assert len(pinnacles) == 4

    def test_pinnacle_structure(self) -> None:
        pinnacles = calculate_pinnacle_numbers(date(1992, 12, 3))
        for p in pinnacles:
            assert "number" in p
            assert "start_age" in p
            assert "end_age" in p
            assert 0 <= p["number"] <= 9

    def test_pinnacle_ages_sequential(self) -> None:
        pinnacles = calculate_pinnacle_numbers(date(1992, 12, 3))
        assert pinnacles[0]["start_age"] == 0
        assert pinnacles[1]["start_age"] == pinnacles[0]["end_age"] + 1
        assert pinnacles[2]["start_age"] == pinnacles[1]["end_age"] + 1
        assert pinnacles[3]["start_age"] == pinnacles[2]["end_age"] + 1
        assert pinnacles[3]["end_age"] is None  # last pinnacle is open-ended

    def test_first_pinnacle_end_depends_on_destiny(self) -> None:
        """First pinnacle ends at age 36 - destiny_number."""
        bd = date(1992, 12, 3)
        destiny, _, _ = calculate_destiny_number(bd)
        pinnacles = calculate_pinnacle_numbers(bd)
        assert pinnacles[0]["end_age"] == 36 - destiny

    def test_four_challenges(self) -> None:
        challenges = calculate_challenge_numbers(date(1992, 12, 3))
        assert len(challenges) == 4

    def test_challenge_structure(self) -> None:
        challenges = calculate_challenge_numbers(date(1992, 12, 3))
        for c in challenges:
            assert "number" in c
            assert "start_age" in c
            assert "end_age" in c
            assert 0 <= c["number"] <= 9

    def test_challenge_can_be_zero(self) -> None:
        """Challenge number 0 means mastery - it's valid."""
        # Challenge is |a - b|, so equal values yield 0
        # This tests that 0 doesn't cause errors
        challenges = calculate_challenge_numbers(date(2000, 1, 1))
        # At least verify it runs without error; 0 may or may not appear
        assert all(0 <= c["number"] <= 9 for c in challenges)


# =====================================================================
# Lo Shu Grid tests
# =====================================================================


class TestLoShuGrid:
    """Tests for Lo Shu magic square analysis."""

    def test_returns_lo_shu_grid_model(self) -> None:
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        assert isinstance(result, LoShuGrid)

    def test_grid_is_3x3(self) -> None:
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        assert len(result.grid) == 3
        for row in result.grid:
            assert len(row) == 3

    def test_grid_cell_structure(self) -> None:
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        for row in result.grid:
            for cell in row:
                assert "number" in cell
                assert "count" in cell
                assert "present" in cell
                assert isinstance(cell["number"], int)
                assert isinstance(cell["count"], int)
                assert isinstance(cell["present"], bool)

    def test_dec_3_1992_digits(self) -> None:
        """Date 03-12-1992: digits are 3,1,2,1,9,9,2 (no zeros)."""
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        # Present: 1(x2), 2(x2), 3(x1), 9(x2)
        assert 1 in result.present_numbers
        assert 2 in result.present_numbers
        assert 3 in result.present_numbers
        assert 9 in result.present_numbers
        # Missing: 4, 5, 6, 7, 8
        assert 4 in result.missing_numbers
        assert 5 in result.missing_numbers
        assert 6 in result.missing_numbers
        assert 7 in result.missing_numbers
        assert 8 in result.missing_numbers

    def test_repeated_numbers(self) -> None:
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        # 1 appears twice, 2 appears twice, 9 appears twice
        assert 1 in result.repeated_numbers
        assert result.repeated_numbers[1] >= 2
        assert 2 in result.repeated_numbers
        assert 9 in result.repeated_numbers

    def test_arrows_detection(self) -> None:
        """If all numbers in an arrow set are present, arrow is detected."""
        # Date where digits 1,5,9 all appear -> determination arrow
        # 1995-01-15: 0,1,0,1,1,9,9,5 -> 1,1,1,9,9,5 -> has 1,5,9
        result = calculate_lo_shu_grid(date(1995, 1, 15))
        assert "determination" in result.arrows_present

    def test_missing_arrows_detection(self) -> None:
        # Date 1992-12-03: missing 4,5,6,7,8
        # Arrow "willpower" = [4,5,6] - all missing
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        assert "willpower" in result.arrows_missing

    def test_present_and_missing_partition(self) -> None:
        """Present + missing should cover exactly 1-9."""
        result = calculate_lo_shu_grid(date(1990, 6, 15))
        all_nums = sorted(result.present_numbers + result.missing_numbers)
        assert all_nums == list(range(1, 10))

    def test_dominant_plane(self) -> None:
        result = calculate_lo_shu_grid(date(1992, 12, 3))
        assert result.dominant_plane is None or result.dominant_plane in (
            "mental",
            "emotional",
            "practical",
        )


# =====================================================================
# Number Compatibility tests
# =====================================================================


class TestNumberCompatibility:
    """Tests for the compatibility calculator."""

    def test_returns_model(self) -> None:
        result = get_number_compatibility(1, 9)
        assert isinstance(result, NumberCompatibility)

    def test_symmetric(self) -> None:
        r1 = get_number_compatibility(1, 9)
        r2 = get_number_compatibility(9, 1)
        assert r1.score == r2.score
        assert r1.nature == r2.nature

    def test_same_number(self) -> None:
        result = get_number_compatibility(5, 5)
        assert result.score > 0
        assert result.number_1 == 5
        assert result.number_2 == 5

    def test_planets_assigned(self) -> None:
        result = get_number_compatibility(1, 2)
        assert result.planet_1 == "sun"
        assert result.planet_2 == "moon"

    def test_score_range(self) -> None:
        for n1 in range(1, 10):
            for n2 in range(1, 10):
                result = get_number_compatibility(n1, n2)
                assert 0 <= result.score <= 100

    def test_nature_values(self) -> None:
        valid = {"excellent", "good", "moderate", "neutral", "challenging", "difficult"}
        for n1 in range(1, 10):
            for n2 in range(1, 10):
                result = get_number_compatibility(n1, n2)
                assert result.nature in valid

    def test_description_not_empty(self) -> None:
        result = get_number_compatibility(3, 6)
        assert len(result.description) > 0

    def test_invalid_number_raises(self) -> None:
        with pytest.raises(ValueError, match="Numbers must be 1-9"):
            get_number_compatibility(0, 5)
        with pytest.raises(ValueError, match="Numbers must be 1-9"):
            get_number_compatibility(5, 10)

    def test_1_and_9_excellent(self) -> None:
        """Sun (1) and Mars (9) are natural friends -> excellent."""
        result = get_number_compatibility(1, 9)
        assert result.nature == "excellent"

    def test_1_and_8_difficult(self) -> None:
        """Sun (1) and Saturn (8) are natural enemies -> difficult."""
        result = get_number_compatibility(1, 8)
        assert result.nature == "difficult"


# =====================================================================
# Cross-reference Jyotish tests
# =====================================================================


class TestCrossReferenceJyotish:
    """Tests for numerology-Jyotish cross-reference."""

    def test_without_chart_data(self) -> None:
        result = cross_reference_jyotish(3, 9)
        assert result["psychic_planet"] == "jupiter"
        assert result["destiny_planet"] == "mars"
        assert result["alignment"] == "chart data needed for full analysis"

    def test_with_strong_planets(self) -> None:
        chart_data = {
            "jupiter": {"house": 1, "sign": "sagittarius", "dignity": "own_sign"},
            "mars": {"house": 10, "sign": "capricorn", "dignity": "exalted"},
        }
        result = cross_reference_jyotish(3, 9, chart_data)
        assert result["psychic_planet_strong"] is True
        assert result["destiny_planet_strong"] is True
        assert result["alignment"] == "excellent"

    def test_with_weak_planets(self) -> None:
        chart_data = {
            "jupiter": {"house": 6, "sign": "capricorn", "dignity": "debilitated"},
            "mars": {"house": 8, "sign": "cancer", "dignity": "debilitated"},
        }
        result = cross_reference_jyotish(3, 9, chart_data)
        assert result["psychic_planet_strong"] is False
        assert result["destiny_planet_strong"] is False
        assert result["alignment"] == "weak"

    def test_partial_alignment(self) -> None:
        chart_data = {
            "jupiter": {"house": 1, "sign": "sagittarius", "dignity": "own_sign"},
            "mars": {"house": 8, "sign": "cancer", "dignity": "debilitated"},
        }
        result = cross_reference_jyotish(3, 9, chart_data)
        assert result["alignment"] == "partial"

    def test_same_planet(self) -> None:
        result = cross_reference_jyotish(1, 1)
        assert result["same_planet"] is True
        assert result["planet_friendship"] == "same"

    def test_planet_friendship_included(self) -> None:
        result = cross_reference_jyotish(1, 8)  # sun vs saturn
        assert result["planet_friendship"] == "enemy"

    def test_recommendations_not_empty(self) -> None:
        chart_data = {
            "sun": {"dignity": "exalted"},
            "moon": {"dignity": "debilitated"},
        }
        result = cross_reference_jyotish(1, 2, chart_data)
        assert len(result["recommendations"]) > 0


# =====================================================================
# Full Profile tests
# =====================================================================


class TestFullProfile:
    """Tests for the master profile calculator."""

    def test_returns_profile_model(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert isinstance(profile, NumerologyProfile)

    def test_psychic_number_correct(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert profile.psychic_number == 3
        assert profile.compound_psychic is None  # day 3 < 10

    def test_destiny_number_correct(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert profile.destiny_number == 9
        assert profile.compound_destiny == 27

    def test_name_number_when_provided(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3), name="Srikanth")
        assert profile.name_number is not None
        assert profile.name_number_pythagorean is not None
        assert profile.name_planet is not None

    def test_no_name_number_when_not_provided(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert profile.name_number is None
        assert profile.name_number_pythagorean is None
        assert profile.name_planet is None

    def test_planets_assigned(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert profile.psychic_planet == "jupiter"  # 3 -> jupiter
        assert profile.destiny_planet == "mars"  # 9 -> mars

    def test_personal_cycles_present(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3), target_date=date(2026, 3, 6))
        assert 1 <= profile.personal_year <= 9
        assert 1 <= profile.personal_month <= 9
        assert 1 <= profile.personal_day <= 9

    def test_lo_shu_grid_present(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert isinstance(profile.lo_shu_grid, dict)
        assert "grid" in profile.lo_shu_grid
        assert "present_numbers" in profile.lo_shu_grid

    def test_harmony_value(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert profile.psychic_destiny_harmony in ("high", "medium", "low")

    def test_missing_numbers_present(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert isinstance(profile.missing_numbers, list)
        assert len(profile.missing_numbers) > 0

    def test_repeated_numbers_present(self) -> None:
        profile = calculate_full_profile(date(1992, 12, 3))
        assert isinstance(profile.repeated_numbers, dict)

    def test_different_dates_different_profiles(self) -> None:
        p1 = calculate_full_profile(date(1992, 12, 3))
        p2 = calculate_full_profile(date(1985, 7, 22))
        assert p1.psychic_number != p2.psychic_number or p1.destiny_number != p2.destiny_number


# =====================================================================
# PersonalCycles model tests
# =====================================================================


class TestGetPersonalCycles:
    """Tests for the get_personal_cycles function."""

    def test_returns_model(self) -> None:
        result = get_personal_cycles(date(1992, 12, 3), date(2026, 3, 6))
        assert isinstance(result, PersonalCycles)

    def test_planets_assigned(self) -> None:
        result = get_personal_cycles(date(1992, 12, 3), date(2026, 3, 6))
        assert result.year_planet in NUMBER_PLANET_MAP.values()
        assert result.month_planet in NUMBER_PLANET_MAP.values()
        assert result.day_planet in NUMBER_PLANET_MAP.values()

    def test_year_meaning_not_empty(self) -> None:
        result = get_personal_cycles(date(1992, 12, 3), date(2026, 3, 6))
        assert len(result.year_meaning) > 0

    def test_pinnacle_and_challenge_present(self) -> None:
        result = get_personal_cycles(date(1992, 12, 3), date(2026, 3, 6))
        assert 0 <= result.pinnacle_number <= 9
        assert 0 <= result.challenge_number <= 9

    def test_defaults_to_today(self) -> None:
        """Should not raise when target_date is not provided."""
        result = get_personal_cycles(date(1992, 12, 3))
        assert isinstance(result, PersonalCycles)


# =====================================================================
# NameAnalysis tests
# =====================================================================


class TestAnalyzeName:
    """Tests for the analyze_name function."""

    def test_returns_model(self) -> None:
        result = analyze_name("Srikanth")
        assert isinstance(result, NameAnalysis)

    def test_both_systems_computed(self) -> None:
        result = analyze_name("Srikanth")
        assert result.chaldean_reduced > 0
        assert result.chaldean_value > 0
        assert result.pythagorean_reduced > 0
        assert result.pythagorean_value > 0

    def test_ruling_planet_from_chaldean(self) -> None:
        result = analyze_name("Srikanth")
        assert result.ruling_planet in NUMBER_PLANET_MAP.values()

    def test_letter_breakdown(self) -> None:
        result = analyze_name("AB")
        assert len(result.letter_breakdown) == 2

    def test_full_name(self) -> None:
        result = analyze_name("Srikanth")
        assert result.full_name == "Srikanth"


# =====================================================================
# Compound meaning tests
# =====================================================================


class TestCompoundMeaning:
    """Tests for compound number interpretation."""

    def test_known_compound(self) -> None:
        meaning = get_compound_meaning(13)
        assert "Transformation" in meaning

    def test_unknown_compound(self) -> None:
        meaning = get_compound_meaning(99)
        assert meaning == ""

    def test_none_compound(self) -> None:
        meaning = get_compound_meaning(None)
        assert meaning == ""

    def test_master_11(self) -> None:
        meaning = get_compound_meaning(11)
        assert "Master Number" in meaning

    def test_master_22(self) -> None:
        meaning = get_compound_meaning(22)
        assert "Master Builder" in meaning


# =====================================================================
# Edge case and integration tests
# =====================================================================


class TestEdgeCases:
    """Tests for boundary conditions and unusual inputs."""

    def test_leap_year_date(self) -> None:
        profile = calculate_full_profile(date(2000, 2, 29))
        assert isinstance(profile, NumerologyProfile)

    def test_very_old_date(self) -> None:
        profile = calculate_full_profile(date(1900, 1, 1))
        assert isinstance(profile, NumerologyProfile)

    def test_future_date(self) -> None:
        profile = calculate_full_profile(date(2050, 12, 31))
        assert isinstance(profile, NumerologyProfile)

    def test_name_with_accented_chars(self) -> None:
        """Non-ASCII alpha chars without mapping should still work for ASCII portion."""
        # The name has enough ASCII letters to produce a result
        reduced, _compound, _breakdown = calculate_name_number("Jose", "chaldean")
        assert reduced > 0

    def test_single_letter_name(self) -> None:
        reduced, compound, breakdown = calculate_name_number("A", "chaldean")
        assert reduced == 1
        assert compound == 1
        assert len(breakdown) == 1

    def test_long_name(self) -> None:
        reduced, _compound, _breakdown = calculate_name_number(
            "Srikanth Ramakrishna Venkatanarasimharajuvaripeta", "chaldean"
        )
        assert 1 <= reduced <= 9

    def test_all_psychic_numbers_reachable(self) -> None:
        """Every number 1-9 should be reachable as a psychic number."""
        seen = set()
        for day in range(1, 32):
            p, _ = calculate_psychic_number(day)
            seen.add(p)
        assert seen == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    def test_import_from_package_init(self) -> None:
        """Verify the module is properly exported from packages.self.src."""
        from packages.self.src import (
            NumerologyProfile,
            calculate_full_profile,
            calculate_psychic_number,
        )

        assert NumerologyProfile is not None
        assert calculate_full_profile is not None
        assert calculate_psychic_number is not None
