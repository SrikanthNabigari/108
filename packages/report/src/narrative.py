"""Narrative synthesizer for the 108 Life Reading.

For each section that needs prose (not just data tables), this module builds
the prompt that gets sent to Claude, then returns the generated text.

Two operation modes:

1. **API mode** (production): calls the Anthropic API with the report data
   as context, returns the AI-generated section text.
2. **Manual mode** (Claude Code subscription): the script that drives the
   report engine prints the prompts, Claude (in the active session) writes
   the narratives, the operator pastes them back. Used for the first 100-200
   reports while the business is on subscription billing.

The prompts are carefully scoped: each section gets only the data it needs,
keeps tokens minimal, and enforces 108's voice guidelines.
"""

from __future__ import annotations

import os
from typing import Any

from packages.report.src.knowledge_gatherer import gather_for_section
from packages.report.src.voice import (
    LAGNA_DESCRIPTORS,
    MOON_DESCRIPTORS,
    planet_house_phrase,
    yoga_phrase,
)

# ── Section → Specialized Agent Mapping ──
#
# Each report section is written by a specialized 108 agent. The agent's
# .claude/agents/<name>.md file contains the full system prompt, tools,
# and voice rules. This mapping tells the report orchestrator which agent
# to spawn for which section.
SECTION_AGENT: dict[str, str] = {
    "what_already_happened": "108-retrodictor",
    "arc_so_far": "108-arc-historian",
    "where_you_are_now": "108-current-chapter",
    "answering_your_question": "108-question-answerer",
    "next_12_months": "108-year-ahead",
    "hidden_strengths": "108-yoga-interpreter",
    "structural_challenges": "108-dosha-counselor",
    "what_to_do_next": "108-action-strategist",
    # Add-on sections use the same SECTION_AGENT mapping
    "past_5_years": "108-past-decoder",
    "next_5_years": "108-five-year-mapper",
    "lifetime": "108-lifetime-cartographer",
    # Domain deep-dives (built in section B)
    "career_deep_dive": "108-career-specialist",
    "relationships_deep_dive": "108-relationship-decoder",
    "wealth_deep_dive": "108-wealth-architect",
    "health_deep_dive": "108-health-mapper",
    "spiritual_deep_dive": "108-spiritual-path",
    "sade_sati_deep_dive": "108-sade-sati",
    # NEW high-demand add-ons (Session 53)
    "children_deep_dive": "108-children-decoder",
    "education_deep_dive": "108-education-mapper",
    "foreign_settlement": "108-foreign-pathfinder",
    "property_vehicle": "108-property-timing",
    "business_launch": "108-business-architect",
    "muhurta_calendar": "108-muhurta-finder",
    "gem_prescription": "108-gem-prescriber",
    "compatibility": "108-compatibility-decoder",
    # Final pass — stitcher runs LAST and writes both cover_hook + closing_cta
    "cover_hook": "108-stitcher",
    "closing_cta": "108-stitcher",
}


def get_agent_for_section(section_id: str) -> str | None:
    """Return the specialized agent name for this section, or None."""
    return SECTION_AGENT.get(section_id)


# ── Voice guidelines pasted into every prompt ──
VOICE_GUIDELINES = """\
VOICE FOR 108 LIFE READING:
- Direct, warm, modern. Sound like a sharp friend, not a Sanskrit recitation.
- No woo-woo phrases ("the universe wants you to...", "your soul...").
- Use Vedic terms (dasha, lagna, nakshatra, yoga) but explain them in 1 line on first use.
- Cite classical sources where relevant (BPHS Ch.46, Phaladeepika v.X) — short, inline.
- 25-35 year old Indian audience. Reference modern life (work, apps, relationships, money) naturally.
- Say hard things directly. Don't sugarcoat. Don't moralize.
- Use specific dates and house/planet placements; never vague generalities.
- QUOTE THE NUMBERS the dossier gives you. When you cite strength/weakness, name
  the actual figure — Ashtakavarga bindus ("Mercury holds 5/8 in its own sign,
  34/56 total"), Shadbala virupas vs. required, the exact degree, the chara karaka
  by name (Atmakaraka/Amatyakaraka/Darakaraka/Putrakaraka), the avastha, the
  pratyantar date. Never write "thin bindu score" or "strength sits below 40%" —
  write the number. Specific numbers are what make the reading feel computed, not guessed.
- Length: each section 200-450 words. SHORTER IS BETTER.
- No bullet lists in narrative sections (data sections handle structure).

v12 ARCHITECTURE RULES (read these BEFORE writing a single sentence):
1. **FACT CHECK** — the dossier opens with a FACT CHECK header listing what is
   structurally TRUE for this chart (Mangal, Kaal Sarp, Ashtama Shani,
   Karakamsha, DO-NOT-CLAIM yogas). Trust ONLY what is marked ACTIVE there.
   Do NOT invent yogas not in the detected list. Do NOT claim Hamsa/Gajakesari
   unless FACT CHECK confirms they fire.
2. **NO CHART RE-INTRODUCTION** — the chart architecture (Lagna lord, key
   placements, yogakaraka) is already established by the earlier pages of the
   report (Your Birth Chart, How to Read, The Architecture). This section
   APPLIES the chart to its specific domain — do NOT re-explain who the Lagna
   lord is or where the key planets sit. Open with the domain, not the chart.
3. **NAKSHATRA LAYER** — the dossier has a NAKSHATRA LAYER block with deity,
   shakti, and symbol for every planet. Weave in at least ONE deity/shakti
   reference per section. (Pushya = Brihaspati nourishment, Ashlesha = Naga
   serpents, Magha = Pitrs/ancestors, Ardra = Rudra storm, Mrigashira = Soma
   deer-seeking, etc.)
4. **CONVERGENCE NOT ASSERTION** — every claim must cite 2+ INDEPENDENT chart
   factors. "Three factors agree" used as a phrase tic loses its meaning;
   only invoke when you actually have three.
5. **CANONICAL DATES VERBATIM** — copy dasha dates exactly from the CANONICAL
   DATES block. Never round, never invent.
"""


# ── Prompt builders for each narrative section ──


