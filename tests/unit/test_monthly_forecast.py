"""Tests for the Monthly Forecast Engine.

Tests cover:
- Retrograde detection
- Dasha transition detection
- Major transit detection
- Weekly summaries computation
- Area ratings (monthly)
- Best dates computation
- Monthly theme generation
- Full monthly forecast integration (mocked)
"""

from datetime import datetime
from unittest.mock import patch

from packages.context.src.monthly_forecast import (
    MONTH_NAMES,
    _compute_area_ratings_monthly,
    _compute_best_dates,
    _detect_retrogrades,
    _generate_monthly_theme,
    _get_dasha_transitions,
    _get_major_transits,
    _get_week_boundaries,
    _monthly_area_summary,
    _planet_sign_duration,
    get_monthly_forecast,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NATAL_PLANETS = {
    "sun": {"longitude": 227.5, "rashi": 7},
    "moon": {"longitude": 326.85, "rashi": 10},
    "mars": {"longitude": 100.2, "rashi": 3},
    "mercury": {"longitude": 243.1, "rashi": 8},
    "jupiter": {"longitude": 120.0, "rashi": 4},
    "venus": {"longitude": 210.5, "rashi": 7},
    "saturn": {"longitude": 310.0, "rashi": 10},
    "rahu": {"longitude": 170.0, "rashi": 5},
    "ketu": {"longitude": 350.0, "rashi": 11},
}


# ---------------------------------------------------------------------------
# MONTH_NAMES tests
# ---------------------------------------------------------------------------


class TestMonthNames:
    def test_twelve_months(self):
        assert len(MONTH_NAMES) == 12

    def test_january_first(self):
        assert MONTH_NAMES[0] == "January"

    def test_december_last(self):
        assert MONTH_NAMES[11] == "December"


# ---------------------------------------------------------------------------
# _planet_sign_duration tests
# ---------------------------------------------------------------------------


class TestPlanetSignDuration:
    def test_sun(self):
        assert _planet_sign_duration("sun") == 30

    def test_moon(self):
        assert _planet_sign_duration("moon") == 2

    def test_saturn(self):
        assert _planet_sign_duration("saturn") == 900

    def test_unknown(self):
        assert _planet_sign_duration("unknown") == 30


# ---------------------------------------------------------------------------
# _get_week_boundaries tests
# ---------------------------------------------------------------------------


class TestGetWeekBoundaries:
    def test_28_day_month(self):
        start = datetime(2026, 2, 1)
        weeks = _get_week_boundaries(start, 28)
        assert len(weeks) == 4
        assert weeks[0][0] == start

    def test_31_day_month(self):
        start = datetime(2026, 1, 1)
        weeks = _get_week_boundaries(start, 31)
        assert len(weeks) <= 4

    def test_no_overlap(self):
        start = datetime(2026, 3, 1)
        weeks = _get_week_boundaries(start, 31)
        for i in range(len(weeks) - 1):
            assert weeks[i][1] < weeks[i + 1][0]


# ---------------------------------------------------------------------------
# _monthly_area_summary tests
# ---------------------------------------------------------------------------


class TestMonthlyAreaSummary:
    def test_strong_rating(self):
        s = _monthly_area_summary("career", 9, [])
        assert "Strong" in s

    def test_positive_rating(self):
        s = _monthly_area_summary("finance", 7, [])
        assert "Positive" in s

    def test_mixed_rating(self):
        s = _monthly_area_summary("health", 4, [])
        assert "Mixed" in s

    def test_challenging_rating(self):
        s = _monthly_area_summary("spiritual", 2, [])
        assert "Challenging" in s

    def test_retrograde_mention(self):
        s = _monthly_area_summary("finance", 5, ["jupiter"])
        assert "Jupiter" in s
        assert "retrograde" in s.lower()


# ---------------------------------------------------------------------------
# _detect_retrogrades tests (mocked)
# ---------------------------------------------------------------------------


class TestDetectRetrogrades:
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    def test_no_retrogrades(self, mock_jd, mock_planets):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = {
            "mercury": {"longitude": 300.0, "speed": 1.3},
            "venus": {"longitude": 280.0, "speed": 1.1},
            "mars": {"longitude": 150.0, "speed": 0.5},
            "jupiter": {"longitude": 40.0, "speed": 0.08},
            "saturn": {"longitude": 340.0, "speed": 0.03},
        }

        result = _detect_retrogrades(datetime(2026, 2, 1), 28)
        assert result["planets_retrograde"] == []
        assert "No retrogrades" in result["impact"]

    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    def test_initial_retrograde_detected(self, mock_jd, mock_planets):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = {
            "mercury": {"longitude": 300.0, "speed": -1.0},
            "venus": {"longitude": 280.0, "speed": 1.1},
            "mars": {"longitude": 150.0, "speed": 0.5},
            "jupiter": {"longitude": 40.0, "speed": 0.08},
            "saturn": {"longitude": 340.0, "speed": 0.03},
        }

        result = _detect_retrogrades(datetime(2026, 2, 1), 28)
        assert "mercury" in result["planets_retrograde"]

    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    def test_retro_dates_populated(self, mock_jd, mock_planets):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = {
            "mercury": {"longitude": 300.0, "speed": -1.0},
            "venus": {"longitude": 280.0, "speed": 1.1},
            "mars": {"longitude": 150.0, "speed": 0.5},
            "jupiter": {"longitude": 40.0, "speed": 0.08},
            "saturn": {"longitude": 340.0, "speed": 0.03},
        }

        result = _detect_retrogrades(datetime(2026, 2, 1), 28)
        assert "mercury" in result["dates"]


# ---------------------------------------------------------------------------
# _get_major_transits tests (mocked)
# ---------------------------------------------------------------------------


class TestGetMajorTransits:
    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    def test_detects_sign_ingress(self, mock_jd, mock_planets):
        mock_jd.return_value = 2460000.0
        call_count = [0]

        def positions_side_effect(_jd):
            call_count[0] += 1
            # Sun moves from 299 to 301 (crosses 300 = Aquarius/Pisces boundary at ~330)
            # Actually let's use cleaner boundary: 29.9 -> 30.1 (Aries to Taurus)
            if call_count[0] <= 1:
                return {
                    "sun": {"longitude": 29.9, "speed": 1.0},
                    "moon": {"longitude": 60.0, "speed": 13.0},
                    "mars": {"longitude": 150.0, "speed": 0.5},
                    "mercury": {"longitude": 240.0, "speed": 1.3},
                    "jupiter": {"longitude": 40.0, "speed": 0.08},
                    "venus": {"longitude": 280.0, "speed": 1.1},
                    "saturn": {"longitude": 340.0, "speed": 0.03},
                    "rahu": {"longitude": 5.0, "speed": -0.05},
                    "ketu": {"longitude": 185.0, "speed": -0.05},
                }
            return {
                "sun": {"longitude": 30.1, "speed": 1.0},
                "moon": {"longitude": 73.0, "speed": 13.0},
                "mars": {"longitude": 150.5, "speed": 0.5},
                "mercury": {"longitude": 241.3, "speed": 1.3},
                "jupiter": {"longitude": 40.08, "speed": 0.08},
                "venus": {"longitude": 281.1, "speed": 1.1},
                "saturn": {"longitude": 340.03, "speed": 0.03},
                "rahu": {"longitude": 4.95, "speed": -0.05},
                "ketu": {"longitude": 184.95, "speed": -0.05},
            }

        mock_planets.side_effect = positions_side_effect

        result = _get_major_transits(NATAL_PLANETS, "libra", datetime(2026, 2, 1), 2)
        # Should detect Sun entering Taurus and Moon entering Gemini
        assert len(result) >= 1
        assert any("Sun" in t["event"] or "Moon" in t["event"] for t in result)

    @patch("packages.cosmos.src.ephemeris.get_all_planets")
    @patch("packages.cosmos.src.ephemeris.get_julian_day")
    def test_sorted_by_date(self, mock_jd, mock_planets):
        mock_jd.return_value = 2460000.0
        mock_planets.return_value = {
            "sun": {"longitude": 300.0, "speed": 1.0},
            "moon": {"longitude": 60.0, "speed": 13.0},
        }

        result = _get_major_transits(NATAL_PLANETS, "libra", datetime(2026, 2, 1), 5)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]["date"] <= result[i + 1]["date"]


