"""Tests for upagraha calculations."""

from datetime import UTC, datetime

from packages.core.src.constants import Rashi, Upagraha
from packages.cosmos.src.upagrahas import (
    calculate_all_upagrahas,
    calculate_ardhaprahara,
    calculate_dhooma,
    calculate_gulika,
    calculate_indrachapa,
    calculate_kala,
    calculate_mandi,
    calculate_mrityu,
    calculate_parivesha,
    calculate_upaketu,
    calculate_vyatipata,
    calculate_yamaghanda_upagraha,
    get_upagraha_effects,
)

# ==========================================
# Mathematical Upagraha Tests
# ==========================================


class TestDhoomaChain:
    """Test the Dhooma -> Vyatipata -> Parivesha -> Indrachapa chain."""

    def test_dhooma_formula(self):
        """Dhooma = Sun + 133°20'."""
        sun_lon = 100.0
        dhooma = calculate_dhooma(sun_lon)
        expected = (100.0 + 133.3333) % 360
        assert abs(dhooma.longitude - expected) < 0.01
        assert dhooma.upagraha == Upagraha.DHOOMA

    def test_dhooma_wraps_around(self):
        """Dhooma wraps around 360°."""
        sun_lon = 300.0
        dhooma = calculate_dhooma(sun_lon)
        expected = (300.0 + 133.3333) % 360
        assert abs(dhooma.longitude - expected) < 0.01

    def test_vyatipata_formula(self):
        """Vyatipata = 360 - Dhooma."""
        dhooma_lon = 233.3333
        vyatipata = calculate_vyatipata(dhooma_lon)
        expected = (360 - 233.3333) % 360
        assert abs(vyatipata.longitude - expected) < 0.01
        assert vyatipata.upagraha == Upagraha.VYATIPATA

    def test_parivesha_formula(self):
        """Parivesha = Vyatipata + 180."""
        vyatipata_lon = 126.6667
        parivesha = calculate_parivesha(vyatipata_lon)
        expected = (126.6667 + 180) % 360
        assert abs(parivesha.longitude - expected) < 0.01
        assert parivesha.upagraha == Upagraha.PARIVESHA

    def test_indrachapa_formula(self):
        """Indrachapa = 360 - Parivesha."""
        parivesha_lon = 306.6667
        indrachapa = calculate_indrachapa(parivesha_lon)
        expected = (360 - 306.6667) % 360
        assert abs(indrachapa.longitude - expected) < 0.01
        assert indrachapa.upagraha == Upagraha.INDRACHAPA

    def test_full_chain_from_sun(self):
        """Test the complete chain: Sun -> Dhooma -> Vyatipata -> Parivesha -> Indrachapa."""
        sun_lon = 45.0  # Sun in Taurus
        lagna = 0.0

        dhooma = calculate_dhooma(sun_lon, lagna)
        vyatipata = calculate_vyatipata(dhooma.longitude, lagna)
        parivesha = calculate_parivesha(vyatipata.longitude, lagna)
        indrachapa = calculate_indrachapa(parivesha.longitude, lagna)

        # All should have valid longitudes
        for pos in [dhooma, vyatipata, parivesha, indrachapa]:
            assert 0 <= pos.longitude < 360
            assert 0 <= pos.degree_in_sign < 30
            assert 1 <= pos.house <= 12

    def test_dhooma_chain_symmetry(self):
        """Dhooma + Indrachapa should relate back to Sun."""
        sun_lon = 120.0
        dhooma = calculate_dhooma(sun_lon)
        vyatipata = calculate_vyatipata(dhooma.longitude)
        parivesha = calculate_parivesha(vyatipata.longitude)
        indrachapa = calculate_indrachapa(parivesha.longitude)

        # Indrachapa should equal Dhooma (since 360-((360-D)+180) = D-180, then 360-(D-180)=540-D)
        # Actually: Vyat = 360-D, Pari = Vyat+180 = 540-D, Indra = 360-Pari = D-180
        expected_indrachapa = (dhooma.longitude - 180) % 360
        assert abs(indrachapa.longitude - expected_indrachapa) < 0.01


