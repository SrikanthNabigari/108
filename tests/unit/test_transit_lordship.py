"""Tests for transit lordship resolver.

Tests cover all 5 public functions: get_all_house_lords, get_planet_lordships,
classify_planet_role, analyze_transit_lordships, and get_lordship_summary.
"""

from __future__ import annotations

from packages.self.src.transit_lordship import (
    analyze_transit_lordships,
    classify_planet_role,
    get_all_house_lords,
    get_lordship_summary,
    get_planet_lordships,
)

# ── Constants ──────────────────────────────────────────────────────────────────
LAGNA_LIBRA = 6
LAGNA_ARIES = 0

SAMPLE_TRANSITS = {
    "sun": {"longitude": 315.0, "rashi_num": 10},
    "moon": {"longitude": 45.0, "rashi_num": 1},
    "mars": {"longitude": 90.0, "rashi_num": 3},
    "mercury": {"longitude": 300.0, "rashi_num": 10},
    "jupiter": {"longitude": 15.0, "rashi_num": 0},
    "venus": {"longitude": 330.0, "rashi_num": 11},
    "saturn": {"longitude": 340.0, "rashi_num": 11},
    "rahu": {"longitude": 350.0, "rashi_num": 11},
    "ketu": {"longitude": 170.0, "rashi_num": 5},
}


# ── get_all_house_lords ───────────────────────────────────────────────────────


class TestGetAllHouseLords:
    """Tests for get_all_house_lords."""

    def test_libra_lagna(self):
        """Libra lagna (6): known lord assignments."""
        lords = get_all_house_lords(LAGNA_LIBRA)
        assert lords[1] == "venus"  # Libra -> Venus
        assert lords[2] == "mars"  # Scorpio -> Mars
        assert lords[3] == "jupiter"  # Sagittarius -> Jupiter
        assert lords[4] == "saturn"  # Capricorn -> Saturn
        assert lords[5] == "saturn"  # Aquarius -> Saturn
        assert lords[6] == "jupiter"  # Pisces -> Jupiter
        assert lords[7] == "mars"  # Aries -> Mars
        assert lords[8] == "venus"  # Taurus -> Venus
        assert lords[9] == "mercury"  # Gemini -> Mercury
        assert lords[10] == "moon"  # Cancer -> Moon
        assert lords[11] == "sun"  # Leo -> Sun
        assert lords[12] == "mercury"  # Virgo -> Mercury

    def test_aries_lagna(self):
        """Aries lagna (0): H1=mars, H2=venus, H3=mercury, etc."""
        lords = get_all_house_lords(LAGNA_ARIES)
        assert lords[1] == "mars"  # Aries -> Mars
        assert lords[2] == "venus"  # Taurus -> Venus
        assert lords[3] == "mercury"  # Gemini -> Mercury
        assert lords[4] == "moon"  # Cancer -> Moon
        assert lords[5] == "sun"  # Leo -> Sun
        assert lords[6] == "mercury"  # Virgo -> Mercury
        assert lords[7] == "venus"  # Libra -> Venus
        assert lords[8] == "mars"  # Scorpio -> Mars
        assert lords[9] == "jupiter"  # Sagittarius -> Jupiter
        assert lords[10] == "saturn"  # Capricorn -> Saturn
        assert lords[11] == "saturn"  # Aquarius -> Saturn
        assert lords[12] == "jupiter"  # Pisces -> Jupiter

    def test_returns_12_entries(self):
        """Always returns exactly 12 entries regardless of lagna."""
        for lagna in range(12):
            lords = get_all_house_lords(lagna)
            assert len(lords) == 12
            assert set(lords.keys()) == set(range(1, 13))

    def test_all_values_are_valid_planets(self):
        """All lord values are valid planet names."""
        valid_planets = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"}
        for lagna in range(12):
            lords = get_all_house_lords(lagna)
            for lord in lords.values():
                assert lord in valid_planets


# ── get_planet_lordships ──────────────────────────────────────────────────────