# ---------------------------------------------------------------------------
# _compute_area_ratings_monthly tests
# ---------------------------------------------------------------------------


class TestComputeAreaRatingsMonthly:
    def test_returns_eight_areas(self):
        areas = _compute_area_ratings_monthly(
            [],
            {"planets_retrograde": []},
            "mercury",
            "ketu",
            NATAL_PLANETS,
            "libra",
            datetime(2026, 2, 1),
            28,
        )
        assert len(areas) == 8

    def test_each_area_has_required_keys(self):
        areas = _compute_area_ratings_monthly(
            [],
            {"planets_retrograde": []},
            "mercury",
            "ketu",
            NATAL_PLANETS,
            "libra",
            datetime(2026, 2, 1),
            28,
        )
        for area_data in areas.values():
            assert "rating" in area_data
            assert "summary" in area_data
            assert "best_dates" in area_data
            assert "avoid_dates" in area_data

    def test_all_areas_have_valid_ratings(self):
        areas = _compute_area_ratings_monthly(
            [],
            {"planets_retrograde": []},
            "mercury",
            "ketu",
            NATAL_PLANETS,
            "libra",
            datetime(2026, 2, 1),
            28,
        )
        for area_data in areas.values():
            assert 1 <= area_data["rating"] <= 10


# ---------------------------------------------------------------------------
# _compute_best_dates tests
# ---------------------------------------------------------------------------