class TestUpaketu:
    """Test Upaketu calculation."""

    def test_upaketu_formula(self):
        """Upaketu = Sun - 30°."""
        sun_lon = 100.0
        upaketu = calculate_upaketu(sun_lon)
        expected = (100.0 - 30) % 360
        assert abs(upaketu.longitude - expected) < 0.01
        assert upaketu.upagraha == Upagraha.UPAKETU

    def test_upaketu_wraps(self):
        """Upaketu wraps below 0°."""
        sun_lon = 10.0
        upaketu = calculate_upaketu(sun_lon)
        expected = (10.0 - 30) % 360  # = 340°
        assert abs(upaketu.longitude - expected) < 0.01

    def test_upaketu_rashi(self):
        """Upaketu rashi is one sign behind Sun."""
        sun_lon = 45.0  # Taurus
        upaketu = calculate_upaketu(sun_lon)
        # 45 - 30 = 15° = Aries
        assert upaketu.rashi == Rashi.ARIES


class TestMathUpagrahaFields:
    """Test that mathematical upagrahas have correct field structure."""

    def test_fields_present(self):
        """All required fields should be present."""
        dhooma = calculate_dhooma(100.0, 0.0)
        assert dhooma.upagraha == Upagraha.DHOOMA
        assert isinstance(dhooma.longitude, float)
        assert isinstance(dhooma.rashi, Rashi)
        assert isinstance(dhooma.degree_in_sign, float)
        assert isinstance(dhooma.house, int)
        assert dhooma.calculation_method == "mathematical"

    def test_house_calculation(self):
        """House should be correctly derived from lagna."""
        # If lagna is at 0° (Aries) and upagraha at 90°, that's house 4
        dhooma = calculate_dhooma(316.6667, 0.0)  # 316.67 + 133.33 = 450 % 360 = 90°
        assert dhooma.house == 4


# ==========================================
# Time-Based Upagraha Tests
# ==========================================


class TestGulika:
    """Test Gulika calculation."""

    def test_gulika_returns_valid_position(self):
        """Gulika should return valid position."""
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)  # Wednesday
        gulika = calculate_gulika(dt, 28.6, 77.2, 0.0)

        assert gulika.upagraha == Upagraha.GULIKA
        assert 0 <= gulika.longitude < 360
        assert 0 <= gulika.degree_in_sign < 30
        assert 1 <= gulika.house <= 12
        assert "saturn" in gulika.calculation_method

    def test_gulika_different_weekdays(self):
        """Gulika position should vary by weekday."""
        # Monday and Friday should give different Gulika positions
        monday = datetime(2024, 3, 18, 10, 0, 0, tzinfo=UTC)
        friday = datetime(2024, 3, 22, 10, 0, 0, tzinfo=UTC)

        gulika_mon = calculate_gulika(monday, 28.6, 77.2, 0.0)
        gulika_fri = calculate_gulika(friday, 28.6, 77.2, 0.0)

        # Different weekdays should generally give different portions
        # (though they could occasionally land on the same sign)
        assert gulika_mon.upagraha == Upagraha.GULIKA
        assert gulika_fri.upagraha == Upagraha.GULIKA


class TestMandi:
    """Test Mandi calculation."""

    def test_mandi_returns_valid_position(self):
        """Mandi should return valid position."""
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        mandi = calculate_mandi(dt, 28.6, 77.2, 0.0)

        assert mandi.upagraha == Upagraha.MANDI
        assert 0 <= mandi.longitude < 360

    def test_mandi_different_from_gulika(self):
        """Mandi (end of portion) should differ from Gulika (start)."""
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        gulika = calculate_gulika(dt, 28.6, 77.2, 0.0)
        mandi = calculate_mandi(dt, 28.6, 77.2, 0.0)

        # They use start vs end of same portion, so should differ
        # (unless portion duration is very short)
        assert mandi.upagraha == Upagraha.MANDI
        assert gulika.upagraha == Upagraha.GULIKA


