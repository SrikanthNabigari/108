"""Tests for Vimshopaka (divisional strength) calculations."""

import pytest

from packages.cosmos.src.divisional import (
    DIGNITY_SCORES,
    VARGA_SCHEMES,
    calculate_vimshopaka_bala,
    get_all_vimshopaka,
    get_planet_dignity_in_sign,
)


class TestPlanetDignity:
    """Tests for get_planet_dignity_in_sign function."""

    def test_dignity_sun_in_aries(self):
        """Sun should be exalted in Aries."""
        result = get_planet_dignity_in_sign("sun", "aries")
        assert result == "exalted"

    def test_dignity_sun_in_libra(self):
        """Sun should be debilitated in Libra."""
        result = get_planet_dignity_in_sign("sun", "libra")
        assert result == "debilitated"

    def test_dignity_sun_in_leo(self):
        """Sun should be in own sign or moolatrikona in Leo."""
        result = get_planet_dignity_in_sign("sun", "leo")
        assert result in ["own", "moolatrikona"]

    def test_dignity_moon_in_taurus(self):
        """Moon should be exalted in Taurus."""
        result = get_planet_dignity_in_sign("moon", "taurus")
        assert result == "exalted"

    def test_dignity_moon_in_scorpio(self):
        """Moon should be debilitated in Scorpio."""
        result = get_planet_dignity_in_sign("moon", "scorpio")
        assert result == "debilitated"

    def test_dignity_moon_in_cancer(self):
        """Moon should be in own sign in Cancer."""
        result = get_planet_dignity_in_sign("moon", "cancer")
        assert result == "own"

    def test_dignity_mars_in_capricorn(self):
        """Mars should be exalted in Capricorn."""
        result = get_planet_dignity_in_sign("mars", "capricorn")
        assert result == "exalted"

    def test_dignity_mars_in_cancer(self):
        """Mars should be debilitated in Cancer."""
        result = get_planet_dignity_in_sign("mars", "cancer")
        assert result == "debilitated"

    def test_dignity_mars_in_aries(self):
        """Mars should be in own/moolatrikona sign in Aries."""
        result = get_planet_dignity_in_sign("mars", "aries")
        assert result in ["own", "moolatrikona"]

    def test_dignity_mars_in_scorpio(self):
        """Mars should be in own sign in Scorpio."""
        result = get_planet_dignity_in_sign("mars", "scorpio")
        assert result == "own"

    def test_dignity_mercury_in_virgo(self):
        """Mercury should be exalted or own/moolatrikona in Virgo."""
        result = get_planet_dignity_in_sign("mercury", "virgo")
        assert result in ["exalted", "own", "moolatrikona"]

    def test_dignity_mercury_in_pisces(self):
        """Mercury should be debilitated in Pisces."""
        result = get_planet_dignity_in_sign("mercury", "pisces")
        assert result == "debilitated"

    def test_dignity_jupiter_in_cancer(self):
        """Jupiter should be exalted in Cancer."""
        result = get_planet_dignity_in_sign("jupiter", "cancer")
        assert result == "exalted"

    def test_dignity_jupiter_in_capricorn(self):
        """Jupiter should be debilitated in Capricorn."""
        result = get_planet_dignity_in_sign("jupiter", "capricorn")
        assert result == "debilitated"

    def test_dignity_venus_in_pisces(self):
        """Venus should be exalted in Pisces."""
        result = get_planet_dignity_in_sign("venus", "pisces")
        assert result == "exalted"

    def test_dignity_venus_in_virgo(self):
        """Venus should be debilitated in Virgo."""
        result = get_planet_dignity_in_sign("venus", "virgo")
        assert result == "debilitated"

    def test_dignity_saturn_in_libra(self):
        """Saturn should be exalted in Libra."""
        result = get_planet_dignity_in_sign("saturn", "libra")
        assert result == "exalted"

    def test_dignity_saturn_in_aries(self):
        """Saturn should be debilitated in Aries."""
        result = get_planet_dignity_in_sign("saturn", "aries")
        assert result == "debilitated"

    def test_dignity_friendly_sign(self):
        """Planet should show 'friend' dignity in friend's sign."""
        # Sun is friends with Mars, Mars rules Aries
        result = get_planet_dignity_in_sign("moon", "gemini")
        # Moon is friends with Mercury, Mercury rules Gemini
        assert result == "friend"

    def test_dignity_enemy_sign(self):
        """Planet should show 'enemy' dignity in enemy's sign."""
        # Saturn is enemy of Sun, Sun rules Leo
        result = get_planet_dignity_in_sign("saturn", "leo")
        assert result == "enemy"

    def test_dignity_neutral_sign(self):
        """Planet should show 'neutral' dignity in neutral planet's sign."""
        # Moon considers Mars neutral, Mars rules Aries
        result = get_planet_dignity_in_sign("moon", "aries")
        assert result == "neutral"

    def test_dignity_rahu(self):
        """Rahu dignity lookup should work."""
        result = get_planet_dignity_in_sign("rahu", "taurus")
        assert result == "exalted"

    def test_dignity_ketu(self):
        """Ketu dignity lookup should work."""
        result = get_planet_dignity_in_sign("ketu", "scorpio")
        assert result == "exalted"