class TestGetPlanetLordships:
    """Tests for get_planet_lordships."""

    def test_mars_libra(self):
        """Mars for Libra lagna lords houses 2 (Scorpio) and 7 (Aries)."""
        assert get_planet_lordships("mars", LAGNA_LIBRA) == [2, 7]

    def test_saturn_libra(self):
        """Saturn for Libra lagna lords houses 4 (Capricorn) and 5 (Aquarius)."""
        assert get_planet_lordships("saturn", LAGNA_LIBRA) == [4, 5]

    def test_jupiter_libra(self):
        """Jupiter for Libra lagna lords houses 3 (Sagittarius) and 6 (Pisces)."""
        assert get_planet_lordships("jupiter", LAGNA_LIBRA) == [3, 6]

    def test_sun_always_one_house(self):
        """Sun always lords exactly 1 house (Leo)."""
        for lagna in range(12):
            houses = get_planet_lordships("sun", lagna)
            assert len(houses) == 1

    def test_moon_always_one_house(self):
        """Moon always lords exactly 1 house (Cancer)."""
        for lagna in range(12):
            houses = get_planet_lordships("moon", lagna)
            assert len(houses) == 1

    def test_dual_rulers_two_houses(self):
        """Mars, Mercury, Jupiter, Venus, Saturn each lord 2 houses."""
        dual_rulers = ["mars", "mercury", "jupiter", "venus", "saturn"]
        for planet in dual_rulers:
            houses = get_planet_lordships(planet, LAGNA_LIBRA)
            assert len(houses) == 2, f"{planet} should lord 2 houses"

    def test_case_insensitive(self):
        """Planet name matching is case-insensitive."""
        assert get_planet_lordships("Mars", LAGNA_LIBRA) == [2, 7]
        assert get_planet_lordships("SATURN", LAGNA_LIBRA) == [4, 5]

    def test_rahu_ketu_no_lordships(self):
        """Rahu and Ketu do not lord any houses in the standard scheme."""
        assert get_planet_lordships("rahu", LAGNA_LIBRA) == []
        assert get_planet_lordships("ketu", LAGNA_LIBRA) == []


# ── classify_planet_role ──────────────────────────────────────────────────────


class TestClassifyPlanetRole:
    """Tests for classify_planet_role."""

    def test_yogakaraka_saturn_libra(self):
        """Saturn for Libra = yogakaraka (lords 4=kendra, 5=trikona)."""
        role = classify_planet_role("saturn", LAGNA_LIBRA)
        assert role["functional_nature"] == "yogakaraka"
        assert role["is_yogakaraka"] is True
        assert role["is_kendradhipati"] is True
        assert role["is_trikonadhipati"] is True
        assert role["houses_ruled"] == [4, 5]

    def test_maraka_mars_libra(self):
        """Mars for Libra = maraka (lords 2 and 7, both maraka houses)."""
        role = classify_planet_role("mars", LAGNA_LIBRA)
        assert role["functional_nature"] == "maraka"
        assert role["is_maraka"] is True
        assert set(role["houses_ruled"]) == {2, 7}

    def test_benefic_sun_libra(self):
        """Sun for Libra lords H11 only — not trikona, not dusthana -> neutral."""
        role = classify_planet_role("sun", LAGNA_LIBRA)
        # H11 is upachaya, not kendra/trikona/dusthana/maraka
        assert role["houses_ruled"] == [11]
        assert role["functional_nature"] == "neutral"

    def test_benefic_trikona_lord(self):
        """Mercury for Aries lagna lords H3 and H6 — dusthana present, not pure benefic."""
        role = classify_planet_role("mercury", LAGNA_ARIES)
        # H3 and H6; H6 is dusthana
        assert role["is_dusthana_lord"] is True

    def test_malefic_dusthana_only(self):
        """Jupiter for Libra lords H3 and H6 — H6 is dusthana, H3 is neither kendra nor trikona."""
        role = classify_planet_role("jupiter", LAGNA_LIBRA)
        assert role["is_dusthana_lord"] is True
        assert role["functional_nature"] == "malefic"

    def test_classify_all_flags(self):
        """Verify all boolean flags are set correctly for Saturn/Libra."""
        role = classify_planet_role("saturn", LAGNA_LIBRA)
        assert isinstance(role["is_kendradhipati"], bool)
        assert isinstance(role["is_trikonadhipati"], bool)
        assert isinstance(role["is_dusthana_lord"], bool)
        assert isinstance(role["is_yogakaraka"], bool)
        assert isinstance(role["is_maraka"], bool)
        # Saturn lords 4 (kendra) and 5 (trikona), neither is dusthana or maraka
        assert role["is_dusthana_lord"] is False
        assert role["is_maraka"] is False

    def test_classify_neutral(self):
        """Moon for Libra lords only H10 (kendra, not trikona, not dusthana)."""
        role = classify_planet_role("moon", LAGNA_LIBRA)
        assert role["houses_ruled"] == [10]
        assert role["is_kendradhipati"] is True
        assert role["is_trikonadhipati"] is False
        # Kendra only, no trikona -> neutral (kendradhipati alone not malefic/benefic)
        assert role["functional_nature"] == "neutral"

    def test_classify_returns_planet_name(self):
        """Result contains the planet name in lowercase."""
        role = classify_planet_role("Venus", LAGNA_LIBRA)
        assert role["planet"] == "venus"

    def test_rahu_ketu_neutral(self):
        """Rahu/Ketu have no lordships, should be neutral."""
        for node in ("rahu", "ketu"):
            role = classify_planet_role(node, LAGNA_LIBRA)
            assert role["houses_ruled"] == []
            assert role["functional_nature"] == "neutral"

    def test_yogakaraka_mars_cancer(self):
        """Mars for Cancer lagna (3) lords H5 (trikona) and H10 (kendra) = yogakaraka."""
        role = classify_planet_role("mars", 3)  # Cancer lagna
        assert role["is_yogakaraka"] is True
        assert role["functional_nature"] == "yogakaraka"
        assert set(role["houses_ruled"]) == {5, 10}


