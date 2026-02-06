"""Tests for packages/context/src/event_correlator.py — Event Correlation Engine."""

from datetime import datetime

from packages.context.src.event_correlator import (
    EVENT_TYPE_HOUSES,
    EVENT_TYPE_PLANETS,
    _accuracy_label,
    _get_house_from_lagna,
    _get_houses_owned_from_lagna,
    _rashi_name_to_idx,
    batch_correlate,
    correlate_event,
)

# Srikanth's birth data
BIRTH_DT = datetime(1992, 12, 3, 3, 0)
MOON_LON = 326.85  # Aquarius
LAGNA_RASHI = 6  # Libra

NATAL_PLANETS = {
    "sun": {"longitude": 227.5, "rashi": 7},
    "moon": {"longitude": 326.85, "rashi": 10},
    "mars": {"longitude": 85.0, "rashi": 2},
    "mercury": {"longitude": 240.0, "rashi": 8},
    "jupiter": {"longitude": 145.0, "rashi": 4},
    "venus": {"longitude": 210.0, "rashi": 7},
    "saturn": {"longitude": 310.0, "rashi": 10},
    "rahu": {"longitude": 170.0, "rashi": 5},
    "ketu": {"longitude": 350.0, "rashi": 11},
}


class TestHelpers:
    """Test helper functions."""

    def test_get_house_from_lagna(self):
        assert _get_house_from_lagna(6, 6) == 1

    def test_get_house_from_lagna_wraps(self):
        assert _get_house_from_lagna(5, 6) == 12

    def test_rashi_name_to_idx_aries(self):
        assert _rashi_name_to_idx("aries") == 0

    def test_rashi_name_to_idx_pisces(self):
        assert _rashi_name_to_idx("pisces") == 11

    def test_rashi_name_to_idx_case_insensitive(self):
        assert _rashi_name_to_idx("LIBRA") == 6

    def test_rashi_name_to_idx_unknown(self):
        assert _rashi_name_to_idx("unknown") == 0

    def test_get_houses_owned_mars(self):
        houses = _get_houses_owned_from_lagna("mars", 6)
        assert 7 in houses  # Aries -> house 7 from Libra
        assert 2 in houses  # Scorpio -> house 2 from Libra

    def test_accuracy_label_high(self):
        assert _accuracy_label(80) == "high"

    def test_accuracy_label_moderate(self):
        assert _accuracy_label(55) == "moderate"

    def test_accuracy_label_low(self):
        assert _accuracy_label(30) == "low"

    def test_accuracy_label_inconclusive(self):
        assert _accuracy_label(10) == "inconclusive"


class TestEventTypeData:
    """Test event type mappings."""

    def test_career_houses(self):
        assert 10 in EVENT_TYPE_HOUSES["career"]

    def test_marriage_houses(self):
        assert 7 in EVENT_TYPE_HOUSES["marriage"]

    def test_health_houses(self):
        assert 6 in EVENT_TYPE_HOUSES["health"]

    def test_career_planets(self):
        assert "sun" in EVENT_TYPE_PLANETS["career"]

    def test_marriage_planets(self):
        assert "venus" in EVENT_TYPE_PLANETS["marriage"]

    def test_all_event_types_have_houses(self):
        for event_type in EVENT_TYPE_HOUSES:
            assert len(EVENT_TYPE_HOUSES[event_type]) > 0

    def test_all_event_types_have_planets(self):
        for event_type in EVENT_TYPE_PLANETS:
            assert len(EVENT_TYPE_PLANETS[event_type]) > 0


