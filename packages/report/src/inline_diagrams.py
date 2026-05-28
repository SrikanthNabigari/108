"""Inline "school science book" educational diagrams for the 108 report.

These render as small in-flow HTML/SVG widgets that explain a single Vedic
concept visually — sized to sit naturally in the middle of a page, like
science-textbook figures with a caption underneath.

Every diagram function returns an HTML string that the markdown pipeline
can drop into any section's body.

Naming convention: `concept_<name>_diagram(...)` for the diagram itself,
`<name>_card(...)` for full card with title + diagram + caption.
"""

from __future__ import annotations

from typing import Any

from packages.report.src.diagrams import (
    PLANET_COLORS,
    PLANET_SYMBOLS,
    RASHI_NAMES,
    RASHI_SHORT,
)

# ──────────────────────────────────────────────────────────────────────
# Card wrapper — every diagram sits inside this with title + caption
# ──────────────────────────────────────────────────────────────────────


def _diagram_card(title: str, svg_or_html: str, caption: str = "") -> str:
    """Standard 'science book figure' wrapper: title, diagram, caption."""
    cap = f'<div class="diagram-card-caption">{caption}</div>' if caption else ""
    return f"""<div class="diagram-card">
<div class="diagram-card-title">{title}</div>
<div class="diagram-card-body">{svg_or_html}</div>
{cap}
</div>"""


# ──────────────────────────────────────────────────────────────────────
# 1. THE 12 HOUSES — circular zodiac with house meanings
# ──────────────────────────────────────────────────────────────────────

HOUSE_MEANINGS = [
    "self · body · identity",
    "wealth · family · speech",
    "courage · siblings · effort",
    "home · mother · vehicles",
    "creativity · children · romance",
    "enemies · debt · service",
    "spouse · partnership · business",
    "transformation · mystery",
    "dharma · father · fortune",
    "career · status · public role",
    "gains · friends · network",
    "loss · foreign · moksha",
]
HOUSE_KENDRA = {1, 4, 7, 10}
HOUSE_TRIKONA = {1, 5, 9}
HOUSE_DUSTHANA = {6, 8, 12}


def houses_explainer_diagram() -> str:
    """Circular bhava chakra — all 12 houses with their meanings color-coded."""
    import math

    cx, cy, r_outer, r_inner = 200, 200, 175, 60
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" '
        'width="320" height="320" style="display:block;margin:0 auto;">',
    ]
    for h in range(1, 13):
        # Each house is a 30° wedge. House 1 starts at top (north), wedges go clockwise.
        start_deg = -90 + (h - 1) * 30
        end_deg = start_deg + 30
        a1 = math.radians(start_deg)
        a2 = math.radians(end_deg)
        x1, y1 = cx + r_outer * math.cos(a1), cy + r_outer * math.sin(a1)
        x2, y2 = cx + r_outer * math.cos(a2), cy + r_outer * math.sin(a2)
        # Determine wedge color
        if h in HOUSE_DUSTHANA:
            fill = "rgba(200, 74, 62, 0.16)"  # red — dusthana
            stroke = "#c84a3e"
        elif h in HOUSE_KENDRA & HOUSE_TRIKONA:
            fill = "rgba(212, 168, 67, 0.22)"  # gold — kendra+trikona (best)
            stroke = "#d4a843"
        elif h in HOUSE_KENDRA:
            fill = "rgba(212, 168, 67, 0.14)"
            stroke = "#d4a843"
        elif h in HOUSE_TRIKONA:
            fill = "rgba(61, 139, 110, 0.16)"  # green — trikona
            stroke = "#3d8b6e"
        else:
            fill = "rgba(255, 255, 255, 0.05)"
            stroke = "#666"
        path = f"M {cx} {cy} L {x1} {y1} A {r_outer} {r_outer} 0 0 1 {x2} {y2} Z"
        parts.append(f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>')
        # House number — between inner and outer radius
        mid = math.radians(start_deg + 15)
        nx, ny = cx + (r_inner + 60) * math.cos(mid), cy + (r_inner + 60) * math.sin(mid)
        parts.append(
            f'<text x="{nx}" y="{ny+5}" text-anchor="middle" '
            f'font-family="Cormorant Garamond,serif" font-size="20" '
            f'font-weight="500" fill="#c9a96e">{h}</text>'
        )
    # Inner circle white-out
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner-2}" '
        f'fill="#0e0e10" stroke="#c9a96e" stroke-width="0.5"/>'
    )
    # Center label
    parts.append(
        f'<text x="{cx}" y="{cy-5}" text-anchor="middle" '
        f'font-family="Cormorant Garamond,serif" font-size="13" '
        f'fill="#aaa" font-style="italic">12 Bhavas</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy+10}" text-anchor="middle" '
        f'font-family="Inter,sans-serif" font-size="8" '
        f'fill="#888" letter-spacing="2px">HOUSES</text>'
    )
    parts.append("</svg>")
    legend = (
        '<div class="diagram-legend">'
        '<span class="legend-chip" style="background:rgba(212,168,67,0.22);border:1px solid #d4a843;">kendra+trikona</span> '
        '<span class="legend-chip" style="background:rgba(212,168,67,0.14);border:1px solid #d4a843;">kendra (angle)</span> '
        '<span class="legend-chip" style="background:rgba(61,139,110,0.16);border:1px solid #3d8b6e;">trikona (trine)</span> '
        '<span class="legend-chip" style="background:rgba(200,74,62,0.16);border:1px solid #c84a3e;">dusthana (difficult)</span>'
        "</div>"
    )
    return "\n".join(parts) + legend


def houses_card() -> str:
    return _diagram_card(
        "The 12 Houses (Bhavas)",
        houses_explainer_diagram(),
        "Each house is a life-domain. Kendras (1/4/7/10) are pillars of action; "
        "trikonas (1/5/9) are pillars of fortune; dusthanas (6/8/12) are the "
        "houses of friction — debt, transformation, and loss. Houses 1, 5, and "
        "9 (the trinity of dharma) are the strongest in any chart.",
    )


# ──────────────────────────────────────────────────────────────────────
# 2. SANDHI / GANDANTA bar — sign boundary zones
# ──────────────────────────────────────────────────────────────────────


def sandhi_bar_diagram(planet: str, sign: str, degree_in_sign: float) -> str:
    """Horizontal 0-30° bar showing where in the sign a planet sits.

    Sandhi (junction) zones at 0-1° and 29-30° are highlighted as weak.
    The 'sweet spot' (3-25°) is shown clean.
    """
    color = PLANET_COLORS.get(planet.lower(), "#f1ede5")
    symbol = PLANET_SYMBOLS.get(planet.lower(), planet[:2].title())
    # 320px wide bar = 30 degrees
    px_per_deg = 10.5
    planet_x = max(2, min(316, degree_in_sign * px_per_deg))
    in_sandhi_start = degree_in_sign < 1.0
    in_sandhi_end = degree_in_sign > 29.0
    label_color = "#c84a3e" if (in_sandhi_start or in_sandhi_end) else color
    sandhi_note = " — in sandhi (sign-cusp, weak)" if (in_sandhi_start or in_sandhi_end) else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 56"
width="320" height="50" style="display:block;margin:8pt auto;">
<rect x="0" y="22" width="360" height="14" fill="#1a1a1a" stroke="#444" stroke-width="0.5"/>
<rect x="0" y="22" width="{1*px_per_deg}" height="14" fill="rgba(200,74,62,0.35)"/>
<rect x="{29*px_per_deg}" y="22" width="{1*px_per_deg}" height="14" fill="rgba(200,74,62,0.35)"/>
<line x1="{planet_x}" y1="14" x2="{planet_x}" y2="44" stroke="{label_color}" stroke-width="2"/>
<text x="{planet_x}" y="11" text-anchor="middle"
  font-family="DejaVu Sans, Inter, sans-serif" font-size="14" fill="{label_color}">{symbol}</text>
<text x="2" y="52" font-family="Inter,sans-serif" font-size="7" fill="#888">0°</text>
<text x="160" y="52" text-anchor="middle" font-family="Inter,sans-serif" font-size="7" fill="#888">15°</text>
<text x="358" y="52" text-anchor="end" font-family="Inter,sans-serif" font-size="7" fill="#888">30°</text>
<text x="180" y="20" text-anchor="middle" font-family="Cormorant Garamond,serif"
  font-style="italic" font-size="9" fill="#aaa">{sign} — 30° of the sign{sandhi_note}</text>
</svg>"""


def sandhi_card(planet: str, sign: str, degree_in_sign: float) -> str:
    title = f"Where {planet.title()} Sits in {sign}"
    caption = (
        f"{planet.title()} at {degree_in_sign:.2f}° in {sign}. "
        "The red zones at 0-1° and 29-30° are sandhi — sign-junctions where a "
        "planet hasn't fully settled into its dispositor's house. Planets there "
        "deliver diluted effects. The middle of the sign (3-25°) is where a "
        "planet has its full voice."
    )
    return _diagram_card(title, sandhi_bar_diagram(planet, sign, degree_in_sign), caption)


# ──────────────────────────────────────────────────────────────────────
# 3. NAVAMSHA (D9) calculation diagram — 30° → 9 navamshas
# ──────────────────────────────────────────────────────────────────────


def navamsha_strip_diagram() -> str:
    """Strip showing how 30° of a sign divides into 9 × 3.333° navamshas."""
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 80"',
        ' width="340" height="76" style="display:block;margin:6pt auto;">',
    ]
    # 9 navamsha cells
    cell_w = 360 / 9
    nav_colors = ["#1a1a1a", "#222"]
    nav_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for i in range(9):
        x = i * cell_w
        parts.append(
            f'<rect x="{x}" y="20" width="{cell_w}" height="32" '
            f'fill="{nav_colors[i%2]}" stroke="#c9a96e" stroke-width="0.3"/>'
        )
        parts.append(
            f'<text x="{x + cell_w/2}" y="42" text-anchor="middle" '
            f'font-family="Cormorant Garamond,serif" font-size="14" '
            f'fill="#c9a96e">{nav_labels[i]}</text>'
        )
        parts.append(
            f'<text x="{x + cell_w/2}" y="64" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="6.5" '
            f'fill="#888">{i*3.33:.1f}°-{(i+1)*3.33:.1f}°</text>'
        )
    parts.append(
        '<text x="180" y="14" text-anchor="middle" '
        'font-family="Cormorant Garamond,serif" font-style="italic" '
        'font-size="10" fill="#aaa">One sign (30°) → 9 navamsha cells (3°20\' each)</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def navamsha_card() -> str:
    return _diagram_card(
        "How Navamsha (D9) Works",
        navamsha_strip_diagram(),
        "Every sign is divided into 9 equal parts (3°20' each), called navamshas. "
        "The 'navamsha sign' of a planet is its soul-level placement — read for "
        "marriage, dharma, and the inner strength of every planet. A planet "
        "weak in the birth chart but strong in D9 is said to have a second chance.",
    )


# ──────────────────────────────────────────────────────────────────────
# 4. DASHA NESTING — the multi-year → multi-month → weeks pyramid
# ──────────────────────────────────────────────────────────────────────


def dasha_nesting_diagram(chart_data: dict[str, Any] | None = None) -> str:
    """Personalized dasha progress diagram — three nested timebars showing
    THIS CUSTOMER's actual Mahadasha, Antardasha, and Pratyantar, with a
    "you are here" marker on each one and exact dates.

    The progressive zoom-in shows the nesting metaphor in their lived time.
    Falls back to a generic illustration if chart_data is missing.
    """
    if not chart_data:
        return _dasha_nesting_generic()
    try:
        from datetime import datetime

        cur = chart_data["dasha"]["current"]
        md, ad, pd = cur["mahadasha"], cur["antardasha"], cur["pratyantardasha"]

        def _strip_tz(dt):
            if hasattr(dt, "tzinfo") and dt.tzinfo:
                return dt.replace(tzinfo=None)
            if isinstance(dt, str):
                d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                if d.tzinfo:
                    d = d.replace(tzinfo=None)
                return d
            return dt

        def _progress(level: dict) -> tuple[float, str, str]:
            start = _strip_tz(level["start_date"])
            end = _strip_tz(level["end_date"])
            try:
                now = _strip_tz(
                    datetime.fromisoformat(
                        chart_data["meta"]["generated_at"].replace("Z", "+00:00")
                    )
                )
            except Exception:
                now = datetime.now()
            total = (end - start).total_seconds()
            elapsed = max(0, min(total, (now - start).total_seconds()))
            pct = (elapsed / total) * 100 if total > 0 else 0
            return pct, start.strftime("%b %Y"), end.strftime("%b %Y")

        def _bar(level: dict, label: str, sublabel: str, bg_color: str) -> str:
            pct, start_str, end_str = _progress(level)
            pct_clamped = max(2, min(98, pct))
            lord = level["lord"].title()
            return f"""<div style="margin:6pt 0;">
  <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;letter-spacing:1.5pt;margin-bottom:3pt;">
    {label} &middot; <span style="color:{bg_color};font-weight:600;">{lord}</span> &middot; {sublabel}
  </div>
  <div style="position:relative;background:#1a1a1a;border:0.5pt solid #444;border-radius:2px;height:18pt;overflow:hidden;">
    <div style="position:absolute;top:0;left:0;height:100%;width:{pct_clamped}%;background:{bg_color};opacity:0.85;"></div>
    <div style="position:absolute;top:0;left:{pct_clamped}%;height:100%;width:1pt;background:#fff;"></div>
    <div style="position:absolute;top:3pt;left:6pt;font-family:Inter,sans-serif;font-size:7.5pt;color:#0e0e10;font-weight:600;">{start_str}</div>
    <div style="position:absolute;top:3pt;right:6pt;font-family:Inter,sans-serif;font-size:7.5pt;color:#aaa;">{end_str}</div>
  </div>
