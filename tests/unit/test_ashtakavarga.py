"""Tests for Ashtakavarga transit scoring and interpretation module."""

import pytest

from packages.self.src.ashtakavarga import (
    get_transit_strength_modifier,
    interpret_ashtakavarga_score,
)


class TestInterpretAshtakavargaScore:
    def test_very_strong(self):
        assert interpret_ashtakavarga_score(7, 8) == "very_strong"
        assert interpret_ashtakavarga_score(8, 8) == "very_strong"

    def test_strong(self):
        assert interpret_ashtakavarga_score(5, 8) == "strong"

    def test_moderate(self):
        assert interpret_ashtakavarga_score(4, 8) == "moderate"

    def test_weak(self):
        assert interpret_ashtakavarga_score(2, 8) == "weak"

    def test_very_weak(self):
        assert interpret_ashtakavarga_score(1, 8) == "very_weak"
        assert interpret_ashtakavarga_score(0, 8) == "very_weak"

    def test_zero_max_returns_unknown(self):
        assert interpret_ashtakavarga_score(5, 0) == "unknown"

    def test_sav_interpretation(self):
        # SAV max is 56
        assert interpret_ashtakavarga_score(45, 56) == "very_strong"
        assert interpret_ashtakavarga_score(35, 56) == "strong"
        assert interpret_ashtakavarga_score(25, 56) == "moderate"
        assert interpret_ashtakavarga_score(15, 56) == "weak"  # 15/56 = 26.8%
        assert interpret_ashtakavarga_score(5, 56) == "very_weak"  # 5/56 = 8.9%


class TestTransitStrengthModifier:
    def test_max_score_gives_1_5(self):
        modifier = get_transit_strength_modifier(8, 8)
        assert modifier == 1.5

    def test_zero_score_gives_0_5(self):
        modifier = get_transit_strength_modifier(0, 8)
        assert modifier == 0.5

    def test_mid_score_gives_1_0(self):
        modifier = get_transit_strength_modifier(4, 8)
        assert modifier == 1.0

    def test_returns_within_range(self):
        for score in range(9):
            modifier = get_transit_strength_modifier(score, 8)
            assert 0.5 <= modifier <= 1.5, f"score={score} gave modifier={modifier}"

    def test_zero_max_returns_neutral(self):
        modifier = get_transit_strength_modifier(5, 0)
        assert modifier == 1.0

    def test_proportional(self):
        # Higher score = higher modifier
        m1 = get_transit_strength_modifier(2, 8)
        m2 = get_transit_strength_modifier(6, 8)
        assert m2 > m1


class TestTransitAshtakavargaScore:
    def test_invalid_sign_raises(self):
        from packages.core.src.constants import Planet
        from packages.self.src.ashtakavarga import get_transit_ashtakavarga_score

        # We can't easily create a full BirthChart here, so just test validation
        with pytest.raises(ValueError, match="transit_sign must be 0-11"):
            get_transit_ashtakavarga_score(Planet.SUN, 12, None)  # type: ignore[arg-type]

        with pytest.raises(ValueError, match="transit_sign must be 0-11"):
            get_transit_ashtakavarga_score(Planet.SUN, -1, None)  # type: ignore[arg-type]

    def test_invalid_sav_sign_raises(self):
        from packages.self.src.ashtakavarga import get_sarvashtakavarga_score

        with pytest.raises(ValueError, match="transit_sign must be 0-11"):
            get_sarvashtakavarga_score(99, None)  # type: ignore[arg-type]