class TestCorrelateEvent:
    """Test single event correlation."""

    def test_returns_expected_keys(self):
        result = correlate_event(
            event_date="2020-03-15",
            event_type="career",
            event_description="Got promoted",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        assert "event" in result
        assert "event_type" in result
        assert "date" in result
        assert "dasha_at_event" in result
        assert "transit_at_event" in result
        assert "correlation_score" in result
        assert "explanation" in result

    def test_event_description_preserved(self):
        result = correlate_event(
            event_date="2020-03-15",
            event_type="career",
            event_description="Got promoted to VP",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        assert result["event"] == "Got promoted to VP"

    def test_event_type_lowercase(self):
        result = correlate_event(
            event_date="2020-03-15",
            event_type="CAREER",
            event_description="Promotion",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        assert result["event_type"] == "career"

    def test_dasha_at_event_has_lords(self):
        result = correlate_event(
            event_date="2025-01-15",
            event_type="career",
            event_description="Job change",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        dasha = result["dasha_at_event"]
        assert "mahadasha" in dasha
        assert "antardasha" in dasha
        # Mercury MD for 2025
        assert dasha["mahadasha"] == "mercury"

    def test_transit_at_event_has_planets(self):
        result = correlate_event(
            event_date="2025-01-15",
            event_type="career",
            event_description="Job change",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        transit = result["transit_at_event"]
        assert "sun" in transit
        assert "moon" in transit
        assert "saturn" in transit

    def test_correlation_score_range(self):
        result = correlate_event(
            event_date="2025-01-15",
            event_type="career",
            event_description="Job change",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        assert 0 <= result["correlation_score"] <= 100

    def test_string_lagna_rashi(self):
        result = correlate_event(
            event_date="2025-01-15",
            event_type="career",
            event_description="Job change",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi="libra",
        )
        assert "correlation_score" in result

    def test_string_birth_datetime(self):
        result = correlate_event(
            event_date="2025-01-15",
            event_type="career",
            event_description="Job change",
            birth_datetime="1992-12-03T03:00:00",
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        assert "correlation_score" in result

    def test_yogas_active_list(self):
        result = correlate_event(
            event_date="2025-01-15",
            event_type="career",
            event_description="Job change",
            birth_datetime=BIRTH_DT,
            natal_planets=NATAL_PLANETS,
            moon_longitude=MOON_LON,
            lagna_rashi=LAGNA_RASHI,
        )
        assert isinstance(result["yogas_active"], list)


class TestBatchCorrelate:
    """Test batch event correlation."""

    def test_returns_expected_keys(self):
        events = [
            {"date": "2020-03-15", "type": "career", "description": "Promotion"},
            {"date": "2022-06-10", "type": "marriage", "description": "Got engaged"},
        ]
        birth_data = {
            "birth_datetime": BIRTH_DT,
            "natal_planets": NATAL_PLANETS,
            "moon_longitude": MOON_LON,
            "lagna_rashi": LAGNA_RASHI,
        }
        result = batch_correlate(events, birth_data)
        assert "events" in result
        assert "total_events" in result
        assert "average_correlation" in result
        assert "chart_accuracy_score" in result
        assert "accuracy_label" in result

    def test_total_events_count(self):
        events = [
            {"date": "2020-03-15", "type": "career", "description": "Promotion"},
        ]
        birth_data = {
            "birth_datetime": BIRTH_DT,
            "natal_planets": NATAL_PLANETS,
            "moon_longitude": MOON_LON,
            "lagna_rashi": LAGNA_RASHI,
        }
        result = batch_correlate(events, birth_data)
        assert result["total_events"] == 1

    def test_multiple_events(self):
        events = [
            {"date": "2020-03-15", "type": "career", "description": "Promotion"},
            {"date": "2021-11-01", "type": "health", "description": "Surgery"},
            {"date": "2023-05-20", "type": "travel", "description": "Moved abroad"},
        ]
        birth_data = {
            "birth_datetime": BIRTH_DT,
            "natal_planets": NATAL_PLANETS,
            "moon_longitude": MOON_LON,
            "lagna_rashi": LAGNA_RASHI,
        }
        result = batch_correlate(events, birth_data)
        assert result["total_events"] == 3
        assert len(result["events"]) == 3

    def test_accuracy_label_present(self):
        events = [
            {"date": "2020-03-15", "type": "career", "description": "Promotion"},
        ]
        birth_data = {
            "birth_datetime": BIRTH_DT,
            "natal_planets": NATAL_PLANETS,
            "moon_longitude": MOON_LON,
            "lagna_rashi": LAGNA_RASHI,
        }
        result = batch_correlate(events, birth_data)
        assert result["accuracy_label"] in ("high", "moderate", "low", "inconclusive")

    def test_empty_events(self):
        birth_data = {
            "birth_datetime": BIRTH_DT,
            "natal_planets": NATAL_PLANETS,
            "moon_longitude": MOON_LON,
            "lagna_rashi": LAGNA_RASHI,
        }
        result = batch_correlate([], birth_data)
        assert result["total_events"] == 0
        assert result["average_correlation"] == 0