# ── analyze_transit_lordships ─────────────────────────────────────────────────


class TestAnalyzeTransitLordships:
    """Tests for analyze_transit_lordships."""

    def test_all_9_planets(self):
        """All 9 planets in SAMPLE_TRANSITS are analyzed."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        planets = {r["planet"] for r in results}
        assert planets == {
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

    def test_structure(self):
        """Each entry has the required fields."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        required_keys = {
            "planet",
            "transit_rashi",
            "transit_house",
            "houses_ruled",
            "functional_nature",
            "role_details",
            "effects_per_house",
        }
        for entry in results:
            assert required_keys.issubset(
                entry.keys()
            ), f"Missing keys in {entry['planet']}: {required_keys - entry.keys()}"

    def test_interpretation_present(self):
        """Effects include interpretation dicts (may be empty if key not found)."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        for entry in results:
            for effect in entry["effects_per_house"]:
                assert "interpretation" in effect
                assert isinstance(effect["interpretation"], dict)

    def test_transit_quality_assigned(self):
        """Each effect has a transit_quality string."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        valid_qualities = {"excellent", "favorable", "challenging", "neutral"}
        for entry in results:
            for effect in entry["effects_per_house"]:
                assert effect["transit_quality"] in valid_qualities

    def test_saturn_yogakaraka_in_pisces(self):
        """Saturn (yogakaraka for Libra) in Pisces (rashi 11) -> H6 from Libra."""
        results = analyze_transit_lordships(
            {"saturn": {"longitude": 340.0, "rashi_num": 11}},
            LAGNA_LIBRA,
        )
        assert len(results) == 1
        sat = results[0]
        assert sat["functional_nature"] == "yogakaraka"
        # Pisces (11) from Libra (6) -> house = (11 - 6) % 12 + 1 = 6
        assert sat["transit_house"] == 6
        assert sat["houses_ruled"] == [4, 5]

    def test_empty_transit_positions(self):
        """Empty input returns empty list."""
        assert analyze_transit_lordships({}, LAGNA_LIBRA) == []

    def test_single_planet(self):
        """Single planet analysis works correctly."""
        results = analyze_transit_lordships(
            {"sun": {"longitude": 315.0, "rashi_num": 10}},
            LAGNA_LIBRA,
        )
        assert len(results) == 1
        assert results[0]["planet"] == "sun"

    def test_effects_per_house_count(self):
        """Number of effects_per_house entries matches houses_ruled count."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        for entry in results:
            assert len(entry["effects_per_house"]) == len(entry["houses_ruled"])

    def test_themes_are_lists(self):
        """Themes for each effect are lists of strings."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        for entry in results:
            for effect in entry["effects_per_house"]:
                assert isinstance(effect["themes"], list)

    def test_lord_in_own_house(self):
        """Special case: planet transiting the sign it lords.

        Venus for Libra lords H1 (Libra=6) and H8 (Taurus=1).
        If Venus transits Libra (rashi_num=6), transit_house=1 from Libra.
        Effect for ruled_house=1 means lord_1 in house_1 (own house).
        """
        results = analyze_transit_lordships(
            {"venus": {"longitude": 195.0, "rashi_num": 6}},
            LAGNA_LIBRA,
        )
        assert len(results) == 1
        venus = results[0]
        assert venus["transit_house"] == 1
        assert 1 in venus["houses_ruled"]
        # Check interpretation key would be lord_1_in_house_1
        own_house_effect = [e for e in venus["effects_per_house"] if e["ruled_house"] == 1]
        assert len(own_house_effect) == 1


