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
    # Phase 1: Timing & Predictions
    elif tool_name == "get_forecast":
        return _blocks_forecast(result)
    elif tool_name == "get_upcoming_events":
        return _blocks_upcoming_events(result)
    elif tool_name == "get_muhurta":
        return _blocks_muhurta(result)
    elif tool_name == "get_remedies":
        return _blocks_remedies(result)
    elif tool_name == "get_dasha_timeline":
        return _blocks_dasha_timeline(result)
    elif tool_name == "correlate_event":
        return _blocks_correlate_event(result)
    # Phase 2: Deep Analysis
    elif tool_name == "get_soul_purpose":
        return _blocks_soul_purpose(result)
    elif tool_name == "get_gem_recommendation":
        return _blocks_gem_recommendation(result)
    elif tool_name == "get_divisional_chart":
        return _blocks_divisional_chart(result)
    elif tool_name == "check_yoga_cancellation":
        return _blocks_yoga_cancellation(result)
    elif tool_name == "get_retrograde_effects":
        return _blocks_retrograde_effects(result)
    elif tool_name == "get_combustion_status":
        return _blocks_combustion_status(result)
    # Phase 3: Advanced Systems
    elif tool_name == "get_varshaphal":
        return _blocks_varshaphal(result)
    elif tool_name == "get_kp_prediction":
        return _blocks_kp_prediction(result)
    elif tool_name == "get_prashna":
        return _blocks_prashna(result)
    elif tool_name == "get_ashtakavarga":
        return _blocks_ashtakavarga(result)
    elif tool_name == "get_alternative_dasha":
        return _blocks_alternative_dasha(result)
    elif tool_name == "get_jaimini_analysis":
        return _blocks_jaimini(result)
    elif tool_name == "lookup_knowledge":
        return _blocks_knowledge(result)
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


# ── Phase 1: Timing & Predictions block builders ──


