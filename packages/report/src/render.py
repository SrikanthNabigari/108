"""Markdown -> branded PDF rendering for 108 Life Reading reports.

Dark-mode aesthetic. Pure black background, off-white body text. Each of
the nine grahas carries its classical color (saffron Sun, rose Venus,
emerald Mercury, etc.) used as accent throughout — for headings,
highlighted planet names, list markers, table dividers.

Pipeline:
    markdown -> HTML (markdown-it-py with table + html) -> 108 brand HTML
    template -> WeasyPrint -> PDF.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from markdown_it import MarkdownIt
from weasyprint import HTML

from packages.report.src.diagrams import PLANET_COLORS, PLANET_KARAKA, PLANET_SANSKRIT

logger = logging.getLogger(__name__)


# Pre-compile planet-name colorizer regex (case-insensitive whole-word)
_PLANET_NAMES_RE = re.compile(
    r"\b(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\b",
    re.IGNORECASE,
)


def _colorize_planets(html: str) -> str:
    """Wrap planet names in coloured <span> tags using their navagraha colors.

    On the FIRST mention of each planet in the report body, also append a
    small italic Sanskrit aside — "Mercury (Budha)" — so the reader bridges
    the English name to the Sanskrit they'll see elsewhere. Subsequent
    mentions are just colored. Every mention gets a `title` attribute (its
    karaka) which some PDF viewers surface on hover.

    Excludes blocks marked with `class="dasha-pyramid"` so the pyramid's
    contrast-aware text colors are preserved.
    """
    seen: set[str] = set()

    def repl(m: re.Match) -> str:
        word = m.group(1)
        key = word.lower()
        color = PLANET_COLORS.get(key, "#f1ede5")
        karaka = PLANET_KARAKA.get(key, "")
        sanskrit = PLANET_SANSKRIT.get(key, "")
        title_attr = f' title="{sanskrit} — {karaka}"' if karaka else ""
        if key not in seen and sanskrit and sanskrit.lower() != key:
            seen.add(key)
            return (
                f'<span class="planet-name" style="color:{color};font-weight:600;"{title_attr}>'
                f"{word}</span>"
                f'<span class="planet-aside" style="color:{color};opacity:0.62;'
                f'font-style:italic;font-size:0.85em;">&nbsp;({sanskrit})</span>'
            )
        return (
            f'<span class="planet-name" style="color:{color};font-weight:600;"{title_attr}>'
            f"{word}</span>"
        )

    # Excise pyramid blocks first so we don't recolor their already-contrast text
    pyramid_re = re.compile(r'<div class="dasha-pyramid".*?</div>\s*</div>', re.DOTALL)
    pyramids: list[str] = []

    def stash(m: re.Match) -> str:
        pyramids.append(m.group(0))
        return f"\x00PYRAMID_{len(pyramids)-1}\x00"

    stripped = pyramid_re.sub(stash, html)
    colored = _PLANET_NAMES_RE.sub(repl, stripped)
    for idx, original in enumerate(pyramids):
        colored = colored.replace(f"\x00PYRAMID_{idx}\x00", original)
    return colored


_ADDON_DOMAIN_MAP = [
    ("career", "career"),
    ("relationship", "relationships"),
    ("marriage", "relationships"),
    ("wealth", "wealth"),
    ("money", "wealth"),
    ("health", "health"),
    ("body", "health"),
    ("spiritual", "spiritual"),
    ("dharma", "spiritual"),
    ("foreign", "foreign"),
    ("settlement", "foreign"),
    ("education", "education"),
    ("learning", "education"),
    ("property", "property"),
    ("vehicle", "property"),
    ("business", "business"),
    ("entrepreneur", "business"),
    ("muhurta", "muhurta"),
    ("gem", "gem"),
    ("children", "children"),
    ("past 5", "past_5"),
    ("next 5", "next_5"),
    ("lifetime", "lifetime"),
]


def _domain_for_title(title: str) -> str:
    t = title.lower()
    for keyword, domain in _ADDON_DOMAIN_MAP:
        if keyword in t:
            return domain
    return "default"


def _mark_addon_sections(html: str) -> str:
    """Replace `<h2>Add-on: …</h2>` with a badged H2 inside a `.addon-section` div.

    The wrapper div is closed at the next `<h2>` (any kind) or at the end of
    the body. Each section also carries a `data-domain` attribute so CSS can
    color-code the badge by the section's karaka planet (Career = Sun,
    Relationships = Venus, etc.).
    """
    pat = re.compile(
        r"<h2>Add-on:\s*([^<]+?)</h2>\s*(.*?)(?=<h2>|\Z)",
        re.DOTALL,
    )

    def repl(m: re.Match) -> str:
        title = m.group(1).strip()
        body = m.group(2)
        domain = _domain_for_title(title)
        return (
            f'<div class="addon-section" data-domain="{domain}">'
            '<div class="addon-badge">ADD-ON READING</div>'
            f'<h2 class="addon-h2">{title}</h2>'
            f"{body}"
            "</div>"
        )

    return pat.sub(repl, html)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{
    size: A4;
    margin: 20mm 18mm 22mm 18mm;
    background: #0e0e10;
    /* Option H: hairline champagne frame inside the page margin */
    border: 0.75pt solid #c9a96e;
    @bottom-left {{
        content: "108 \\2014  Life's Operating System";
        font-family: 'Inter', 'Helvetica', sans-serif;
        font-size: 8pt;
        color: #888;
        font-style: italic;
        letter-spacing: 1.5px;
    }}
    @bottom-center {{
        content: "{customer_name}";
        font-family: 'Cormorant Garamond', 'Georgia', serif;
        font-size: 8.5pt;
        color: #c9a96e;
        font-style: italic;
        letter-spacing: 1.2px;
    }}
    @bottom-right {{
        content: counter(page) " of " counter(pages);
        font-family: 'Inter', 'Helvetica', sans-serif;
        font-size: 8pt;
        color: #888;
        letter-spacing: 1px;
    }}
    /* Corner accents — solid champagne squares at top-left & bottom-right */
    @top-left-corner {{
        content: "";
        background: #c9a96e;
        width: 8pt;
        height: 8pt;
    }}
    @bottom-right-corner {{
        content: "";
        background: #c9a96e;
        width: 8pt;
        height: 8pt;
    }}
}}
/* Cover page — no footer at all, larger top margin for visual rest */
@page :first {{
    margin-top: 28mm;
    @bottom-left {{ content: ""; }}
    @bottom-center {{ content: ""; }}
    @bottom-right {{ content: ""; }}
}}
/* Section pages — let each section start on a new page where it makes sense.
   We rely on H2-driven page breaks below rather than per-page rules. */

* {{ box-sizing: border-box; }}

html, body {{
    background: #0e0e10;
    color: #f1ede5;
    margin: 0;
    padding: 0;
}}

body {{
    font-family: 'Inter', 'Helvetica', 'Arial', sans-serif;
    font-size: 10.5pt;
    line-height: 1.65;
    color: #f1ede5;
}}

/* ── COVER PAGE ── */
h1 {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 38pt;
    font-weight: 600;
    color: #c9a96e;
    margin: 0 0 0.3em 0;
    letter-spacing: -0.5px;
    line-height: 1.1;
}}
/* "108" lockup ONLY on the cover's H1 (the first H1 in the document).
   Stray H1s from agent narratives no longer trigger this giant decoration. */
body > h1:first-of-type::before {{
    content: "108";
    font-size: 0.4em;
    color: #c9a96e;
    font-weight: 300;
    letter-spacing: 6px;
    display: block;
    margin-bottom: 1em;
    opacity: 0.7;
}}
h1 + p strong {{
    color: #c9a96e;
    font-size: 13pt;
    letter-spacing: 0.5px;
}}

/* ── SECTION HEADINGS ──
   Generous top margin so H2 breathes from prior content. We don't force
   page-break here — that produced an inflated page count when short
   sections each consumed a full page. WeasyPrint will paginate naturally;
   addon sections still get their own page via the .addon-section wrapper. */
h2 {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 24pt;
    font-weight: 500;
    color: #c9a96e;
    margin: 1.6em 0 0.4em 0;
    padding-bottom: 0.35em;
    border-bottom: 1px solid #c9a96e;
    page-break-after: avoid;
    break-after: avoid;
    letter-spacing: -0.3px;
}}
h3 {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 15pt;
    font-weight: 500;
    color: #d4b896;
    margin: 1.8em 0 0.4em 0;
    page-break-after: avoid;
    break-after: avoid;
    letter-spacing: -0.2px;
}}

/* ── PARAGRAPHS ── */
/* Ragged-right (not justified) on a narrow A4 column — avoids the rivers and
   over-hyphenation that read as cheap; editorial-premium sets left-aligned. */
p {{
    margin: 0.6em 0 0.9em 0;
    text-align: left;
    hyphens: none;
    color: #d6d6d6;
}}

em {{
    color: #d6dadf;
    font-style: italic;
}}
strong {{
    color: #c9a96e;
    font-weight: 600;
}}

/* ── BLOCKQUOTES (user's question) ── */
blockquote {{
    border-left: 3px solid #c9a96e;
    background: #1a1a1a;
    margin: 1em 0;
    padding: 0.8em 1.2em;
    font-style: italic;
    color: #c9a96e;
    font-size: 11pt;
    border-radius: 2px;
}}
blockquote p {{
    margin: 0;
    color: #c9a96e;
}}

/* ── TABLES ── */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
    break-inside: avoid;
    background: #111;
}}
th {{
    background: #c9a96e;
    color: #0e0e10;
    font-weight: 700;
    text-align: left;
    padding: 7pt 10pt;
    font-size: 9pt;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
td {{
    padding: 6pt 10pt;
    border-bottom: 1px solid #2a2a2a;
    vertical-align: top;
    color: #d4d4d4;
}}
tr:nth-child(even) td {{
    background: #161616;
}}

/* ── BULLET LISTS ── */
ul {{
    margin: 0.5em 0 1em 0;
    padding-left: 1.4em;
}}
ul li {{
    margin: 0.4em 0;
    line-height: 1.6;
    color: #d4d4d4;
}}
ul li::marker {{
    color: #c9a96e;
}}

ol {{
    margin: 0.5em 0 1em 0;
    padding-left: 1.6em;
}}
ol li {{
    margin: 0.5em 0;
    padding-left: 0.3em;
    line-height: 1.6;
    color: #d4d4d4;
}}
ol li::marker {{
    color: #c9a96e;
    font-weight: 600;
}}

/* ── HORIZONTAL RULES ── */
hr {{
    border: 0;
    height: 1px;
    background: linear-gradient(to right,
        transparent 0%, #c9a96e 30%, #c9a96e 70%, transparent 100%);
    margin: 2.5em 0;
    opacity: 0.4;
}}

/* ── INLINE CODE ── */
code {{
    background: #1f1f1f;
    padding: 0.05em 0.35em;
    border-radius: 2px;
    font-family: 'Menlo', 'Monaco', monospace;
    font-size: 9pt;
    color: #c9a96e;
}}

p, blockquote, table, ul, ol {{ orphans: 2; widows: 2; }}

/* ── FOOTER CREDIT ── */
.footer-credit {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-style: italic;
    color: #666;
    text-align: center;
    margin-top: 2em;
    font-size: 10pt;
    letter-spacing: 2px;
}}

/* ════════════════════════════════════════════ */
/*  DIAGRAM PAGES                                */
/* ════════════════════════════════════════════ */

.diagram-page {{
    page-break-before: always;
    break-before: page;
    color: #f1ede5;
}}

.diagram-page .page-intro {{
    color: #aaa;
    font-style: italic;
    text-align: left;
    font-size: 10.5pt;
    margin-bottom: 24pt;
}}

.caption-small {{
    font-size: 9pt;
    color: #9a9a9a;
    text-align: center;
    font-style: italic;
    margin-top: 12pt;
    line-height: 1.6;
}}

/* ── NAVAGRAHAS PAGE — planet cards ── */
.planet-grid {{
    display: block;
}}
.planet-card {{
    background: #1a1a1a;
    margin: 8pt 0;
    padding: 8pt 14pt;
    border-radius: 2px;
    page-break-inside: avoid;
    break-inside: avoid;
}}
.planet-card-header {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 14pt;
    font-weight: 500;
    margin-bottom: 4pt;
}}
.planet-glyph {{
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 11pt;
    background: rgba(255,255,255,0.08);
    padding: 2pt 6pt;
    border-radius: 3px;
    margin-right: 8pt;
}}
.planet-sanskrit {{ font-style: italic; }}
.planet-english {{
    color: #888;
    font-size: 11pt;
    margin-left: 4pt;
}}
.planet-years {{
    float: right;
    color: #888;
    font-size: 10pt;
    font-family: 'Inter', sans-serif;
    font-style: italic;
    margin-top: 3pt;
}}
.planet-karaka {{
    color: #ccc;
    font-size: 10pt;
    margin-top: 0;
}}

.dasha-sequence {{
    text-align: center;
    margin: 16pt 0;
    line-height: 2;
}}
.dasha-pill {{
    display: inline-block;
    padding: 3pt 8pt;
    border-radius: 12pt;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 9pt;
    color: #fff;
    margin: 2pt 0;
    letter-spacing: 0.5px;
}}
.dasha-arrow {{
    color: #888;
    margin: 0 4pt;
    font-size: 11pt;
}}

/* ── DASHA PAGE ── */
.dasha-detail-table th {{
    background: #c9a96e;
    color: #0e0e10;
}}
.dasha-detail-table td:first-child {{
    color: #c9a96e;
    font-weight: 600;
}}

/* ── HOUSES PAGE ── */
.houses-table {{
    margin-top: 16pt;
}}

/* ── CHART WHEEL PAGE ── */
.chart-wheel-page svg {{
    border-radius: 4px;
}}
.chart-table th {{
    background: #c9a96e;
    color: #0e0e10;
}}

/* ── COVER HOOK (stitcher output on page 1) ──
   Sized to fit beneath the cover header + table on a single A4 page. If
   the stitcher writes a longer-than-usual hook it will spill to page 2;
   that's acceptable. We don't force a page-break here because TOC already
   sets page-break-before, which avoids the empty-page artifact. */
.cover-hook {{
    margin-top: 20pt;
    padding: 14pt 18pt;
    background: #15110a;
    border-left: 3px solid #c9a96e;
    border-radius: 2px;
}}
.cover-hook p {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 11.5pt;
    line-height: 1.55;
    color: #e8e2d0;
    margin: 0 0 0.3em 0;
    text-align: left;
    hyphens: none;
    font-style: italic;
}}
.cover-hook p:last-child {{ margin-bottom: 0; }}

/* ── PRIMER TABLE (reference page) ── */
.primer-table {{
    font-size: 9pt;
}}
.primer-table th {{
    background: #1a1a1a;
    color: #c9a96e;
    font-size: 8pt;
}}
.primer-table td {{
    padding: 4pt 8pt;
}}

/* ── PULL-QUOTE (one per section, set apart) ── */
.pull-quote {{
    position: relative;
    margin: 18pt 24pt 22pt 24pt;
    padding: 12pt 18pt 14pt 36pt;
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 14pt;
    line-height: 1.45;
    color: #f5efd9;
    font-style: italic;
    border-left: 2px solid #c9a96e;
    background: rgba(250, 204, 21, 0.04);
    page-break-inside: avoid;
}}
.pull-quote-mark {{
    position: absolute;
    left: 8pt;
    top: -2pt;
    color: #c9a96e;
    font-family: 'Cormorant Garamond', serif;
    font-size: 36pt;
    line-height: 1;
    font-style: normal;
    opacity: 0.7;
}}

/* ── CUSP NOTE (lagna near sign boundary, in Sources & Method) ── */
.cusp-note {{
    margin: 8pt 0 14pt 0;
    padding: 12pt 14pt;
    background: rgba(220, 38, 38, 0.06);
    border-left: 2px solid #dc2626;
    border-radius: 2px;
    font-size: 10pt;
    line-height: 1.55;
    color: #f1d4d4;
}}
.cusp-note p:first-child {{ margin-top: 0; }}
.cusp-note p:last-child {{ margin-bottom: 0; }}

/* Life Story Spine — start on a fresh page so its 24pt heading never orphans
   at the bottom of the preceding section. */
.life-story-spine {{
    page-break-before: always;
}}

/* ── ADD-ON SECTIONS (deep-dives + year-window readings) ──
   NOTE: do NOT set `page-break-inside: avoid` — many add-ons exceed a
   single page and WeasyPrint will then render an EMPTY placeholder page
   (just the badge + title) before the content. Let the content flow. */
.addon-section {{
    margin: 0 0 24pt 0;
    padding: 22pt 22pt 18pt 22pt;
    background: linear-gradient(180deg, rgba(201, 169, 110, 0.04) 0%, rgba(14,14,16,0) 60%);
    border-top: 1px solid rgba(201, 169, 110, 0.40);
    border-bottom: 1px solid rgba(201, 169, 110, 0.18);
    page-break-before: always;
}}
/* Keep the badge + heading from breaking apart from the first paragraph */
.addon-badge, .addon-h2 {{
    page-break-after: avoid;
    page-break-inside: avoid;
}}
.addon-badge {{
    display: inline-block;
    margin-bottom: 6pt;
    padding: 2pt 8pt;
    background: #c9a96e;
    color: #0e0e10;
    font-family: 'Inter', sans-serif;
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 2px;
    border-radius: 1px;
}}
.addon-h2 {{
    color: #d4b896;
    margin-top: 0;
    border-bottom-color: rgba(201, 169, 110, 0.30);
}}

/* ── ADD-ON DOMAIN THEMING ──
   Each add-on section is tagged by domain → colored accent on the badge
   and border, matching the karaka planet (Sun for career, Venus for
   relationships, Jupiter for wealth/education, etc.). Subtle but ties the
   reading visually to the planetary palette. */
.addon-section[data-domain="career"]       .addon-badge {{ background: #e6c98a; }}  /* Sun */
.addon-section[data-domain="relationships"] .addon-badge {{ background: #c9a5a5; }} /* Venus */
.addon-section[data-domain="wealth"]       .addon-badge {{ background: #d4a843; }}  /* Jupiter */
.addon-section[data-domain="health"]       .addon-badge {{ background: #c84a3e; color: #f1ede5; }}  /* Mars */
.addon-section[data-domain="spiritual"]    .addon-badge {{ background: #c8843f; color: #1a1208; }}  /* Ketu */
.addon-section[data-domain="foreign"]      .addon-badge {{ background: #8b8d92; color: #f1ede5; }} /* Rahu */
.addon-section[data-domain="education"]    .addon-badge {{ background: #3d8b6e; color: #f1ede5; }} /* Mercury */
.addon-section[data-domain="property"]     .addon-badge {{ background: #9d7bb8; color: #f1ede5; }} /* Saturn */
.addon-section[data-domain="business"]     .addon-badge {{ background: #3d8b6e; color: #f1ede5; }} /* Mercury */
.addon-section[data-domain="muhurta"]      .addon-badge {{ background: #d6dadf; }}  /* Moon */
.addon-section[data-domain="gem"]          .addon-badge {{ background: #c9a5a5; }}  /* Venus (gem-karaka) */
.addon-section[data-domain="children"]     .addon-badge {{ background: #d4a843; }}  /* Jupiter (putra-karaka) */
.addon-section[data-domain="past_5"]       .addon-badge {{ background: #9d7bb8; color: #f1ede5; }}
.addon-section[data-domain="next_5"]       .addon-badge {{ background: #d4a843; }}
.addon-section[data-domain="lifetime"]     .addon-badge {{ background: #e6c98a; }}

/* ── TABLE OF CONTENTS ── */
.toc-page {{
    margin-top: 0;
    page-break-before: always;
    page-break-after: always;
}}
.toc-h2 {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 24pt;
    font-weight: 500;
    color: #c9a96e;
    margin: 0 0 0.5em 0;
    padding-bottom: 0.35em;
    border-bottom: 1px solid #c9a96e;
    letter-spacing: -0.3px;
}}
.toc-intro {{
    font-style: italic;
    color: #aaa;
    text-align: left;
    margin: 0 0 28pt 0;
    font-size: 10pt;
    line-height: 1.6;
}}
.toc-grid {{
    /* simple flowing list — WeasyPrint multi-column would be neater but
       brittle across runs; keep it predictable. */
}}
.toc-group {{
    margin: 0 0 24pt 0;
    page-break-inside: avoid;
}}
.toc-group-label {{
    font-family: 'Inter', sans-serif;
    font-size: 8.5pt;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #c9a96e;
    margin: 0 0 8pt 0;
    padding-bottom: 4pt;
    border-bottom: 0.5pt solid rgba(201, 169, 110, 0.45);
}}
.toc-item {{
    display: block;
    padding: 5pt 0;
    border-bottom: 0.4pt solid rgba(201, 169, 110, 0.12);
}}
.toc-title {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-size: 12.5pt;
    color: #e8e2d0;
    letter-spacing: 0.2px;
}}

/* ── INLINE EDUCATIONAL DIAGRAM CARDS (the "school science book" style) ── */
.diagram-card {{
    background: rgba(255, 255, 255, 0.025);
    border: 0.5pt solid rgba(201, 169, 110, 0.30);
    border-radius: 3px;
    padding: 8pt 14pt 10pt 14pt;
    margin: 10pt 0;
    page-break-inside: avoid;
    break-inside: avoid;
}}
.diagram-card-title {{
    font-family: 'Cormorant Garamond', 'Georgia', serif;
    font-style: italic;
    font-size: 11.5pt;
    color: #c9a96e;
    text-align: center;
    margin: 0 0 5pt 0;
    letter-spacing: 0.3px;
}}
.diagram-card-body {{
    text-align: center;
    margin: 2pt 0 4pt 0;
}}
.diagram-card-caption {{
    font-size: 9pt;
    line-height: 1.55;
    color: #b0b0b0;
    text-align: left;
    margin-top: 6pt;
    padding-top: 6pt;
    border-top: 0.3pt solid rgba(201, 169, 110, 0.18);
    font-style: italic;
}}
.diagram-legend {{
    margin-top: 8pt;
    text-align: center;
    font-size: 7.5pt;
}}
.legend-chip {{
    display: inline-block;
    padding: 2pt 6pt;
    margin: 2pt;
    border-radius: 8pt;
    color: #d4d4d4;
    letter-spacing: 0.3px;
    font-family: 'Inter', sans-serif;
}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def markdown_to_pdf(
    markdown_text: str,
    output_path: str | Path | None = None,
    title: str = "108 Life Reading",
    chart_data: dict | None = None,
) -> bytes:
    """Render Markdown to a branded dark-mode PDF.

    Args:
        markdown_text: The full report Markdown.
        output_path: If given, write PDF to this path AND return bytes.
        title: HTML <title> tag content.
        chart_data: Optional output of collect_chart_data(). If provided,
            chart wheel + dasha pyramid + navagrahas + houses pages are
            appended after Sources & Method.

    Returns:
        PDF as bytes.
    """
    md = MarkdownIt("commonmark", {"breaks": True, "html": True}).enable("table")
    body_html = md.render(markdown_text)

    body_html = body_html.replace(
        "<p><em>Generated",
        '<p class="footer-credit"><em>Generated',
    )

    # If chart_data is provided, do two things when the markdown carries the
    # corresponding sections (legacy markdowns may have stale baked-in data):
    #   1) Replace the entire "## Your Birth Chart" block with a fresh
    #      template-generated wheel + planet table from the live chart_data.
    #   2) Inject educational diagram cards right after "How to Read This
    #      Report" — what the SECTION_RENDERERS pipeline would inject.
    if chart_data:
        import re

        # ── 1) Replace stale Birth Chart block ────────────────────────────────
        try:
            from packages.report.src.templates import section_your_chart

            fresh_chart = section_your_chart(chart_data)
            # Convert the fresh markdown-flavored block through markdown-it too
            fresh_chart_html = (
                MarkdownIt("commonmark", {"breaks": True, "html": True})
                .enable("table")
                .render(fresh_chart)
            )
            chart_pattern = re.compile(
                r"<h2[^>]*>Your Birth Chart</h2>.*?(?=<h2|<hr|$)",
                re.DOTALL,
            )
            if chart_pattern.search(body_html):
                body_html = chart_pattern.sub(fresh_chart_html, body_html, count=1)
        except Exception as e:
            logger.warning(f"Failed to replace Birth Chart block: {e}")
        # ── 2) Inject educational concept cards after "How to Read This Report"
        # ONLY if the markdown didn't already carry them (render_markdown's
        # reference_primer section embeds them). This backfill is for legacy
        # markdowns that lack the diagrams — skip when already present to avoid
        # rendering every diagram twice.
        try:
            if "diagram-card" not in body_html:
                from packages.report.src.templates import _inline_concept_cards

                cards_html = _inline_concept_cards(chart_data)
                anchor = re.search(r"<h2[^>]*>How to Read This Report</h2>", body_html)
                if anchor:
                    cut = anchor.end()
                    body_html = body_html[:cut] + "\n" + cards_html + "\n" + body_html[cut:]
        except Exception as e:
            logger.warning(f"Failed to inject concept cards: {e}")
        # ── 2b) Replace any stale "Antardasha (until DATE)" / "Pratyantardasha
        # (until DATE)" cells in cover/intro tables — keep these aligned with
        # live chart_data so the cover never says "Ketu (until 2026-05-22)"
        # after Ketu has ended.
        try:
            cur = chart_data.get("dasha", {}).get("current", {})
            md_lord_t = cur.get("mahadasha", {}).get("lord", "").title()
            md_end = str(cur.get("mahadasha", {}).get("end_date", ""))[:10]
            ad_lord_t = cur.get("antardasha", {}).get("lord", "").title()
            ad_end = str(cur.get("antardasha", {}).get("end_date", ""))[:10]
            # Anchor on the row LABEL (Mahadasha / Antardasha) so we replace
            # the right row regardless of what stale value was baked in.
            if md_lord_t and md_end:
                body_html = re.sub(
                    r"(<td>\s*Mahadasha\s*</td>\s*<td>)[^<]+(</td>)",
                    rf"\g<1>{md_lord_t} (until {md_end})\g<2>",
                    body_html,
                    count=1,
                )
            if ad_lord_t and ad_end:
                body_html = re.sub(
                    r"(<td>\s*Antardasha\s*</td>\s*<td>)[^<]+(</td>)",
                    rf"\g<1>{ad_lord_t} (until {ad_end})\g<2>",
                    body_html,
                    count=1,
                )
        except Exception as e:
            logger.warning(f"Failed to refresh AD/PD cells: {e}")
        # ── 3) Replace any baked-in dasha pyramid bars with a fresh 3-level
        # pyramid (MD/AD/PD) computed from live chart_data.
        try:
            cur = chart_data.get("dasha", {}).get("current", {})
            md_l = cur.get("mahadasha", {}).get("lord", "")
            ad_l = cur.get("antardasha", {}).get("lord", "")
            pd_l = cur.get("pratyantardasha", {}).get("lord", "")
            if md_l and ad_l and pd_l:
                # Lord → navagraha color
                colors = {
                    "sun": "#ff8c00",
                    "moon": "#c0d4ed",
                    "mars": "#dc2626",
                    "mercury": "#22c55e",
                    "jupiter": "#facc15",
                    "venus": "#f9a8d4",
                    "saturn": "#7c3aed",
                    "rahu": "#9ca3af",
                    "ketu": "#a16207",
                }

                def _bar(width: int, color: str, label: str) -> str:
                    text_col = "#0a0a0a" if color in {"#facc15", "#f9a8d4", "#c0d4ed"} else "#fff"
                    return (
                        f'<div style="width:{width}%;margin:0 auto;background:{color};'
                        f"opacity:0.94;padding:9pt 10pt;border-bottom:1px solid "
                        f"rgba(0,0,0,0.4);font-family:Inter,sans-serif;"
                        f"font-size:10.5pt;font-weight:600;letter-spacing:1.5px;"
                        f'color:{text_col};text-align:center;">{label}</div>'
                    )

                fresh_pyramid = (
                    '<div class="dasha-pyramid" style="margin:14pt 0 8pt 0;">'
                    + _bar(
                        100,
                        colors.get(md_l, "#888"),
                        f"MD &middot; {md_l.title()} &middot; Mahadasha",
                    )
                    + _bar(
                        82,
                        colors.get(ad_l, "#888"),
                        f"AD &middot; {ad_l.title()} &middot; Antardasha",
                    )
                    + _bar(
                        64,
                        colors.get(pd_l, "#888"),
                        f"PD &middot; {pd_l.title()} &middot; Pratyantar",
                    )
                    + '<div style="text-align:center;margin-top:8pt;">'
                    '<span style="color:#fff;font-size:14pt;">&#x25BC;</span>'
                    '<div style="color:#aaa;font-style:italic;'
                    "font-family:Cormorant Garamond,serif;font-size:10pt;"
                    'margin-top:2pt;">this exact moment in your life</div></div></div>'
                )
                body_html = re.sub(
                    r'<div class="dasha-pyramid"[^>]*>.*?</div>\s*</div>',
                    fresh_pyramid,
                    body_html,
                    count=1,
                    flags=re.DOTALL,
                )
        except Exception as e:
            logger.warning(f"Failed to replace dasha pyramid: {e}")
        # ── 4) Inject Life Story Spine right BEFORE "The Architecture" — it
        # serves as the predictive headline page (current situation + active
        # windows + 20-year slow-transit calendar) sitting between the chart
        # primer and the narrative chapters.
        try:
            from packages.report.src.templates import section_life_story_spine

            # Skip if render_markdown already emitted the spine (life_story_spine
            # section) — otherwise it renders twice.
            spine_md = (
                "" if "life-story-spine" in body_html else section_life_story_spine(chart_data)
            )
            if spine_md:
                spine_html = (
                    '<h2 class="addon-h2">Your Life Story — What, When, Why</h2>\n' + spine_md
                )
                # Place before "The Architecture" (or any first body-section H2 if
                # that anchor isn't present)
                arch = re.search(r"<h2[^>]*>The Architecture</h2>", body_html)
                if arch is None:
                    arch = re.search(
                        r"<h2[^>]*>(Where You Came From|The Years You\'re In)</h2>",
                        body_html,
                    )
                if arch:
                    cut = arch.start()
                    body_html = body_html[:cut] + spine_html + "\n" + body_html[cut:]
        except Exception as e:
            logger.warning(f"Failed to inject Life Story Spine: {e}")

    # Mark add-on sections so they're visually distinct from base report.
    # Each H2 like "<h2>Add-on: Career & Money Deep-Dive</h2>" becomes a
    # badge-led H2 inside a class-wrapped div. The wrap-back-up of the
    # div is handled by closing before the NEXT H2 (or end of body).
    body_html = _mark_addon_sections(body_html)

    # Colorize planet names throughout the body content (NOT inside diagrams)
    body_html = _colorize_planets(body_html)

    # Customer name flows through to the @bottom-center footer so every page
    # past the cover reads as personalized (e.g. "Kirti Dubey").
    customer_name = ""
    if chart_data:
        try:
            customer_name = (chart_data.get("birth") or {}).get("full_name", "") or ""
        except Exception:
            customer_name = ""

    # v12: validator pre-render — print findings as a non-blocking note so the
    # operator sees them in the console (errors don't stop the render; the
    # operator decides whether to ship). For pipeline integration, call
    # validate_all_sections() directly and gate the render.
    if chart_data:
        try:
            import os as _os

            from packages.report.src.validator import format_validator_report, validate_all_sections

            sections_dir = _os.environ.get("REPORT_SECTIONS_DIR")
            if sections_dir and Path(sections_dir).is_dir():
                val = validate_all_sections(sections_dir, chart_data)
                logger.info(
                    "Pre-render validator: %s",
                    "PASS" if val["ok"] else f"FAIL ({val['errors']} errors)",
                )
                if not val["ok"] or val["warnings"] > 0:
                    print(format_validator_report(val))
        except Exception as e:
            logger.debug(f"Pre-render validator skipped: {e}")

    full_html = _HTML_TEMPLATE.format(title=title, body=body_html, customer_name=customer_name)

    pdf_bytes = HTML(string=full_html).write_pdf()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pdf_bytes)
        logger.info(f"PDF written: {path} ({len(pdf_bytes):,} bytes)")

    return pdf_bytes


def render_report_pdf(
    markdown_path: str | Path,
    output_path: str | Path | None = None,
    chart_data: dict | None = None,
) -> Path:
    md_path = Path(markdown_path)
    if output_path is None:
        output_path = md_path.with_suffix(".pdf")
    output_path = Path(output_path)
    title = md_path.stem.replace("_FULL_v4", "").replace("_", " ").title() + " — 108 Reading"
    markdown_text = md_path.read_text()
    markdown_to_pdf(markdown_text, output_path=output_path, title=title, chart_data=chart_data)
    return output_path