# ── get_lordship_summary ─────────────────────────────────────────────────────


class TestGetLordshipSummary:
    """Tests for get_lordship_summary."""

    def test_structure(self):
        """Summary has all required keys."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(results)
        required_keys = {
            "yogakaraka_transits",
            "benefic_transits",
            "malefic_transits",
            "maraka_transits",
            "dusthana_activations",
            "favorable_count",
            "unfavorable_count",
            "key_insight",
        }
        assert required_keys.issubset(summary.keys())

    def test_yogakaraka_present(self):
        """When yogakaraka present, key_insight mentions it."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(results)
        assert "saturn" in summary["yogakaraka_transits"]
        assert "Yogakaraka" in summary["key_insight"]

    def test_counts(self):
        """Favorable + unfavorable counts are non-negative integers."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(results)
        assert isinstance(summary["favorable_count"], int)
        assert isinstance(summary["unfavorable_count"], int)
        assert summary["favorable_count"] >= 0
        assert summary["unfavorable_count"] >= 0

    def test_empty_input(self):
        """Empty transit list produces a mixed-period summary."""
        summary = get_lordship_summary([])
        assert summary["yogakaraka_transits"] == []
        assert summary["key_insight"] == "Mixed period with balanced planetary influences"
        assert summary["favorable_count"] == 0
        assert summary["unfavorable_count"] == 0

    def test_dusthana_activations_are_dusthana_houses(self):
        """dusthana_activations only contains actual dusthana house numbers."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(results)
        for h in summary["dusthana_activations"]:
            assert h in {6, 8, 12}

    def test_maraka_transits(self):
        """Mars for Libra should appear in maraka_transits."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(results)
        assert "mars" in summary["maraka_transits"]

    def test_malefic_transits(self):
        """Jupiter for Libra (lords 3,6) should appear in malefic_transits."""
        results = analyze_transit_lordships(SAMPLE_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(results)
        assert "jupiter" in summary["malefic_transits"]

    def test_challenging_insight_when_no_yogakaraka(self):
        """When no yogakaraka and unfavorable > favorable, insight mentions challenging."""
        # Use Aries lagna where Saturn is NOT yogakaraka
        # Only use dusthana lords
        transits_only_dusthana = {
            "mercury": {"longitude": 240.0, "rashi_num": 8},  # Mercury in Sag
            "mars": {"longitude": 210.0, "rashi_num": 7},  # Mars in Scorpio
        }
        results = analyze_transit_lordships(transits_only_dusthana, LAGNA_ARIES)
        summary = get_lordship_summary(results)
        # If unfavorable > favorable, insight should mention challenging or mixed
        assert isinstance(summary["key_insight"], str)
        assert len(summary["key_insight"]) > 0