def _blocks_forecast(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    forecast = result.get("forecast", result)
    if not isinstance(forecast, dict):
        return []

    # Day/period rating score card
    rating = forecast.get("day_rating", forecast.get("week_rating", forecast.get("month_rating")))
    if rating is not None:
        period = (
            "Day" if "day_rating" in forecast else "Week" if "week_rating" in forecast else "Month"
        )
        blocks.append(
            {
                "type": "score_card",
                "data": {
                    "label": f"{period} Rating",
                    "score": round(float(rating), 1) if isinstance(rating, int | float) else 0,
                    "max": 10,
                    "color": "#4CAF50"
                    if (isinstance(rating, int | float) and rating >= 6)
                    else "#FF9800",
                    "subtitle": forecast.get("summary", ""),
                },
            }
        )

    # Area ratings table
    areas = forecast.get("area_ratings", forecast.get("areas", []))
    if areas:
        area_list = (
            areas
            if isinstance(areas, list)
            else [{"area": k, "rating": v} for k, v in areas.items()]
            if isinstance(areas, dict)
            else []
        )
        if area_list:
            rows = []
            for a in area_list:
                if isinstance(a, dict):
                    rows.append(
                        [
                            str(a.get("area", a.get("id", ""))).title(),
                            str(round(float(a.get("rating", a.get("score", 0))), 1)),
                        ]
                    )
            if rows:
                blocks.append(
                    {"type": "table", "data": {"headers": ["Area", "Rating"], "rows": rows}}
                )

    # Recommendations as alerts
    recs = forecast.get("recommendations", [])
    if recs and isinstance(recs, list):
        blocks.append(
            {
                "type": "alert",
                "data": {
                    "level": "info",
                    "title": "Recommendations",
                    "message": "; ".join(str(r) for r in recs[:5]),
                },
            }
        )

    return blocks


def _blocks_upcoming_events(result: dict[str, Any]) -> list[dict[str, Any]]:
    triggers = result.get("triggers", [])
    if not triggers:
        return []

    rows = []
    for t in triggers[:15]:
        if isinstance(t, dict):
            rows.append(
                [
                    str(t.get("date", t.get("event_date", ""))),
                    str(t.get("event", t.get("description", ""))),
                    str(t.get("type", t.get("event_type", ""))),
                    str(t.get("significance", t.get("impact", ""))),
                ]
            )

    return [
        {
            "type": "table",
            "data": {
                "headers": ["Date", "Event", "Type", "Significance"],
                "rows": rows,
            },
        }
    ]


def _blocks_muhurta(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    score = result.get("score", result.get("quality_score", 0))
    quality = result.get("quality", result.get("overall_quality", "average"))

    color = (
        "#4CAF50"
        if quality in ("excellent", "good")
        else "#FF9800"
        if quality == "average"
        else "#FF5722"
    )
    blocks.append(
        {
            "type": "score_card",
            "data": {
                "label": "Muhurta Quality",
                "score": round(float(score), 1) if isinstance(score, int | float) else 0,
                "max": 100,
                "color": color,
                "subtitle": str(quality).title(),
            },
        }
    )

    # Inauspicious period alert
    inausp = result.get("inauspicious_periods", {})
    if isinstance(inausp, dict):
        warnings = []
        for period_name, period_data in inausp.items():
            if isinstance(period_data, dict) and period_data.get("active"):
                warnings.append(
                    f"{period_name}: {period_data.get('start', '')} - {period_data.get('end', '')}"
                )
        if warnings:
            blocks.append(
                {
                    "type": "alert",
                    "data": {
                        "level": "warning",
                        "title": "Inauspicious Periods",
                        "message": "; ".join(warnings),
                    },
                }
            )

    return blocks


def _blocks_remedies(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    remedies = result.get("remedies", result)
    if not isinstance(remedies, dict | list):
        return []

    remedy_list = remedies if isinstance(remedies, list) else remedies.get("remedies", [])
    if isinstance(remedy_list, list) and remedy_list:
        rows = []
        for r in remedy_list[:10]:
            if isinstance(r, dict):
                rows.append(
                    [
                        str(r.get("remedy", r.get("name", ""))),
                        str(r.get("type", r.get("category", ""))),
                        str(r.get("priority", r.get("importance", ""))),
                    ]
                )
        if rows:
            blocks.append(
                {"type": "table", "data": {"headers": ["Remedy", "Type", "Priority"], "rows": rows}}
            )

    # Top recommendation alert
    if isinstance(remedy_list, list) and remedy_list:
        top = remedy_list[0] if isinstance(remedy_list[0], dict) else {}
        if top:
            blocks.append(
                {
                    "type": "alert",
                    "data": {
                        "level": "info",
                        "title": "Top Recommendation",
                        "message": str(
                            top.get("remedy", top.get("name", top.get("description", "")))
                        ),
                    },
                }
            )

    return blocks


def _blocks_dasha_timeline(result: dict[str, Any]) -> list[dict[str, Any]]:
    periods = result.get("dasha_periods", result.get("dasha_timeline", []))
    if not isinstance(periods, list) or not periods:
        return []

    rows = []
    for p in periods[:20]:
        if isinstance(p, dict):
            lord = str(p.get("lord", p.get("planet", "")))
            start = str(p.get("start_date", p.get("start", "")))
            end = str(p.get("end_date", p.get("end", "")))
            years = str(p.get("years", ""))
            rows.append(
                [
                    lord.title(),
                    start[:10] if len(start) > 10 else start,
                    end[:10] if len(end) > 10 else end,
                    years,
                ]
            )

    return [
        {
            "type": "table",
            "data": {"headers": ["Lord", "Start", "End", "Years"], "rows": rows},
        }
    ]


def _blocks_correlate_event(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    correlation = result.get("correlation", result)
    if not isinstance(correlation, dict):
        return []

    score = correlation.get("correlation_score", correlation.get("score", 0))
    blocks.append(
        {
            "type": "score_card",
            "data": {
                "label": "Correlation Score",
                "score": round(float(score), 1) if isinstance(score, int | float) else 0,
                "max": 10,
                "color": "#4CAF50"
                if (isinstance(score, int | float) and score >= 6)
                else "#FF9800",
                "subtitle": correlation.get("summary", ""),
            },
        }
    )

    # Matching factors table
    factors = correlation.get("matching_factors", correlation.get("factors", []))
    if isinstance(factors, list) and factors:
        rows = [
            [
                str(f.get("factor", f.get("name", ""))),
                str(f.get("description", f.get("detail", ""))),
            ]
            for f in factors[:8]
            if isinstance(f, dict)
        ]
        if rows:
            blocks.append(
                {"type": "table", "data": {"headers": ["Factor", "Details"], "rows": rows}}
            )

    return blocks


# ── Phase 2: Deep Analysis block builders ──


def _blocks_soul_purpose(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    ak = result.get("atmakaraka", result)
    if not isinstance(ak, dict):
        return []

    planet = ak.get("atmakaraka_planet", ak.get("planet", ""))
    blocks.append(
        {
            "type": "score_card",
            "data": {
                "label": "Atmakaraka",
                "score": 0,
                "max": 0,
                "color": "#9C27B0",
                "subtitle": str(planet).title() if planet else "Unknown",
            },
        }
    )

    rows = []
    for key in ("karakamsha", "ishta_devata", "soul_purpose", "career_direction", "spiritual_path"):
        val = ak.get(key)
        if val:
            rows.append([key.replace("_", " ").title(), str(val)])
    if rows:
        blocks.append({"type": "table", "data": {"headers": ["Aspect", "Details"], "rows": rows}})

    return blocks


def _blocks_gem_recommendation(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    gems = result.get("gems", result)
    if not isinstance(gems, dict):
        return []

    # Primary and supporting gems table
    rows = []
    primary = gems.get("primary_gem", gems.get("recommended", {}))
    if isinstance(primary, dict):
        rows.append(
            [
                str(primary.get("gem", primary.get("name", ""))),
                str(primary.get("planet", "")),
                str(primary.get("weight", "")),
                str(primary.get("metal", "")),
                str(primary.get("finger", "")),
            ]
        )

    supporting = gems.get("supporting_gems", gems.get("secondary", []))
    if isinstance(supporting, list):
        for g in supporting[:3]:
            if isinstance(g, dict):
                rows.append(
                    [
                        str(g.get("gem", g.get("name", ""))),
                        str(g.get("planet", "")),
                        str(g.get("weight", "")),
                        str(g.get("metal", "")),
                        str(g.get("finger", "")),
                    ]
                )

    if rows:
        blocks.append(
            {
                "type": "table",
                "data": {"headers": ["Gem", "Planet", "Weight", "Metal", "Finger"], "rows": rows},
            }
        )

    # Contraindications alert
    contra = gems.get("contraindicated", gems.get("avoid", []))
    if contra:
        msg = ", ".join(str(c.get("gem", c) if isinstance(c, dict) else c) for c in contra[:5])
        blocks.append(
            {
                "type": "alert",
                "data": {"level": "warning", "title": "Contraindicated", "message": msg},
            }
        )

    return blocks


def _blocks_divisional_chart(result: dict[str, Any]) -> list[dict[str, Any]]:
    charts = result.get("divisional_charts", {})
    if not charts:
        return []

    blocks: list[dict[str, Any]] = []
    for chart_name, chart_data in charts.items():
        if not isinstance(chart_data, dict):
            continue
        rows = []
        for planet, pos in chart_data.items():
            if isinstance(pos, dict):
                rows.append(
                    [
                        str(planet).title(),
                        str(pos.get("sign", pos.get("rashi", ""))),
                    ]
                )
            elif isinstance(pos, str):
                rows.append([str(planet).title(), pos])

        if rows:
            blocks.append(
                {
                    "type": "table",
                    "data": {"headers": ["Planet", f"Sign ({chart_name})"], "rows": rows},
                }
            )

    return blocks


def _blocks_yoga_cancellation(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []

    total = result.get("total_yogas", 0)
    surviving = result.get("surviving_count", 0)
    cancelled = result.get("cancelled_count", 0)

    blocks.append(
        {
            "type": "score_card",
            "data": {
                "label": "Surviving Yogas",
                "score": surviving,
                "max": total,
                "color": "#4CAF50" if surviving > cancelled else "#FF9800",
                "subtitle": f"{cancelled} cancelled out of {total}",
            },
        }
    )

    # Cancelled yogas table
    cancelled_list = result.get("cancelled_yogas", [])
    if cancelled_list:
        rows = [
            [
                str(y.get("name", y.get("yoga_name", ""))),
                "Cancelled",
                str(y.get("cancel_reason", y.get("reason", ""))),
            ]
            for y in cancelled_list[:10]
            if isinstance(y, dict)
        ]
        if rows:
            blocks.append(
                {"type": "table", "data": {"headers": ["Yoga", "Status", "Reason"], "rows": rows}}
            )

    return blocks


def _blocks_retrograde_effects(result: dict[str, Any]) -> list[dict[str, Any]]:
    retro_planets = result.get("retrograde_planets", [])
    if not retro_planets:
        return [
            {
                "type": "alert",
                "data": {
                    "level": "info",
                    "title": "Retrograde",
                    "message": "No retrograde planets in natal chart",
                },
            }
        ]

    rows = []
    for r in retro_planets:
        if isinstance(r, dict):
            rows.append(
                [
                    str(r.get("planet", "")).title(),
                    str(r.get("effects", r.get("description", ""))),
                    str(r.get("karmic_theme", r.get("theme", ""))),
                ]
            )

    blocks: list[dict[str, Any]] = []
    if rows:
        blocks.append(
            {
                "type": "table",
                "data": {"headers": ["Planet", "Effects", "Karmic Theme"], "rows": rows},
            }
        )
    return blocks


def _blocks_combustion_status(result: dict[str, Any]) -> list[dict[str, Any]]:
    combust = result.get("combust_planets", [])
    if not combust:
        return [
            {
                "type": "alert",
                "data": {"level": "info", "title": "Combustion", "message": "No combust planets"},
            }
        ]

    rows = []
    for c in combust:
        if isinstance(c, dict):
            rows.append(
                [
                    str(c.get("planet", "")).title(),
                    "Yes" if c.get("is_combust") else "No",
                    str(round(float(c.get("angular_distance", 0)), 2)),
                    str(c.get("effects", c.get("description", ""))),
                ]
            )

    blocks: list[dict[str, Any]] = []
    if rows:
        blocks.append(
            {
                "type": "table",
                "data": {
                    "headers": ["Planet", "Combust", "Degrees from Sun", "Effects"],
                    "rows": rows,
                },
            }
        )
    return blocks


# ── Phase 3: Advanced Systems block builders ──


def _blocks_varshaphal(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    year = result.get("year", "")
    muntha = result.get("muntha", result.get("muntha_rashi", ""))
    varshesha = result.get("varshesha", result.get("year_lord", ""))

    rows = []
    if muntha:
        rows.append(["Muntha", str(muntha)])
    if varshesha:
        rows.append(["Varshesha (Year Lord)", str(varshesha)])
    prediction = result.get("general_prediction", result.get("prediction", ""))
    if prediction:
        rows.append(["Prediction", str(prediction)])

    if rows:
        blocks.append(
            {"type": "table", "data": {"headers": [f"Varshaphal {year}", "Details"], "rows": rows}}
        )

    return blocks


def _blocks_kp_prediction(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    kp = result.get("kp_analysis", result)
    if not isinstance(kp, dict):
        return []

    prediction = kp.get("prediction", {})
    if isinstance(prediction, dict):
        verdict = prediction.get("verdict", prediction.get("judgment", ""))
        confidence = prediction.get("confidence", 0)

        color = (
            "#4CAF50"
            if "yes" in str(verdict).lower() or "favorable" in str(verdict).lower()
            else "#FF5722"
        )
        blocks.append(
            {
                "type": "score_card",
                "data": {
                    "label": f"KP: {kp.get('query_type', '').title()}",
                    "score": round(float(confidence), 1)
                    if isinstance(confidence, int | float)
                    else 0,
                    "max": 100,
                    "color": color,
                    "subtitle": str(verdict),
                },
            }
        )

    # Cuspal sublords table
    cuspal = kp.get("cuspal_sublords", {})
    if isinstance(cuspal, dict) and cuspal:
        rows = [[f"House {k}", str(v)] for k, v in list(cuspal.items())[:12]]
        if rows:
            blocks.append(
                {"type": "table", "data": {"headers": ["House", "Sub-Lord"], "rows": rows}}
            )

    return blocks


def _blocks_prashna(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []

    judgment = result.get("judgment", result.get("answer", ""))
    if judgment:
        blocks.append(
            {
                "type": "score_card",
                "data": {
                    "label": "Prashna Answer",
                    "score": 0,
                    "max": 0,
                    "color": "#9C27B0",
                    "subtitle": str(judgment),
                },
            }
        )

    rows = []
    for key in ("timing", "recommendation", "lagna_lord", "moon_nakshatra"):
        val = result.get(key)
        if val:
            rows.append([key.replace("_", " ").title(), str(val)])
    if rows:
        blocks.append({"type": "table", "data": {"headers": ["Factor", "Details"], "rows": rows}})

    return blocks


def _blocks_ashtakavarga(result: dict[str, Any]) -> list[dict[str, Any]]:
    bav = result.get("bhinnashtakavarga", {})
    sav = result.get("sarvashtakavarga", [])
    if not bav and not sav:
        return []

    blocks: list[dict[str, Any]] = []

    # SAV summary as a table row
    if isinstance(sav, list) and sav:
        rashi_names = [
            "Ari",
            "Tau",
            "Gem",
            "Can",
            "Leo",
            "Vir",
            "Lib",
            "Sco",
            "Sag",
            "Cap",
            "Aqu",
            "Pis",
        ]
        sav_rows = [
            [rashi_names[i] if i < len(rashi_names) else str(i + 1), str(v)]
            for i, v in enumerate(sav[:12])
        ]
        blocks.append(
            {"type": "table", "data": {"headers": ["Sign", "SAV Bindus"], "rows": sav_rows}}
        )

    # BAV per planet
    if isinstance(bav, dict):
        for planet, scores in bav.items():
            if isinstance(scores, list):
                total = sum(s for s in scores if isinstance(s, int))
                blocks.append(
                    {
                        "type": "alert",
                        "data": {
                            "level": "info",
                            "title": f"{planet.title()} BAV",
                            "message": f"Total bindus: {total}",
                        },
                    }
                )

    return blocks


def _blocks_alternative_dasha(result: dict[str, Any]) -> list[dict[str, Any]]:
    system = result.get("system", "")
    current = result.get("current_period", result.get("current", {}))

    blocks: list[dict[str, Any]] = []
    if isinstance(current, dict):
        lord = current.get("lord", current.get("planet", current.get("yogini", "")))
        blocks.append(
            {
                "type": "score_card",
                "data": {
                    "label": f"{system.title()} Dasha",
                    "score": 0,
                    "max": 0,
                    "color": "#2196F3",
                    "subtitle": f"Current: {lord}",
                },
            }
        )

    periods = result.get("periods", result.get("sequence", []))
    if isinstance(periods, list) and periods:
        rows = []
        for p in periods[:15]:
            if isinstance(p, dict):
                rows.append(
                    [
                        str(p.get("lord", p.get("planet", p.get("yogini", "")))),
                        str(p.get("start_date", p.get("start", "")))[:10],
                        str(p.get("end_date", p.get("end", "")))[:10],
                    ]
                )
        if rows:
            blocks.append(
                {"type": "table", "data": {"headers": ["Lord", "Start", "End"], "rows": rows}}
            )

    return blocks


def _blocks_jaimini(result: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []

    karakas = result.get("chara_karakas", [])
    if isinstance(karakas, list) and karakas:
        rows = []
        for k in karakas:
            if isinstance(k, dict):
                rows.append(
                    [
                        str(k.get("karaka", k.get("karaka_name", ""))),
                        str(k.get("planet", k.get("planet_name", ""))),
                        str(k.get("degree", k.get("degree_in_sign", ""))),
                    ]
                )
        if rows:
            blocks.append(
                {"type": "table", "data": {"headers": ["Karaka", "Planet", "Degree"], "rows": rows}}
            )

    analysis = result.get("analysis", {})
    if isinstance(analysis, dict):
        for key, val in analysis.items():
            if isinstance(val, str) and val:
                blocks.append(
                    {
                        "type": "alert",
                        "data": {
                            "level": "info",
                            "title": key.replace("_", " ").title(),
                            "message": val,
                        },
                    }
                )

    return blocks


def _blocks_knowledge(result: dict[str, Any]) -> list[dict[str, Any]]:
    results = result.get("results", [])
    if not results:
        return [
            {
                "type": "alert",
                "data": {
                    "level": "info",
                    "title": "Knowledge",
                    "message": f"No results for '{result.get('query', '')}'.",
                },
            }
        ]

    blocks: list[dict[str, Any]] = []
    for entry in results[:5]:
        if isinstance(entry, dict):
            name = entry.get("name", entry.get("id", ""))
            desc = entry.get("description", entry.get("meaning", entry.get("effects", "")))
            if name or desc:
                blocks.append(
                    {
                        "type": "alert",
                        "data": {"level": "info", "title": str(name), "message": str(desc)[:500]},
                    }
                )

    return blocks


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