</div>"""

        md_bar = _bar(
            md,
            "MAHADASHA · the chapter (years)",
            f"{md.get('years', '?')}y total",
            PLANET_COLORS.get(md["lord"], "#c9a96e"),
        )
        ad_bar = _bar(
            ad,
            "ANTARDASHA · the section (months)",
            "zoom in",
            PLANET_COLORS.get(ad["lord"], "#c9a96e"),
        )
        pd_bar = _bar(
            pd,
            "PRATYANTAR · the paragraph (weeks)",
            "zoom in further",
            PLANET_COLORS.get(pd["lord"], "#c9a96e"),
        )

        return f"""<div style="margin:6pt auto;max-width:340pt;">
{md_bar}
<div style="text-align:center;color:#666;font-size:11pt;margin:-2pt 0;">↓</div>
{ad_bar}
<div style="text-align:center;color:#666;font-size:11pt;margin:-2pt 0;">↓</div>
{pd_bar}
<div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:9pt;
            color:#aaa;text-align:center;margin-top:10pt;line-height:1.5;">
  Each bar is a slice of the parent. The white line is where you are right now.
</div>
</div>"""
    except Exception:
        return _dasha_nesting_generic()


def _dasha_nesting_generic() -> str:
    """Fallback if no chart data — generic illustration."""
    return """<div style="margin:6pt auto;max-width:340pt;">
  <div style="width:100%;background:#d4a843;color:#0e0e10;padding:7pt;text-align:center;
              font-family:Inter,sans-serif;font-size:10pt;font-weight:700;letter-spacing:1pt;
              border-radius:2px;margin-bottom:4pt;">MAHADASHA &middot; 6-20 years</div>
  <div style="width:55%;margin-left:25%;background:#3d8b6e;color:#fff;padding:7pt;text-align:center;
              font-family:Inter,sans-serif;font-size:9pt;font-weight:700;letter-spacing:1pt;
              border-radius:2px;margin-bottom:4pt;">ANTARDASHA &middot; months</div>
  <div style="width:25%;margin-left:38%;background:#c9a5a5;color:#0e0e10;padding:7pt;text-align:center;
              font-family:Inter,sans-serif;font-size:9pt;font-weight:700;letter-spacing:1pt;
              border-radius:2px;">PRATYANTAR &middot; weeks</div>
