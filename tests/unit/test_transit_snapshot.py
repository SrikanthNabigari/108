"""Tests for the transit snapshot gateway endpoint wiring.

Validates that get_transit_snapshot, analyze_transit_lordships, and
get_lordship_summary are correctly imported and can be called with
representative data, and that the gateway endpoint response structure
is correct.
"""

from __future__ import annotations

from unittest.mock import patch

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

MOCK_TRANSITS = {
    "sun": {
        "longitude": 315.0,
        "rashi_num": 10,
        "rashi": "Aquarius",
        "degree_in_rashi": 15.0,
        "speed": 1.0,
        "is_retrograde": False,
    },
    "moon": {
        "longitude": 45.0,
        "rashi_num": 1,
        "rashi": "Taurus",
        "degree_in_rashi": 15.0,
        "speed": 13.0,
        "is_retrograde": False,
    },
    "mars": {
        "longitude": 90.0,
        "rashi_num": 3,
        "rashi": "Cancer",
        "degree_in_rashi": 0.0,
        "speed": 0.5,
        "is_retrograde": False,
    },
    "mercury": {
        "longitude": 300.0,
        "rashi_num": 10,
        "rashi": "Aquarius",
        "degree_in_rashi": 0.0,
        "speed": 1.5,
        "is_retrograde": False,
    },
    "jupiter": {
        "longitude": 15.0,
        "rashi_num": 0,
        "rashi": "Aries",
        "degree_in_rashi": 15.0,
        "speed": 0.08,
        "is_retrograde": False,
    },
    "venus": {
        "longitude": 330.0,
        "rashi_num": 11,
        "rashi": "Pisces",
        "degree_in_rashi": 0.0,
        "speed": 1.2,
        "is_retrograde": False,
    },
    "saturn": {
        "longitude": 340.0,
        "rashi_num": 11,
        "rashi": "Pisces",
        "degree_in_rashi": 10.0,
        "speed": 0.03,
        "is_retrograde": False,
    },
    "rahu": {
        "longitude": 350.0,
        "rashi_num": 11,
        "rashi": "Pisces",
        "degree_in_rashi": 20.0,
        "speed": -0.05,
        "is_retrograde": True,
    },
    "ketu": {
        "longitude": 170.0,
        "rashi_num": 5,
        "rashi": "Virgo",
        "degree_in_rashi": 20.0,
        "speed": -0.05,
        "is_retrograde": True,
    },
}

LAGNA_LIBRA = 6
MOON_AQUARIUS = 10

SAMPLE_NATAL_PLANETS = {
    "sun": {"longitude": 227.0, "rashi": 7, "house": 2},
    "moon": {"longitude": 327.0, "rashi": 10, "house": 5},
    "mars": {"longitude": 100.0, "rashi": 3, "house": 10},
    "mercury": {"longitude": 240.0, "rashi": 8, "house": 3},
    "jupiter": {"longitude": 120.0, "rashi": 4, "house": 11},
    "venus": {"longitude": 192.0, "rashi": 6, "house": 1},
    "saturn": {"longitude": 310.0, "rashi": 10, "house": 5},
    "rahu": {"longitude": 260.0, "rashi": 8, "house": 3},
    "ketu": {"longitude": 80.0, "rashi": 2, "house": 9},
}


# ---------------------------------------------------------------------------
# Unit tests for imports and function calls
# ---------------------------------------------------------------------------


class TestImports:
    """Verify new functions are properly importable."""

    def test_import_get_transit_snapshot(self):
        from packages.context.src import get_transit_snapshot

        assert callable(get_transit_snapshot)

    def test_import_check_double_transit(self):
        from packages.context.src import check_double_transit

        assert callable(check_double_transit)

    def test_import_get_house_activations(self):
        from packages.context.src import get_house_activations

        assert callable(get_house_activations)

    def test_import_analyze_transit_lordships(self):
        from packages.self.src import analyze_transit_lordships

        assert callable(analyze_transit_lordships)

    def test_import_get_lordship_summary(self):
        from packages.self.src import get_lordship_summary

        assert callable(get_lordship_summary)


