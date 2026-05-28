"""v12 Validator — fact-checks all section narratives against the dossier
BEFORE the stitcher pass, catching false yoga claims and contradictions.

Runs as a single Python function (no LLM call needed for the regex layer).
For deeper LLM-grade contradiction checking, see `lvalidate_with_agent()`
which can be invoked separately.

Findings format:
    [(section_id, severity, finding_text), ...]
    severity ∈ {"error", "warning", "info"}
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# ── Hard rules (always-applies, regardless of chart) ──

_HARD_FORBIDDEN_PHRASES = [
    # Banned v11 voice slips
    ("the universe wants", "warning", "Banned phrase: 'the universe wants ...'"),
    ("trust the process", "warning", "Banned phrase: 'trust the process'"),
    ("old soul", "warning", "Banned phrase: 'old soul'"),
    ("shadow work", "warning", "Banned phrase: 'shadow work'"),
    ("inner child", "warning", "Banned phrase: 'inner child'"),
    # Technical jargon leaks
    (r"BAV\s+\d+\s*/\s*\d+", "error", "Raw BAV bindu count leaked"),
    (r"Vimshopaka.{0,15}\d+\s*%", "error", "Raw Vimshopaka percentage leaked"),
    (r"Shadbala.{0,15}\d+\s*virupa", "error", "Raw Shadbala virupa count leaked"),
    (r"Sudarshana\s+(wheel\s+)?\d+\s*[/of]+\s*3", "error", "Raw Sudarshana fraction leaked"),
    # Date format inconsistency
    (r"\b20\d{2}-\d{2}-\d{2}\b", "warning", "ISO date format used (should be 'Mon DD, YYYY')"),
]


def _validate_section(
    section_id: str,
    text: str,
    fact_check: dict[str, Any],
    chart_data: dict[str, Any],
) -> list[tuple[str, str, str]]:
    """Return list of (section_id, severity, finding) for this one section."""
    findings: list[tuple[str, str, str]] = []
    lowered = text.lower()

    # 1. Hard-banned phrases
    for needle, sev, msg in _HARD_FORBIDDEN_PHRASES:
        if needle.startswith(("\\", "[")) or "\\" in needle:
            # regex
            if re.search(needle, text, flags=re.IGNORECASE):
                findings.append((section_id, sev, msg))
        else:
            if needle in lowered:
                findings.append((section_id, sev, msg))

    # 2. False yoga claims (cross-check against FACT CHECK / detected yogas)
    _detected_yogas = {
        (y.get("name") if isinstance(y, dict) else str(y)).lower()
        for y in (chart_data.get("yogas") or [])
    }
    forbidden_yogas = fact_check.get("forbidden_yogas", [])

    # If a forbidden yoga is mentioned positively, flag it
    for yoga_label in forbidden_yogas:
        yoga_name = yoga_label.split("(")[0].strip().lower()
        # Match "Hamsa Yoga" / "Hamsa yoga" / "Hamsa" anywhere
        pattern = rf"\b{re.escape(yoga_name)}\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(
                (
                    section_id,
                    "error",
                    f"Claims {yoga_label!r} which DOES NOT fire for this chart (per FACT CHECK)",
                )
            )

    # 3. Mangal Dosha claim must match FACT CHECK status
    mangal_status = fact_check.get("mangal_status")  # "active" / "cancelled" / "not_firing"
    has_mangal_mention = (
        "mangal dosha" in lowered or "kuja dosha" in lowered or "manglik" in lowered
    )
    if has_mangal_mention:
        if mangal_status == "not_firing":
            findings.append(
                (
                    section_id,
                    "error",
                    "Mentions Mangal Dosha but FACT CHECK says it does NOT fire for this chart",
                )
            )
        elif mangal_status == "cancelled":
            # Must explicitly say cancelled or mitigated — not flagged as active friction
            cancellation_mentioned = any(
                w in lowered
                for w in (
                    "cancelled",
                    "canceled",
                    "neutralized",
                    "mitigated",
                    "not a curse",
                    "doesn't apply",
                    "does not apply",
                    "does not fire",
                    "no longer",
                )
            )
            if not cancellation_mentioned and section_id == "structural_challenges":
                findings.append(
                    (
                        section_id,
                        "warning",
                        "Mentions Mangal Dosha as friction but FACT CHECK says it's CANCELLED — should explain cancellation",
                    )
                )

    # 4. Sade Sati claim must match
    sade_active = fact_check.get("sade_sati_active", False)
    has_sade_mention = "sade sati" in lowered
    if has_sade_mention and not sade_active:
        # Allow: "no Sade Sati", "not currently in Sade Sati"
        negated = bool(
            re.search(
                r"(no|not|without|outside|absent|isn'?t|not currently in|not active)[^.]{0,40}sade sati",
                lowered,
            )
        )
        if not negated:
            findings.append(
                (
                    section_id,
                    "warning",
                    "Mentions Sade Sati positively but it's not active for this chart",
                )
            )

    # 5. Sanskrit jargon without inline gloss (sample check on first occurrence)
    JARGON = [
        "atmakaraka",
        "amatyakaraka",
        "putrakaraka",
        "darakaraka",
        "karakamsha",
        "sudarshana",
        "bhrigu bindu",
        "indu lagna",
        "vimshopaka",
        "shadbala",
        "ashtakavarga",
    ]
    for term in JARGON:
        if term in lowered:
            # Look for a gloss within ~60 chars after first mention
            idx = lowered.find(term)
            window = text[idx : idx + 80 + len(term)]
            has_gloss = any(c in window for c in ("—", "(", "-")) or " = " in window
            if not has_gloss:
                findings.append(
                    (
                        section_id,
                        "info",
                        f"Sanskrit term {term!r} used without inline gloss on first occurrence",
                    )
                )

    # 6. Section length — soft caps (v12 wants 300-500 typical, 700+ is bloat)
    word_count = len(text.split())
    if word_count > 1100:
        findings.append(
            (
                section_id,
                "warning",
                f"Section is {word_count} words — over the 700-1000 soft cap. Trim.",
            )
        )
    elif word_count < 100:
        findings.append((section_id, "warning", f"Section is only {word_count} words — too short."))

    return findings


def _build_fact_check_summary(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Extract the FACT CHECK structured truths the validator compares against."""
    natal = chart_data.get("natal_planets_dict") or {}
    sv = chart_data.get("state_vector") or {}
    sade = sv.get("sade_sati") or {}

    # Determine forbidden yogas (re-runs the same checks gather_classical_fact_check does)
    forbidden: list[str] = []
    if "jupiter" in natal:
        jup_sign = int(float(natal["jupiter"]["longitude"]) // 30)
        lagna_sign = chart_data.get("lagna", {}).get("rashi_idx", 0)
        jup_house = ((jup_sign - lagna_sign) % 12) + 1
        if not (jup_sign in (8, 11, 3) and jup_house in (1, 4, 7, 10)):
            forbidden.append("Hamsa Yoga")
    if "moon" in natal and "jupiter" in natal:
        moon_sign = int(float(natal["moon"]["longitude"]) // 30)
        jup_sign = int(float(natal["jupiter"]["longitude"]) // 30)
        if ((moon_sign - jup_sign) % 12) + 1 not in (1, 4, 7, 10):
            forbidden.append("Gajakesari Yoga")

    # Mangal Dosha status — use the FACT CHECK detection (which has cancellation
    # logic), NOT the legacy chart_data['doshas'] list (which doesn't always
    # surface cancelled doshas).
    from packages.report.src.knowledge_gatherer import _mangal_dosha_check

    try:
        mangal = _mangal_dosha_check(chart_data)
        if not mangal.get("active"):
            mangal_status = "not_firing"
        elif mangal.get("is_cancelled"):
            mangal_status = "cancelled"
        else:
            mangal_status = "active"
    except Exception:
        # Fallback to legacy reading
        detected_doshas = chart_data.get("doshas") or []
        m = next((d for d in detected_doshas if "mangal" in d.get("name", "").lower()), None)
        if m is None:
            mangal_status = "not_firing"
        elif m.get("is_cancelled"):
            mangal_status = "cancelled"
        else:
            mangal_status = "active"

    return {
        "forbidden_yogas": forbidden,
        "mangal_status": mangal_status,
        "sade_sati_active": bool(sade.get("active")),
        "detected_yoga_names": [
            (y.get("name") if isinstance(y, dict) else str(y))
            for y in (chart_data.get("yogas") or [])
        ],
    }


def validate_all_sections(
    sections_dir: str | Path,
    chart_data: dict[str, Any],
) -> dict[str, Any]:
    """Validate every .md file in sections_dir against the chart's FACT CHECK.

    Returns a structured report dict:
        {
          "ok": bool,
          "errors": int,
          "warnings": int,
          "infos": int,
          "findings": [(section_id, severity, message), ...],
          "by_section": {section_id: [(severity, message), ...]},
        }
    """
    sections_dir = Path(sections_dir)
    fact_check = _build_fact_check_summary(chart_data)
    all_findings: list[tuple[str, str, str]] = []
    by_section: dict[str, list[tuple[str, str]]] = {}

    for md_file in sorted(sections_dir.glob("*.md")):
        if md_file.stem.startswith("_"):  # skip _stitcher.md etc.
            continue
        text = md_file.read_text()
        findings = _validate_section(md_file.stem, text, fact_check, chart_data)
        all_findings.extend(findings)
        by_section[md_file.stem] = [(sev, msg) for _, sev, msg in findings]

    counts = {"error": 0, "warning": 0, "info": 0}
    for _, sev, _ in all_findings:
        counts[sev] = counts.get(sev, 0) + 1

    return {
        "ok": counts["error"] == 0,
        "errors": counts["error"],
        "warnings": counts["warning"],
        "infos": counts["info"],
        "findings": all_findings,
        "by_section": by_section,
        "fact_check": fact_check,
    }


def format_validator_report(result: dict[str, Any]) -> str:
    """Pretty-print the validator output for operator console."""
    lines = [
        "═══════════════════════════════════════════════════════════════",
        f"VALIDATOR REPORT — {'PASS' if result['ok'] else 'FAIL'} "
        f"({result['errors']} errors, {result['warnings']} warnings, {result['infos']} infos)",
        "═══════════════════════════════════════════════════════════════",
    ]
    by_section = result.get("by_section") or {}
    for sid in sorted(by_section.keys()):
        findings = by_section[sid]
        if not findings:
            continue
        lines.append(f"\n[{sid}]")
        for sev, msg in findings:
            tag = {"error": "❌", "warning": "⚠ ", "info": "  "}.get(sev, "  ")
            lines.append(f"  {tag} {msg}")
    if not any(by_section.values()):
        lines.append("\n  All sections passed validation. ✓")
    return "\n".join(lines)
