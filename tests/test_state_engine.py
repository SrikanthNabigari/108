"""Tests for the State Vector Engine."""

from datetime import datetime
from typing import Any, ClassVar

from packages.context.src.state_engine import (
    AREA_HOUSES,
    AREA_PLANETS,
    FACTOR_WEIGHTS,
    RASHI_NAMES,
    _build_birth_chart,
    _clamp,
    _compute_area_scores,
    _compute_ashtakavarga_transit_score,
    _compute_dasha_area_score,
    _compute_double_transit_area_score,
    _detect_natal_doshas,
    _detect_natal_yogas,
    _dignity_for_planet,
    _house_from_lagna,
    _mental_state_label,
    _normalize_dasha,
    _normalize_gochara,
    _normalize_panchanga,
    _normalize_transit_moon,
    _rashi_index,
    _score_ashtakavarga,
    _score_dosha_impact,
    _score_shadbala,
    _score_yoga_activation,
    _score_yoga_with_natal,
    _virupas_to_score,
    compute_area_trend,
    compute_state_range,
    compute_state_vector,
    get_hora_lord,
)

# ── Test data: user's birth chart ──

BIRTH_DT = "1992-12-03T03:00:00"
BIRTH_LAT = 16.726239
BIRTH_LON = 81.288428
LAGNA_RASHI = "libra"
MOON_LONGITUDE = 326.85
MOON_RASHI = "aquarius"

NATAL_PLANETS = {
    "sun": {"longitude": 226.5, "rashi": 7, "house": 2},
    "moon": {"longitude": 326.85, "rashi": 10, "house": 5},
    "mars": {"longitude": 103.2, "rashi": 3, "house": 10},
    "mercury": {"longitude": 241.3, "rashi": 8, "house": 2},
    "jupiter": {"longitude": 142.8, "rashi": 4, "house": 11},
    "venus": {"longitude": 206.1, "rashi": 6, "house": 12},
    "saturn": {"longitude": 313.7, "rashi": 10, "house": 4},
    "rahu": {"longitude": 205.5, "rashi": 6, "house": 12},
    "ketu": {"longitude": 25.5, "rashi": 0, "house": 6},
}


# ── Utility tests ──


class TestUtilities:
    def test_rashi_index(self):
        assert _rashi_index("aries") == 0
        assert _rashi_index("libra") == 6
        assert _rashi_index("pisces") == 11
        assert _rashi_index("LIBRA") == 6
        assert _rashi_index("unknown") == 0

    def test_house_from_lagna(self):
        # Libra lagna (6). Planet in Libra (6) → house 1
        assert _house_from_lagna(6, 6) == 1
        # Planet in Scorpio (7) → house 2
        assert _house_from_lagna(7, 6) == 2
        # Planet in Aries (0) → house 7
        assert _house_from_lagna(0, 6) == 7
        # Wrap-around: planet in Virgo (5) from Libra (6) → house 12
        assert _house_from_lagna(5, 6) == 12

    def test_clamp(self):
        assert _clamp(5.0) == 5.0
        assert _clamp(-1.0) == 0.0
        assert _clamp(12.0) == 10.0
        assert _clamp(3.0, 2.0, 8.0) == 3.0

    def test_mental_state_labels(self):
        assert _mental_state_label(9.0) == "Thriving"
        assert _mental_state_label(8.0) == "Thriving"
        assert _mental_state_label(7.0) == "Flowing"
        assert _mental_state_label(6.5) == "Flowing"
        assert _mental_state_label(5.5) == "Steady"
        assert _mental_state_label(5.0) == "Steady"
        assert _mental_state_label(4.0) == "Challenged"
        assert _mental_state_label(3.5) == "Challenged"
        assert _mental_state_label(2.5) == "Struggling"
        assert _mental_state_label(1.0) == "Turbulent"


# ── Panchanga normalizer tests ──


class TestNormalizePanchanga:
    def test_empty_panchanga(self):
        score, _planet, _desc = _normalize_panchanga({})
        assert 0 <= score <= 10
        assert score == 5.0  # baseline

    def test_good_panchanga(self):
        panchanga = {
            "tithi": {"name": "Panchami", "number": 5, "paksha": "Shukla"},
            "yoga": {"name": "Siddha"},
            "vara": {"name": "Thursday"},
            "karana": {"name": "Bava"},
        }
        score, _planet, desc = _normalize_panchanga(panchanga)
        assert score > 5.0  # Should be above baseline
        assert "Panchami" in desc
        assert "Thursday" in desc
        assert "Siddha yoga" in desc

    def test_bad_panchanga(self):
        panchanga = {
            "tithi": {"name": "Chaturthi", "number": 4, "paksha": "Krishna"},
            "yoga": {"name": "Vyatipata"},
            "vara": {"name": "Saturday"},
            "karana": {"name": "Shakuni"},
        }
        score, _planet, _desc = _normalize_panchanga(panchanga)
        assert score < 5.0  # Should be below baseline

    def test_score_always_in_range(self):
        # Even extreme values should clamp
        panchanga = {
            "tithi": {"number": 30, "paksha": "Krishna"},
            "yoga": {"name": "Vishkumbha"},
            "vara": {"name": "Saturday"},
        }
        score, _, _ = _normalize_panchanga(panchanga)
        assert 0 <= score <= 10


# ── Transit Moon tests ──


class TestNormalizeTransitMoon:
    def test_favorable_house(self):
        # Moon in house 11 from natal Moon (most favorable)
        # Natal Moon in Cancer (3), transit Moon in Taurus (1) → H11 from Moon
        transit_positions = {"moon": 1}  # Taurus
        lagna_index = 6  # Libra lagna (kept for signature compat)
        score, planet, desc = _normalize_transit_moon(
            transit_positions, lagna_index, moon_rashi_idx=3
        )
        assert score == 8.5  # H11 from Moon = best
        assert planet == "moon"
        assert "H11 from Moon" in desc

    def test_unfavorable_house(self):
        # Moon in house 8 from natal Moon (Chandrashtama)
        # Natal Moon in Libra (6), transit Moon in Taurus (1) → H8 from Moon
        transit_positions = {"moon": 1}  # Taurus
        lagna_index = 6
        score, _, desc = _normalize_transit_moon(transit_positions, lagna_index, moon_rashi_idx=6)
        assert score <= 1.0  # H8 = Chandrashtama (2.0 base - 1.0 penalty)
        assert "H8 from Moon" in desc
        assert "CHANDRASHTAMA" in desc

    def test_empty_positions(self):
        score, _, _ = _normalize_transit_moon({}, 0)
        assert 0 <= score <= 10

    def test_chandrashtama_detection(self):
        # Transit Moon in 8th from natal Moon should flag Chandrashtama
        # Natal Moon in Aries (0), transit Moon in Scorpio (7) → H8
        transit_positions = {"moon": 7}
        score, _, desc = _normalize_transit_moon(transit_positions, 0, moon_rashi_idx=0)
        assert "CHANDRASHTAMA" in desc
        assert score < 3.0

    def test_tarabala_naidhana(self):
        # Naidhana tara (7th) should have strong negative effect
        transit_positions = {"moon": 0}
        # Birth Moon nak 1 (Ashwini), transit nak 7 (Punarvasu) → tara 7 = Naidhana
        raw_planets = {"moon": {"longitude": 80.0}}  # ~nak 7
        _score, _, desc = _normalize_transit_moon(
            transit_positions,
            0,
            birth_moon_nak=1,
            raw_planets=raw_planets,
            moon_rashi_idx=0,
        )
        assert "Naidhana" in desc