class TestCheckDoubleTransit:
    """Integration tests for check_double_transit through wiring."""

    def test_basic_call(self):
        from packages.context.src import check_double_transit

        result = check_double_transit(
            jupiter_rashi=0,  # Aries
            saturn_rashi=10,  # Aquarius
            lagna_rashi=LAGNA_LIBRA,
        )
        assert isinstance(result, dict)
        # All values should be dicts with strength info
        for house_num, info in result.items():
            assert isinstance(house_num, int)
            assert 1 <= house_num <= 12
            assert "jupiter_influence" in info
            assert "saturn_influence" in info
            assert "strength" in info
            assert info["strength"] in ("strong", "moderate")

    def test_same_sign_both_occupy(self):
        from packages.context.src import check_double_transit

        result = check_double_transit(
            jupiter_rashi=0,  # Aries
            saturn_rashi=0,  # Aries (same sign)
            lagna_rashi=0,  # Aries lagna
        )
        # House 1 (Aries) should be in result with both occupying
        assert 1 in result
        assert result[1]["jupiter_influence"] == "occupies"
        assert result[1]["saturn_influence"] == "occupies"
        assert result[1]["strength"] == "strong"


class TestGetHouseActivations:
    """Integration tests for get_house_activations."""

    def test_returns_12_houses(self):
        from packages.context.src import get_house_activations

        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS, chart=None)
        assert len(result) == 12

    def test_score_range(self):
        from packages.context.src import get_house_activations

        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS, chart=None)
        for house in result:
            assert 0 <= house["score"] <= 100

    def test_grade_values(self):
        from packages.context.src import get_house_activations

        valid_grades = {"highly_active", "active", "moderate", "quiet"}
        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS, chart=None)
        for house in result:
            assert house["grade"] in valid_grades

    def test_house_dict_structure(self):
        from packages.context.src import get_house_activations

        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS, chart=None)
        required_keys = {
            "house",
            "sign",
            "score",
            "grade",
            "planets_present",
            "planets_aspecting",
            "double_transit",
            "themes",
            "summary",
        }
        for house in result:
            assert required_keys.issubset(
                house.keys()
            ), f"House {house.get('house')} missing keys: {required_keys - house.keys()}"

    def test_houses_numbered_1_to_12(self):
        from packages.context.src import get_house_activations

        result = get_house_activations(MOCK_TRANSITS, LAGNA_LIBRA, MOON_AQUARIUS, chart=None)
        house_nums = {h["house"] for h in result}
        assert house_nums == set(range(1, 13))


class TestAnalyzeTransitLordships:
    """Integration tests for analyze_transit_lordships."""

    def test_analyzes_all_planets(self):
        from packages.self.src import analyze_transit_lordships

        result = analyze_transit_lordships(MOCK_TRANSITS, LAGNA_LIBRA)
        assert len(result) == 9

    def test_result_structure(self):
        from packages.self.src import analyze_transit_lordships

        result = analyze_transit_lordships(MOCK_TRANSITS, LAGNA_LIBRA)
        for entry in result:
            assert "planet" in entry
            assert "transit_rashi" in entry
            assert "transit_house" in entry
            assert "houses_ruled" in entry
            assert "functional_nature" in entry

    def test_saturn_yogakaraka_for_libra(self):
        from packages.self.src import analyze_transit_lordships

        result = analyze_transit_lordships(MOCK_TRANSITS, LAGNA_LIBRA)
        saturn_entry = next(e for e in result if e["planet"] == "saturn")
        assert saturn_entry["functional_nature"] == "yogakaraka"


class TestGetLordshipSummary:
    """Integration tests for get_lordship_summary."""

    def test_summary_structure(self):
        from packages.self.src import analyze_transit_lordships, get_lordship_summary

        lordships = analyze_transit_lordships(MOCK_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(lordships)
        assert "yogakaraka_transits" in summary
        assert "benefic_transits" in summary
        assert "malefic_transits" in summary
        assert "maraka_transits" in summary
        assert "favorable_count" in summary
        assert "unfavorable_count" in summary
        assert "key_insight" in summary

    def test_yogakaraka_detected(self):
        from packages.self.src import analyze_transit_lordships, get_lordship_summary

        lordships = analyze_transit_lordships(MOCK_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(lordships)
        # Saturn is yogakaraka for Libra
        assert "saturn" in summary["yogakaraka_transits"]

    def test_key_insight_nonempty(self):
        from packages.self.src import analyze_transit_lordships, get_lordship_summary

        lordships = analyze_transit_lordships(MOCK_TRANSITS, LAGNA_LIBRA)
        summary = get_lordship_summary(lordships)
        assert len(summary["key_insight"]) > 10


class TestTransitSnapshot:
    """Integration tests for get_transit_snapshot (mocked transit positions)."""

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_snapshot_structure(self, mock_get_transits):
        from packages.context.src import get_transit_snapshot

        mock_get_transits.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
            chart=None,
        )
        assert "timestamp" in result
        assert "transit_positions" in result
        assert "house_activations" in result
        assert "double_transit_houses" in result
        assert "most_active_houses" in result
        assert "most_quiet_houses" in result
        assert "overall_trend" in result
        assert "summary" in result

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_snapshot_has_12_houses(self, mock_get_transits):
        from packages.context.src import get_transit_snapshot

        mock_get_transits.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
        )
        assert len(result["house_activations"]) == 12

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_snapshot_most_active_sorted(self, mock_get_transits):
        from packages.context.src import get_transit_snapshot

        mock_get_transits.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
        )
        active = result["most_active_houses"]
        assert len(active) == 3
        # Scores should be descending
        scores = {h["house"]: h["score"] for h in result["house_activations"]}
        assert scores[active[0]] >= scores[active[1]] >= scores[active[2]]

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_snapshot_trend_valid(self, mock_get_transits):
        from packages.context.src import get_transit_snapshot

        mock_get_transits.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
        )
        assert result["overall_trend"] in ("favorable", "mixed", "challenging")

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_snapshot_summary_nonempty(self, mock_get_transits):
        from packages.context.src import get_transit_snapshot

        mock_get_transits.return_value = MOCK_TRANSITS
        result = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
        )
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0