</div>"""


def _strip_tz_local(dt):
    """Local strip-tz used by the Vimshottari wheel."""
    from datetime import datetime

    if isinstance(dt, str):
        d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return d.replace(tzinfo=None) if d.tzinfo else d
    if hasattr(dt, "tzinfo") and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt


def vimshottari_wheel_svg(chart_data: dict[str, Any]) -> str:
    """Editorial Vimshottari wheel — 120-year cycle as 5 nested rings.

    Faithful to Reference 1. Architecture:
      • Outer ring (MD) → ring 2 (AD) → ring 3 (PD) → ring 4 (SD) → ring 5 (PrD)
      • Every wedge in every ring subdivides into its 9 children (full sunburst)
      • Pure monochrome grayscale — alternating ring shades; NO color highlights
      • Wheel does NOT rotate; sits in fixed cosmological order starting from
        Ketu at top (12 o'clock = angle 0)
      • A thin vertical white NOW line drops from above the wheel through the
        outer edge to the center dot, falling at whatever angle NOW occupies
        (not snapped to top)
      • A small white tab protrudes above the outer ring where the NOW line
        crosses — marks the customer's exact current position
      • Labels ONLY on the radial slice that NOW passes through — MD/AD/PD/SD
        codes appear inside the appropriate ring along the NOW axis
    """
    import math
    from datetime import datetime

    _strip_tz = _strip_tz_local  # noqa: alias for in-function brevity
    cur = chart_data["dasha"]["current"]
    md_seq = chart_data["dasha"].get("mahadasha_sequence", [])
    birth_dt = datetime.fromisoformat(chart_data["birth"]["datetime"].replace("Z", "+00:00"))
    if birth_dt.tzinfo:
        birth_dt = birth_dt.replace(tzinfo=None)
    now = datetime.now()

    # Vimshottari sequence — fixed cosmological order
    SEQ = [
        ("ketu", 7),
        ("venus", 20),
        ("sun", 6),
        ("moon", 10),
        ("mars", 7),
        ("rahu", 18),
        ("jupiter", 16),
        ("saturn", 19),
        ("mercury", 17),
    ]
    SEQ_DICT = dict(SEQ)
    deg_per_year = 3.0  # 360° / 120y

    # ─── Compute NOW's absolute angle in the wheel (0-360) ───
    birth_md = md_seq[0] if md_seq else None
    if not birth_md:
        return '<div style="color:#888;font-size:9pt;text-align:center;">Vimshottari wheel unavailable.</div>'
    birth_md_lord = birth_md.get("lord")
    birth_md_end = _strip_tz(birth_md.get("end") or birth_md.get("end_date"))
    full_md_years = SEQ_DICT.get(birth_md_lord, 7)
    years_used_at_birth = full_md_years - ((birth_md_end - birth_dt).days / 365.25)
    seq_idx = next((i for i, (l, _) in enumerate(SEQ) if l == birth_md_lord), 0)
    seq_start_deg = sum(y for _, y in SEQ[:seq_idx]) * deg_per_year
    birth_angle = seq_start_deg + years_used_at_birth * deg_per_year
    elapsed_years = (now - birth_dt).days / 365.25
    now_angle = (birth_angle + elapsed_years * deg_per_year) % 360

    # ─── Layout constants ───
    cx, cy = 200, 200
    R_MD_OUT = 178
    R_MD_IN = 144  # MD ring (outer)
    R_AD_IN = 116  # AD ring
    R_PD_IN = 90  # PD ring
    R_SD_IN = 66  # SD ring
    R_PR_IN = 44  # Prana ring
    R_CORE = 28  # core disc

    # Pure monochrome — alternating ring shades for visible separation
    BG = "#0e0e12"
    RING_A = "#3a3a42"  # outer MD (lightest)
    RING_B = "#4d4d56"  # AD (light)
    RING_C = "#363640"  # PD (mid)
    RING_D = "#4a4a54"  # SD (light)
    RING_E = "#34343e"  # Prana (mid)
    STROKE = "#0a0a0e"  # nearly-black separator

    current_md_lord = cur["mahadasha"]["lord"]
    current_ad_lord = cur["antardasha"]["lord"]
    current_pd_lord = cur["pratyantardasha"]["lord"]
    current_sd_lord = (
        (cur.get("sookshma") or {}).get("lord")
        or (cur.get("sukshma") or {}).get("lord")
        or current_pd_lord
    )
    current_pr_lord = (cur.get("prana") or {}).get("lord") or current_sd_lord

    # Rotate so current MD's mid-point sits at top (12 o'clock).
    # The reference customer's current MD wedge sits at the very top — that's
    # what gives the NOW radial its iconic vertical line.
    current_md_seq_idx = next(
        (i for i, (l, _) in enumerate(SEQ) if l == cur["mahadasha"]["lord"]), 0
    )
    current_md_start_deg = sum(y for _, y in SEQ[:current_md_seq_idx]) * deg_per_year
    current_md_yrs = SEQ_DICT.get(cur["mahadasha"]["lord"], 7)
    current_md_mid_deg = current_md_start_deg + (current_md_yrs * deg_per_year) / 2
    wheel_rotation = -current_md_mid_deg  # rotate this many degrees so MD mid → top

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"',
        ' width="380" height="380" style="display:block;margin:4pt auto;">',
        f'<circle cx="{cx}" cy="{cy}" r="{R_MD_OUT + 4}" fill="{BG}" stroke="#2a2a2f" stroke-width="0.4"/>',
        f'<g transform="rotate({wheel_rotation} {cx} {cy})">',
    ]

    def _wedge(
        r_out: float,
        r_in: float,
        a_start: float,
        a_end: float,
        fill: str,
        stroke: str = STROKE,
        sw: float = 0.3,
    ) -> str:
        a1 = math.radians(a_start - 90)
        a2 = math.radians(a_end - 90)
        x1, y1 = cx + r_out * math.cos(a1), cy + r_out * math.sin(a1)
        x2, y2 = cx + r_out * math.cos(a2), cy + r_out * math.sin(a2)
        x3, y3 = cx + r_in * math.cos(a2), cy + r_in * math.sin(a2)
        x4, y4 = cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)
        large = 1 if (a_end - a_start) > 180 else 0
        return (
            f'<path d="M {x1:.2f} {y1:.2f} A {r_out} {r_out} 0 {large} 1 {x2:.2f} {y2:.2f} '
            f'L {x3:.2f} {y3:.2f} A {r_in} {r_in} 0 {large} 0 {x4:.2f} {y4:.2f} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    # ─── Build full sunburst: every wedge in every ring subdivides ───
    # We track which wedge at each level contains NOW (for label placement)
    now_path: dict[int, tuple[float, float, str]] = {}  # level → (a_start, a_end, lord)

    angle = 0.0
    for md_lord, md_yrs in SEQ:
        md_w = md_yrs * deg_per_year
        parts.append(_wedge(R_MD_OUT, R_MD_IN, angle, angle + md_w, RING_A, sw=0.5))
        if angle <= now_angle < angle + md_w:
            now_path[0] = (angle, angle + md_w, md_lord)
        # AD ring
        md_seq_idx = next(i for i, (l, _) in enumerate(SEQ) if l == md_lord)
        ad_order = [SEQ[(md_seq_idx + i) % 9] for i in range(9)]
        a = angle
        for ad_lord, ad_full_yrs in ad_order:
            ad_yrs = (ad_full_yrs * md_yrs) / 120
            ad_w = ad_yrs * deg_per_year
            parts.append(_wedge(R_MD_IN, R_AD_IN, a, a + ad_w, RING_B, sw=0.25))
            if a <= now_angle < a + ad_w:
                now_path[1] = (a, a + ad_w, ad_lord)
            # PD ring
            ad_seq_idx = next(i for i, (l, _) in enumerate(SEQ) if l == ad_lord)
            pd_order = [SEQ[(ad_seq_idx + i) % 9] for i in range(9)]
            p = a
            for pd_lord, pd_full_yrs in pd_order:
                pd_yrs = (pd_full_yrs * ad_yrs) / 120
                pd_w = pd_yrs * deg_per_year
                parts.append(_wedge(R_AD_IN, R_PD_IN, p, p + pd_w, RING_C, sw=0.18))
                if p <= now_angle < p + pd_w:
                    now_path[2] = (p, p + pd_w, pd_lord)
                # SD ring — full sunburst across whole wheel
                pd_seq_idx = next(i for i, (l, _) in enumerate(SEQ) if l == pd_lord)
                sd_order = [SEQ[(pd_seq_idx + i) % 9] for i in range(9)]
                s = p
                for sd_lord, sd_full_yrs in sd_order:
                    sd_yrs = (sd_full_yrs * pd_yrs) / 120
                    sd_w = sd_yrs * deg_per_year
                    parts.append(_wedge(R_PD_IN, R_SD_IN, s, s + sd_w, RING_D, sw=0.08))
                    if s <= now_angle < s + sd_w:
                        now_path[3] = (s, s + sd_w, sd_lord)
                        # only compute Prana label for the wedge containing NOW
                        sd_seq_idx = next(i for i, (l, _) in enumerate(SEQ) if l == sd_lord)
                        pr_order = [SEQ[(sd_seq_idx + i) % 9] for i in range(9)]
                        pr = s
                        for pr_lord, pr_full_yrs in pr_order:
                            pr_yrs = (pr_full_yrs * sd_yrs) / 120
                            pr_w = pr_yrs * deg_per_year
                            if pr <= now_angle < pr + pr_w:
                                now_path[4] = (pr, pr + pr_w, pr_lord)
                                break
                            pr += pr_w
                    s += sd_w
                p += pd_w
            a += ad_w
        angle += md_w

    parts.append("</g>")  # close rotation group

    # Prana ring as a single annular band (rendered AFTER rotation close so it
    # appears as a clean horizontal band; subdivisions skipped — 59K wedges
    # bloated the file to 1.3 MB without adding visual signal)
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{(R_SD_IN + R_PR_IN) / 2}" '
        f'fill="none" stroke="{RING_E}" stroke-width="{R_SD_IN - R_PR_IN}"/>'
    )
    # core disc
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{R_CORE}" fill="{BG}" stroke="{STROKE}" stroke-width="0.4"/>'
    )

    # ─── NOW radial: post-rotation, NOW lives at screen angle (now_angle + wheel_rotation) ───
    # Since wheel_rotation = -current_md_mid_deg, and now_angle sits inside the
    # current MD, the post-rotation NOW angle is small (close to 0 = top).
    screen_now_deg = (now_angle + wheel_rotation) % 360
    now_rad = math.radians(screen_now_deg - 90)
    nx_out = cx + (R_MD_OUT + 8) * math.cos(now_rad)
    ny_out = cy + (R_MD_OUT + 8) * math.sin(now_rad)
    nx_core = cx + R_CORE * math.cos(now_rad)
    ny_core = cy + R_CORE * math.sin(now_rad)
    parts.append(
        f'<line x1="{nx_out:.2f}" y1="{ny_out:.2f}" x2="{nx_core:.2f}" y2="{ny_core:.2f}" '
        f'stroke="#ffffff" stroke-width="0.9" opacity="0.95"/>'
    )
    # small tab/peak at the outer end
    tab_a1 = math.radians(now_angle - 90 - 1.5)
    tab_a2 = math.radians(now_angle - 90 + 1.5)
    tx_in1 = cx + R_MD_OUT * math.cos(tab_a1)
    ty_in1 = cy + R_MD_OUT * math.sin(tab_a1)
    tx_in2 = cx + R_MD_OUT * math.cos(tab_a2)
    ty_in2 = cy + R_MD_OUT * math.sin(tab_a2)
    tx_out1 = cx + (R_MD_OUT + 7) * math.cos(tab_a1)
    ty_out1 = cy + (R_MD_OUT + 7) * math.sin(tab_a1)
    tx_out2 = cx + (R_MD_OUT + 7) * math.cos(tab_a2)
    ty_out2 = cy + (R_MD_OUT + 7) * math.sin(tab_a2)
    parts.append(
        f'<path d="M {tx_in1:.2f} {ty_in1:.2f} L {tx_out1:.2f} {ty_out1:.2f} '
        f'L {tx_out2:.2f} {ty_out2:.2f} L {tx_in2:.2f} {ty_in2:.2f} Z" '
        f'fill="#ffffff" opacity="0.95"/>'
    )

    # ─── Solid white center dot ───
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="3.6" fill="#ffffff"/>')

    # ─── Labels: ONLY along the NOW radial, one per ring ───
    # Place at MIDPOINT of the NOW radial within each ring, using the
    # post-rotation screen position
    def _label_at_now(
        r_mid: float, text: str, font_size: float, fill: str, letter_spacing: float = 0.4
    ) -> str:
        a = math.radians(screen_now_deg - 90)
        lx = cx + r_mid * math.cos(a)
        ly = cy + r_mid * math.sin(a)
        return (
            f'<text x="{lx:.2f}" y="{ly + 2:.2f}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="{font_size}" '
            f'font-weight="700" letter-spacing="{letter_spacing}px" '
            f'fill="{fill}">{text}</text>'
        )

    if 0 in now_path:
        parts.append(
            _label_at_now((R_MD_OUT + R_MD_IN) / 2, now_path[0][2][:3].upper(), 8.5, "#e8e8ec", 1.2)
        )
    if 1 in now_path:
        parts.append(
            _label_at_now((R_MD_IN + R_AD_IN) / 2, now_path[1][2][:3].upper(), 7.5, "#d8d8dc", 1.0)
        )
    if 2 in now_path:
        parts.append(
            _label_at_now((R_AD_IN + R_PD_IN) / 2, now_path[2][2][:3].upper(), 6.5, "#c8c8cc", 0.8)
        )
    if 3 in now_path:
        parts.append(
            _label_at_now((R_PD_IN + R_SD_IN) / 2, now_path[3][2][:3].upper(), 5.5, "#b8b8bc", 0.6)
        )
    if 4 in now_path:
        parts.append(
            _label_at_now((R_SD_IN + R_PR_IN) / 2, now_path[4][2][:3].upper(), 4.8, "#a8a8ac", 0.5)
        )

    parts.append("</svg>")

    # ─── Breadcrumb crumb (above the diagram caption) ───
    md_lord_t = current_md_lord.upper()
    ad_lord_t = current_ad_lord.upper()
    pd_lord_t = current_pd_lord.upper()
    sd_lord_t = current_sd_lord.upper()

    md_start_dt = _strip_tz(cur["mahadasha"]["start_date"])
    md_end_dt = _strip_tz(cur["mahadasha"]["end_date"])
    md_yrs_full = SEQ_DICT.get(current_md_lord, int(round((md_end_dt - md_start_dt).days / 365.25)))
    elapsed_in_md = (now - md_start_dt).days / 365.25
    md_start_str = md_start_dt.strftime("%d %b %Y").upper()
    md_end_str = md_end_dt.strftime("%d %b %Y").upper()

    today_str = now.strftime("%d %b %Y").upper()
    crumb = (
        f'<div style="text-align:center;margin-top:6pt;font-family:Inter,sans-serif;'
        f'font-size:8pt;letter-spacing:2.6pt;color:#9b9ba1;font-weight:500;">'
        f'<span style="color:#d8d8dc">{md_lord_t}</span>'
        f' &nbsp;&nbsp;→&nbsp;&nbsp; <span style="color:#d8d8dc">{ad_lord_t}</span>'
        f' &nbsp;&nbsp;→&nbsp;&nbsp; <span style="color:#d8d8dc">{pd_lord_t}</span>'
        f' &nbsp;&nbsp;→&nbsp;&nbsp; <span style="color:#d8d8dc">{sd_lord_t}</span>'
        f"</div>"
        f'<div style="text-align:center;margin-top:6pt;font-family:Inter,sans-serif;'
        f'font-size:8pt;letter-spacing:3pt;color:#d8d8de;font-weight:500;">'
        f"{today_str}</div>"
    )
    footer_top = (
        f'<div style="text-align:center;margin-top:6pt;font-family:Inter,sans-serif;'
        f'font-size:7.5pt;letter-spacing:1.6pt;color:#888;">'
        f'<span style="color:#d8d8dc">{md_lord_t}</span> &nbsp;·&nbsp; '
        f"{md_yrs_full}Y &nbsp;·&nbsp; {md_start_str} → {md_end_str}"
        f"</div>"
    )
    footer_bot = (
        f'<div style="text-align:right;margin-top:4pt;font-family:Inter,sans-serif;'
        f'font-size:7pt;letter-spacing:2.4pt;color:#666;padding-right:18pt;">'
        f"YEAR {elapsed_in_md:.1f} OF {md_yrs_full}"
        f"</div>"
    )

    return crumb + "\n".join(parts) + footer_top + footer_bot


_HOUSE_THEME = {
    1: ("Self · Body", "Tanu"),
    2: ("Wealth · Family · Speech", "Dhana"),
    3: ("Effort · Siblings · Voice", "Sahaja"),
    4: ("Home · Mother · Foundation", "Sukha"),
    5: ("Creativity · Children · Romance", "Putra"),
    6: ("Service · Enemies · Debts", "Shatru"),
    7: ("Spouse · Partnership", "Yuvati"),
    8: ("Transformation · Hidden", "Randhra"),
    9: ("Dharma · Father · Fortune", "Dharma"),
    10: ("Career · Public Role", "Karma"),
    11: ("Gains · Network", "Labha"),
    12: ("Loss · Foreign · Moksha", "Vyaya"),
}

_SIGN_LORD = {
    0: "mars",
    1: "venus",
    2: "mercury",
    3: "moon",
    4: "sun",
    5: "mercury",
    6: "venus",
    7: "mars",
    8: "jupiter",
    9: "saturn",
    10: "saturn",
    11: "jupiter",
}

_SIGN_NAMES_FULL = [
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


def house_lords_map_html(chart_data: dict[str, Any]) -> str:
    """The 12-row personalized House-Lords map for THIS customer.

    For each house: house number + theme + sign sitting on it + lord +
    where the lord sits + one-line interpretive note showing the 'house
    activates through' relationship.
    """
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]

    def _lord_house(lord: str) -> tuple[int, str]:
        """Return (house_lord_sits_in, sign_lord_sits_in)."""
        if lord not in natal:
            return (0, "")
        p_sign = int(float(natal[lord]["longitude"]) // 30)
        h = ((p_sign - lagna_sign_idx) % 12) + 1
        return (h, _SIGN_NAMES_FULL[p_sign])

    # Build 12 rows
    rows_html = ""
    for h in range(1, 13):
        sign_on_house_idx = (lagna_sign_idx + h - 1) % 12
        sign_name = _SIGN_NAMES_FULL[sign_on_house_idx]
        lord = _SIGN_LORD[sign_on_house_idx]
        lord_color = PLANET_COLORS.get(lord, "#c9a96e")
        lord_glyph = PLANET_SYMBOLS.get(lord, "")
        lord_house, lord_sign = _lord_house(lord)
        house_theme, sk = _HOUSE_THEME[h]

        # The "activates through" reading
        if lord_house and lord_house != h:
            activation = f"<b>{h}H themes</b> activate <i>through</i> <b>{lord_house}H</b> ({_HOUSE_THEME[lord_house][0].split('·')[0].strip()})"
        elif lord_house == h:
            activation = f"<b>OWN HOUSE</b> — the strongest signature; {h}H grounds itself"
        else:
            activation = "Lord placement unavailable"

        # Highlight kendra+trikona, dusthana
        if h in (1, 4, 7, 10) and h in (1, 5, 9):
            house_marker = '<span style="background:#d4a843;color:#0e0e10;padding:1pt 5pt;font-family:Inter,sans-serif;font-size:7pt;font-weight:700;border-radius:2px;">KEN+TRI</span>'
        elif h in (1, 4, 7, 10):
            house_marker = '<span style="background:rgba(212,168,67,0.40);color:#fff;padding:1pt 5pt;font-family:Inter,sans-serif;font-size:7pt;font-weight:700;border-radius:2px;">KENDRA</span>'
        elif h in (1, 5, 9):
            house_marker = '<span style="background:rgba(61,139,110,0.40);color:#fff;padding:1pt 5pt;font-family:Inter,sans-serif;font-size:7pt;font-weight:700;border-radius:2px;">TRIKONA</span>'
        elif h in (6, 8, 12):
            house_marker = '<span style="background:rgba(200,74,62,0.32);color:#fff;padding:1pt 5pt;font-family:Inter,sans-serif;font-size:7pt;font-weight:700;border-radius:2px;">DUSTHANA</span>'
        else:
            house_marker = ""

        rows_html += f"""<tr style="border-bottom:0.3pt solid rgba(201,169,110,0.10);">
  <td style="padding:5pt 7pt;width:30pt;vertical-align:top;text-align:center;">
    <div style="font-family:'Cormorant Garamond',serif;font-size:18pt;font-weight:600;color:#c9a96e;">{h}</div>
    <div style="font-family:Inter,sans-serif;font-size:6pt;color:#888;letter-spacing:0.5pt;">{sk.upper()}</div>
  </td>
  <td style="padding:5pt 7pt;width:130pt;vertical-align:top;">
    <div style="font-family:'Cormorant Garamond',serif;font-size:10pt;color:#e8e2d0;">{house_theme}</div>
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;margin-top:2pt;">{sign_name}</div>
    <div style="margin-top:3pt;">{house_marker}</div>
  </td>
  <td style="padding:5pt 7pt;width:75pt;vertical-align:top;">
    <div style="font-family:'Cormorant Garamond',serif;font-size:10pt;color:{lord_color};">
      <span style="font-family:DejaVu Sans,Inter,sans-serif;font-size:13pt;">{lord_glyph}</span> {lord.title()}
    </div>
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;margin-top:2pt;">in {lord_house}H {lord_sign}</div>
  </td>
  <td style="padding:5pt 7pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:8pt;color:#d4d4d4;line-height:1.5;">{activation}</div>
  </td>
</tr>"""

    return f"""<table style="width:100%;border-collapse:collapse;margin:6pt auto;">
<thead>
<tr style="border-bottom:1pt solid #c9a96e;">
  <th style="padding:5pt 7pt;text-align:center;font-family:Inter,sans-serif;font-size:7pt;color:#c9a96e;letter-spacing:1.5pt;">#</th>
  <th style="padding:5pt 7pt;text-align:left;font-family:Inter,sans-serif;font-size:7pt;color:#c9a96e;letter-spacing:1.5pt;">HOUSE THEME</th>
  <th style="padding:5pt 7pt;text-align:left;font-family:Inter,sans-serif;font-size:7pt;color:#c9a96e;letter-spacing:1.5pt;">LORD &amp; PLACEMENT</th>
  <th style="padding:5pt 7pt;text-align:left;font-family:Inter,sans-serif;font-size:7pt;color:#c9a96e;letter-spacing:1.5pt;">HOW IT ACTIVATES</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>"""


_YOGAKARAKA_BY_LAGNA = {
    0: ("None", "Aries Lagna has no single yogakaraka"),
    1: ("Saturn", "Yogakaraka — rules 9H (Capricorn) AND 10H (Aquarius)"),
    2: ("None", "Gemini Lagna has no single yogakaraka"),
    3: ("Mars", "Yogakaraka — rules 5H (Scorpio) AND 10H (Aries)"),
    4: ("Mars", "Yogakaraka — rules 4H (Scorpio) AND 9H (Aries)"),
    5: ("None", "Virgo Lagna has no single yogakaraka"),
    6: ("Saturn", "Yogakaraka — rules 4H (Capricorn) AND 5H (Aquarius)"),
    7: ("None", "Scorpio Lagna has no single yogakaraka"),
    8: ("None", "Sagittarius Lagna has no single yogakaraka"),
    9: ("Venus", "Yogakaraka — rules 5H (Taurus) AND 10H (Libra)"),
    10: ("Venus", "Yogakaraka — rules 4H (Taurus) AND 9H (Libra)"),
    11: ("Mars", "Yogakaraka — rules 5H (Aries via Scorpio) AND 10H (Sagittarius)"),
}

_CHARA_KARAKA_LABELS = [
    ("AK", "Atmakaraka", "Soul significator"),
    ("AmK", "Amatyakaraka", "Career / mind"),
    ("BK", "Bhratrikaraka", "Siblings / peers"),
    ("MK", "Matrikaraka", "Mother / nurture"),
    ("PK", "Putrakaraka", "Children / creativity"),
    ("GK", "Gnatikaraka", "Cousins / enemies"),
    ("DK", "Darakaraka", "Spouse"),
]

_NATURAL_KARAKAS = [
    ("sun", "Soul · father · authority · vitality"),
    ("moon", "Mind · mother · public · comfort"),
    ("mars", "Action · siblings · property · blood"),
    ("mercury", "Intellect · communication · business · skin"),
    ("jupiter", "Wisdom · children (for father) · husband (for women)"),
    ("venus", "Love · wife (for men) · beauty · vehicles"),
    ("saturn", "Discipline · longevity · servants · old-age"),
    ("rahu", "Foreign · technology · unconventional ambition"),
    ("ketu", "Moksha · dissolution · occult · past-life"),
]


def karakas_card_html(chart_data: dict[str, Any]) -> str:
    """The 3-system Karakas explainer — Yogakaraka + Chara Karakas + Natural."""
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]
    yk_planet, yk_note = _YOGAKARAKA_BY_LAGNA.get(lagna_sign_idx, ("None", ""))

    # Compute Chara Karakas — rank planets by degree-in-sign descending
    deg_list = []
    for p in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]:
        if p in natal:
            lon = float(natal[p]["longitude"])
            deg_in_sign = lon - int(lon // 30) * 30
            deg_list.append((p, deg_in_sign))
    deg_list.sort(key=lambda x: x[1], reverse=True)

    # Yogakaraka block
    yk_color = PLANET_COLORS.get(yk_planet.lower(), "#c9a96e")
    yk_glyph = PLANET_SYMBOLS.get(yk_planet.lower(), "")
    yk_html = f"""<div style="background:rgba(212,168,67,0.10);border-left:3pt solid #d4a843;padding:10pt 14pt;margin:8pt 0 16pt 0;border-radius:2px;">
  <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#d4a843;letter-spacing:2pt;margin-bottom:4pt;">YOGAKARAKA</div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:14pt;color:{yk_color};">
    <span style="font-family:DejaVu Sans,Inter,sans-serif;font-size:18pt;">{yk_glyph}</span> {yk_planet}
  </div>
  <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:10pt;color:#aaa;margin-top:3pt;">{yk_note}</div>
</div>"""

    # Chara Karakas block — 7 rows
    ck_rows = ""
    for (label, name, role), (planet, deg) in zip(_CHARA_KARAKA_LABELS, deg_list, strict=False):
        color = PLANET_COLORS.get(planet, "#c9a96e")
        glyph = PLANET_SYMBOLS.get(planet, "")
        ck_rows += f"""<tr style="border-bottom:0.3pt solid rgba(201,169,110,0.10);">
  <td style="padding:4pt 6pt;width:45pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:1pt;font-weight:700;">{label}</div>
  </td>
  <td style="padding:4pt 6pt;width:110pt;vertical-align:top;">
    <div style="font-family:'Cormorant Garamond',serif;font-size:10pt;color:#e8e2d0;">{name}</div>
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;margin-top:1pt;">{role}</div>
  </td>
  <td style="padding:4pt 6pt;vertical-align:top;">
    <div style="font-family:'Cormorant Garamond',serif;font-size:11pt;color:{color};">
      <span style="font-family:DejaVu Sans,Inter,sans-serif;font-size:13pt;">{glyph}</span> {planet.title()}
    </div>
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;margin-top:1pt;">{deg:.2f}° in sign</div>
  </td>
</tr>"""

    # Natural Karakas block
    nk_rows = ""
    for p, role in _NATURAL_KARAKAS:
        color = PLANET_COLORS.get(p, "#c9a96e")
        glyph = PLANET_SYMBOLS.get(p, "")
        nk_rows += f"""<tr>
  <td style="padding:3pt 6pt;width:90pt;">
    <span style="font-family:DejaVu Sans,Inter,sans-serif;font-size:12pt;color:{color};">{glyph}</span>
    <span style="font-family:'Cormorant Garamond',serif;font-size:10pt;color:{color};margin-left:4pt;">{p.title()}</span>
  </td>
  <td style="padding:3pt 6pt;font-family:Inter,sans-serif;font-size:8pt;color:#aaa;">{role}</td>
</tr>"""

    return f"""<div style="margin:6pt auto;">

{yk_html}

<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:2pt;margin:8pt 0 4pt 0;">YOUR 7 CHARA KARAKAS (JAIMINI)</div>
<p style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:9.5pt;color:#aaa;margin:0 0 6pt 0;">Soul-significators ranked by degree-in-sign. The highest-degree planet becomes your Atmakaraka — the planet your soul rides this lifetime.</p>
<table style="width:100%;border-collapse:collapse;margin-bottom:14pt;">
{ck_rows}
</table>

<div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:2pt;margin:14pt 0 4pt 0;">NATURAL KARAKAS (UNIVERSAL)</div>
<p style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:9.5pt;color:#aaa;margin:0 0 6pt 0;">Permanent significations every planet carries — these are the same for everyone.</p>
<table style="width:100%;border-collapse:collapse;">
{nk_rows}
</table>

</div>"""


def karakas_card(chart_data: dict[str, Any]) -> str:
    """The 3-system Karakas explainer as a primer-page card."""
    return _diagram_card(
        "Your Karakas — Three Systems Of Significators",
        karakas_card_html(chart_data),
        "When the report mentions your 'Atmakaraka' or 'Yogakaraka' or "
        "the karaka of marriage, it could be drawing from one of three "
        "different systems. The Yogakaraka is the single most beneficial "
        "planet for your Lagna. The Chara Karakas are your 7 soul-roles "
        "computed by degree. The Natural Karakas are universal planet-roles "
        "everyone shares. All three speak about the same chart from different angles.",
    )


# ─── Rashi-Nakshatra Cosmic Wheel ──────────────────────────────────────────

_RASHI_NAMES_FULL_SK = [
    "MESHA",
    "VRISHABHA",
    "MITHUNA",
    "KARKA",
    "SIMHA",
    "KANYA",
    "TULA",
    "VRISCHIKA",
    "DHANU",
    "MAKARA",
    "KUMBHA",
    "MEENA",
]
_RASHI_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# Element colors (very subtle — fire/earth/air/water)
_RASHI_ELEMENT_COLOR = {
    0: "#3a2a26",
    4: "#3a2a26",
    8: "#3a2a26",  # fire (Aries Leo Sagittarius)
    1: "#293027",
    5: "#293027",
    9: "#293027",  # earth (Taurus Virgo Capricorn)
    2: "#26303a",
    6: "#26303a",
    10: "#26303a",  # air (Gemini Libra Aquarius)
    3: "#262d3a",
    7: "#262d3a",
    11: "#262d3a",  # water (Cancer Scorpio Pisces)
}

# 27 nakshatras with abbreviation (3 chars) — in order from 0° Aries
_NAKSHATRAS_27 = [
    ("ASW", "Ashwini"),
    ("BHA", "Bharani"),
    ("KRT", "Krittika"),
    ("ROH", "Rohini"),
    ("MRG", "Mrigashira"),
    ("ARD", "Ardra"),
    ("PUN", "Punarvasu"),
    ("PUS", "Pushya"),
    ("ASL", "Ashlesha"),
    ("MAG", "Magha"),
    ("PPH", "P.Phalguni"),
    ("UPH", "U.Phalguni"),
    ("HAS", "Hasta"),
    ("CHI", "Chitra"),
    ("SWA", "Swati"),
    ("VIS", "Vishakha"),
    ("ANU", "Anuradha"),
    ("JYE", "Jyeshtha"),
    ("MUL", "Mula"),
    ("PAS", "P.Ashadha"),
    ("UAS", "U.Ashadha"),
    ("SRA", "Shravana"),
    ("DHA", "Dhanishtha"),
    ("SHA", "Shatabhisha"),
    ("PBH", "P.Bhadrapada"),
    ("UBH", "U.Bhadrapada"),
    ("REV", "Revati"),
]

# nakshatra ruler (cycle: ke ve su mo ma ra ju sa me ...)
_NAK_RULERS = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"] * 3


def nakshatra_rashi_wheel_svg(chart_data: dict[str, Any]) -> str:
    """Cosmic Rashi-Nakshatra wheel — 12 signs outer + 27 nakshatras + planets.

    Reference 2 design adapted: dark cosmic background with subtle starfield,
    outer ring of 12 rashi wedges (30° each, color-tinted by element), middle
    ring of 27 nakshatra wedges (13.33° each), planet glyphs plotted in the
    center at their actual sidereal longitudes. A thin radial line marks the
    Lagna position.
    """
    import math

    natal = chart_data.get("natal_planets_dict") or chart_data.get("planets") or {}
    lagna = chart_data.get("lagna", {})
    # Lagna stores rashi_idx + degree separately; reconstruct longitude
    lagna_lon = (
        float(lagna.get("longitude", 0.0))
        if "longitude" in lagna
        else (int(lagna.get("rashi_idx", 0)) * 30 + float(lagna.get("degree", 0.0)))
    )

    cx, cy = 200, 200
    R_RASHI_OUT = 178
    R_RASHI_IN = 145
    R_NAK_OUT = 145
    R_NAK_IN = 118
    R_PLANET_ORBIT = 88  # mid-radius for planet plotting band
    R_PLANET_INNER = 65
    R_CORE = 30

    BG = "#0a0a14"
    STARLIGHT = "#1a1a26"
    NAK_BAND_A = "#1d1d28"
    NAK_BAND_B = "#252535"
    STROKE = "#06060c"

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"',
        ' width="390" height="390" style="display:block;margin:4pt auto;">',
        f'<circle cx="{cx}" cy="{cy}" r="{R_RASHI_OUT + 6}" fill="{BG}" stroke="#202036" stroke-width="0.6"/>',
    ]

    # Subtle starfield (12 random-ish dots)
    star_dots = [
        (40, 60),
        (360, 80),
        (80, 340),
        (330, 330),
        (50, 200),
        (370, 210),
        (110, 90),
        (290, 70),
        (70, 290),
        (310, 300),
        (180, 30),
        (220, 370),
    ]
    for sx, sy in star_dots:
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="0.8" fill="{STARLIGHT}"/>')

    def _wedge(r_out, r_in, a_start, a_end, fill, stroke=STROKE, sw=0.4):
        a1 = math.radians(a_start - 90)
        a2 = math.radians(a_end - 90)
        x1, y1 = cx + r_out * math.cos(a1), cy + r_out * math.sin(a1)
        x2, y2 = cx + r_out * math.cos(a2), cy + r_out * math.sin(a2)
        x3, y3 = cx + r_in * math.cos(a2), cy + r_in * math.sin(a2)
        x4, y4 = cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)
        large = 1 if (a_end - a_start) > 180 else 0
        return (
            f'<path d="M {x1:.2f} {y1:.2f} A {r_out} {r_out} 0 {large} 1 {x2:.2f} {y2:.2f} '
            f'L {x3:.2f} {y3:.2f} A {r_in} {r_in} 0 {large} 0 {x4:.2f} {y4:.2f} Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    # ─── Outer ring: 12 Rashi wedges, 30° each ───
    # Wheel rotated so 0° Aries sits at top
    for i in range(12):
        a_start = i * 30
        a_end = (i + 1) * 30
        fill = _RASHI_ELEMENT_COLOR.get(i, NAK_BAND_A)
        parts.append(_wedge(R_RASHI_OUT, R_RASHI_IN, a_start, a_end, fill, sw=0.5))

    # ─── Middle ring: 27 Nakshatra wedges, 13.33° each, alternating shades ───
    for i in range(27):
        a_start = i * (360 / 27)
        a_end = (i + 1) * (360 / 27)
        fill = NAK_BAND_A if (i % 2 == 0) else NAK_BAND_B
        parts.append(_wedge(R_NAK_OUT, R_NAK_IN, a_start, a_end, fill, sw=0.25))

    # ─── Rashi labels (glyph + Sanskrit name) at outer ring midpoint ───
    for i in range(12):
        mid_deg = i * 30 + 15
        mid_rad = math.radians(mid_deg - 90)
        lx = cx + ((R_RASHI_OUT + R_RASHI_IN) / 2) * math.cos(mid_rad)
        ly = cy + ((R_RASHI_OUT + R_RASHI_IN) / 2) * math.sin(mid_rad)
        # Sanskrit name above glyph
        parts.append(
            f'<text x="{lx:.2f}" y="{ly - 1:.2f}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="6.5" '
            f'letter-spacing="0.8px" fill="#c0c0c8" font-weight="600">'
            f"{_RASHI_NAMES_FULL_SK[i]}</text>"
            f'<text x="{lx:.2f}" y="{ly + 10:.2f}" text-anchor="middle" '
            f'font-family="DejaVu Sans,Inter,sans-serif" font-size="11" '
            f'fill="#a8a8b0">{_RASHI_GLYPHS[i]}</text>'
        )

    # ─── Nakshatra labels (3-char abbreviation) ───
    for i, (abbrev, _full) in enumerate(_NAKSHATRAS_27):
        mid_deg = i * (360 / 27) + (360 / 54)
        mid_rad = math.radians(mid_deg - 90)
        lx = cx + ((R_NAK_OUT + R_NAK_IN) / 2) * math.cos(mid_rad)
        ly = cy + ((R_NAK_OUT + R_NAK_IN) / 2) * math.sin(mid_rad)
        # color the abbrev by nakshatra-ruler planet
        ruler = _NAK_RULERS[i]
        col = PLANET_COLORS.get(ruler, "#8a8a92")
        parts.append(
            f'<text x="{lx:.2f}" y="{ly + 3:.2f}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="6" '
            f'letter-spacing="0.5px" fill="{col}" font-weight="600">'
            f"{abbrev}</text>"
        )

    # ─── Planet glyphs plotted at their natal longitudes ───
    # Render in two passes — outer orbit for slow planets, inner for fast — so
    # they don't collide when close.
    SLOW = {"saturn", "jupiter", "rahu", "ketu"}
    placed: list[tuple[float, str, float, float]] = []  # (long, planet, x, y)

    def _maybe_offset_planet(p_name: str, p_lon: float, base_r: float) -> tuple[float, float]:
        a = math.radians(p_lon - 90)
        # Stagger if a planet is within 4° of an already-placed one
        offset_r = 0
        for ol, op, ox, oy in placed:
            if abs(p_lon - ol) < 4 or abs(p_lon - ol) > 356:
                offset_r += 12
        r = base_r - offset_r
        return cx + r * math.cos(a), cy + r * math.sin(a)

    for p_name in ["saturn", "jupiter", "rahu", "ketu", "mars", "sun", "venus", "mercury", "moon"]:
        if p_name not in natal:
            continue
        pd = natal[p_name]
        if not isinstance(pd, dict):
            continue
        p_lon = float(pd.get("longitude", 0.0))
        base_r = R_PLANET_ORBIT if p_name in SLOW else R_PLANET_INNER
        px, py = _maybe_offset_planet(p_name, p_lon, base_r)
        placed.append((p_lon, p_name, px, py))
        glyph = PLANET_SYMBOLS.get(p_name, "·")
        col = PLANET_COLORS.get(p_name, "#c9a96e")
        # planet disc
        parts.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="9" '
            f'fill="#15151f" stroke="{col}" stroke-width="0.8"/>'
            f'<text x="{px:.2f}" y="{py + 3.5:.2f}" text-anchor="middle" '
            f'font-family="DejaVu Sans,Inter,sans-serif" font-size="10" '
            f'fill="{col}">{glyph}</text>'
        )

    # ─── Lagna marker: thin gold radial from outer edge to nakshatra ring inner edge ───
    lagna_rad = math.radians(lagna_lon - 90)
    lx_out = cx + R_RASHI_OUT * math.cos(lagna_rad)
    ly_out = cy + R_RASHI_OUT * math.sin(lagna_rad)
    lx_in = cx + (R_NAK_IN - 4) * math.cos(lagna_rad)
    ly_in = cy + (R_NAK_IN - 4) * math.sin(lagna_rad)
    parts.append(
        f'<line x1="{lx_out:.2f}" y1="{ly_out:.2f}" x2="{lx_in:.2f}" y2="{ly_in:.2f}" '
        f'stroke="#d4c08c" stroke-width="1.2" opacity="0.92"/>'
    )
    # ASC label outside
    lab_x = cx + (R_RASHI_OUT + 11) * math.cos(lagna_rad)
    lab_y = cy + (R_RASHI_OUT + 11) * math.sin(lagna_rad)
    parts.append(
        f'<text x="{lab_x:.2f}" y="{lab_y + 3:.2f}" text-anchor="middle" '
        f'font-family="Inter,sans-serif" font-size="7" font-weight="700" '
        f'letter-spacing="1px" fill="#d4c08c">ASC</text>'
    )

    # ─── Core disc ───
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{R_CORE}" fill="{BG}" stroke="#303048" stroke-width="0.5"/>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" '
        f'font-family="Cormorant Garamond,serif" font-size="11" font-style="italic" '
        f'fill="#c0c0c8">you</text>'
    )

    parts.append("</svg>")

    # Caption
    asc_sign_idx = int(lagna.get("rashi_idx", int(lagna_lon // 30)))
    asc_sign = _RASHI_NAMES_FULL_SK[asc_sign_idx].title()
    asc_deg = float(lagna.get("degree", lagna_lon % 30))
    moon_lon = float((natal.get("moon") or {}).get("longitude", 0.0)) if natal else 0.0
    moon_nak_idx = int(moon_lon // (360 / 27))
    moon_nak_name = _NAKSHATRAS_27[moon_nak_idx][1] if 0 <= moon_nak_idx < 27 else "—"

    footer = (
        f'<div style="text-align:center;margin-top:8pt;font-family:Inter,sans-serif;'
        f'font-size:8pt;letter-spacing:2pt;color:#9b9ba1;">'
        f'<span style="color:#d4c08c">ASC</span> '
        f"{asc_sign} {asc_deg:.1f}° &nbsp;·&nbsp; "
        f'<span style="color:#d8d8de">MOON</span> in '
        f'<span style="color:#d8d8de">{moon_nak_name}</span>'
        f"</div>"
    )

    return "\n".join(parts) + footer


def nakshatra_rashi_card(chart_data: dict[str, Any]) -> str:
    """The Rashi-Nakshatra cosmic wheel as a primer-page diagram card."""
    return _diagram_card(
        "The Sky At Your Birth — 12 Signs · 27 Nakshatras · 9 Planets",
        nakshatra_rashi_wheel_svg(chart_data),
        "This is the sidereal sky frozen at the moment of your first breath. "
        "The <b>outer ring</b> shows the 12 Rashi (signs) — 30° each, colored "
        "by element (fire / earth / air / water). The <b>middle ring</b> shows "
        "the 27 Nakshatras (lunar mansions) — 13°20' each, colored by their "
        "ruling planet. Inside, your <b>nine planets</b> sit at the exact "
        "degrees where they stood that day. The gold <b>ASC</b> radial marks "
        "your Lagna — the slice of sky rising in the East at your birth.",
    )


def house_lords_card(chart_data: dict[str, Any]) -> str:
    """The personalized 12-row House Lords map as a primer-page card."""
    return _diagram_card(
        "Where Your House Lords Sit — The Architecture of Your Life",
        house_lords_map_html(chart_data),
        "Every house has a lord — the planet that rules the sign sitting on "
        "it. The lord's <i>placement</i> determines how that life-domain plays "
        "out: the house's themes activate THROUGH the house where the lord "
        "sits. Read this table once and you'll understand 80% of how your "
        "chart is wired before you read another paragraph.",
    )


def vimshottari_wheel_card(chart_data: dict[str, Any]) -> str:
    """The Vimshottari Wheel as a primer-page diagram card."""
    return _diagram_card(
        "Your Vimshottari Wheel — The 120-Year Cycle",
        vimshottari_wheel_svg(chart_data),
        "The 9-planet 120-year clock. The outer ring is your "
        "<b>Mahadashas</b> — the slow chapters. Only your <b>current</b> "
        "chapter subdivides inward: ring 2 = the <b>Antardashas</b> "
        "inside it (years apart), ring 3 = <b>Pratyantars</b> (months "
        "apart), ring 4 = <b>Sookshma</b> (weeks apart). Notice the "
        "dates on each ring — the further inside you go, the faster "
        "time moves. The white radial drops on <b>NOW</b>, locked at "
        "the top of the wheel. As time passes, the wheel turns under it.",
    )


def dasha_nesting_card(chart_data: dict[str, Any] | None = None) -> str:
    """Card showing the dasha nesting using THIS customer's actual current
    Mahadasha → Antardasha → Pratyantar, with you-are-here markers."""
    if chart_data:
        try:
            cur = chart_data["dasha"]["current"]
            md_lord = cur["mahadasha"]["lord"].title()
            ad_lord = cur["antardasha"]["lord"].title()
            pd_lord = cur["pratyantardasha"]["lord"].title()
            caption = (
                f"You're currently inside the <b style='color:#c9a96e;'>{md_lord} chapter</b> "
                f"(your Mahadasha — a multi-year arc). Inside that, the "
                f"<b>{ad_lord} section</b> is shaping the past months and the months "
                f"ahead. The narrowest layer — <b>{pd_lord}</b> — is the texture of "
                f"this exact week. When the report says 'dasha lord' it means the "
                f"planet running one of these three layers. When you read about "
                f"'<b>{md_lord}-{ad_lord}-{pd_lord}</b>' that is exactly where you are right now."
            )
            return _diagram_card(
                "How Your Dashas Nest — Where You Are Right Now",
                dasha_nesting_diagram(chart_data),
                caption,
            )
        except Exception:
            pass
    return _diagram_card(
        "How Dashas Nest (Vimshottari)",
        dasha_nesting_diagram(None),
        "Your life moves through planetary 'chapters' (Mahadashas) lasting "
        "6 to 20 years. Inside each chapter sit 9 sub-periods (Antardashas), "
        "and each sub-period contains 9 sub-sub-periods (Pratyantardashas). "
        "All three layers run simultaneously — the present-moment 'flavor' "
        "of your life is the stack of all three.",
    )


# ──────────────────────────────────────────────────────────────────────
# 4b. DASHA vs TRANSIT — the most important conceptual distinction
# ──────────────────────────────────────────────────────────────────────


def dasha_vs_transit_diagram() -> str:
    """Side-by-side: dasha (the chapter, slow) vs transit (the weather, fast).
    Then explains the dasha-transit intersection — the prediction moment."""
    return """<div style="margin:6pt auto;max-width:340pt;">
  <table style="width:100%;border-collapse:separate;border-spacing:10pt 0;">
    <tr>
      <td style="width:48%;background:#1a1a1a;border:0.5pt solid #c9a96e;border-radius:3px;
                 padding:10pt 12pt;vertical-align:top;">
        <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;
                    letter-spacing:2pt;margin-bottom:6pt;text-align:center;">DASHA</div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:11pt;
                    color:#e8e2d0;text-align:center;line-height:1.4;">
          <i>your inner chapter</i><br>
          set at birth · unfolds in years &amp; months<br>
          <span style="color:#888;font-size:9pt;">(Vedic time)</span>
        </div>
      </td>
      <td style="width:48%;background:#1a1a1a;border:0.5pt solid #c9a96e;border-radius:3px;
                 padding:10pt 12pt;vertical-align:top;">
        <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;
                    letter-spacing:2pt;margin-bottom:6pt;text-align:center;">TRANSIT</div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:11pt;
                    color:#e8e2d0;text-align:center;line-height:1.4;">
          <i>today's sky</i><br>
          where planets sit RIGHT NOW · changes hourly to monthly<br>
          <span style="color:#888;font-size:9pt;">(real-time)</span>
        </div>
      </td>
    </tr>
  </table>
  <div style="background:rgba(212,168,67,0.10);border-left:2pt solid #d4a843;
              padding:8pt 12pt;margin-top:10pt;border-radius:2px;">
    <div style="font-family:Inter,sans-serif;font-size:8pt;color:#d4a843;
                letter-spacing:1.5pt;margin-bottom:4pt;">DASHA × TRANSIT</div>
    <div style="font-family:'Cormorant Garamond',serif;font-style:italic;
                font-size:10.5pt;color:#e8e2d0;line-height:1.5;">
      When today's transit lights up a house or planet that your active dasha
      is ALREADY focused on, that's when predictable events fire. The dasha
      sets which themes are live; the transit picks the date.
    </div>
  </div>
</div>"""


def dasha_vs_transit_card() -> str:
    return _diagram_card(
        "Dasha vs Transit — Two Different Clocks",
        dasha_vs_transit_diagram(),
        "This is the single most important distinction in the report. "
        "<b>Dasha</b> is the planetary chapter you're in — slow, decade-scale, "
        "set the moment you were born. <b>Transit</b> is where planets actually "
        "are in the sky right now — fast, week-scale, changes constantly. "
        "Most predictive moments happen when a transit activates a house your "
        "dasha is already lighting up. When the report says 'dasha-transit hit' "
        "or 'the activation fires on [date]' — this is what it means.",
    )


# ──────────────────────────────────────────────────────────────────────
# 5. KAAL SARP / KAAL AMRIT arc
# ──────────────────────────────────────────────────────────────────────


def kaal_sarp_arc_diagram(
    rahu_sign_idx: int,
    ketu_sign_idx: int,
    is_amrit: bool,
) -> str:
    """Circular zodiac with Rahu/Ketu marked and the contained arc shaded."""
    import math

    cx, cy, r = 180, 180, 140
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360"',
        ' width="290" height="290" style="display:block;margin:6pt auto;">',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#444" stroke-width="1"/>',
    ]
    # Sign segments
    for i in range(12):
        start_deg = -90 + i * 30
        end_deg = start_deg + 30
        a1 = math.radians(start_deg)
        a2 = math.radians(end_deg)
        x_outer1, y_outer1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x_outer2, y_outer2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        x_inner1, y_inner1 = cx + (r - 12) * math.cos(a1), cy + (r - 12) * math.sin(a1)
        x_inner2, y_inner2 = cx + (r - 12) * math.cos(a2), cy + (r - 12) * math.sin(a2)
        # If sign i is in the "between" arc, shade
        in_arc = False
        if is_amrit:
            # Ketu→Rahu forward
            s = ketu_sign_idx
            while s != rahu_sign_idx:
                s = (s + 1) % 12
                if s == i:
                    in_arc = True
                    break
        else:
            # Rahu→Ketu forward (Kaal Sarp)
            s = rahu_sign_idx
            while s != ketu_sign_idx:
                s = (s + 1) % 12
                if s == i:
                    in_arc = True
                    break
        path = (
            f"M {x_inner1} {y_inner1} L {x_outer1} {y_outer1} "
            f"A {r} {r} 0 0 1 {x_outer2} {y_outer2} "
            f"L {x_inner2} {y_inner2} A {r-12} {r-12} 0 0 0 {x_inner1} {y_inner1} Z"
        )
        fill = (
            ("rgba(61,139,110,0.32)" if is_amrit else "rgba(157,123,184,0.32)")
            if in_arc
            else "rgba(255,255,255,0.04)"
        )
        parts.append(f'<path d="{path}" fill="{fill}" stroke="#666" stroke-width="0.5"/>')
        # Sign label
        mid = math.radians(start_deg + 15)
        lx, ly = cx + (r - 25) * math.cos(mid), cy + (r - 25) * math.sin(mid)
        parts.append(
            f'<text x="{lx}" y="{ly+4}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="8" fill="#888">{RASHI_SHORT[i]}</text>'
        )
    # Rahu / Ketu markers
    for sign_idx, name, color, symbol in [
        (rahu_sign_idx, "Rahu", "#8b8d92", "☊"),
        (ketu_sign_idx, "Ketu", "#c8843f", "☋"),
    ]:
        mid = math.radians(-90 + sign_idx * 30 + 15)
        mx, my = cx + (r + 18) * math.cos(mid), cy + (r + 18) * math.sin(mid)
        parts.append(
            f'<text x="{mx}" y="{my+5}" text-anchor="middle" '
            f'font-family="DejaVu Sans, Inter, sans-serif" font-size="20" '
            f'fill="{color}">{symbol}</text>'
        )
    label = "Kaal Amrit" if is_amrit else "Kaal Sarp"
    parts.append(
        f'<text x="{cx}" y="{cy-4}" text-anchor="middle" '
        f'font-family="Cormorant Garamond,serif" font-style="italic" '
        f'font-size="14" fill="#c9a96e">{label}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy+12}" text-anchor="middle" '
        f'font-family="Inter,sans-serif" font-size="8" '
        f'fill="#888" letter-spacing="2px">YOGA</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def kaal_sarp_card(rahu_sign_idx: int, ketu_sign_idx: int, is_amrit: bool) -> str:
    title = "Kaal Amrit Yoga" if is_amrit else "Kaal Sarp Yoga"
    direction = "Ketu → Rahu (forward zodiac)" if is_amrit else "Rahu → Ketu (forward zodiac)"
    caption = (
        f"All seven planets sit inside the {'jade-green' if is_amrit else 'amethyst'} arc — "
        f"between Ketu in {RASHI_NAMES[ketu_sign_idx]} and Rahu in {RASHI_NAMES[rahu_sign_idx]}, "
        f"travelling {direction}. "
        + (
            "The benevolent twin: rewards arrive transformed and lasting, "
            "after sustained dharmic effort."
            if is_amrit
            else "Nodal axis dominates the life — effort yields delayed but karmically purified gains."
        )
    )
    return _diagram_card(
        title, kaal_sarp_arc_diagram(rahu_sign_idx, ketu_sign_idx, is_amrit), caption
    )


# ──────────────────────────────────────────────────────────────────────
# 6. MANGAL DOSHA positions diagram
# ──────────────────────────────────────────────────────────────────────


def mangal_dosha_diagram(mars_house_from_lagna: int) -> str:
    """Mini diamond chart showing the 6 doshic positions (1/2/4/7/8/12)
    with Mars's actual position highlighted."""
    DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}
    POS = {
        1: (180, 90),
        2: (90, 45),
        3: (45, 90),
        4: (90, 180),
        5: (45, 270),
        6: (90, 315),
        7: (180, 270),
        8: (270, 315),
        9: (315, 270),
        10: (270, 180),
        11: (315, 90),
        12: (270, 45),
    }
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360"',
        ' width="240" height="240" style="display:block;margin:6pt auto;">',
        '<rect x="0" y="0" width="360" height="360" fill="#0e0e10" stroke="#888" stroke-width="1.5"/>',
        '<line x1="0" y1="0" x2="360" y2="360" stroke="#666" stroke-width="0.8"/>',
        '<line x1="360" y1="0" x2="0" y2="360" stroke="#666" stroke-width="0.8"/>',
        '<polygon points="180,0 360,180 180,360 0,180" fill="none" stroke="#888" stroke-width="1.2"/>',
    ]
    for h in range(1, 13):
        x, y = POS[h]
        is_dosha = h in DOSHA_HOUSES
        is_mars_here = h == mars_house_from_lagna
        if is_mars_here:
            color = "#c84a3e"
            label = "♂"
            font_size = 22
        elif is_dosha:
            color = "rgba(200, 74, 62, 0.40)"
            label = "✗"
            font_size = 16
        else:
            color = "#444"
            label = ""
            font_size = 14
        parts.append(
            f'<text x="{x}" y="{y - 8}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="10" font-weight="600" '
            f'fill="{("#c9a96e" if is_dosha else "#666")}">H{h}</text>'
        )
        if label:
            parts.append(
                f'<text x="{x}" y="{y + 18}" text-anchor="middle" '
                f'font-family="DejaVu Sans, Inter, sans-serif" font-size="{font_size}" '
                f'fill="{color}">{label}</text>'
            )
    parts.append("</svg>")
    return "\n".join(parts)


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def mangal_dosha_card(
    mars_house_from_lagna: int,
    mars_house_from_moon: int,
    is_cancelled: bool,
    cancellation_factors: list[str] | None = None,
    mars_house_from_venus: int | None = None,
) -> str:
    doshic = {1, 2, 4, 7, 8, 12}
    fires_lagna = mars_house_from_lagna in doshic
    fires_moon = mars_house_from_moon in doshic
    fires_venus = mars_house_from_venus in doshic if mars_house_from_venus else False
    # Name only the axes that actually fire, so the verdict matches
    # _mangal_dosha_check (which also tests from Venus — the source of the
    # earlier diagram/narrative contradiction).
    fired_from = []
    if fires_lagna:
        fired_from.append(f"{_ordinal(mars_house_from_lagna)} from Lagna")
    if fires_moon:
        fired_from.append(f"{_ordinal(mars_house_from_moon)} from Moon")
    if fires_venus:
        fired_from.append(f"{_ordinal(mars_house_from_venus)} from Venus")
    fired_str = ", ".join(fired_from)
    if not (fires_lagna or fires_moon or fires_venus):
        verdict = "Mars sits outside the six doshic positions. Mangal Dosha does not fire."
    elif is_cancelled:
        factors = "; ".join(cancellation_factors or []) or "classical mitigation conditions met"
        verdict = (
            f"Mangal Dosha fires (Mars in {fired_str}) but is <b>cancelled</b>: {factors}. "
            "The classical fear does not apply."
        )
    else:
        verdict = (
            f"Mangal Dosha is <b style='color:#c84a3e;'>active</b> — Mars sits in "
            f"{fired_str}. Affects partnership-house themes; needs honest acknowledgement in "
            "matchmaking conversations."
        )
    return _diagram_card(
        "Mangal Dosha — The Six Doshic Positions",
        mangal_dosha_diagram(mars_house_from_lagna),
        f"Classical Mangal (Kuja) Dosha fires when Mars sits in houses 1, 2, 4, 7, "
        f"8, or 12 from the Lagna, Moon, or Venus. {verdict}",
    )