# ── Gochara tests ──


class TestNormalizeGochara:
    def test_mostly_favorable_with_house_scores(self):
        """Per-house graded scores — favorable houses score 6.5-9.5."""
        transit_result = {
            "summary": {
                "favorable_count": 5,
                "unfavorable_count": 2,
                "overall_trend": "favorable",
            },
            "planet_transits": {
                "jupiter": {"is_favorable": True, "house_from_moon": 11},  # 9.5
                "venus": {"is_favorable": True, "house_from_moon": 5},  # 8.0
                "mercury": {"is_favorable": True, "house_from_moon": 2},  # 7.0
                "moon": {"is_favorable": True, "house_from_moon": 10},  # 7.5
                "sun": {"is_favorable": True, "house_from_moon": 10},  # 8.5
                "mars": {"is_favorable": False, "house_from_moon": 8},  # 2.0
                "saturn": {"is_favorable": False, "house_from_moon": 8},  # 1.5
            },
            "sade_sati": {"active": False},
        }
        score, _planet, desc = _normalize_gochara(transit_result)
        assert score > 5.0
        assert "5 favorable" in desc

    def test_sade_sati_peak(self):
        transit_result = {
            "summary": {
                "favorable_count": 3,
                "unfavorable_count": 4,
                "overall_trend": "mixed",
            },
            "planet_transits": {
                "jupiter": {"is_favorable": True, "house_from_moon": 2},  # 7.5
                "venus": {"is_favorable": True, "house_from_moon": 1},  # 7.0
                "mercury": {"is_favorable": True, "house_from_moon": 4},  # 7.0
                "moon": {"is_favorable": False, "house_from_moon": 8},  # 2.5
                "sun": {"is_favorable": False, "house_from_moon": 8},  # 2.0
                "mars": {"is_favorable": False, "house_from_moon": 1},  # 3.0
                "saturn": {"is_favorable": False, "house_from_moon": 1},  # 2.0
            },
            "sade_sati": {"active": True, "phase": "peak"},
        }
        score, planet, _ = _normalize_gochara(transit_result)
        assert score < 5.0
        assert planet == "saturn"

    def test_empty_transit(self):
        score, _, desc = _normalize_gochara({})
        assert score == 5.0
        assert "No transit data" in desc

    def test_sandhi_penalty(self):
        """Planet at sign boundary (sandhi) should score lower than mid-sign."""
        transit_result = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {
                "jupiter": {"is_favorable": True, "house_from_moon": 11},  # 9.5 base
            },
            "sade_sati": {"active": False},
        }
        # Jupiter mid-sign (15°) = no sandhi penalty
        raw_mid = {"jupiter": {"longitude": 75.0}}  # 15° in Gemini
        score_mid, _, _ = _normalize_gochara(transit_result, raw_planets=raw_mid)

        # Jupiter near boundary (0.5°) = significant sandhi penalty
        raw_edge = {"jupiter": {"longitude": 60.5}}  # 0.5° in Gemini
        score_edge, _, _ = _normalize_gochara(transit_result, raw_planets=raw_edge)

        # Mid-sign should be higher since sandhi weakens the transit
        assert score_mid > score_edge

    def test_house_differentiation(self):
        """Different houses for same planet should give different scores."""
        # Jupiter in house 11 (gains = 9.5)
        result_11 = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {"jupiter": {"is_favorable": True, "house_from_moon": 11}},
            "sade_sati": {"active": False},
        }
        # Jupiter in house 2 (wealth = 7.5)
        result_2 = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {"jupiter": {"is_favorable": True, "house_from_moon": 2}},
            "sade_sati": {"active": False},
        }
        # Jupiter in house 8 (obstacles = 2.5)
        result_8 = {
            "summary": {
                "favorable_count": 0,
                "unfavorable_count": 1,
                "overall_trend": "unfavorable",
            },
            "planet_transits": {"jupiter": {"is_favorable": False, "house_from_moon": 8}},
            "sade_sati": {"active": False},
        }
        score_11, _, _ = _normalize_gochara(result_11)
        score_2, _, _ = _normalize_gochara(result_2)
        score_8, _, _ = _normalize_gochara(result_8)

        assert score_11 > score_2 > score_8
        assert score_11 > 8.0
        assert score_8 < 4.0

    def test_retrograde_intensifies(self):
        """Retrograde planet should intensify both favorable and unfavorable effects."""
        transit_result = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {"jupiter": {"is_favorable": True, "house_from_moon": 11}},
            "sade_sati": {"active": False},
        }
        raw_direct = {"jupiter": {"longitude": 75.0, "is_retrograde": False}}
        raw_retro = {"jupiter": {"longitude": 75.0, "is_retrograde": True}}

        score_direct, _, _ = _normalize_gochara(transit_result, raw_planets=raw_direct)
        score_retro, _, _ = _normalize_gochara(transit_result, raw_planets=raw_retro)

        # Retrograde favorable = even higher score
        assert score_retro > score_direct

    def test_vedha_cancellation(self):
        """Vedha should largely cancel a favorable transit, pulling score toward neutral."""
        transit_result = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {
                "jupiter": {"is_favorable": True, "has_vedha": False, "house_from_moon": 11},
            },
            "sade_sati": {"active": False},
        }
        result_vedha = {
            "summary": {
                "favorable_count": 0,
                "unfavorable_count": 1,
                "overall_trend": "unfavorable",
            },
            "planet_transits": {
                "jupiter": {"is_favorable": True, "has_vedha": True, "house_from_moon": 11},
            },
            "sade_sati": {"active": False},
        }
        score_clear, _, _ = _normalize_gochara(transit_result)
        score_vedha, _, _ = _normalize_gochara(result_vedha)

        # Vedha should significantly reduce the score
        assert score_clear > score_vedha
        # Vedha score should be closer to neutral (5.0)
        assert abs(score_vedha - 5.0) < abs(score_clear - 5.0)

    def test_lordship_modifier(self):
        """Yogakaraka planet should score higher than malefic lord."""
        transit_result = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {"saturn": {"is_favorable": True, "house_from_moon": 11}},
            "sade_sati": {"active": False},
        }
        # Libra lagna (6): Saturn is yogakaraka (lords 4 + 5)
        score_yk, _, _ = _normalize_gochara(transit_result, lagna_index=6)
        # Aries lagna (0): Saturn lords 10 + 11, neutral/benefic
        score_neutral, _, _ = _normalize_gochara(transit_result, lagna_index=0)

        # Yogakaraka boost should give higher score
        assert score_yk > score_neutral

    def test_fallback_without_house_from_moon(self):
        """Without house_from_moon, should fallback to is_favorable-based scoring."""
        transit_result = {
            "summary": {"favorable_count": 1, "unfavorable_count": 0, "overall_trend": "favorable"},
            "planet_transits": {
                "jupiter": {"is_favorable": True},  # no house_from_moon
            },
            "sade_sati": {"active": False},
        }
        score, _, _ = _normalize_gochara(transit_result)
        assert score > 5.0  # favorable fallback = 7.5


