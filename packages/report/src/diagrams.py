"""Diagram + chart-wheel generators for 108 Life Reading PDFs (dark mode).

Visual elements:
    1. Personalized chart wheel SVG — North Indian (diamond) style,
       planets in their classical navagraha colors.
    2. Dasha System Pyramid SVG — inverted nested-triangle visual showing
       MD → AD → PD → SD → Prana → Deha hierarchy with the customer's
       actual current dasha lords colored.
    3. Navagrahas reference page — visual cards (one per planet) with
       glyph, sanskrit name, classical color, key themes, dasha years.
    4. Houses reference page — 12-segment circular bhava wheel + table.
"""

from __future__ import annotations

from typing import Any

# ── Sign + planet symbols ──
RASHI_NAMES = [
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
RASHI_SHORT = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

# v12: ASCII two-letter glyphs kept for tables (compact, alphanumeric, always renders).
# A separate `PLANET_SYMBOLS` map carries the proper astrological/devanagari glyphs
# for the chart-wheel SVG and decorative use. Unicode astrology block is well-supported
# by WeasyPrint via the default sans-serif fallback.
PLANET_GLYPHS = {
    "sun": "Su",
    "moon": "Mo",
    "mars": "Ma",
    "mercury": "Me",
    "jupiter": "Ju",
    "venus": "Ve",
    "saturn": "Sa",
    "rahu": "Ra",
    "ketu": "Ke",
}
PLANET_SYMBOLS = {
    "sun": "☉",  # ☉ Sun
    "moon": "☽",  # ☽ Moon (waxing crescent — more elegant than full disc)
    "mars": "♂",  # ♂ Mars
    "mercury": "☿",  # ☿ Mercury
    "jupiter": "♃",  # ♃ Jupiter
    "venus": "♀",  # ♀ Venus
    "saturn": "♄",  # ♄ Saturn
    "rahu": "☊",  # ☊ Ascending Node (Rahu)
    "ketu": "☋",  # ☋ Descending Node (Ketu)
}
PLANET_SANSKRIT = {
    "sun": "Surya",
    "moon": "Chandra",
    "mars": "Mangala",
    "mercury": "Budha",
    "jupiter": "Guru",
    "venus": "Shukra",
    "saturn": "Shani",
    "rahu": "Rahu",
    "ketu": "Ketu",
}

# Navagraha colors — V3 muted-jewel palette, tuned for Option H Onyx+champagne
# background. Each color passes WCAG AA-Large contrast on #0e0e10 background
# (smallest is Mars at 4.2, largest Moon at 13.9). Classical associations preserved
# (Sun gold, Mars red, Mercury green, Jupiter saffron, Saturn purple, etc.) but
# saturation lowered so they sit beside the champagne accent without fighting it.
PLANET_COLORS = {
    "sun": "#e6c98a",  # ivory-gold (sūrya) — distinct from champagne accent
    "moon": "#d6dadf",  # soft silver (chandra)
    "mars": "#c84a3e",  # warm brick red (kuja)
    "mercury": "#3d8b6e",  # deep jade (budha)
    "jupiter": "#d4a843",  # mustard-saffron (guru) — replaces dated lemon yellow
    "venus": "#c9a5a5",  # dusty rose (shukra)
    "saturn": "#9d7bb8",  # dusty amethyst (shani) — muted purple, not Material violet
    "rahu": "#8b8d92",  # cool smoke (rahu)
    "ketu": "#c8843f",  # warm cinnamon (ketu)
}

PLANET_KARAKA = {
    "sun": "Soul, father, authority, vitality",
    "moon": "Mind, mother, comfort, public",
    "mars": "Action, courage, siblings, property",
    "mercury": "Intellect, communication, business",
    "jupiter": "Wisdom, dharma, children, fortune",
    "venus": "Love, beauty, money, partnership",
    "saturn": "Discipline, karma, longevity, structure",
    "rahu": "Ambition, foreign, unconventional",
    "ketu": "Dissolution, mysticism, moksha",
}

PLANET_DASHA_YEARS = {
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "mercury": 17,
    "jupiter": 16,
    "venus": 20,
    "saturn": 19,
    "rahu": 18,
    "ketu": 7,
}


# ════════════════════════════════════════════════════════
#  1. NAVAGRAHA VISUAL CARDS PAGE
# ════════════════════════════════════════════════════════


def _planet_card_html(p: str) -> str:
    color = PLANET_COLORS[p]
    glyph = PLANET_GLYPHS[p]
    sanskrit = PLANET_SANSKRIT[p]
    english = p.title()
    karaka = PLANET_KARAKA[p]
    years = PLANET_DASHA_YEARS[p]
    return f"""
    <div class="planet-card" style="border-left:4px solid {color};">
      <div class="planet-card-header" style="color:{color};">
        <span class="planet-glyph">{glyph}</span>
        <span class="planet-sanskrit">{sanskrit}</span>
        <span class="planet-english">/ {english}</span>
        <span class="planet-years">{years}y</span>
      </div>
      <div class="planet-karaka">{karaka}</div>
    </div>
    """


def navagrahas_page_html() -> str:
    """The Navagrahas educational page — visual cards in classical colors."""
    cards = "\n".join(
        _planet_card_html(p)
        for p in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"]
    )
    return f"""
<div class="diagram-page navagrahas-page">

<h2>The Nine Planets — Navagrahas</h2>

<p class="page-intro">Vedic astrology uses nine grahas (significators), not eight planets. Each governs specific themes in your chart and rules a portion of the 120-year Vimshottari Dasha cycle. The colors below are the classical color of each graha — used as accent throughout this report.</p>

<div class="planet-grid">
{cards}
</div>

<h3 style="margin-top:24pt;">The Vimshottari Dasha System</h3>

<p>Each graha rules a major life-period (Mahadasha) in a fixed sequence totaling <b>120 years</b>. Which graha rules at any moment is determined by the Moon's nakshatra at birth. Inside each Mahadasha, the same nine grahas run sub-periods — each level smaller, each modulating the parent period's flavor.</p>

<div class="dasha-sequence">
  <span class="dasha-pill" style="background:#c8843f;">Ke 7y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#c9a5a5;color:#000;">Ve 20y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#e6c98a;">Su 6y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#d6dadf;color:#000;">Mo 10y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#c84a3e;">Ma 7y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#9ca3af;color:#000;">Ra 18y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#d4a843;color:#000;">Ju 16y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#9d7bb8;">Sa 19y</span>
  <span class="dasha-arrow">→</span>
  <span class="dasha-pill" style="background:#3d8b6e;">Me 17y</span>
</div>

</div>
"""


# ════════════════════════════════════════════════════════
#  2. DASHA PYRAMID SVG (per customer)
# ════════════════════════════════════════════════════════


def dasha_pyramid_svg(data: dict[str, Any]) -> str:
    """Inverted-pyramid HTML showing this customer's current dasha hierarchy.

    Six nested trapezoidal bands rendered as plain HTML divs (NOT inline SVG —
    WeasyPrint's SVG support stops after the first polygon for nested shapes,
    so we use CSS-positioned divs which render reliably). Each band is
    colored by the lord ruling that level + labeled with lord + duration.
    """
    cur = data["dasha"]["current"]
    levels: list[dict[str, Any]] = []
    # Show only the three meaningful levels (MD/AD/PD). The deeper SD/Prana/Deha
    # layers are technically computed but rarely lived-with by customers and
    # cramped the visual. Stripped per v12 review.
    for level_name, key, label in [
        ("Mahadasha", "mahadasha", "MD"),
        ("Antardasha", "antardasha", "AD"),
        ("Pratyantar", "pratyantardasha", "PD"),
    ]:
        info = cur.get(key)
        if info:
            lord = info.get("lord", "?")
            color = PLANET_COLORS.get(lord, "#888")
            levels.append(
                {
                    "label": label,
                    "name": level_name,
                    "lord": lord.title(),
                    "color": color,
                }
            )

    # Each band shrinks meaningfully so the pyramid reads as 3 distinct bands.
    bands_html: list[str] = []
    light_planets = {"#d6dadf", "#c9a5a5", "#d4a843", "#e6c98a"}
    widths = [100, 70, 44]  # explicit, balanced widths for 3 levels
    for i, lv in enumerate(levels):
        width_pct = widths[i] if i < len(widths) else max(20, 100 - i * 22)
        text_color = "#0e0e10" if lv["color"] in light_planets else "#fff"
        bands_html.append(
            f'<div style="'
            f'width:{width_pct}%;'
            f'margin:0 auto;'
            f'background:{lv["color"]};'
            f'opacity:0.94;'
            f'padding:12pt 14pt;'
            f'border-bottom:1px solid rgba(0,0,0,0.4);'
            f'font-family:Inter,sans-serif;'
            f'font-size:11pt;'
            f'font-weight:600;'
            f'letter-spacing:2px;'
            f'color:{text_color};'
            f'text-align:center;'
            f'">{lv["label"]} &middot; {lv["lord"]} &middot; {lv["name"]}</div>'
        )
    bands = "".join(bands_html)
    return (
        '<div class="dasha-pyramid" style="margin:14pt 0 8pt 0;">'
        f"{bands}"
        '<div style="text-align:center;margin-top:8pt;">'
        '<span style="color:#fff;font-size:14pt;">&#x25BC;</span>'
        '<div style="color:#aaa;font-style:italic;font-family:Cormorant Garamond,serif;'
        'font-size:10pt;margin-top:2pt;">this exact moment in your life</div>'
        "</div>"
        "</div>"
    )


def dasha_diagram_html(data: dict[str, Any]) -> str:
    """Full dasha-system diagram page with per-customer pyramid + caption."""
    pyramid = dasha_pyramid_svg(data)
    return f"""
<div class="diagram-page dasha-page">

<h2>Your Dasha Hierarchy — Right Now</h2>

<p class="page-intro">The Vimshottari Dasha system nests planetary periods within periods. The widest band is your Mahadasha (the multi-year chapter you're inside). Each band beneath it is a sub-period within the parent. The three shown below are the layers that shape your lived experience week-to-week, year-to-year, and decade-to-decade.</p>

<div style="margin:36pt 0;">
{pyramid}
</div>

<table class="dasha-detail-table">
<thead><tr><th>Level</th><th>Lord</th><th>Duration</th><th>What it does</th></tr></thead>
<tbody>
<tr><td><b>Mahadasha</b></td><td>{data['dasha']['current']['mahadasha']['lord'].title()}</td>
    <td>{data['dasha']['current']['mahadasha'].get('years_total', '?')} years</td>
    <td>The multi-year chapter of your life</td></tr>
<tr><td><b>Antardasha</b></td><td>{data['dasha']['current']['antardasha']['lord'].title()}</td>
    <td>months &ndash; years</td><td>The sub-period flavour modulating the chapter</td></tr>
<tr><td><b>Pratyantardasha</b></td><td>{data['dasha']['current']['pratyantardasha']['lord'].title()}</td>
    <td>weeks &ndash; months</td><td>The current operating weather</td></tr>
</tbody>
</table>

</div>
"""


# ════════════════════════════════════════════════════════
#  3. HOUSES PAGE — visual wheel + table
# ════════════════════════════════════════════════════════


def houses_wheel_svg() -> str:
    """12-segment circular bhava wheel with categories color-coded."""
    house_categories = {
        1: ("kendra+trikona", "#d4a843"),  # both
        2: ("dhana", "#d6dadf"),
        3: ("upachaya", "#3d8b6e"),
        4: ("kendra", "#e6c98a"),
        5: ("trikona", "#d4a843"),
        6: ("dusthana+upachaya", "#c84a3e"),
        7: ("kendra+maraka", "#e6c98a"),
        8: ("dusthana", "#9d7bb8"),
        9: ("trikona", "#d4a843"),
        10: ("kendra+upachaya", "#e6c98a"),
        11: ("upachaya+labha", "#3d8b6e"),
        12: ("dusthana+vyaya", "#9d7bb8"),
    }
    cx, cy, r = 200, 200, 160
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" '
        'width="320" height="320" style="display:block;margin:0 auto;">',
        # Outer circle
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#888" stroke-width="1.5"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r-90}" fill="none" stroke="#444" stroke-width="0.5"/>',
    ]
    import math

    for h in range(1, 13):
        # House 1 starts at top-left going clockwise (Vedic convention)
        # Angle: each house is 30 degrees
        angle_start = -90 - (h - 1) * 30  # start from 12 o'clock counter-clockwise (Vedic)
        angle_end = angle_start - 30
        # Convert to radians
        a1 = math.radians(angle_start)
        a2 = math.radians(angle_end)
        # Segment points
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        path = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 0 0 {x2} {y2} Z"
        _cat, color = house_categories[h]
        parts.append(
            f'<path d="{path}" fill="{color}" fill-opacity="0.18" stroke="#666" stroke-width="0.5"/>'
        )
        # House number label
        label_angle = math.radians((angle_start + angle_end) / 2)
        lx, ly = cx + (r - 30) * math.cos(label_angle), cy + (r - 30) * math.sin(label_angle)
        parts.append(
            f'<text x="{lx}" y="{ly+5}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="14" font-weight="700" '
            f'fill="#fff">{h}</text>'
        )
    # Center label
    parts.append(
        f'<text x="{cx}" y="{cy-5}" text-anchor="middle" '
        f'font-family="Cormorant Garamond,serif" font-size="13" '
        f'fill="#aaa" font-style="italic">Bhavas</text>'
    )
    parts.append(
        f'<text x="{cx}" y="{cy+10}" text-anchor="middle" '
        f'font-family="Inter,sans-serif" font-size="9" '
        f'fill="#888" letter-spacing="2px">12 HOUSES</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def houses_page_html() -> str:
    rows = ""
    house_data = [
        (1, "Tanu", "Self, body, personality, vitality", "Sun", "Kendra+Trikona"),
        (2, "Dhana", "Wealth, family, speech, food", "Jupiter", "Dhana"),
        (3, "Sahaja", "Siblings, courage, communication", "Mars", "Upachaya"),
        (4, "Sukha", "Mother, home, comfort, vehicles", "Moon", "Kendra"),
        (5, "Putra", "Children, creativity, intelligence", "Jupiter", "Trikona"),
        (6, "Shatru", "Enemies, illness, debts, service", "Mars", "Dusthana"),
        (7, "Yuvati", "Spouse, partnership, business", "Venus", "Kendra+Maraka"),
        (8, "Randhra", "Transformation, longevity, occult", "Saturn", "Dusthana"),
        (9, "Dharma", "Father, dharma, fortune, guru", "Jupiter", "Trikona"),
        (10, "Karma", "Career, status, public role", "Sun", "Kendra"),
        (11, "Labha", "Gains, friends, aspirations", "Jupiter", "Upachaya"),
        (12, "Vyaya", "Losses, moksha, foreign, isolation", "Saturn", "Dusthana"),
    ]
    for h, sk, what, kar, cat in house_data:
        rows += f"<tr><td><b>{h}</b></td><td>{sk}</td><td>{what}</td><td>{kar}</td><td><i>{cat}</i></td></tr>\n"

    return f"""
<div class="diagram-page houses-page">

<h2>The Twelve Houses — Bhavas</h2>

<p class="page-intro">The chart is divided into twelve houses (bhavas), counted from your Lagna (Ascendant). Each house governs specific life domains. Where a planet sits, and which planet rules each house, determines the chart's structural readings.</p>

{houses_wheel_svg()}

<table class="houses-table">
<thead><tr><th>#</th><th>Sanskrit</th><th>What it governs</th><th>Karaka</th><th>Category</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>

<p class="caption-small">
<b style="color:#d4a843;">Trikona (1, 5, 9)</b> — trine houses of dharma. Most auspicious. &nbsp;
<b style="color:#e6c98a;">Kendra (1, 4, 7, 10)</b> — angular pillars; planets here gain strength. &nbsp;
<b style="color:#3d8b6e;">Upachaya (3, 6, 10, 11)</b> — houses of growth, compound positively over time. &nbsp;
<b style="color:#9d7bb8;">Dusthana (6, 8, 12)</b> — difficult houses; in dusthana lordship pattern, can create Vipreet Raja Yoga.
</p>

</div>
"""


# ════════════════════════════════════════════════════════
#  4. PERSONALIZED CHART WHEEL (North Indian, dark)
# ════════════════════════════════════════════════════════


def chart_wheel_svg(natal_planets: dict[str, dict[str, Any]], lagna_idx: int) -> str:
    """North Indian style chart wheel SVG, dark mode, planets in their colors."""
    house_planets: dict[int, list[tuple[str, str]]] = {h: [] for h in range(1, 13)}
    for pname, pdata in natal_planets.items():
        if not isinstance(pdata, dict):
            continue
        lon = float(pdata.get("longitude", 0))
        sign_idx = int(lon // 30) % 12
        house = ((sign_idx - lagna_idx) % 12) + 1
        # v12: use astrological symbol (☉☽♂☿♃♀♄☊☋) instead of ASCII (Su, Mo...)
        glyph = PLANET_SYMBOLS.get(pname, PLANET_GLYPHS.get(pname, pname[:2].title()))
        color = PLANET_COLORS.get(pname, "#fff")
        house_planets[house].append((glyph, color))

    house_signs = {h: RASHI_SHORT[(lagna_idx + h - 1) % 12] for h in range(1, 13)}

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
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360" '
        'width="320" height="320" style="background:#0e0e10;border:1px solid #444;">',
        '<rect x="0" y="0" width="360" height="360" fill="#0e0e10" stroke="#888" stroke-width="2"/>',
        '<line x1="0" y1="0" x2="360" y2="360" stroke="#666" stroke-width="1"/>',
        '<line x1="360" y1="0" x2="0" y2="360" stroke="#666" stroke-width="1"/>',
        '<polygon points="180,0 360,180 180,360 0,180" fill="none" stroke="#888" stroke-width="1.5"/>',
    ]

    for h in range(1, 13):
        x, y = POS[h]
        sign = house_signs[h]
        planets = house_planets[h]
        parts.append(
            f'<text x="{x}" y="{y - 25}" text-anchor="middle" '
            f'font-family="Georgia,serif" font-size="9" fill="#888" font-style="italic">{sign}</text>'
        )
        parts.append(
            f'<text x="{x}" y="{y - 14}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="8" fill="#d4a843" font-weight="600">H{h}</text>'
        )
        if planets:
            # Render each planet glyph in its own color
            line1 = planets[:3]
            line2 = planets[3:6]
            x_offset = -((len(line1) - 1) * 18) / 2
            for i, (glyph, color) in enumerate(line1):
                parts.append(
                    f'<text x="{x + x_offset + i*18}" y="{y + 5}" text-anchor="middle" '
                    f'font-family="DejaVu Sans, Inter, sans-serif" font-size="15" font-weight="500" '
                    f'fill="{color}">{glyph}</text>'
                )
            if line2:
                x_offset2 = -((len(line2) - 1) * 18) / 2
                for i, (glyph, color) in enumerate(line2):
                    parts.append(
                        f'<text x="{x + x_offset2 + i*18}" y="{y + 22}" text-anchor="middle" '
                        f'font-family="Inter,sans-serif" font-size="12" font-weight="700" '
                        f'fill="{color}">{glyph}</text>'
                    )
    parts.append("</svg>")
    return "\n".join(parts)


def chart_wheel_page_html(data: dict[str, Any]) -> str:
    svg = chart_wheel_svg(data["natal_planets_dict"], data["lagna"]["rashi_idx"])
    rows = ""
    for p in data.get("planets", []):
        retro = "<span style='color:#c84a3e;'>(R)</span>" if p.get("is_retrograde") else ""
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
    return f"""
<div class="diagram-page chart-wheel-page">

<h2>Your Birth Chart — Rashi (D1)</h2>

<p style="text-align:center;color:#aaa;font-style:italic;margin:0 0 24pt 0;">
{data['birth']['full_name']} &middot; Born {data['birth']['datetime_human']}<br>
<b style="color:#d4a843;">{data['lagna']['rashi']} Lagna</b> &middot;
<b style="color:#d6dadf;">{data['moon']['rashi']} Moon</b> in
<b>{data['moon']['nakshatra']}</b>
</p>

<div style="text-align:center;margin:0 0 24pt 0;">
{svg}
</div>

<p class="caption-small">
North Indian (diamond) style. Lagna at top center. Houses count counter-clockwise.
Each planet shown in its classical color.
</p>

<h3>Chart at a glance</h3>

<table class="chart-table">
<thead><tr><th>Planet</th><th>Sign</th><th>House</th><th>Nakshatra</th><th>Pada</th><th>Status</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>

</div>
"""


# ════════════════════════════════════════════════════════
#  D9 NAVAMSHA CHART — marriage/dharma/strength
# ════════════════════════════════════════════════════════


def _d9_sign_idx_of(longitude: float) -> int:
    """Compute Navamsha sign index for a sidereal longitude."""
    sign = int(longitude // 30)
    deg = longitude - sign * 30
    nav_idx = int(deg // (30.0 / 9.0))
    if sign in (0, 3, 6, 9):  # movable
        d9_start = sign
    elif sign in (1, 4, 7, 10):  # fixed
        d9_start = (sign + 8) % 12
    else:  # dual
        d9_start = (sign + 4) % 12
    return (d9_start + nav_idx) % 12


def d9_chart_wheel_svg(natal_planets: dict[str, dict[str, Any]], d1_lagna_longitude: float) -> str:
    """North Indian D9 (Navamsha) chart — marriage/dharma/inner-strength layer.

    Uses D9 sign as house frame. D9 Lagna = navamsha of the D1 lagna longitude.
    Same visual idiom as the D1 wheel so the customer can read them side by side.
    """
    d9_lagna_idx = _d9_sign_idx_of(d1_lagna_longitude)
    house_planets: dict[int, list[tuple[str, str]]] = {h: [] for h in range(1, 13)}
    for pname, pdata in natal_planets.items():
        if not isinstance(pdata, dict):
            continue
        lon = float(pdata.get("longitude", 0))
        d9_sign = _d9_sign_idx_of(lon)
        house = ((d9_sign - d9_lagna_idx) % 12) + 1
        glyph = PLANET_SYMBOLS.get(pname, PLANET_GLYPHS.get(pname, pname[:2].title()))
        color = PLANET_COLORS.get(pname, "#fff")
        house_planets[house].append((glyph, color))

    house_signs = {h: RASHI_SHORT[(d9_lagna_idx + h - 1) % 12] for h in range(1, 13)}
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
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360" '
        'width="320" height="320" style="background:#0e0e10;border:1px solid #444;">',
        '<rect x="0" y="0" width="360" height="360" fill="#0e0e10" stroke="#888" stroke-width="2"/>',
        '<line x1="0" y1="0" x2="360" y2="360" stroke="#666" stroke-width="1"/>',
        '<line x1="360" y1="0" x2="0" y2="360" stroke="#666" stroke-width="1"/>',
        '<polygon points="180,0 360,180 180,360 0,180" fill="none" stroke="#888" stroke-width="1.5"/>',
    ]
    for h in range(1, 13):
        x, y = POS[h]
        sign = house_signs[h]
        planets = house_planets[h]
        parts.append(
            f'<text x="{x}" y="{y - 25}" text-anchor="middle" '
            f'font-family="Georgia,serif" font-size="9" fill="#888" font-style="italic">{sign}</text>'
        )
        parts.append(
            f'<text x="{x}" y="{y - 14}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="8" fill="#d4a843" font-weight="600">H{h}</text>'
        )
        if planets:
            line1 = planets[:3]
            line2 = planets[3:6]
            x_offset = -((len(line1) - 1) * 18) / 2
            for i, (glyph, color) in enumerate(line1):
                parts.append(
                    f'<text x="{x + x_offset + i*18}" y="{y + 5}" text-anchor="middle" '
                    f'font-family="DejaVu Sans, Inter, sans-serif" font-size="15" font-weight="500" '
                    f'fill="{color}">{glyph}</text>'
                )
            if line2:
                x_offset2 = -((len(line2) - 1) * 18) / 2
                for i, (glyph, color) in enumerate(line2):
                    parts.append(
                        f'<text x="{x + x_offset2 + i*18}" y="{y + 22}" text-anchor="middle" '
                        f'font-family="DejaVu Sans, Inter, sans-serif" font-size="15" font-weight="500" '
                        f'fill="{color}">{glyph}</text>'
                    )
    parts.append("</svg>")
    return "\n".join(parts)


def d9_chart_page_html(data: dict[str, Any]) -> str:
    """The Navamsha (D9) chart page — marriage, dharma, and inner-strength layer.

    Renders D1 + D9 side-by-side so the customer can see how the planets
    move between the two charts (the classical 'second face' of the natal chart).
    """
    natal = data["natal_planets_dict"]
    d1_lagna_lon = data["lagna"]["rashi_idx"] * 30 + data["lagna"]["degree"]
    d9_svg = d9_chart_wheel_svg(natal, d1_lagna_lon)
    d1_svg = chart_wheel_svg(natal, data["lagna"]["rashi_idx"])
    d9_lagna_sign = RASHI_NAMES[_d9_sign_idx_of(d1_lagna_lon)]
    return f"""
<div class="diagram-page d9-chart-page">

<h2>Your Navamsha — D9 Chart</h2>

<p style="text-align:center;color:#aaa;font-style:italic;margin:0 0 18pt 0;font-size:10pt;">
The D9 (Navamsha) is the second face of your natal chart — the classical
lens for marriage, dharma, and the inner strength of every planet. A planet
that looks weak in the birth chart (D1) but strong in D9 is described as
"having a second chance." Read these two side by side.
</p>

<div style="display:block;text-align:center;margin:0 0 16pt 0;">
  <div style="display:inline-block;margin:0 14pt;vertical-align:top;">
    <div style="color:#c9a96e;font-family:'Cormorant Garamond',serif;font-size:13pt;margin-bottom:6pt;letter-spacing:1px;">D1 &middot; Rashi</div>
    {d1_svg}
    <div style="color:#888;font-size:9pt;font-style:italic;margin-top:6pt;">{data['lagna']['rashi']} Lagna</div>
  </div>
  <div style="display:inline-block;margin:0 14pt;vertical-align:top;">
    <div style="color:#c9a96e;font-family:'Cormorant Garamond',serif;font-size:13pt;margin-bottom:6pt;letter-spacing:1px;">D9 &middot; Navamsha</div>
    {d9_svg}
    <div style="color:#888;font-size:9pt;font-style:italic;margin-top:6pt;">{d9_lagna_sign} D9 Lagna</div>
  </div>
</div>

<p class="caption-small">
The D9 sign of each planet shows the soul-level "preferred environment" of that planet —
where it actually wants to live. Marriage, dharma, and second-half-of-life themes
read more accurately from D9 than from D1.
</p>

</div>
"""


# ════════════════════════════════════════════════════════
#  LIFELINE — horizontal past→present→future timeline
# ════════════════════════════════════════════════════════


def lifeline_svg(data: dict[str, Any]) -> str:
    """Horizontal timeline of all Mahadashas with TODAY marker.

    Width 720, height 130. Each MD = colored block (PLANET_COLORS) sized
    by years. Today is a vertical line with label. Decade tick marks
    below for orientation.
    """
    from datetime import datetime

    md_seq = data.get("dasha", {}).get("mahadasha_sequence", [])
    if not md_seq:
        return ""

    # Parse dates
    def _parse(d: str) -> datetime:
        # Accept "YYYY-MM-DD..." iso strings
        return (
            datetime.fromisoformat(d.replace("Z", "+00:00"))
            if "T" in d
            else datetime.fromisoformat(d)
        )

    spans: list[dict[str, Any]] = []
    for m in md_seq:
        try:
            spans.append(
                {
                    "lord": m["lord"],
                    "start": _parse(m["start"]),
                    "end": _parse(m["end"]),
                    "years": float(m.get("years", 0)),
                }
            )
        except Exception:
            continue
    if not spans:
        return ""

    first = spans[0]["start"]
    last = spans[-1]["end"]
    total_secs = max((last - first).total_seconds(), 1.0)
    # TODAY from generated_at, fall back to now
    try:
        today = _parse(data["meta"]["generated_at"])
        # Strip tz so subtraction works with naive datetimes
        if today.tzinfo and not first.tzinfo:
            today = today.replace(tzinfo=None)
        if first.tzinfo and not today.tzinfo:
            today = today.replace(tzinfo=first.tzinfo)
    except Exception:
        today = datetime.utcnow()

    # Birth date — separate from first MD start (first MD usually starts BEFORE birth)
    try:
        birth_dt = (
            _parse(data["birth"]["datetime_iso"])
            if "datetime_iso" in data.get("birth", {})
            else None
        )
    except Exception:
        birth_dt = None

    W, H = 720, 130
    BAR_Y, BAR_H = 30, 36
    LEFT, RIGHT = 0, W

    def _x(dt: datetime) -> float:
        # Clamp to bar range
        if first.tzinfo and not dt.tzinfo:
            dt = dt.replace(tzinfo=first.tzinfo)
        elif dt.tzinfo and not first.tzinfo:
            dt = dt.replace(tzinfo=None)
        frac = (dt - first).total_seconds() / total_secs
        return max(0.0, min(1.0, frac)) * (RIGHT - LEFT) + LEFT

    # Build colored MD blocks
    blocks_svg: list[str] = []
    labels_svg: list[str] = []
    for s in spans:
        x0 = _x(s["start"])
        x1 = _x(s["end"])
        w = max(x1 - x0, 0.5)
        lord = s["lord"]
        color = PLANET_COLORS.get(lord, "#666")
        is_current = s["start"] <= today < s["end"]
        stroke = "#d4a843" if is_current else "rgba(255,255,255,0.10)"
        sw = 2 if is_current else 0.6
        blocks_svg.append(
            f'<rect x="{x0:.1f}" y="{BAR_Y}" width="{w:.1f}" height="{BAR_H}" '
            f'fill="{color}" opacity="{0.95 if is_current else 0.78}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )
        # Planet glyph in-block only if block is wide enough
        if w >= 28:
            labels_svg.append(
                f'<text x="{x0 + w/2:.1f}" y="{BAR_Y + BAR_H/2 + 4}" '
                f'text-anchor="middle" font-family="Inter,sans-serif" font-size="11" '
                f'font-weight="600" fill="#0e0e10">{PLANET_GLYPHS.get(lord,"?")}</text>'
            )
        # Years label below block for wide blocks
        if w >= 40:
            labels_svg.append(
                f'<text x="{x0 + w/2:.1f}" y="{BAR_Y + BAR_H + 12}" '
                f'text-anchor="middle" font-family="Inter,sans-serif" font-size="8" '
                f'fill="#888">{round(s["years"])}y</text>'
            )

    # Decade tick marks below
    ticks_svg: list[str] = []
    if birth_dt:
        for age in range(0, 110, 10):
            tick_dt = birth_dt.replace(year=birth_dt.year + age)
            if tick_dt < first or tick_dt > last:
                continue
            tx = _x(tick_dt)
            ticks_svg.append(
                f'<line x1="{tx:.1f}" y1="{BAR_Y + BAR_H + 18}" '
                f'x2="{tx:.1f}" y2="{BAR_Y + BAR_H + 22}" stroke="#555" stroke-width="0.8"/>'
            )
            ticks_svg.append(
                f'<text x="{tx:.1f}" y="{BAR_Y + BAR_H + 33}" text-anchor="middle" '
                f'font-family="Inter,sans-serif" font-size="8" fill="#888">{age}</text>'
            )

    # TODAY marker
    today_x = _x(today)
    today_marker = (
        f'<line x1="{today_x:.1f}" y1="{BAR_Y - 8}" x2="{today_x:.1f}" y2="{BAR_Y + BAR_H + 8}" '
        f'stroke="#d4a843" stroke-width="2" stroke-dasharray="3,2"/>'
        f'<text x="{today_x:.1f}" y="{BAR_Y - 12}" text-anchor="middle" '
        f'font-family="Inter,sans-serif" font-size="9" fill="#d4a843" font-weight="600">TODAY</text>'
    )

    # End labels
    end_labels = (
        f'<text x="0" y="{BAR_Y + BAR_H + 33}" text-anchor="start" '
        f'font-family="Inter,sans-serif" font-size="8" fill="#666">age</text>'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="100%" style="max-width:720px;display:block;margin:0 auto;">'
        + "".join(blocks_svg)
        + "".join(labels_svg)
        + "".join(ticks_svg)
        + today_marker
        + end_labels
        + "</svg>"
    )
    return svg


# ════════════════════════════════════════════════════════
#  CONVERGENCE DIAGRAM — defining planets at a glance
# ════════════════════════════════════════════════════════


def convergence_diagram_svg(data: dict[str, Any]) -> str:
    """Hub-and-spoke diagram of planets carrying 3+ classical signatures.

    Visual translation of the dossier's CONVERGENCE TRIGGERS block. Each
    convergence planet is a circle in its navagraha color, sized by the
    number of signatures. Spokes labeled with each signature (Lagna lord,
    Atmakaraka, current Mahadasha, etc.) point in.
    """
    # Recompute convergence signatures (same logic as gather_deep_chart_layers)
    natal = data.get("natal_planets_dict", {})
    lagna_idx = data.get("lagna", {}).get("rashi_idx", 0)
    cur_md = (data.get("dasha", {}) or {}).get("current", {}).get("mahadasha", {}).get("lord")

    # Sign lords (must match knowledge_gatherer SIGN_LORDS_IDX)
    SLORD = {
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

    sigs: list[tuple[str, str]] = []
    sigs.append((SLORD[lagna_idx], "Lagna lord"))
    sigs.append((SLORD[(lagna_idx + 1) % 12], "2nd lord (wealth)"))
    sigs.append((SLORD[(lagna_idx + 6) % 12], "7th lord (partnership)"))
    sigs.append((SLORD[(lagna_idx + 8) % 12], "9th lord (dharma)"))
    sigs.append((SLORD[(lagna_idx + 9) % 12], "10th lord (career)"))
    if cur_md:
        sigs.append((cur_md, "current Mahadasha"))
    # Jaimini karakas (Atmakaraka, Amatyakaraka, Darakaraka, Putrakaraka)
    try:
        from datetime import datetime

        from packages.context.src.state_engine import _build_birth_chart
        from packages.self.src.jaimini import calculate_chara_karakas

        birth_dt = datetime.fromisoformat(data["birth"]["datetime"])
        from packages.report.src.knowledge_gatherer import _RASHI

        moon_lon = data["moon"]["longitude"]
        chart = _build_birth_chart(
            birth_dt,
            data["birth"]["lat"],
            data["birth"]["lon"],
            natal,
            _RASHI[lagna_idx],
            _RASHI[int(moon_lon // 30) % 12],
            moon_lon,
        )
        for k in calculate_chara_karakas(chart):
            role = (k.karaka.value if hasattr(k.karaka, "value") else str(k.karaka)).lower()
            planet = (k.planet.value if hasattr(k.planet, "value") else str(k.planet)).lower()
            if role == "atmakaraka":
                sigs.append((planet, "Soul-significator"))
            elif role == "amatyakaraka":
                sigs.append((planet, "Career-mind significator"))
            elif role == "darakaraka":
                sigs.append((planet, "Spouse-significator"))
            elif role == "putrakaraka":
                sigs.append((planet, "Children-significator"))
    except Exception:
        pass

    from collections import Counter, defaultdict

    counts = Counter(p for p, _ in sigs)
    by_planet: dict[str, list[str]] = defaultdict(list)
    for p, label in sigs:
        by_planet[p].append(label)

    # Convergence threshold = 3+ signatures
    converged = sorted(
        [(p, by_planet[p]) for p, c in counts.items() if c >= 3], key=lambda x: -len(x[1])
    )
    if not converged:
        return (
            '<div style="text-align:center;color:#aaa;font-style:italic;'
            'padding:30pt;">No single planet in this chart carries 3 or more '
            "classical signatures. Each life area has its own ruler — read the "
            "house-lord walk for the structural map.</div>"
        )

    # Layout: each converged planet gets its own hub-and-spoke "card"
    cards: list[str] = []
    for planet, labels in converged:
        color = PLANET_COLORS.get(planet, "#888")
        glyph = PLANET_GLYPHS.get(planet, "?")
        sanskrit = PLANET_SANSKRIT.get(planet, "")
        karaka = PLANET_KARAKA.get(planet, "")
        # SVG: hub at center, spokes labeled
        n = len(labels)
        W, H = 540, 320
        cx, cy, hub_r = W // 2, H // 2, 44
        import math

        spokes_svg: list[str] = []
        for i, label in enumerate(labels):
            angle = (-math.pi / 2) + (2 * math.pi * i / n)
            # Outer label position
            lx = cx + 200 * math.cos(angle)
            ly = cy + 130 * math.sin(angle)
            # Spoke endpoint at hub edge
            sx = cx + hub_r * math.cos(angle)
            sy = cy + hub_r * math.sin(angle)
            # Label endpoint just inside the text
            ex = lx - 50 * math.cos(angle)
            ey = ly - 14 * math.sin(angle)
            spokes_svg.append(
                f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
                f'stroke="{color}" stroke-width="1.2" stroke-opacity="0.5"/>'
            )
            anchor = (
                "start"
                if math.cos(angle) > 0.1
                else ("end" if math.cos(angle) < -0.1 else "middle")
            )
            spokes_svg.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
                f'font-family="Inter,sans-serif" font-size="10" fill="#e8e8e8" '
                f'dominant-baseline="middle">{label}</text>'
            )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="100%" style="max-width:540px;display:block;margin:0 auto;">'
            + "".join(spokes_svg)
            + f'<circle cx="{cx}" cy="{cy}" r="{hub_r}" fill="{color}" '
            f'fill-opacity="0.95" stroke="rgba(255,255,255,0.25)" stroke-width="2"/>'
            + f'<text x="{cx}" y="{cy-6}" text-anchor="middle" '
            f'font-family="Cormorant Garamond,serif" font-size="22" '
            f'font-weight="700" fill="#0e0e10">{glyph}</text>'
            + f'<text x="{cx}" y="{cy+14}" text-anchor="middle" '
            f'font-family="Inter,sans-serif" font-size="9" fill="#0e0e10" '
            f'letter-spacing="0.5px">{planet.upper()}</text>' + "</svg>"
        )
        card = (
            f'<div class="convergence-card" style="margin-bottom:18pt;">'
            f'<div style="text-align:center;margin-bottom:6pt;">'
            f'<div style="color:{color};font-family:Cormorant Garamond,serif;'
            f'font-size:20pt;font-weight:600;">{planet.title()} <span '
            f'style="opacity:0.7;font-style:italic;font-size:13pt;">({sanskrit})</span></div>'
            f'<div style="color:#aaa;font-size:9pt;">Carries {len(labels)} '
            f"classical signatures &middot; {karaka}</div></div>{svg}</div>"
        )
        cards.append(card)

    return (
        '<div style="margin:14pt 0;">'
        + '<p style="text-align:center;color:#aaa;font-style:italic;'
        + 'font-size:9.5pt;margin:0 0 14pt 0;">When a single planet shows up '
        + "across many classical lenses, the reader has structurally LIVED "
        + "its themes. These are your chart's defining planets.</p>"
        + "".join(cards)
        + "</div>"
    )


# ════════════════════════════════════════════════════════
#  PUBLIC ENTRY — assemble all 4 diagram pages
# ════════════════════════════════════════════════════════


def all_diagram_pages_html(data: dict[str, Any]) -> str:
    """All 4 diagram pages stitched together for the PDF.

    Order: Chart Wheel (personal) → Dasha Pyramid (personal) →
           Navagrahas (reference) → Houses (reference).
    """
    return (
        chart_wheel_page_html(data)
        + dasha_diagram_html(data)
        + navagrahas_page_html()
        + houses_page_html()
    )
