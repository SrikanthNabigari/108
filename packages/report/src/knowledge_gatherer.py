"""Knowledge gatherer for narrative prompts.

For each report section, pulls the relevant slices of the 108 knowledge base
(BPHS interpretations, dasha effects, yoga descriptions, planet-in-house,
planet-in-sign, planet-in-nakshatra, house-lord-in-house) and returns them
as a structured "REFERENCE MATERIAL" block to inject into the LLM prompt.

This is the layer that turns "LLM uses general training" into "LLM uses YOUR
classical knowledge base." Without this, narratives are generic. With this,
they are grounded in BPHS / Phaladeepika / Jaimini specifics for the actual
chart in front of us.
"""

from __future__ import annotations

import logging
from typing import Any

from packages.core.src.knowledge_loader import (
    get_antardasha_effects,
    get_dasha_guide,
    get_dosha_rules,
    get_house_lord_in_house_interpretations,
    get_planet_in_house_interpretations,
    get_planet_in_nakshatra_interpretations,
    get_planet_in_sign_interpretations,
    get_pratyantardasha_effects,
    get_yoga_rules,
)
from packages.cosmos.src.divisional import (
    get_divisional_chart,
)

logger = logging.getLogger(__name__)

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


# ── Cached knowledge loaders ──
_pin_house: dict[str, Any] | None = None
_pin_sign: dict[str, Any] | None = None
_pin_nak: dict[str, Any] | None = None
_lord_in_house: dict[str, Any] | None = None
_dasha_guide_cache: dict[str, Any] | None = None
_yoga_master: dict[str, Any] | None = None
_dosha_master: dict[str, Any] | None = None


def _ensure_loaded() -> None:
    global _pin_house, _pin_sign, _pin_nak, _lord_in_house
    global _dasha_guide_cache, _yoga_master, _dosha_master
    try:
        if _pin_house is None:
            _pin_house = get_planet_in_house_interpretations().get("planet_in_house", {})
        if _pin_sign is None:
            _pin_sign = get_planet_in_sign_interpretations().get("planet_in_sign", {})
        if _pin_nak is None:
            _pin_nak = get_planet_in_nakshatra_interpretations().get("planet_in_nakshatra", {})
        if _lord_in_house is None:
            _lord_in_house = get_house_lord_in_house_interpretations()
        if _dasha_guide_cache is None:
            _dasha_guide_cache = get_dasha_guide().get("dasha_guide", {})
        if _yoga_master is None:
            _yoga_master = get_yoga_rules()
        if _dosha_master is None:
            _dosha_master = get_dosha_rules()
    except Exception as e:  # pragma: no cover
        logger.warning(f"Knowledge load failed: {e}")


# ── Per-placement lookups ──


def lookup_planet_in_house(planet: str, house: int) -> dict[str, Any]:
    _ensure_loaded()
    key = f"{planet.lower()}_in_house_{house}"
    return (_pin_house or {}).get(key, {})


def lookup_planet_in_sign(planet: str, sign_idx: int) -> dict[str, Any]:
    _ensure_loaded()
    sign = _RASHI[sign_idx % 12]
    key = f"{planet.lower()}_in_{sign}"
    return (_pin_sign or {}).get(key, {})


def lookup_planet_in_nakshatra(planet: str, nakshatra_name: str) -> dict[str, Any]:
    _ensure_loaded()
    # Nakshatra names in JSON are lowercase + underscored
    nak_norm = nakshatra_name.lower().replace(".", "").replace(" ", "_")
    key = f"{planet.lower()}_in_{nak_norm}"
    result = (_pin_nak or {}).get(key, {})
    if not result:
        # Try variant: "p.bhadrapada" vs "purva_bhadrapada"
        variants = {
            "p_bhadrapada": "purva_bhadrapada",
            "u_bhadrapada": "uttara_bhadrapada",
            "p_phalguni": "purva_phalguni",
            "u_phalguni": "uttara_phalguni",
            "p_ashadha": "purva_ashadha",
            "u_ashadha": "uttara_ashadha",
        }
        if nak_norm in variants:
            key2 = f"{planet.lower()}_in_{variants[nak_norm]}"
            result = (_pin_nak or {}).get(key2, {})
    return result


def lookup_house_lord_in_house(lord_house: int, sits_in_house: int) -> dict[str, Any]:
    _ensure_loaded()
    key = f"lord_{lord_house}_in_house_{sits_in_house}"
    # The JSON has a top-level "house_lord_in_house" wrapper key — handle both shapes.
    cache = _lord_in_house or {}
    if "house_lord_in_house" in cache:
        cache = cache["house_lord_in_house"]
    return cache.get(key, {})


# ── Bhava (house) themes — used to convert "lord X in Y" into lived-experience prose ──
HOUSE_THEMES: dict[int, dict[str, str]] = {
    1: {"name": "self", "lived": "how you show up; body, identity, first impression"},
    2: {"name": "wealth/speech", "lived": "money you accumulate, family of origin, what you say"},
    3: {"name": "courage", "lived": "siblings, short journeys, the things you take initiative on"},
    4: {"name": "home", "lived": "mother, emotional foundation, property, sense of belonging"},
    5: {
        "name": "creativity",
        "lived": "children, romance, speculation, the work you do for its own sake",
    },
    6: {
        "name": "service",
        "lived": "daily work, enemies, illness, debts — the friction you serve through",
    },
    7: {"name": "partnership", "lived": "spouse, business partners, the public you face"},
    8: {
        "name": "transformation",
        "lived": "shared resources, inheritance, the long secrets, the things that change you",
    },
    9: {"name": "dharma", "lived": "father, fortune, higher teaching, the meaning you live by"},
    10: {"name": "career", "lived": "public reputation, profession, what the world knows you for"},
    11: {"name": "gains", "lived": "friends, networks, dreams realised, money flowing in"},
    12: {
        "name": "moksha",
        "lived": "dissolution, foreign lands, hidden enemies, sleep, what releases you",
    },
}