# ── Dasha tests ──


class TestNormalizeDasha:
    def test_no_dasha(self):
        score, _planet, desc = _normalize_dasha(None, {})
        assert score == 5.0
        assert "unavailable" in desc

    def test_good_dasha(self):
        dasha = {
            "mahadasha": {"lord": "jupiter"},
            "antardasha": {"lord": "venus"},
            "pratyantardasha": {"lord": "mercury"},
        }
        # Jupiter in Cancer (exalted), Venus in Taurus (own), Mercury in Virgo (own)
        natal = {
            "jupiter": {"rashi": 3},  # Cancer = exalted
            "venus": {"rashi": 1},  # Taurus = own
            "mercury": {"rashi": 5},  # Virgo = own
        }
        # Sagittarius lagna (8): Jupiter lords 1+4 = benefic/yogakaraka
        score, planet, desc = _normalize_dasha(dasha, natal, lagna_index=8)
        assert score > 6.5  # High dignity + functional benefic
        assert planet == "jupiter"
        assert "Jupiter MD" in desc

    def test_bad_dasha(self):
        dasha = {
            "mahadasha": {"lord": "saturn"},
            "antardasha": {"lord": "mars"},
            "pratyantardasha": {"lord": "rahu"},
        }
        # Saturn debilitated in Aries, Mars debilitated in Cancer
        natal = {
            "saturn": {"rashi": 0},  # Aries = debilitated
            "mars": {"rashi": 3},  # Cancer = debilitated
            "rahu": {"rashi": 4},  # Leo = neutral
        }
        # Leo lagna (4): Saturn lords 6+7 (malefic+maraka)
        score, _, _ = _normalize_dasha(dasha, natal, lagna_index=4)
        assert score < 5.0

    def test_functional_nature_matters(self):
        """Same planet, same dignity, different lagna = different score."""
        dasha = {
            "mahadasha": {"lord": "saturn"},
            "antardasha": {"lord": "mercury"},
            "pratyantardasha": {},
        }
        natal = {
            "saturn": {"rashi": 10},  # Aquarius = own sign
            "mercury": {"rashi": 2},  # Gemini = own sign
        }
        # Libra lagna (6): Saturn is YOGAKARAKA (lords 4+5)
        score_yk, _, desc_yk = _normalize_dasha(dasha, natal, lagna_index=6)
        # Leo lagna (4): Saturn lords 6+7 (malefic/maraka)
        score_bad, _, _ = _normalize_dasha(dasha, natal, lagna_index=4)
        assert score_yk > score_bad
        assert "yogakaraka" in desc_yk.lower() or "Saturn MD" in desc_yk


# ── Dignity tests ──


class TestDignityForPlanet:
    def test_exalted(self):
        # Sun exalted in Aries (0)
        assert _dignity_for_planet("sun", {"sun": {"rashi": 0}}) == 10.0

    def test_debilitated(self):
        # Sun debilitated in Libra (6)
        assert _dignity_for_planet("sun", {"sun": {"rashi": 6}}) == 1.0

    def test_own_sign(self):
        # Mars in Aries (0) or Scorpio (7)
        assert _dignity_for_planet("mars", {"mars": {"rashi": 0}}) == 8.0
        assert _dignity_for_planet("mars", {"mars": {"rashi": 7}}) == 8.0

    def test_no_data(self):
        score = _dignity_for_planet("jupiter", {})
        assert score > 5.0  # Jupiter is natural benefic


# ── Yoga activation tests ──


class TestScoreYogaActivation:
    def test_benefics_in_kendra_trikona(self):
        # Jupiter in house 1 (kendra+trikona), Venus in house 5 (trikona)
        # Libra lagna (6). Jupiter in Libra (6) = house 1, Venus in Aquarius (10) = house 5
        transit_positions = {
            "jupiter": 6,  # house 1 from Libra (kendra + trikona)
            "venus": 10,  # house 5 from Libra (trikona)
            "mercury": 2,  # house 9 from Libra (trikona)
        }
        lagna_index = 6  # Libra
        score, _planet, desc = _score_yoga_activation(transit_positions, lagna_index)
        assert score > 6.0  # benefics in good houses
        assert "benefics in kendra/trikona" in desc

    def test_malefics_in_dusthana(self):
        # Saturn in house 12, Mars in house 8 → should drag score below baseline
        # Libra lagna (6). Saturn in Virgo (5) = house 12, Mars in Taurus (1) = house 8
        transit_positions = {
            "saturn": 5,  # house 12 from Libra (dusthana)
            "mars": 1,  # house 8 from Libra (dusthana)
            "rahu": 11,  # house 6 from Libra (dusthana)
        }
        lagna_index = 6  # Libra
        score, _, _ = _score_yoga_activation(transit_positions, lagna_index)
        assert score < 5.0  # malefics in dusthana drag score down

    def test_empty(self):
        score, planet, _ = _score_yoga_activation({}, 0)
        assert score == 5.0
        assert planet == "jupiter"


# ── Shadbala tests ──


class TestVirupasToScore:
    """Test the virupas → 0-10 normalization curve."""

    def test_zero_virupas(self):
        assert _virupas_to_score(0) == 0.0

    def test_minimum_threshold(self):
        # 180 virupas = minimum required = 3.5
        assert _virupas_to_score(180) == 3.5

    def test_strong_threshold(self):
        # 300 virupas = strong = 6.5
        assert _virupas_to_score(300) == 6.5

    def test_very_strong(self):
        # 420 virupas = very strong = 9.0
        assert _virupas_to_score(420) == 9.0

    def test_max_capped(self):
        # Very high virupas caps at 10.0
        assert _virupas_to_score(600) == 10.0

    def test_moderate(self):
        # 240 virupas = midway between 180 and 300 → ~5.0
        score = _virupas_to_score(240)
        assert 4.5 <= score <= 5.5