def build_prompt_what_already_happened(data: dict[str, Any]) -> str:
    """Section: 'What Already Happened' — retrodictive credibility from intake.

    Maps each customer-reported past event to the dasha/transit/Sade-Sati
    signature active at that date. This is THE section that earns the
    rest of the report — read the past back to the customer with chart
    specificity so the predictions later carry weight.
    """
    events = data.get("intake_events") or []
    if not events:
        return ""
    knowledge = gather_for_section("what_already_happened", data)
    n_events = len(events)
    return f"""{VOICE_GUIDELINES}

TASK: Write the "What Already Happened" section. {min(n_events, 7)} short paragraphs,
one per intake event the customer shared. ~120-180 words per event paragraph.

CHART DATA:
- Lagna: {data['lagna']['rashi']} {data['lagna']['degree']:.2f}°
- Moon: {data['moon']['rashi']} in {data['moon']['nakshatra']} Pada {data['moon']['pada']}

REFERENCE MATERIAL — the dasha + transit + Sade Sati signature active at EACH
event date. Use these to map the event back to a specific chart signature:
{knowledge}

WRITE: One paragraph per event in the order the customer listed them. Structure
each paragraph as:

  1. Open with the event in lived terms ("the nine-year stretch where money would
     not come" / "your grandmother's death in late 2024" / "the move to Vizag
     last year").
  2. Name the chart signature that was firing at that date — using the
     REFERENCE MATERIAL above for the EXACT MD/AD lord + their natal house +
     Sade Sati phase. Do NOT invent the signature — use what the dossier gives.
  3. Explain in plain language WHY that signature produces that kind of event.
     "Mercury is your 12th lord of loss + 9th lord of dharma; when 12L lord
     runs its own period, the chart pulls you toward learning instead of
     earning." This is the retrodictive proof.
  4. One closing sentence that reframes the event as the chart working, not
     the person failing.

VOICE REQUIREMENTS — CRITICAL:

- **Direct second-person.** "You" not "the native." Speak TO them.
- **Specific, never generic.** "Your grandmother died in late 2024 — the
  classical lunar eclipse of November 8, 2024 fell on your 8H Ketu" is good.
  "Family changes can happen during eclipses" is Barnum garbage — delete.
- **One CONCRETE chart fact per claim minimum.** No claim survives that has
  zero independent chart support.
- **Multi-factor convergence wins.** When two or three signatures stack
  (Sade Sati peak + AD lord activation + eclipse on natal placement), say so
  explicitly — that is what makes the reading uncanny.
- **No remedies, no rescue tone, no "you are healing."**
- **Citation discipline:** at most 1 italic classical citation across the
  whole section; NO trailing Sources footer.

Do NOT prefix with `## What Already Happened` — the template adds that.
Begin directly with the first event paragraph.

If the dossier returns "[NO INTAKE EVENTS PROVIDED]", output nothing — return
an empty string.
"""


