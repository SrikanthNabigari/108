"""Chat tool definitions and execution dispatcher.

Defines the tools Claude can call during chat and dispatches execution
to existing 108-core calculators.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Ensure packages are importable
PACKAGES_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PACKAGES_ROOT))

# ── Tool Definitions (Anthropic tools format) ──

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "get_state_now",
        "description": (
            "Get the current state vector with 7 factor scores (panchanga, transit moon, "
            "gochara, dasha, yoga, shadbala, ashtakavarga) and 8 life area scores "
            "(career, relationships, health, finance, spiritual, family, education, travel). "
            "Returns a composite score and mental state label."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_life_area",
        "description": (
            "Get detailed score for a single life area. Use this when the user asks about "
            "a specific area like career, health, relationships, finance, spiritual, "
            "family, education, or travel."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "area_id": {
                    "type": "string",
                    "description": "Life area ID",
                    "enum": [
                        "career",
                        "relationships",
                        "health",
                        "finance",
                        "spiritual",
                        "family",
                        "education",
                        "travel",
                    ],
                },
            },
            "required": ["area_id"],
        },
    },
    {
        "name": "get_current_dasha",
        "description": (
            "Get the current Vimshottari dasha periods (Mahadasha, Antardasha, "
            "Pratyantardasha) with start/end dates and progress percentages."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_current_transits",
        "description": (
            "Get current planetary transits with their positions, house from moon, "
            "and favorability. Includes Sade Sati and Dhaiya status."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_panchanga",
        "description": (
            "Get today's panchanga (Vedic almanac): tithi, nakshatra, yoga, karana, vara, "
            "sunrise/sunset times."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_birth_chart_summary",
        "description": (
            "Get a summary of the user's natal birth chart including planetary positions, "
            "lagna, moon sign, and house placements."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_yogas",
        "description": (
            "Detect all natal yogas (auspicious planetary combinations) in the user's "
            "birth chart. Returns yoga names, types, and involved planets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_doshas",
        "description": (
            "Detect all doshas (challenging combinations) in the user's birth chart. "
            "Includes Mangal dosha, Kaal Sarp, Pitra dosha, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_planet_strength",
        "description": (
            "Get Shadbala (6-component) strength for a specific planet. "
            "Shows positional, directional, temporal, motional, natural, and aspectual strength."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "planet": {
                    "type": "string",
                    "description": "Planet name",
                    "enum": [
                        "sun",
                        "moon",
                        "mars",
                        "mercury",
                        "jupiter",
                        "venus",
                        "saturn",
                        "rahu",
                        "ketu",
                    ],
                },
            },
            "required": ["planet"],
        },
    },
    {
        "name": "get_compatibility",
        "description": (
            "Check compatibility with another person. Requires partner's birth details."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_birth_datetime": {
                    "type": "string",
                    "description": "Partner's birth datetime in ISO format",
                },
                "partner_latitude": {
                    "type": "number",
                    "description": "Partner's birth latitude",
                },
                "partner_longitude": {
                    "type": "number",
                    "description": "Partner's birth longitude",
                },
            },
            "required": [
                "partner_birth_datetime",
                "partner_latitude",
                "partner_longitude",
            ],
        },
    },
]


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return the list of tool definitions for the Anthropic API."""
    return TOOL_DEFINITIONS


def execute_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    birth_context: dict[str, Any],
) -> dict[str, Any]:
    """Execute a tool by name, dispatching to the appropriate calculator.

    Args:
        tool_name: Name of the tool to execute.
        tool_input: Input parameters from Claude's tool call.
        birth_context: User's birth chart context with natal_planets, moon_longitude, etc.

    Returns:
        Tool result dict. Always includes a "success" key.
    """
    try:
        if tool_name == "get_state_now":
            return _exec_state_now(birth_context)
        elif tool_name == "get_life_area":
            return _exec_life_area(tool_input, birth_context)
        elif tool_name == "get_current_dasha":
            return _exec_current_dasha(birth_context)
        elif tool_name == "get_current_transits":
            return _exec_current_transits(birth_context)
        elif tool_name == "get_panchanga":
            return _exec_panchanga(birth_context)
        elif tool_name == "get_birth_chart_summary":
            return _exec_birth_chart_summary(birth_context)
        elif tool_name == "get_yogas":
            return _exec_yogas(birth_context)
        elif tool_name == "get_doshas":
            return _exec_doshas(birth_context)
        elif tool_name == "get_planet_strength":
            return _exec_planet_strength(tool_input, birth_context)
        elif tool_name == "get_compatibility":
            return _exec_compatibility(tool_input, birth_context)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}")
        return {"success": False, "error": str(e)}