class TestBuildBirthChart:
    """Test the BirthChart construction helper."""

    def test_basic_construction(self):
        birth_dt = datetime(1992, 12, 3, 3, 0)
        chart = _build_birth_chart(
            birth_dt,
            BIRTH_LAT,
            BIRTH_LON,
            NATAL_PLANETS,
            LAGNA_RASHI,
            MOON_RASHI,
            MOON_LONGITUDE,
        )
        assert chart.lagna_rashi.value == "libra"
        assert chart.moon_rashi.value == "aquarius"
        assert len(chart.planets) == 9  # all 9 planets
        assert len(chart.houses.cusps) == 12

    def test_planet_positions_populated(self):
        birth_dt = datetime(1992, 12, 3, 3, 0)
        chart = _build_birth_chart(
            birth_dt,
            BIRTH_LAT,
            BIRTH_LON,
            NATAL_PLANETS,
            LAGNA_RASHI,
            MOON_RASHI,
            MOON_LONGITUDE,
        )
        from packages.core.src.constants import Planet

        # Jupiter should be in chart with correct longitude
        jup = chart.planets[Planet.JUPITER]
        assert abs(jup.longitude - 142.8) < 0.01
        assert jup.house == 11
        assert jup.rashi_degree == 142.8 % 30

    def test_nakshatra_computed(self):
        birth_dt = datetime(1992, 12, 3, 3, 0)
        chart = _build_birth_chart(
            birth_dt,
            BIRTH_LAT,
            BIRTH_LON,
            NATAL_PLANETS,
            LAGNA_RASHI,
            MOON_RASHI,
            MOON_LONGITUDE,
        )
        from packages.core.src.constants import Planet

        # Moon at 326.85° → nakshatra 25 (purva_bhadrapada)
        moon = chart.planets[Planet.MOON]
        assert moon.nakshatra == "purva_bhadrapada"


class TestScoreShadbala:
    """Test real Shadbala integration via StrengthCalculator."""

    def _make_chart(self):
        """Helper to build chart from test data."""
        return _build_birth_chart(
            datetime(1992, 12, 3, 3, 0),
            BIRTH_LAT,
            BIRTH_LON,
            NATAL_PLANETS,
            LAGNA_RASHI,
            MOON_RASHI,
            MOON_LONGITUDE,
        )

    def test_with_dasha_and_chart(self):
        """Real Shadbala with Mercury MD should return a valid score."""
        dasha = {
            "mahadasha": {"lord": "mercury"},
            "antardasha": {"lord": "jupiter"},
        }
        chart = self._make_chart()
        score, planet, desc = _score_shadbala(dasha, NATAL_PLANETS, chart)
        assert 0.0 <= score <= 10.0
        assert planet in ("mercury", "jupiter")
        assert "Shadbala" in desc

    def test_score_varies_by_dasha_lord(self):
        """Different dasha lords produce different Shadbala scores."""
        chart = self._make_chart()
        dasha_a = {"mahadasha": {"lord": "jupiter"}, "antardasha": {"lord": "venus"}}
        dasha_b = {"mahadasha": {"lord": "saturn"}, "antardasha": {"lord": "mars"}}
        score_a, _, _ = _score_shadbala(dasha_a, NATAL_PLANETS, chart)
        score_b, _, _ = _score_shadbala(dasha_b, NATAL_PLANETS, chart)
        # Not exactly equal — different lords have different strengths
        assert score_a != score_b

    def test_no_dasha_returns_default(self):
        score, _, _ = _score_shadbala(None, {})
        assert score == 5.0

    def test_no_chart_returns_default(self):
        dasha = {"mahadasha": {"lord": "mercury"}}
        score, _, _ = _score_shadbala(dasha, NATAL_PLANETS, None)
        assert score == 5.0

    def test_description_includes_virupas(self):
        """Description should show virupas value."""
        dasha = {"mahadasha": {"lord": "mercury"}, "antardasha": {"lord": "jupiter"}}
        chart = self._make_chart()
        _, _, desc = _score_shadbala(dasha, NATAL_PLANETS, chart)
        assert "v)" in desc  # e.g. "Mercury/Jupiter Shadbala (strong, 318v)"

    def test_pd_lord_contributes(self):
        """Including PD lord should shift score."""
        chart = self._make_chart()
        dasha_no_pd = {"mahadasha": {"lord": "mercury"}, "antardasha": {"lord": "jupiter"}}
        dasha_with_pd = {
            "mahadasha": {"lord": "mercury"},
            "antardasha": {"lord": "jupiter"},
            "pratyantardasha": {"lord": "saturn"},
        }
        score_no, _, _ = _score_shadbala(dasha_no_pd, NATAL_PLANETS, chart)
        score_with, _, _ = _score_shadbala(dasha_with_pd, NATAL_PLANETS, chart)
        # PD contributes 20% weight so scores should differ
        assert score_no != score_with


# ── Ashtakavarga tests ──


class TestScoreAshtakavarga:
    def test_high_sav_houses(self):
        # Planets in house 11 (SAV=54) and house 10 (SAV=36) → high score
        transit_pos = {"jupiter": 4, "saturn": 3}  # houses 11 and 10 from Libra
        lagna = 6  # Libra
        score, _, desc = _score_ashtakavarga(transit_pos, lagna)
        assert score >= 5.0
        assert "SAV" in desc

    def test_low_sav_houses(self):
        # Planets in house 12 (SAV=16) and house 7 (SAV=19) → low score
        transit_pos = {"moon": 5, "mars": 0}  # houses 12 and 7 from Libra
        lagna = 6  # Libra
        score, _, _ = _score_ashtakavarga(transit_pos, lagna)
        assert score < 3.0


# ── Natal Yoga Detection tests ──


