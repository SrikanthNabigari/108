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
            "Pratyantardasha, Sookshma, Prana, Deha) with start/end dates and progress."
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
    # ── Phase 1: Timing & Predictions ──
    {
        "name": "get_forecast",
        "description": (
            "Get a daily, weekly, or monthly forecast. Daily gives day rating with "
            "panchanga and transit aspects. Weekly gives 7-day area ratings. Monthly "
            "gives major transits and area analysis for the full month."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "description": "Forecast period",
                    "enum": ["daily", "weekly", "monthly"],
                },
            },
            "required": ["period"],
        },
    },
    {
        "name": "get_upcoming_events",
        "description": (
            "Get upcoming significant astrological events in the next N days. "
            "Includes transit ingresses, planetary aspects to natal planets, and "
            "dasha period changes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "Days to look ahead (default 30, max 90)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_muhurta",
        "description": (
            "Check auspicious timing (muhurta) for an activity on a specific date. "
            "Evaluates tithi, nakshatra, yoga, karana, vara, Rahu Kaal, and other factors."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "activity": {
                    "type": "string",
                    "description": "Activity type",
                    "enum": [
                        "marriage",
                        "travel",
                        "business_start",
                        "surgery",
                        "vehicle_purchase",
                        "home_entry",
                        "education_start",
                        "investment",
                        "meeting",
                        "ceremony",
                    ],
                },
                "date": {
                    "type": "string",
                    "description": "ISO date to check (default: today)",
                },
            },
            "required": ["activity"],
        },
    },
    {
        "name": "get_remedies",
        "description": (
            "Get personalized astrological remedies based on current dasha, "
            "active doshas, and weak planets. Includes gemstones, mantras, "
            "donations, and rituals."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_dasha_timeline",
        "description": (
            "Get the full Vimshottari dasha timeline showing all mahadasha and "
            "antardasha periods with start/end dates. Use for life planning."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "years": {
                    "type": "integer",
                    "description": "Years ahead to show (default 50)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "correlate_event",
        "description": (
            "Analyze why a past life event happened by correlating it with dasha "
            "and transit positions at that date. Helps understand karmic patterns."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "event_date": {
                    "type": "string",
                    "description": "ISO date of the event (e.g. 2020-03-15)",
                },
                "event_type": {
                    "type": "string",
                    "description": "Event category",
                    "enum": [
                        "career",
                        "marriage",
                        "health",
                        "money",
                        "education",
                        "travel",
                        "family",
                        "spiritual",
                    ],
                },
                "description": {
                    "type": "string",
                    "description": "Brief description of the event",
                },
            },
            "required": ["event_date", "event_type", "description"],
        },
    },
    # ── Phase 2: Deep Analysis ──
    {
        "name": "get_soul_purpose",
        "description": (
            "Get Atmakaraka (soul indicator) analysis revealing soul purpose, "
            "Karakamsha sign, Ishta Devata, career direction, and spiritual path."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_gem_recommendation",
        "description": (
            "Get personalized gemstone prescription based on birth chart. "
            "Includes primary gem, supporting gems, contraindications, weight, "
            "metal, and wearing instructions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "planet": {
                    "type": "string",
                    "description": "Specific planet gem to check (optional, omit for full recommendation)",
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
            "required": [],
        },
    },
    {
        "name": "get_divisional_chart",
        "description": (
            "Get a divisional chart (Varga) showing planetary positions in D2 (wealth), "
            "D3 (siblings), D9 (marriage/dharma), D10 (career), D12 (parents), etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_number": {
                    "type": "integer",
                    "description": "Divisional chart number",
                    "enum": [2, 3, 9, 10, 12, 24, 30, 60],
                },
            },
            "required": ["chart_number"],
        },
    },
    {
        "name": "check_yoga_cancellation",
        "description": (
            "Validate natal yogas by checking cancellation rules. Shows which yogas "
            "survive and which are cancelled by combustion, debilitation, or enemy aspects."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_retrograde_effects",
        "description": (
            "Analyze retrograde planets in the birth chart. Retrogrades indicate "
            "karmic lessons, internalized energy, and past-life patterns."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_combustion_status",
        "description": (
            "Check for combust planets (too close to the Sun). Combustion weakens "
            "a planet's significations and requires remedial measures."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    # ── Phase 3: Advanced Systems ──
    {
        "name": "get_varshaphal",
        "description": (
            "Get Varshaphal (annual solar return) analysis for the current or specified year. "
            "Shows Muntha position, Varshesha (year lord), and annual house effects."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "Year to analyze (default: current year)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_kp_prediction",
        "description": (
            "Get KP (Krishnamurti Paddhati) system prediction for a yes/no question. "
            "Uses sub-lord theory for precise predictions about specific life areas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question_type": {
                    "type": "string",
                    "description": "Life area to predict",
                    "enum": [
                        "career",
                        "marriage",
                        "children",
                        "wealth",
                        "health",
                        "education",
                        "travel",
                        "property",
                        "legal",
                        "spiritual",
                    ],
                },
            },
            "required": ["question_type"],
        },
    },
    {
        "name": "get_prashna",
        "description": (
            "Perform Prashna (horary) astrology for a specific question. "
            "Casts a chart for the moment of the question to get an answer."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The specific question to ask",
                },
                "category": {
                    "type": "string",
                    "description": "Question category",
                    "enum": [
                        "general",
                        "health",
                        "marriage",
                        "career",
                        "travel",
                        "lost_object",
                        "legal",
                    ],
                },
            },
            "required": ["question", "category"],
        },
    },
    {
        "name": "get_ashtakavarga",
        "description": (
            "Get Ashtakavarga analysis showing bindhu scores for all planets across "
            "all signs. Reveals which signs and houses are strong or weak for each planet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_alternative_dasha",
        "description": (
            "Get an alternative dasha system calculation. Yogini Dasha (36-year cycle, "
            "good for female charts), Ashtottari (108-year cycle, night births), "
            "or Narayana Dasha (sign-based, Jaimini system)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "description": "Dasha system to use",
                    "enum": ["yogini", "ashtottari", "narayana"],
                },
            },
            "required": ["system"],
        },
    },
    {
        "name": "get_jaimini_analysis",
        "description": (
            "Get Jaimini astrology analysis including Chara Karakas (variable significators), "
            "Atmakaraka, Karakamsha, and Chara Dasha overview."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "lookup_knowledge",
        "description": (
            "Search the Jyotish knowledge base for information about planets, rashis, "
            "nakshatras, yogas, houses, or doshas. Returns interpretations and meanings."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g. planet name, yoga name, nakshatra)",
                },
                "category": {
                    "type": "string",
                    "description": "Knowledge category to search",
                    "enum": [
                        "planet",
                        "rashi",
                        "nakshatra",
                        "yoga",
                        "house",
                        "dosha",
                    ],
                },
            },
            "required": ["query", "category"],
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
        # Phase 1: Timing & Predictions
        elif tool_name == "get_forecast":
            return _exec_forecast(tool_input, birth_context)
        elif tool_name == "get_upcoming_events":
            return _exec_upcoming_events(tool_input, birth_context)
        elif tool_name == "get_muhurta":
            return _exec_muhurta(tool_input, birth_context)
        elif tool_name == "get_remedies":
            return _exec_remedies(birth_context)
        elif tool_name == "get_dasha_timeline":
            return _exec_dasha_timeline(tool_input, birth_context)
        elif tool_name == "correlate_event":
            return _exec_correlate_event(tool_input, birth_context)
        # Phase 2: Deep Analysis
        elif tool_name == "get_soul_purpose":
            return _exec_soul_purpose(birth_context)
        elif tool_name == "get_gem_recommendation":
            return _exec_gem_recommendation(tool_input, birth_context)
        elif tool_name == "get_divisional_chart":
            return _exec_divisional_chart(tool_input, birth_context)
        elif tool_name == "check_yoga_cancellation":
            return _exec_yoga_cancellation(birth_context)
        elif tool_name == "get_retrograde_effects":
            return _exec_retrograde_effects(birth_context)
        elif tool_name == "get_combustion_status":
            return _exec_combustion_status(birth_context)
        # Phase 3: Advanced Systems
        elif tool_name == "get_varshaphal":
            return _exec_varshaphal(tool_input, birth_context)
        elif tool_name == "get_kp_prediction":
            return _exec_kp_prediction(tool_input, birth_context)
        elif tool_name == "get_prashna":
            return _exec_prashna(tool_input, birth_context)
        elif tool_name == "get_ashtakavarga":
            return _exec_ashtakavarga(birth_context)
        elif tool_name == "get_alternative_dasha":
            return _exec_alternative_dasha(tool_input, birth_context)
        elif tool_name == "get_jaimini_analysis":
            return _exec_jaimini_analysis(birth_context)
        elif tool_name == "lookup_knowledge":
            return _exec_lookup_knowledge(tool_input)
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

    # Build a minimal natal chart dict — get_transit_analysis() handles
    # moon sign resolution internally (sign / rashi_name / longitude fallback).
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }

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


# ── Phase 1: Timing & Predictions Handlers ──


def _exec_forecast(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    period = inp.get("period", "daily")
    if period == "weekly":
        return tools.get_weekly_forecast(birth_dt, ctx["birth_lat"], ctx["birth_lon"])
    elif period == "monthly":
        return tools.get_monthly_forecast(birth_dt, ctx["birth_lat"], ctx["birth_lon"])
    else:
        return tools.get_daily_forecast(birth_dt, ctx["birth_lat"], ctx["birth_lon"])


def _exec_upcoming_events(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    days = min(inp.get("days_ahead", 30), 90)
    return tools.get_upcoming_triggers(
        natal_planets=ctx.get("natal_planets", {}),
        lagna_rashi=ctx.get("lagna_rashi", "Aries"),
        moon_rashi=ctx.get("moon_rashi", "Aries"),
        days_ahead=days,
        birth_datetime=ctx.get("birth_datetime"),
        moon_longitude=ctx.get("moon_longitude"),
    )


def _exec_muhurta(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    activity = inp.get("activity", "meeting")
    date_str = inp.get("date")
    dt = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()
    return tools.check_muhurta(
        activity=activity,
        datetime_to_check=dt,
        latitude=ctx.get("birth_lat", 28.6139),
        longitude=ctx.get("birth_lon", 77.2090),
    )


def _exec_remedies(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    # Compute current dasha lord
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    dasha_info = tools.get_dasha_info(birth_dt, ctx.get("moon_longitude", 0))
    current_dasha = dasha_info.get("current_mahadasha", {}).get("lord", "")

    # Detect active doshas
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    dosha_result = tools.detect_doshas(natal_chart)
    active_doshas = [
        d["name"]
        for d in dosha_result.get("doshas", [])
        if isinstance(d, dict) and d.get("is_present")
    ]

    # Find weak planets
    weak_planets = []
    for pname, pdata in ctx.get("natal_planets", {}).items():
        if isinstance(pdata, dict):
            house = pdata.get("house", 1)
            strength = tools.get_planet_strength(
                pname, pdata, house, ctx.get("lagna_rashi", "Aries")
            )
            total = (
                strength.get("shadbala", {}).get("total", 5)
                if isinstance(strength.get("shadbala"), dict)
                else 5
            )
            if isinstance(total, int | float) and total < 4:
                weak_planets.append(pname)

    return tools.get_remedies(
        current_dasha=current_dasha,
        active_doshas=active_doshas,
        weak_planets=weak_planets,
        lagna_rashi=ctx.get("lagna_rashi", ""),
    )


def _exec_dasha_timeline(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    years = inp.get("years", 50)
    return tools.get_dasha_timeline(birth_dt, ctx.get("moon_longitude", 0), years=years)


def _exec_correlate_event(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    return tools.correlate_life_event(
        event_date=inp["event_date"],
        event_type=inp["event_type"],
        event_description=inp["description"],
        birth_datetime=ctx["birth_datetime"]
        if isinstance(ctx["birth_datetime"], str)
        else ctx["birth_datetime"].isoformat(),
        natal_planets=ctx.get("natal_planets", {}),
        moon_longitude=ctx.get("moon_longitude", 0),
        lagna_rashi=ctx.get("lagna_rashi", "Aries"),
    )


# ── Phase 2: Deep Analysis Handlers ──


def _exec_soul_purpose(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    return tools.get_atmakaraka_analysis(birth_dt, ctx["birth_lat"], ctx["birth_lon"])


def _exec_gem_recommendation(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    planet = inp.get("planet")
    return tools.get_gem_recommendation(
        birth_dt, ctx["birth_lat"], ctx["birth_lon"], gem_planet=planet
    )


def _exec_divisional_chart(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    chart_num = inp.get("chart_number", 9)
    return tools.get_divisional_charts(ctx.get("natal_planets", {}), charts=[chart_num])


def _exec_yoga_cancellation(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    yogas_result = tools.detect_yogas(natal_chart)
    yogas = yogas_result.get("yogas", [])

    sun_data = ctx.get("natal_planets", {}).get("sun", {})
    sun_lon = sun_data.get("longitude", 0) if isinstance(sun_data, dict) else 0

    return tools.check_yoga_cancellations(
        yogas=yogas,
        planets=ctx.get("natal_planets", {}),
        lagna_rashi=ctx.get("lagna_rashi", "Aries"),
        sun_longitude=sun_lon,
    )


def _exec_retrograde_effects(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.self.src.retrograde import get_retrograde_analysis

    return {
        **get_retrograde_analysis(ctx.get("natal_planets", {}), is_natal=True),
        "success": True,
    }


def _exec_combustion_status(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.self.src.combustion import get_combustion_analysis

    return {
        **get_combustion_analysis(ctx.get("natal_planets", {})),
        "success": True,
    }


# ── Phase 3: Advanced Systems Handlers ──


def _exec_varshaphal(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.context.src.varshaphal import get_varshaphal_analysis

    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    year = inp.get("year", datetime.utcnow().year)
    age = year - birth_dt.year

    # Determine lagna rashi index
    lagna_rashi = ctx.get("lagna_rashi", "Aries")
    rashi_names = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    lagna_idx = next((i for i, r in enumerate(rashi_names) if r.lower() == lagna_rashi.lower()), 0)

    result = get_varshaphal_analysis(
        birth_lagna_rashi=lagna_idx,
        age=max(0, age),
    )
    return {**result, "year": year, "success": True}


def _exec_kp_prediction(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    return tools.get_kp_analysis(
        birth_dt,
        ctx["birth_lat"],
        ctx["birth_lon"],
        query_type=inp.get("question_type", "career"),
    )


def _exec_prashna(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.self.src.prashna import analyze_prashna

    category = inp.get("category", "general")
    question = inp.get("question", "")
    now = datetime.utcnow()

    result = analyze_prashna(
        question=question,
        question_dt=now,
        latitude=ctx.get("birth_lat", 28.6139),
        longitude=ctx.get("birth_lon", 77.2090),
        category=category,
    )
    # Convert pydantic model or dict
    if hasattr(result, "model_dump"):
        return {**result.model_dump(), "success": True}
    elif isinstance(result, dict):
        return {**result, "success": True}
    return {"result": str(result), "success": True}


def _exec_ashtakavarga(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    chart = tools._dict_to_birth_chart(natal_chart)

    from packages.self.src.ashtakavarga import (
        calculate_bhinnashtakavarga,
        calculate_sarvashtakavarga,
    )

    planet_names = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
    from packages.core.src import Planet

    bav_data = {}
    for pname in planet_names:
        try:
            p_enum = Planet(pname)
            bav = calculate_bhinnashtakavarga(p_enum, chart)
            bav_data[pname] = bav if isinstance(bav, list) else list(bav)
        except Exception:
            bav_data[pname] = [0] * 12

    sav = calculate_sarvashtakavarga(chart)
    sav_list = sav if isinstance(sav, list) else list(sav)

    return {
        "bhinnashtakavarga": bav_data,
        "sarvashtakavarga": sav_list,
        "success": True,
    }


def _exec_alternative_dasha(inp: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    system = inp.get("system", "yogini")
    birth_dt = ctx["birth_datetime"]
    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)

    moon_lon = ctx.get("moon_longitude", 0)
    # Calculate nakshatra index and degree
    nak_idx = int((moon_lon * 27) / 360) + 1
    degree_in_nak = (moon_lon % (360 / 27)) * (13.333 / (360 / 27))

    if system == "yogini":
        from packages.context.src.yogini_dasha import get_current_yogini_dasha

        result = get_current_yogini_dasha(nak_idx, degree_in_nak, birth_dt)
        return {**result, "system": "yogini", "success": True}
    elif system == "ashtottari":
        from packages.context.src.ashtottari_dasha import get_current_ashtottari

        result = get_current_ashtottari(nak_idx, degree_in_nak, birth_dt)
        return {**result, "system": "ashtottari", "success": True}
    elif system == "narayana":
        from packages.guide.src.tools import get_tools

        tools = get_tools()
        natal_chart = {
            "planets": ctx.get("natal_planets", {}),
            "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
        }
        chart = tools._dict_to_birth_chart(natal_chart)

        from packages.context.src.narayana_dasha import get_current_narayana_dasha

        result = get_current_narayana_dasha(chart, birth_dt)
        return {**result, "system": "narayana", "success": True}
    return {"success": False, "error": f"Unknown dasha system: {system}"}


def _exec_jaimini_analysis(ctx: dict[str, Any]) -> dict[str, Any]:
    from packages.guide.src.tools import get_tools

    tools = get_tools()
    natal_chart = {
        "planets": ctx.get("natal_planets", {}),
        "lagna": {"sign": ctx.get("lagna_rashi", "Aries")},
    }
    chart = tools._dict_to_birth_chart(natal_chart)

    from packages.self.src.jaimini import (
        calculate_chara_karakas,
        get_all_chara_karaka_analysis,
    )

    karakas = calculate_chara_karakas(chart)
    karaka_list = []
    for k in karakas:
        if hasattr(k, "model_dump"):
            karaka_list.append(k.model_dump())
        elif isinstance(k, dict):
            karaka_list.append(k)
        else:
            karaka_list.append({"karaka": str(k)})

    analysis = get_all_chara_karaka_analysis(chart)

    # Serialize enum values
    def _serialize(obj: Any) -> Any:
        if hasattr(obj, "value"):
            return obj.value
        if isinstance(obj, dict):
            return {str(k): _serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_serialize(v) for v in obj]
        return obj

    return {
        "chara_karakas": _serialize(karaka_list),
        "analysis": _serialize(analysis),
        "success": True,
    }


def _exec_lookup_knowledge(inp: dict[str, Any]) -> dict[str, Any]:
    from packages.core.src.knowledge_loader import (
        load_definition,
        load_interpretation,
        load_rules,
    )

    query = inp.get("query", "").lower().strip()
    category = inp.get("category", "planet")

    # Map category to knowledge file names
    _category_files: dict[str, list[tuple[str, str]]] = {
        "planet": [
            ("definitions", "planets"),
            ("interpretations", "planet_interpretations"),
        ],
        "rashi": [
            ("definitions", "rashis"),
        ],
        "nakshatra": [
            ("definitions", "nakshatras"),
        ],
        "yoga": [
            ("rules", "yoga_rules"),
            ("rules", "advanced_yoga_rules"),
        ],
        "house": [
            ("definitions", "houses"),
        ],
        "dosha": [
            ("rules", "dosha_rules"),
        ],
    }

    loaders = {
        "definitions": load_definition,
        "rules": load_rules,
        "interpretations": load_interpretation,
    }
    results: list[dict[str, Any]] = []
    files = _category_files.get(category, [])

    for file_type, file_name in files:
        loader = loaders.get(file_type)
        if not loader:
            continue
        try:
            data = loader(file_name)
        except Exception:
            continue

        # Search through the loaded data for matching entries
        matches = _search_knowledge(data, query)
        if matches:
            results.extend(matches)

    return {
        "query": query,
        "category": category,
        "results": results[:10],
        "result_count": len(results),
        "success": True,
    }


def _search_knowledge(data: Any, query: str) -> list[dict[str, Any]]:
    """Recursively search knowledge data for entries matching the query."""
    matches: list[dict[str, Any]] = []
    if isinstance(data, dict):
        # Check if this dict itself is a matching entry
        name = str(data.get("name", data.get("id", ""))).lower()
        if query in name or name in query:
            matches.append(data)
        # Search nested structures
        for value in data.values():
            if isinstance(value, list | dict):
                matches.extend(_search_knowledge(value, query))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                name = str(item.get("name", item.get("id", ""))).lower()
                if query in name or name in query:
                    matches.append(item)
                else:
                    # Check description too
                    desc = str(item.get("description", "")).lower()
                    if query in desc:
                        matches.append(item)
    return matches
