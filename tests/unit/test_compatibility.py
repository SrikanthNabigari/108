"""Tests for Kundali Matching (Ashta Kuta) compatibility."""

from packages.self.src.compatibility import (
    calculate_ashta_kuta,
    calculate_bhakoot_score,
    calculate_gana_score,
    calculate_graha_maitri_score,
    calculate_nadi_score,
    calculate_tara_score,
    calculate_varna_score,
    calculate_vashya_score,
    calculate_yoni_score,
    get_compatibility_verdict,
)


class TestVarnaScore:
    def test_same_varna(self):
        # Aries and Leo are both Kshatriya
        score = calculate_varna_score(1, 5)
        assert score == 1.0

    def test_boy_higher_varna(self):
        # Cancer (Brahmin) boy, Aries (Kshatriya) girl
        score = calculate_varna_score(4, 1)
        assert score >= 0.5


class TestVashyaScore:
    def test_same_category(self):
        # Same category should get max
        score = calculate_vashya_score(3, 6)  # both Manava
        assert score == 2.0

    def test_returns_valid_range(self):
        score = calculate_vashya_score(1, 7)
        assert 0 <= score <= 2.0


class TestTaraScore:
    def test_sampat_tara(self):
        # 2nd tara (Sampat) should give 3 points
        score = calculate_tara_score(0, 1)  # Ashwini to Bharani = 2nd
        assert score == 3.0

    def test_vipat_tara(self):
        # 3rd tara (Vipat) should give 0 points
        score = calculate_tara_score(0, 2)  # 3rd position
        assert score == 0.0

    def test_returns_valid_range(self):
        for i in range(27):
            score = calculate_tara_score(0, i)
            assert 0 <= score <= 3.0


class TestYoniScore:
    def test_same_yoni(self):
        # Same animal should give max
        score = calculate_yoni_score("Ashwini", "Shatabhisha")  # both Horse
        assert score == 4.0

    def test_enemy_yoni(self):
        # Cat and Rat are enemies
        score = calculate_yoni_score("Punarvasu", "Magha")  # Cat vs Rat
        assert score <= 2.0

    def test_unknown_nakshatra_returns_default(self):
        score = calculate_yoni_score("Unknown", "Ashwini")
        assert score == 2.0


class TestGrahaMaitriScore:
    def test_friendly_lords(self):
        # Sun and Jupiter are friends
        score = calculate_graha_maitri_score(5, 9)  # Leo (Sun) and Sagittarius (Jupiter)
        assert score == 5.0

    def test_enemy_lords(self):
        # Sun and Saturn are enemies
        score = calculate_graha_maitri_score(5, 10)  # Leo (Sun) and Capricorn (Saturn)
        assert score <= 3.0


class TestGanaScore:
    def test_same_deva(self):
        score = calculate_gana_score("Deva", "Deva")
        assert score == 6.0

    def test_deva_rakshasa(self):
        score = calculate_gana_score("Deva", "Rakshasa")
        assert score == 1.0

    def test_rakshasa_rakshasa(self):
        score = calculate_gana_score("Rakshasa", "Rakshasa")
        assert score == 6.0


class TestBhakootScore:
    def test_no_dosha(self):
        # Same rashi = no dosha
        score = calculate_bhakoot_score(1, 1)
        assert score == 7.0

    def test_returns_valid_range(self):
        for b in range(1, 13):
            for g in range(1, 13):
                score = calculate_bhakoot_score(b, g)
                assert score in (0.0, 7.0)


class TestNadiScore:
    def test_same_nadi_zero(self):
        score = calculate_nadi_score("Adi", "Adi")
        assert score == 0.0

    def test_different_nadi_max(self):
        score = calculate_nadi_score("Adi", "Madhya")
        assert score == 8.0

    def test_all_different_pairs(self):
        assert calculate_nadi_score("Adi", "Antya") == 8.0
        assert calculate_nadi_score("Madhya", "Antya") == 8.0
        assert calculate_nadi_score("Madhya", "Madhya") == 0.0


class TestAshtaKuta:
    def test_full_calculation(self):
        result = calculate_ashta_kuta(
            boy_rashi=5,  # Leo
            girl_rashi=9,  # Sagittarius
            boy_nakshatra="Magha",
            girl_nakshatra="Mula",
            boy_nakshatra_idx=9,
            girl_nakshatra_idx=18,
            boy_gana="Rakshasa",
            girl_gana="Rakshasa",
            boy_nadi="Adi",
            girl_nadi="Antya",
        )

        assert "total_score" in result
        assert "max_score" in result
        assert result["max_score"] == 36.0
        assert "percentage" in result
        assert "verdict" in result
        assert "kuta_scores" in result
        assert len(result["kuta_scores"]) == 8

    def test_all_scores_within_range(self):
        result = calculate_ashta_kuta(
            boy_rashi=1,
            girl_rashi=7,
            boy_nakshatra="Ashwini",
            girl_nakshatra="Swati",
            boy_nakshatra_idx=0,
            girl_nakshatra_idx=14,
            boy_gana="Deva",
            girl_gana="Deva",
            boy_nadi="Adi",
            girl_nadi="Madhya",
        )

        for kuta in result["kuta_scores"].values():
            assert kuta["score"] <= kuta["max_score"]
            assert kuta["score"] >= 0

    def test_critical_doshas_detected(self):
        result = calculate_ashta_kuta(
            boy_rashi=1,
            girl_rashi=1,
            boy_nakshatra="Ashwini",
            girl_nakshatra="Ashwini",
            boy_nakshatra_idx=0,
            girl_nakshatra_idx=0,
            boy_gana="Deva",
            girl_gana="Deva",
            boy_nadi="Adi",
            girl_nadi="Adi",  # Same nadi = dosha
        )

        assert result["kuta_scores"]["nadi"]["score"] == 0.0
        assert any(d["dosha"] == "Nadi Dosha" for d in result["critical_doshas"])


class TestVerdict:
    def test_excellent(self):
        assert get_compatibility_verdict(35) == "Excellent"

    def test_good(self):
        assert get_compatibility_verdict(28) == "Good"

    def test_average(self):
        assert get_compatibility_verdict(20) == "Average"

    def test_not_recommended(self):
        assert get_compatibility_verdict(15) == "Not Recommended"