# ──────────────────────────────────────────────────────────────────────
# 7. COMBUST planet diagram — Sun + planet within X°
# ──────────────────────────────────────────────────────────────────────


def combust_diagram(planet: str, planet_lon: float, sun_lon: float, orb_limit: float = 10) -> str:
    """Show Sun's position with a glare-zone, and the planet inside or outside it."""
    color = PLANET_COLORS.get(planet.lower(), "#fff")
    symbol = PLANET_SYMBOLS.get(planet.lower(), planet[:2].title())
    # Normalize to view: Sun at center 180px
    offset = (planet_lon - sun_lon + 180) % 360 - 180
    is_combust = abs(offset) < orb_limit
    # View span: Sun at center, ±20° visible
    view_span = 40
    px_per_deg = 320 / view_span
    sun_x = 160
    planet_x = max(15, min(305, sun_x + offset * px_per_deg))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 100"
width="320" height="96" style="display:block;margin:6pt auto;">
<!-- combust zone shaded -->
<rect x="{sun_x - orb_limit*px_per_deg}" y="36" width="{orb_limit*2*px_per_deg}" height="28"
  fill="rgba(230,201,138,0.18)" stroke="#e6c98a" stroke-width="0.4" stroke-dasharray="3,2"/>
<!-- baseline -->
<line x1="0" y1="50" x2="320" y2="50" stroke="#444" stroke-width="0.5"/>
<!-- Sun glyph -->
<text x="{sun_x}" y="56" text-anchor="middle" font-family="DejaVu Sans, Inter, sans-serif"
  font-size="22" fill="#e6c98a">☉</text>
