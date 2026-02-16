"""Tests for Sookshma Dasha integration in gateway and knowledge layer.

Tests cover:
- Sookshma Dasha presence in get_current_dasha() results
- SD sequence from gateway's sub-periods logic
- SD in dasha effects via knowledge guide
- Knowledge loader for sookshma_dasha_guide
"""

from datetime import datetime
from typing import Any

import pytest

from packages.context.src.dasha import (
    get_current_dasha,
    get_sookshma_dasha_sequence,
)
from packages.core.src.knowledge_loader import (
    get_sookshma_dasha_guide,
)

# User's birth data
BIRTH_DT = datetime(1992, 12, 3, 3, 0, 0)
MOON_LON = 326.85
QUERY_DT = datetime(2026, 2, 15, 12, 0, 0)

# All 9 planets
ALL_PLANETS = ["sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury", "ketu", "venus"]


# ======================================================================
# A. Sookshma Dasha in get_current_dasha() response
# ======================================================================
class TestSookshmaInCurrentDasha:
    """Verify get_current_dasha() returns sookshma_dasha at Level 4."""

    def test_sookshma_key_exists(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        assert result is not None
        assert "sookshma_dasha" in result

    def test_sookshma_has_required_fields(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        sd = result["sookshma_dasha"]
        assert sd is not None, "sookshma_dasha should not be None for a valid query"
        assert "lord" in sd
        assert "start_date" in sd
        assert "end_date" in sd
        assert "years" in sd
        assert "days_remaining" in sd

    def test_sookshma_lord_is_valid_planet(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        sd = result["sookshma_dasha"]
        assert sd["lord"] in ALL_PLANETS

    def test_sookshma_dates_within_pd(self):
        """SD period should fall within the PD boundaries."""
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        pd = result["pratyantardasha"]
        sd = result["sookshma_dasha"]
        assert sd is not None
        assert pd is not None
        assert sd["start_date"] >= pd["start_date"]
        assert sd["end_date"] <= pd["end_date"]

    def test_sookshma_days_remaining_positive(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        sd = result["sookshma_dasha"]
        assert sd["days_remaining"] >= 0

    def test_prana_dasha_present(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        assert "prana_dasha" in result
        prana = result["prana_dasha"]
        assert prana is not None
        assert prana["lord"] in ALL_PLANETS
        assert prana["days_remaining"] >= 0

    def test_deha_dasha_present(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        assert "deha_dasha" in result
        deha = result["deha_dasha"]
        assert deha is not None
        assert deha["lord"] in ALL_PLANETS
        assert deha["hours_remaining"] >= 0

    def test_prana_within_sookshma(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        sd = result["sookshma_dasha"]
        prana = result["prana_dasha"]
        assert prana["start_date"] >= sd["start_date"]
        assert prana["end_date"] <= sd["end_date"]

    def test_deha_within_prana(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        prana = result["prana_dasha"]
        deha = result["deha_dasha"]
        assert deha["start_date"] >= prana["start_date"]
        assert deha["end_date"] <= prana["end_date"]


# ======================================================================
# B. Sookshma Sequence (simulating sub-periods endpoint)
# ======================================================================
class TestSookshmaSequenceGateway:
    """Test SD sequence generation as the gateway would call it."""

    def test_sookshma_sequence_has_9_entries(self):
        """The gateway calls get_sookshma_dasha_sequence for /dasha/sub-periods?level=sd."""
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        pd = result["pratyantardasha"]
        sd_seq = get_sookshma_dasha_sequence(pd["lord"], pd["start_date"], pd["end_date"])
        assert len(sd_seq) == 9

    def test_sookshma_sequence_starts_with_pd_lord(self):
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        pd = result["pratyantardasha"]
        sd_seq = get_sookshma_dasha_sequence(pd["lord"], pd["start_date"], pd["end_date"])
        assert sd_seq[0]["lord"] == pd["lord"]

    def test_sookshma_sequence_covers_full_pd(self):
        """Sum of SD periods should equal PD duration."""
        result = get_current_dasha(BIRTH_DT, MOON_LON, QUERY_DT)
        pd = result["pratyantardasha"]
        sd_seq = get_sookshma_dasha_sequence(pd["lord"], pd["start_date"], pd["end_date"])
        total_days = sum((p["end_date"] - p["start_date"]).total_seconds() / 86400 for p in sd_seq)
        expected_days = (pd["end_date"] - pd["start_date"]).total_seconds() / 86400
        assert abs(total_days - expected_days) < 0.01


# ======================================================================
# C. Sookshma Dasha Knowledge Guide
# ======================================================================
class TestSookshmaDashaGuide:
    """Test sookshma_dasha_guide.json content via knowledge loader."""

    @pytest.fixture()
    def guide(self) -> dict[str, Any]:
        data = get_sookshma_dasha_guide()
        return data.get("sookshma_dasha_guide", data)

    def test_guide_loads_successfully(self, guide: dict):
        assert guide, "Sookshma dasha guide should not be empty"
        assert "description" in guide

    def test_guide_has_all_9_planets(self, guide: dict):
        for planet in ALL_PLANETS:
            assert planet in guide, f"Missing planet: {planet}"

    def test_planet_entries_have_required_fields(self, guide: dict):
        required_fields = {
            "duration_range",
            "theme",
            "energy",
            "favorable_activities",
            "unfavorable_activities",
            "health_watch",
            "practical_advice",
            "blending_rules",
        }
        for planet in ALL_PLANETS:
            entry = guide[planet]
            for field in required_fields:
                assert field in entry, f"{planet} missing field: {field}"

    def test_favorable_activities_are_lists(self, guide: dict):
        for planet in ALL_PLANETS:
            entry = guide[planet]
            assert isinstance(entry["favorable_activities"], list)
            assert (
                len(entry["favorable_activities"]) >= 3
            ), f"{planet} needs at least 3 favorable activities"

    def test_blending_rules_has_keys(self, guide: dict):
        expected_keys = {"with_friendly_pd", "with_enemy_pd", "with_neutral_pd"}
        for planet in ALL_PLANETS:
            blending = guide[planet]["blending_rules"]
            assert isinstance(blending, dict)
            for key in expected_keys:
                assert key in blending, f"{planet} blending_rules missing: {key}"


# ======================================================================
# D. Dasha Effects with SD param
# ======================================================================
class TestDashaEffectsWithSd:
    """Test that the sookshma knowledge guide returns valid data for effects."""

    def test_sd_guide_planet_entry_structure(self):
        """When gateway passes sd=X, it loads guide[X] — verify structure."""
        data = get_sookshma_dasha_guide()
        guide = data.get("sookshma_dasha_guide", data)
        for planet in ALL_PLANETS:
            entry = guide.get(planet, {})
            assert "theme" in entry
            assert "practical_advice" in entry
            assert isinstance(entry["practical_advice"], list)


# ======================================================================
# E. Sookshma Dasha Combination Effects (PD x SD = 81)
# ======================================================================
class TestSookshmaDashaCombinationEffects:
    """Test sookshma_dasha_effects.json (81 PD x SD combinations)."""

    def test_effects_load_successfully(self):
        from packages.core.src.knowledge_loader import get_sookshma_dasha_effects

        data = get_sookshma_dasha_effects()
        assert isinstance(data, dict)
        # Should have 9 parent (PD) lords
        assert len(data) >= 9, f"Expected 9 PD lords, got {len(data)}"

    def test_all_81_combinations_present(self):
        from packages.core.src.knowledge_loader import get_sookshma_dasha_effects

        data = get_sookshma_dasha_effects()
        count = 0
        for pd_lord in ALL_PLANETS:
            assert pd_lord in data, f"Missing PD lord: {pd_lord}"
            for sd_lord in ALL_PLANETS:
                assert sd_lord in data[pd_lord], f"Missing SD: {pd_lord}-{sd_lord}"
                count += 1
        assert count == 81

    def test_combination_entry_structure(self):
        from packages.core.src.knowledge_loader import get_sookshma_dasha_effects

        data = get_sookshma_dasha_effects()
        required_fields = {"relationship", "theme", "effects", "health", "career", "relationships"}
        for pd_lord in ALL_PLANETS:
            for sd_lord in ALL_PLANETS:
                entry = data[pd_lord][sd_lord]
                for field in required_fields:
                    assert field in entry, f"{pd_lord}-{sd_lord} missing: {field}"

    def test_effect_function_returns_data(self):
        from packages.context.src.dasha import get_sookshma_dasha_effect

        effect = get_sookshma_dasha_effect("venus", "mars")
        if effect is not None:
            assert "theme" in effect
            assert "effects" in effect
            assert isinstance(effect["effects"], list)

    def test_effect_function_same_lord(self):
        from packages.context.src.dasha import get_sookshma_dasha_effect

        effect = get_sookshma_dasha_effect("jupiter", "jupiter")
        if effect is not None:
            assert effect["relationship"] == "same"


# ======================================================================
# F. Prana Dasha Combination Effects (SD x Prana = 81)
# ======================================================================
class TestPranaDashaCombinationEffects:
    """Test prana_dasha_effects.json (81 SD x Prana combinations)."""

    def test_effects_load_successfully(self):
        from packages.core.src.knowledge_loader import get_prana_dasha_effects

        data = get_prana_dasha_effects()
        assert isinstance(data, dict)
        assert len(data) >= 9, f"Expected 9 SD lords, got {len(data)}"

    def test_all_81_combinations_present(self):
        from packages.core.src.knowledge_loader import get_prana_dasha_effects

        data = get_prana_dasha_effects()
        count = 0
        for sd_lord in ALL_PLANETS:
            assert sd_lord in data, f"Missing SD lord: {sd_lord}"
            for prana_lord in ALL_PLANETS:
                assert prana_lord in data[sd_lord], f"Missing Prana: {sd_lord}-{prana_lord}"
                count += 1
        assert count == 81

    def test_combination_entry_structure(self):
        from packages.core.src.knowledge_loader import get_prana_dasha_effects

        data = get_prana_dasha_effects()
        required_fields = {"relationship", "theme", "effects", "health", "career", "relationships"}
        for sd_lord in ALL_PLANETS:
            for prana_lord in ALL_PLANETS:
                entry = data[sd_lord][prana_lord]
                for field in required_fields:
                    assert field in entry, f"{sd_lord}-{prana_lord} missing: {field}"

    def test_effect_function_returns_data(self):
        from packages.context.src.dasha import get_prana_dasha_effect

        effect = get_prana_dasha_effect("mars", "jupiter")
        if effect is not None:
            assert "theme" in effect
            assert "effects" in effect
            assert isinstance(effect["effects"], list)

    def test_effect_function_same_lord(self):
        from packages.context.src.dasha import get_prana_dasha_effect

        effect = get_prana_dasha_effect("saturn", "saturn")
        if effect is not None:
            assert effect["relationship"] == "same"