# Sign lordships — the planet ruling each rashi (0-indexed Aries → Pisces)
SIGN_LORDS_IDX: dict[int, str] = {
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


def lookup_dasha_guide(planet: str) -> dict[str, Any]:
    _ensure_loaded()
    return (_dasha_guide_cache or {}).get(planet.lower(), {})


def lookup_md_ad(md_lord: str, ad_lord: str) -> dict[str, Any]:
    """Get classical MD-AD effects (81 combinations)."""
    try:
        all_eff = get_antardasha_effects()
        return all_eff.get(md_lord.lower(), {}).get(ad_lord.lower(), {})
    except Exception:
        return {}


def lookup_md_ad_pd(md: str, ad: str, pd: str) -> dict[str, Any]:
    """Get classical MD-AD-PD effects (729 combinations)."""
    try:
        all_eff = get_pratyantardasha_effects()
        return all_eff.get(md.lower(), {}).get(ad.lower(), {}).get(pd.lower(), {})
    except Exception:
        return {}


# ── Section-aware gatherers ──


def _format_lookup(label: str, data: dict[str, Any], keys: list[str]) -> str:
    """Compact one-block formatter for a knowledge lookup."""
    if not data:
        return ""
    lines = [f"  {label}:"]
    for k in keys:
        v = data.get(k)
        if isinstance(v, str) and v.strip():
            lines.append(f"    {k}: {v.strip()[:300]}")
        elif isinstance(v, list) and v:
            lines.append(f"    {k}: {', '.join(str(x) for x in v[:6])}")
    return "\n".join(lines) if len(lines) > 1 else ""


def gather_for_arc_so_far(chart_data: dict[str, Any]) -> str:
    """Reference material for Section 2 — past/present dasha narrative."""
    natal = chart_data["natal_planets_dict"]
    md_seq = chart_data["dasha"]["mahadasha_sequence"][:5]
    blocks: list[str] = ["=== DASHA-PERIOD KNOWLEDGE (BPHS / Dasha Guide) ==="]

    for md in md_seq:
        lord = md["lord"]
        natal_house = natal.get(lord, {}).get("house", 0)
        # Dasha guide
        dg = lookup_dasha_guide(lord)
        block = (
            f"\n[{lord.upper()} MD: {md['start'][:7]} to {md['end'][:7]}, {md['years']:.1f}y]\n"
            f"  Theme: {dg.get('theme', '')}\n"
            f"  Career: {dg.get('career', '')[:200]}\n"
            f"  Practical: {dg.get('practical_advice', '')[:200]}\n"
        )
        if natal_house:
            ph = lookup_planet_in_house(lord, natal_house)
            block += (
                f"  Natal: {lord.title()} sits in your H{natal_house}\n"
                f"  Effect: {ph.get('summary', '')[:200]}\n"
            )
        blocks.append(block)
    return "\n".join(blocks)


def gather_for_where_you_are_now(chart_data: dict[str, Any]) -> str:
    """Reference material for Section 3 — current dasha + sade sati specifics."""
    cur = chart_data["dasha"]["current"]
    md_lord = cur["mahadasha"]["lord"]
    ad_lord = cur["antardasha"]["lord"]
    _pd_lord = cur["pratyantardasha"]["lord"]
    natal = chart_data["natal_planets_dict"]
    sv = chart_data["state_vector"]

    blocks: list[str] = ["=== CURRENT-PERIOD KNOWLEDGE ==="]

    # Dasha guide for MD
    dg_md = lookup_dasha_guide(md_lord)
    blocks.append(
        f"\n[MAHADASHA: {md_lord.upper()}]\n"
        f"  Theme: {dg_md.get('theme', '')}\n"
        f"  Focus areas: {', '.join(dg_md.get('focus_areas', [])[:5])}\n"
        f"  Career: {dg_md.get('career', '')[:200]}\n"
        f"  Health: {dg_md.get('health', '')[:200]}\n"
        f"  Finance: {dg_md.get('finances', '')[:200]}\n"
    )

    # Antardasha (MD x AD effects)
    md_ad = lookup_md_ad(md_lord, ad_lord)
    if md_ad:
        blocks.append(
            f"\n[ANTARDASHA: {md_lord.upper()}-{ad_lord.upper()}]\n"
            f"  General: {', '.join(md_ad.get('general_effects', [])[:3])}\n"
            f"  Positive: {', '.join(md_ad.get('positive', [])[:4])}\n"
            f"  Negative: {', '.join(md_ad.get('negative', [])[:4])}\n"
            f"  Career: {', '.join(md_ad.get('career_education', [])[:3])}\n"
            f"  Wealth: {', '.join(md_ad.get('wealth_family', [])[:3])}\n"
        )

    # Natal placement of MD lord (where it lives in chart)
    md_natal_house = natal.get(md_lord, {}).get("house", 0)
    if md_natal_house:
        ph = lookup_planet_in_house(md_lord, md_natal_house)
        if ph:
            blocks.append(
                f"\n[{md_lord.upper()} natal: H{md_natal_house}]\n"
                f"  Summary: {ph.get('summary', '')[:200]}\n"
                f"  Positive aspects: {', '.join(ph.get('positive', [])[:3])}\n"
                f"  Negative aspects: {', '.join(ph.get('negative', [])[:3])}\n"
            )

    # Sade Sati phase
    sade = sv.get("sade_sati", {})
    if sade.get("active"):
        blocks.append(
            f"\n[SADE SATI: {sade.get('phase', '?').upper()} phase]\n"
            f"  This is Saturn's 7.5-year challenge cycle. Phase '{sade.get('phase')}' "
            f"is the {'first' if sade.get('phase')=='rising' else 'second' if sade.get('phase')=='peak' else 'final'} "
            f"of three 2.5-year sub-phases. The setting phase is consolidation, not peak struggle.\n"
        )

    return "\n".join(blocks)


def gather_for_question(chart_data: dict[str, Any]) -> str:
    """Reference material for Section 4 — topic-aware chart slice."""
    q = (chart_data.get("user_question") or "").lower()
    natal = chart_data["natal_planets_dict"]
    sv = chart_data["state_vector"]

    # Topic detection (rough)
    topic = "general"
    if any(w in q for w in ["career", "job", "work", "business", "profession"]):
        topic = "career"
    elif any(
        w in q
        for w in [
            "money",
            "finance",
            "financial",
            "wealth",
            "income",
            "rich",
            "broke",
            "debt",
            "earn",
            "salary",
        ]
    ):
        topic = "finance"
    elif any(w in q for w in ["marriage", "spouse", "partner", "wife", "husband", "love"]):
        topic = "marriage"
    elif any(w in q for w in ["health", "illness", "disease", "body"]):
        topic = "health"
    elif any(w in q for w in ["family", "father", "mother", "parent", "home"]):
        topic = "family"
    elif any(w in q for w in ["spirit", "moksha", "dharma", "guru", "meditation"]):
        topic = "spiritual"
    elif any(w in q for w in ["travel", "foreign", "abroad", "journey"]):
        topic = "travel"

    # Topic → relevant houses
    topic_houses = {
        "career": [10, 6, 2],
        "finance": [2, 11, 5],
        "marriage": [7, 5, 11, 8],
        "health": [1, 6, 8],
        "family": [4, 2, 1],
        "spiritual": [9, 12, 5],
        "travel": [3, 9, 12],
        "general": [1, 5, 9, 10],
    }[topic]
    topic_karaka = {
        "career": "saturn",
        "finance": "jupiter",
        "marriage": "venus",
        "health": "sun",
        "family": "moon",
        "spiritual": "ketu",
        "travel": "rahu",
        "general": None,
    }[topic]

    blocks: list[str] = [f"=== TOPIC: {topic.upper()} (auto-detected from question) ==="]

    # Lord of each topic house, and where it sits
    lagna_idx = chart_data["lagna"]["rashi_idx"]
    from packages.cosmos.src.houses import SIGN_RULERS

    seen_lords = set()
    for h in topic_houses[:3]:
        lord_sign_idx = (lagna_idx + h - 1) % 12
        lord = SIGN_RULERS.get(lord_sign_idx)
        if not lord or lord in seen_lords:
            continue
        seen_lords.add(lord)
        lord_house = natal.get(lord, {}).get("house", 0)
        if not lord_house:
            continue
        lh = lookup_house_lord_in_house(h, lord_house)
        if lh:
            blocks.append(
                f"\n[Lord of H{h} ({lord.title()}) sits in H{lord_house}]\n"
                f"  Effect: {lh.get('summary', lh.get('effect', ''))[:250]}\n"
            )

    # Karaka analysis
    if topic_karaka:
        kar_house = natal.get(topic_karaka, {}).get("house", 0)
        if kar_house:
            ph = lookup_planet_in_house(topic_karaka, kar_house)
            if ph:
                blocks.append(
                    f"\n[Karaka {topic_karaka.upper()} for {topic}, sits in H{kar_house}]\n"
                    f"  Summary: {ph.get('summary', '')[:200]}\n"
                    f"  Career notes: {ph.get('career', '')[:150]}\n"
                )

    # Area score for the topic
    area = next((a for a in sv["areas"] if a["id"] == topic), None)
    if area:
        ns = area["natal_support"]
        blocks.append(
            f"\n[Area score for {topic.upper()}]\n"
            f"  Today: {area['score']:.1f}/10 ({area.get('insight','')})\n"
            f"  Natal support: {ns['score']:.1f}/10 (dispositor: {ns.get('dispositor','-')} in H{ns.get('dispositor_house','?')}, "
            f"argala active: {ns.get('argala_active_count',0)})\n"
        )

    return "\n".join(blocks)


def gather_for_what_to_do(chart_data: dict[str, Any]) -> str:
    """Reference material for Section 8 — actionable guidance."""
    cur = chart_data["dasha"]["current"]
    md_lord = cur["mahadasha"]["lord"]
    sv = chart_data["state_vector"]
    upcoming = chart_data.get("upcoming_events", [])[:5]

    blocks = ["=== ACTION KNOWLEDGE ==="]

    dg = lookup_dasha_guide(md_lord)
    blocks.append(
        f"\n[Practical advice for {md_lord.upper()} MD natives]\n"
        f"  {dg.get('practical_advice', '')[:400]}\n"
        f"  Suggested focus: {', '.join(dg.get('focus_areas', [])[:4])}\n"
    )

    top_area = max(sv["areas"], key=lambda x: x["score"])
    bot_area = min(sv["areas"], key=lambda x: x["score"])
    blocks.append(
        f"\n[Strongest area today: {top_area['name']} {top_area['score']:.1f}]\n"
        f"  Lean here. Insight: {top_area.get('insight','')}\n"
        f"\n[Weakest area today: {bot_area['name']} {bot_area['score']:.1f}]\n"
        f"  Avoid major moves here. Insight: {bot_area.get('insight','')}\n"
    )

    if upcoming:
        upc = "\n".join(
            f"  - {e.get('date','?')[:10]}: {e.get('type','?')} ({e.get('planet') or e.get('transit_planet','?')})"
            for e in upcoming
        )
        blocks.append(f"\n[Next 90-day triggers]\n{upc}")

    return "\n".join(blocks)


# ── Deep classical layers (for ALL profound-Jyotishi sections) ──


def gather_deep_chart_layers(chart_data: dict[str, Any]) -> str:
    """Return the multi-lens classical reading dossier.

    A profound Jyotishi reads through ALL these lenses simultaneously:
    - Vimshottari Dasha lord placement, dignity, lordship, conditions
    - Divisional charts (D9 Navamsa for marriage/strength, D10 Dasamsa for
      career, D24 Siddhamsha for education, D60 Shashtiamsha for past karma)
    - Jaimini overlay (Atmakaraka, Amatyakaraka, etc., Karakamsha, Argala)
    - Ashtakavarga bindus per dasha lord (8-bindu system)
    - Shadbala 6 components (positional, temporal, motional, etc.)
    - Vargottama planets (same sign in D1 and D9 = double strength)
    - Combustion / retrograde / planetary war status
    - Nadi readings (planetary conjunctions in same sign)

    Returns one consolidated dossier block for injection into ANY agent prompt.
    """
    from packages.context.src.state_engine import _build_birth_chart

    natal = chart_data["natal_planets_dict"]
    lagna_idx = chart_data["lagna"]["rashi_idx"]
    moon_lon = chart_data["moon"]["longitude"]
    cur_md_lord = chart_data["dasha"]["current"]["mahadasha"]["lord"]
    cur_ad_lord = chart_data["dasha"]["current"]["antardasha"]["lord"]

    blocks: list[str] = ["=== DEEP CLASSICAL LAYERS (multi-lens dossier) ==="]

    # Build typed chart for advanced calculations
    try:
        from datetime import datetime

        birth_dt = datetime.fromisoformat(chart_data["birth"]["datetime"])
        chart = _build_birth_chart(
            birth_dt,
            chart_data["birth"]["lat"],
            chart_data["birth"]["lon"],
            natal,
            _RASHI[lagna_idx],
            _RASHI[int(moon_lon // 30) % 12],
            moon_lon,
        )
    except Exception as e:
        logger.warning(f"Chart build for deep layers failed: {e}")
        return "\n".join(blocks)

    # ── 1. Divisional chart positions (D9, D10, D24, D60) ──
    planet_lons = {p: float(d["longitude"]) for p, d in natal.items()}
    divisional_summary: list[str] = ["\n[DIVISIONAL CHARTS]"]
    for div_num, div_name, div_purpose in [
        (9, "D9 Navamsha", "marriage, dharma, planetary strength"),
        (10, "D10 Dasamsha", "career, public role, achievements"),
        (24, "D24 Siddhamsha", "education, learning capacity"),
        (60, "D60 Shashtiamsha", "past karma, deepest patterns"),
    ]:
        try:
            d_chart = get_divisional_chart(planet_lons, div_num)
            positions = d_chart.get("planets", {})
            divisional_summary.append(f"\n  {div_name} ({div_purpose}):")
            for p, pos in positions.items():
                if isinstance(pos, dict):
                    sign = pos.get("sign_name", pos.get("rashi_name", "?"))
                    divisional_summary.append(f"    {p}: {sign}")
        except Exception:
            continue
    blocks.append("\n".join(divisional_summary))

    # ── 2. Vargottama planets (D1 sign == D9 sign) ──
    try:
        d1_signs: dict[str, str] = {}
        d9_signs: dict[str, str] = {}
        d9 = get_divisional_chart(planet_lons, 9)
        for p, lon in planet_lons.items():
            d1_signs[p] = _RASHI[int(lon // 30) % 12]
        for p, pos in d9.get("planets", {}).items():
            if isinstance(pos, dict):
                d9_signs[p] = pos.get("sign_name", pos.get("rashi_name", "")).lower()
        vargottama = [p for p in d1_signs if d9_signs.get(p) == d1_signs[p]]
        if vargottama:
            blocks.append(
                f"\n[VARGOTTAMA PLANETS] (same sign in D1 and D9 — double strength)\n"
                f"  {', '.join(p.title() for p in vargottama)}"
            )
    except Exception:
        pass

    # ── 3. Combustion + Retrograde + Speed conditions ──
    conditions: list[str] = ["\n[PLANETARY CONDITIONS]"]
    sun_lon = planet_lons.get("sun", 0)
    for p, lon in planet_lons.items():
        if p == "sun":
            continue
        # Combustion check: distance from Sun
        diff = abs((lon - sun_lon + 180) % 360 - 180)
        combust_orb = {"mercury": 14, "venus": 10, "mars": 17, "jupiter": 11, "saturn": 15}.get(
            p, 10
        )
        flags = []
        if diff < combust_orb and p in combust_orb_planets():
            flags.append(f"COMBUST (orb {diff:.1f}°)")
        if natal.get(p, {}).get("is_retrograde"):
            flags.append("retrograde")
        if flags:
            conditions.append(f"  {p}: {', '.join(flags)}")
    if len(conditions) > 1:
        blocks.append("\n".join(conditions))

    # ── 4. Jaimini Chara Karakas ──
    try:
        from packages.self.src.jaimini import calculate_chara_karakas

        karakas = calculate_chara_karakas(chart)
        kar_lines = ["\n[CHARA KARAKAS] (Jaimini soul-significators)"]
        kar_role_meaning = {
            "atmakaraka": "soul, life-mission, deepest desire",
            "amatyakaraka": "career, advisor, mind",
            "bhratrikaraka": "siblings, courage, communication",
            "matrikaraka": "mother, comfort, education",
            "putrakaraka": "children, creativity, mantra",
            "gnatikaraka": "obstacles, illness, hidden enemies",
            "darakaraka": "spouse, relationships",
        }
        for k in karakas:
            kr = k.karaka.value
            kar_lines.append(
                f"  {kr.title():15s} = {k.planet.value.title():8s} "
                f"({k.degree_in_sign:.2f}° {k.rashi.value.title()}) "
                f"→ {kar_role_meaning.get(kr, '')}"
            )
        blocks.append("\n".join(kar_lines))
    except Exception as e:
        logger.debug(f"Chara karakas failed: {e}")

    # ── 5. Karakamsha (Atmakaraka in D9) ──
    try:
        from packages.self.src.jaimini import get_karakamsha

        km = get_karakamsha(chart)
        if km:
            blocks.append(
                f"\n[KARAKAMSHA] (Atmakaraka's D9 sign — your soul's chosen environment)\n"
                f"  Atmakaraka = {km.atmakaraka_planet.value.title()} "
                f"sits in {km.karakamsha_rashi.value.title()} in D9\n"
                f"  Themes: {', '.join(km.themes[:5]) if hasattr(km, 'themes') else ''}"
            )
    except Exception:
        pass

    # ── 6. Argala on key houses (1, 5, 7, 9, 10) ──
    try:
        from packages.self.src.jaimini import calculate_argala

        argala = calculate_argala(chart)
        arg_lines = ["\n[ARGALA] (Jaimini intervention/obstruction on key houses)"]
        for h in (1, 5, 7, 9, 10):
            entry = argala.get(h, {})
            active = entry.get("active_argala_count", 0)
            arg_lines.append(
                f"  H{h} ({entry.get('sign', '?').title()}): "
                f"{active}/4 argalas active — {entry.get('summary', '')}"
            )
        blocks.append("\n".join(arg_lines))
    except Exception:
        pass

    # ── 7. Ashtakavarga bindus for dasha lord (Bhinnashtakavarga) ──
    try:
        from packages.core.src.constants import Planet
        from packages.self.src.ashtakavarga import calculate_bhinnashtakavarga

        planet_enum_map = {p.value: p for p in Planet}
        ashta_lines = ["\n[ASHTAKAVARGA BINDUS — current dasha lords]"]
        for lord in [cur_md_lord, cur_ad_lord]:
            penum = planet_enum_map.get(lord.lower())
            if penum:
                bav = calculate_bhinnashtakavarga(penum, chart)
                # Score in dasha-lord's natal sign
                lord_lon = planet_lons.get(lord, 0)
                lord_sign = int(lord_lon // 30) % 12
                bindus_in_natal_sign = bav[lord_sign]
                total = sum(bav)
                ashta_lines.append(
                    f"  {lord.title():8s} BAV total: {total}/56  "
                    f"(in own natal sign {_RASHI[lord_sign].title()}: {bindus_in_natal_sign}/8 bindus)"
                )
        blocks.append("\n".join(ashta_lines))
    except Exception as e:
        logger.debug(f"Ashtakavarga failed: {e}")

    # ── 8. Shadbala for dasha lord (real 6-fold strength) ──
    try:
        from packages.self.src.strength import StrengthCalculator

        sc = StrengthCalculator()
        all_strengths = sc.get_all_planet_strengths(chart)
        sb_lines = ["\n[SHADBALA — six-fold strength]"]
        for lord in [cur_md_lord, cur_ad_lord]:
            s = all_strengths.get(lord, {})
            total = s.get("total", 0)
            req = s.get("required_minimum", 0)
            ratio = (total / req) if req > 0 else 0
            verdict = "STRONG" if ratio >= 1.0 else "moderate" if ratio >= 0.7 else "WEAK"
            sb_lines.append(
                f"  {lord.title():8s}: {total:.0f} virupas (need {req:.0f}) — {verdict}"
            )
        blocks.append("\n".join(sb_lines))
    except Exception as e:
        logger.debug(f"Shadbala failed: {e}")

    # ── 9. Nadi conjunctions (planets sharing a sign — most intense yoga form) ──
    try:
        from packages.self.src.chandra_kala_nadi import get_conjunctions, get_planet_sign_map

        sign_map = get_planet_sign_map(natal)
        conj = get_conjunctions(sign_map)
        if conj:
            conj_lines = ["\n[NADI CONJUNCTIONS — sign-sharing planets, most potent yoga form]"]
            for c in conj[:6]:
                planets = c.get("planets", [])
                sign = c.get("sign", "?")
                conj_lines.append(f"  {' + '.join(p.title() for p in planets)} in {sign.title()}")
            blocks.append("\n".join(conj_lines))
    except Exception:
        pass

    # Build natal_with_rashi: add 'rashi' field needed by Sudarshana & Indu Lagna
    natal_with_rashi: dict[str, dict[str, Any]] = {}
    for p, d in natal.items():
        lon = float(d.get("longitude", 0.0))
        sign_idx = int(lon // 30) % 12
        natal_with_rashi[p] = {
            **d,
            "rashi": _RASHI[sign_idx],
        }
    moon_rashi = _RASHI[int(moon_lon // 30) % 12]
    sun_lon = float(natal.get("sun", {}).get("longitude", 0.0))
    sun_rashi = _RASHI[int(sun_lon // 30) % 12]
    lagna_rashi = _RASHI[lagna_idx]

    # ── 10. SUDARSHANA CHAKRA — 3-lagna house confirmation ──
    try:
        from packages.self.src.sudarshana_chakra import analyze_house_from_three_wheels

        sud_lines = ["\n[SUDARSHANA CHAKRA — house confirmed by Lagna + Moon + Sun]"]
        sud_lines.append(
            "  Lens: a house is structurally LIVE when 2 of 3 wheels have planets there"
        )
        # Key life houses
        key_houses = [
            (1, "self"),
            (2, "wealth/speech"),
            (4, "home/comfort"),
            (5, "creativity/children"),
            (7, "marriage"),
            (9, "dharma/fortune"),
            (10, "career"),
            (11, "gains"),
        ]
        for h, theme in key_houses:
            res = analyze_house_from_three_wheels(
                h, lagna_rashi, moon_rashi, sun_rashi, natal_with_rashi
            )
            verdict = res["strength_note"]
            wheel_signals: list[str] = []
            for w in res["wheels"]:
                if w["occupied"]:
                    pts = "+".join(p.title()[:2] for p in w["planets_in_house"])
                    wheel_signals.append(f"{w['wheel']}:{pts}")
            signals_str = " | ".join(wheel_signals) if wheel_signals else "no planets in any wheel"
            sud_lines.append(
                f"  H{h:<2} ({theme}): {res['confirmation_count']}/3  {verdict}  [{signals_str}]"
            )
        blocks.append("\n".join(sud_lines))
    except Exception as e:
        logger.debug(f"Sudarshana failed: {e}")

    # ── 11. SENSITIVE POINTS — Bhrigu Bindu + Indu Lagna ──
    try:
        from packages.self.src.sensitive_points import (
            calculate_bhrigu_bindu,
            calculate_indu_lagna,
        )

        sp_lines = ["\n[SENSITIVE POINTS — calculated fortune triggers]"]
        rahu_lon = float(natal.get("rahu", {}).get("longitude", 0.0))
        bb = calculate_bhrigu_bindu(rahu_lon, moon_lon)
        # Compute the house Bhrigu Bindu falls in (from lagna)
        bb_sign_idx = int(bb["longitude"] // 30) % 12
        bb_house = ((bb_sign_idx - lagna_idx) % 12) + 1
        sp_lines.append(
            f"  Bhrigu Bindu (Rahu-Moon midpoint): {bb['sign'].title()} "
            f"{bb['degree_in_sign']:.2f}° → House {bb_house} from lagna. "
            f"Transit Jupiter or current dasha-lord crossing this point = major life event."
        )
        try:
            il = calculate_indu_lagna(natal_with_rashi, lagna_rashi)
            il_sign = il.get("indu_lagna_sign", "?")
            il_lord = il.get("indu_lagna_lord", "?")
            il_sign_idx = _RASHI.index(il_sign.lower()) if il_sign.lower() in _RASHI else -1
            il_house = ((il_sign_idx - lagna_idx) % 12) + 1 if il_sign_idx >= 0 else "?"
            sp_lines.append(
                f"  Indu Lagna (wealth lagna, BPHS Ch.35): {il_sign.title()} → H{il_house} from lagna, "
                f"ruled by {il_lord.title()}. The dispositor of this sign is the actual wealth-engine of the chart."
            )
        except Exception:
            pass
        blocks.append("\n".join(sp_lines))
    except Exception as e:
        logger.debug(f"Sensitive points failed: {e}")

    # ── 12. YOGINI DASHA — parallel timing lens (8-period system) ──
    try:
        from datetime import datetime

        from packages.context.src.yogini_dasha import get_current_yogini_dasha

        birth_dt2 = datetime.fromisoformat(chart_data["birth"]["datetime"])
        query_dt2 = datetime.fromisoformat(chart_data["meta"]["generated_at"])
        moon_nak_idx = int(moon_lon // 13.333333333) % 27 + 1  # 1-27
        moon_pada = int((moon_lon % 13.333333333) / 3.333333333) + 1
        moon_deg_in_nak = moon_lon % 13.333333333
        current_yog = get_current_yogini_dasha(
            birth_dt2,
            moon_nak_idx,
            moon_pada,
            moon_deg_in_nak,
            query_dt2,
        )
        yog_lord = current_yog.get("lord", "?")
        yog_name = current_yog.get("yogini", "?")
        yog_end = current_yog.get("end_date")
        yog_lines = ["\n[YOGINI DASHA — parallel 8-period timing system (Moon-based)]"]
        yog_lines.append(
            f"  Current Yogini MD: {yog_name.title()} ({yog_lord.title()}-flavored), "
            f"ends {str(yog_end)[:10] if yog_end else '?'}."
        )
        yog_lines.append(
            f"  Use for cross-confirmation with Vimshottari ({cur_md_lord.title()} MD/{cur_ad_lord.title()} AD). "
            f"When both systems point to the same lord, the period is structurally locked."
        )
        blocks.append("\n".join(yog_lines))
    except Exception as e:
        logger.debug(f"Yogini failed: {e}")

    # ── 13. VIMSHOPAKA BALA — composite 16-varga strength for current dasha lords ──
    try:
        from packages.cosmos.src.divisional import calculate_vimshopaka_bala

        vp_lines = ["\n[VIMSHOPAKA BALA — composite divisional strength (deeper than Shadbala)]"]
        for lord in [cur_md_lord, cur_ad_lord]:
            try:
                lon = float(natal.get(lord, {}).get("longitude", 0.0))
                vp = calculate_vimshopaka_bala(lord, lon, scheme="shad_varga")
                pct = vp.get("percentage", 0)
                cat = vp.get("category", "?")
                vp_lines.append(f"  {lord.title():8s}: {pct:.1f}% across 6 vargas — {cat}")
            except Exception:
                continue
        vp_lines.append(
            "  When Vimshopaka >= 60% the planet WILL deliver its dasha results even if "
            "Shadbala is moderate. Below 40% = the dasha runs hollow."
        )
        blocks.append("\n".join(vp_lines))
    except Exception as e:
        logger.debug(f"Vimshopaka failed: {e}")

    # ── 14. TAJAKA VARSHAPHAL — Muntha + Year-Lord for current age ──
    try:
        from datetime import datetime

        from packages.context.src.varshaphal import calculate_muntha

        birth_dt3 = datetime.fromisoformat(chart_data["birth"]["datetime"])
        query_dt3 = datetime.fromisoformat(chart_data["meta"]["generated_at"])
        # Completed years since birth
        age_years = (
            query_dt3.year
            - birth_dt3.year
            - ((query_dt3.month, query_dt3.day) < (birth_dt3.month, birth_dt3.day))
        )
        muntha = calculate_muntha(lagna_idx, age_years)
        m_house = muntha["house_from_lagna"]
        m_rashi_idx = muntha["muntha_rashi"]
        m_rashi = _RASHI[m_rashi_idx].title()
        m_theme = muntha.get("theme") or "(no rule data)"
        tj_lines = [
            "\n[TAJAKA VARSHAPHAL — annual chart Muntha (where the year's pressure lands)]",
            f"  Age {age_years} → Muntha sits in {m_rashi} = H{m_house} from natal lagna.",
            f"  Year theme: {m_theme}",
            "  Muntha shows the natal house being structurally tested or rewarded this birth-year. "
            "Cross-check: when current Vimshottari MD/AD lord rules or aspects this house, "
            "the year's themes are amplified.",
        ]
        blocks.append("\n".join(tj_lines))
    except Exception as e:
        logger.debug(f"Varshaphal failed: {e}")

    # ── 15. KARAKA-AS-LAGNA — each Chara Karaka as topical ascendant ──
    # Each Jaimini karaka is treated as the ascendant for its specific topic.
    # Whatever sits in the topical house from that karaka rules the result.
    try:
        from packages.self.src.jaimini import calculate_chara_karakas

        # We need a typed BirthChart for jaimini — reuse the one built above
        karakas = calculate_chara_karakas(chart)
        # role -> (topical_house, label)
        TOPIC = {
            "atmakaraka": (12, "moksha/dharma fulfillment"),
            "amatyakaraka": (10, "career outcomes"),
            "bhratrikaraka": (3, "courage/siblings/comms"),
            "matrikaraka": (4, "mother/home/comfort"),
            "putrakaraka": (5, "children/creativity"),
            "gnatikaraka": (6, "obstacles/health/illness"),
            "darakaraka": (7, "marriage/spouse"),
        }
        kk_lines = ["\n[KARAKA-AS-LAGNA — Jaimini topical houses]"]
        kk_lines.append(
            "  For each topic, the karaka acts as the topical lagna; the planets in the "
            "topical house from that karaka tell the topic's actual result."
        )
        for k in karakas:
            role = (k.karaka.value if hasattr(k.karaka, "value") else str(k.karaka)).lower()
            if role not in TOPIC:
                continue
            topic_house, label = TOPIC[role]
            karaka_planet = (
                k.planet.value if hasattr(k.planet, "value") else str(k.planet)
            ).lower()
            karaka_lon = float(natal.get(karaka_planet, {}).get("longitude", 0.0))
            karaka_sign_idx = int(karaka_lon // 30) % 12
            target_sign_idx = (karaka_sign_idx + topic_house - 1) % 12
            target_sign = _RASHI[target_sign_idx].title()
            # Which natal planets sit in that target sign?
            occupants = [
                p
                for p, d in natal.items()
                if int(float(d.get("longitude", 0.0)) // 30) % 12 == target_sign_idx
            ]
            occ_str = "+".join(p.title() for p in occupants) if occupants else "(empty)"
            kk_lines.append(
                f"  {role.title():14s}={karaka_planet.title():8s} → "
                f"{label}: H{topic_house} from karaka = {target_sign} [{occ_str}]"
            )
        blocks.append("\n".join(kk_lines))
    except Exception as e:
        logger.debug(f"Karaka-Sudarshana failed: {e}")

    # ── 16. CLASSICAL HOUSE-LORD WALK — BPHS systematic reading ──
    # The single most underused signal in our previous reports. Walks ALL 12
    # house lords in order, locates where each one sits from lagna, pulls
    # the BPHS-anchored interpretation, and emits one paragraph per lord
    # framed for the reader's lived experience.
    try:
        walk_lines = ["\n[CLASSICAL HOUSE-LORD WALK — BPHS systematic reading]"]
        walk_lines.append(
            "  This is the sequential Parashari reading the dossier was missing. Each line "
            "names the house, its lord in this chart, where that lord sits, and what BPHS "
            "specifically says happens when this lord lands there. Use these as the "
            "DEEPEST CONVERGENCE LAYER — when 3+ of these statements align with each "
            "other (and with the karaka/yoga/dasha signals above), the reader has "
            "structurally LIVED that pattern. Write the section around that convergence "
            "in lived-experience language, not in classical terminology."
        )
        for h in range(1, 13):
            # The sign that falls on this house from lagna
            house_sign_idx = (lagna_idx + h - 1) % 12
            lord = SIGN_LORDS_IDX[house_sign_idx]
            # Where the lord actually sits
            lord_lon = float(natal.get(lord, {}).get("longitude", 0.0))
            lord_sign_idx = int(lord_lon // 30) % 12
            sits_in = ((lord_sign_idx - lagna_idx) % 12) + 1
            sits_in_sign = _RASHI[lord_sign_idx].title()
            # Look up the classical effect for this lord_X_in_house_Y combination
            cls = lookup_house_lord_in_house(h, sits_in)
            summary = cls.get("summary", "(no classical entry)")
            specific = cls.get("specific_effects", "")
            theme = HOUSE_THEMES.get(h, {}).get("lived", "")
            classical_line = summary
            if specific and specific != summary:
                classical_line = f"{summary}. {specific}"
            # Dignity flag — own sign / exalted boosts; debilitation undermines
            dignity_note = ""
            EXALTATION = {
                "sun": 0,
                "moon": 1,
                "mars": 9,
                "mercury": 5,
                "jupiter": 3,
                "venus": 11,
                "saturn": 6,
            }
            DEBILITATION = {
                "sun": 6,
                "moon": 7,
                "mars": 3,
                "mercury": 11,
                "jupiter": 9,
                "venus": 5,
                "saturn": 0,
            }
            OWN_SIGNS = {
                "sun": [4],
                "moon": [3],
                "mars": [0, 7],
                "mercury": [2, 5],
                "jupiter": [8, 11],
                "venus": [1, 6],
                "saturn": [9, 10],
            }
            if EXALTATION.get(lord) == lord_sign_idx:
                dignity_note = " (EXALTED → the effect lands at full power)"
            elif DEBILITATION.get(lord) == lord_sign_idx:
                dignity_note = " (DEBILITATED → the effect is undermined; check for Neecha Bhanga)"
            elif lord_sign_idx in OWN_SIGNS.get(lord, []):
                dignity_note = " (OWN SIGN → the effect runs strong and clean)"
            walk_lines.append(
                f"\n  H{h} ({HOUSE_THEMES[h]['name']}) — lord {lord.title()} sits in H{sits_in} "
                f"({sits_in_sign}){dignity_note}"
            )
            walk_lines.append(f"     Classical (BPHS): {classical_line}")
            walk_lines.append(
                f"     Lived theme: this is where the '{theme}' question shows up in life."
            )
        blocks.append("\n".join(walk_lines))
    except Exception as e:
        logger.debug(f"Classical house-lord walk failed: {e}")

    # ── 17. CONVERGENCE TRIGGERS — surface the eerily-accurate moments ──
    # Detect when 3+ independent classical signatures point at the same planet
    # or the same house. Tells the writer "lean here — the reader has LIVED this."
    try:
        from collections import Counter

        signals: list[tuple[str, str]] = []  # (planet, source-of-signal)
        # Lagna lord
        lagna_lord = SIGN_LORDS_IDX[lagna_idx]
        signals.append((lagna_lord, "lagna lord"))
        # 10L (career)
        h10_sign_idx = (lagna_idx + 9) % 12
        signals.append((SIGN_LORDS_IDX[h10_sign_idx], "10L (career)"))
        # 2L (wealth)
        h2_sign_idx = (lagna_idx + 1) % 12
        signals.append((SIGN_LORDS_IDX[h2_sign_idx], "2L (wealth)"))
        # 7L (partnership)
        h7_sign_idx = (lagna_idx + 6) % 12
        signals.append((SIGN_LORDS_IDX[h7_sign_idx], "7L (partnership)"))
        # 9L (dharma)
        h9_sign_idx = (lagna_idx + 8) % 12
        signals.append((SIGN_LORDS_IDX[h9_sign_idx], "9L (dharma)"))
        # Karakas from chart-data Chara Karakas (if computed earlier in blocks)
        try:
            from packages.self.src.jaimini import calculate_chara_karakas

            karakas = calculate_chara_karakas(chart)
            for k in karakas:
                role = (k.karaka.value if hasattr(k.karaka, "value") else str(k.karaka)).lower()
                planet = (k.planet.value if hasattr(k.planet, "value") else str(k.planet)).lower()
                if role in {"atmakaraka", "amatyakaraka", "darakaraka", "putrakaraka"}:
                    signals.append((planet, f"Jaimini {role}"))
        except Exception:
            pass
        # Current MD lord
        signals.append((cur_md_lord, "current Mahadasha lord"))

        counts = Counter(p for p, _ in signals)
        triple = [(p, c) for p, c in counts.items() if c >= 3]
        if triple:
            conv_lines = ["\n[CONVERGENCE TRIGGERS — planets carrying ≥3 classical signatures]"]
            conv_lines.append(
                "  When a single planet shows up across 3+ independent classical lenses "
                "(house lordship, karaka role, dasha activation), it has DEFINING power "
                "over the chart. The reader has lived its themes — write to that."
            )
            for planet, count in sorted(triple, key=lambda x: -x[1]):
                sources = [s for p, s in signals if p == planet]
                # Where does this planet sit
                p_lon = float(natal.get(planet, {}).get("longitude", 0.0))
                p_sign = _RASHI[int(p_lon // 30) % 12].title()
                p_house = natal.get(planet, {}).get("house", "?")
                conv_lines.append(
                    f"  {planet.title():8s} ({count} signatures: {', '.join(sources)}) "
                    f"sits in {p_sign} H{p_house}. This planet IS this person."
                )
            blocks.append("\n".join(conv_lines))
    except Exception as e:
        logger.debug(f"Convergence detection failed: {e}")

    # ── 18a. VIMSHOTTARI CANONICAL DATES — DO NOT INVENT ──
    # Every agent must use these exact dates when referencing sub-period
    # transitions. Without this, agents independently invent dates like
    # "November 2026" or "January 2027" for the Mercury-Venus pivot when the
    # real date is May 22 2026. This block is the SINGLE source of truth.
    try:
        from datetime import datetime as _dt

        from packages.context.src.dasha import (
            get_antardasha_sequence as _ad_seq,
        )
        from packages.context.src.dasha import (
            get_pratyantardasha_sequence as _pd_seq,
        )

        _birth = _dt.fromisoformat(chart_data["birth"]["datetime"])
        _query = _dt.fromisoformat(chart_data["meta"]["generated_at"])
        if _birth.tzinfo:
            _birth = _birth.replace(tzinfo=None)
        if _query.tzinfo:
            _query = _query.replace(tzinfo=None)

        _md = chart_data["dasha"]["current"]["mahadasha"]
        _md_start = (
            _md["start_date"]
            if hasattr(_md["start_date"], "year")
            else _dt.fromisoformat(str(_md["start_date"]))
        )
        _md_end = (
            _md["end_date"]
            if hasattr(_md["end_date"], "year")
            else _dt.fromisoformat(str(_md["end_date"]))
        )
        if _md_start.tzinfo:
            _md_start = _md_start.replace(tzinfo=None)
        if _md_end.tzinfo:
            _md_end = _md_end.replace(tzinfo=None)
        _md_total = (_md_end - _md_start).days / 365.25
        _md_elapsed = (_query - _md_start).days / 365.25
        _md_remaining = _md_total - _md_elapsed

        canon: list[str] = [
            "\n[VIMSHOTTARI CANONICAL DATES — these are the ONLY dates to use]",
            "  PURPOSE: this is internal scaffolding for YOU, the writer, to",
            "  know exactly when each sub-period transitions. It is NOT content",
            "  to be enumerated in the prose. Do not list these dates sub-period",
            "  by sub-period in your output — that turns the reading into a",
            "  syllabus. Reference at most ONE OR TWO of these dates in your",
            "  prose, and only when a specific date directly illuminates the",
            "  current moment or the question being answered.",
            "",
            "  HARD RULE for the writer: when you DO mention a sub-period date",
            "  in prose, use the EXACT date listed below, written as e.g.",
            "  'May 22, 2026' or 'on the twenty-second of May 2026'. Never write",
            "  'late 2026', 'November 2026', or 'January 2027' for a transition",
            "  that is actually May 22 2026. Other agents are reading the same",
            "  table — internal contradictions will break the reader's trust.",
            "",
            f"  CURRENT MAHADASHA: {cur_md_lord.title()}",
            f"    Started:   {_md_start.date().isoformat()}",
            f"    Ends:      {_md_end.date().isoformat()}",
            f"    Total length:   {_md_total:.0f} years",
            f"    Elapsed:        {_md_elapsed:.1f} years (as of {_query.date().isoformat()})",
            f"    Remaining:      {_md_remaining:.1f} years",
            "",
            f"  ALL ANTARDASHAS in {cur_md_lord.title()} MD (exact start/end):",
        ]
        try:
            _ads_full = _ad_seq(cur_md_lord, _md_start, _md_end)
            for _ad in _ads_full:
                _as = _ad["start_date"]
                _ae = _ad["end_date"]
                if _as.tzinfo:
                    _as = _as.replace(tzinfo=None)
                if _ae.tzinfo:
                    _ae = _ae.replace(tzinfo=None)
                _mark = " ← CURRENT" if _as <= _query <= _ae else ""
                canon.append(
                    f"    {cur_md_lord.title()}-{_ad['lord'].title():8s}  "
                    f"{_as.date().isoformat()}  →  {_ae.date().isoformat()}{_mark}"
                )
        except Exception as _e:
            logger.debug(f"AD enumeration failed: {_e}")

        # Pratyantardashas inside current AD — granular for muhurta/year-ahead
        _cur_ad = chart_data["dasha"]["current"]["antardasha"]
        _ad_start = (
            _cur_ad["start_date"]
            if hasattr(_cur_ad["start_date"], "year")
            else _dt.fromisoformat(str(_cur_ad["start_date"]))
        )
        _ad_end = (
            _cur_ad["end_date"]
            if hasattr(_cur_ad["end_date"], "year")
            else _dt.fromisoformat(str(_cur_ad["end_date"]))
        )
        if _ad_start.tzinfo:
            _ad_start = _ad_start.replace(tzinfo=None)
        if _ad_end.tzinfo:
            _ad_end = _ad_end.replace(tzinfo=None)
        try:
            _pds = _pd_seq(cur_ad_lord, _ad_start, _ad_end)
            canon.append("")
            canon.append(
                f"  PRATYANTARDASHAS in current "
                f"{cur_md_lord.title()}-{cur_ad_lord.title()} AD (granular):"
            )
            for _pd in _pds:
                _ps = _pd["start_date"]
                _pe = _pd["end_date"]
                if _ps.tzinfo:
                    _ps = _ps.replace(tzinfo=None)
                if _pe.tzinfo:
                    _pe = _pe.replace(tzinfo=None)
                _mark = " ← CURRENT" if _ps <= _query <= _pe else ""
                canon.append(
                    f"    {cur_md_lord.title()}-{cur_ad_lord.title()}-{_pd['lord'].title():8s}  "
                    f"{_ps.date().isoformat()}  →  {_pe.date().isoformat()}{_mark}"
                )
        except Exception as _e:
            logger.debug(f"PD enumeration failed: {_e}")

        # ALSO list the FIRST AD of the NEXT MD so agents can speak to the
        # boundary between current MD and next MD without inventing a date.
        try:
            from packages.context.src.dasha import get_mahadasha_sequence as _md_seq

            _all_mds = _md_seq(_birth, chart_data["moon"]["longitude"], years=120)
            for _i, _next_md in enumerate(_all_mds):
                _ns = _next_md["start_date"]
                if _ns.tzinfo:
                    _ns = _ns.replace(tzinfo=None)
                if _ns >= _md_end:
                    _ne = _next_md["end_date"]
                    if _ne.tzinfo:
                        _ne = _ne.replace(tzinfo=None)
                    canon.append("")
                    canon.append(
                        f"  NEXT MAHADASHA: {_next_md['lord'].title()}  "
                        f"{_ns.date().isoformat()}  →  {_ne.date().isoformat()}"
                    )
                    break
        except Exception as _e:
            logger.debug(f"Next MD lookup failed: {_e}")

        blocks.append("\n".join(canon))
    except Exception as _e:
        logger.warning(f"Canonical dates block failed: {_e}")

    # ── 18. LIVED-LIFE TIMELINE — chronology of past 25-30 years of sub-periods ──
    # The single most under-used signal. Each Antardasha (sub-period) within the
    # Mahadasha shaped the native through a specific life-area lens. The
    # cumulative texture of past sub-periods IS who the person is now. Agents
    # should reference this chronology when writing — it makes the reading
    # feel like the system actually knows the person, not just where they are.
    try:
        from datetime import datetime, timedelta

        from packages.context.src.dasha import (
            get_antardasha_sequence,
            get_mahadasha_sequence,
        )

        birth_dt2 = datetime.fromisoformat(chart_data["birth"]["datetime"])
        query_dt2 = datetime.fromisoformat(chart_data["meta"]["generated_at"])
        # Strip tz to keep arithmetic clean
        if birth_dt2.tzinfo:
            birth_dt2 = birth_dt2.replace(tzinfo=None)
        if query_dt2.tzinfo:
            query_dt2 = query_dt2.replace(tzinfo=None)

        # Get all MDs covering birth → today + 1 year
        mds = get_mahadasha_sequence(birth_dt2, moon_lon, years=120)

        # Per-planet life-themes derived from its NATAL house. The AD lord's
        # natal house = the life-area being shaped during that sub-period.
        HOUSE_THEME_SHORT: dict[int, str] = {
            1: "identity and how he showed up",
            2: "money, family, voice",
            3: "courage, siblings, short journeys",
            4: "home, mother, inner ground",
            5: "creativity, romance, learning",
            6: "service, debts, daily friction",
            7: "partnership, marriage, the public",
            8: "transformation, secrets, deep change",
            9: "dharma, father, higher meaning",
            10: "career, public reputation, status",
            11: "gains, friendships, the network",
            12: "dissolution, foreign, spirituality, sleep",
        }
        # Per-planet karaka-flavor (what that planet's energy tends to bring)
        PLANET_FLAVOR: dict[str, str] = {
            "sun": "authority, identity, father-energy, public exposure",
            "moon": "emotional weather, mother, home, comfort or unrest",
            "mars": "drive, action, conflict, energy and fight",
            "mercury": "intellect, communication, business, study, articulation",
            "jupiter": "expansion, teaching, wisdom, fortune, meaning",
            "venus": "love, beauty, marriage, money, aesthetic refinement",
            "saturn": "discipline, restriction, slow building, karmic audit",
            "rahu": "ambition, foreign, unconventional, unusual rises",
            "ketu": "dissolution, spirituality, detachment, mystery, sudden loss",
        }

        tl_lines = ["\n[LIVED-LIFE TIMELINE — chronology of past sub-periods]"]
        tl_lines.append(
            "  PURPOSE — FOR YOUR UNDERSTANDING ONLY, NOT FOR PROSE: this "
            "chronology exists so YOU, the writer, know the texture of who "
            "this person has been — what they were structurally living through "
            "at each age. Use it to ground your voice in the lived person, not "
            "as content to enumerate. DO NOT walk the reader through every "
            "sub-period; that turns prose into a syllabus. Instead, reference "
            "AT MOST ONE OR TWO past sub-periods, and only when one directly "
            "illuminates the current moment or the question being answered "
            "— for example, 'the same Ketu signature ran on you in 2009-2010, "
            "and it cracked open the same kind of question.' That single "
            "callback makes the reader feel seen; enumerating the whole "
            "ladder makes them feel processed. Format: year-range | age | "
            "sub-period | natal house of AD lord | what was being shaped."
        )

        # For each MD that overlaps the period (birth → today + 1yr lookahead),
        # walk its ADs.
        cutoff_future = query_dt2 + timedelta(days=365)
        items: list[str] = []
        for md in mds:
            md_lord = md["lord"]
            md_start = md["start_date"]
            md_end = md["end_date"]
            if md_start.tzinfo:
                md_start = md_start.replace(tzinfo=None)
            if md_end.tzinfo:
                md_end = md_end.replace(tzinfo=None)
            # Skip MDs entirely outside the window
            if md_end < birth_dt2 or md_start > cutoff_future:
                continue
            ads = get_antardasha_sequence(md_lord, md_start, md_end)
            for ad in ads:
                ad_lord = ad["lord"]
                ad_start = ad["start_date"]
                ad_end = ad["end_date"]
                if ad_start.tzinfo:
                    ad_start = ad_start.replace(tzinfo=None)
                if ad_end.tzinfo:
                    ad_end = ad_end.replace(tzinfo=None)
                # Include sub-periods that overlap with anything from age 5 to now+1yr
                age_at_ad_start = (ad_start - birth_dt2).days / 365.25
                if age_at_ad_start < 5:
                    continue
                if ad_start > cutoff_future:
                    break
                # AD lord's natal house tells us the life-area being shaped
                ad_info = natal.get(ad_lord, {})
                ad_house = ad_info.get("house")
                ad_house_theme = HOUSE_THEME_SHORT.get(ad_house, f"H{ad_house}")
                # Is this AD currently active?
                is_now = ad_start <= query_dt2 <= ad_end
                marker = " ← NOW" if is_now else ""
                # Age range
                age_end = (ad_end - birth_dt2).days / 365.25
                age_str = f"age {int(age_at_ad_start)}-{int(age_end)}"
                # Format
                items.append(
                    f"  {ad_start.year}-{ad_end.year:>4} | {age_str:>10} | "
                    f"{md_lord.title()}-{ad_lord.title():8s} sub-period | "
                    f"AD lord sits in H{ad_house} ({ad_house_theme}) | "
                    f"{PLANET_FLAVOR.get(ad_lord, '')}{marker}"
                )

        tl_lines.extend(items)
        blocks.append("\n".join(tl_lines))
    except Exception as e:
        logger.debug(f"Lived timeline failed: {e}")

    return "\n".join(blocks)


def combust_orb_planets() -> set[str]:
    """Set of planets that can be combust (Sun obviously can't be combust by Sun)."""
    return {"mercury", "venus", "mars", "jupiter", "saturn"}


# ════════════════════════════════════════════════════════════════════
#  v12 CLASSICAL ENRICHMENT — FACT CHECK + missing dossier layers
# ════════════════════════════════════════════════════════════════════
#
# This block fixes the v11 audit findings: agents were silently missing
# Kaal Sarp / Mangal status, Ashtama Shani, Karakamsha, nakshatra-level
# reading, and sign-sandhi flags. Now every dossier carries a
# "FACT CHECK" header that authoritatively lists which yogas/doshas
# FIRE for THIS chart, so agents can't invent ones that don't.

_NAKSHATRA_DEFS_CACHE: list[dict[str, Any]] | None = None


def _load_nakshatra_defs() -> list[dict[str, Any]]:
    global _NAKSHATRA_DEFS_CACHE
    if _NAKSHATRA_DEFS_CACHE is None:
        import json
        from pathlib import Path

        p = (
            Path(__file__).parent.parent.parent.parent
            / "knowledge"
            / "definitions"
            / "nakshatras.json"
        )
        with p.open() as f:
            data = json.load(f)
        _NAKSHATRA_DEFS_CACHE = data["nakshatras"]
    return _NAKSHATRA_DEFS_CACHE


def _nakshatra_info(longitude: float) -> dict[str, Any]:
    """Return the nakshatra definition for a longitude (with pada-flavor sign)."""
    nak_size = 360.0 / 27.0
    nak_num = int(longitude // nak_size)
    nak = _load_nakshatra_defs()[nak_num]
    # Determine pada
    pos_in_nak = longitude - (nak_num * nak_size)
    pada_num = min(4, int(pos_in_nak // (nak_size / 4.0)) + 1)
    pada = nak["padas"][pada_num - 1]
    return {
        "name": nak["name"],
        "ruler": nak["ruler"],
        "deity": nak["deity"],
        "symbol": nak["symbol"],
        "shakti": nak["shakti"],
        "gana": nak["gana"],
        "animal": nak["animal"],
        "pada": pada_num,
        "pada_navamsha_sign": pada["navamsha_sign"].title(),
    }


def _d9_sign_idx(longitude: float) -> int:
    """Compute Navamsha (D9) sign index for a tropical-Vedic longitude."""
    sign = int(longitude // 30)
    deg_in_sign = longitude - sign * 30
    nav_idx = int(deg_in_sign // (30.0 / 9.0))
    # Movable signs (Aries/Cancer/Libra/Capricorn) — D9 starts from own sign
    if sign in (0, 3, 6, 9):
        d9_start = sign
    # Fixed signs (Taurus/Leo/Scorpio/Aquarius) — D9 starts 9th from own
    elif sign in (1, 4, 7, 10):
        d9_start = (sign + 8) % 12
    # Dual signs (Gemini/Virgo/Sagittarius/Pisces) — D9 starts 5th from own
    else:
        d9_start = (sign + 4) % 12
    return (d9_start + nav_idx) % 12


def _mangal_dosha_check(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Classical Mangal Dosha analysis with cancellation logic.

    Positions: Mars in 1/2/4/7/8/12 from Lagna, Moon, or Venus = Mangal.
    Cancellations checked: own/exalted Mars, Mars-Jupiter conjunction,
    Jupiter aspect on Mars, Mars in Mercury's sign in 2H.
    """
    natal = chart_data.get("natal_planets_dict") or {}
    if "mars" not in natal:
        return {"active": False, "reason": "no Mars data"}
    mars_lon = float(natal["mars"]["longitude"])
    mars_sign = int(mars_lon // 30)
    lagna_sign = chart_data["lagna"]["rashi_idx"]
    moon_sign = int(float(natal["moon"]["longitude"]) // 30) if "moon" in natal else lagna_sign
    venus_sign = int(float(natal["venus"]["longitude"]) // 30) if "venus" in natal else lagna_sign

    DOSHA_POS = {1, 2, 4, 7, 8, 12}
    house_from_lagna = ((mars_sign - lagna_sign) % 12) + 1
    house_from_moon = ((mars_sign - moon_sign) % 12) + 1
    house_from_venus = ((mars_sign - venus_sign) % 12) + 1

    fires_lagna = house_from_lagna in DOSHA_POS
    fires_moon = house_from_moon in DOSHA_POS
    fires_venus = house_from_venus in DOSHA_POS
    fires_count = sum([fires_lagna, fires_moon, fires_venus])

    # Cancellations (classical)
    cancels: list[str] = []
    # Mars in own sign (Aries=0, Scorpio=7) or exalted (Capricorn=9)
    if mars_sign in (0, 7):
        cancels.append("Mars in own sign")
    if mars_sign == 9:
        cancels.append("Mars exalted in Capricorn")
    # Mars debilitated in Cancer is NOT a cancellation — it intensifies the dosha
    # Jupiter conjunct Mars
    if "jupiter" in natal:
        jup_sign = int(float(natal["jupiter"]["longitude"]) // 30)
        if jup_sign == mars_sign:
            cancels.append("Jupiter conjunct Mars in same sign")
        # Jupiter 7th-from-Mars (mutual 7th aspect)
        if abs(((jup_sign - mars_sign) % 12) - 6) == 0:
            cancels.append("Jupiter aspects Mars by 7th")
    # Mars in Mercury's sign (Gemini=2 or Virgo=5) sitting in 2H from Lagna
    if mars_sign in (2, 5) and house_from_lagna == 2:
        cancels.append("Mars in Mercury's sign in 2H")

    is_cancelled = len(cancels) > 0
    return {
        "active": fires_count > 0,
        "is_cancelled": is_cancelled,
        "fires_count": fires_count,
        "house_from_lagna": house_from_lagna,
        "house_from_moon": house_from_moon,
        "house_from_venus": house_from_venus,
        "fires_from_lagna": fires_lagna,
        "fires_from_moon": fires_moon,
        "fires_from_venus": fires_venus,
        "cancellation_factors": cancels,
        "mars_sign_idx": mars_sign,
    }


def _kaal_sarp_amrit_check(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Detect Kaal Sarp (planets between Rahu→Ketu) vs Kaal Amrit (Ketu→Rahu).

    Both produce nodal-axis flavored life, but Kaal Sarp is the harder one;
    Kaal Amrit (the same configuration in reverse direction) is benevolent.
    """
    natal = chart_data.get("natal_planets_dict") or {}
    if "rahu" not in natal or "ketu" not in natal:
        return {"active": False}
    rahu_sign = int(float(natal["rahu"]["longitude"]) // 30)
    ketu_sign = int(float(natal["ketu"]["longitude"]) // 30)
    grahas = [
        p for p in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn") if p in natal
    ]
    if len(grahas) < 7:
        return {"active": False}
    # arc from Rahu walking forward to Ketu — if all planets fall in this arc, Kaal Sarp
    arc_rahu_to_ketu: set[int] = set()
    s = rahu_sign
    while s != ketu_sign:
        s = (s + 1) % 12
        arc_rahu_to_ketu.add(s)
    arc_ketu_to_rahu: set[int] = set()
    s = ketu_sign
    while s != rahu_sign:
        s = (s + 1) % 12
        arc_ketu_to_rahu.add(s)
    planet_signs = {p: int(float(natal[p]["longitude"]) // 30) for p in grahas}
    in_arc_rahu_to_ketu = all(planet_signs[p] in arc_rahu_to_ketu for p in grahas)
    in_arc_ketu_to_rahu = all(planet_signs[p] in arc_ketu_to_rahu for p in grahas)
    if in_arc_rahu_to_ketu:
        return {
            "active": True,
            "type": "kaal_sarp",
            "direction": "rahu_to_ketu",
            "rahu_sign_idx": rahu_sign,
            "ketu_sign_idx": ketu_sign,
        }
    if in_arc_ketu_to_rahu:
        return {
            "active": True,
            "type": "kaal_amrit",
            "direction": "ketu_to_rahu",
            "rahu_sign_idx": rahu_sign,
            "ketu_sign_idx": ketu_sign,
        }
    return {"active": False}


def _ashtama_kantaka_shani_check(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Detect classical Saturn-transit pressures from natal Moon.

    Ashtama Shani = Saturn transiting 8th from Moon (2.5y heavy transit).
    Kantaka Shani = Saturn transiting 4th from Moon (the 'thorn' Saturn).
    Both are distinct from Sade Sati (Saturn in 12/1/2 from Moon).
    """
    natal = chart_data.get("natal_planets_dict") or {}
    _sv = chart_data.get("state_vector") or {}
    # Try to pull current transit Saturn sign from state_vector ambient signals
    _ambient = chart_data.get("ambient_signals") or {}
    saturn_transit_sign = None
    # Look for a "saturn_transit_sign" hint; otherwise compute from generated_at
    try:
        from datetime import datetime

        from packages.cosmos.src.ephemeris import (
            get_all_planets,
            get_ayanamsa,
            get_julian_day,
        )

        gen = datetime.fromisoformat(chart_data["meta"]["generated_at"])
        jd = get_julian_day(gen)
        ayan = get_ayanamsa(jd, "lahiri")
        sat = get_all_planets(jd, ayanamsa=ayan)["saturn"]
        saturn_transit_sign = int(float(sat["longitude"]) // 30)
    except Exception:
        return {"active": False}
    if "moon" not in natal:
        return {"active": False}
    moon_sign = int(float(natal["moon"]["longitude"]) // 30)
    house_from_moon = ((saturn_transit_sign - moon_sign) % 12) + 1
    if house_from_moon == 8:
        return {"active": True, "type": "ashtama_shani", "house_from_moon": 8}
    if house_from_moon == 4:
        return {"active": True, "type": "kantaka_shani", "house_from_moon": 4}
    if house_from_moon in (12, 1, 2):
        # Sade Sati — already covered by sade_sati state_vector field
        return {"active": False, "note": "in sade_sati range — separate signal"}
    return {"active": False}


def _karakamsha_reading(chart_data: dict[str, Any]) -> dict[str, Any]:
    """Compute Karakamsha (D9 sign of the Atmakaraka) and load its reading.

    Texts treat this as the soul's chosen environment for this lifetime.
    """
    natal = chart_data.get("natal_planets_dict") or {}
    # Find atmakaraka: highest degree in own sign (excluding Rahu/Ketu)
    ak_candidates = [
        (p, float(d["longitude"]) % 30)
        for p, d in natal.items()
        if p not in ("rahu", "ketu") and isinstance(d, dict)
    ]
    if not ak_candidates:
        return {}
    ak_planet, ak_deg = max(ak_candidates, key=lambda x: x[1])
    ak_lon = float(natal[ak_planet]["longitude"])
    karakamsha_sign_idx = _d9_sign_idx(ak_lon)
    return {
        "atmakaraka": ak_planet,
        "atmakaraka_degree_in_sign": round(ak_deg, 3),
        "karakamsha_sign": _RASHI[karakamsha_sign_idx],
        "karakamsha_sign_idx": karakamsha_sign_idx,
    }


def _sandhi_planets(chart_data: dict[str, Any]) -> list[str]:
    """List planets at sign-sandhi (< 1° from sign boundary) — structurally weak."""
    natal = chart_data.get("natal_planets_dict") or {}
    out: list[str] = []
    for p, d in natal.items():
        if not isinstance(d, dict):
            continue
        deg = float(d["longitude"]) % 30
        if deg < 1.0:
            out.append(f"{p.title()} at {deg:.2f}° (entering new sign — weak sandhi)")
        elif deg > 29.0:
            out.append(f"{p.title()} at {deg:.2f}° (leaving sign — gandanta-flavor)")
    return out


def _nakshatra_dossier(chart_data: dict[str, Any]) -> str:
    """Per-planet nakshatra reading with deity/shakti/symbol."""
    natal = chart_data.get("natal_planets_dict") or {}
    asc_lon = (
        chart_data.get("lagna", {}).get("degree", 0)
        + chart_data.get("lagna", {}).get("rashi_idx", 0) * 30
    )
    lines = ["\n[NAKSHATRA LAYER — deities, shaktis, archetypal readings]"]
    # Lagna nakshatra first
    try:
        nak = _nakshatra_info(asc_lon)
        lines.append(
            f"  Lagna in {nak['name']} (ruler {nak['ruler']}, deity {nak['deity']}, "
            f"shakti '{nak['shakti']}', symbol '{nak['symbol']}', gana {nak['gana']}). "
            f"Pada {nak['pada']} = {nak['pada_navamsha_sign']} navamsha."
        )
    except Exception:
        pass
    for p in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"):
        if p not in natal:
            continue
        lon = float(natal[p]["longitude"])
        try:
            nak = _nakshatra_info(lon)
            lines.append(
                f"  {p.title()} in {nak['name']} Pada {nak['pada']} "
                f"(deity {nak['deity']}, shakti '{nak['shakti']}', symbol '{nak['symbol']}'). "
                f"Pada navamsha = {nak['pada_navamsha_sign']}."
            )
        except Exception:
            continue
    return "\n".join(lines)


def gather_classical_fact_check(chart_data: dict[str, Any]) -> str:
    """Authoritative FACT CHECK block — what fires for THIS chart, what doesn't.

    Agents should treat this as the ground truth. They are NOT allowed to claim
    yogas/doshas/transits that don't appear here as 'active: True'.
    """
    blocks: list[str] = [
        "═══════════════════════════════════════════════════════════════",
        "FACT CHECK — what is structurally TRUE for this chart",
        "═══════════════════════════════════════════════════════════════",
        "(Agents: trust ONLY what appears here. Do not invent yogas or doshas.",
        " The detectors below have already run against this exact chart.)",
        "",
    ]

    # 1. Mangal Dosha
    mangal = _mangal_dosha_check(chart_data)
    if mangal.get("active"):
        positions = []
        if mangal.get("fires_from_lagna"):
            positions.append(f"{mangal['house_from_lagna']}H from Lagna")
        if mangal.get("fires_from_moon"):
            positions.append(f"{mangal['house_from_moon']}H from Moon")
        if mangal.get("fires_from_venus"):
            positions.append(f"{mangal['house_from_venus']}H from Venus")
        status = "CANCELLED" if mangal["is_cancelled"] else "ACTIVE (not cancelled)"
        cancels = (
            ", ".join(mangal["cancellation_factors"]) or "none of the classical cancellations fire"
        )
        blocks.append(
            f"[Mangal Dosha] {status}. Fires from: {'; '.join(positions)}. "
            f"Cancellation check: {cancels}."
        )
    else:
        blocks.append(
            "[Mangal Dosha] does NOT fire (Mars not in 1/2/4/7/8/12 from Lagna, Moon, or Venus)."
        )

    # 2. Kaal Sarp / Kaal Amrit
    ks = _kaal_sarp_amrit_check(chart_data)
    if ks.get("active"):
        if ks["type"] == "kaal_sarp":
            blocks.append(
                "[Kaal Sarp Yoga] ACTIVE — all 7 planets sit between Rahu and Ketu (Rahu→Ketu direction). "
                "Classical: nodal-axis dominates life-themes; effort yields delayed, transformed rewards."
            )
        else:
            blocks.append(
                "[Kaal Amrit Yoga] ACTIVE — all 7 planets between Ketu and Rahu (Ketu→Rahu direction). "
                "This is the BENEVOLENT twin of Kaal Sarp. BPHS Ch.6 + Phaladeepika Ch.24: "
                "native achieves through sustained dharmic effort what others get easily; "
                "rewards arrive transformed, more lasting, less material-flashy."
            )
    else:
        blocks.append("[Kaal Sarp / Kaal Amrit] does NOT fire.")

    # 3. Ashtama / Kantaka Shani (current transit)
    shani = _ashtama_kantaka_shani_check(chart_data)
    if shani.get("active"):
        t = shani["type"]
        if t == "ashtama_shani":
            blocks.append(
                "[Ashtama Shani] ACTIVE NOW — Saturn transits 8th from natal Moon. "
                "Phaladeepika Ch.26: 2.5-year transit of grief / health audit / "
                "structural transformation / possible inheritance. Hold all major "
                "commitments. Distinct from (and often harder than) Sade Sati."
            )
        elif t == "kantaka_shani":
            blocks.append(
                "[Kantaka Shani] ACTIVE NOW — Saturn transits 4th from natal Moon. "
                "Classical: home/foundation/inner-ground under pressure; mother's health, "
                "vehicles, domestic peace tested for 2.5 years."
            )
    else:
        blocks.append("[Ashtama/Kantaka Shani] not currently firing.")

    # 4. Sade Sati (from state_vector)
    sade = (chart_data.get("state_vector") or {}).get("sade_sati") or {}
    if sade.get("active"):
        blocks.append(f"[Sade Sati] ACTIVE — phase: {sade.get('phase', '?')}.")
    else:
        blocks.append("[Sade Sati] not currently active.")

    # 5. Karakamsha
    kk = _karakamsha_reading(chart_data)
    if kk:
        blocks.append(
            f"[Karakamsha] Atmakaraka = {kk['atmakaraka'].title()} at "
            f"{kk['atmakaraka_degree_in_sign']:.2f}° in its own sign. "
            f"D9 (navamsha) sign of the Atmakaraka = **{kk['karakamsha_sign']}**. "
            f"This is the soul's chosen environment for this lifetime — "
            f"agents should read the entire chart through this lens for spiritual/dharma sections."
        )

    # 6. Sandhi (sign-cusp) planets
    sand = _sandhi_planets(chart_data)
    if sand:
        blocks.append(
            "[Sign-Sandhi planets] " + "; ".join(sand) + ". Structurally weak — effects diluted."
        )

    # 7. Detected doshas + yogas summary
    doshas = chart_data.get("doshas") or []
    if doshas:
        names = ", ".join(d["name"] for d in doshas[:8])
        blocks.append(f"[Detected doshas] {len(doshas)} total: {names}.")
    yogas = chart_data.get("yogas") or []
    if yogas:
        blocks.append(
            f"[Detected yogas] {len(yogas)} total detected. Agents: cite ONLY yogas "
            "that appear in the chart_data['yogas'] list. Do NOT claim yogas not listed."
        )

    # 8. Yogas the agent must NOT claim (common errors caught in v11 audit)
    natal = chart_data.get("natal_planets_dict") or {}
    forbidden = []
    # Hamsa requires Jupiter in own (Sag/Pis) OR exalted (Cancer) AND in kendra
    if "jupiter" in natal:
        jup_sign = int(float(natal["jupiter"]["longitude"]) // 30)
        # Sagittarius=8, Pisces=11, Cancer=3 (exaltation)
        lagna_sign = chart_data["lagna"]["rashi_idx"]
        jup_house = ((jup_sign - lagna_sign) % 12) + 1
        jup_in_own_or_exalt = jup_sign in (8, 11, 3)
        jup_in_kendra = jup_house in (1, 4, 7, 10)
        if not (jup_in_own_or_exalt and jup_in_kendra):
            forbidden.append("Hamsa Yoga (Jupiter not in own/exalted in kendra)")
    # Gajakesari requires Moon in 1/4/7/10 from Jupiter (or vice versa — kendras only)
    if "moon" in natal and "jupiter" in natal:
        moon_sign = int(float(natal["moon"]["longitude"]) // 30)
        jup_sign = int(float(natal["jupiter"]["longitude"]) // 30)
        moon_from_jup = ((moon_sign - jup_sign) % 12) + 1
        if moon_from_jup not in (1, 4, 7, 10):
            forbidden.append("Gajakesari Yoga (Moon not in kendra from Jupiter)")
    if forbidden:
        blocks.append(
            "[DO NOT CLAIM] These yogas do NOT fire for this chart: " + "; ".join(forbidden) + "."
        )

    return "\n".join(blocks)


def gather_nakshatra_layer(chart_data: dict[str, Any]) -> str:
    """Per-planet nakshatra readings with deity, shakti, symbol — for narrative depth."""
    return _nakshatra_dossier(chart_data)


def gather_for_what_already_happened(chart_data: dict[str, Any]) -> str:
    """Map customer's intake events to the dasha/transit signatures active at each.

    This is the RETRODICTIVE CREDIBILITY layer. For each event the customer told
    us happened, we look up:
      - which Mahadasha + Antardasha were running on that date
      - which natal house the AD lord activates
      - was Sade Sati active (and which phase)
      - were any major slow-planet transits hitting the natal moon/lagna
    Then the agent uses these signatures to write "the death/move/loss of X
    around DATE was XYZ firing — that's why it happened then."

    Without intake events, returns a note telling agents to skip the section.
    """
    from datetime import datetime

    from packages.context.src.dasha import get_antardasha_sequence, get_mahadasha_sequence

    events = chart_data.get("intake_events") or []
    if not events:
        return (
            "[NO INTAKE EVENTS PROVIDED]\n"
            "  The customer did not share specific past life events. Skip this section "
            "entirely OR ask the agent to use the lived-life timeline as a general "
            "retrodiction frame instead (without claiming specific events happened).\n"
        )

    natal = chart_data["natal_planets_dict"]
    birth_dt = datetime.fromisoformat(chart_data["birth"]["datetime"])
    if birth_dt.tzinfo:
        birth_dt = birth_dt.replace(tzinfo=None)
    moon_lon = chart_data["moon"]["longitude"]
    sade = (chart_data.get("state_vector") or {}).get("sade_sati") or {}

    HOUSE_THEME: dict[int, str] = {
        1: "self, body, identity",
        2: "wealth, family, voice",
        3: "courage, siblings, short journeys",
        4: "home, mother, inner ground, elders",
        5: "creativity, romance, children, learning",
        6: "service, debts, daily friction, health",
        7: "partnership, marriage, the public",
        8: "transformation, sudden change, hidden things, death",
        9: "dharma, father, higher meaning",
        10: "career, public reputation, status",
        11: "gains, friendships, the network",
        12: "loss, dissolution, foreign, spirituality, expenses",
    }

    blocks: list[str] = [
        "[CUSTOMER'S INTAKE EVENTS — retrodictive mapping]",
        "  For each event below, the agent has the dasha + transit + Sade Sati",
        "  signature that was active on that date. Use these to write 'the X",
        "  that happened around DATE was Y firing — that's why it happened then.'",
        "  This section creates retrodictive credibility BEFORE any predictive",
        "  claims are made later in the report.",
        "",
    ]

    # Pre-compute MD sequence once
    try:
        mds = get_mahadasha_sequence(birth_dt, moon_lon, years=120)
    except Exception as e:
        logger.warning(f"MD sequence for intake events failed: {e}")
        mds = []

    for ev in events:
        # Parse event date — accept date_iso, year, or year_range
        ev_date: datetime | None = None
        ev_label: str = ""
        if ev.get("date_iso"):
            try:
                ev_date = datetime.fromisoformat(str(ev["date_iso"]).replace("Z", "+00:00"))
                if ev_date.tzinfo:
                    ev_date = ev_date.replace(tzinfo=None)
                ev_label = ev_date.strftime("%B %Y")
            except Exception:
                pass
        elif ev.get("year"):
            try:
                ev_date = datetime(int(ev["year"]), 6, 30)  # midyear default
                ev_label = str(ev["year"])
            except Exception:
                pass
        elif ev.get("year_range"):
            try:
                yr_start, yr_end = ev["year_range"]
                ev_date = datetime(int(yr_start), 1, 1)
                ev_label = f"{yr_start}-{yr_end} (range)"
            except Exception:
                pass

        if ev_date is None:
            blocks.append(f"  [EVENT]: {ev.get('description', '?')} — date unparseable, skipping")
            continue

        # Find MD active at that date
        active_md = None
        for md in mds:
            ms = md["start_date"]
            me = md["end_date"]
            if ms.tzinfo:
                ms = ms.replace(tzinfo=None)
            if me.tzinfo:
                me = me.replace(tzinfo=None)
            if ms <= ev_date <= me:
                active_md = (md["lord"], ms, me)
                break

        # Find AD active at that date
        active_ad = None
        if active_md:
            try:
                ads = get_antardasha_sequence(active_md[0], active_md[1], active_md[2])
                for ad in ads:
                    as_ = ad["start_date"]
                    ae = ad["end_date"]
                    if as_.tzinfo:
                        as_ = as_.replace(tzinfo=None)
                    if ae.tzinfo:
                        ae = ae.replace(tzinfo=None)
                    if as_ <= ev_date <= ae:
                        active_ad = (ad["lord"], as_, ae)
                        break
            except Exception:
                pass

        # Get natal houses of MD and AD lords
        md_info = natal.get(active_md[0], {}) if active_md else {}
        md_house = md_info.get("house", 0) if md_info else 0
        ad_info = natal.get(active_ad[0], {}) if active_ad else {}
        ad_house = ad_info.get("house", 0) if ad_info else 0

        # Sade Sati state at that date (best-effort — phase from current state is
        # an approximation; for past dates we mark as "approximately known")
        sade_note = ""
        if sade.get("active"):
            sade_note = (
                f" | Sade Sati: {sade.get('phase', '?')} phase (still active as of report date)"
            )

        # Format the event block
        blocks.append(
            f"  [EVENT @ {ev_label}] type={ev.get('type', 'other')}\n"
            f"    description: {ev.get('description', '?')}\n"
            f"    active MD: {active_md[0].title() if active_md else '?'} "
            f"(MD lord sits in H{md_house}: {HOUSE_THEME.get(md_house, '?')})\n"
            f"    active AD: {active_ad[0].title() if active_ad else '?'} "
            f"(AD lord sits in H{ad_house}: {HOUSE_THEME.get(ad_house, '?')})"
            f"{sade_note}\n"
        )

    return "\n".join(blocks)


# ── Public entry ──


def gather_for_section(section_id: str, chart_data: dict[str, Any]) -> str:
    """Return REFERENCE MATERIAL block for the named section.

    Stacks (in order, top-priority first):
      1. **FACT CHECK** — what is structurally TRUE for this chart
         (Kaal Sarp, Mangal Dosha with cancellation, Ashtama Shani,
         Karakamsha, sandhi planets, plus a DO-NOT-CLAIM list of yogas
         the agent might falsely invent). Catches the v11 errors.
      2. **NAKSHATRA LAYER** — per-planet deities, shaktis, symbols
         (the layer the v11 reports were missing entirely).
      3. **Section-specific dossier** (per gatherer function).
      4. **Deep multi-lens dossier** (divisional, Jaimini, AV, Shadbala).
    """
    # 1. FACT CHECK first — agents read this BEFORE anything else.
    fact_check = ""
    try:
        fact_check = gather_classical_fact_check(chart_data)
    except Exception as e:
        logger.warning(f"Fact-check gather failed: {e}")
    # 2. Nakshatra layer
    nakshatra_layer = ""
    try:
        nakshatra_layer = gather_nakshatra_layer(chart_data)
    except Exception as e:
        logger.warning(f"Nakshatra gather failed: {e}")
    # 3. Section-specific
    gatherer = {
        "arc_so_far": gather_for_arc_so_far,
        "where_you_are_now": gather_for_where_you_are_now,
        "answering_your_question": gather_for_question,
        "what_to_do_next": gather_for_what_to_do,
        "what_already_happened": gather_for_what_already_happened,
    }.get(section_id)
    section_specific = ""
    if gatherer:
        try:
            section_specific = gatherer(chart_data)
        except Exception as e:
            logger.warning(f"Section gatherer failed for {section_id}: {e}")
    # 4. Deep multi-lens
    deep = ""
    try:
        deep = gather_deep_chart_layers(chart_data)
    except Exception as e:
        logger.warning(f"Deep layer gather failed: {e}")
    parts = [fact_check, nakshatra_layer, section_specific, deep]
    return "\n\n".join(p for p in parts if p).strip()