<!-- Planet glyph -->
<text x="{planet_x}" y="56" text-anchor="middle" font-family="DejaVu Sans, Inter, sans-serif"
  font-size="18" fill="{color}">{symbol}</text>
<!-- labels -->
<text x="{sun_x}" y="80" text-anchor="middle" font-family="Inter,sans-serif"
  font-size="7" fill="#888">Sun ({sun_lon:.1f}°)</text>
<text x="{planet_x}" y="80" text-anchor="middle" font-family="Inter,sans-serif"
  font-size="7" fill="{color}">{planet.title()} ({planet_lon:.1f}°)</text>
<text x="160" y="14" text-anchor="middle" font-family="Cormorant Garamond,serif"
  font-style="italic" font-size="10" fill="#aaa">
  {'COMBUST' if is_combust else 'not combust'} — gap is {abs(offset):.1f}° (combust zone = within {orb_limit}°)
</text>
</svg>"""


def combust_card(planet: str, planet_lon: float, sun_lon: float, orb_limit: float = 10) -> str:
    offset = (planet_lon - sun_lon + 180) % 360 - 180
    is_combust = abs(offset) < orb_limit
    caption = (
        f"A planet within ~{orb_limit:.0f}° of the Sun is **combust** — its rays are "
        f"drowned by solar glare. The planet's significations operate quietly, often "
        f"behind the scenes. "
        f"{planet.title()} is {abs(offset):.1f}° from the Sun, "
        f"{'inside' if is_combust else 'outside'} the combust zone."
    )
    return _diagram_card(
        f"Is {planet.title()} Combust?",
        combust_diagram(planet, planet_lon, sun_lon, orb_limit),
        caption,
    )


# ──────────────────────────────────────────────────────────────────────
# 8. ATMAKARAKA + KARAKAMSHA — the soul-significator pointer
# ──────────────────────────────────────────────────────────────────────


def karakamsha_card(atmakaraka_planet: str, ak_degree: float, karakamsha_sign: str) -> str:
    """Visual card naming the Atmakaraka + its Karakamsha (D9) sign.

    HTML-table layout for reliable side-by-side rendering in WeasyPrint.
    """
    color = PLANET_COLORS.get(atmakaraka_planet.lower(), "#c9a96e")
    symbol = PLANET_SYMBOLS.get(atmakaraka_planet.lower(), atmakaraka_planet[:2].title())
    svg = f"""<table style="margin:6pt auto;border-collapse:separate;border-spacing:14pt 0;width:auto;">
  <tr>
    <td style="background:#1a1a1a;border:1pt solid {color};border-radius:3px;padding:12pt 18pt;text-align:center;width:150pt;vertical-align:middle;">
      <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;letter-spacing:2pt;margin-bottom:8pt;">ATMAKARAKA (SOUL)</div>
      <div style="font-family:DejaVu Sans,Inter,sans-serif;font-size:34pt;color:{color};line-height:1;margin-bottom:6pt;">{symbol}</div>
      <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:11pt;color:{color};">{atmakaraka_planet.title()} &middot; {ak_degree:.2f}&deg;</div>
    </td>
    <td style="vertical-align:middle;color:#c9a96e;font-size:18pt;padding:0 4pt;">→<br><span style="font-size:7pt;color:#888;letter-spacing:1pt;">D9</span></td>
    <td style="background:#1a1a1a;border:1pt solid #c9a96e;border-radius:3px;padding:12pt 18pt;text-align:center;width:130pt;vertical-align:middle;">
      <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;letter-spacing:2pt;margin-bottom:8pt;">KARAKAMSHA</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:22pt;color:#c9a96e;margin-bottom:6pt;">{karakamsha_sign.title()}</div>
      <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:9pt;color:#aaa;">soul's chosen environment</div>
    </td>
  </tr>