# ── Tool Handlers ──


def _exec_state_now(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.context.src.state_engine import compute_state_vector

    return compute_state_vector(
        birth_datetime=ctx["birth_datetime"],
        birth_lat=ctx["birth_lat"],
        birth_lon=ctx["birth_lon"],
        natal_planets=ctx["natal_planets"],
        moon_longitude=ctx["moon_longitude"],
        lagna_rashi=ctx["lagna_rashi"],
        moon_rashi=ctx.get("moon_rashi"),
    )


def _exec_life_area(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.context.src.state_engine import compute_state_vector

    area_id = inp.get("area_id", "career")
    sv = compute_state_vector(
        birth_datetime=ctx["birth_datetime"],
        birth_lat=ctx["birth_lat"],
        birth_lon=ctx["birth_lon"],
        natal_planets=ctx["natal_planets"],
        moon_longitude=ctx["moon_longitude"],
        lagna_rashi=ctx["lagna_rashi"],
        moon_rashi=ctx.get("moon_rashi"),
    )
    # Find the requested area
    for area in sv.get("areas", []):
        if isinstance(area, dict) and area.get("id") == area_id:
            return {
                "area": area,
                "composite": sv.get("composite", 0),
                "mental_state": sv.get("mental_state", "unknown"),
                "success": True,
            }
    return {"success": False, "error": f"Area '{area_id}' not found"}


def _exec_current_dasha(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    return tools.get_dasha_info(birth_dt, ctx["moon_longitude"])


def _exec_current_transits(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    # Build a minimal natal chart dict for transit analysis
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    # Ensure moon has sign info for transit analysis
    moon_data = natal_chart["planets"].get("moon", {})
    if "sign" not in moon_data and ctx.get("moon_rashi"):
        moon_data["sign"] = ctx["moon_rashi"]
        natal_chart["planets"]["moon"] = moon_data

    return tools.get_transit_analysis(natal_chart)


def _exec_panchanga(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    return tools.get_today_panchanga(
        latitude=ctx.get("birth_lat", 28.6139),
        longitude=ctx.get("birth_lon", 77.2090),
    )


def _exec_birth_chart_summary(ctx: dict[str, Any]) -> dict[str, Any]:
    """Return a summary of the birth chart from the context."""
    natal_planets = ctx.get("natal_planets", {})
    summary_planets = {}
    for name, data in natal_planets.items():
        if isinstance(data, dict):
            summary_planets[name] = {
                "longitude": data.get("longitude"),
                "rashi": data.get("rashi_name") or data.get("rashi", ""),
                "house": data.get("house"),
                "nakshatra": data.get("nakshatra"),
                "is_retrograde": data.get("is_retrograde", False),
            }
    return {
        "lagna_rashi": ctx.get("lagna_rashi"),
        "moon_rashi": ctx.get("moon_rashi"),
        "moon_nakshatra": ctx.get("moon_nakshatra"),
        "birth_datetime": ctx.get("birth_datetime"),
        "planets": summary_planets,
        "success": True,
    }


def _exec_yogas(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    return tools.detect_yogas(natal_chart)


def _exec_doshas(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    return tools.detect_doshas(natal_chart)


def _exec_planet_strength(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    planet_name = inp.get("planet", "sun")
    natal_planets = ctx.get("natal_planets", {})
    planet_data = natal_planets.get(planet_name, {})
    house_num = planet_data.get("house", 1) if isinstance(planet_data, dict) else 1
    lagna = ctx.get("lagna_rashi", "Aries")
    return tools.get_planet_strength(planet_name, planet_data, house_num, lagna)


def _exec_compatibility(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    partner_dt = datetime.fromisoformat(inp["partner_birth_datetime"])
    return tools.get_synastry_report(
        native_birth_dt=birth_dt,
        native_lat=ctx["birth_lat"],
        native_lon=ctx["birth_lon"],
        partner_birth_dt=partner_dt,
        partner_lat=inp["partner_latitude"],
        partner_lon=inp["partner_longitude"],
    )