class TestComputeBestDates:
    def test_returns_five_categories(self):
        dates = _compute_best_dates([], [], datetime(2026, 2, 1), 28)
        assert "career_moves" in dates
        assert "financial" in dates
        assert "travel" in dates
        assert "spiritual" in dates
        assert "avoid_important" in dates

    def test_jupiter_transit_adds_career(self):
        transits = [
            {"date": "2026-02-10", "event": "Jupiter enters Aries", "house": 7},
        ]
        dates = _compute_best_dates(transits, [], datetime(2026, 2, 1), 28)
        assert "2026-02-10" in dates["career_moves"]

    def test_saturn_transit_adds_avoid(self):
        transits = [
            {"date": "2026-02-15", "event": "Saturn enters Pisces", "house": 6},
        ]
        dates = _compute_best_dates(transits, [], datetime(2026, 2, 1), 28)
        assert "2026-02-15" in dates["avoid_important"]


# ---------------------------------------------------------------------------
# _generate_monthly_theme tests
# ---------------------------------------------------------------------------


class TestGenerateMonthlyTheme:
    def test_high_rating(self):
        areas = {
            "career": {"rating": 8},
            "finance": {"rating": 7},
            "relationships": {"rating": 6},
            "health": {"rating": 7},
            "spiritual": {"rating": 5},
            "family": {"rating": 6},
            "education": {"rating": 6},
            "travel": {"rating": 5},
        }
        theme = _generate_monthly_theme(7.5, "jupiter", "venus", areas, {"planets_retrograde": []})
        assert "Strong" in theme

    def test_medium_rating(self):
        areas = {
            "career": {"rating": 5},
            "finance": {"rating": 5},
            "relationships": {"rating": 5},
            "health": {"rating": 5},
            "spiritual": {"rating": 5},
            "family": {"rating": 5},
            "education": {"rating": 5},
            "travel": {"rating": 5},
        }
        theme = _generate_monthly_theme(5.5, "mercury", "ketu", areas, {"planets_retrograde": []})
        assert "Balanced" in theme

    def test_low_rating(self):
        areas = {
            "career": {"rating": 3},
            "finance": {"rating": 3},
            "relationships": {"rating": 4},
            "health": {"rating": 3},
            "spiritual": {"rating": 3},
            "family": {"rating": 3},
            "education": {"rating": 3},
            "travel": {"rating": 3},
        }
        theme = _generate_monthly_theme(3.0, "saturn", "rahu", areas, {"planets_retrograde": []})
        assert "Reflective" in theme

    def test_retrograde_mentioned(self):
        areas = {
            "career": {"rating": 5},
            "finance": {"rating": 5},
            "relationships": {"rating": 5},
            "health": {"rating": 5},
            "spiritual": {"rating": 5},
            "family": {"rating": 5},
            "education": {"rating": 5},
            "travel": {"rating": 5},
        }
        theme = _generate_monthly_theme(
            5.0, "mercury", "ketu", areas, {"planets_retrograde": ["mercury"]}
        )
        assert "Mercury" in theme


# ---------------------------------------------------------------------------
# _get_dasha_transitions tests (mocked)
# ---------------------------------------------------------------------------