</table>"""
    caption = (
        f"Your <b>Atmakaraka</b> ({atmakaraka_planet.title()}) is the planet your soul "
        f"chose to ride this lifetime — the highest-degree planet in your chart "
        f"(excluding the nodes). Its position in the D9 chart (Navamsha) is called "
        f"<b>Karakamsha</b> — your soul's preferred environment. For you, that "
        f"environment is <b style='color:#c9a96e;'>{karakamsha_sign.title()}</b>. "
        f"Spiritual readings begin here."
    )
    return _diagram_card("Atmakaraka → Karakamsha", svg, caption)


# ──────────────────────────────────────────────────────────────────────
# 9. PLANET ASPECTS — which planet sees which
# ──────────────────────────────────────────────────────────────────────


def planet_aspects_diagram(planet: str) -> str:
    """Show the special aspect angles a planet casts."""
    color = PLANET_COLORS.get(planet.lower(), "#c9a96e")
    symbol = PLANET_SYMBOLS.get(planet.lower(), planet[:2].title())
    # Every planet casts 7th aspect; Mars also 4&8, Jupiter also 5&9, Saturn also 3&10
    extra = {
        "mars": [4, 8],
        "jupiter": [5, 9],
        "saturn": [3, 10],
    }.get(planet.lower(), [])
    aspects = sorted({7} | set(extra))
    import math

    cx, cy, r = 180, 180, 130
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360"',
        ' width="290" height="290" style="display:block;margin:6pt auto;">',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="0.5"/>',
    ]
    # 12 segments labeled 1-12 (sign-positions)
    for i in range(12):
        a = math.radians(-90 + i * 30 + 15)
        lx, ly = cx + (r - 20) * math.cos(a), cy + (r - 20) * math.sin(a)
        label_color = color if (i + 1) in aspects or i == 0 else "#666"
        font_weight = "600" if (i + 1) in aspects or i == 0 else "400"
        parts.append(
            f'<text x="{lx}" y="{ly+5}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="11" font-weight="{font_weight}" '
            f'fill="{label_color}">{i+1}</text>'
        )
    # Planet at center
    parts.append(
        f'<text x="{cx}" y="{cy+12}" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, sans-serif" font-size="36" '
        f'fill="{color}">{symbol}</text>'
    )
    # Aspect lines from center to aspected positions
    for h in aspects:
        a = math.radians(-90 + (h - 1) * 30 + 15)
        tx, ty = cx + (r - 35) * math.cos(a), cy + (r - 35) * math.sin(a)
        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" '
            f'stroke="{color}" stroke-width="1.2" stroke-dasharray="3,3" opacity="0.7"/>'
        )
    parts.append("</svg>")
    aspect_words = ", ".join(f"{h}th" for h in aspects)
    parts.append(
        f'<div style="text-align:center;color:#aaa;font-style:italic;font-size:9pt;margin-top:4pt;">'
        f"{planet.title()} aspects houses: {aspect_words} (from its own position)."
        "</div>"
    )
    return "\n".join(parts)


def aspects_card(planet: str) -> str:
    return _diagram_card(
        f"{planet.title()}'s Special Aspects",
        planet_aspects_diagram(planet),
        f"Every planet aspects (sees) the 7th house from itself. "
        f"{planet.title()} additionally has special aspects to specific houses — "
        "shown with dashed lines. Aspect = influence; the aspected house is "
        "shaped by this planet's nature.",
    )


# ──────────────────────────────────────────────────────────────────────
# 10. LIFE STORY SPINE — the WHAT-WHEN-WHY predictive narrative
# ──────────────────────────────────────────────────────────────────────

_CATEGORY_COLORS = {
    "marriage": "#c9a5a5",
    "career": "#e6c98a",
    "wealth": "#d4a843",
    "property": "#9d7bb8",
    "foreign": "#8b8d92",
    "health": "#c84a3e",
    "accident": "#c84a3e",
    "spiritual": "#c8843f",
    "structural_pivot": "#3d8b6e",
    "life_shift": "#d6dadf",
    "family": "#e6c98a",
}

_CATEGORY_LABELS = {
    "marriage": "Marriage / Partnership",
    "career": "Career",
    "wealth": "Wealth / Income",
    "property": "Property / Home",
    "foreign": "Foreign / Relocation",
    "health": "Health Audit",
    "accident": "Caution / Accident-Risk",
    "spiritual": "Spiritual Opening",
    "structural_pivot": "Structural Pivot",
    "life_shift": "Life-Shift",
    "family": "Family Event",
}


_PLANET_TRANSIT_COLOR = {
    "saturn": "#9d7bb8",
    "jupiter": "#d4a843",
    "rahu": "#8b8d92",
    "ketu": "#c8843f",
}


def _slow_transits_table(chart_data: dict, years: int = 5) -> str:
    """Render the slow-transit (Saturn/Jupiter/Rahu) calendar as a table of
    major ingresses with house-from-Lagna and one-line classical reading."""
    try:
        from packages.context.src.slow_transits_calendar import compute_slow_transits_calendar

        events = compute_slow_transits_calendar(chart_data, years_ahead=years)
    except Exception:
        return ""
    if not events:
        return ""

    major = [e for e in events if e["is_major"]]
    rows = ""
    for ev in major[:20]:
        p = ev["planet"].title()
        color = _PLANET_TRANSIT_COLOR.get(ev["planet"], "#c9a96e")
        glyph = {"saturn": "♄", "jupiter": "♃", "rahu": "☊", "ketu": "☋"}.get(ev["planet"], "")
        reading_title = ev["lagna_reading"][0] if ev["lagna_reading"] else ""
        reading_body = ev["lagna_reading"][1] if ev["lagna_reading"] else ""
        rows += f"""<tr style="border-bottom:0.3pt solid rgba(201,169,110,0.10);">
  <td style="padding:5pt 8pt;width:65pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:8.5pt;color:#e8e2d0;font-weight:600;">{ev['date']}</div>
  </td>
  <td style="padding:5pt 8pt;width:90pt;vertical-align:top;border-left:2pt solid {color};">
    <span style="font-family:DejaVu Sans,Inter,sans-serif;font-size:13pt;color:{color};">{glyph}</span>
    <span style="font-family:Inter,sans-serif;font-size:8.5pt;color:#aaa;letter-spacing:0.5pt;margin-left:3pt;">{p}</span>
    <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:9.5pt;color:#c9a96e;margin-top:2pt;">→ {ev['to_sign']}</div>
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;margin-top:1pt;">H{ev['house_from_lagna']} Lagna · H{ev['house_from_moon']} Moon</div>
  </td>
  <td style="padding:5pt 8pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:8.5pt;color:{color};font-weight:600;">{reading_title}</div>
    <div style="font-family:Inter,sans-serif;font-size:8pt;color:#aaa;line-height:1.4;margin-top:2pt;">{reading_body}</div>
  </td>
