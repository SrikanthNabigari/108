"""Tests for the forecast knowledge module.

Verifies that knowledge-backed text generation works correctly
and produces human-readable output.
"""

from packages.context.src.forecast_knowledge import (
    build_daily_recommendations,
    build_daily_summary,
    build_monthly_recommendations,
    build_monthly_summary,
    build_weekly_recommendations,
    build_weekly_summary,
    get_antardasha_text,
    get_dasha_guide,
    get_double_transit_text,
    get_nakshatra_transit_text,
    get_tithi_guidance,
    get_transit_aspect_effect,
    get_vara_guidance,
)

# ---------------------------------------------------------------------------
# Lookup function tests
# ---------------------------------------------------------------------------


class TestVaraGuidance:
    def test_monday(self):
        v = get_vara_guidance("Monday")
        assert v["lord"] == "moon"
        assert len(v["good_for"]) > 0

    def test_saturday(self):
        v = get_vara_guidance("Saturday")
        assert v["lord"] == "saturn"

    def test_case_insensitive(self):
        v = get_vara_guidance("FRIDAY")
        assert v["lord"] == "venus"

    def test_unknown_day(self):
        v = get_vara_guidance("Xday")
        assert v["good_for"] == []


class TestTithiGuidance:
    def test_pratipada(self):
        t = get_tithi_guidance("Pratipada")
        assert len(t["good_for"]) > 0

    def test_shukla_saptami(self):
        t = get_tithi_guidance("Shukla Saptami")
        # Should match Saptami
        assert t["nature"] != ""

    def test_unknown(self):
        t = get_tithi_guidance("Unknown Tithi")
        assert t["good_for"] == []


class TestTransitAspectEffect:
    def test_sun_moon_conjunction(self):
        effect = get_transit_aspect_effect("sun", "moon", "conjunction")
        assert len(effect) > 0
        assert isinstance(effect, str)

    def test_saturn_moon_square(self):
        effect = get_transit_aspect_effect("saturn", "moon", "square")
        assert len(effect) > 0

    def test_unknown_combo(self):
        effect = get_transit_aspect_effect("xyz", "abc", "trine")
        assert effect == ""


class TestNakshatraTransitText:
    def test_moon_pushya(self):
        n = get_nakshatra_transit_text("moon", "Pushya")
        assert n["theme"] != ""

    def test_sun_ashwini(self):
        n = get_nakshatra_transit_text("sun", "ashwini")
        assert n["theme"] != ""

    def test_unknown_nakshatra(self):
        n = get_nakshatra_transit_text("moon", "Unknown")
        assert n["theme"] == ""


class TestAntardashaText:
    def test_mercury_ketu(self):
        ad = get_antardasha_text("mercury", "ketu")
        assert len(ad["general_effects"]) > 0

    def test_sun_moon(self):
        ad = get_antardasha_text("sun", "moon")
        assert ad["career"] != ""

    def test_unknown(self):
        ad = get_antardasha_text("xyz", "abc")
        assert ad["general_effects"] == []


class TestDashaGuide:
    def test_mercury(self):
        g = get_dasha_guide("mercury")
        assert g["theme"] != ""
        assert len(g.get("practical_advice", [])) > 0

    def test_unknown(self):
        g = get_dasha_guide("xyz")
        assert g == {}


class TestDoubleTransitText:
    def test_house_1(self):
        dt = get_double_transit_text(1)
        assert len(dt["themes"]) > 0
        assert dt["effect"] != ""

    def test_house_10(self):
        dt = get_double_transit_text(10)
        assert len(dt["typical_events"]) > 0

    def test_invalid_house(self):
        dt = get_double_transit_text(99)
        assert dt["themes"] == []


# ---------------------------------------------------------------------------
# Builder function tests
# ---------------------------------------------------------------------------


