"""Chart-Specific Question Generator (CSQG).

Pure function: chart_data → list of 5-7 questions tailored to THIS chart's
loudest signatures. Used in the customer-onboarding flow:

    1. Customer pays, submits birth details (date/time/place)
    2. We compute chart instantly
    3. CSQG scans the chart for signatures that *predict specific life events*
       and emits one question per signature it finds
    4. We rank by signature strength and pick top 5-7
    5. Send via WhatsApp / email; customer replies
    6. Replies become `intake_events` fed back into the report engine
    7. Generate report grounded in verified events

The CSQG must NOT use any external knowledge of the customer (their story, what
they said in conversation, what previous reports said). It works on the chart
data only — same input every operator gets.

Each detection rule:
    - Scans chart_data for one specific signature
    - If signature present: emits a Question with the underlying reasoning
    - The reasoning is NOT shown to customer — it's audit trail for operator

This file is intentionally rule-by-rule and easy to extend. Add a new rule by
writing a function that returns a Question (or None) given chart_data.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Question:
    """A chart-derived question for the customer.

    Attributes:
        category: Broad area (family, money, career, spirituality, etc.)
        text: The actual question, WhatsApp-friendly. <200 chars.
        signature: Internal chart reasoning, NOT shown to customer.
            Operator/audit can see why this question fires.
        strength: 0.0 - 1.0. How structurally loud this signature is.
            Used to rank/pick top N.
        expected_answer_type: One of "yes_no", "year", "brief", "details".
        intake_event_type: What event_type the answer maps to in
            intake_events JSON (so the report can reuse it).
    """

    category: str
    text: str
    signature: str
    strength: float
    expected_answer_type: str
    intake_event_type: str


# ── Helper accessors ──────────────────────────────────────────────────


def _planet(chart: dict, name: str) -> dict | None:
    return (chart.get("natal_planets_dict") or {}).get(name)


def _house_of(chart: dict, planet: str) -> int | None:
    p = _planet(chart, planet)
    return p.get("house") if p else None


def _lagna_sign(chart: dict) -> str | None:
    return (chart.get("lagna") or {}).get("rashi")


def _ruler_of_house(lagna_sign: str, house: int) -> str | None:
    """Return the planet that rules the Nth house from this Lagna."""
    rulers = {
        "Aries": [
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
        ],
        "Taurus": [
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
        ],
        "Gemini": [
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
        ],
        "Cancer": [
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
        ],
        "Leo": [
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
        ],
        "Virgo": [
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
        ],
        "Libra": [
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
        ],
        "Scorpio": [
            "mars",
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
        ],
        "Sagittarius": [
            "jupiter",
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
        ],
        "Capricorn": [
            "saturn",
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
        ],
        "Aquarius": [
            "saturn",
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
        ],
        "Pisces": [
            "jupiter",
            "mars",
            "venus",
            "mercury",
            "moon",
            "sun",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "saturn",
        ],
    }
    seq = rulers.get(lagna_sign)
    if not seq or not (1 <= house <= 12):
        return None
    return seq[house - 1]


def _is_debilitated(chart: dict, planet: str) -> bool:
    """True if planet is in its sign of debilitation."""
    p = _planet(chart, planet)
    if not p:
        return False
    lon = float(p.get("longitude", 0))
    sign = int(lon // 30) % 12
    debilitation = {
        "sun": 6,
        "moon": 7,
        "mars": 3,
        "mercury": 11,
        "jupiter": 9,
        "venus": 5,
        "saturn": 0,
    }
    return debilitation.get(planet) == sign


def _is_exalted(chart: dict, planet: str) -> bool:
    p = _planet(chart, planet)
    if not p:
        return False
    lon = float(p.get("longitude", 0))
    sign = int(lon // 30) % 12
    exaltation = {
        "sun": 0,
        "moon": 1,
        "mars": 9,
        "mercury": 5,
        "jupiter": 3,
        "venus": 11,
        "saturn": 6,
    }
    return exaltation.get(planet) == sign


def _is_retrograde(chart: dict, planet: str) -> bool:
    p = _planet(chart, planet)
    return bool(p and p.get("is_retrograde"))


def _conjuncts(chart: dict, p1: str, p2: str, orb_signs: int = 0) -> bool:
    """True if two planets share a sign (orb_signs=0) or are within orb."""
    a = _planet(chart, p1)
    b = _planet(chart, p2)
    if not a or not b:
        return False
    sa = int(float(a["longitude"]) // 30) % 12
    sb = int(float(b["longitude"]) // 30) % 12
    return abs(sa - sb) <= orb_signs


def _current_md_lord(chart: dict) -> str | None:
    cur = (chart.get("dasha") or {}).get("current") or {}
    return (cur.get("mahadasha") or {}).get("lord")


def _current_ad_lord(chart: dict) -> str | None:
    cur = (chart.get("dasha") or {}).get("current") or {}
    return (cur.get("antardasha") or {}).get("lord")


def _age_now(chart: dict) -> float:
    birth = datetime.fromisoformat(chart["birth"]["datetime"])
    if birth.tzinfo:
        birth = birth.replace(tzinfo=None)
    now = datetime.fromisoformat(chart["meta"]["generated_at"])
    if now.tzinfo:
        now = now.replace(tzinfo=None)
    return (now - birth).days / 365.25


def _sade_sati(chart: dict) -> dict:
    return (chart.get("state_vector") or {}).get("sade_sati") or {}


# ── Detection rules (each emits 0 or 1 question) ──────────────────────


def rule_sade_sati(chart: dict) -> Question | None:
    s = _sade_sati(chart)
    if not s.get("active"):
        return None
    phase = s.get("phase", "")
    text = (
        "The chart shows you may be living through (or just finishing) a heavier-than-usual "
        "phase the last 2-3 years — slower than your friends, more tired, more things ending "
        "than starting. Has the last few years felt that way? Roughly which year did the heaviness "
        "start, and is it lifting now?"
    )
    return Question(
        category="life_phase",
        text=text,
        signature=f"Sade Sati {phase} phase active on natal Moon",
        strength=0.9,
        expected_answer_type="brief",
        intake_event_type="long_phase",
    )


def rule_sun_rahu_or_ketu_axis(chart: dict) -> Question | None:
    """Sun-Rahu or Sun-Ketu conjunction surfaces father/family-secret patterns."""
    if _conjuncts(chart, "sun", "rahu") or _conjuncts(chart, "sun", "ketu"):
        h = _house_of(chart, "sun") or 0
        house_themes = {
            1: "your own identity",
            2: "family wealth and inherited money",
            4: "home and mother",
            5: "creativity or children",
            7: "marriage",
            8: "shared resources and hidden things",
            9: "father and dharma",
            10: "career and public role",
            11: "gains",
        }
        h_theme = house_themes.get(h, f"the area of house {h}")
        text = (
            "Your chart shows a complicated relationship to authority or your father — "
            f"the kind that often plays out around {h_theme}. Was there a moment in your life "
            "where you learned something about your father (or a father-figure like a boss, "
            "elder, mentor) that shifted how you saw them — money trouble, a hidden chapter, "
            "a separation, something not spoken openly? Roughly which year?"
        )
        return Question(
            category="father_authority",
            text=text,
            signature=f"Sun-Rahu/Ketu conjunction in H{h}",
            strength=0.85,
            expected_answer_type="brief",
            intake_event_type="father_revelation",
        )
    return None


def rule_debilitated_2l_or_11l(chart: dict) -> Question | None:
    """Debilitated wealth/gains lords surface income drought patterns."""
    lagna = _lagna_sign(chart) or ""
    l2 = _ruler_of_house(lagna, 2)
    l11 = _ruler_of_house(lagna, 11)
    candidates = []
    if l2 and _is_debilitated(chart, l2):
        candidates.append(("2nd lord (wealth)", l2))
    if l11 and _is_debilitated(chart, l11):
        candidates.append(("11th lord (gains)", l11))
    if not candidates:
        return None
    label, planet = candidates[0]
    text = (
        "The chart suggests money has not come easily — the planet that governs your earnings "
        "is structurally compromised at birth, so paid work has likely required more effort "
        "and produced less return than your peers' careers. Has there been a stretch of months "
        "or years where income simply wouldn't come, even though you were trying? Roughly which "
        "years?"
    )
    return Question(
        category="finance",
        text=text,
        signature=f"{label} {planet} debilitated",
        strength=0.85,
        expected_answer_type="brief",
        intake_event_type="financial_drought",
    )


def rule_mercury_rules_9_and_12(chart: dict) -> Question | None:
    """Mercury as 9L AND 12L → strong pull toward spiritual/inward learning periods."""
    lagna = _lagna_sign(chart) or ""
    l9 = _ruler_of_house(lagna, 9)
    l12 = _ruler_of_house(lagna, 12)
    if l9 == "mercury" and l12 == "mercury":
        text = (
            "Your chart structurally pulls you toward stretches of inward learning — reading, "
            "searching, dropping into questions about meaning rather than chasing markets. Was "
            "there a recent period (the last 2-3 years) where you went deep into spirituality, "
            "philosophy, self-inquiry, or scripture — reading a lot, then either stopping suddenly "
            "or quietly losing the appetite? Roughly when?"
        )
        return Question(
            category="spiritual",
            text=text,
            signature="Mercury rules 9L AND 12L (rare convergence)",
            strength=0.8,
            expected_answer_type="brief",
            intake_event_type="spiritual_shift",
        )
    return None


def rule_ketu_in_8h(chart: dict) -> Question | None:
    """Ketu in 8H → sudden hidden change, things resurfacing from past."""
    if _house_of(chart, "ketu") == 8:
        text = (
            "The chart shows a signature for sudden, unplanned re-emergence of things from your "
            "past — old people, old projects, old places that show up unexpectedly and pull you "
            "into something. In the last 1-2 years, did someone or something from 5+ years ago "
            "come back and change your direction (a job, a move, a relationship, an offer)? "
            "Briefly what happened?"
        )
        return Question(
            category="hidden_change",
            text=text,
            signature="Ketu in 8H — sudden hidden re-emergence",
            strength=0.8,
            expected_answer_type="brief",
            intake_event_type="hidden_change",
        )
    return None


def rule_recent_dasha_change(chart: dict) -> Question | None:
    """A Mahadasha shift in the last 3 years surfaces an identity transition."""
    cur = (chart.get("dasha") or {}).get("current") or {}
    md = cur.get("mahadasha") or {}
    start = md.get("start_date")
    if not start:
        return None
    try:
        start_dt = start if hasattr(start, "year") else datetime.fromisoformat(str(start))
        if start_dt.tzinfo:
            start_dt = start_dt.replace(tzinfo=None)
        now = datetime.fromisoformat(chart["meta"]["generated_at"])
        if now.tzinfo:
            now = now.replace(tzinfo=None)
        years_since = (now - start_dt).days / 365.25
        if years_since > 5:
            return None
        text = (
            f"The chart shifted into a major new life-phase around {start_dt.year}. People "
            "usually notice it as: something they'd been doing for years suddenly ended (job, "
            "relationship, city, identity), and something new started feeling possible. Did "
            f"something like that happen for you around late {start_dt.year} or early {start_dt.year + 1}? "
            "Briefly what?"
        )
        return Question(
            category="identity_transition",
            text=text,
            signature=f"Mahadasha shift to {md.get('lord', '?').title()} on {start_dt.date()}",
            strength=0.75,
            expected_answer_type="brief",
            intake_event_type="career_change",
        )
    except Exception:
        return None


def rule_saturn_return_window(chart: dict) -> Question | None:
    """Saturn return at age 28-30 → adult identity laydown."""
    age = _age_now(chart)
    if not (29 <= age <= 35):
        return None
    text = (
        "Most adults go through a structural identity reset between roughly age 28 and 31 — "
        "the version of themselves they'd been holding together for other people quietly falls "
        "apart, and what survives is the version that's actually theirs. Did you feel a shift "
        "like this between roughly 2020 and 2023 — relationships ending, jobs ending, friend "
        "groups changing, a sense of becoming someone new? Roughly when did the shift land?"
    )
    return Question(
        category="identity_transition",
        text=text,
        signature="Saturn return window age 28-30 (Saturn transiting natal Saturn)",
        strength=0.7,
        expected_answer_type="brief",
        intake_event_type="identity_shift",
    )


def rule_sade_sati_setting_phase_elder(chart: dict) -> Question | None:
    """Sade Sati setting phase + Saturn in family-house often = elder loss."""
    s = _sade_sati(chart)
    if not (s.get("active") and s.get("phase") in ("peak", "setting")):
        return None
    sat_house = _house_of(chart, "saturn") or 0
    if sat_house in (4, 2):  # family/home houses
        text = (
            "The chart shows a window where the family elder generation often releases. Did you "
            "lose a grandparent (or another significant elder, like a parent's sibling) in the "
            "last 2-3 years? Roughly which year and month?"
        )
        return Question(
            category="family",
            text=text,
            signature=f"Sade Sati {s.get('phase')} + Saturn in H{sat_house} (family axis)",
            strength=0.85,
            expected_answer_type="brief",
            intake_event_type="elder_death",
        )
    return None


def rule_mars_debilitated_7_or_10(chart: dict) -> Question | None:
    """Mars debilitated in career/partnership houses → struggles there."""
    h = _house_of(chart, "mars") or 0
    if _is_debilitated(chart, "mars") and h in (7, 10):
        retro_note = (
            " (the chart partially redeems this through retrograde — Neecha Bhanga)"
            if _is_retrograde(chart, "mars")
            else ""
        )
        if h == 7:
            text = (
                "The chart shows a signature where partnerships — romantic or business — often "
                "leave you carrying more of the emotional or operational load than the other person, "
                f"sometimes without realising it{retro_note}. Has there been a partnership in the last "
                "few years where you felt this play out? Briefly what happened?"
            )
            cat = "relationships"
            ev_type = "relationship_strain"
        else:
            text = (
                "The chart shows a signature where the career-engine is structurally compromised — "
                "you push harder than your peers for less return, particularly in commercial work "
                f"like sales, negotiation, or pricing your own services{retro_note}. Has career or "
                "income negotiations been a recurring struggle for you? Briefly what's the texture?"
            )
            cat = "career"
            ev_type = "career_struggle"
        return Question(
            category=cat,
            text=text,
            signature=f"Mars debilitated in H{h}{' (Neecha Bhanga via retrograde)' if _is_retrograde(chart, 'mars') else ''}",
            strength=0.75,
            expected_answer_type="brief",
            intake_event_type=ev_type,
        )
    return None


def rule_jupiter_in_12(chart: dict) -> Question | None:
    """Jupiter in 12H → foreign, retreat, expansion through dissolution."""
    if _house_of(chart, "jupiter") == 12:
        text = (
            "The chart shows expansion and growth often arrive for you through unconventional "
            "channels — foreign-flavoured work, retreats, periods of being away from your usual "
            "circles, or things you do behind the scenes. Has there been a foreign or retreat-shaped "
            "stretch in the last 3-5 years that quietly changed you? Roughly which years?"
        )
        return Question(
            category="foreign_retreat",
            text=text,
            signature="Jupiter in H12 — growth through dissolution/foreign",
            strength=0.65,
            expected_answer_type="brief",
            intake_event_type="foreign_or_retreat",
        )
    return None


def rule_current_ketu_period(chart: dict) -> Question | None:
    """Current AD/PD is Ketu → quiet emptying."""
    if _current_ad_lord(chart) == "ketu":
        text = (
            "The chart shows you're in the closing months of a quietly emptying sub-period — old "
            "definitions of yourself, old certainties, possibly even close friendships have been "
            "softly losing their grip without a clear reason. Does the last 6-12 months feel like "
            "things are quietly emptying out? Briefly what's let go?"
        )
        return Question(
            category="current_phase",
            text=text,
            signature="Current Antardasha = Ketu (dissolution sub-period)",
            strength=0.7,
            expected_answer_type="brief",
            intake_event_type="recent_dissolution",
        )
    return None


def rule_lagna_at_cusp(chart: dict) -> Question | None:
    """Lagna within 2° of sign boundary → birth-time verification needed."""
    lagna = chart.get("lagna") or {}
    deg = float(lagna.get("degree", 15.0))
    if deg <= 2.0 or deg >= 28.0:
        adjacent = "previous" if deg <= 2.0 else "next"
        text = (
            f"Your birth time places your rising sign very close to a sign-cusp ({deg:.1f}° "
            f"into {lagna.get('rashi', '?')}). This means some astrologers and apps might show "
            f"your rising as the {adjacent} sign instead. To confirm: have any prior astrology "
            "readings (apps, family pandits, paid reports) ever shown a different rising sign for "
            "you? If yes, which sign? This helps us lock the chart precisely."
        )
        return Question(
            category="birth_time_check",
            text=text,
            signature=f"Lagna at cusp: {deg:.1f}° {lagna.get('rashi', '?')}",
            strength=0.95,  # always include cusp checks — critical for accuracy
            expected_answer_type="brief",
            intake_event_type="birth_time_check",
        )
    return None


def rule_stellium_in_house(chart: dict) -> Question | None:
    """3+ planets sharing a house = a house running unusually loud.

    Fires for most charts — stelliums are common striking features. The
    question's framing changes by house theme.
    """
    counts: dict[int, list[str]] = {}
    for name, p in (chart.get("natal_planets_dict") or {}).items():
        h = p.get("house")
        if not h or name in ("rahu", "ketu"):
            # Exclude nodes from stellium count (they're shadow points, count separately)
            continue
        counts.setdefault(h, []).append(name)
    # Find loudest stellium
    best = max(counts.items(), key=lambda kv: len(kv[1]), default=(None, []))
    if not best[0] or len(best[1]) < 3:
        return None
    house, planets = best
    house_themes = {
        1: (
            "identity / how you show up",
            "a phase where everyone around you was projecting different versions of who you were",
        ),
        2: (
            "family money and what gets said",
            "a period where family money, inheritance, or arguments around it dominated your life",
        ),
        3: (
            "courage and effort",
            "a stretch where you had to fight for every small win — siblings, short journeys, sheer effort years",
        ),
        4: (
            "home, mother, inner ground",
            "a chapter of unusual focus on the home — the mother, the physical house, where you lived",
        ),
        5: ("creativity and children", "a creative or romantic chapter that was wildly active"),
        6: (
            "daily friction, work, debts",
            "a long stretch where daily problems, debts, or health absorbed most of your energy",
        ),
        7: (
            "partnership and the public",
            "a partnership or public-facing chapter that defined a decade",
        ),
        8: (
            "transformation and hidden things",
            "a multi-year stretch of buried changes, sudden gains, inheritances, secret financial pressure, or near-occult interest",
        ),
        9: (
            "dharma, father, higher learning",
            "a chapter where philosophy, scripture, the father, or a teacher took the spotlight",
        ),
        10: (
            "career and public role",
            "a career chapter where you were over-extended — too many roles in too many directions at once",
        ),
        11: (
            "gains and friendships",
            "a period where a network of friends became unusually important — for income, for direction, for everything",
        ),
        12: (
            "loss, foreign, dissolution",
            "a stretch where things quietly fell away — savings, certainties, places, people — without you fully noticing",
        ),
    }
    theme, lived = house_themes.get(
        house, (f"the area of house {house}", "something that kept replaying for years")
    )
    text = (
        f"The chart shows an unusual concentration of planetary energy in one specific area of your "
        f"life — {theme}. The texture of this is usually: {lived}. Does any of that ring true? "
        f"Roughly which years was this loudest, and what was happening?"
    )
    return Question(
        category=f"stellium_h{house}",
        text=text,
        signature=f"{len(planets)}-planet stellium in H{house}: {', '.join(p.title() for p in planets)}",
        strength=0.72,
        expected_answer_type="brief",
        intake_event_type="long_phase",
    )


def rule_combust_md_or_atmakaraka(chart: dict) -> Question | None:
    """If current MD lord is combust OR Atmakaraka is combust, ask about the
    'overshadowed engine' lived signature."""
    # Combustion: planet within ~10° of Sun (variable by planet, simplified)
    sun = _planet(chart, "sun")
    if not sun:
        return None
    sun_lon = float(sun.get("longitude", 0))
    combust_orbs = {
        "mercury": 14.0,
        "venus": 10.0,
        "mars": 17.0,
        "jupiter": 11.0,
        "saturn": 15.0,
        "moon": 12.0,
    }
    md_lord = _current_md_lord(chart)
    if not md_lord or md_lord in ("sun", "rahu", "ketu"):
        return None
    p = _planet(chart, md_lord)
    if not p:
        return None
    p_lon = float(p.get("longitude", 0))
    diff = abs(p_lon - sun_lon)
    if diff > 180:
        diff = 360 - diff
    orb = combust_orbs.get(md_lord, 10.0)
    if diff > orb:
        return None
    text = (
        f"Your current life-period (the next several years) is governed by a planet — {md_lord.title()} — "
        f"that sits very close to the Sun in your birth chart, technically *combust*. The classical "
        f"reading is that this planet's themes feel constantly *obscured by something brighter* — "
        f"the period gives, but quietly, almost invisibly, like work that gets credited to someone "
        f"else, or value you create that isn't visibly priced. Does the texture of the last 1-3 years "
        f"have that feel — you've been producing, but recognition or money has lagged the actual work?"
    )
    return Question(
        category="current_phase_combust",
        text=text,
        signature=f"Current MD lord {md_lord.title()} combust (orb {diff:.1f}°)",
        strength=0.78,
        expected_answer_type="brief",
        intake_event_type="long_phase",
    )


def rule_yogakaraka_strength(chart: dict) -> Question | None:
    """For charts where lagna has a clear yogakaraka planet, check if it's
    strong (own sign / exalted) and in a kendra/trikona. This is one of the
    most consequential chart signatures."""
    YK = {
        "Aries": None,
        "Taurus": "saturn",
        "Gemini": None,
        "Cancer": "mars",
        "Leo": "mars",
        "Virgo": None,
        "Libra": "saturn",
        "Scorpio": None,
        "Sagittarius": None,
        "Capricorn": "venus",
        "Aquarius": "venus",
        "Pisces": None,
    }
    lagna = _lagna_sign(chart) or ""
    yk = YK.get(lagna)
    if not yk:
        return None
    p = _planet(chart, yk)
    if not p:
        return None
    house = p.get("house")
    in_kendra_trikona = house in (1, 4, 5, 7, 9, 10)
    own_or_exalted = _is_exalted(chart, yk) or (
        # Own-sign check
        (yk == "saturn" and (int(float(p["longitude"]) // 30) % 12) in (9, 10))
        or (yk == "mars" and (int(float(p["longitude"]) // 30) % 12) in (0, 7))
        or (yk == "venus" and (int(float(p["longitude"]) // 30) % 12) in (1, 6))
    )
    if not (in_kendra_trikona and (own_or_exalted or in_kendra_trikona)):
        return None
    strength_word = "exceptionally strong" if own_or_exalted else "well-placed"
    text = (
        f"Your chart has a planet — {yk.title()} — that classically functions as your "
        f"*yogakaraka*, meaning it rules both your creative house and your career house at "
        f"the same time. In your chart this planet is {strength_word}, sitting in house {house}. "
        f"The lived signature: you tend to over-deliver in a specific area — usually whichever "
        f"theme {yk.title()} governs for you — to the point where people associate that capability "
        f"with you whether you've claimed it or not. Is there a specific skill or instinct that "
        f"feels disproportionately *yours* compared to your peers? What is it?"
    )
    return Question(
        category="natural_aptitude",
        text=text,
        signature=f"Yogakaraka {yk.title()} in H{house}, {'own/exalted' if own_or_exalted else 'kendra/trikona'}",
        strength=0.65,
        expected_answer_type="brief",
        intake_event_type="natural_aptitude",
    )


def rule_difficult_sub_period_in_last_5y(chart: dict) -> Question | None:
    """If a Mars-Rahu, Saturn-Rahu, or Rahu-Saturn sub-period ran in the
    last 5 years, ask about that specific stretch of pressure."""
    try:
        from datetime import datetime, timedelta

        from packages.context.src.dasha import (
            get_antardasha_sequence,
            get_mahadasha_sequence,
        )

        birth_dt = datetime.fromisoformat(chart["birth"]["datetime"])
        if birth_dt.tzinfo:
            birth_dt = birth_dt.replace(tzinfo=None)
        now = datetime.fromisoformat(chart["meta"]["generated_at"])
        if now.tzinfo:
            now = now.replace(tzinfo=None)
        five_y_ago = now - timedelta(days=365 * 5)
        moon_lon = chart["moon"]["longitude"]
        mds = get_mahadasha_sequence(birth_dt, moon_lon, years=120)
        # Difficult AD combos
        rough = {
            ("mars", "rahu"),
            ("rahu", "mars"),
            ("saturn", "rahu"),
            ("rahu", "saturn"),
            ("saturn", "ketu"),
            ("ketu", "saturn"),
        }
        hit = None
        for md in mds:
            ms = md["start_date"]
            me = md["end_date"]
            if ms.tzinfo:
                ms = ms.replace(tzinfo=None)
            if me.tzinfo:
                me = me.replace(tzinfo=None)
            if me < five_y_ago or ms > now:
                continue
            ads = get_antardasha_sequence(md["lord"], ms, me)
            for ad in ads:
                as_ = ad["start_date"]
                ae = ad["end_date"]
                if as_.tzinfo:
                    as_ = as_.replace(tzinfo=None)
                if ae.tzinfo:
                    ae = ae.replace(tzinfo=None)
                # Overlap with last 5y
                if ae < five_y_ago or as_ > now:
                    continue
                key = (md["lord"], ad["lord"])
                if key in rough:
                    hit = (key, as_, ae)
                    break
            if hit:
                break
        if not hit:
            return None
        combo, ws, we = hit
        text = (
            f"Between {ws.strftime('%B %Y')} and {we.strftime('%B %Y')} you ran through a "
            f"sub-period that the classical texts consistently flag as one of the harder "
            f"windows — {combo[0].title()}-{combo[1].title()}, a combination that typically "
            f"produces a specific kind of pressure: ambition pushed against scarcity, financial "
            f"or career setbacks that felt structural rather than fixable. Does that window feel "
            f"like a heavy stretch when you look back? What specifically was happening?"
        )
        return Question(
            category="past_difficult_period",
            text=text,
            signature=f"{combo[0].title()}-{combo[1].title()} sub-period {ws.date()} to {we.date()}",
            strength=0.7,
            expected_answer_type="brief",
            intake_event_type="long_phase",
        )
    except Exception:
        return None


def rule_vipreet_raja_yoga_active(chart: dict) -> Question | None:
    """If the chart has a detected Vimala/Sarala/Harsha yoga, ask about a
    hardship that quietly became an advantage."""
    yogas = chart.get("yogas") or []
    names_lower = " ".join((y.get("name") or "").lower() for y in yogas)
    if not any(k in names_lower for k in ("vimala", "sarala", "harsha", "vipreet", "vipareet")):
        return None
    text = (
        "Your chart carries a signature the texts call *the reversal yoga* — patterns where "
        "a difficulty that should have flattened you instead becomes the very thing that "
        "moves you forward. Often plays out as: an illness, a failure, a humiliation, or a "
        "long unwanted detour that opens the door to the work or person you actually needed. "
        "Has anything like that happened to you in the last 5-10 years? Briefly what?"
    )
    return Question(
        category="reversal_pattern",
        text=text,
        signature="Vipreet Raja Yoga (Vimala/Sarala/Harsha) detected in chart",
        strength=0.7,
        expected_answer_type="brief",
        intake_event_type="other",
    )


def rule_putrakaraka_5h_signature(chart: dict) -> Question | None:
    """For adults 30+, asking about children timing."""
    age = _age_now(chart)
    if not (28 <= age <= 42):
        return None
    h5_lord_planet = _ruler_of_house(_lagna_sign(chart) or "", 5)
    if not h5_lord_planet:
        return None
    text = (
        "Reading the children-line of your chart now (since you're in the age range where this "
        "becomes a real question): are you currently a parent? If yes, how many children and when "
        "were they born? If no, is having children something you're actively considering or have "
        "decided against — and is there a partner in the picture?"
    )
    return Question(
        category="children",
        text=text,
        signature=f"5H lord = {h5_lord_planet} for age {age:.0f}",
        strength=0.55,
        expected_answer_type="brief",
        intake_event_type="children_status",
    )


# ── The dispatcher ────────────────────────────────────────────────────

ALL_RULES: list[Callable[[dict], Question | None]] = [
    rule_lagna_at_cusp,  # always first — birth-time accuracy
    rule_sade_sati,  # high signal if active
    rule_sade_sati_setting_phase_elder,
    rule_sun_rahu_or_ketu_axis,
    rule_debilitated_2l_or_11l,
    rule_mercury_rules_9_and_12,
    rule_ketu_in_8h,
    rule_combust_md_or_atmakaraka,  # NEW — overshadowed life-period engine
    rule_difficult_sub_period_in_last_5y,  # NEW — Mars/Saturn-Rahu past pressure
    rule_stellium_in_house,  # NEW — striking concentration of planets
    rule_vipreet_raja_yoga_active,  # NEW — reversal-yoga signature
    rule_yogakaraka_strength,  # NEW — chart's classical asset planet
    rule_recent_dasha_change,
    rule_saturn_return_window,
    rule_mars_debilitated_7_or_10,
    rule_jupiter_in_12,
    rule_current_ketu_period,
    rule_putrakaraka_5h_signature,
]


def generate_questions(
    chart: dict[str, Any],
    max_questions: int = 7,
    min_questions: int = 5,
) -> list[Question]:
    """Run all detection rules against the chart, return top N questions.

    Args:
        chart: collect_chart_data output (full chart_data dict).
        max_questions: Cap on questions returned (default 7).
        min_questions: Soft floor; if fewer rules fire, returns what we have.

    Returns:
        List of Question objects, sorted by strength descending.
        Never returns more than max_questions.
    """
    fired: list[Question] = []
    for rule in ALL_RULES:
        try:
            q = rule(chart)
            if q is not None:
                fired.append(q)
        except Exception:
            # Rules must be tolerant — a bad rule should never block the rest
            continue

    fired.sort(key=lambda q: -q.strength)

    # Soft de-dup: don't ask two questions in the same category (keep stronger)
    seen_categories: set[str] = set()
    deduped: list[Question] = []
    for q in fired:
        if q.category in seen_categories:
            continue
        seen_categories.add(q.category)
        deduped.append(q)

    return deduped[:max_questions]


def format_for_whatsapp(questions: list[Question], full_name: str) -> str:
    """Format the question set as a WhatsApp-ready message string."""
    lines = [
        f"Namaste {full_name.split()[0] if full_name else ''},",
        "",
        "Thank you for ordering your 108 Life Reading.",
        "",
        "Before we generate your report, we've looked at your chart and noticed "
        "a few specific signatures. To make your reading as accurate as we can, "
        "could you reply with your answers to the questions below? Even a one-line "
        "answer per question is enough.",
        "",
        "(Your answers stay private and only feed into your reading. If a question "
        "doesn't apply to you, just say 'skip' or 'doesn't apply'.)",
        "",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q.text}")
        lines.append("")
    lines.append("Once we have your answers, your report will be delivered within 24 hours.")
    return "\n".join(lines)


def to_audit_block(questions: list[Question]) -> str:
    """Operator-facing audit log: each question + its chart signature."""
    lines = ["[CSQG AUDIT — questions fired for this chart]"]
    for i, q in enumerate(questions, 1):
        lines.append(
            f"  Q{i} [{q.category}] strength={q.strength:.2f}" f"  signature: {q.signature}"
        )
    return "\n".join(lines)
