"""Tests for the Gem Recommendation Engine."""


from packages.self.src.gem_recommender import (
    LAGNA_CLASSIFICATIONS,
    PLANET_GEMS,
    _check_enemy_gems,
    _get_planet_role,
    check_gem_compatibility,
    get_lagna_gem_map,
    recommend_gems,
)

# ---------------------------------------------------------------------------
# Helper data
# ---------------------------------------------------------------------------

# Simplified planets dict for Libra Lagna native
LIBRA_PLANETS = {
    "sun": {"longitude": 227.0, "rashi": "scorpio", "house": 2},
    "moon": {"longitude": 326.85, "rashi": "aquarius", "house": 5},
    "mars": {"longitude": 109.5, "rashi": "cancer", "house": 10},
    "mercury": {"longitude": 213.0, "rashi": "scorpio", "house": 2},
    "jupiter": {"longitude": 152.0, "rashi": "virgo", "house": 12},
    "venus": {"longitude": 260.0, "rashi": "sagittarius", "house": 3},
    "saturn": {"longitude": 313.0, "rashi": "aquarius", "house": 5},
}


# ---------------------------------------------------------------------------
# Tests: planet role classification
# ---------------------------------------------------------------------------


class TestGetPlanetRole:
    def test_libra_yoga_karaka(self):
        assert _get_planet_role("saturn", "libra") == "yoga_karaka"

    def test_libra_primary_benefic_venus(self):
        assert _get_planet_role("venus", "libra") == "primary_benefic"

    def test_libra_functional_malefic_jupiter(self):
        assert _get_planet_role("jupiter", "libra") == "functional_malefic"

    def test_libra_maraka_mars(self):
        assert _get_planet_role("mars", "libra") == "maraka"

    def test_cancer_yoga_karaka_mars(self):
        assert _get_planet_role("mars", "cancer") == "yoga_karaka"

    def test_aries_no_yoga_karaka(self):
        assert _get_planet_role("mars", "aries") == "primary_benefic"

    def test_unknown_lagna_returns_neutral(self):
        assert _get_planet_role("sun", "unknown") == "neutral"

    def test_all_lagnas_have_classifications(self):
        all_lagnas = [
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
        for lagna in all_lagnas:
            assert lagna in LAGNA_CLASSIFICATIONS


# ---------------------------------------------------------------------------
# Tests: enemy gem checking
# ---------------------------------------------------------------------------


class TestCheckEnemyGems:
    def test_no_conflict(self):
        result = _check_enemy_gems(["ruby", "yellow_sapphire"])
        assert result == []

    def test_ruby_blue_sapphire_conflict(self):
        result = _check_enemy_gems(["ruby", "blue_sapphire"])
        assert len(result) == 1
        assert ("ruby", "blue_sapphire") in result

    def test_multiple_conflicts(self):
        result = _check_enemy_gems(["ruby", "blue_sapphire", "hessonite"])
        assert len(result) == 2

    def test_empty_list(self):
        result = _check_enemy_gems([])
        assert result == []


# ---------------------------------------------------------------------------
# Tests: get_lagna_gem_map
# ---------------------------------------------------------------------------


class TestGetLagnaGemMap:
    def test_libra_returns_benefic_gems(self):
        result = get_lagna_gem_map("libra")
        assert result["lagna"] == "libra"
        benefic_planets = {g["planet"] for g in result["benefic_gems"]}
        assert "saturn" in benefic_planets  # yoga karaka
        assert "venus" in benefic_planets

    def test_libra_has_yoga_karaka_gem(self):
        result = get_lagna_gem_map("libra")
        assert "yoga_karaka_gem" in result
        assert result["yoga_karaka_gem"]["planet"] == "saturn"
        assert result["yoga_karaka_gem"]["gem"] == "blue_sapphire"

    def test_libra_harmful_includes_jupiter(self):
        result = get_lagna_gem_map("libra")
        harmful_planets = {g["planet"] for g in result["harmful_gems"]}
        assert "jupiter" in harmful_planets

    def test_aries_no_yoga_karaka(self):
        result = get_lagna_gem_map("aries")
        assert "yoga_karaka_gem" not in result

    def test_cancer_yoga_karaka_mars(self):
        result = get_lagna_gem_map("cancer")
        assert result["yoga_karaka_gem"]["planet"] == "mars"
        assert result["yoga_karaka_gem"]["gem"] == "red_coral"

    def test_unknown_lagna(self):
        result = get_lagna_gem_map("invalid")
        assert "error" in result

    def test_all_12_lagnas_work(self):
        lagnas = [
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
        for lagna in lagnas:
            result = get_lagna_gem_map(lagna)
            assert "benefic_gems" in result
            assert "harmful_gems" in result


# ---------------------------------------------------------------------------
# Tests: check_gem_compatibility
# ---------------------------------------------------------------------------


class TestCheckGemCompatibility:
    def test_libra_saturn_safe(self):
        result = check_gem_compatibility("saturn", "libra", LIBRA_PLANETS)
        assert result["safe"] is True
        assert result["role"] == "yoga_karaka"
        assert result["recommendation"] == "Recommended"

    def test_libra_jupiter_not_safe(self):
        result = check_gem_compatibility("jupiter", "libra", LIBRA_PLANETS)
        assert result["safe"] is False
        assert "functional malefic" in result["warnings"][0].lower()

    def test_libra_mars_maraka(self):
        result = check_gem_compatibility("mars", "libra", LIBRA_PLANETS)
        assert result["safe"] is False
        assert result["recommendation"] == "Not recommended"

    def test_debilitated_benefic_recommended(self):
        """Mars debilitated in Cancer for Cancer Lagna (yoga karaka) should add note."""
        planets = {"mars": {"longitude": 109.5, "rashi": "cancer"}}
        result = check_gem_compatibility("mars", "cancer", planets)
        assert result["safe"] is True
        # Should have a note about debilitation recommending the gem
        debil_warning = [w for w in result["warnings"] if "debilitated" in w.lower()]
        assert len(debil_warning) > 0

    def test_returns_gem_name(self):
        result = check_gem_compatibility("venus", "libra", LIBRA_PLANETS)
        assert result["gem"] == "diamond"


# ---------------------------------------------------------------------------
# Tests: recommend_gems (full engine)
# ---------------------------------------------------------------------------


class TestRecommendGems:
    def test_libra_primary_gem_is_saturn(self):
        result = recommend_gems("libra", LIBRA_PLANETS)
        assert result["primary_gem"] is not None
        assert result["primary_gem"]["planet"] == "saturn"
        assert result["primary_gem"]["gem"] == "blue_sapphire"

    def test_libra_has_contraindicated(self):
        result = recommend_gems("libra", LIBRA_PLANETS)
        contra_planets = {c["planet"] for c in result["contraindicated"]}
        assert "jupiter" in contra_planets or "mars" in contra_planets

    def test_secondary_gems_present(self):
        result = recommend_gems("libra", LIBRA_PLANETS)
        assert isinstance(result["secondary_gems"], list)

    def test_dasha_gem_when_benefic(self):
        dasha = {"mahadasha_lord": "mercury"}
        result = recommend_gems("libra", LIBRA_PLANETS, current_dasha=dasha)
        assert result["dasha_gem"] is not None
        assert result["dasha_gem"]["planet"] == "mercury"

    def test_dasha_gem_skipped_when_malefic(self):
        dasha = {"mahadasha_lord": "jupiter"}  # malefic for Libra
        result = recommend_gems("libra", LIBRA_PLANETS, current_dasha=dasha)
        assert result["dasha_gem"] is None

    def test_has_general_advice(self):
        result = recommend_gems("libra", LIBRA_PLANETS)
        assert "general_advice" in result
        assert isinstance(result["general_advice"], str)
        assert len(result["general_advice"]) > 0

    def test_aries_lagna(self):
        planets = {"sun": {"longitude": 20.0, "rashi": "aries", "house": 1}}
        result = recommend_gems("aries", planets)
        assert result["primary_gem"] is not None
        # Sun or Jupiter should be primary for Aries
        assert result["primary_gem"]["planet"] in ("sun", "jupiter", "mars")

    def test_cancer_yoga_karaka_mars(self):
        planets = {"mars": {"longitude": 270.0, "rashi": "capricorn", "house": 7}}
        result = recommend_gems("cancer", planets)
        assert result["primary_gem"]["planet"] == "mars"
        assert "Yoga Karaka" in result["primary_gem"]["reason"]

    def test_unknown_lagna_returns_error(self):
        result = recommend_gems("invalid", {})
        assert "error" in result

    def test_enemy_conflict_detection(self):
        """If recommended gems conflict, enemy_conflicts should be populated."""
        # For a Lagna where both Ruby and Blue Sapphire might be recommended
        # This is unlikely in practice but test the mechanism
        result = recommend_gems("libra", LIBRA_PLANETS)
        assert isinstance(result["enemy_conflicts"], list)

    def test_shadbala_weak_planet_note(self):
        shadbala = {"venus": {"total": 0.5}}
        result = recommend_gems("libra", LIBRA_PLANETS, shadbala=shadbala)
        # Venus is a primary benefic; check that weak note appears in secondary gems
        venus_gems = [g for g in result["secondary_gems"] if g["planet"] == "venus"]
        if venus_gems:
            assert "weak" in venus_gems[0]["reason"].lower()

    def test_active_doshas_in_advice(self):
        doshas = [{"name": "Mangal Dosha"}]
        result = recommend_gems("libra", LIBRA_PLANETS, active_doshas=doshas)
        assert "Mangal Dosha" in result["general_advice"]

    def test_gem_entry_has_required_fields(self):
        result = recommend_gems("libra", LIBRA_PLANETS)
        pg = result["primary_gem"]
        assert "planet" in pg
        assert "gem" in pg
        assert "reason" in pg
        assert "finger" in pg
        assert "metal" in pg
        assert "minimum_carat" in pg
        assert "wearing_day" in pg

    def test_all_planet_gems_defined(self):
        """Every planet should have gem info."""
        for planet in [
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        ]:
            assert planet in PLANET_GEMS
            assert "primary" in PLANET_GEMS[planet]
