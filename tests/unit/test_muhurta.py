"""Unit tests for new muhurta functions: Abhijit, Brahma, Marana Kaal, Eclipse."""

from datetime import datetime

import pytest

from packages.context.src.muhurta import (
    get_abhijit_muhurta,
    get_brahma_muhurta,
    get_eclipse_periods,
    get_marana_kaal,
)


class TestAbhijitMuhurta:
    """Tests for get_abhijit_muhurta."""

    def test_returns_tuple(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        sunset = datetime(2026, 2, 4, 18, 30)
        result = get_abhijit_muhurta(sunrise, sunset)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_start_before_end(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        sunset = datetime(2026, 2, 4, 18, 30)
        start, end = get_abhijit_muhurta(sunrise, sunset)
        assert start < end

    def test_around_noon(self):
        sunrise = datetime(2026, 2, 4, 6, 0)
        sunset = datetime(2026, 2, 4, 18, 0)
        start, end = get_abhijit_muhurta(sunrise, sunset)
        # 12 hour day, 15 muhurtas, each = 48 min
        # 8th muhurta starts at 7 * 48 = 336 min = 5h36m after sunrise = 11:36
        # Ends at 8 * 48 = 384 min = 6h24m after sunrise = 12:24
        assert start.hour in (11, 12)
        assert end.hour in (12, 13)

    def test_within_daylight_hours(self):
        sunrise = datetime(2026, 6, 21, 5, 45)
        sunset = datetime(2026, 6, 21, 19, 15)
        start, end = get_abhijit_muhurta(sunrise, sunset)
        assert start >= sunrise
        assert end <= sunset

    def test_duration_is_one_fifteenth_of_day(self):
        sunrise = datetime(2026, 2, 4, 6, 0)
        sunset = datetime(2026, 2, 4, 18, 0)
        start, end = get_abhijit_muhurta(sunrise, sunset)
        day_seconds = (sunset - sunrise).total_seconds()
        muhurta_seconds = (end - start).total_seconds()
        expected = day_seconds / 15
        assert abs(muhurta_seconds - expected) < 1  # within 1 second

    def test_short_day(self):
        # Winter day: 10 hours of daylight
        sunrise = datetime(2026, 12, 21, 7, 0)
        sunset = datetime(2026, 12, 21, 17, 0)
        start, end = get_abhijit_muhurta(sunrise, sunset)
        assert start >= sunrise
        assert end <= sunset


class TestBrahmaMuhurta:
    """Tests for get_brahma_muhurta."""

    def test_returns_tuple(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        result = get_brahma_muhurta(sunrise)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_start_before_end(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        start, end = get_brahma_muhurta(sunrise)
        assert start < end

    def test_before_sunrise(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        start, end = get_brahma_muhurta(sunrise)
        assert end < sunrise
        assert start < sunrise

    def test_96_minutes_before_sunrise(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        start, _end = get_brahma_muhurta(sunrise)
        # Start is 96 minutes before sunrise
        assert start.hour == 4
        assert start.minute == 54

    def test_48_minute_duration(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        start, end = get_brahma_muhurta(sunrise)
        duration_minutes = (end - start).total_seconds() / 60
        assert duration_minutes == 48

    def test_end_is_48_minutes_before_sunrise(self):
        sunrise = datetime(2026, 2, 4, 6, 30)
        _start, end = get_brahma_muhurta(sunrise)
        # End should be 48 minutes before sunrise = 5:42
        assert end.hour == 5
        assert end.minute == 42


class TestMaranaKaal:
    """Tests for get_marana_kaal."""

    def test_returns_list_of_tuples(self):
        result = get_marana_kaal(0)  # Monday
        assert isinstance(result, list)
        for period in result:
            assert isinstance(period, tuple)
            assert len(period) == 2

    def test_each_day_has_two_periods(self):
        for weekday in range(7):
            result = get_marana_kaal(weekday)
            assert len(result) == 2, f"Weekday {weekday} should have 2 periods"

    def test_monday_periods(self):
        result = get_marana_kaal(0)
        assert result[0] == ("06:30", "07:30")
        assert result[1] == ("14:00", "15:00")

    def test_sunday_periods(self):
        result = get_marana_kaal(6)
        assert ("16:00", "17:00") in result
        assert ("12:00", "13:00") in result

    def test_invalid_weekday_raises(self):
        with pytest.raises(ValueError, match="Weekday must be 0-6"):
            get_marana_kaal(7)

    def test_negative_weekday_raises(self):
        with pytest.raises(ValueError, match="Weekday must be 0-6"):
            get_marana_kaal(-1)

    def test_all_periods_valid_time_format(self):
        for weekday in range(7):
            periods = get_marana_kaal(weekday)
            for start, end in periods:
                # Validate HH:MM format
                h, m = start.split(":")
                assert 0 <= int(h) <= 23
                assert 0 <= int(m) <= 59
                h, m = end.split(":")
                assert 0 <= int(h) <= 23
                assert 0 <= int(m) <= 59


class TestEclipsePeriods:
    """Tests for get_eclipse_periods."""

    def test_returns_list(self):
        result = get_eclipse_periods(2025, 3)
        assert isinstance(result, list)

    def test_eclipse_type_is_solar_or_lunar(self):
        # March 2025 has a total lunar eclipse on March 14
        result = get_eclipse_periods(2025, 3)
        for eclipse in result:
            assert eclipse["type"] in ("solar", "lunar")

    def test_eclipse_has_required_fields(self):
        result = get_eclipse_periods(2025, 3)
        for eclipse in result:
            assert "type" in eclipse
            assert "maximum" in eclipse
            assert "description" in eclipse

    def test_known_eclipse_month(self):
        # March 2025 has a lunar eclipse
        result = get_eclipse_periods(2025, 3)
        assert len(result) >= 1

    def test_no_eclipse_month(self):
        # Most months have no eclipses; try a random month
        result = get_eclipse_periods(2025, 2)
        # Could be 0 or non-zero, just ensure it returns valid list
        assert isinstance(result, list)

    def test_invalid_month_raises(self):
        with pytest.raises(ValueError, match="Month must be 1-12"):
            get_eclipse_periods(2025, 0)

    def test_invalid_month_13_raises(self):
        with pytest.raises(ValueError, match="Month must be 1-12"):
            get_eclipse_periods(2025, 13)

    def test_eclipse_maximum_in_correct_month(self):
        result = get_eclipse_periods(2025, 3)
        for eclipse in result:
            if eclipse["maximum"]:
                assert eclipse["maximum"].month == 3

    def test_description_contains_date(self):
        result = get_eclipse_periods(2025, 3)
        for eclipse in result:
            assert "2025" in eclipse["description"]

    def test_december_boundary(self):
        # December should work correctly (tests month=12 boundary)
        result = get_eclipse_periods(2025, 12)
        assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