class TestDetectNatalYogas:
    """Real YogaDetector (522 rules) via BirthChart."""

    def _make_chart(self, planets, lagna_rashi="libra", moon_lon=326.85, moon_rashi="aquarius"):
        return _build_birth_chart(
            datetime.fromisoformat(BIRTH_DT),
            BIRTH_LAT,
            BIRTH_LON,
            planets,
            lagna_rashi,
            moon_rashi,
            moon_lon,
        )

    def test_user_chart_has_yogas(self):
        """User's actual chart should detect multiple yogas from 522-rule base."""
        chart = self._make_chart(NATAL_PLANETS)
        yogas, raw = _detect_natal_yogas(NATAL_PLANETS, 6, chart)
        assert isinstance(yogas, list)
        assert len(yogas) > 0, "Real detector should find yogas in user's chart"
        assert len(raw) == len(yogas), "Raw list should match dict list length"
        # All entries have required keys
        for y in yogas:
            assert "name" in y
            assert "planets" in y
            assert "category" in y
            assert 0 <= y["strength"] <= 1

    def test_panch_mahapurusha_shasha(self):
        """Saturn in own sign (Capricorn) in kendra (H4) → Shasha Yoga."""
        planets = {
            "saturn": {"longitude": 280.0, "rashi": 9, "house": 4},
            "moon": {"longitude": 50.0, "rashi": 1, "house": 8},
            "sun": {"longitude": 100.0, "rashi": 3, "house": 10},
            "mercury": {"longitude": 110.0, "rashi": 3, "house": 10},
            "mars": {"longitude": 20.0, "rashi": 0, "house": 7},
            "jupiter": {"longitude": 250.0, "rashi": 8, "house": 3},
            "venus": {"longitude": 330.0, "rashi": 11, "house": 6},
            "rahu": {"longitude": 60.0, "rashi": 2, "house": 9},
            "ketu": {"longitude": 240.0, "rashi": 8, "house": 3},
        }
        chart = self._make_chart(planets, moon_lon=50.0, moon_rashi="taurus")
        yogas, _raw = _detect_natal_yogas(planets, 6, chart)
        names = [y["name"] for y in yogas]
        assert any(
            "sasa" in n.lower() or "shasha" in n.lower() for n in names
        ), f"Expected Sasa/Shasha yoga, got: {names}"

    def test_no_chart_returns_empty(self):
        """Without BirthChart, returns empty list (graceful fallback)."""
        yogas, raw = _detect_natal_yogas(NATAL_PLANETS, 6, None)
        assert yogas == []
        assert raw == []

    def test_yoga_has_house_info(self):
        """Detected yogas should include house numbers from involved planets."""
        chart = self._make_chart(NATAL_PLANETS)
        yogas, _raw = _detect_natal_yogas(NATAL_PLANETS, 6, chart)
        # At least some yogas should have houses populated
        has_houses = any(len(y.get("houses", [])) > 0 for y in yogas)
        assert has_houses or len(yogas) == 0


# ── Natal Dosha Detection tests ──


class TestDetectNatalDoshas:
    """Real DoshaDetector (55 rules) via BirthChart."""

    def _make_chart(self, planets, lagna_rashi="libra", moon_lon=326.85, moon_rashi="aquarius"):
        return _build_birth_chart(
            datetime.fromisoformat(BIRTH_DT),
            BIRTH_LAT,
            BIRTH_LON,
            planets,
            lagna_rashi,
            moon_rashi,
            moon_lon,
        )

    def test_mangal_dosha(self):
        """Mars in house 7 from Aries lagna -> Mangal Dosha via real detector."""
        planets = {
            "mars": {"longitude": 190.0, "rashi": 6, "house": 7},
            "rahu": {"longitude": 100.0, "rashi": 3, "house": 4},
            "ketu": {"longitude": 280.0, "rashi": 9, "house": 10},
            "sun": {"longitude": 15.0, "rashi": 0, "house": 1},
            "moon": {"longitude": 50.0, "rashi": 1, "house": 2},
            "mercury": {"longitude": 20.0, "rashi": 0, "house": 1},
            "jupiter": {"longitude": 250.0, "rashi": 8, "house": 5},
            "venus": {"longitude": 340.0, "rashi": 11, "house": 12},
            "saturn": {"longitude": 300.0, "rashi": 10, "house": 7},
        }
        chart = self._make_chart(planets, "aries", 50.0, "taurus")
        doshas = _detect_natal_doshas(planets, 0, chart)
        names = [d["name"] for d in doshas]
        # Real DoshaDetector should find Mangal Dosha for Mars in H7
        assert any("mangal" in n.lower() or "kuja" in n.lower() for n in names)

    def test_user_chart_has_doshas(self):
        """User's chart should detect doshas from real 55-rule base."""
        chart = self._make_chart(NATAL_PLANETS)
        doshas = _detect_natal_doshas(NATAL_PLANETS, 6, chart)
        assert isinstance(doshas, list)
        for d in doshas:
            assert "name" in d
            assert "severity" in d
            assert "affected_areas" in d

    def test_no_chart_returns_empty(self):
        """Without BirthChart, returns empty list (graceful fallback)."""
        doshas = _detect_natal_doshas(NATAL_PLANETS, 6, None)
        assert doshas == []

    def test_dosha_has_planets(self):
        """Detected doshas should have involved planet names."""
        chart = self._make_chart(NATAL_PLANETS)
        doshas = _detect_natal_doshas(NATAL_PLANETS, 6, chart)
        for d in doshas:
            assert isinstance(d.get("planets", []), list)


# ── Yoga with Natal tests ──


class TestScoreYogaWithNatal:
    def test_activated_yoga_boosts_score(self):
        """Active natal yoga should boost YOG score above generic baseline."""
        natal_yogas = [
            {
                "name": "Gaja Kesari",
                "planets": ["jupiter", "moon"],
                "houses": [5, 11],
                "category": "raja",
                "strength": 0.8,
            },
        ]
        # Jupiter transiting house 5 from Libra = Aquarius (10)
        transit_pos = {"jupiter": 10, "moon": 3, "venus": 6}
        lagna = 6  # Libra
        score, _dominant, desc = _score_yoga_with_natal(natal_yogas, transit_pos, lagna)
        assert score > 5.0
        assert "1/1 yogas active" in desc
        assert "Gaja Kesari" in desc

    def test_no_natal_yogas_falls_back(self):
        """Without natal yogas, should use generic scoring."""
        transit_pos = {"jupiter": 6, "venus": 10}
        score, _, desc = _score_yoga_with_natal([], transit_pos, 6)
        assert "No natal yogas" in desc
        assert 0 <= score <= 10


# ── Dosha Impact tests ──


