"""Chart data collector for the 108 Life Reading report.

Single function: collect_chart_data(birth_data) -> dict.

Walks the existing 108 calculation engine end-to-end and returns one
report-shaped dict containing every slice the narrative + template layers
need. Designed so the rest of the report engine never has to re-call
calculation tools — all data is computed once, here.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from packages.context.src.chara_dasha_transit import get_chara_dasha_overlay_from_raw
from packages.context.src.dasha import (
    get_antardasha_sequence,
    get_current_dasha,
    get_mahadasha_sequence,
)
from packages.context.src.state_engine import compute_state_vector
from packages.context.src.tithi_pravesha import (
    cast_tithi_pravesha_chart,
    interpret_tithi_pravesha,
)
from packages.context.src.transit_tracker import (
    get_ambient_signals,
    get_upcoming_triggers,
)
from packages.cosmos.src.ephemeris import (
    get_all_planets,
    get_ayanamsa,
    get_house_cusps,
    get_julian_day,
)
from packages.report.src.lagna_reconcile import reconcile_lagna
from packages.self.src.dosha_detector import DoshaDetector
from packages.self.src.yoga_detector import YogaDetector

_RASHI = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]
_RASHI_TITLE = [r.title() for r in _RASHI]
_NAK = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "P.Phalguni",
    "U.Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "P.Ashadha",
    "U.Ashadha",
    "Shravana",
    "Dhanishtha",
    "Shatabhisha",
    "P.Bhadrapada",
    "U.Bhadrapada",
    "Revati",
]


def collect_chart_data(
    birth_datetime: str,
    birth_lat: float,
    birth_lon: float,
    full_name: str | None = None,
    user_question: str | None = None,
    addons: list[str] | None = None,
    query_datetime: str | None = None,
    intake_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the complete report-input dict for one customer.

    Args:
        birth_datetime: ISO format with tz, e.g. "1992-12-03T03:00:00+05:30".
        birth_lat: Birth latitude.
        birth_lon: Birth longitude.
        full_name: Customer's full name (appears in report).
        user_question: The customer's primary question (drives Section 5).
        addons: Optional add-on slugs (e.g. ["career", "relationships",
                                            "year_ahead"]).
        query_datetime: ISO moment to evaluate "now" (default: actual now).

    Returns:
        Nested dict with keys:
            meta, birth, lagna, planets, panchanga,
            dasha (current + sequences), yogas, doshas,
            state_vector, ambient_signals, tithi_pravesha,
            chara_dasha, upcoming_events, vry_yogas,
            user_question, addons.
    """
    addons = addons or []
    birth_dt = datetime.fromisoformat(birth_datetime)
    query_dt = (
        datetime.fromisoformat(query_datetime)
        if query_datetime
        else datetime.now(tz=birth_dt.tzinfo)
        if birth_dt.tzinfo
        else datetime.now()
    )

    # ── 1. Birth chart core ──
    jd = get_julian_day(birth_dt)
    raw_planets = get_all_planets(jd)
    cusps_data = get_house_cusps(jd, birth_lat, birth_lon)
    ayan = get_ayanamsa(jd)
    # get_house_cusps already returns the SIDEREAL ascendant (ayanamsha
    # subtracted inside). Earlier this code subtracted ayanamsha a second
    # time, producing a chart shifted ~24° backward — which silently moved
    # cusp-births into the previous sign (e.g. Libra 0.91° read as Virgo 7.16°).
    asc_sid = float(cusps_data.get("ascendant", 0.0))
    asc_trop = (asc_sid + ayan) % 360
    # Reconcile cusp edge cases against popular convention
    lagna_idx, lagna_deg, lagna_note = reconcile_lagna(asc_sid, asc_trop)

    natal_planets: dict[str, dict[str, Any]] = {}
    planets_list: list[dict[str, Any]] = []
    for pname, pdata in raw_planets.items():
        lon = float(pdata["longitude"])
        sign_idx = int(lon // 30) % 12
        house = ((sign_idx - lagna_idx) % 12) + 1
        nak_idx = int(lon // 13.333333333) % 27
        pada = int((lon % 13.333333333) / 3.333333333) + 1
        is_retro = bool(pdata.get("is_retrograde", False))
        natal_planets[pname] = {
            "longitude": lon,
            "house": house,
            "is_retrograde": is_retro,
            "speed": float(pdata.get("speed", 0.0)),
        }
        planets_list.append(
            {
                "name": pname,
                "longitude": round(lon, 4),
                "rashi": _RASHI_TITLE[sign_idx],
                "rashi_idx": sign_idx,
                "rashi_degree": round(lon % 30, 2),
                "house": house,
                "nakshatra": _NAK[nak_idx],
                "nakshatra_pada": pada,
                "is_retrograde": is_retro,
            }
        )

    moon_lon = float(raw_planets["moon"]["longitude"])
    moon_rashi_idx = int(moon_lon // 30) % 12
    moon_nak_idx = int(moon_lon // 13.333333333) % 27
    moon_pada = int((moon_lon % 13.333333333) / 3.333333333) + 1

    # ── 2. Dashas (current + full Mahadasha sequence) ──
    current_dasha = get_current_dasha(birth_dt, moon_lon, query_dt)
    md_sequence = get_mahadasha_sequence(birth_dt, moon_lon, years=120)
    md_for_report = [
        {
            "lord": p["lord"],
            "start": p["start_date"].isoformat()
            if hasattr(p["start_date"], "isoformat")
            else str(p["start_date"]),
            "end": p["end_date"].isoformat()
            if hasattr(p["end_date"], "isoformat")
            else str(p["end_date"]),
            "years": round(p.get("years", 0), 2),
        }
        for p in md_sequence
    ]
    # Antardashas of current MD (for "what's left of this MD" section)
    current_md_antars: list[dict[str, Any]] = []
    if current_dasha:
        cur_md = current_dasha["mahadasha"]
        # Find that MD in sequence to get its dates
        for md in md_sequence:
            if md["lord"] == cur_md["lord"] and md["start_date"] <= query_dt < md["end_date"]:
                ad_seq = get_antardasha_sequence(md["lord"], md["start_date"], md["end_date"])
                current_md_antars = [
                    {
                        "lord": a["lord"],
                        "start": a["start_date"].isoformat(),
                        "end": a["end_date"].isoformat(),
                        "years": round(a.get("years", 0), 2),
                    }
                    for a in ad_seq
                ]
                break

    # ── 3. State vector + ambient + tithi pravesha + chara dasha ──
    lagna_rashi = _RASHI[lagna_idx]
    moon_rashi = _RASHI[moon_rashi_idx]
    state_vector = compute_state_vector(
        birth_datetime=birth_datetime,
        birth_lat=birth_lat,
        birth_lon=birth_lon,
        natal_planets=natal_planets,
        moon_longitude=moon_lon,
        lagna_rashi=lagna_rashi,
        moon_rashi=moon_rashi,
        query_datetime=query_dt.isoformat(),
    )

    ambient = get_ambient_signals(
        natal_planets=natal_planets,
        lagna_rashi=lagna_rashi,
        moon_longitude=moon_lon,
        query_datetime=query_dt,
        birth_datetime=birth_dt,
    )

    # Tithi Pravesha for current lunar age
    natal_sun = float(raw_planets["sun"]["longitude"])
    delta_days = (
        (query_dt - birth_dt).days
        if birth_dt.tzinfo == query_dt.tzinfo
        else (query_dt.replace(tzinfo=None) - birth_dt.replace(tzinfo=None)).days
    )
    year_offset = max(1, int(delta_days / 354.36707))
    try:
        tp_chart = cast_tithi_pravesha_chart(
            birth_dt,
            natal_sun,
            moon_lon,
            target_year_offset=year_offset,
            location_lat=birth_lat,
            location_lon=birth_lon,
        )
        tp_chart["interpretation"] = interpret_tithi_pravesha(tp_chart, natal_planets, lagna_idx)
    except Exception:
        tp_chart = None

    try:
        chara_overlay = get_chara_dasha_overlay_from_raw(
            birth_dt,
            birth_lat,
            birth_lon,
            natal_planets,
            lagna_rashi,
            moon_lon,
            moon_rashi,
            query_dt,
        )
    except Exception:
        chara_overlay = None

    # Upcoming events — next 90 days
    try:
        upcoming = get_upcoming_triggers(
            natal_planets=natal_planets,
            lagna_rashi=lagna_rashi,
            moon_rashi=moon_rashi,
            start_date=query_dt,
            days_ahead=90,
            birth_datetime=birth_dt,
            moon_longitude=moon_lon,
        )
    except Exception:
        upcoming = []

    # ── 4. Yogas + Doshas (full natal detection) ──
    natal_yogas: list[dict[str, Any]] = []
    natal_doshas: list[dict[str, Any]] = []
    try:
        yd = YogaDetector()
        # Build BirthChart for typed detectors
        from packages.context.src.state_engine import _build_birth_chart

        chart = _build_birth_chart(
            birth_dt,
            birth_lat,
            birth_lon,
            natal_planets,
            lagna_rashi,
            moon_rashi,
            moon_lon,
        )
        natal_yogas = [
            {
                "name": y.name,
                "strength": getattr(y, "strength", 0.5),
                "description": getattr(y, "description", ""),
            }
            for y in yd.detect_all_yogas(chart)
        ]
        dd = DoshaDetector()
        # IMPORTANT: method is `detect_all()`, not `detect_all_doshas()`.
        # Previous wrong name was silently swallowed by the bare except below,
        # producing reports with `doshas: []` for every chart since launch.
        natal_doshas = [
            {
                "name": d.name,
                "severity": getattr(d, "severity", "moderate"),
                "description": getattr(d, "description", ""),
                "cancellation_factors": getattr(d, "cancellation_factors", []),
                "is_cancelled": getattr(d, "is_cancelled", False),
                "from_lagna": getattr(d, "from_lagna", None),
                "from_moon": getattr(d, "from_moon", None),
                "from_venus": getattr(d, "from_venus", None),
            }
            for d in dd.detect_all(chart)
        ]
    except Exception as e:  # pragma: no cover — keep import errors loud
        import logging

        logging.getLogger(__name__).warning(
            "Dosha detection failed silently: %s — reports will have empty doshas. "
            "Fix the underlying error rather than relying on this fallback.",
            e,
        )

    # VRY (Vipreet Raja Yogas) — pulled from state vector output
    vry_yogas = state_vector.get("natal_vipreet_raja_yogas", [])

    return {
        "meta": {
            "report_name": "108 Life Reading",
            "generated_at": query_dt.isoformat(),
            "engine_version": "108-core/2.0",
        },
        "birth": {
            "full_name": full_name or "Native",
            "datetime": birth_datetime,
            "datetime_iso": birth_dt.isoformat(),
            "datetime_human": birth_dt.strftime("%d %B %Y, %I:%M %p"),
            "lat": birth_lat,
            "lon": birth_lon,
        },
        "lagna": {
            "rashi": _RASHI_TITLE[lagna_idx],
            "rashi_idx": lagna_idx,
            "degree": round(lagna_deg, 2),
            "reconciliation_note": lagna_note,
        },
        "moon": {
            "rashi": _RASHI_TITLE[moon_rashi_idx],
            "longitude": round(moon_lon, 4),
            "nakshatra": _NAK[moon_nak_idx],
            "pada": moon_pada,
        },
        "planets": planets_list,
        "natal_planets_dict": natal_planets,
        "dasha": {
            "current": current_dasha,
            "mahadasha_sequence": md_for_report,
            "current_md_antardashas": current_md_antars,
        },
        "yogas": natal_yogas,
        "doshas": natal_doshas,
        "vry_yogas": vry_yogas,
        "state_vector": state_vector,
        "ambient_signals": ambient,
        "tithi_pravesha": tp_chart,
        "chara_dasha_overlay": chara_overlay,
        "upcoming_events": upcoming[:25],  # cap for report length
        "user_question": user_question,
        "addons": addons,
        # Optional intake events from customer: list of dicts with shape
        # {"date_iso": "2024-12-15" | "year": 2024 | "year_range": [2017, 2025],
        #  "type": "elder_death" | "move" | "job_loss" | "financial_drought"
        #          | "relationship_end" | "career_change" | "spiritual_shift"
        #          | "health" | "windfall" | "other",
        #  "description": "free text describing what happened"}
        # When present, agents (esp. what_already_happened) MUST map each event
        # to the dasha/transit signature active at that date and use it as
        # retrodictive credibility before any predictive content.
        "intake_events": intake_events or [],
    }
