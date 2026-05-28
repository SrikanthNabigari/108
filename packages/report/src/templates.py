"""Report section templates and assembly for the 108 Life Reading.

The report has 10 sections (configurable). Each section is a function
that takes the report-data dict (from data_collector.collect_chart_data)
plus optional narrative-text from the synthesizer, and returns Markdown.

The base report renders sections 1-10 (~8-12 pages). Add-ons append
extra sections (career deep-dive, relationships deep-dive, year-ahead).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Ordered ids of the base report. Each id maps to a render_section_<id>
# function below.
REPORT_SECTIONS: list[str] = [
    "opening",  # Cover with personalized hook
    "table_of_contents",  # Visual TOC right after the cover
    "your_chart",  # Chart wheel — see your chart FIRST
    "who_you_are",  # The personal payoff IMMEDIATELY after the chart
    "life_story_spine",  # v12 — WHAT-WHEN-WHY predictive spine (the headline page)
    # CONDITIONAL — fires only when customer provided intake_events. Maps each
    # event to the dasha/transit signature active at that date — the
    # retrodictive credibility section that earns the rest of the report.
    "what_already_happened",
    "arc_so_far",  # Past dashas (dasha pyramid embedded here)
    "where_you_are_now",
    "answering_your_question",
    "next_12_months",
    # Emotional arc: friction first, then the counterweights, then action.
    # Reader leaves the report on an uplift, not a downer.
    "structural_challenges",
    "sade_sati_deep_dive",  # CONDITIONAL — auto-fires only when Sade Sati active
    "hidden_strengths",
    "what_to_do_next",
    "closing_cta",  # 3-move summary + decisive date
    # NOTE: reference_primer (the educational diagram cards) + chart_vitals are
    # appended AFTER addons as a back APPENDIX (see sections_for_addons) — the
    # customer reads about THEMSELVES first, not a textbook. sources_and_method
    # closes the document.
    "sources_and_method",
]


# Sections that the system auto-surfaces ONLY when their structural trigger
# is active in the chart — customer doesn't pick these (they don't know they
# have them). Compare: ADDON_SECTION_MAP entries are customer-chosen topics.
def is_section_active_for_chart(section_id: str, data: dict[str, Any]) -> bool:
    """True if a conditional section should render for this chart, else False."""
    if section_id == "what_already_happened":
        # Fires only when customer provided intake_events. Otherwise skipped
        # silently so a non-intake customer gets the same report flow minus
        # this section.
        return bool(data.get("intake_events"))
    if section_id == "sade_sati_deep_dive":
        sade = (data.get("state_vector") or {}).get("sade_sati") or {}
        if sade.get("active"):
            return True
        # Also fire if Sade Sati begins within next 12 months — heads-up matters
        # (Looks for sade_sati.next_start_date if state_engine provides it.)
        next_start = sade.get("next_start_date")
        if next_start:
            try:
                from datetime import datetime, timedelta

                ns = datetime.fromisoformat(str(next_start).replace("Z", "+00:00"))
                gen = datetime.fromisoformat(data["meta"]["generated_at"])
                if ns.tzinfo and not gen.tzinfo:
                    ns = ns.replace(tzinfo=None)
                if (ns - gen) <= timedelta(days=365):
                    return True
            except Exception:
                pass
        return False
    return True  # all other sections always render


# ── Helper: pretty data formatters ──


def _format_planet_one_line(p: dict[str, Any]) -> str:
    retro = " (R)" if p.get("is_retrograde") else ""
    return (
        f"{p['name'].title():9s} {p['rashi']:11s} {p['rashi_degree']:5.2f}°  "
        f"H{p['house']:<2}  {p['nakshatra']} P{p['nakshatra_pada']}{retro}"
    )


def _format_dasha_line(d: dict[str, Any]) -> str:
    return (
        f"**{d['mahadasha']['lord'].title()}** Mahadasha "
        f"(ends {str(d['mahadasha']['end_date'])[:10]}) · "
        f"**{d['antardasha']['lord'].title()}** Antardasha "
        f"(ends {str(d['antardasha']['end_date'])[:10]}) · "
        f"**{d['pratyantardasha']['lord'].title()}** Pratyantardasha"
    )


# ── Section renderers ──
# Each takes (data, narrative) where narrative is an optional string from the
# AI synthesizer. Returns the section's Markdown.


def section_opening(data: dict[str, Any], narrative: str | None = None) -> str:
    """Cover page. If `narrative` is provided (from stitcher's cover_hook), use it;
    otherwise fall back to the static voice intro derived from lagna/moon.
    """
    from packages.report.src.narrative import quick_voice_intro

    name = data["birth"]["full_name"]
    lagna = data["lagna"]
    moon = data["moon"]
    cur = data["dasha"]["current"]
    # Cover hook block — either personalized (from stitcher) or static fallback
    if narrative:
        hook_html = f'\n<div class="cover-hook">\n\n{narrative}\n\n</div>\n'
    else:
        hook_html = quick_voice_intro(data)
    return f"""# Your 108 Life Reading

**{name}**
*Born {data['birth']['datetime_human']}*

---

### Your chart in one line

**{lagna['rashi']} Lagna · {moon['rashi']} Moon · {moon['nakshatra']} Pada {moon['pada']}**

### The chapter you're in

| | |
|---|---|
| Mahadasha | {cur['mahadasha']['lord'].title()} (until {str(cur['mahadasha']['end_date'])[:10]}) |
| Antardasha | {cur['antardasha']['lord'].title()} (until {str(cur['antardasha']['end_date'])[:10]}) |
| Lagna lord | {_lagna_lord_for(lagna['rashi']).title()} |

{hook_html}
"""


def _lagna_lord_for(lagna_rashi: str) -> str:
    """Return the planet ruling the given lagna sign."""
    rulers = {
        "Aries": "mars",
        "Taurus": "venus",
        "Gemini": "mercury",
        "Cancer": "moon",
        "Leo": "sun",
        "Virgo": "mercury",
        "Libra": "venus",
        "Scorpio": "mars",
        "Sagittarius": "jupiter",
        "Capricorn": "saturn",
        "Aquarius": "saturn",
        "Pisces": "jupiter",
    }
    return rulers.get(lagna_rashi, "")


def section_who_you_are(data: dict[str, Any], narrative: str | None = None) -> str:
    from packages.report.src.narrative import quick_who_you_are, quick_who_you_are_planets

    lagna = data["lagna"]
    moon = data["moon"]
    yogas_block = quick_who_you_are(data)
    planets_block = quick_who_you_are_planets(data)
    return f"""## The Architecture

*Who you are, structurally*

Your **{lagna['rashi']} Lagna** is the front door of who you are — how you show up. Your **{moon['rashi']} Moon** in **{moon['nakshatra']}** (Pada {moon['pada']}) is your inner weather — how you actually feel.

The Lagna is the role you play; the Moon is the self underneath it. Where they pull in different directions, that tension is the engine of the chart, not a flaw in it.
{planets_block}
{yogas_block}

{narrative or ''}
"""


def section_arc_so_far(data: dict[str, Any], narrative: str | None = None) -> str:
    """The narrative arc of past dashas — uses the lifeline timeline only.

    The dasha pyramid was removed (v12) because the personalized
    dasha-nesting card in the reference primer already shows the
    customer's current MD/AD/PD with you-are-here markers. Showing both
    was redundant and confusing.
    """
    from packages.report.src.diagrams import lifeline_svg

    md_seq = data["dasha"]["mahadasha_sequence"][:6]
    rows = "\n".join(
        f"| {m['lord'].title():8s} | {m['start'][:10]} → {m['end'][:10]} | {m['years']:.1f}y |"
        for m in md_seq
    )
    lifeline = lifeline_svg(data)
    return f"""## Where You Came From

*The periods that shaped you*

Your life moves through Mahadasha periods — each ruled by a planet, each with its own theme. The horizontal lifeline below shows every period from birth onwards. Each block is a Mahadasha, sized by its years, coloured by its ruling planet. The yellow line marks today.

<div style="margin:18pt 0 6pt 0;text-align:center;">
{lifeline}
<p class="caption-small" style="margin-top:4pt;">
Past periods to the left of <span style="color:#c9a96e;">TODAY</span>; future periods to the right. Read the colors against the navagraha legend on the previous pages.
</p>
</div>

The first six periods of your life, in order:

| Lord | Period | Years |
|------|--------|-------|
{rows}

{narrative or '*(narrative synthesizer fills the past-to-present arc here)*'}
"""


def _natal_support_band(score: float) -> tuple[str, str]:
    """Map a 0-10 natal-support score to (label, color)."""
    if score >= 7.0:
        return "exceptional", "#c9a96e"
    if score >= 5.0:
        return "strong", "#22c55e"
    if score >= 3.0:
        return "moderate", "#c0d4ed"
    return "weak", "#dc2626"


def section_what_already_happened(data: dict[str, Any], narrative: str | None = None) -> str:
    """Section: 'What Already Happened' — retrodictive credibility from intake events.

    Only renders when customer provided intake_events. Maps each event to the
    dasha/transit signature active at that date so the reader sees their own
    past life events explained by the chart BEFORE any predictive content.
    """
    events = data.get("intake_events") or []
    if not events:
        return ""
    # Tiny event list at the top so the reader sees what they told us being
    # mirrored back. The narrative (from the agent) does the actual chart work.
    listed = "\n".join(
        f"- {ev.get('description', '?')}"
        + (
            f" *(around {ev.get('date_iso', ev.get('year', ev.get('year_range', '?')))})*"
            if (ev.get("date_iso") or ev.get("year") or ev.get("year_range"))
            else ""
        )
        for ev in events[:8]
    )
    return f"""## What Already Happened

*Reading the past five-to-ten years back to you through the chart — so you can verify the chart actually knows you before it tells you anything about what comes next.*

{listed}

{narrative or '*(narrative pending — the agent maps each event above to its dasha/transit signature)*'}
"""


def section_where_you_are_now(data: dict[str, Any], narrative: str | None = None) -> str:
    """Section 3 — This Chapter of Your Life (life-window framing, not today)."""
    sv = data["state_vector"]
    sade_sati = sv.get("sade_sati", {})
    sade_line = (
        f"\n**Sade Sati:** {sade_sati.get('phase', '').title()} phase active.\n"
        if sade_sati.get("active")
        else ""
    )
    # The 8 area natal-support scores (structural, not today's transient state)
    areas = sorted(sv["areas"], key=lambda x: -x["natal_support"]["score"])
    area_rows = "\n".join(
        f"| {a['name']} | <b style='color:{_natal_support_band(a['natal_support']['score'])[1]};'>"
        f"{_natal_support_band(a['natal_support']['score'])[0]}</b> "
        f"({a['natal_support']['score']:.1f}/10) | "
        f"{a['natal_support'].get('dispositor', '-').title()} (H{a['natal_support'].get('dispositor_house','?')}) |"
        for a in areas
    )
    return f"""## The Years You're In

*Your current life-window*

{_format_dasha_line(data['dasha']['current'])}

{sade_line}

### Structural support per life area

Each life area in your chart has a *natal-support* score — a 0-10 reading of how the structural foundations of that domain were built into your chart at birth. It does not vary by day or transit. Read it as: a `strong` area is one whose ruler, houses, and dispositors are placed favorably enough that — when the right dasha runs — it will respond. A `weak` area is one whose structural ground is thin; the same dasha will produce less here than elsewhere. <span class="caption-small" style="display:inline;">Bands: weak 0-3 · moderate 3-5 · strong 5-7 · exceptional 7+.</span>

| Area | Natal Support | Dispositor |
|------|---------------|------------|
{area_rows}

{narrative or ''}
"""


def section_answering_your_question(data: dict[str, Any], narrative: str | None = None) -> str:
    q = data.get("user_question") or "(no question submitted)"
    if narrative:
        # Agent narrative usually includes the question; just render it
        return f"## The Question You Asked\n\n*What the chart says*\n\n{narrative}\n"
    return f"""## The Question You Asked

*What the chart says*

> *{q}*

*(narrative synthesizer answers using chart specifics here)*
"""


def section_next_12_months(data: dict[str, Any], narrative: str | None = None) -> str:
    if narrative:
        # Agent narrative replaces the bare data table
        return f"## What's Coming\n\n*The next twelve months*\n\n{narrative}\n"
    upcoming = data.get("upcoming_events", [])[:8]
    rows = []
    for e in upcoming:
        date = e.get("date", "?")
        typ = e.get("type", "?")
        if typ == "ingress":
            line = f"{e.get('planet','?').title()} enters {e.get('new_sign','?').title()}"
        elif typ == "conjunction":
            line = f"{e.get('transit_planet','?').title()} conjuncts natal {e.get('natal_planet','?').title()}"
        elif typ == "aspect":
            line = f"{e.get('transit_planet','?').title()} aspects natal {e.get('natal_planet','?').title()}"
        elif typ == "dasha_change":
            line = f"Dasha change: {e.get('new_lord','?').title()}"
        elif typ == "retrograde_station":
            line = f"{e.get('planet','?').title()} {e.get('station','?')}"
        else:
            line = typ
        rows.append(f"| {date[:10]} | {line} |")
    rows_md = "\n".join(rows) if rows else "| - | (no major triggers detected) |"
    tp = data.get("tithi_pravesha")
    tp_line = ""
    if tp:
        interp = tp.get("interpretation", {})
        tp_line = f"\n**This lunar year's ruler:** {interp.get('year_ruler', '?').title()}.\n"
    return f"""## What's Coming

*The next twelve months*

{tp_line}
| Date | Event |
|------|-------|
{rows_md}
"""


def section_hidden_strengths(data: dict[str, Any], narrative: str | None = None) -> str:
    if narrative:
        # Agent narrative already covers yogas comprehensively
        return (
            f"## What You Haven't Used Yet\n\n*Strengths waiting for activation*\n\n{narrative}\n"
        )
    vry = data.get("vry_yogas", [])
    vry_block = (
        "\n".join(
            f"- **{y['name']}** — your {y['lord_planet'].title()} (lord of H{y['lord_of_house']}) sits in H{y['sits_in_house']}. Activates as a Raja Yoga when this planet runs as MD or AD."
            for y in vry
        )
        if vry
        else "- (no Vipreet Raja Yogas detected)"
    )
    return f"""## What You Haven't Used Yet

*Strengths waiting for activation*

These are placements that don't show up in everyday life but carry significant power when activated by dasha or transit.

### Vipreet Raja Yogas

{vry_block}
"""


def section_structural_challenges(data: dict[str, Any], narrative: str | None = None) -> str:
    if narrative:
        # Agent narrative names + interprets the doshas
        return (
            f"## The Friction You Inherited\n\n*Patterns to work with, not deny*\n\n{narrative}\n"
        )
    doshas = data.get("doshas", [])
    if doshas:
        rows = "\n".join(f"- **{d['name']}** (severity: {d.get('severity', '?')})" for d in doshas)
    else:
        rows = "- (no significant doshas detected)"
    return f"""## The Friction You Inherited

*Patterns to work with, not deny*

Every chart has friction points. Naming them removes their power. These are the patterns to work *with*, not against. The strengths that balance them follow in the next section.

{rows}
"""


def section_what_to_do_next(data: dict[str, Any], narrative: str | None = None) -> str:
    return f"""## Your Move

*The next concrete steps*

{narrative or '*(narrative synthesizer fills 3 specific actions, 1 thing to stop, 1 thing to start)*'}
"""


def section_your_chart(data: dict[str, Any], narrative: str | None = None) -> str:
    """Page 2: the personalized chart wheel — see your chart before reading about it."""
    from packages.report.src.diagrams import PLANET_COLORS, PLANET_GLYPHS, chart_wheel_svg

    svg = chart_wheel_svg(data["natal_planets_dict"], data["lagna"]["rashi_idx"])
    rows = ""
    for p in data.get("planets", []):
        retro = "<span style='color:#dc2626;'>(R)</span>" if p.get("is_retrograde") else ""
        color = PLANET_COLORS.get(p["name"], "#fff")
        rows += (
            f'<tr><td><b style="color:{color};">{PLANET_GLYPHS.get(p["name"], "?")} '
            f'{p["name"].title()}</b></td>'
            f'<td>{p["rashi"]} {p["rashi_degree"]:.1f}&deg;</td>'
            f'<td>H{p["house"]}</td>'
            f'<td>{p["nakshatra"]}</td>'
            f'<td>P{p["nakshatra_pada"]}</td>'
            f'<td>{retro}</td></tr>\n'
        )
    return f"""## Your Birth Chart

<p style="text-align:center;color:#aaa;font-style:italic;margin:0 0 16pt 0;">
Born {data['birth']['datetime_human']}<br>
<b style="color:#c9a96e;">{data['lagna']['rashi']} Lagna</b> &middot;
<b style="color:#c0d4ed;">{data['moon']['rashi']} Moon</b> in
<b>{data['moon']['nakshatra']}</b> Pada {data['moon']['pada']}
</p>

<div style="text-align:center;margin:0 0 16pt 0;">
{svg}
</div>

<p class="caption-small">
North Indian (diamond) style. Lagna at top center. Houses count counter-clockwise.
Each planet shown in its classical navagraha color.
</p>

<table class="chart-table">
<thead><tr><th>Planet</th><th>Sign</th><th>House</th><th>Nakshatra</th><th>Pada</th><th></th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
"""


def section_reference_primer(data: dict[str, Any], narrative: str | None = None) -> str:
    """Page 3: compact navagrahas + houses primer.

    Quick reference so the symbols in the narrative make sense as the reader
    encounters them. Combines into one page — not two separate pages.
    """
    from packages.report.src.diagrams import (
        PLANET_COLORS,
        PLANET_DASHA_YEARS,
        PLANET_GLYPHS,
        PLANET_KARAKA,
        PLANET_SANSKRIT,
    )

    # Compact planet rows
    p_rows = ""
    for p in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]:
        color = PLANET_COLORS[p]
        p_rows += (
            f"<tr>"
            f'<td><b style="color:{color};">{PLANET_GLYPHS[p]}</b></td>'
            f'<td><i style="color:{color};">{PLANET_SANSKRIT[p]}</i></td>'
            f"<td>{p.title()}</td>"
            f"<td>{PLANET_KARAKA[p]}</td>"
            f'<td style="color:#888;">{PLANET_DASHA_YEARS[p]}y</td>'
            f"</tr>\n"
        )
    # Compact house rows
    h_data = [
        (1, "Tanu", "Self, body, vitality"),
        (2, "Dhana", "Wealth, family, speech"),
        (3, "Sahaja", "Siblings, courage, comms"),
        (4, "Sukha", "Mother, home, comfort"),
        (5, "Putra", "Children, creativity, dharma seed"),
        (6, "Shatru", "Enemies, illness, debts, service"),
        (7, "Yuvati", "Spouse, partnership, business"),
        (8, "Randhra", "Transformation, longevity, occult"),
        (9, "Dharma", "Father, dharma, fortune, guru"),
        (10, "Karma", "Career, status, public role"),
        (11, "Labha", "Gains, friends, aspirations"),
        (12, "Vyaya", "Losses, moksha, foreign"),
    ]
    h_rows = "".join(
        f"<tr><td><b>{h}</b></td><td><i>{sk}</i></td><td>{w}</td></tr>\n" for h, sk, w in h_data
    )
    return f"""## How to Read This Report

The next dozen pages reference Vedic terms — planets in their Sanskrit form, houses by number, dasha periods, yogas, doshas. Here's the legend.

### The Nine Planets (Navagrahas)

<table class="primer-table">
<thead><tr><th></th><th>Sanskrit</th><th>English</th><th>Governs</th><th></th></tr></thead>
<tbody>
{p_rows}
</tbody>
</table>

### The Twelve Houses (Bhavas)

<table class="primer-table">
<thead><tr><th>#</th><th>Sanskrit</th><th>Governs</th></tr></thead>
<tbody>
{h_rows}
</tbody>
</table>

<p class="caption-small">
<b style="color:#c9a96e;">Trikona (1,5,9)</b> — most auspicious trine houses &nbsp;
<b style="color:#d4b896;">Kendra (1,4,7,10)</b> — angular pillars &nbsp;
<b style="color:#22c55e;">Upachaya (3,6,10,11)</b> — houses of growth &nbsp;
<b style="color:#9d7bb8;">Dusthana (6,8,12)</b> — difficult houses
</p>

{_inline_concept_cards(data)}
"""


def _inline_concept_cards(data: dict[str, Any]) -> str:
    """Educational diagram cards that explain the concepts the report uses.

    These are 'school science book' figures that drop into the reference primer
    page so the customer learns *what* a dasha is, *what* a navamsha is, etc.,
    before they encounter those terms in the narrative.

    Chart-specific cards (Karakamsha, Mangal status, Kaal Sarp arc, sandhi
    planets) are added only when the chart actually carries them.
    """
    from packages.report.src.inline_diagrams import (
        dasha_nesting_card,
        dasha_vs_transit_card,
        house_lords_card,
        houses_card,
        kaal_sarp_card,
        karakamsha_card,
        karakas_card,
        mangal_dosha_card,
        nakshatra_rashi_card,
        navamsha_card,
        sandhi_card,
        vimshottari_wheel_card,
    )
    from packages.report.src.knowledge_gatherer import (
        _kaal_sarp_amrit_check,
        _karakamsha_reading,
        _mangal_dosha_check,
        _sandhi_planets,
    )

    cards: list[str] = []
    # Universal cards (always included — they teach the system).
    # Order matters: houses first (what's the chart), then dashas
    # (when does each part activate), then dasha-vs-transit (the most
    # confusing distinction in the report), then navamsha (the second-chart).
    # ─── EXPLAINERS first (universal — what the chart language means) ────
    cards.append(houses_card())  # What a house is — 12 bhava chakra
    cards.append(navamsha_card())  # What D9 is
    cards.append(dasha_vs_transit_card())  # Two-clock explainer
    cards.append(vimshottari_wheel_card(data))  # 120-year cycle wheel
    cards.append(dasha_nesting_card(data))  # Where you are right now in the nesting
    cards.append(nakshatra_rashi_card(data))  # The sky at birth — full sidereal map

    # ─── PERSONAL ARCHITECTURE after the explainers ──────────────────────
    cards.append(house_lords_card(data))  # YOUR 12-row architecture
    cards.append(karakas_card(data))  # YOUR Yogakaraka + Chara + Natural

    # Chart-specific cards (only when the chart carries them)
    try:
        kk = _karakamsha_reading(data)
        if kk and kk.get("atmakaraka"):
            cards.append(
                karakamsha_card(
                    kk["atmakaraka"],
                    kk["atmakaraka_degree_in_sign"],
                    kk["karakamsha_sign"],
                )
            )
    except Exception:
        pass

    try:
        ks = _kaal_sarp_amrit_check(data)
        if ks.get("active"):
            cards.append(
                kaal_sarp_card(
                    ks["rahu_sign_idx"],
                    ks["ketu_sign_idx"],
                    is_amrit=(ks["type"] == "kaal_amrit"),
                )
            )
    except Exception:
        pass

    try:
        m = _mangal_dosha_check(data)
        if m.get("active"):
            cards.append(
                mangal_dosha_card(
                    m["house_from_lagna"],
                    m["house_from_moon"],
                    m["is_cancelled"],
                    m["cancellation_factors"],
                    mars_house_from_venus=m.get("house_from_venus"),
                )
            )
    except Exception:
        pass

    try:
        # Show ONE sandhi-planet card if any planet is at a sign boundary
        sands = _sandhi_planets(data)
        if sands:
            # Extract first sandhi planet's data to render a sandhi bar
            natal = data.get("natal_planets_dict") or {}
            for p, pd in natal.items():
                if not isinstance(pd, dict):
                    continue
                deg = float(pd["longitude"]) % 30
                if deg < 1.0 or deg > 29.0:
                    sign_idx = int(float(pd["longitude"]) // 30)
                    from packages.report.src.diagrams import RASHI_NAMES

                    cards.append(sandhi_card(p, RASHI_NAMES[sign_idx], deg))
                    break
    except Exception:
        pass

    return "\n\n".join(cards)


def section_closing_cta(data: dict[str, Any], narrative: str | None = None) -> str:
    """Final actionable section — written by the stitcher agent.

    Distills the entire report into 3 most-important moves + 1 decisive date.
    """
    if narrative:
        return f"## Where To Go From Here\n\n{narrative}\n"
    # Fallback derives from existing data if stitcher didn't run
    cur = data["dasha"]["current"]
    return f"""## Where To Go From Here

You've just read the architecture, the past arc, the present chapter, the year ahead, your hidden strengths, your structural friction, and your next moves.

The chart is not destiny — it's *texture*. You decide what to do inside it.

One last frame: your current sub-period is **{cur['mahadasha']['lord'].title()} Mahadasha · {cur['antardasha']['lord'].title()} Antardasha**, running until {str(cur['antardasha']['end_date'])[:10]}. Whatever you choose to start, stop, or commit to in the coming weeks lands inside that window.

Read this report again in three months. The same words will mean different things.
"""


def _domain_section(title: str, narrative: str | None) -> str:
    if narrative:
        return f"## Add-on: {title}\n\n{narrative}\n"
    return f"## Add-on: {title}\n\n*(narrative pending)*\n"


def section_career_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    return _domain_section("Career & Money Deep-Dive", narrative)


def section_life_story_spine(data: dict[str, Any], narrative: str | None = None) -> str:
    """v12: The WHAT-WHEN-WHY predictive spine — the headline page of the report.

    This is what the customer most needs to see: the major life events the
    chart can predict, with specific date windows and chart-grounded WHY.
    Replaces/supplements the fragmented "lifetime", "next 5 years", etc.
    """
    _ = narrative
    try:
        from packages.report.src.inline_diagrams import life_story_spine_html

        return life_story_spine_html(data)
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Life Story Spine render failed: {e}")
        return ""


def section_d9_navamsha_chart(data: dict[str, Any], narrative: str | None = None) -> str:
    """The Navamsha (D9) chart page — sits inside the Relationships add-on as
    its visual companion. Customers asking about marriage need to see the D9.
    """
    _ = narrative
    try:
        from packages.report.src.diagrams import d9_chart_page_html

        return d9_chart_page_html(data)
    except Exception:
        return ""


def section_relationships_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    """Relationships deep-dive, with the D9 Navamsha chart page rendered first
    so customers see the marriage chart before reading the marriage prose."""
    d9_page = section_d9_navamsha_chart(data, None)
    body = _domain_section("Relationships & Marriage", narrative)
    if d9_page:
        return f"{d9_page}\n\n{body}"
    return body


def section_wealth_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    return _domain_section("Wealth & Money Architecture", narrative)


def section_health_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    return _domain_section("Health & Body", narrative)


def section_spiritual_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    return _domain_section("Spiritual Path & Dharma", narrative)


def section_sade_sati_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    # NOTE: Sade Sati is a CONDITIONAL BASE section (not an add-on). The
    # title here MUST NOT start with "Add-on:" — that would cause the
    # _mark_addon_sections post-processor in render.py to wrap it in the
    # purple ADD-ON badge, which would mislead the reader.
    if narrative:
        return f"## Sade Sati — The Saturn Audit\n\n{narrative}\n"
    return "## Sade Sati — The Saturn Audit\n\n*(narrative pending)*\n"


def section_children_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    return f"## Add-on: Children & Progeny\n\n{narrative or '*(narrative pending)*'}\n"


def section_education_deep_dive(data: dict[str, Any], narrative: str | None = None) -> str:
    return f"## Add-on: Education & Learning Path\n\n{narrative or '*(narrative pending)*'}\n"


def section_foreign_settlement(data: dict[str, Any], narrative: str | None = None) -> str:
    return f"## Add-on: Foreign Settlement & Travel\n\n{narrative or '*(narrative pending)*'}\n"


def section_property_vehicle(data: dict[str, Any], narrative: str | None = None) -> str:
    return f"## Add-on: Property & Vehicle Timing\n\n{narrative or '*(narrative pending)*'}\n"


def section_business_launch(data: dict[str, Any], narrative: str | None = None) -> str:
    return (
        f"## Add-on: Business Launch & Entrepreneurship\n\n{narrative or '*(narrative pending)*'}\n"
    )


def section_muhurta_calendar(data: dict[str, Any], narrative: str | None = None) -> str:
    return (
        f"## Add-on: Muhurta Calendar — Next 12 Months\n\n{narrative or '*(narrative pending)*'}\n"
    )


def section_gem_prescription(data: dict[str, Any], narrative: str | None = None) -> str:
    return f"## Add-on: Gemstone Prescription\n\n{narrative or '*(narrative pending)*'}\n"


def section_compatibility(data: dict[str, Any], narrative: str | None = None) -> str:
    return (
        f"## Add-on: Compatibility — Kundali Matching\n\n{narrative or '*(narrative pending)*'}\n"
    )


def section_past_5_years(data: dict[str, Any], narrative: str | None = None) -> str:
    if narrative:
        return f"## Add-on: Past 5 Years Decoded\n\n{narrative}\n"
    return "## Add-on: Past 5 Years Decoded\n\n*(narrative pending)*\n"


def section_next_5_years(data: dict[str, Any], narrative: str | None = None) -> str:
    if narrative:
        return f"## Add-on: Next 5 Years Map\n\n{narrative}\n"
    return "## Add-on: Next 5 Years Map\n\n*(narrative pending)*\n"


def section_lifetime(data: dict[str, Any], narrative: str | None = None) -> str:
    if narrative:
        return f"## Add-on: Lifetime Overview\n\n{narrative}\n"
    return "## Add-on: Lifetime Overview\n\n*(narrative pending)*\n"


def section_chart_vitals(data: dict[str, Any], narrative: str | None = None) -> str:
    """Appendix page: the technical numbers behind the reading.

    Pure data, no prose. For the analytically-inclined reader who wants to
    see the strengths, bindus, and karakas the agents drew from.
    """
    from packages.report.src.diagrams import (
        PLANET_COLORS,
        PLANET_GLYPHS,
        convergence_diagram_svg,
    )

    _natal = data.get("natal_planets_dict", {})
    convergence_html = convergence_diagram_svg(data)

    # Planet table — sign, house, dignity flag
    EXALTATION = {
        "sun": "Aries",
        "moon": "Taurus",
        "mars": "Capricorn",
        "mercury": "Virgo",
        "jupiter": "Cancer",
        "venus": "Pisces",
        "saturn": "Libra",
    }
    DEBILITATION = {
        "sun": "Libra",
        "moon": "Scorpio",
        "mars": "Cancer",
        "mercury": "Pisces",
        "jupiter": "Capricorn",
        "venus": "Virgo",
        "saturn": "Aries",
    }
    OWN_SIGNS = {
        "sun": ["Leo"],
        "moon": ["Cancer"],
        "mars": ["Aries", "Scorpio"],
        "mercury": ["Gemini", "Virgo"],
        "jupiter": ["Sagittarius", "Pisces"],
        "venus": ["Taurus", "Libra"],
        "saturn": ["Capricorn", "Aquarius"],
    }

    def _dignity(p: str, sign: str) -> str:
        if EXALTATION.get(p) == sign:
            return '<span style="color:#22c55e;">exalted</span>'
        if DEBILITATION.get(p) == sign:
            return '<span style="color:#dc2626;">debilitated</span>'
        if sign in OWN_SIGNS.get(p, []):
            return '<span style="color:#c9a96e;">own sign</span>'
        return '<span style="color:#888;">—</span>'

    planet_rows = ""
    for p in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]:
        info = data.get("natal_planets_dict", {}).get(p, {})
        lon = float(info.get("longitude", 0.0))
        signs = [
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
        sign = signs[int(lon // 30) % 12]
        deg = lon % 30
        house = info.get("house", "?")
        retro = " (R)" if info.get("is_retrograde") else ""
        color = PLANET_COLORS.get(p, "#fff")
        planet_rows += (
            f'<tr>'
            f'<td><b style="color:{color};">{PLANET_GLYPHS.get(p, "?")} {p.title()}</b></td>'
            f'<td>{sign} {deg:.1f}°{retro}</td>'
            f'<td>H{house}</td>'
            f'<td>{_dignity(p, sign)}</td>'
            f'</tr>\n'
        )

    return f"""## Chart Vitals — The Technical Layer

*For the analytical reader. The classical numbers that grounded every conclusion above.*

### Defining planets (convergence map)

{convergence_html}

### Planetary positions

<table class="chart-table">
<thead><tr><th>Planet</th><th>Sign</th><th>House</th><th>Dignity</th></tr></thead>
<tbody>
{planet_rows}
</tbody>
</table>

<p class="caption-small">
Dignity legend: <b style="color:#22c55e;">exalted</b> = the planet at its strongest; <b style="color:#c9a96e;">own sign</b> = runs clean and full-power; <b style="color:#dc2626;">debilitated</b> = the effect is undermined unless cancelled (Neecha Bhanga). Houses count from your Lagna (Ascendant).
</p>
"""


def section_sources_and_method(data: dict[str, Any], narrative: str | None = None) -> str:
    cusp_note = data["lagna"].get("reconciliation_note") or ""
    cusp_block = ""
    if cusp_note:
        # Render as raw HTML (not markdown-then-wrapped) so the .cusp-note
        # CSS class applies — markdown-it strips wrapping divs around inner
        # markdown when html:true.
        cusp_block = (
            '\n<div class="cusp-note">\n'
            '<p style="margin-top:0;font-weight:700;color:#fca5a5;letter-spacing:0.5px;font-size:9pt;">'
            "A NOTE ON YOUR LAGNA</p>\n"
            f"<p>{cusp_note}</p>\n"
            "<p>If your stated birth time is accurate to the minute, this report's lagna "
            "is correct. If your birth time is approximate (many records round to the "
            "nearest 5 or 10 minutes), the lagna could be the adjacent sign — and that "
            "would change house assignments throughout.</p>\n"
            '<p style="margin-bottom:0;">If anything in the reading does not ring true on '
            "second reading, consider rectifying your birth time through Prashna or "
            "major-event matching, then re-running the report.</p>\n"
            "</div>\n"
        )
    return f"""## Sources & Method
{cusp_block}
This report was generated using classical Vedic methods:

- **Brihat Parashara Hora Shastra** (BPHS) — house, dasha, and yoga interpretation
- **Jaimini sutras** — Chara Dasha, Chara Karakas, Argala
- **Vimshottari Dasha** — based on Moon's natal nakshatra (your Moon in {data['moon']['nakshatra']})
- **Lahiri ayanamsa** for sidereal calculations
- **108 calculation engine** (v{data['meta']['engine_version']}) — Swiss Ephemeris-backed precision

This is a guidance document, not a substitute for personal judgment. Astrology describes the *texture* of a moment; you decide what to do inside it.

---

*Generated {data['meta']['generated_at'][:10]} · 108 — Life's Operating System*
"""


# ── Section dispatch table ──

# Display title for each section id (used by the Table of Contents and by any
# future section-router that needs human-readable labels). Keep this in sync
# with each section's actual H2 heading. Section ids not in this map are
# rendered with their id title-cased.
SECTION_TITLES: dict[str, str] = {
    "table_of_contents": "Contents",
    "your_chart": "Your Birth Chart",
    "reference_primer": "How to Read This Report",
    "life_story_spine": "Your Life Story — What, When, Why",
    "who_you_are": "The Architecture",
    "what_already_happened": "What Already Happened",
    "arc_so_far": "Where You Came From",
    "where_you_are_now": "The Years You're In",
    "answering_your_question": "The Question You Asked",
    "next_12_months": "What's Coming",
    "structural_challenges": "The Friction You Inherited",
    "sade_sati_deep_dive": "Your Sade Sati Window",
    "hidden_strengths": "Hidden Strengths",
    "what_to_do_next": "What To Do Next",
    "closing_cta": "Your Move",
    "past_5_years": "The Past 5 Years",
    "next_5_years": "The Next 5 Years",
    "lifetime": "Your Lifetime Arc",
    "career_deep_dive": "Career & Money",
    "relationships_deep_dive": "Relationships & Marriage",
    "wealth_deep_dive": "Wealth Architecture",
    "health_deep_dive": "Health & Body",
    "spiritual_deep_dive": "Spiritual Path & Dharma",
    "children_deep_dive": "Children & Progeny",
    "education_deep_dive": "Education & Learning",
    "foreign_settlement": "Foreign & Settlement",
    "property_vehicle": "Property & Vehicle",
    "business_launch": "Business & Entrepreneurship",
    "muhurta_calendar": "Muhurta Calendar",
    "gem_prescription": "Gem Prescription",
    "compatibility": "Compatibility",
    "chart_vitals": "Chart Vitals (Appendix)",
    "sources_and_method": "Sources & Method",
}

# Sections that should appear in the TOC. Skip cover + TOC itself.
_TOC_SKIP_IDS: set[str] = {"opening", "table_of_contents"}


def section_table_of_contents(data: dict[str, Any], narrative: str | None = None) -> str:
    """Render the Table of Contents page.

    Groups sections into 4 visual columns: Your Chart, Your Story, Your
    Domains, Appendix. Within each group, lists active sections that will
    actually render for this chart (respecting conditional gates).
    """
    _ = narrative  # TOC is structural, not narrative-fed
    addons = data.get("addons", []) or []
    full_sections = sections_for_addons(addons)
    active = [
        sid
        for sid in full_sections
        if sid not in _TOC_SKIP_IDS and is_section_active_for_chart(sid, data)
    ]
    chart_block_ids = {"your_chart"}
    story_block_ids = {
        "who_you_are",
        "life_story_spine",
        "what_already_happened",
        "arc_so_far",
        "where_you_are_now",
        "answering_your_question",
        "next_12_months",
        "structural_challenges",
        "sade_sati_deep_dive",
        "hidden_strengths",
        "what_to_do_next",
        "closing_cta",
    }
    appendix_block_ids = {"reference_primer", "chart_vitals", "sources_and_method"}

    def _grouped() -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {
            "Your Chart": [],
            "Your Story": [],
            "Your Domains": [],
            "Appendix": [],
        }
        for sid in active:
            if sid in chart_block_ids:
                groups["Your Chart"].append(sid)
            elif sid in story_block_ids:
                groups["Your Story"].append(sid)
            elif sid in appendix_block_ids:
                groups["Appendix"].append(sid)
            else:
                groups["Your Domains"].append(sid)
        return groups

    groups = _grouped()
    rows_html = []
    for group_name, sids in groups.items():
        if not sids:
            continue
        items = "".join(
            f'<div class="toc-item">'
            f'<span class="toc-title">{SECTION_TITLES.get(sid, sid.replace("_", " ").title())}</span>'
            f'</div>'
            for sid in sids
        )
        rows_html.append(
            f'<div class="toc-group">'
            f'<div class="toc-group-label">{group_name}</div>'
            f"{items}"
            f"</div>"
        )
    groups_html = "\n".join(rows_html)
    # Note: emit the H2 *inside* the .toc-page wrapper so the page-break
    # CSS rule on the wrapper applies to the heading too. If the H2 were
    # outside, markdown-it would close the previous element first and the
    # H2 would render at the bottom of the prior page.
    return f"""<div class="toc-page">

<h2 class="toc-h2">Contents</h2>

<p class="toc-intro">A 108 Life Reading is built to be read in any order. Start where you are most curious. The cover hook frames the chart; the sections below open the architecture, the timing, and the domains.</p>

<div class="toc-grid">
{groups_html}
</div>

</div>
"""


SECTION_RENDERERS: dict[str, Callable[[dict[str, Any], str | None], str]] = {
    "opening": section_opening,
    "table_of_contents": section_table_of_contents,
    "your_chart": section_your_chart,
    "reference_primer": section_reference_primer,
    "life_story_spine": section_life_story_spine,
    "who_you_are": section_who_you_are,
    "what_already_happened": section_what_already_happened,
    "arc_so_far": section_arc_so_far,
    "closing_cta": section_closing_cta,
    "where_you_are_now": section_where_you_are_now,
    "answering_your_question": section_answering_your_question,
    "next_12_months": section_next_12_months,
    "hidden_strengths": section_hidden_strengths,
    "structural_challenges": section_structural_challenges,
    "what_to_do_next": section_what_to_do_next,
    "past_5_years": section_past_5_years,
    "next_5_years": section_next_5_years,
    "lifetime": section_lifetime,
    "career_deep_dive": section_career_deep_dive,
    "relationships_deep_dive": section_relationships_deep_dive,
    "wealth_deep_dive": section_wealth_deep_dive,
    "health_deep_dive": section_health_deep_dive,
    "spiritual_deep_dive": section_spiritual_deep_dive,
    "sade_sati_deep_dive": section_sade_sati_deep_dive,
    "children_deep_dive": section_children_deep_dive,
    "education_deep_dive": section_education_deep_dive,
    "foreign_settlement": section_foreign_settlement,
    "property_vehicle": section_property_vehicle,
    "business_launch": section_business_launch,
    "muhurta_calendar": section_muhurta_calendar,
    "gem_prescription": section_gem_prescription,
    "compatibility": section_compatibility,
    "chart_vitals": section_chart_vitals,
    "sources_and_method": section_sources_and_method,
}


# Mapping: addon slug → section id to insert before sources_and_method
ADDON_SECTION_MAP: dict[str, str] = {
    "past_5_years": "past_5_years",
    "next_5_years": "next_5_years",
    "lifetime": "lifetime",
    "career_deep_dive": "career_deep_dive",
    "relationships_deep_dive": "relationships_deep_dive",
    "wealth_deep_dive": "wealth_deep_dive",
    "health_deep_dive": "health_deep_dive",
    "spiritual_deep_dive": "spiritual_deep_dive",
    # NEW high-demand customer-vocabulary add-ons (Session 53)
    "children_deep_dive": "children_deep_dive",
    "education_deep_dive": "education_deep_dive",
    "foreign_settlement": "foreign_settlement",
    "property_vehicle": "property_vehicle",
    "business_launch": "business_launch",
    "muhurta_calendar": "muhurta_calendar",
    "gem_prescription": "gem_prescription",
    "compatibility": "compatibility",  # requires partner_birth in data; agent gates on this
    # NOTE: sade_sati_deep_dive is NOT here — it's a conditional BASE section.
    # Customers don't know if they have Sade Sati; the system auto-surfaces it.
}


def sections_for_addons(addons: list[str]) -> list[str]:
    """Return the full ordered section list including add-on sections.

    Final order: base (closing) → add-ons → Chart Vitals appendix → Sources & Method.
    Chart Vitals is the technical-data appendix, so it belongs AFTER all
    narrative sections (including add-ons), right before Sources & Method.
    """
    base = REPORT_SECTIONS[:-1]  # all except sources_and_method
    addon_sections = [ADDON_SECTION_MAP[a] for a in addons if a in ADDON_SECTION_MAP]
    # Back appendix: educational primer + technical vitals sit AFTER the
    # personal narrative and add-ons, before sources.
    return base + addon_sections + ["reference_primer", "chart_vitals", "sources_and_method"]


_MONTHS_LONG = {
    "January": "Jan",
    "February": "Feb",
    "March": "Mar",
    "April": "Apr",
    "May": "May",
    "June": "Jun",
    "July": "Jul",
    "August": "Aug",
    "September": "Sep",
    "October": "Oct",
    "November": "Nov",
    "December": "Dec",
}
_MONTHS_NUM = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}
_NUMBER_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
    "twenty-first": 21,
    "twenty-second": 22,
    "twenty-third": 23,
    "twenty-fourth": 24,
    "twenty-fifth": 25,
    "twenty-sixth": 26,
    "twenty-seventh": 27,
    "twenty-eighth": 28,
    "twenty-ninth": 29,
    "thirtieth": 30,
    "thirty-first": 31,
}


def _normalize_dates(text: str) -> str:
    """Force one date format ("Mon DD, YYYY") across the report.

    Agents independently chose between five formats — "Jun 2, 2026",
    "June 2, 2026", "2026-06-02", "the second of June 2026", "June 2nd, 2026".
    This rewrites all of them to the canonical "Mon DD, YYYY" form for visual
    consistency. Run on the FINAL stitched markdown, not per section.
    """
    import re

    # 1. ISO date "2026-06-02" / "1978-05-16" → "Jun 2, 2026"
    def _iso(m: re.Match) -> str:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        if mo not in _MONTHS_NUM:
            return m.group(0)
        return f"{_MONTHS_NUM[mo]} {int(d)}, {y}"

    text = re.sub(r"\b((?:19|20)\d{2})-(\d{2})-(\d{2})\b", _iso, text)

    # 2. Long month "June 2, 2026" → "Jun 2, 2026". Also handles "June 2nd, 2026"
    def _long_month(m: re.Match) -> str:
        mo = m.group(1)
        d = m.group(2)
        y = m.group(3)
        return f"{_MONTHS_LONG[mo]} {int(d)}, {y}"

    text = re.sub(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})\b",
        _long_month,
        text,
    )

    # 3. "the second of June 2026" / "the twenty-fifth of April 2030" →
    #    "Jun 2, 2026" / "Apr 25, 2030"
    nw_alt = "|".join(re.escape(k) for k in sorted(_NUMBER_WORDS.keys(), key=len, reverse=True))

    def _written(m: re.Match) -> str:
        nw = m.group(1).lower()
        mo = m.group(2)
        y = m.group(3)
        day = _NUMBER_WORDS.get(nw)
        if not day or mo not in _MONTHS_LONG:
            return m.group(0)
        return f"{_MONTHS_LONG[mo]} {day}, {y}"

    text = re.sub(
        rf"\bthe\s+({nw_alt})\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{{4}})\b",
        _written,
        text,
        flags=re.IGNORECASE,
    )

    # 4. UK-style "19 September 2025" → "Sep 19, 2025"
    def _uk(m: re.Match) -> str:
        d = m.group(1)
        mo = m.group(2)
        y = m.group(3)
        return f"{_MONTHS_LONG[mo]} {int(d)}, {y}"

    text = re.sub(
        r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
        _uk,
        text,
    )
    return text


def _clean_agent_narrative(text: str) -> str:
    """Post-generation cleaner applied to every agent narrative.

    Removes recurring v11 violations the agents kept slipping in:

    1. Raw state-vector decimal scores: "(7.3)", "Love at 5.8", "Money at 5.6"
    2. Trailing "(Sources: ...)" footer blocks
    3. Technical jargon leaked to prose: "Sudarshana 3/3", "Vimshopaka 45%",
       "BAV 0/56", "Shadbala 269 virupas"
    4. Compressed house notation in prose: "H10" → "10th house"
    """
    if not text:
        return text
    import re

    # 1a. Strip raw decimal scores like " (7.3)" but preserve "(7.3 ratti)".
    text = re.sub(r"\s*\((\d+\.\d+)\)", "", text)
    # 1b. Strip leaked area scores: "Love at 5.8", "Money at 5.6", "Health at 2.7"
    text = re.sub(
        r"\b(Love|Money|Health|Career|Spirit|Travel|Education|Family|Wealth)\s+at\s+\d+\.\d+\b",
        lambda m: m.group(1),
        text,
        flags=re.IGNORECASE,
    )

    # 2. Trailing "*(Sources: ...)*" italicized footer with parens.
    text = re.sub(
        r"\n+\s*\*?\(Sources?:[^)]+\)\*?\s*$",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # 2b. Trailing "Sources: ..." line without parens.
    text = re.sub(
        r"\n+\s*\*?Sources?:[^\n]+\*?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # 3. Technical-jargon leaks (internal metrics that should never reach the customer).
    # "Sudarshana 3/3" / "Sudarshana 2 of 3" → "all three chart angles confirm"/"two of three"
    text = re.sub(
        r"Sudarshana\s+(?:wheel\s+)?3\s*[/of]+\s*3",
        "all three chart-angles confirm",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Sudarshana\s+(?:wheel\s+)?2\s*[/of]+\s*3",
        "two of three chart-angles agree",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Sudarshana\s+(?:wheel\s+)?1\s*[/of]+\s*3",
        "one chart-angle hints",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"Sudarshana\s+(?:wheel\s+)?0\s*[/of]+\s*3",
        "no chart-angle backs this",
        text,
        flags=re.IGNORECASE,
    )
    # "Vimshopaka 45.8%" / "Vimshopaka at 45%" → "moderate" (etc.)
    text = re.sub(
        r"Vimshopaka\s+(?:at\s+|of\s+)?\d+(?:\.\d+)?\s*%?",
        "structural strength",
        text,
        flags=re.IGNORECASE,
    )
    # "BAV 0/56" / "BAV 29/56" → strip the score, keep "Ashtakavarga"
    text = re.sub(r"BAV\s+\d+\s*/\s*\d+", "Ashtakavarga support", text, flags=re.IGNORECASE)
    # "Shadbala 269 virupas" → "Shadbala"
    text = re.sub(
        r"Shadbala\s+(?:of\s+)?\d+(?:\.\d+)?\s*virupas?",
        "Shadbala",
        text,
        flags=re.IGNORECASE,
    )

    # 4. Compressed house notation H10 → 10th house (only when followed by space, not
    #    when inside a markdown table cell which uses standalone "H10").
    text = re.sub(
        r"\bH(\d{1,2})\b(?=[ ,.;:])",
        lambda m: f"{_ordinal(int(m.group(1)))} house",
        text,
    )

    return text.rstrip() + "\n"


def _ordinal(n: int) -> str:
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th")
    return f"{n}{suffix}"


def _strip_leading_h2(text: str) -> str:
    """Remove a leading H1 or H2 heading from agent-generated narrative.

    Agents are sometimes instructed to start their output with
    `## Add-on: <Title>` for routability. Others emit `# Title` directly.
    The section renderer ALSO prepends its own `## Add-on: <Title>`, so any
    leading heading from the agent becomes a duplicate.

    Worse: a leading `#` H1 triggers the cover-page "108" ::before decoration
    on a non-cover page, producing a giant duplicate header mid-document.

    Strip a single leading `#` or `##` heading line + the blank line after.
    """
    if not text:
        return text
    lines = text.split("\n", 2)
    if not lines:
        return text
    head = lines[0].lstrip()
    # Accept either `# ...` (H1) or `## ...` (H2) as the leading heading.
    if not (head.startswith("# ") or head.startswith("## ")):
        return text
    rest = lines[1:]
    if rest and rest[0].strip() == "" and len(rest) > 1:
        return rest[1]
    return "\n".join(rest)


def _convergence_html(quote: str) -> str:
    """Unused; placeholder for future convergence inline visuals."""
    return ""


def _pull_quote_html(quote: str) -> str:
    """HTML for a section pull-quote (large, distinct, design-led)."""
    return (
        '<div class="pull-quote">'
        f'<span class="pull-quote-mark">&ldquo;</span>'
        f"{quote}"
        "</div>"
    )


def render_markdown(
    data: dict[str, Any],
    narratives: dict[str, str] | None = None,
    sections: list[str] | None = None,
    pull_quotes: dict[str, str] | None = None,
) -> str:
    """Render the full report as a single Markdown string.

    Args:
        data: Output of collect_chart_data().
        narratives: Optional {section_id: ai_generated_narrative_text}.
            When omitted, sections render structural data only with
            narrative-placeholder notes.
        sections: Override of sections to include. If omitted, uses base
            REPORT_SECTIONS plus any addons in data["addons"].
        pull_quotes: Optional {section_id: pull_quote_text} from the stitcher.
            When provided, each section's pull-quote is injected after the
            section's H2/dek and before the section body.
    """
    narratives = narratives or {}
    pull_quotes = pull_quotes or {}
    if sections is None:
        addons = data.get("addons", []) or []
        sections = sections_for_addons(addons)
    parts: list[str] = []
    for sid in sections:
        renderer = SECTION_RENDERERS.get(sid)
        if not renderer:
            continue
        # Conditional gate — auto-skip sections that don't apply to this chart
        if not is_section_active_for_chart(sid, data):
            continue
        # Strip leading H2 from agent narrative if it duplicates the section title.
        # Skip for opening (cover hook is plain prose, not an H2-wrapped narrative)
        # and closing_cta (also pure prose).
        narr = narratives.get(sid)
        if narr and sid not in {"opening", "closing_cta"}:
            narr = _strip_leading_h2(narr)
            narr = _clean_agent_narrative(narr)
        body = renderer(data, narr)
        quote = pull_quotes.get(sid)
        if quote and sid not in {
            "opening",
            "your_chart",
            "reference_primer",
            "sources_and_method",
            "closing_cta",
            "chart_vitals",
        }:
            # Inject after the first blank line that follows the H2 + dek
            # The dek is the line immediately after H2 in italics; pull-quote
            # belongs right after that, before the body.
            lines = body.split("\n", 1)
            if len(lines) == 2:
                head, rest = lines
                # Find the second blank-line boundary so we land after H2+dek
                segs = rest.split("\n\n", 2)
                if len(segs) >= 2:
                    # segs[0] = dek line (italic), segs[1+] = body
                    rest_after = "\n\n".join(segs[1:])
                    body = f"{head}\n{segs[0]}\n\n{_pull_quote_html(quote)}\n\n{rest_after}"
                else:
                    body = f"{head}\n\n{_pull_quote_html(quote)}\n\n{rest}"
        parts.append(body)
    # Apply final-pass date format normalization across the whole document.
    # Cleaner ran per-section above (jargon, scores); this one runs once at the
    # end because date forms cross section boundaries (stitcher + cover hook).
    final = "\n\n---\n\n".join(parts)
    final = _normalize_dates(final)
    return final