class TestCombinedSnapshotWithLordship:
    """Test combining snapshot + lordship like the gateway endpoint does."""

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_combined_response(self, mock_get_transits):
        from packages.context.src import get_transit_snapshot
        from packages.self.src import analyze_transit_lordships, get_lordship_summary

        mock_get_transits.return_value = MOCK_TRANSITS

        snapshot = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
        )

        transit_positions = snapshot.get("transit_positions", {})
        lordship_analysis = analyze_transit_lordships(transit_positions, LAGNA_LIBRA)
        lordship_summary = get_lordship_summary(lordship_analysis)

        combined = {
            **snapshot,
            "lordship_analysis": lordship_analysis,
            "lordship_summary": lordship_summary,
        }

        # Verify combined has all expected keys
        assert "house_activations" in combined
        assert "lordship_analysis" in combined
        assert "lordship_summary" in combined
        assert len(combined["lordship_analysis"]) == 9
        assert "yogakaraka_transits" in combined["lordship_summary"]

    @patch("packages.context.src.house_activation.get_transit_positions")
    def test_preview_tier_shape(self, mock_get_transits):
        """Simulate what the preview tier returns."""
        from packages.context.src import get_transit_snapshot

        mock_get_transits.return_value = MOCK_TRANSITS

        snapshot = get_transit_snapshot(
            julian_day=2460750.0,
            lagna_rashi=LAGNA_LIBRA,
            moon_rashi=MOON_AQUARIUS,
            natal_planets=SAMPLE_NATAL_PLANETS,
        )

        preview = {
            "transit_positions": snapshot.get("transit_positions", {}),
            "house_activations": [
                {
                    "house": h["house"],
                    "score": h["score"],
                    "grade": h["grade"],
                    "double_transit": h["double_transit"],
                    "themes": h["themes"],
                }
                for h in snapshot.get("house_activations", [])
            ],
            "double_transit_houses": snapshot.get("double_transit_houses", []),
            "most_active_houses": snapshot.get("most_active_houses", []),
            "overall_trend": snapshot.get("overall_trend", "mixed"),
            "access": "preview",
        }

        assert preview["access"] == "preview"
        assert len(preview["house_activations"]) == 12
        # Preview house dict should not have planets_present or planets_aspecting
        for h in preview["house_activations"]:
            assert "planets_present" not in h
            assert "planets_aspecting" not in h
            assert "house" in h
            assert "score" in h
            assert "grade" in h


class TestKnowledgeFilesExist:
    """Verify knowledge rule files created by knowledge-agent are loadable."""

    def test_double_transit_rules_loadable(self):
        import json
        from pathlib import Path

        path = (
            Path(__file__).parent.parent.parent
            / "knowledge"
            / "rules"
            / "double_transit_rules.json"
        )
        with path.open() as f:
            data = json.load(f)
        assert "rules" in data
        assert len(data["rules"]) == 12

    def test_transit_lordship_rules_loadable(self):
        import json
        from pathlib import Path

        path = (
            Path(__file__).parent.parent.parent
            / "knowledge"
            / "rules"
            / "transit_lordship_rules.json"
        )
        with path.open() as f:
            data = json.load(f)
        assert "functional_nature_rules" in data
        assert "lord_transit_house_rules" in data
        assert "special_transit_rules" in data