def build_prompt_arc_so_far(data: dict[str, Any]) -> str:
    """Section 2 — narrative of past dasha periods leading to now."""
    md_seq = data["dasha"]["mahadasha_sequence"][:5]
    lines = []
    for m in md_seq:
        lord = m["lord"]
        lines.append(
            f"- {lord.title()} MD: {m['start'][:10]} -> {m['end'][:10]} ({m['years']:.1f}y)"
        )
    md_block = "\n".join(lines)
    natal_planets = data["natal_planets_dict"]
    placements = []
    for pname, p in natal_planets.items():
        sign_idx = int(p["longitude"] // 30) % 12
        placements.append(f"  {pname}: H{p['house']}, sign idx {sign_idx}")
    placements_block = "\n".join(placements)
    knowledge = gather_for_section("arc_so_far", data)

    return f"""{VOICE_GUIDELINES}

TASK: Write Section 2 ("The Arc So Far") — the narrative of how this person's
past dasha periods built who they are today. 250-400 words.

CHART DATA:
- Lagna: {data['lagna']['rashi']}
- Moon: {data['moon']['rashi']} in {data['moon']['nakshatra']} Pada {data['moon']['pada']}
- Birth: {data['birth']['datetime_human']}

NATAL PLACEMENTS (planet: house, sign):
{placements_block}

DASHA SEQUENCE (past + current):
{md_block}

REFERENCE MATERIAL — pull facts and language from THIS, not your training:
{knowledge}

WRITE: A 3-paragraph narrative. Paragraph 1: childhood/early dasha period and what
it built. Paragraph 2: middle period (often Saturn for late 20s/early 30s adults).
Paragraph 3: how they arrived at the current period and what's just behind them.

Reference specific dasha lords by name. Tie each period's themes to where that
lord is placed natally. Use the REFERENCE MATERIAL above for the actual themes
and effects — don't invent generalities. Cite BPHS/Phaladeepika where the
reference material gives you a specific source.
"""


def build_prompt_where_you_are_now(data: dict[str, Any]) -> str:
    """Section 3 — current state, today's reading."""
    sv = data["state_vector"]
    cur = data["dasha"]["current"]
    factors_summary = ", ".join(f"{f['short_name']}={f['score']:.1f}" for f in sv["factors"])
    top_areas = sorted(sv["areas"], key=lambda x: -x["score"])[:4]
    bottom_areas = sorted(sv["areas"], key=lambda x: x["score"])[:2]
    areas_top = ", ".join(f"{a['name']} ({a['score']:.1f})" for a in top_areas)
    areas_bot = ", ".join(f"{a['name']} ({a['score']:.1f})" for a in bottom_areas)
    sade = sv.get("sade_sati", {})

    knowledge = gather_for_section("where_you_are_now", data)
    return f"""{VOICE_GUIDELINES}

TASK: Write Section 3 ("Where You Are Now") — present-moment reading. 250-400 words.

NOW STATE:
- Composite: {sv['composite']:.1f}/10 ({sv['mental_state']})
- Mahadasha: {cur['mahadasha']['lord'].title()} ends {str(cur['mahadasha']['end_date'])[:10]}
- Antardasha: {cur['antardasha']['lord'].title()} ends {str(cur['antardasha']['end_date'])[:10]}
- Pratyantardasha: {cur['pratyantardasha']['lord'].title()}
- Factors today: {factors_summary}
- Top life areas right now: {areas_top}
- Weakest life areas: {areas_bot}
- Sade Sati: {sade.get('phase', 'not active')} {('(active)' if sade.get('active') else '')}

REFERENCE MATERIAL — pull facts and language from THIS, not your training:
{knowledge}

WRITE: 2-3 paragraphs.
- What this MD/AD combination ACTUALLY produces in daily life — use the
  REFERENCE MATERIAL's effects, not generic descriptions.
- What the high-score areas are signaling and what the low-score areas mean
  (don't catastrophize the low ones — name them).
- If Sade Sati is active, give one direct line about which phase and what it means.
- Cite (BPHS Ch.X) etc. only where the reference material provides a source.
"""


def build_prompt_answering_question(data: dict[str, Any]) -> str:
    """Section 4 — direct answer to user's submitted question."""
    q = data.get("user_question") or "What should I focus on right now?"
    sv = data["state_vector"]
    cur = data["dasha"]["current"]
    upcoming = data.get("upcoming_events", [])[:5]
    upc_block = "\n".join(
        f"  - {e.get('date', '?')[:10]}: {e.get('type', '?')} ({e.get('planet') or e.get('transit_planet') or '?'})"
        for e in upcoming
    )
    natal_planets = data["natal_planets_dict"]
    placements = "\n".join(f"  {p}: H{d['house']}" for p, d in natal_planets.items())
    knowledge = gather_for_section("answering_your_question", data)
    return f"""{VOICE_GUIDELINES}

TASK: Write Section 4 ("Answering Your Question") — directly answer the user's
question using their chart specifics. 300-450 words.

USER'S QUESTION: "{q}"

RELEVANT CHART CONTEXT:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']})
- Current dasha: {cur['mahadasha']['lord'].title()} MD / {cur['antardasha']['lord'].title()} AD
- Today's composite: {sv['composite']:.1f}/10 ({sv['mental_state']})
- Natal placements:
{placements}
- Upcoming triggers (next 90 days):
{upc_block}

REFERENCE MATERIAL (topic-aware, pulled for THIS user's question):
{knowledge}

WRITE: A direct answer to the question. Use the chart to back EVERY claim with a
specific placement, dasha, or transit. If the question is about a life domain
(career, marriage, money, etc.), pull the relevant area score AND the
REFERENCE MATERIAL's house-lord effects and karaka analysis.
If the question is open ("what should I focus on"), pick the SINGLE most
chart-aligned theme for the next 90 days and tell them in one sentence what
to do about it.

End with one specific date or window (within next 6 months) when something
relevant shifts.
"""


def build_prompt_next_12_months(data: dict[str, Any]) -> str:
    """Section 5 — year ahead forecast."""
    knowledge = gather_for_section("where_you_are_now", data)
    cur = data["dasha"]["current"]
    ad_seq = data["dasha"].get("current_md_antardashas", [])
    upcoming = data.get("upcoming_events", [])
    # Find AD shifts in next 12 months
    next_yr_ads: list[dict[str, Any]] = []
    from datetime import datetime, timedelta

    try:
        now = datetime.fromisoformat(data["meta"]["generated_at"])
        horizon = now + timedelta(days=365)
        for ad in ad_seq:
            ad_end = ad.get("end", "")
            if ad_end:
                ad_end_dt = (
                    datetime.fromisoformat(ad_end.replace("Z", "+00:00"))
                    if "T" in ad_end
                    else datetime.fromisoformat(ad_end + "T00:00:00+00:00")
                )
                # Normalize tz
                if now.tzinfo and not ad_end_dt.tzinfo:
                    ad_end_dt = ad_end_dt.replace(tzinfo=now.tzinfo)
                elif not now.tzinfo and ad_end_dt.tzinfo:
                    now = now.replace(tzinfo=ad_end_dt.tzinfo)
                if now <= ad_end_dt <= horizon:
                    next_yr_ads.append(ad)
    except Exception:
        pass
    ad_block = (
        "\n".join(f"  - {ad['lord'].title()} AD ends {ad['end'][:10]}" for ad in next_yr_ads)
        or "  (no AD shifts in the next 12 months)"
    )

    upc_block = "\n".join(
        f"  - {e.get('date','?')[:10]}: {e.get('type','?')} ({e.get('planet') or e.get('transit_planet','?')})"
        for e in upcoming[:15]
    )
    tp = data.get("tithi_pravesha") or {}
    tp_line = ""
    if tp:
        interp = tp.get("interpretation", {})
        tp_line = f"\nTithi Pravesha (lunar-year anniversary): {tp.get('tithi_pravesha_datetime', '?')[:10]}, year ruler: {interp.get('year_ruler', '?').title()}"

    return f"""TASK: Write Section 5 ("The Year Ahead — Next 12 Months") for paid 108 Life Reading. 400-600 words.

CHART CONTEXT:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']})
- Current dasha: {cur['mahadasha']['lord'].title()} MD / {cur['antardasha']['lord'].title()} AD (ends {str(cur['antardasha']['end_date'])[:10]})

AD SHIFTS IN NEXT 12 MONTHS:
{ad_block}

UPCOMING TRIGGERS (next 90 days, sorted):
{upc_block}
{tp_line}

REFERENCE MATERIAL:
{knowledge}

WRITE: A dated forecast covering the next 12 months. Bullet form acceptable for dated events; surrounding paragraphs for framing. Cover AD shifts, slow planet ingresses, Jupiter/Saturn natal aspects, eclipse-on-natal events, Sade Sati shifts, Tithi Pravesha if relevant. End with highest-leverage moment + worst-decision moment of the year.

OUTPUT: Markdown only. 400-600 words. No preamble.
"""


def build_prompt_hidden_strengths(data: dict[str, Any]) -> str:
    """Section 6 — yoga interpretation."""
    knowledge = gather_for_section("hidden_strengths", data) or gather_for_section(
        "where_you_are_now", data
    )
    yogas = data.get("yogas", [])
    yoga_summary = "\n".join(
        f"  - {y['name']} (strength {y.get('strength', '?')})" for y in yogas[:25]
    )
    vry = data.get("vry_yogas", [])
    vry_block = (
        "\n".join(
            f"  - {y['name']}: {y['lord_planet']} (lord of H{y['lord_of_house']}) in H{y['sits_in_house']}"
            for y in vry
        )
        if vry
        else "  (none detected)"
    )
    return f"""TASK: Write Section 6 ("Your Hidden Strengths") for a paid 108 Life Reading. 300-400 words.

CHART CONTEXT:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']})
- Current dasha: {data['dasha']['current']['mahadasha']['lord'].title()} MD / {data['dasha']['current']['antardasha']['lord'].title()} AD

DETECTED YOGAS (top 25):
{yoga_summary}

VIPREET RAJA YOGAS:
{vry_block}

REFERENCE MATERIAL (deep classical layers — Chara Karakas, Argala, Ashtakavarga, Shadbala, Nadi):
{knowledge}

WRITE: 300-400 words. Pick 3-5 most consequential yogas — Pancha Mahapurusha, Vipreet Raja, Raja, Dhana, Adhi, Gaja Kesari, Vargottama in priority order. Explain what each gives this native specifically (use placement details). End with 1-2 dormant yogas + when their dasha activates them.

Light bullet list allowed for the dormant-activation table. Otherwise narrative paragraphs.

OUTPUT: Markdown only. No preamble.
"""


def build_prompt_structural_challenges(data: dict[str, Any]) -> str:
    """Section 7 — dosha counselor."""
    knowledge = gather_for_section("structural_challenges", data) or gather_for_section(
        "where_you_are_now", data
    )
    doshas = data.get("doshas", [])
    if doshas:
        d_block = "\n".join(f"  - {d['name']} (severity: {d.get('severity', '?')})" for d in doshas)
    else:
        d_block = "  (no major doshas detected)"
    sade = data.get("state_vector", {}).get("sade_sati", {})
    sade_line = (
        f"\nSADE SATI: {sade.get('phase', '?').upper()} phase active"
        if sade.get("active")
        else "\nSADE SATI: not currently active"
    )
    yogas = data.get("yogas", [])
    afflictive_yogas = [
        y
        for y in yogas
        if any(
            bad in y.get("name", "").lower()
            for bad in ["daridra", "shoka", "arishta", "ashubha", "papa"]
        )
    ]
    aff_block = (
        "\n".join(f"  - {y['name']}" for y in afflictive_yogas) if afflictive_yogas else "  (none)"
    )
    return f"""TASK: Write Section 7 ("Structural Challenges") for a paid 108 Life Reading. 200-350 words.

CHART CONTEXT:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']}
- Current dasha: {data['dasha']['current']['mahadasha']['lord'].title()} MD

DETECTED DOSHAS:
{d_block}
{sade_line}

AFFLICTIVE YOGAS (challenge-pattern yogas):
{aff_block}

REFERENCE MATERIAL:
{knowledge}

WRITE: 200-350 words. Name the 2-4 doshas/afflictions that materially shape this life. For each: severity, what it ACTUALLY does in modern life, what eases or neutralizes it.

Bullet list for the dosha names + 1-2 sentence elaboration each. Surrounding paragraphs for framing and closing perspective.

CRITICAL: NO REMEDIES (no gemstones, mantras, pujas, rituals). Analytical only.

OUTPUT: Markdown only. No preamble.
"""


def build_prompt_what_to_do_next(data: dict[str, Any]) -> str:
    """Section 8 — three actions, one stop, one start."""
    sv = data["state_vector"]
    cur = data["dasha"]["current"]
    knowledge = gather_for_section("what_to_do_next", data)
    return f"""{VOICE_GUIDELINES}

TASK: Write Section 8 ("What To Do Next") — concrete actions. 200-300 words.

CURRENT CONTEXT:
- {cur['mahadasha']['lord'].title()} MD / {cur['antardasha']['lord'].title()} AD
- Composite: {sv['composite']:.1f}/10
- Strongest area today: {max(sv['areas'], key=lambda x: x['score'])['name']}
- Weakest area today: {min(sv['areas'], key=lambda x: x['score'])['name']}

REFERENCE MATERIAL — practical advice grounded in this dasha + chart:
{knowledge}

WRITE in this exact structure:

**3 things to start (specific, dated where possible):**
1. ...
2. ...
3. ...

**1 thing to stop:**
- ...

**1 thing to lean into (your structural strength):**
- ...

Make each action concrete enough to do this week. Tie each to a dasha/placement
when relevant. NO platitudes. NO "trust the universe" type lines.
"""


# ── API mode (production) ──


def generate_section_text(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    """Call Anthropic API with the prompt; return generated text.

    Used in production. Reads ANTHROPIC_API_KEY from env.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. For manual/subscription mode, use "
            "build_all_prompts() and feed prompts to Claude directly."
        )
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError("Install anthropic SDK: uv add anthropic") from exc

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    # extract text from first content block
    for block in msg.content:
        if hasattr(block, "text"):
            return block.text
    return ""


# ── Manual / subscription mode ──

# ── ADD-ON PROMPT BUILDERS ──


def build_prompt_past_5_years(data: dict[str, Any]) -> str:
    """Add-on: Past 5 Years Decoded."""
    knowledge = gather_for_section("arc_so_far", data)
    cur = data["dasha"]["current"]
    md_lord = cur["mahadasha"]["lord"]
    ad_seq = data["dasha"].get("current_md_antardashas", [])
    # Filter to ADs that overlapped the past 5 years
    from datetime import datetime, timedelta

    now = datetime.fromisoformat(data["meta"]["generated_at"])
    relevant_ads: list[str] = []
    for ad in ad_seq:
        try:
            end = (
                datetime.fromisoformat(ad["end"].replace("Z", "+00:00"))
                if "T" in ad["end"]
                else datetime.fromisoformat(ad["end"] + "T00:00:00+00:00")
            )
            start = (
                datetime.fromisoformat(ad["start"].replace("Z", "+00:00"))
                if "T" in ad["start"]
                else datetime.fromisoformat(ad["start"] + "T00:00:00+00:00")
            )
            if end.tzinfo and not now.tzinfo:
                now_aligned = now.replace(tzinfo=end.tzinfo)
            elif not end.tzinfo and now.tzinfo:
                now_aligned = now.replace(tzinfo=None)
                end = end
                start = start
            else:
                now_aligned = now
            five_aligned = now_aligned - timedelta(days=5 * 365.25)
            if start <= now_aligned and end >= five_aligned:
                relevant_ads.append(
                    f"  - {ad['lord'].title()} AD: {ad['start'][:10]} → {ad['end'][:10]}"
                )
        except Exception:
            continue
    ad_block = (
        "\n".join(relevant_ads) or f"  (Multiple ADs of {md_lord.title()} MD spanning past 5 years)"
    )
    return f"""TASK: Write the "Past 5 Years Decoded" add-on section for paid 108 Life Reading. 400-600 words.

CHART:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']})
- Current MD: {md_lord.title()}
- Today: {data['meta']['generated_at'][:10]}

ANTARDASHA SUB-PERIODS spanning the past 5 years:
{ad_block}

REFERENCE MATERIAL:
{knowledge}

WRITE: One paragraph per AD (3-6 ADs typical in 5-year window). For each AD:
- Name the AD lord + exact dates (start → end)
- What this sub-period TYPICALLY produces given AD lord's natal placement + relationship to MD lord
- Major slow transits during that AD window (Sade Sati phases, Jupiter/Saturn returns, eclipses)
- Translate to life-impact: what this AD likely BUILT or DISSOLVED in this person

Opening paragraph: frame the past 5 years as the texture of specific dashas + transits, not random.
Closing paragraph: the through-line of the 5 years; how the present sub-period is positioned relative to that arc.

Bullet form acceptable for AD-level entries; surrounding narrative for framing.

OUTPUT: Markdown only. 400-600 words. No preamble.
"""


def build_prompt_next_5_years(data: dict[str, Any]) -> str:
    """Add-on: Next 5 Years Map."""
    knowledge = gather_for_section("where_you_are_now", data)
    cur = data["dasha"]["current"]
    md_seq = data["dasha"]["mahadasha_sequence"]
    ad_seq = data["dasha"].get("current_md_antardashas", [])
    from datetime import datetime, timedelta

    now = datetime.fromisoformat(data["meta"]["generated_at"])
    horizon = now + timedelta(days=5 * 365.25)
    upcoming_ads: list[str] = []
    for ad in ad_seq:
        try:
            end = (
                datetime.fromisoformat(ad["end"].replace("Z", "+00:00"))
                if "T" in ad["end"]
                else datetime.fromisoformat(ad["end"] + "T00:00:00+00:00")
            )
            if end.tzinfo and not now.tzinfo:
                now_aligned = now.replace(tzinfo=end.tzinfo)
                horizon_aligned = horizon.replace(tzinfo=end.tzinfo)
            else:
                now_aligned = now
                horizon_aligned = horizon
            if now_aligned <= end <= horizon_aligned:
                upcoming_ads.append(f"  - {ad['lord'].title()} AD ends {ad['end'][:10]}")
        except Exception:
            continue
    ad_block = "\n".join(upcoming_ads) or "  (no AD shifts in next 5 years — same MD running)"

    # MD shifts in next 5 years
    md_shifts: list[str] = []
    for md in md_seq:
        try:
            end = (
                datetime.fromisoformat(md["end"])
                if "T" in md["end"]
                else datetime.fromisoformat(md["end"] + "T00:00:00")
            )
            if now.replace(tzinfo=None) <= end.replace(tzinfo=None) <= horizon.replace(tzinfo=None):
                md_shifts.append(
                    f"  - {md['lord'].title()} MD ends {md['end'][:10]} ({md['years']:.1f}y total)"
                )
        except Exception:
            continue
    md_block = "\n".join(md_shifts) or "  (current MD continues through entire 5-year window)"

    return f"""TASK: Write the "Next 5 Years Map" add-on section for paid 108 Life Reading. 500-700 words.

CHART:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']})
- Current dasha: {cur['mahadasha']['lord'].title()} MD / {cur['antardasha']['lord'].title()} AD
- Today: {data['meta']['generated_at'][:10]}

MAHADASHA SHIFTS in next 5 years:
{md_block}

ANTARDASHA SHIFTS in next 5 years:
{ad_block}

REFERENCE MATERIAL:
{knowledge}

WRITE: A 5-year strategic map. NOT a year-by-year forecast — a chapter-by-chapter view.

OPENING (3 sentences): name dominant MD + ADs spanning the window; name 1-2 slow planet transits running through it; classical maxim that frames it.

BODY (4-6 entries by year or AD):
- Year/AD label
- What it's structurally about for THIS native
- Major external triggers in that year (slow planet ingress, eclipse, Sade Sati transition, Saturn/Jupiter return)
- Practical implication: 1 sentence

If a Mahadasha shift happens in the 5 years, give it extra paragraph weight.

STRATEGIC WINDOWS section (3-5 dated):
- Cleanest year/window for major commitments
- Most challenging year/window
- Sade Sati / Dhaiya entries or exits
- Saturn return (~age 29-30) or Jupiter return (~age 12, 24, 36, 48, 60) if applicable

CLOSING (2-3 sentences): the 5-year arc as a single phase; the one decision to make NOW with this 5-year horizon.

OUTPUT: Markdown only. 500-700 words. No preamble.
"""


def build_prompt_lifetime(data: dict[str, Any]) -> str:
    """Add-on: Lifetime Overview."""
    knowledge = gather_for_section("arc_so_far", data)
    md_seq = data["dasha"]["mahadasha_sequence"]
    md_lines = "\n".join(
        f"  - {m['lord'].title()} MD: {m['start'][:10]} → {m['end'][:10]} ({m['years']:.1f}y)"
        for m in md_seq[:10]
    )
    natal = data["natal_planets_dict"]
    placements = "\n".join(f"  - {p}: H{d['house']}" for p, d in natal.items())

    return f"""TASK: Write the "Lifetime Overview" add-on section for paid 108 Life Reading. 700-900 words.

CHART:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']})
- Birth: {data['birth']['datetime_human']}

NATAL PLACEMENTS (planet → house):
{placements}

FULL VIMSHOTTARI MAHADASHA SEQUENCE (all 9 chapters):
{md_lines}

REFERENCE MATERIAL:
{knowledge}

WRITE: Walk through ALL 9 Mahadashas as the chapters of an entire life.

OPENING (2-3 sentences): frame the lifetime as a sequence of chapters, each carrying that MD lord's natal flavor.

BODY: ONE PARAGRAPH PER MD (9 paragraphs total, each 50-80 words):
- Name the MD lord + start/end years/ages
- Tie the period to where the lord sits natally
- One classical maxim governing this MD
- The likely texture of that chapter — what it built or will build

CLOSING (3-4 sentences):
- The shape of the lifetime as a whole — the through-line
- The peak chapter (the MD where the most can be made of this chart)
- One sentence: the moksha-pointing direction this chart suggests

NO bullet lists in this section — pure narrative paragraph structure.

OUTPUT: Markdown only. 700-900 words. No preamble.
"""


# ── DOMAIN DEEP-DIVE PROMPT BUILDERS ──


def _domain_prompt(domain: str, title: str, lenses_block: str, data: dict[str, Any]) -> str:  # noqa: ARG001
    knowledge = gather_for_section("answering_your_question", data)  # topic-aware
    natal = data["natal_planets_dict"]
    placements = "\n".join(f"  {p}: H{d['house']}" for p, d in natal.items())
    cur = data["dasha"]["current"]
    return f"""TASK: Write the "{title}" add-on deep-dive section for paid 108 Life Reading. 500-700 words.

CHART:
- Lagna: {data['lagna']['rashi']} | Moon: {data['moon']['rashi']} ({data['moon']['nakshatra']} P{data['moon']['pada']})
- Current dasha: {cur['mahadasha']['lord'].title()} MD / {cur['antardasha']['lord'].title()} AD
- Today: {data['meta']['generated_at'][:10]}

NATAL PLACEMENTS (planet → house):
{placements}

DOMAIN-SPECIFIC LENSES TO READ THROUGH:
{lenses_block}

REFERENCE MATERIAL (deep classical dossier):
{knowledge}

WRITE: 500-700 words. Follow your agent system-prompt's 4-section structure. Multi-lens synthesis. Modern voice. Cite classical sources from REFERENCE only. No remedies. No woo.

OUTPUT: Markdown only. No preamble.
"""


def build_prompt_career_deep_dive(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "career",
        "Career & Money Deep-Dive",
        """- 10H (karma bhava) + 10L placement + dignity
- Saturn (karaka of profession) — placement, dignity, conditions
- Sun (karaka of authority + government)
- Amatyakaraka (Jaimini career significator)
- D10 Dasamsha placements
- 2H + 11H for income, Jupiter as Dhana karaka
- Argala on 10H
- Ashtakavarga of 10H + native dasha lord
- Current dasha lord's relationship to career significators""",
        data,
    )


def build_prompt_relationships_deep_dive(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "relationships",
        "Relationships & Marriage",
        """- 7H (partnership bhava) + 7L placement + dignity
- Venus (karaka of marriage) — placement, dignity, conditions
- Darakaraka (Jaimini spouse significator)
- Upapada Lagna (UL) — marriage stability indicator
- 2nd from UL — sustenance of marriage
- 7th from UL — physical relationship
- D9 Navamsha — THE chart for marriage analysis
- Mangal Dosha + Kalatra Shoka detection
- Dasha sequences that classically activate marriage (when 7L/Venus/UL lord runs)""",
        data,
    )


def build_prompt_wealth_deep_dive(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "wealth",
        "Wealth & Money Architecture",
        """- Lakshmi yogas (rare wealth combinations)
- Dhana yogas (Lagna lord + 2L + 5L + 9L + 11L exchanges)
- Daridra yogas (poverty patterns from trine/kendra lords in dusthana)
- Vipreet Raja yogas (Harsha/Sarala/Vimala — wealth through difficulty)
- Jupiter (Dhana karaka) — full placement story
- Atmakaraka in D9 (Karakamsha) — soul's chosen wealth environment
- 2H + 11H + 9H structural strength
- Ancestral wealth themes (Pitra Dosha + 4H)
- Decade-by-decade wealth trajectory through Mahadasha sequence""",
        data,
    )


def build_prompt_health_deep_dive(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "health",
        "Health & Body",
        """- 1H (constitution) + 1L placement + dignity
- 6H (illness, recovery) + 6L placement
- 8H (chronic + longevity)
- 12H (hospitalization, sleep, isolation)
- Sun (vitality karaka)
- Moon (mental health)
- Saturn (chronic patterns + bones/joints)
- Mars (acute + blood/inflammation)
- Mercury (nervous system + skin)
- Ayurvedic dosha inferred from chart elements (vata/pitta/kapha)
- Current Mahadasha health profile (body parts affected per dasha lord)""",
        data,
    )


def build_prompt_spiritual_deep_dive(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "spiritual",
        "Spiritual Path & Dharma",
        """- 9H (dharma) + 9L placement + dignity
- 12H (moksha + spiritual practice)
- 5H (purva-punya, mantra capacity)
- Jupiter (dharma karaka)
- Ketu (moksha karaka)
- Atmakaraka (the soul significator — Jaimini's most important planet)
- Karakamsha (AK's D9 sign — soul's chosen environment)
- Ishta Devata (chart-specific deity-form from karakamsha)
- Spiritual yogas (Pravrajya, Tapasvi, Sannyasa)""",
        data,
    )


def build_prompt_children(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "children_deep_dive",
        "Children & Progeny",
        """- 5H (children) sign + occupants + 5L + dignity
- Jupiter (Putra karaka, the natural significator for children)
- Putrakaraka (Jaimini — the karaka FOR children specifically)
- D7 Saptamamsha if available — the dedicated divisional chart for children
- Karakamsha 5H view (5H from Atmakaraka's D9 sign)
- Dasha of 5L, Jupiter, Putrakaraka — these are the windows
- Jupiter transits to 5H or 5L as triggers
- 5H argala count; afflictions to 5H (especially Saturn, Rahu, Ketu)""",
        data,
    )


def build_prompt_education(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "education_deep_dive",
        "Education & Learning Path",
        """- 4H (foundation) + 4L + dignity (early-life learning)
- 5H (intellect, mantra capacity) + 5L
- 9H (higher knowledge, university, philosophy) + 9L
- Mercury (intellect karaka) + Jupiter (wisdom karaka)
- D24 Siddhamsha — the dedicated divisional chart for education
- Sudarshana 5H + 9H from Lagna AND Moon AND Sun (3-wheel confirmation for learning capacity)
- Dasha periods of Mercury, Jupiter, 4L, 5L, 9L — these are the education-active windows
- Foreign-education flags: 9H + 12H + Rahu intersections""",
        data,
    )


def build_prompt_foreign(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "foreign_settlement",
        "Foreign Settlement & Travel",
        """- 3H (short-distance, business travel) + 3L
- 9H (long-distance, philosophical/dharmic travel) + 9L
- 12H (foreign residence, dissolution-of-home) + 12L
- 4H lord condition — strong 4H means rooted; afflicted 4H means displacement
- Rahu placement and dignity — the foreign karaka in Vedic
- Moon (water travel, relocate karaka)
- Dasha of Rahu, 9L, 12L, or 4L afflictor — these are mobility windows
- Karaka-as-Lagna: Rahu's house from itself, planets in 9H/12H from karakas""",
        data,
    )


def build_prompt_property(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "property_vehicle",
        "Property & Vehicle Timing",
        """- 4H (immovable property + vehicles classically) + 4L
- Mars (real estate karaka — Bhumi karaka)
- Venus (vehicles + comfort goods karaka)
- 11H (gains, acquisitions, big purchases) + 11L
- Indu Lagna (wealth lagna) — its house from natal lagna shows where wealth lands
- Jupiter transit to 4H or 11H as acquisition windows
- Dasha of 4L, 11L, Mars, Venus
- Honest call-out on Daridra Yoga or 4H affliction if present""",
        data,
    )


def build_prompt_business(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "business_launch",
        "Business Launch & Entrepreneurship",
        """- 10H (career outlet) + 10L
- 7H (partnership in business — different signal than spouse 7H)
- 11H (gains, network, scale) + 11L
- 2H (cash flow, accumulated wealth) + 2L
- Mercury (commerce karaka, communication, contracts)
- Saturn (long-build discipline) vs Jupiter (expansion) vs Mars (energy/risk) — chart's risk profile
- Amatyakaraka (career karaka, Jaimini)
- D10 Dasamsha 10H
- Dasha of 10L, 11L, 2L, Amatyakaraka, Mercury — launch windows
- Avoid windows: 8H lord dasha, retrograde Mercury for contracts, Rahu MD without solid foundation""",
        data,
    )


def build_prompt_muhurta(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "muhurta_calendar",
        "Muhurta Calendar — Next 12 Months",
        """- Native's Janma Nakshatra + Tara Bala wheel (which Nakshatras are friendly)
- Vara Bala (which weekdays favor this native)
- Tithi compatibility with natal Moon
- Current Tithi Pravesha year-ruler
- Eclipse dates in next 12 months (avoid)
- Saturn/Mercury retrograde stations in next 12 months
- Current Mahadasha lord — favorable Muhurtas often align with MD lord transits
- For specific events: marriage (7L favorable transit), business (10L), property (4L, Jupiter to 4H), travel (3L/9L), surgery (Mars + 8L), naming/Gruha pravesha (Jupiter transits)""",
        data,
    )


def build_prompt_gem(data: dict[str, Any]) -> str:
    return _domain_prompt(
        "gem_prescription",
        "Gemstone Prescription",
        """- Lagna lord — for the primary Janma Ratna (life-stone)
- Atmakaraka — for the soul-significator gem
- Current Mahadasha lord — for the period-strengthening gem
- Yogakaraka (if 1L+9L or 9L+10L lord, etc.) — for the supreme benefic gem
- 6L / 8L / 12L identification — gems to AVOID (these planets shouldn't be amplified)
- Existing chart gem recommendations from the dossier's recommend_chart_remedies output if present
- Specifications: ratti weight (cite traditional minimum), metal (gold/silver/panchadhatu), finger, day, hand""",
        data,
    )


def build_prompt_compatibility(data: dict[str, Any]) -> str:
    """Compatibility add-on requires partner_birth in data; if absent, the
    agent itself writes the brief 'partner data needed' notice.
    """
    return _domain_prompt(
        "compatibility",
        "Compatibility — Kundali Matching",
        """- Partner birth details: check `data.get("partner_birth")` — if missing, write the brief notice
- Native's natal Moon nakshatra + pada
- Native's Mars condition (Mangal Dosha screen)
- 8-Kuta (Ashta Koota) components: Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi
- Synastry overlay — partner's planets onto native's houses
- Honest assessment — Kuta is a screen, not a verdict""",
        data,
    )


def build_prompt_sade_sati(data: dict[str, Any]) -> str:
    """Sade Sati deep-dive — Saturn's 7.5-year cycle through 12H/1H/2H from natal Moon.

    The agent reads the chart's current Sade Sati phase + dates, the prior
    cycle (~30 years prior), and Saturn's natal placement which modifies how
    the cycle lands.
    """
    sv = data.get("state_vector", {})
    sade = sv.get("sade_sati", {}) or {}
    natal_planets = data.get("natal_planets_dict", {})
    saturn = natal_planets.get("saturn", {})
    saturn_lon = float(saturn.get("longitude", 0.0))
    saturn_rashi_idx = int(saturn_lon // 30) % 12
    moon_rashi = data["moon"]["rashi"]
    moon_rashi_idx = [
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
    ].index(moon_rashi)

    # Try to compute precise phase dates
    phase_dates_block = (
        "(phase ingress dates not pre-computed; agent should fetch from MCP if needed)"
    )
    try:
        from packages.context.src.transits import get_sade_sati_dates

        sd = get_sade_sati_dates(moon_rashi_idx, saturn_rashi_idx)
        pd = sd.get("phase_dates", {})
        if pd:
            phase_dates_block = "\n".join(
                f"  {phase}: {info.get('start','?')} → {info.get('end','?')}"
                for phase, info in pd.items()
            )
    except Exception:
        pass

    knowledge = gather_for_section("sade_sati_deep_dive", data)

    return f"""{VOICE_GUIDELINES}

TASK: Write the Sade Sati deep-dive add-on. 650-900 words. Pure classical Parashari grounding. No woo, no remedies, no "the dreaded Sade Sati" clichés.

CHART DATA:
- Native: {data['birth']['full_name']}
- Lagna: {data['lagna']['rashi']}
- Natal Moon: {moon_rashi} (rashi idx {moon_rashi_idx})
- Natal Saturn: rashi idx {saturn_rashi_idx} ({['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][saturn_rashi_idx]}), house {saturn.get('house','?')}
- Sade Sati active right now: {sade.get('active', False)}
- Current phase: {sade.get('phase', 'n/a')}

PHASE INGRESS DATES (from ephemeris):
{phase_dates_block}

REFERENCE MATERIAL (deep classical layers — including Yogini, Vimshopaka, Sudarshana for cross-validation):
{knowledge}

WRITE: Follow the section structure in the agent definition. Use H3 sub-headings. State exact ingress dates. Compare to prior Sade Sati cycle if applicable (subtract ~30 years from current to find prior). Honour the no-remedies rule.

If Sade Sati is NOT active for this native, write the short "not currently active" version (2 paragraphs, prior + next cycle dates).
"""


# ── STITCHER PROMPT ──


def build_prompt_stitcher(data: dict[str, Any], section_narratives: dict[str, str]) -> str:
    """Build the stitcher prompt — runs LAST, after all section agents finish.

    Takes all section narratives + chart facts and produces two delimited blocks:
    cover_hook (4-6 sentences) and closing_cta (200-300 words).
    """
    cur = data["dasha"]["current"]
    sade = data["state_vector"].get("sade_sati", {})
    sade_line = (
        f"Sade Sati: {sade.get('phase', '?')} phase active"
        if sade.get("active")
        else "Sade Sati: not active"
    )
    yogas = ", ".join(y.get("name", "") for y in data.get("yogas", [])[:5])
    doshas = ", ".join(
        f"{d.get('name','?')} ({d.get('severity','?')})" for d in data.get("doshas", [])[:3]
    )
    vry = ", ".join(y["name"] for y in data.get("vry_yogas", []))

    # Section narratives in order
    sections_order = [
        "arc_so_far",
        "where_you_are_now",
        "answering_your_question",
        "next_12_months",
        "hidden_strengths",
        "structural_challenges",
        "what_to_do_next",
    ]
    sections_block = ""
    for sid in sections_order:
        if sid in section_narratives:
            title = sid.replace("_", " ").title()
            sections_block += f"\n\n=== SECTION: {title} ===\n{section_narratives[sid][:2500]}\n"

    return f"""TASK: Final-pass stitcher for {data['birth']['full_name']}'s 108 Life Reading. You are spawned LAST in the pipeline.

CUSTOMER:
- Name: {data['birth']['full_name']}
- Born: {data['birth']['datetime_human']}
- Lagna: {data['lagna']['rashi']}
- Moon: {data['moon']['rashi']} in {data['moon']['nakshatra']} Pada {data['moon']['pada']}
- Current: {cur['mahadasha']['lord'].title()} Mahadasha / {cur['antardasha']['lord'].title()} Antardasha (ends {str(cur['antardasha']['end_date'])[:10]})
- {sade_line}

KEY CHART FACTS:
- Top yogas: {yogas}
- Vipreet Raja Yogas: {vry or '(none)'}
- Doshas: {doshas or '(none significant)'}

USER'S QUESTION (their reason for buying): "{data.get('user_question', '')}"

═══════════════════════════════════════════════════════════════
ALL SECTION NARRATIVES (read all before writing):
═══════════════════════════════════════════════════════════════
{sections_block}

═══════════════════════════════════════════════════════════════
YOUR OUTPUT — EXACTLY TWO DELIMITED BLOCKS:
═══════════════════════════════════════════════════════════════

===COVER_HOOK_START===
<4-6 sentences. Personalized to THIS chart. Sets the emotional + intellectual frame for the whole report. Reader reads this on page 1 — first 10 seconds decide if they trust the product. NO bullet lists. NO woo.>
===COVER_HOOK_END===

===CLOSING_CTA_START===
### The three moves that matter most

1. **[Action 1]** — single-sentence rationale tied to a specific placement/dasha.
2. **[Action 2]** — same.
3. **[Action 3]** — same.

### The one date to circle

**[Specific date or window]** — what shifts then, what to do, what to avoid.

### A final word

[3-4 sentences. Tie the whole reading together. Honor difficulty. Don't catastrophize. Don't oversell. End on a quotable line.]
===CLOSING_CTA_END===

===PULL_QUOTES_START===
arc_so_far: <one memorable line, 12-22 words, extracted or distilled from that section's narrative. Plain text, no markdown.>
where_you_are_now: <one memorable line>
answering_your_question: <one memorable line>
next_12_months: <one memorable line>
hidden_strengths: <one memorable line>
structural_challenges: <one memorable line>
what_to_do_next: <one memorable line>
===PULL_QUOTES_END===

CONSTRAINTS:
- Every action must be dated or doable within next 4 weeks
- NO remedies (no gemstones, mantras, pujas)
- NO repeating yoga names or dates more than twice
- Pull-quotes: ONE line per section. 12-22 words. The line a friend would screenshot and send.
- Do NOT echo a section heading as the pull-quote. It must be a sentence from the body — chart-specific, not generic.
- ONLY the three delimited blocks, no preamble, no signoff
"""


def parse_stitcher_output(output: str) -> dict[str, Any]:
    """Parse the stitcher's three-block output into a dict.

    Returns:
        {
            "cover_hook": str,
            "closing_cta": str,
            "pull_quotes": {section_id: str, ...},
        }

    Empty values if delimiters not found.
    """
    import re

    result: dict[str, Any] = {"cover_hook": "", "closing_cta": "", "pull_quotes": {}}
    m = re.search(r"===COVER_HOOK_START===\s*(.*?)\s*===COVER_HOOK_END===", output, re.DOTALL)
    if m:
        result["cover_hook"] = m.group(1).strip()
    m = re.search(r"===CLOSING_CTA_START===\s*(.*?)\s*===CLOSING_CTA_END===", output, re.DOTALL)
    if m:
        result["closing_cta"] = m.group(1).strip()
    m = re.search(r"===PULL_QUOTES_START===\s*(.*?)\s*===PULL_QUOTES_END===", output, re.DOTALL)
    if m:
        pq_block = m.group(1).strip()
        quotes: dict[str, str] = {}
        for line in pq_block.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            sid, _, quote = line.partition(":")
            sid = sid.strip()
            quote = quote.strip().strip('"').strip("'")
            # Skip placeholder lines that still carry angle-bracket markers
            if not quote or quote.startswith("<"):
                continue
            quotes[sid] = quote
        result["pull_quotes"] = quotes
    return result


def build_all_prompts(data: dict[str, Any]) -> dict[str, str]:
    """Build prompts for every narrative section + any active add-ons.

    Base report always emits the 7 core sections. Add-ons in
    data["addons"] (e.g. ["past_5_years", "next_5_years", "lifetime"])
    add their own prompts.
    """
    prompts = {
        "arc_so_far": build_prompt_arc_so_far(data),
        "where_you_are_now": build_prompt_where_you_are_now(data),
        "answering_your_question": build_prompt_answering_question(data),
        "next_12_months": build_prompt_next_12_months(data),
        "hidden_strengths": build_prompt_hidden_strengths(data),
        "structural_challenges": build_prompt_structural_challenges(data),
        "what_to_do_next": build_prompt_what_to_do_next(data),
    }
    # Conditional: only add what_already_happened prompt if customer provided
    # intake events (otherwise the section is skipped silently)
    if data.get("intake_events"):
        prompts["what_already_happened"] = build_prompt_what_already_happened(data)
    addons = data.get("addons", []) or []
    addon_builders = {
        "past_5_years": build_prompt_past_5_years,
        "next_5_years": build_prompt_next_5_years,
        "lifetime": build_prompt_lifetime,
        "career_deep_dive": build_prompt_career_deep_dive,
        "relationships_deep_dive": build_prompt_relationships_deep_dive,
        "wealth_deep_dive": build_prompt_wealth_deep_dive,
        "health_deep_dive": build_prompt_health_deep_dive,
        "spiritual_deep_dive": build_prompt_spiritual_deep_dive,
        # NEW high-demand add-ons (Session 53)
        "children_deep_dive": build_prompt_children,
        "education_deep_dive": build_prompt_education,
        "foreign_settlement": build_prompt_foreign,
        "property_vehicle": build_prompt_property,
        "business_launch": build_prompt_business,
        "muhurta_calendar": build_prompt_muhurta,
        "gem_prescription": build_prompt_gem,
        "compatibility": build_prompt_compatibility,
        # year_ahead is already in core (next_12_months)
    }
    # Conditional BASE section — auto-fires when Sade Sati is active.
    # Built here (not in addons dict) because customer doesn't pick it.
    sade = (data.get("state_vector") or {}).get("sade_sati") or {}
    if sade.get("active"):
        prompts["sade_sati_deep_dive"] = build_prompt_sade_sati(data)
    for addon in addons:
        builder = addon_builders.get(addon)
        if builder:
            prompts[addon] = builder(data)
    return prompts


def quick_voice_intro(data: dict[str, Any]) -> str:
    """Section 1 opening blurb — non-AI, derived from voice helpers.

    Sets the chart's lagna/moon character. No today-focus content — that
    lives in the daily app, not in the paid report.
    """
    lagna = data["lagna"]["rashi"].lower()
    moon = data["moon"]["rashi"].lower()
    lagna_line = LAGNA_DESCRIPTORS.get(lagna, "")
    moon_line = MOON_DESCRIPTORS.get(moon, "")
    return f"\n\n**Outwardly:** {lagna_line}.  \n" f"**Inwardly:** {moon_line}."


def quick_who_you_are(data: dict[str, Any]) -> str:
    """Section 1 supplement — yoga voice descriptions."""
    yogas = data.get("yogas", [])[:5]
    out = []
    for y in yogas:
        phrase = yoga_phrase(y["name"])
        if phrase:
            out.append(f"- **{y['name']}** — {phrase}")
        else:
            out.append(f"- **{y['name']}**")
    if not out:
        return ""
    return "\n\n**What these mean in plain English:**\n" + "\n".join(out)


def quick_who_you_are_planets(data: dict[str, Any]) -> str:
    """Section 1 supplement — planet-house plain-language placements."""
    natal = data["natal_planets_dict"]
    out: list[str] = []
    for pname, p in natal.items():
        phrase = planet_house_phrase(pname, p["house"])
        if phrase:
            out.append(f"- **{pname.title()} in House {p['house']}** — {phrase}")
    if not out:
        return ""
    return "\n\n**Your strongest placement signals:**\n" + "\n".join(out[:4])