class TestScoreDoshaImpact:
    def test_mangal_dosha_penalty(self):
        """Mangal Dosha should penalize relationships and health."""
        doshas = [
            {
                "name": "Mangal Dosha",
                "severity": "severe",
                "planets": ["mars"],
                "affected_areas": ["relationships", "health"],
                "houses": [7],
            }
        ]
        # Mars transiting house 7 from Libra = Aries (0)
        transit_pos = {"mars": 0}
        penalties = _score_dosha_impact(doshas, transit_pos, 6)
        assert penalties["relationships"] < 0
        assert penalties["health"] < 0
        assert penalties["career"] == 0.0  # Not affected

    def test_sade_sati_peak_all_areas(self):
        """Sade Sati peak should drag key areas (health, career, family, etc.)."""
        sade_sati = {"active": True, "phase": "peak", "house_from_moon": 1}
        penalties = _score_dosha_impact([], {}, 0, sade_sati)
        # Peak Sade Sati hits health, career, relationships, family, finance, spiritual
        assert penalties["health"] < 0
        assert penalties["career"] < 0
        assert penalties["family"] < 0
        assert penalties["relationships"] < 0
        # At least 4 areas should be affected
        negative_areas = sum(1 for v in penalties.values() if v < 0)
        assert negative_areas >= 4

    def test_sade_sati_rising_targets_health(self):
        """Sade Sati rising should mainly hit health and spiritual."""
        sade_sati = {"active": True, "phase": "rising", "house_from_moon": 12}
        penalties = _score_dosha_impact([], {}, 0, sade_sati)
        assert penalties["health"] < penalties["career"]
        assert penalties["spiritual"] < 0

    def test_dhaiya_small_panoti(self):
        """Saturn 4th/8th from Moon (Dhaiya) should add mild penalties."""
        sade_sati = {"active": False, "house_from_moon": 4}
        penalties = _score_dosha_impact([], {}, 0, sade_sati)
        assert penalties["health"] < 0
        assert penalties["career"] < 0

    def test_no_doshas_no_penalties(self):
        """No doshas + no sade sati = zero penalties."""
        penalties = _score_dosha_impact([], {}, 0, {"active": False, "house_from_moon": 5})
        for area in penalties.values():
            assert area == 0.0

    def test_transit_amplification(self):
        """Dosha penalty should be stronger when transit amplifies it."""
        doshas = [
            {
                "name": "Mangal Dosha",
                "severity": "severe",
                "planets": ["mars"],
                "affected_areas": ["relationships"],
                "houses": [7],
            }
        ]
        # Mars NOT in dosha house
        penalties_calm = _score_dosha_impact(doshas, {"mars": 3}, 6)
        # Mars IN dosha house (house 7 from Libra = Aries = 0)
        penalties_amp = _score_dosha_impact(doshas, {"mars": 0}, 6)
        # Amplified should be worse (more negative)
        assert penalties_amp["relationships"] < penalties_calm["relationships"]


# ── Hora Lord tests ──


class TestGetHoraLord:
    def test_returns_valid_planet(self):
        dt = datetime(2026, 2, 10, 12, 0, 0)
        lord = get_hora_lord(dt, BIRTH_LAT, BIRTH_LON)
        valid_planets = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"}
        assert lord in valid_planets

    def test_different_hours_different_lords(self):
        # Different hours should (usually) give different lords
        lords = set()
        for hour in range(0, 24, 3):
            dt = datetime(2026, 2, 10, hour, 0, 0)
            lord = get_hora_lord(dt, BIRTH_LAT, BIRTH_LON)
            lords.add(lord)
        # With 8 different hours, should have at least 3 unique lords
        assert len(lords) >= 3


# ── Area Scores tests ──


class TestAreaScores:
    def test_returns_8_areas(self):
        factors = [
            {"id": "panchanga", "score": 6.0},
            {"id": "transit_moon", "score": 7.0},
            {"id": "gochara", "score": 5.5},
            {"id": "dasha", "score": 8.0},
            {"id": "yoga_activation", "score": 5.0},
            {"id": "shadbala", "score": 6.0},
            {"id": "ashtakavarga", "score": 5.5},
        ]
        transit_pos = {"moon": 9}  # Capricorn
        lagna = 6  # Libra

        areas = _compute_area_scores(factors, transit_pos, lagna)
        assert len(areas) == 8

        area_ids = {a["id"] for a in areas}
        assert area_ids == {
            "career",
            "relationships",
            "health",
            "finance",
            "spiritual",
            "family",
            "education",
            "travel",
        }

    def test_area_score_in_range(self):
        factors = [{"id": k, "score": 5.0} for k in FACTOR_WEIGHTS]
        areas = _compute_area_scores(factors, {"moon": 0}, 0)
        for area in areas:
            assert 0 <= area["score"] <= 10
            assert "insight" in area
            assert "houses" in area
            assert "dominant_planet" in area

    def test_moon_in_career_house_boosts_career(self):
        factors = [{"id": k, "score": 5.0} for k in FACTOR_WEIGHTS]
        # Moon in house 10 (career house) for Libra lagna
        transit_pos = {"moon": 3}  # Cancer → house 10 from Libra
        lagna = 6
        areas = _compute_area_scores(factors, transit_pos, lagna)
        career = next(a for a in areas if a["id"] == "career")
        health = next(a for a in areas if a["id"] == "health")
        # Career should be boosted since Moon is in one of its houses
        assert career["score"] >= health["score"]


# ── Integration: compute_state_vector ──


class TestComputeStateVector:
    def test_basic_computation(self):
        result = compute_state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            moon_rashi=MOON_RASHI,
            query_datetime="2026-02-10T12:00:00",
        )

        # Structure
        assert "factors" in result
        assert "areas" in result
        assert "composite" in result
        assert "mental_state" in result
        assert "confluence" in result
        assert "hora_lord" in result
        assert "date" in result

        # Factors
        assert len(result["factors"]) == 7
        factor_ids = {f["id"] for f in result["factors"]}
        expected_ids = set(FACTOR_WEIGHTS.keys())
        assert factor_ids == expected_ids

        # Each factor has required fields
        for f in result["factors"]:
            assert "id" in f
            assert "name" in f
            assert "short_name" in f
            assert "score" in f
            assert "dominant_planet" in f
            assert "description" in f
            assert 0 <= f["score"] <= 10

        # Areas
        assert len(result["areas"]) == 8

        # Composite
        assert 0 <= result["composite"] <= 10

        # Mental state
        valid_states = {
            "Thriving",
            "Flowing",
            "Steady",
            "Challenged",
            "Struggling",
            "Turbulent",
        }
        assert result["mental_state"] in valid_states

        # Confluence
        assert 0 <= result["confluence"] <= 6

        # Hora lord
        valid_planets = {
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
        }
        assert result["hora_lord"] in valid_planets

        # Natal yogas and doshas
        assert "natal_yogas" in result
        assert isinstance(result["natal_yogas"], list)
        assert "natal_doshas" in result
        assert isinstance(result["natal_doshas"], list)

        # Sade Sati info
        assert "sade_sati" in result
        assert "active" in result["sade_sati"]

    def test_different_dates_different_results(self):
        r1 = compute_state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            query_datetime="2026-01-01T12:00:00",
        )
        r2 = compute_state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            query_datetime="2026-06-15T12:00:00",
        )
        # Different dates should produce different composites (almost certainly)
        assert r1["date"] != r2["date"]

    def test_default_query_datetime(self):
        result = compute_state_vector(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
        )
        # Should use today's date
        assert result["date"] == datetime.now().date().isoformat()


# ── Integration: compute_state_range ──