class TestVimshopakaBala:
    """Tests for calculate_vimshopaka_bala function."""

    def test_vimshopaka_shad_varga(self):
        """Test Vimshopaka calculation with shad_varga scheme."""
        result = calculate_vimshopaka_bala("sun", 10.0, "shad_varga")

        # Check structure
        assert "total_points" in result
        assert "max_points" in result
        assert "percentage" in result
        assert "category" in result
        assert "varga_details" in result

        # Check varga count
        assert len(result["varga_details"]) == 6

    def test_vimshopaka_sapta_varga(self):
        """Test Vimshopaka calculation with sapta_varga scheme."""
        result = calculate_vimshopaka_bala("moon", 45.0, "sapta_varga")

        # Check varga count
        assert len(result["varga_details"]) == 7

    def test_vimshopaka_dasha_varga(self):
        """Test Vimshopaka calculation with dasha_varga scheme."""
        result = calculate_vimshopaka_bala("mars", 280.0, "dasha_varga")

        # Check varga count
        assert len(result["varga_details"]) == 10

    def test_vimshopaka_shodasha_varga(self):
        """Test Vimshopaka calculation with shodasha_varga scheme."""
        result = calculate_vimshopaka_bala("jupiter", 100.0, "shodasha_varga")

        # Check varga count
        assert len(result["varga_details"]) == 16

    def test_vimshopaka_returns_correct_fields(self):
        """Verify all required fields are present in the result."""
        result = calculate_vimshopaka_bala("venus", 180.0, "shad_varga")

        assert isinstance(result["total_points"], int)
        assert isinstance(result["max_points"], int)
        assert isinstance(result["percentage"], float)
        assert isinstance(result["category"], str)
        assert isinstance(result["varga_details"], list)

        # Check varga detail fields
        detail = result["varga_details"][0]
        assert "division" in detail
        assert "rashi" in detail
        assert "dignity" in detail
        assert "score" in detail

    def test_vimshopaka_score_range(self):
        """Vimshopaka scores should be within valid range."""
        result = calculate_vimshopaka_bala("saturn", 200.0, "shad_varga")

        assert 0 <= result["total_points"] <= result["max_points"]
        assert 0 <= result["percentage"] <= 100

        # Check individual scores
        for detail in result["varga_details"]:
            assert 0 <= detail["score"] <= 20

    def test_vimshopaka_exalted_planet_high_score(self):
        """Exalted planet in D1 should have high score for that varga."""
        # Sun at 10° (Aries) - exalted
        result = calculate_vimshopaka_bala("sun", 10.0, "shad_varga")

        # D1 should show exalted dignity
        d1_detail = next(d for d in result["varga_details"] if d["division"] == 1)
        assert d1_detail["dignity"] == "exalted"
        assert d1_detail["score"] == 20

    def test_vimshopaka_debilitated_planet_low_score(self):
        """Debilitated planet in D1 should have low score for that varga."""
        # Sun at 190° (Libra) - debilitated
        result = calculate_vimshopaka_bala("sun", 190.0, "shad_varga")

        # D1 should show debilitated dignity
        d1_detail = next(d for d in result["varga_details"] if d["division"] == 1)
        assert d1_detail["dignity"] == "debilitated"
        assert d1_detail["score"] == 0

    def test_vimshopaka_category_excellent(self):
        """Test category assignment for excellent strength (>75%)."""
        # Sun at 10° Aries (exalted) should score well in many vargas
        result = calculate_vimshopaka_bala("sun", 10.0, "shad_varga")

        if result["percentage"] > 75:
            assert result["category"] == "excellent"

    def test_vimshopaka_category_boundaries(self):
        """Verify category assignment logic."""
        # Test with various longitudes to get different percentages
        test_cases = [
            (10.0, "sun"),  # Likely high score
            (190.0, "sun"),  # Debilitated, low score
            (125.0, "moon"),  # Mid-range
        ]

        for longitude, planet in test_cases:
            result = calculate_vimshopaka_bala(planet, longitude, "shad_varga")
            percentage = result["percentage"]
            category = result["category"]

            if percentage > 75:
                assert category == "excellent"
            elif percentage > 60:
                assert category == "good"
            elif percentage > 40:
                assert category == "moderate"
            elif percentage > 25:
                assert category == "weak"
            else:
                assert category == "very_weak"

    def test_vimshopaka_invalid_scheme(self):
        """Invalid scheme should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_vimshopaka_bala("sun", 10.0, "invalid_scheme")


class TestAllVimshopaka:
    """Tests for get_all_vimshopaka function."""

    def test_all_vimshopaka_multiple_planets(self):
        """Test Vimshopaka calculation for multiple planets."""
        planets = {
            "sun": 10.0,
            "moon": 45.0,
            "mars": 280.0,
        }

        result = get_all_vimshopaka(planets, "shad_varga")

        assert len(result) == 3
        assert "sun" in result
        assert "moon" in result
        assert "mars" in result

    def test_all_vimshopaka_returns_all_planets(self):
        """All input planets should be present in output."""
        planets = {
            "sun": 10.0,
            "moon": 45.0,
            "mars": 280.0,
            "mercury": 55.0,
            "jupiter": 100.0,
            "venus": 180.0,
            "saturn": 300.0,
        }

        result = get_all_vimshopaka(planets, "sapta_varga")

        for planet_name in planets:
            assert planet_name in result
            assert "percentage" in result[planet_name]
            assert "category" in result[planet_name]

    def test_all_vimshopaka_each_planet_valid(self):
        """Each planet result should have valid structure."""
        planets = {"sun": 10.0, "moon": 45.0}

        result = get_all_vimshopaka(planets, "shad_varga")

        for _planet_name, vimshopaka in result.items():
            assert "total_points" in vimshopaka
            assert "max_points" in vimshopaka
            assert "percentage" in vimshopaka
            assert "category" in vimshopaka
            assert "varga_details" in vimshopaka


class TestConstants:
    """Tests for Vimshopaka constants."""

    def test_varga_schemes_have_correct_counts(self):
        """Verify each varga scheme has the correct number of divisions."""
        assert len(VARGA_SCHEMES["shad_varga"]) == 6
        assert len(VARGA_SCHEMES["sapta_varga"]) == 7
        assert len(VARGA_SCHEMES["dasha_varga"]) == 10
        assert len(VARGA_SCHEMES["shodasha_varga"]) == 16

    def test_varga_schemes_structure(self):
        """Verify varga schemes contain valid division numbers."""
        for _scheme_name, divisions in VARGA_SCHEMES.items():
            assert isinstance(divisions, list)
            assert len(divisions) > 0

            for division in divisions:
                assert isinstance(division, int)
                assert division >= 1

    def test_dignity_scores_complete(self):
        """Verify all dignity levels have scores."""
        required_dignities = [
            "exalted",
            "moolatrikona",
            "own",
            "friend",
            "neutral",
            "enemy",
            "debilitated",
        ]

        for dignity in required_dignities:
            assert dignity in DIGNITY_SCORES
            assert isinstance(DIGNITY_SCORES[dignity], int)
            assert 0 <= DIGNITY_SCORES[dignity] <= 20

    def test_dignity_scores_ordering(self):
        """Verify dignity scores are in correct hierarchical order."""
        assert DIGNITY_SCORES["exalted"] > DIGNITY_SCORES["moolatrikona"]
        assert DIGNITY_SCORES["moolatrikona"] > DIGNITY_SCORES["own"]
        assert DIGNITY_SCORES["own"] > DIGNITY_SCORES["friend"]
        assert DIGNITY_SCORES["friend"] > DIGNITY_SCORES["neutral"]
        assert DIGNITY_SCORES["neutral"] > DIGNITY_SCORES["enemy"]
        assert DIGNITY_SCORES["enemy"] > DIGNITY_SCORES["debilitated"]


class TestFriendshipTable:
    """Tests for friendship table integration."""

    def test_friendship_table_loaded(self):
        """Verify friendship data loads correctly."""
        # Test a few friendship relationships by checking dignities
        # Sun is friends with Moon
        result = get_planet_dignity_in_sign("sun", "cancer")  # Moon's sign
        assert result == "friend"

        # Venus is enemy of Sun
        result = get_planet_dignity_in_sign("venus", "leo")  # Sun's sign
        assert result == "enemy"

    def test_rahu_ketu_dignity(self):
        """Rahu and Ketu dignity lookup should work correctly."""
        # Rahu exalted in Taurus
        result = get_planet_dignity_in_sign("rahu", "taurus")
        assert result == "exalted"

        # Ketu debilitated in Taurus
        result = get_planet_dignity_in_sign("ketu", "taurus")
        assert result == "debilitated"

        # Ketu exalted in Scorpio
        result = get_planet_dignity_in_sign("ketu", "scorpio")
        assert result == "exalted"
