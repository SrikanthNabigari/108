"""Tests for chat block builders."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.guide.src.chat_blocks import analysis_to_blocks, build_blocks


class TestBuildBlocks:
    """Tests for the main build_blocks dispatcher."""

    def test_empty_tool_results_returns_empty(self):
        assert build_blocks([]) == []

    def test_state_vector_produces_three_blocks(self):
        state_result = {
            "composite": 6.5,
            "mental_state": "Flowing",
            "factors": [
                {"id": "panchanga", "short_name": "PAN", "score": 7.0, "label": "Good"},
                {"id": "dasha", "short_name": "DAS", "score": 5.5, "label": "Neutral"},
            ],
            "areas": [
                {
                    "id": "career",
                    "score": 7.2,
                    "double_transit": True,
                    "active_yogas": ["Gajakesari"],
                },
                {"id": "health", "score": 5.0, "double_transit": False, "active_yogas": []},
            ],
            "success": True,
        }
        blocks = build_blocks([("get_state_now", {}, state_result)])
        assert len(blocks) == 3

        # score_card
        assert blocks[0]["type"] == "score_card"
        assert blocks[0]["data"]["label"] == "Overall State"
        assert blocks[0]["data"]["score"] == 6.5
        assert blocks[0]["data"]["subtitle"] == "Flowing"

        # factor_grid
        assert blocks[1]["type"] == "factor_grid"
        assert len(blocks[1]["data"]["factors"]) == 2

        # area_list
        assert blocks[2]["type"] == "area_list"
        assert len(blocks[2]["data"]["areas"]) == 2
        assert blocks[2]["data"]["areas"][0]["double_transit"] is True

    def test_life_area_produces_score_card(self):
        result = {
            "area": {"id": "career", "score": 7.2, "double_transit": True},
            "composite": 6.5,
            "mental_state": "Flowing",
            "success": True,
        }
        blocks = build_blocks([("get_life_area", {"area_id": "career"}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "score_card"
        assert blocks[0]["data"]["label"] == "Career"

    def test_dasha_produces_dasha_card(self):
        result = {
            "current_mahadasha": {
                "lord": "Mercury",
                "start": "2019-09-01",
                "end": "2036-09-01",
                "progress_percent": 37.2,
            },
            "current_antardasha": {
                "lord": "Saturn",
                "start": "2024-01-01",
                "end": "2026-10-01",
                "progress_percent": 55.0,
            },
            "success": True,
        }
        blocks = build_blocks([("get_current_dasha", {}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "dasha_card"
        assert blocks[0]["data"]["maha"] == "Mercury"
        assert blocks[0]["data"]["antar"] == "Saturn"

    def test_transits_produces_table(self):
        result = {
            "transits": {
                "saturn": {"sign": "Pisces", "house_from_moon": 2, "favorable": True},
                "jupiter": {"sign": "Gemini", "house_from_moon": 5, "favorable": True},
            },
            "sade_sati": {"is_active": False},
            "success": True,
        }
        blocks = build_blocks([("get_current_transits", {}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "table"
        assert len(blocks[0]["data"]["rows"]) == 2
        assert blocks[0]["data"]["headers"][0] == "Planet"

    def test_transits_with_sade_sati_alert(self):
        result = {
            "transits": {
                "saturn": {"sign": "Aquarius", "house_from_moon": 1, "favorable": False},
            },
            "sade_sati": {"is_active": True, "phase": "peak"},
            "success": True,
        }
        blocks = build_blocks([("get_current_transits", {}, result)])
        assert len(blocks) == 2
        alert = blocks[1]
        assert alert["type"] == "alert"
        assert alert["data"]["level"] == "warning"
        assert "Sade Sati" in alert["data"]["title"]

    def test_panchanga_produces_card(self):
        result = {
            "tithi": {"name": "Shukla Dashami", "number": 10},
            "nakshatra": "Rohini",
            "yoga": {"name": "Siddha"},
            "karana": "Bava",
            "vara": {"name": "Wednesday", "lord": "Mercury"},
            "date": "2026-02-11",
            "success": True,
        }
        blocks = build_blocks([("get_panchanga", {}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "panchanga_card"
        assert blocks[0]["data"]["tithi"] == "Shukla Dashami"
        assert blocks[0]["data"]["nakshatra"] == "Rohini"

    def test_yogas_produces_table(self):
        result = {
            "yogas": [
                {"name": "Gajakesari", "category": "mahapurusha", "strength": "strong"},
                {"name": "Budhaditya", "category": "raja", "strength": "medium"},
            ],
            "success": True,
        }
        blocks = build_blocks([("get_yogas", {}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "table"
        assert len(blocks[0]["data"]["rows"]) == 2

    def test_doshas_produces_alerts(self):
        result = {
            "doshas": [
                {"name": "Mangal Dosha", "severity": "high", "description": "Mars in 7th house"},
                {"name": "Kaal Sarp", "severity": "medium", "remedy": "Rahu-Ketu puja"},
            ],
            "success": True,
        }
        blocks = build_blocks([("get_doshas", {}, result)])
        assert len(blocks) == 2
        assert blocks[0]["type"] == "alert"
        assert blocks[0]["data"]["level"] == "error"  # high severity
        assert blocks[1]["data"]["level"] == "warning"  # medium severity

    def test_planet_strength_produces_score_card(self):
        result = {
            "planet": "jupiter",
            "shadbala": {"total": 7.5},
            "dignity": "exalted",
            "success": True,
        }
        blocks = build_blocks([("get_planet_strength", {"planet": "jupiter"}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "score_card"
        assert blocks[0]["data"]["score"] == 7.5

    def test_failed_result_produces_no_blocks(self):
        result = {"success": False, "error": "something went wrong"}
        blocks = build_blocks([("get_state_now", {}, result)])
        assert blocks == []

    def test_multiple_tool_results_combined(self):
        state = {
            "composite": 6.0,
            "mental_state": "Steady",
            "factors": [{"id": "panchanga", "short_name": "PAN", "score": 6.0, "label": "OK"}],
            "areas": [{"id": "career", "score": 7.0, "double_transit": False, "active_yogas": []}],
            "success": True,
        }
        dasha = {
            "current_mahadasha": {
                "lord": "Mercury",
                "start": "2019",
                "end": "2036",
                "progress_percent": 40,
            },
            "current_antardasha": {
                "lord": "Venus",
                "start": "2025",
                "end": "2027",
                "progress_percent": 10,
            },
            "success": True,
        }
        blocks = build_blocks(
            [
                ("get_state_now", {}, state),
                ("get_current_dasha", {}, dasha),
            ]
        )
        types = [b["type"] for b in blocks]
        assert "score_card" in types
        assert "factor_grid" in types
        assert "area_list" in types
        assert "dasha_card" in types

    def test_birth_chart_summary_produces_table(self):
        result = {
            "planets": {
                "sun": {"rashi": 7, "house": 2, "nakshatra": "Anuradha"},
                "moon": {"rashi": 10, "house": 5, "nakshatra": "Purva Bhadrapada"},
            },
            "lagna_rashi": "Libra",
            "success": True,
        }
        blocks = build_blocks([("get_birth_chart_summary", {}, result)])
        assert len(blocks) == 1
        assert blocks[0]["type"] == "table"
        assert len(blocks[0]["data"]["rows"]) == 2

    def test_block_shape_has_type_and_data(self):
        result = {
            "composite": 5.0,
            "mental_state": "Steady",
            "factors": [],
            "areas": [],
            "success": True,
        }
        blocks = build_blocks([("get_state_now", {}, result)])
        for block in blocks:
            assert "type" in block
            assert "data" in block


class TestAnalysisToBlocks:
    """Tests for the analysis_to_blocks() bridge function."""

    def test_empty_results(self):
        assert analysis_to_blocks({}) == []

    def test_none_results(self):
        assert analysis_to_blocks(None) == []

    def test_state_vector_produces_blocks(self):
        results = {
            "state_vector": {
                "composite": 6.5,
                "mental_state": "Flowing",
                "factors": [
                    {"id": "panchanga", "short_name": "PAN", "score": 7.0, "label": "Good"},
                ],
                "areas": [
                    {"id": "career", "score": 7.2, "double_transit": True, "active_yogas": []},
                ],
            },
        }
        blocks = analysis_to_blocks(results)
        types = [b["type"] for b in blocks]
        assert "score_card" in types
        assert "factor_grid" in types
        assert "area_list" in types

    def test_state_vector_without_composite_skipped(self):
        results = {"state_vector": {"factors": [], "areas": []}}
        assert analysis_to_blocks(results) == []

    def test_dasha_produces_card(self):
        results = {
            "current_dasha": {
                "mahadasha": "Mercury",
                "antardasha": "Saturn",
                "start": "2019-09-01",
                "end": "2036-09-01",
                "progress_percent": 37.2,
                "antar_start": "2024-01-01",
                "antar_end": "2026-10-01",
                "antar_progress": 55.0,
            },
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "dasha_card"
        assert blocks[0]["data"]["maha"] == "Mercury"
        assert blocks[0]["data"]["antar"] == "Saturn"

    def test_dasha_without_mahadasha_skipped(self):
        results = {"current_dasha": {"antardasha": "Saturn"}}
        assert analysis_to_blocks(results) == []

    def test_yogas_produces_table(self):
        results = {
            "detected_yogas": [
                {"name": "Gajakesari", "category": "mahapurusha", "strength": "strong"},
            ],
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "table"
        assert len(blocks[0]["data"]["rows"]) == 1

    def test_doshas_produces_alerts(self):
        results = {
            "detected_doshas": [
                {"name": "Mangal Dosha", "severity": "high", "description": "Mars in 7th"},
            ],
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "alert"
        assert blocks[0]["data"]["level"] == "error"

    def test_transit_produces_table(self):
        results = {
            "transit_analysis": {
                "key_transits": [
                    {"planet": "saturn", "from_moon": 2, "favorable": True, "sign": "Pisces"},
                ],
                "sade_sati": False,
            },
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) == 1
        assert blocks[0]["type"] == "table"
        assert blocks[0]["data"]["rows"][0][0] == "Saturn"

    def test_transit_with_sade_sati_alert(self):
        results = {
            "transit_analysis": {
                "key_transits": [
                    {"planet": "saturn", "from_moon": 1, "favorable": False, "sign": "Aquarius"},
                ],
                "sade_sati": True,
                "sade_sati_phase": "peak",
            },
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) == 2
        assert blocks[1]["type"] == "alert"
        assert "Sade Sati" in blocks[1]["data"]["title"]

    def test_combined_results(self):
        results = {
            "state_vector": {
                "composite": 6.0,
                "mental_state": "Steady",
                "factors": [{"id": "panchanga", "short_name": "PAN", "score": 6.0, "label": "OK"}],
                "areas": [
                    {"id": "career", "score": 7.0, "double_transit": False, "active_yogas": []}
                ],
            },
            "current_dasha": {
                "mahadasha": "Mercury",
                "antardasha": "Venus",
            },
            "detected_yogas": [
                {"name": "Gajakesari", "category": "mahapurusha", "strength": "strong"},
            ],
        }
        blocks = analysis_to_blocks(results)
        types = [b["type"] for b in blocks]
        assert "score_card" in types
        assert "dasha_card" in types
        assert "table" in types

    def test_limits_yogas_to_10(self):
        results = {
            "detected_yogas": [
                {"name": f"Yoga{i}", "category": "raja", "strength": "medium"} for i in range(20)
            ],
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) == 1
        # Table rows should be at most 10 (limited in analysis_to_blocks)
        assert len(blocks[0]["data"]["rows"]) <= 10

    def test_limits_doshas_to_5(self):
        results = {
            "detected_doshas": [
                {"name": f"Dosha{i}", "severity": "medium", "description": f"desc{i}"}
                for i in range(10)
            ],
        }
        blocks = analysis_to_blocks(results)
        assert len(blocks) <= 5

    def test_non_dict_state_vector_skipped(self):
        results = {"state_vector": "invalid"}
        assert analysis_to_blocks(results) == []

    def test_empty_yogas_list_skipped(self):
        results = {"detected_yogas": []}
        assert analysis_to_blocks(results) == []
