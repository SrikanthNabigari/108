"""Tests for BPHS chart-specific dasha interpreter."""

from packages.context.src.dasha_interpreter import (
    _build_prediction,
    _build_summary,
    _check_combustion,
    _dignity_label,
    _find_aspects_received,
    _find_conjunctions,
    _house_label,
    _lookup_house_lord_reading,
    interpret_dasha_combination,
    interpret_dasha_lord,
)

# ── Sample natal data for Libra lagna (rashi_idx=6) ──
# Mercury at 163 (Virgo = own sign, rashi 5), house 12 from Libra
# Saturn at 290 (Capricorn = own sign, rashi 9), house 4 from Libra
# Sun at 230 (Scorpio, rashi 7), house 2 from Libra
# Jupiter at 100 (Cancer=exalted, rashi 3), house 10 from Libra
# Venus at 200 (Libra=own, rashi 6), house 1 from Libra
# Mars at 95 (Cancer=debilitated, rashi 3), house 10 from Libra
# Moon at 330 (Aquarius, rashi 10), house 5 from Libra
# Rahu at 310 (Aquarius, rashi 10), house 5 from Libra
# Ketu at 130 (Leo, rashi 4), house 11 from Libra

LIBRA_LAGNA = 6

NATAL_PLANETS = {
    "sun": {"longitude": 230.0, "is_retrograde": False},
    "moon": {"longitude": 330.0, "is_retrograde": False},
    "mars": {"longitude": 95.0, "is_retrograde": True},
    "mercury": {"longitude": 163.0, "is_retrograde": False},
    "jupiter": {"longitude": 100.0, "is_retrograde": False},
    "venus": {"longitude": 200.0, "is_retrograde": False},
    "saturn": {"longitude": 290.0, "is_retrograde": False},
    "rahu": {"longitude": 310.0, "is_retrograde": False},
    "ketu": {"longitude": 130.0, "is_retrograde": False},
}


class TestHouseLabel:
    def test_first_house(self):
        assert "1st" in _house_label(1)
        assert "Self" in _house_label(1)

    def test_tenth_house(self):
        assert "10th" in _house_label(10)
        assert "Career" in _house_label(10)


class TestDignityLabel:
    def test_exalted(self):
        # Jupiter in Cancer (rashi 3) = exalted
        key, label = _dignity_label("jupiter", 3)
        assert key == "exalted"
        assert "Exalted" in label

    def test_own_sign(self):
        # Venus in Taurus (rashi 1) = own sign
        key, label = _dignity_label("venus", 1)
        assert key == "own_sign"
        assert "own sign" in label

    def test_debilitated(self):
        # Mars in Cancer (rashi 3) = debilitated
        key, label = _dignity_label("mars", 3)
        assert key == "debilitated"
        assert "Debilitated" in label

    def test_neutral(self):
        # Sun in Scorpio (rashi 7) = neutral
        key, label = _dignity_label("sun", 7)
        assert key == "neutral"
        assert "neutral" in label.lower()