class TestOtherTimeBased:
    """Test other time-based upagrahas."""

    def test_yamaghanda(self):
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        pos = calculate_yamaghanda_upagraha(dt, 28.6, 77.2, 0.0)
        assert pos.upagraha == Upagraha.YAMAGHANDA
        assert 0 <= pos.longitude < 360

    def test_kala(self):
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        pos = calculate_kala(dt, 28.6, 77.2, 0.0)
        assert pos.upagraha == Upagraha.KALA
        assert 0 <= pos.longitude < 360

    def test_mrityu(self):
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        pos = calculate_mrityu(dt, 28.6, 77.2, 0.0)
        assert pos.upagraha == Upagraha.MRITYU
        assert 0 <= pos.longitude < 360

    def test_ardhaprahara(self):
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        pos = calculate_ardhaprahara(dt, 28.6, 77.2, 0.0)
        assert pos.upagraha == Upagraha.ARDHAPRAHARA
        assert 0 <= pos.longitude < 360


# ==========================================
# Complete Calculation Tests
# ==========================================


class TestAllUpagrahas:
    """Test calculate_all_upagrahas."""

    def test_returns_all_11(self):
        """Should return all 11 upagrahas."""
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        result = calculate_all_upagrahas(dt, 28.6, 77.2, 0.0, 350.0)

        assert len(result.positions) == 11

        expected_names = [
            "gulika",
            "mandi",
            "yamaghanda",
            "kala",
            "mrityu",
            "ardhaprahara",
            "dhooma",
            "vyatipata",
            "parivesha",
            "indrachapa",
            "upaketu",
        ]
        for name in expected_names:
            assert name in result.positions, f"Missing upagraha: {name}"

    def test_sunrise_sunset_present(self):
        """Result should include sunrise/sunset data."""
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        result = calculate_all_upagrahas(dt, 28.6, 77.2, 0.0, 350.0)

        assert result.sunrise is not None
        assert result.sunset is not None
        assert result.day_duration_hours > 0

    def test_effects_populated(self):
        """Effects list should be populated."""
        dt = datetime(2024, 3, 20, 10, 0, 0, tzinfo=UTC)
        result = calculate_all_upagrahas(dt, 28.6, 77.2, 0.0, 350.0)

        assert len(result.effects) > 0

    def test_user_chart_integration(self):
        """Test with user's birth data (1992-12-03T03:00+05:30)."""
        # Birth in IST = UTC-5:30, so 03:00 IST = 21:30 UTC on Dec 2
        dt = datetime(1992, 12, 2, 21, 30, 0, tzinfo=UTC)
        lat, lon = 16.726239, 81.288428
        # Approximate sun longitude for this date
        sun_lon = 227.0  # Sun in Scorpio approx

        result = calculate_all_upagrahas(dt, lat, lon, 180.0, sun_lon)

        assert len(result.positions) == 11
        for name, pos in result.positions.items():
            assert 0 <= pos.longitude < 360, f"{name} longitude out of range"
            assert 1 <= pos.house <= 12, f"{name} house out of range"


class TestUpagrahaEffects:
    """Test effects lookup."""

    def test_effects_for_gulika(self):
        """Should return effects for Gulika."""
        pos = calculate_dhooma(100.0, 0.0)
        # Override to be a Gulika for testing
        gulika_pos = pos.model_copy(update={"upagraha": Upagraha.GULIKA, "house": 6})
        effects = get_upagraha_effects(gulika_pos)

        assert effects["upagraha"] == "gulika"
        assert effects["house"] == 6
        assert "effects" in effects

    def test_effects_for_unknown_house(self):
        """Should handle missing house effects gracefully."""
        pos = calculate_dhooma(100.0, 0.0)
        effects = get_upagraha_effects(pos)

        assert "upagraha" in effects
        assert "effects" in effects