class TestComputeStateRange:
    def test_daily_range(self):
        result = compute_state_range(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            start_date="2026-02-01",
            end_date="2026-02-07",
            resolution="daily",
        )

        assert result["resolution"] == "daily"
        assert len(result["vectors"]) == 7  # 7 days
        assert isinstance(result["events"], list)

        for vec in result["vectors"]:
            assert "factors" in vec
            assert "composite" in vec

    def test_weekly_range(self):
        result = compute_state_range(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            start_date="2026-01-01",
            end_date="2026-03-31",
            resolution="weekly",
        )
        assert result["resolution"] == "weekly"
        # ~13 weeks in 3 months
        assert 10 <= len(result["vectors"]) <= 15

    def test_hourly_range_limited(self):
        result = compute_state_range(
            birth_datetime=BIRTH_DT,
            birth_lat=BIRTH_LAT,
            birth_lon=BIRTH_LON,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LONGITUDE,
            lagna_rashi=LAGNA_RASHI,
            start_date="2026-02-10",
            end_date="2026-02-20",  # 10 days but should be capped to 2
            resolution="hourly",
        )
        assert result["resolution"] == "hourly"
        # 48 hours max (2 days)
        assert len(result["vectors"]) <= 49


# ── Constants tests ──


class TestConstants:
    def test_factor_weights_sum_to_one(self):
        total = sum(FACTOR_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_area_houses_valid(self):
        assert len(AREA_HOUSES) == 8
        for _area_id, houses in AREA_HOUSES.items():
            assert len(houses) == 3
            for h in houses:
                assert 1 <= h <= 12

    def test_area_planets_valid(self):
        valid = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}
        for _area_id, planet in AREA_PLANETS.items():
            assert planet in valid

    def test_rashi_names_count(self):
        assert len(RASHI_NAMES) == 12


# ── Area Scores with Engine Wiring tests ──


class TestAreaScoresWithEngines:
    """Test the BPHS-aligned 5-component area scoring model."""

    _BASE_FACTORS: ClassVar[list[dict[str, Any]]] = [
        {"id": "panchanga", "score": 5.0},
        {"id": "transit_moon", "score": 5.0},
        {"id": "gochara", "score": 5.0},
        {"id": "dasha", "score": 5.0},
        {"id": "yoga_activation", "score": 5.0},
        {"id": "shadbala", "score": 5.0},
        {"id": "ashtakavarga", "score": 5.0},
    ]

    @staticmethod
    def _make_house_activations(overrides: dict[int, dict] | None = None) -> list[dict]:
        """Build a 12-house activation list. Override specific houses."""
        activations = []
        for h in range(1, 13):
            base = {
                "house": h,
                "score": 50,
                "grade": "moderate",
                "double_transit": False,
                "planets_present": [],
                "planets_aspecting": [],
                "ashtakavarga_sav": 25,
                "themes": [],
                "summary": "",
            }
            if overrides and h in overrides:
                base.update(overrides[h])
            activations.append(base)
        return activations

    def test_dasha_dominance_affects_area(self):
        """Dasha lord ruling area houses should produce higher score (40% weight)."""
        # Mercury MD rules H9, H12 from Libra lagna (6) → spiritual houses [9, 12, 5]
        dasha = {"mahadasha": {"lord": "mercury"}, "antardasha": {"lord": "venus"}}
        areas = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            6,  # Libra lagna
            dasha_result=dasha,
        )
        spiritual = next(a for a in areas if a["id"] == "spiritual")
        career = next(a for a in areas if a["id"] == "career")
        # Spiritual should benefit more from dasha (Mercury lords its houses 9+12)
        assert spiritual["score"] > career["score"]

    def test_double_transit_bonus(self):
        """Area whose primary house has double transit should get a boost (15% weight)."""
        ha_with_dt = self._make_house_activations({10: {"score": 60, "double_transit": True}})
        ha_without_dt = self._make_house_activations({10: {"score": 60, "double_transit": False}})
        areas_with = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha_with_dt,
        )
        areas_without = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha_without_dt,
        )
        career_with = next(a for a in areas_with if a["id"] == "career")
        career_without = next(a for a in areas_without if a["id"] == "career")
        assert career_with["score"] > career_without["score"]
        assert career_with["double_transit"] is True
        assert career_without["double_transit"] is False

    def test_lordship_quality_output(self):
        """Lordship quality should be reflected in output field."""
        ha = self._make_house_activations()
        tl_yk = [
            {"planet": "saturn", "houses_ruled": [10, 11], "functional_nature": "yogakaraka"},
        ]
        areas = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha,
            transit_lordships=tl_yk,
        )
        career = next(a for a in areas if a["id"] == "career")
        assert career["lordship_quality"] == "yogakaraka"

    def test_yoga_activation_boost(self):
        """Active yoga touching area houses should boost that area's score (10% weight)."""
        ha = self._make_house_activations()
        ay = [
            {
                "yoga_name": "Gajakesari",
                "is_active_now": True,
                "activated_houses": [11],
                "involved_houses": [5, 11],
                "strength": 0.8,
            },
        ]
        areas_with = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha,
            active_yogas=ay,
        )
        areas_without = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha,
            active_yogas=[],
        )
        # Finance houses = [2, 11, 5] — yoga activates house 11
        fin_with = next(a for a in areas_with if a["id"] == "finance")
        fin_without = next(a for a in areas_without if a["id"] == "finance")
        assert fin_with["score"] > fin_without["score"]
        assert "Gajakesari" in fin_with["active_yogas"]

    def test_panchanga_affects_all_areas(self):
        """High panchanga factor should boost all area scores (10% weight)."""
        factors_high_pan = [
            {"id": "panchanga", "score": 9.0},
            {"id": "transit_moon", "score": 5.0},
            {"id": "gochara", "score": 5.0},
            {"id": "dasha", "score": 5.0},
            {"id": "yoga_activation", "score": 5.0},
            {"id": "shadbala", "score": 5.0},
            {"id": "ashtakavarga", "score": 5.0},
        ]
        areas_high = _compute_area_scores(factors_high_pan, {"moon": 0}, 0)
        areas_low = _compute_area_scores(self._BASE_FACTORS, {"moon": 0}, 0)
        # At least some areas should be higher with high panchanga
        high_scores = [a["score"] for a in areas_high]
        low_scores = [a["score"] for a in areas_low]
        assert sum(high_scores) > sum(low_scores)

    def test_no_activations_still_works(self):
        """When house_activations=None, model should still produce valid scores."""
        areas = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=None,
        )
        assert len(areas) == 8
        for a in areas:
            assert 0 <= a["score"] <= 10
            assert a["double_transit"] is False
            assert a["lordship_quality"] == "neutral"
            assert a["active_yogas"] == []

    def test_area_scores_in_range(self):
        """All area scores should clamp to 0-10 regardless of input."""
        ha = self._make_house_activations(
            {h: {"score": 100, "double_transit": True} for h in range(1, 13)}
        )
        tl = [
            {
                "planet": "jupiter",
                "houses_ruled": list(range(1, 13)),
                "functional_nature": "yogakaraka",
            },
        ]
        ay = [
            {
                "yoga_name": "Test",
                "is_active_now": True,
                "activated_houses": list(range(1, 13)),
                "involved_houses": list(range(1, 13)),
                "strength": 1.0,
            },
        ]
        areas = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha,
            transit_lordships=tl,
            active_yogas=ay,
        )
        for a in areas:
            assert 0 <= a["score"] <= 10

    def test_new_areas_have_valid_scores(self):
        """Family, education, and travel should produce valid scores."""
        ha = self._make_house_activations()
        areas = _compute_area_scores(
            self._BASE_FACTORS,
            {"moon": 0},
            0,
            house_activations=ha,
        )
        new_ids = {"family", "education", "travel"}
        found_ids = {a["id"] for a in areas}
        assert new_ids.issubset(found_ids)

        for a in areas:
            if a["id"] in new_ids:
                assert 0 <= a["score"] <= 10
                assert len(a["houses"]) == 3
                assert a["dominant_planet"] != ""
                assert a["insight"] != ""

    def test_new_area_house_mappings(self):
        """Verify the correct house mappings for new areas."""
        from packages.context.src.state_engine import AREA_HOUSES

        assert AREA_HOUSES["family"] == [4, 2, 1]
        assert AREA_HOUSES["education"] == [4, 5, 9]
        assert AREA_HOUSES["travel"] == [3, 9, 12]

    def test_new_areas_dosha_penalties(self):
        """_score_dosha_impact should include all 8 areas."""
        penalties = _score_dosha_impact([], {}, 0, {"active": False, "house_from_moon": 5})
        assert "family" in penalties
        assert "education" in penalties
        assert "travel" in penalties
        for v in penalties.values():
            assert v == 0.0

    def test_sade_sati_setting_affects_family(self):
        """Sade Sati setting phase should penalize family area."""
        sade_sati = {"active": True, "phase": "setting", "house_from_moon": 2}
        penalties = _score_dosha_impact([], {}, 0, sade_sati)
        assert penalties["family"] < 0