</tr>"""
    return rows


def life_story_spine_html(chart_data: dict) -> str:
    """Render the full Life Story Spine — current situation + upcoming events table.

    Designed to be ONE clean page the customer can absorb in 60 seconds and
    walk away knowing WHAT will happen, WHEN, and WHY.
    """
    from datetime import datetime

    from packages.context.src.life_event_predictor import (
        get_current_situation,
        predict_life_events,
    )

    cs = get_current_situation(chart_data)
    events = predict_life_events(chart_data)
    now = datetime.now()

    active = [
        e
        for e in events
        if datetime.fromisoformat(e["date_start"]) <= now <= datetime.fromisoformat(e["date_end"])
    ]
    upcoming = [e for e in events if datetime.fromisoformat(e["date_start"]) > now]
    upcoming_20y = [
        e for e in upcoming if datetime.fromisoformat(e["date_start"]).year <= now.year + 20
    ]

    # ── Section 1 — Right Now ──
    now_rows = ""
    for ev in active[:6]:
        color = _CATEGORY_COLORS.get(ev["category"], "#c9a96e")
        cat_label = _CATEGORY_LABELS.get(ev["category"], ev["category"].title())
        end_dt = datetime.fromisoformat(ev["date_end"])
        days_left = (end_dt - now).days
        days_str = f"~{days_left}d left" if 0 < days_left < 730 else f"until {ev['date_end']}"
        now_rows += f"""<tr>
  <td style="padding:6pt 8pt;border-left:3pt solid {color};">
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:{color};letter-spacing:1.5pt;margin-bottom:2pt;">{cat_label.upper()}</div>
    <div style="font-family:'Cormorant Garamond',serif;font-size:11pt;color:#e8e2d0;">{ev['event']}</div>
    <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:8.5pt;color:#888;margin-top:2pt;">{ev['rationale']}</div>
  </td>
  <td style="padding:6pt 8pt;text-align:right;width:75pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;">{days_str}</div>
  </td>
