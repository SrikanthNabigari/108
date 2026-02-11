"""Chat block builders — converts tool results into render_blocks.

Each block type matches the Flutter ChatBlock model:
  {type: str, content: str | None, data: dict | None}

Claude decides WHAT data to fetch (via tools).
This module decides HOW to display it (deterministic UI blocks).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Mental state color mapping ──

_STATE_COLORS: dict[str, str] = {
    "Thriving": "#4CAF50",
    "Flowing": "#8BC34A",
    "Steady": "#FFC107",
    "Challenged": "#FF9800",
    "Struggling": "#FF5722",
    "Turbulent": "#F44336",
}


def build_blocks(
    tool_calls_with_results: list[tuple[str, dict[str, Any], dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Build render_blocks from a list of (tool_name, tool_input, tool_result) tuples.

    Args:
        tool_calls_with_results: List of (tool_name, input, result) tuples.

    Returns:
        List of block dicts matching Flutter ChatBlock shape.
    """
    blocks: list[dict[str, Any]] = []
    for tool_name, tool_input, result in tool_calls_with_results:
        if not result.get("success", True) if isinstance(result, dict) else True:
            continue

        try:
            tool_blocks = _build_for_tool(tool_name, tool_input, result)
            blocks.extend(tool_blocks)
        except Exception as e:
            logger.warning(f"Block build error for {tool_name}: {e}")

    return blocks