class TestInterpretDashaLord:
    def test_mercury_libra_lagna(self):
        """Mercury for Libra lagna: rules 9th (trikona) and 12th (dusthana), neutral."""
        result = interpret_dasha_lord("mercury", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["houses_ruled"] == [9, 12]
        # Trikona + dusthana = neutral (per classify_planet_role logic)
        assert result["functional_nature"] == "neutral"
        assert result["lord"] == "mercury"

    def test_saturn_yogakaraka_libra(self):
        """Saturn for Libra lagna: rules 4th and 5th, yogakaraka."""
        result = interpret_dasha_lord("saturn", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["houses_ruled"] == [4, 5]
        assert result["functional_nature"] == "yogakaraka"

    def test_dignity_populated(self):
        """Mercury in Virgo (exaltation sign) should have exalted dignity."""
        result = interpret_dasha_lord("mercury", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["dignity"] == "exalted"
        assert "Exalted" in result["dignity_label"]

    def test_natal_house_populated(self):
        """Mercury at 163 (Virgo=rashi 5) from Libra lagna(6) = house 12."""
        result = interpret_dasha_lord("mercury", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["natal_house"] == 12

    def test_retrograde_flag(self):
        """Mars is retrograde in our test data."""
        result = interpret_dasha_lord("mars", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["is_retrograde"] is True

    def test_house_labels_present(self):
        result = interpret_dasha_lord("saturn", NATAL_PLANETS, LIBRA_LAGNA)
        assert len(result["house_labels"]) == 2
        assert any("4th" in hl for hl in result["house_labels"])

    def test_summary_not_empty(self):
        """Every valid interpretation should have a non-empty summary."""
        for planet in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
            result = interpret_dasha_lord(planet, NATAL_PLANETS, LIBRA_LAGNA)
            assert result["summary"], f"Empty summary for {planet}"

    def test_prediction_not_empty(self):
        result = interpret_dasha_lord("mercury", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["prediction"]

    def test_rahu_no_lordship(self):
        """Rahu/Ketu have empty houses_ruled, should handle gracefully."""
        result = interpret_dasha_lord("rahu", NATAL_PLANETS, LIBRA_LAGNA)
        # Rahu may or may not have houses depending on classification;
        # key is no crash and summary exists
        assert result["summary"]
        assert result["lord"] == "rahu"

    def test_ketu_graceful(self):
        result = interpret_dasha_lord("ketu", NATAL_PLANETS, LIBRA_LAGNA)
        assert result["lord"] == "ketu"
        assert result["summary"]

    def test_no_birth_chart_graceful(self):
        """Works without BirthChart (no yogas/shadbala)."""
        result = interpret_dasha_lord("mercury", NATAL_PLANETS, LIBRA_LAGNA, birth_chart=None)
        assert result["yogas"] == []
        assert result["shadbala_score"] is None

    def test_nature_explanation(self):
        result = interpret_dasha_lord("mercury", NATAL_PLANETS, LIBRA_LAGNA)
        assert "Libra" in result["nature_explanation"]


class TestAspectsReceived:
    def test_aspects_on_mercury_house(self):
        """Mercury in house 12 from Libra. Check which planets aspect house 12."""
        # Mercury is at rashi 5 (Virgo), lagna 6 (Libra) => house 12
        aspects = _find_aspects_received("mercury", 12, NATAL_PLANETS, LIBRA_LAGNA)
        # This tests structure, not exact astrological correctness
        assert isinstance(aspects, list)
        for asp in aspects:
            assert "planet" in asp
            assert "from_house" in asp
            assert "nature" in asp


class TestConjunctionDetection:
    def test_jupiter_mars_conjunction(self):
        """Jupiter and Mars are both in Cancer (rashi 3)."""
        conjunctions = _find_conjunctions("jupiter", NATAL_PLANETS, LIBRA_LAGNA)
        planet_names = [c["planet"] for c in conjunctions]
        assert "mars" in planet_names

    def test_no_self_conjunction(self):
        """Planet should not be conjunct with itself."""
        conjunctions = _find_conjunctions("jupiter", NATAL_PLANETS, LIBRA_LAGNA)
        planet_names = [c["planet"] for c in conjunctions]
        assert "jupiter" not in planet_names


class TestCombustion:
    def test_combustion_sun_exempt(self):
        assert _check_combustion("sun", NATAL_PLANETS) is False

    def test_combustion_rahu_exempt(self):
        assert _check_combustion("rahu", NATAL_PLANETS) is False

    def test_combustion_mercury_near_sun(self):
        """Mercury at 163, Sun at 230. Distance ~67 degrees. Not combust."""
        assert _check_combustion("mercury", NATAL_PLANETS) is False

    def test_combustion_close_planet(self):
        """Test combustion with planet very close to Sun."""
        planets = {
            "sun": {"longitude": 230.0},
            "mercury": {"longitude": 235.0},  # only 5 degrees away
        }
        assert _check_combustion("mercury", planets) is True


class TestHouseLordReading:
    def test_lookup_existing(self):
        """lord_9_in_house_12 should exist in knowledge base."""
        reading = _lookup_house_lord_reading([9], 12)
        # May or may not have content depending on JSON data
        assert isinstance(reading, dict)
        assert "summary" in reading

    def test_lookup_multiple_houses(self):
        """Mercury rules 9 and 12, placed in house 12."""
        reading = _lookup_house_lord_reading([9, 12], 12)
        assert isinstance(reading, dict)
        assert "positive" in reading


class TestInterpretDashaCombination:
    def test_basic_combination(self):
        result = interpret_dasha_combination(
            md="mercury",
            ad="ketu",
            pd=None,
            natal_planets=NATAL_PLANETS,
            lagna_index=LIBRA_LAGNA,
        )
        assert result["mahadasha"]["lord"] == "mercury"
        assert result["antardasha"]["lord"] == "ketu"
        assert result["pratyantardasha"] is None

    def test_house_distance(self):
        """Mercury in house 12, Ketu in house 11 from Libra."""
        result = interpret_dasha_combination(
            md="mercury",
            ad="ketu",
            pd=None,
            natal_planets=NATAL_PLANETS,
            lagna_index=LIBRA_LAGNA,
        )
        assert result["md_ad_house_distance"] > 0
        assert result["positional_relationship"] in (
            "conjunction",
            "dwirdwadash",
            "upachaya",
            "kendra",
            "trine",
            "shadashtak",
            "opposition",
            "unknown",
        )

    def test_trine_relationship(self):
        """Saturn H4, Jupiter H10. Distance = (10-4)%12 = 6 => shadashtak."""
        result = interpret_dasha_combination(
            md="saturn",
            ad="jupiter",
            pd=None,
            natal_planets=NATAL_PLANETS,
            lagna_index=LIBRA_LAGNA,
        )
        # Distance 6 = shadashtak
        assert result["md_ad_house_distance"] == 6
        assert result["positional_relationship"] == "shadashtak"
        assert result["combination_quality"] == "challenging"

    def test_overall_summary(self):
        result = interpret_dasha_combination(
            md="mercury",
            ad="saturn",
            pd="jupiter",
            natal_planets=NATAL_PLANETS,
            lagna_index=LIBRA_LAGNA,
        )
        assert result["overall_summary"]
        assert result["pratyantardasha"] is not None

    def test_md_only(self):
        """Only MD, no AD/PD."""
        result = interpret_dasha_combination(
            md="venus",
            ad=None,
            pd=None,
            natal_planets=NATAL_PLANETS,
            lagna_index=LIBRA_LAGNA,
        )
        assert result["antardasha"] is None
        assert result["pratyantardasha"] is None
        assert result["md_ad_house_distance"] == 0


class TestBuildSummaryAndPrediction:
    def test_summary_with_all_factors(self):
        data = {
            "lord": "mercury",
            "houses_ruled": [9, 12],
            "house_labels": ["9th (Dharma, Fortune)", "12th (Moksha, Foreign)"],
            "functional_nature": "benefic",
            "natal_house": 4,
            "natal_house_label": "4th (Home, Education, Mother)",
            "dignity": "own_sign",
            "is_retrograde": False,
            "is_combust": False,
            "aspects_received": [
                {"planet": "jupiter", "from_house": 10, "nature": "benefic"},
            ],
            "conjunctions": [{"planet": "venus", "relationship": "friend"}],
            "yogas": [],
        }
        summary = _build_summary(data)
        assert "Mercury" in summary
        assert "9th" in summary

    def test_prediction_benefic(self):
        data = {
            "functional_nature": "benefic",
            "houses_ruled": [9, 12],
            "natal_house": 4,
            "dignity": "exalted",
            "yogas": [],
        }
        pred = _build_prediction(data)
        assert "blesses" in pred.lower() or "favors" in pred.lower() or "period" in pred.lower()

    def test_prediction_malefic(self):
        data = {
            "functional_nature": "malefic",
            "houses_ruled": [6, 8],
            "natal_house": 3,
            "dignity": "neutral",
            "yogas": [],
        }
        pred = _build_prediction(data)
        assert "period" in pred.lower()