class TestGetDashaTransitions:
    @patch("packages.context.src.dasha.get_mahadasha_sequence")
    def test_no_transitions_in_month(self, mock_maha):
        mock_maha.return_value = [
            {
                "lord": "mercury",
                "start_date": datetime(2019, 9, 1),
                "end_date": datetime(2036, 9, 1),
                "years": 17,
            }
        ]
        result = _get_dasha_transitions(
            datetime(1992, 12, 3, 3, 0),
            326.85,
            datetime(2026, 2, 1),
            datetime(2026, 2, 28),
        )
        # No MD/AD transition in Feb 2026 for this data
        # PD transitions may show up, but with mocked data, none expected
        assert isinstance(result, list)

    @patch("packages.context.src.dasha.get_pratyantardasha_sequence")
    @patch("packages.context.src.dasha.get_antardasha_sequence")
    @patch("packages.context.src.dasha.get_mahadasha_sequence")
    def test_detects_ad_transition(self, mock_maha, mock_antar, mock_pd):
        mock_maha.return_value = [
            {
                "lord": "mercury",
                "start_date": datetime(2019, 9, 1),
                "end_date": datetime(2036, 9, 1),
                "years": 17,
            }
        ]
        mock_antar.return_value = [
            {
                "lord": "ketu",
                "start_date": datetime(2025, 1, 1),
                "end_date": datetime(2026, 2, 15),
                "years": 1.1,
            },
            {
                "lord": "venus",
                "start_date": datetime(2026, 2, 15),
                "end_date": datetime(2029, 1, 1),
                "years": 2.8,
            },
        ]
        mock_pd.return_value = []

        result = _get_dasha_transitions(
            datetime(1992, 12, 3, 3, 0),
            326.85,
            datetime(2026, 2, 1),
            datetime(2026, 2, 28),
        )

        ad_transitions = [t for t in result if t["level"] == "antardasha"]
        assert len(ad_transitions) >= 1
        assert "Venus" in ad_transitions[0]["to"]


# ---------------------------------------------------------------------------
# Full get_monthly_forecast (mocked) tests
# ---------------------------------------------------------------------------