def _build_for_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Dispatch block building by tool name."""
    if tool_name == "get_state_now":
        return _blocks_state_vector(result)
    elif tool_name == "get_life_area":
        return _blocks_life_area(result, tool_input)
    elif tool_name == "get_current_dasha":
        return _blocks_dasha(result)
    elif tool_name == "get_current_transits":
        return _blocks_transits(result)
    elif tool_name == "get_panchanga":
        return _blocks_panchanga(result)
    elif tool_name == "get_birth_chart_summary":
        return _blocks_birth_chart(result)
    elif tool_name == "get_yogas":
        return _blocks_yogas(result)
    elif tool_name == "get_doshas":
        return _blocks_doshas(result)
    elif tool_name == "get_planet_strength":
        return _blocks_planet_strength(result)
    elif tool_name == "get_compatibility":
        return _blocks_compatibility(result)
    return []


# ── Per-tool block builders ──


def _blocks_state_vector(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    composite = result.get("composite", 0)
    mental_state = result.get("mental_state", "Steady")

    # Score card for composite
    blocks.append(
        {
            "type": "score_card",
            "data": {
                "label": "Overall State",
                "score": round(composite, 1),
                "max": 10,
                "color": _STATE_COLORS.get(mental_state, "#FFC107"),
                "subtitle": mental_state,
            },
        }
    )

    # Factor grid
    factors = result.get("factors", [])
    if factors:
        blocks.append(
            {
                "type": "factor_grid",
                "data": {
                    "factors": [
                        {
                            "id": f.get("id", ""),
                            "short_name": f.get("short_name", ""),
                            "score": round(f.get("score", 0), 1),
                            "label": f.get("label", ""),
                        }
                        for f in factors
                        if isinstance(f, dict)
                    ],
                },
            }
        )

    # Area list
    areas = result.get("areas", [])
    if areas:
        blocks.append(
            {
                "type": "area_list",
                "data": {
                    "areas": [
                        {
                            "id": a.get("id", ""),
                            "score": round(a.get("score", 0), 1),
                            "double_transit": a.get("double_transit", False),
                            "active_yogas": a.get("active_yogas", []),
                        }
                        for a in areas
                        if isinstance(a, dict)
                    ],
                },
            }
        )

    return blocks


def _blocks_life_area(result: dict[str, Any], tool_input: dict[str, Any]) -> list[dict[str, Any]]:
    area = result.get("area", {})
    if not area:
        return []

    area_id = tool_input.get("area_id", area.get("id", ""))
    score = area.get("score", 0)
    mental_state = result.get("mental_state", "Steady")

    return [
        {
            "type": "score_card",
            "data": {
                "label": area_id.replace("_", " ").title(),
                "score": round(score, 1),
                "max": 10,
                "color": _STATE_COLORS.get(mental_state, "#FFC107"),
                "subtitle": f"Double transit: {'Yes' if area.get('double_transit') else 'No'}",
            },
        },
    ]


def _blocks_dasha(result: dict[str, Any]) -> list[dict[str, Any]]:
    maha = result.get("current_mahadasha", {})
    antar = result.get("current_antardasha", {})

    if not maha:
        return []

    return [
        {
            "type": "dasha_card",
            "data": {
                "maha": maha.get("lord", ""),
                "maha_progress": maha.get("progress_percent", 0),
                "antar": antar.get("lord", ""),
                "antar_progress": antar.get("progress_percent", 0),
                "maha_start": maha.get("start"),
                "maha_end": maha.get("end"),
                "antar_start": antar.get("start"),
                "antar_end": antar.get("end"),
            },
        },
    ]


def _blocks_transits(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    transits = result.get("transits", {})

    if transits:
        rows = []
        for planet, data in transits.items():
            rows.append(
                [
                    planet.title(),
                    data.get("sign", ""),
                    str(data.get("house_from_moon", "")),
                    "Yes" if data.get("favorable") else "No",
                ]
            )

        blocks.append(
            {
                "type": "table",
                "data": {
                    "headers": ["Planet", "Sign", "House from Moon", "Favorable"],
                    "rows": rows,
                },
            }
        )

    # Sade Sati alert
    sade_sati = result.get("sade_sati", {})
    if isinstance(sade_sati, dict) and sade_sati.get("is_active"):
        blocks.append(
            {
                "type": "alert",
                "data": {
                    "level": "warning",
                    "title": "Sade Sati Active",
                    "message": f"Phase: {sade_sati.get('phase', 'unknown')}",
                },
            }
        )

    return blocks


def _blocks_panchanga(result: dict[str, Any]) -> list[dict[str, Any]]:
    if not result.get("success", True) if isinstance(result, dict) else True:
        return []

    return [
        {
            "type": "panchanga_card",
            "data": {
                "tithi": _extract_name(result.get("tithi")),
                "nakshatra": _extract_name(result.get("nakshatra")),
                "yoga": _extract_name(result.get("yoga")),
                "karana": _extract_name(result.get("karana")),
                "vara": _extract_name(result.get("vara")),
                "date": result.get("date", ""),
            },
        },
    ]


def _blocks_birth_chart(result: dict[str, Any]) -> list[dict[str, Any]]:
    planets = result.get("planets", {})
    if not planets:
        return []

    rows = []
    for name, data in planets.items():
        if isinstance(data, dict):
            rashi = data.get("rashi", "")
            # Show sign name (title-cased), not numeric index
            rashi_display = rashi.title() if isinstance(rashi, str) else str(rashi)
            retro = " (R)" if data.get("is_retrograde") else ""
            rows.append(
                [
                    f"{name.title()}{retro}",
                    rashi_display,
                    str(data.get("house", "")),
                    str(data.get("nakshatra", "")),
                ]
            )

    return [
        {
            "type": "table",
            "data": {
                "headers": ["Planet", "Rashi", "House", "Nakshatra"],
                "rows": rows,
            },
        },
    ]


def _blocks_yogas(result: dict[str, Any]) -> list[dict[str, Any]]:
    yogas = result.get("yogas", [])
    if not yogas:
        return []

    rows = []
    for y in yogas[:15]:  # Limit to 15 for readability
        if isinstance(y, dict):
            rows.append(
                [
                    y.get("name", y.get("yoga_name", "")),
                    y.get("category", y.get("type", "")),
                    y.get("strength", ""),
                ]
            )

    return [
        {
            "type": "table",
            "data": {
                "headers": ["Yoga", "Category", "Strength"],
                "rows": rows,
            },
        },
    ]


def _blocks_doshas(result: dict[str, Any]) -> list[dict[str, Any]]:
    doshas = result.get("doshas", [])
    if not doshas:
        return []

    blocks: list[dict[str, Any]] = []
    for d in doshas[:10]:
        if isinstance(d, dict):
            severity = d.get("severity", d.get("strength", "medium"))
            level = "error" if severity == "high" else "warning" if severity == "medium" else "info"
            blocks.append(
                {
                    "type": "alert",
                    "data": {
                        "level": level,
                        "title": d.get("name", d.get("dosha_name", "Dosha")),
                        "message": d.get("description", d.get("remedy", "")),
                    },
                }
            )

    return blocks


def _blocks_planet_strength(result: dict[str, Any]) -> list[dict[str, Any]]:
    if not result.get("success"):
        return []

    planet = result.get("planet", "")
    shadbala = result.get("shadbala", {})
    total = shadbala.get("total", 0) if isinstance(shadbala, dict) else 0

    return [
        {
            "type": "score_card",
            "data": {
                "label": f"{planet.title()} Strength",
                "score": round(total, 1) if isinstance(total, int | float) else 0,
                "max": 10,
                "color": "#4CAF50"
                if (isinstance(total, int | float) and total >= 5)
                else "#FF9800",
                "subtitle": f"Dignity: {result.get('dignity', 'neutral')}",
            },
        },
    ]


def _blocks_compatibility(result: dict[str, Any]) -> list[dict[str, Any]]:
    synastry = result.get("synastry", {})
    if not synastry:
        return []

    score = synastry.get("overall_score", synastry.get("compatibility_score", 0))
    return [
        {
            "type": "score_card",
            "data": {
                "label": "Compatibility",
                "score": round(score, 1) if isinstance(score, int | float) else 0,
                "max": 36,
                "color": "#4CAF50"
                if (isinstance(score, int | float) and score >= 18)
                else "#FF9800",
                "subtitle": "Ashtakoot matching",
            },
        },
    ]


def analysis_to_blocks(analysis_results: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert LangGraph analysis_results to render_blocks.

    Maps analysis_results keys to (tool_name, input, result) tuples
    that build_blocks() already knows how to handle.

    Args:
        analysis_results: Dict from Guide agent's AgentState.analysis_results.

    Returns:
        List of block dicts matching Flutter ChatBlock shape.
    """
    if not analysis_results:
        return []

    tool_tuples: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    # State vector -> score_card + factor_grid + area_list
    sv = analysis_results.get("state_vector")
    if isinstance(sv, dict) and sv.get("composite") is not None:
        tool_tuples.append(
            (
                "get_state_now",
                {},
                {
                    "composite": sv["composite"],
                    "mental_state": sv.get("mental_state", ""),
                    "factors": sv.get("factors", []),
                    "areas": sv.get("areas", []),
                    "success": True,
                },
            )
        )

    # Current dasha -> dasha_card
    dasha = analysis_results.get("current_dasha")
    if isinstance(dasha, dict) and dasha.get("mahadasha"):
        tool_tuples.append(
            (
                "get_current_dasha",
                {},
                {
                    "current_mahadasha": {
                        "lord": dasha["mahadasha"],
                        "start": dasha.get("start", ""),
                        "end": dasha.get("end", ""),
                        "progress_percent": dasha.get("progress_percent", 0),
                    },
                    "current_antardasha": {
                        "lord": dasha.get("antardasha", ""),
                        "start": dasha.get("antar_start", ""),
                        "end": dasha.get("antar_end", ""),
                        "progress_percent": dasha.get("antar_progress", 0),
                    },
                    "success": True,
                },
            )
        )

    # Detected yogas -> table
    yogas = analysis_results.get("detected_yogas")
    if isinstance(yogas, list) and yogas:
        tool_tuples.append(
            (
                "get_yogas",
                {},
                {
                    "yogas": yogas[:10],
                    "success": True,
                },
            )
        )

    # Detected doshas -> alert blocks
    doshas = analysis_results.get("detected_doshas")
    if isinstance(doshas, list) and doshas:
        tool_tuples.append(
            (
                "get_doshas",
                {},
                {
                    "doshas": doshas[:5],
                    "success": True,
                },
            )
        )

    # Transit analysis -> table + optional sade_sati alert
    transit = analysis_results.get("transit_analysis")
    if isinstance(transit, dict) and transit.get("key_transits"):
        transits_dict: dict[str, Any] = {}
        for t in transit["key_transits"]:
            if isinstance(t, dict):
                transits_dict[t.get("planet", "unknown")] = {
                    "house_from_moon": t.get("from_moon", 0),
                    "favorable": t.get("favorable", False),
                    "sign": t.get("sign", ""),
                }
        sade_sati: dict[str, Any] = {
            "is_active": bool(transit.get("sade_sati", False)),
        }
        if transit.get("sade_sati"):
            sade_sati["phase"] = transit.get("sade_sati_phase", "peak")
        tool_tuples.append(
            (
                "get_current_transits",
                {},
                {
                    "transits": transits_dict,
                    "sade_sati": sade_sati,
                    "success": True,
                },
            )
        )

    return build_blocks(tool_tuples)


def _extract_name(value: Any) -> str:
    """Extract name from a panchanga field (may be str or dict)."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("name", value.get("lord", str(value)))
    return str(value) if value is not None else ""