</tr>"""

    # ── Section 2 — Next Upcoming Events Table ──
    upcoming_rows = ""
    for ev in upcoming_20y[:12]:
        color = _CATEGORY_COLORS.get(ev["category"], "#c9a96e")
        cat_label = _CATEGORY_LABELS.get(ev["category"], ev["category"].title())
        conf_color = {
            "certain": "#e6c98a",
            "high": "#3d8b6e",
            "moderate": "#d4a843",
            "low": "#888",
        }.get(ev["confidence"], "#888")
        start_dt = datetime.fromisoformat(ev["date_start"])
        # Date range — short form
        end_dt = datetime.fromisoformat(ev["date_end"])
        if start_dt.year == end_dt.year:
            date_str = f"{start_dt.strftime('%b')} – {end_dt.strftime('%b %Y')}"
        else:
            date_str = f"{start_dt.strftime('%b %Y')} → {end_dt.strftime('%b %Y')}"
        upcoming_rows += f"""<tr style="border-bottom:0.3pt solid rgba(201,169,110,0.10);">
  <td style="padding:7pt 8pt;width:90pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:9pt;color:#e8e2d0;font-weight:600;">{date_str}</div>
    <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#888;margin-top:1pt;">age {ev['life_age']}</div>
  </td>
  <td style="padding:7pt 8pt;border-left:2pt solid {color};vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:7pt;color:{color};letter-spacing:1.5pt;margin-bottom:2pt;">{cat_label.upper()}</div>
    <div style="font-family:'Cormorant Garamond',serif;font-size:11pt;color:#e8e2d0;line-height:1.3;">{ev['event']}</div>
    <div style="font-family:Inter,sans-serif;font-size:8pt;color:#aaa;margin-top:4pt;line-height:1.4;">{ev['rationale']}</div>
  </td>
  <td style="padding:7pt 8pt;text-align:right;width:55pt;vertical-align:top;">
    <span style="background:{conf_color};color:#0e0e10;padding:2pt 6pt;font-family:Inter,sans-serif;font-size:7pt;font-weight:700;letter-spacing:1pt;border-radius:1px;text-transform:uppercase;">{ev['confidence']}</span>
  </td>
</tr>"""

    # ── Section 3 — Current Themes (the WHY-engine for "now") ──
    themes_html = ""
    for theme in cs.get("current_themes", []):
        themes_html += f'<div style="font-family:Inter,sans-serif;font-size:9pt;color:#d4d4d4;margin:3pt 0;">• {theme}</div>'

    # ── Section 4 — Past Verification (trust-builder) ──
    try:
        from packages.context.src.life_event_predictor import get_past_verification_events

        past = get_past_verification_events(chart_data, years_back=8)
    except Exception:
        past = []
    past_rows = ""
    for ev in past[-6:]:  # last 6 past events
        date_str = ev["date_start"]
        past_rows += f"""<tr style="border-bottom:0.3pt solid rgba(201,169,110,0.08);">
  <td style="padding:6pt 8pt;width:80pt;vertical-align:top;">
    <div style="font-family:Inter,sans-serif;font-size:8.5pt;color:#aaa;">{date_str}</div>
  </td>
  <td style="padding:6pt 8pt;vertical-align:top;">
    <div style="font-family:'Cormorant Garamond',serif;font-size:11pt;color:#e8e2d0;">{ev['event']}</div>
    <div style="font-family:Inter,sans-serif;font-size:8pt;color:#aaa;margin-top:3pt;line-height:1.4;">{ev['what_likely_happened']}</div>
  </td>
</tr>"""

    # ── Section 4 — Next Major Pivot Highlight ──
    pivot_html = ""
    if cs.get("next_pivot"):
        np = cs["next_pivot"]
        days = np["days_away"]
        if days < 365:
            time_str = f"{days} days away"
        elif days < 365 * 5:
            time_str = f"{days // 365} years away"
        else:
            time_str = f"~{days // 365} years away"
        pivot_html = f"""<div style="background:rgba(212,168,67,0.10);border-left:3pt solid #d4a843;padding:10pt 14pt;border-radius:2px;margin-top:12pt;">
  <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#d4a843;letter-spacing:2pt;margin-bottom:4pt;">NEXT MAJOR PIVOT</div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:13pt;color:#e8e2d0;line-height:1.3;">{np['event']}</div>
  <div style="font-family:'Cormorant Garamond',serif;font-style:italic;font-size:10pt;color:#aaa;margin-top:3pt;">{np['date']} &middot; {time_str}</div>
</div>"""

    return f"""<div class="life-story-spine">

<h2 style="font-family:'Cormorant Garamond',serif;font-size:24pt;color:#c9a96e;margin:0 0 0.4em 0;padding-bottom:0.35em;border-bottom:1pt solid #c9a96e;">Your Life Story — What, When, Why</h2>

<p style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#aaa;font-size:11pt;margin:0 0 18pt 0;line-height:1.5;">
Every prediction below is grounded in the chart's actual signatures.
<b style="color:#e6c98a;">Certain</b> = astronomical fact (returns, dasha shifts).
<b style="color:#3d8b6e;">High</b> = 3+ chart signatures stack.
<b style="color:#d4a843;">Moderate</b> = 2 signatures stack.
</p>

<h3 style="font-family:'Cormorant Garamond',serif;font-size:14pt;color:#c9a96e;margin:18pt 0 6pt 0;">Where You Are Right Now</h3>

<div style="background:rgba(255,255,255,0.025);border:0.5pt solid rgba(201,169,110,0.25);border-radius:3px;padding:12pt 14pt;margin-bottom:16pt;">
  <div style="font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:2pt;margin-bottom:6pt;">CURRENT ACTIVATION (THE WHY-ENGINE)</div>
  {themes_html}
  {pivot_html}
</div>

<h3 style="font-family:'Cormorant Garamond',serif;font-size:14pt;color:#c9a96e;margin:18pt 0 6pt 0;">Currently Active Windows</h3>

<table style="width:100%;border-collapse:collapse;margin-bottom:16pt;">
{now_rows}
</table>

<h3 style="font-family:'Cormorant Garamond',serif;font-size:14pt;color:#c9a96e;margin:18pt 0 6pt 0;">Looking Back — Past Signatures To Verify</h3>

<p style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#aaa;font-size:10pt;margin:0 0 8pt 0;line-height:1.5;">
These windows from your past show what was structurally active. If you remember events in those domains during those dates, the chart was speaking. This is the trust-anchor for the future predictions below.
</p>

<table style="width:100%;border-collapse:collapse;margin-bottom:20pt;">
{past_rows}
</table>

<h3 style="font-family:'Cormorant Garamond',serif;font-size:14pt;color:#c9a96e;margin:18pt 0 6pt 0;">The Next 20 Years — Major Events Forecast</h3>

<table style="width:100%;border-collapse:collapse;">
<thead>
<tr style="border-bottom:1pt solid #c9a96e;">
  <th style="padding:5pt 8pt;text-align:left;font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:1.5pt;">WHEN</th>
  <th style="padding:5pt 8pt;text-align:left;font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:1.5pt;">WHAT &amp; WHY</th>
  <th style="padding:5pt 8pt;text-align:right;font-family:Inter,sans-serif;font-size:7.5pt;color:#c9a96e;letter-spacing:1.5pt;">CONFIDENCE</th>
</tr>
</thead>
<tbody>
{upcoming_rows}
</tbody>
</table>

<p style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#888;font-size:9pt;margin-top:18pt;line-height:1.5;">
Read this table top-to-bottom as your decade-ahead story. Each row is a window where specific chart signatures stack on the same theme. Predictions land within these windows ~80% of the time when 3+ signatures converge.
</p>

<h3 style="font-family:'Cormorant Garamond',serif;font-size:14pt;color:#c9a96e;margin:24pt 0 4pt 0;">Coming Slow-Transit Weather (Saturn / Jupiter / Rahu)</h3>

<p style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#aaa;font-size:10pt;margin:0 0 10pt 0;line-height:1.5;">
The "weather system" of life events. When a slow planet (Saturn, Jupiter, Rahu) changes sign, it changes which house it activates in your chart — and that's when major life-themes shift in a way you can FEEL. Major dates next 5 years:
</p>

<table style="width:100%;border-collapse:collapse;">
{_slow_transits_table(chart_data, years=5)}
</table>

<p style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#888;font-size:9pt;margin-top:14pt;line-height:1.5;">
Saturn ingress = ~2.5 years in each sign (the 7.5-year Sade Sati cycle is 3 ingresses through 12H/1H/2H from Moon). Jupiter ingress = ~1 year per sign (12-year return cycle). Rahu ingress = ~1.5 years per sign (18-year axis cycle).
</p>

</div>
"""