class TestBuildDailySummary:
    def test_returns_nonempty_string(self):
        summary = build_daily_summary(
            day_rating=7,
            moon_sign="aquarius",
            moon_nakshatra="Pushya",
            moon_house_from_lagna=5,
            dasha_md="mercury",
            dasha_ad="ketu",
            transit_aspects=[],
            is_chandrashtama=False,
        )
        assert isinstance(summary, str)
        assert len(summary) > 20

    def test_chandrashtama_mentioned(self):
        summary = build_daily_summary(
            day_rating=4,
            moon_sign="virgo",
            moon_nakshatra="Hasta",
            moon_house_from_lagna=12,
            dasha_md="mercury",
            dasha_ad="ketu",
            transit_aspects=[],
            is_chandrashtama=True,
        )
        assert "Chandrashtama" in summary

    def test_with_transit_aspects(self):
        summary = build_daily_summary(
            day_rating=6,
            moon_sign="gemini",
            moon_nakshatra="Ardra",
            moon_house_from_lagna=9,
            dasha_md="mercury",
            dasha_ad="venus",
            transit_aspects=[
                {"transit": "saturn", "natal": "moon", "aspect": "conjunction", "orb": 1.5},
            ],
            is_chandrashtama=False,
        )
        assert isinstance(summary, str)
        assert len(summary) > 20


class TestBuildDailyRecommendations:
    def test_returns_list_of_strings(self):
        recs = build_daily_recommendations(
            weekday="wednesday",
            tithi_name="Pratipada",
            moon_nakshatra="Pushya",
            dasha_md="mercury",
            dasha_ad="ketu",
            transit_aspects=[],
            is_chandrashtama=False,
        )
        assert isinstance(recs, list)
        assert all(isinstance(r, str) for r in recs)
        assert len(recs) >= 2

    def test_chandrashtama_included(self):
        recs = build_daily_recommendations(
            weekday="monday",
            tithi_name="Ashtami",
            moon_nakshatra="Rohini",
            dasha_md="mercury",
            dasha_ad="venus",
            transit_aspects=[],
            is_chandrashtama=True,
        )
        assert any("Chandrashtama" in r for r in recs)

    def test_max_six_items(self):
        recs = build_daily_recommendations(
            weekday="thursday",
            tithi_name="Pratipada",
            moon_nakshatra="Pushya",
            dasha_md="sun",
            dasha_ad="moon",
            transit_aspects=[
                {"transit": "jupiter", "natal": "sun", "aspect": "trine", "orb": 1.0},
            ],
            is_chandrashtama=True,
        )
        assert len(recs) <= 6


class TestBuildWeeklySummary:
    def test_returns_nonempty(self):
        summary = build_weekly_summary(
            overall_rating=6.5,
            dasha_md="mercury",
            dasha_ad="ketu",
            key_transits=[],
            areas={
                "career": {"rating": 7},
                "relationships": {"rating": 5},
                "health": {"rating": 6},
            },
        )
        assert isinstance(summary, str)
        assert len(summary) > 20


class TestBuildWeeklyRecommendations:
    def test_returns_list(self):
        recs = build_weekly_recommendations(
            dasha_md="mercury",
            dasha_ad="ketu",
            key_transits=[],
        )
        assert isinstance(recs, list)
        assert len(recs) >= 1


class TestBuildMonthlySummary:
    def test_returns_nonempty(self):
        summary = build_monthly_summary(
            month_rating=6.5,
            dasha_md="mercury",
            dasha_ad="ketu",
            double_transit_houses=[10],
            best_area="career",
            weakest_area="travel",
        )
        assert isinstance(summary, str)
        assert len(summary) > 20
        assert "Mercury" in summary


class TestBuildMonthlyRecommendations:
    def test_returns_list(self):
        recs = build_monthly_recommendations(
            dasha_md="mercury",
            dasha_ad="ketu",
            double_transit_houses=[10, 7],
        )
        assert isinstance(recs, list)
        assert len(recs) >= 1
        assert len(recs) <= 6