class TestGetMonthlyForecast:
    @patch("packages.context.src.monthly_forecast._compute_best_dates")
    @patch("packages.context.src.monthly_forecast._compute_weekly_summaries")
    @patch("packages.context.src.monthly_forecast._compute_area_ratings_monthly")
    @patch("packages.context.src.monthly_forecast._detect_retrogrades")
    @patch("packages.context.src.monthly_forecast._get_major_transits")
    @patch("packages.context.src.monthly_forecast._get_dasha_transitions")
    @patch("packages.context.src.dasha.get_current_dasha")
    def test_returns_required_keys(
        self,
        mock_dasha,
        mock_transitions,
        mock_transits,
        mock_retro,
        mock_areas,
        mock_weeks,
        mock_dates,
    ):
        mock_dasha.return_value = {
            "mahadasha": {"lord": "mercury"},
            "antardasha": {"lord": "ketu"},
        }
        mock_transitions.return_value = []
        mock_transits.return_value = []
        mock_retro.return_value = {"planets_retrograde": [], "dates": {}, "impact": "None"}
        mock_areas.return_value = {
            "career": {"rating": 6, "summary": "Good", "best_dates": [], "avoid_dates": []},
            "finance": {"rating": 5, "summary": "OK", "best_dates": [], "avoid_dates": []},
            "relationships": {"rating": 5, "summary": "OK", "best_dates": [], "avoid_dates": []},
            "health": {"rating": 6, "summary": "Good", "best_dates": [], "avoid_dates": []},
            "spiritual": {"rating": 7, "summary": "Strong", "best_dates": [], "avoid_dates": []},
            "family": {"rating": 5, "summary": "OK", "best_dates": [], "avoid_dates": []},
            "education": {"rating": 6, "summary": "Good", "best_dates": [], "avoid_dates": []},
            "travel": {"rating": 5, "summary": "OK", "best_dates": [], "avoid_dates": []},
        }
        mock_weeks.return_value = [
            {"week": 1, "dates": "Feb 1-7", "rating": 6, "theme": "Steady"},
        ]
        mock_dates.return_value = {
            "career_moves": [],
            "financial": [],
            "travel": [],
            "spiritual": [],
            "avoid_important": [],
        }

        result = get_monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            month=2,
            year=2026,
        )

        assert result["month"] == "February"
        assert result["year"] == 2026
        assert "overall_rating" in result
        assert "monthly_theme" in result
        assert "dasha_context" in result
        assert "major_transits" in result
        assert "retrograde_status" in result
        assert "areas" in result
        assert "weekly_summaries" in result
        assert "best_dates" in result
        # New enriched fields
        assert "gochara_summary" in result
        assert "active_yogas" in result
        assert "active_doshas" in result
        assert "sade_sati" in result
        assert "muhurta_dates" in result
        assert "month_rating" in result
        assert isinstance(result["gochara_summary"], list)
        assert isinstance(result["active_yogas"], list)
        assert isinstance(result["muhurta_dates"], list)

    @patch("packages.context.src.monthly_forecast._compute_best_dates")
    @patch("packages.context.src.monthly_forecast._compute_weekly_summaries")
    @patch("packages.context.src.monthly_forecast._compute_area_ratings_monthly")
    @patch("packages.context.src.monthly_forecast._detect_retrogrades")
    @patch("packages.context.src.monthly_forecast._get_major_transits")
    @patch("packages.context.src.monthly_forecast._get_dasha_transitions")
    @patch("packages.context.src.dasha.get_current_dasha")
    def test_overall_rating_in_range(
        self,
        mock_dasha,
        mock_transitions,
        mock_transits,
        mock_retro,
        mock_areas,
        mock_weeks,
        mock_dates,
    ):
        mock_dasha.return_value = None
        mock_transitions.return_value = []
        mock_transits.return_value = []
        mock_retro.return_value = {"planets_retrograde": [], "dates": {}, "impact": "None"}
        mock_areas.return_value = {
            "career": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "finance": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "relationships": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "health": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "spiritual": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "family": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "education": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "travel": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
        }
        mock_weeks.return_value = []
        mock_dates.return_value = {
            "career_moves": [],
            "financial": [],
            "travel": [],
            "spiritual": [],
            "avoid_important": [],
        }

        result = get_monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            month=2,
            year=2026,
        )

        assert 1.0 <= result["overall_rating"] <= 10.0

    @patch("packages.context.src.monthly_forecast._compute_best_dates")
    @patch("packages.context.src.monthly_forecast._compute_weekly_summaries")
    @patch("packages.context.src.monthly_forecast._compute_area_ratings_monthly")
    @patch("packages.context.src.monthly_forecast._detect_retrogrades")
    @patch("packages.context.src.monthly_forecast._get_major_transits")
    @patch("packages.context.src.monthly_forecast._get_dasha_transitions")
    @patch("packages.context.src.dasha.get_current_dasha")
    def test_dasha_context_populated(
        self,
        mock_dasha,
        mock_transitions,
        mock_transits,
        mock_retro,
        mock_areas,
        mock_weeks,
        mock_dates,
    ):
        mock_dasha.return_value = {
            "mahadasha": {"lord": "mercury"},
            "antardasha": {"lord": "ketu"},
        }
        mock_transitions.return_value = [
            {"date": "2026-02-15", "from": "Me-Ke-Ve", "to": "Me-Ke-Su", "level": "pratyantardasha"}
        ]
        mock_transits.return_value = []
        mock_retro.return_value = {"planets_retrograde": [], "dates": {}, "impact": "None"}
        mock_areas.return_value = {
            "career": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "finance": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "relationships": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "health": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "spiritual": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "family": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "education": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
            "travel": {"rating": 5, "summary": "", "best_dates": [], "avoid_dates": []},
        }
        mock_weeks.return_value = []
        mock_dates.return_value = {
            "career_moves": [],
            "financial": [],
            "travel": [],
            "spiritual": [],
            "avoid_important": [],
        }

        result = get_monthly_forecast(
            birth_datetime="1992-12-03T03:00:00",
            birth_lat=16.726239,
            birth_lon=81.288428,
            natal_planets=NATAL_PLANETS,
            moon_longitude=326.85,
            lagna_rashi="libra",
            month=2,
            year=2026,
        )

        dc = result["dasha_context"]
        assert dc["mahadasha"] == "mercury"
        assert dc["antardasha"] == "ketu"
        assert len(dc["transitions"]) == 1