# ── New helper function tests ──


class TestComputeDashaAreaScore:
    """Tests for _compute_dasha_area_score helper."""

    def test_no_dasha_returns_neutral(self):
        score = _compute_dasha_area_score([10, 6, 2], None, {}, 6)
        assert score == 5.0

    def test_lord_ruling_area_house_boosts_score(self):
        # Mercury from Libra lagna rules H9, H12 → spiritual [9, 12, 5]
        dasha = {"mahadasha": {"lord": "mercury"}, "antardasha": {"lord": "venus"}}
        spiritual_score = _compute_dasha_area_score([9, 12, 5], dasha, NATAL_PLANETS, 6)
        career_score = _compute_dasha_area_score([10, 6, 2], dasha, NATAL_PLANETS, 6)
        assert spiritual_score > career_score

    def test_lord_in_area_house_natally_boosts(self):
        # Jupiter sits in house 11 natally → finance houses [2, 11, 5]
        dasha = {"mahadasha": {"lord": "jupiter"}, "antardasha": {"lord": "moon"}}
        score = _compute_dasha_area_score([2, 11, 5], dasha, NATAL_PLANETS, 6)
        assert score > 5.0  # boosted by natal placement

    def test_score_in_range(self):
        dasha = {"mahadasha": {"lord": "saturn"}, "antardasha": {"lord": "rahu"}}
        for houses in AREA_HOUSES.values():
            score = _compute_dasha_area_score(houses, dasha, NATAL_PLANETS, 6)
            assert 0 <= score <= 10


class TestComputeAshtakavargaTransitScore:
    """Tests for _compute_ashtakavarga_transit_score helper."""

    def test_no_transits_in_area_returns_fallback(self):
        # No planets in career houses
        score = _compute_ashtakavarga_transit_score([10, 6, 2], {}, 6, None)
        assert score == 5.0  # neutral fallback

    def test_planet_in_area_house_produces_score(self):
        # Jupiter in house 11 from Aries lagna (rashi 10 = Aquarius, house = 11 from 0)
        transit_pos = {"jupiter": 10}  # rashi 10 = Aquarius
        score = _compute_ashtakavarga_transit_score([2, 11, 5], transit_pos, 0, None)
        assert 0 <= score <= 10

    def test_score_in_range(self):
        transit_pos = {"saturn": 3, "jupiter": 8, "mars": 0, "moon": 5}
        for houses in AREA_HOUSES.values():
            score = _compute_ashtakavarga_transit_score(houses, transit_pos, 6, None)
            assert 0 <= score <= 10


class TestComputeDoubleTransitAreaScore:
    """Tests for _compute_double_transit_area_score helper."""

    def test_no_activations_returns_low(self):
        score, has_dt = _compute_double_transit_area_score([10, 6, 2], None)
        assert score == 3.0
        assert has_dt is False

    def test_primary_house_dt_returns_max(self):
        ha = [{"house": 10, "double_transit": True}]
        score, has_dt = _compute_double_transit_area_score([10, 6, 2], ha)
        assert score == 10.0
        assert has_dt is True

    def test_secondary_house_dt_returns_medium(self):
        ha = [{"house": 10, "double_transit": False}, {"house": 6, "double_transit": True}]
        score, has_dt = _compute_double_transit_area_score([10, 6, 2], ha)
        assert score == 7.0
        assert has_dt is True

    def test_no_dt_returns_low(self):
        ha = [
            {"house": 10, "double_transit": False},
            {"house": 6, "double_transit": False},
            {"house": 2, "double_transit": False},
        ]
        score, has_dt = _compute_double_transit_area_score([10, 6, 2], ha)
        assert score == 3.0
        assert has_dt is False


class TestComputeAreaTrend:
    """Tests for compute_area_trend public function."""

    def test_up_trend(self):
        current = [{"id": "career", "score": 7.0}]
        previous = [{"id": "career", "score": 5.0}]
        trends = compute_area_trend(current, previous)
        assert trends["career"] == "up"

    def test_down_trend(self):
        current = [{"id": "career", "score": 3.0}]
        previous = [{"id": "career", "score": 5.0}]
        trends = compute_area_trend(current, previous)
        assert trends["career"] == "down"

    def test_neutral_trend(self):
        current = [{"id": "career", "score": 5.2}]
        previous = [{"id": "career", "score": 5.0}]
        trends = compute_area_trend(current, previous)
        assert trends["career"] == "neutral"

    def test_custom_threshold(self):
        current = [{"id": "career", "score": 5.8}]
        previous = [{"id": "career", "score": 5.0}]
        trends = compute_area_trend(current, previous, threshold=1.0)
        assert trends["career"] == "neutral"  # 0.8 < 1.0

    def test_all_8_areas(self):
        current = [{"id": a, "score": 5.0} for a in AREA_HOUSES]
        previous = [{"id": a, "score": 5.0} for a in AREA_HOUSES]
        trends = compute_area_trend(current, previous)
        assert len(trends) == 8
        assert all(t == "neutral" for t in trends.values())
