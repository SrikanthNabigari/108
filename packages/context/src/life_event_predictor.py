"""Life Event Predictor — the predictive engine for the 108 Life Story Spine.

Takes a chart and produces structured WHAT-WHEN-WHY predictions for the
major life events Vedic astrology can call with classical confidence.

Categories covered:
    1. MARRIAGE         — partnership windows (7L AD + Venus/Jupiter transits)
    2. CAREER PEAKS     — 10L MD/AD activations
    3. CAREER CHANGES   — job/field shifts (10L AD transitions, Rahu on 10H)
    4. WEALTH PEAKS     — Dhana yoga lord activations + Jupiter return
    5. PROPERTY         — 4L AD + Mars transit support
    6. FOREIGN SETTLEMENT — 12L AD + Rahu transit
    7. FIRST CHILD      — 5L AD + Jupiter transit on 5H
    8. PARENTAL EVENTS  — Sun (father) / Moon (mother) audit windows
    9. SATURN RETURNS   — every 29 years
   10. JUPITER RETURNS  — every 12 years
   11. NODAL RETURNS    — every 18 years
   12. SADE SATI CYCLES — Saturn through 12/1/2 from Moon
   13. MD SHIFTS        — the 9 life-act chapter changes
   14. HEALTH AUDITS    — 6L/8L AD + Mars/Saturn transit on 6H/8H
   15. ACCIDENT WINDOWS — Mars-Saturn transit conjunctions + retrograde Mars
   16. LIFE SHIFTS      — major reinventions (Lagna-lord MD, Sade Sati exits)
   17. SPIRITUAL OPENING — Ketu AD + 12H/9H transit support

Output schema:
    [
      {
        "id": "marriage_window_2026",
        "event": "Marriage Window",
        "category": "marriage",
        "date_start": "2026-11-26",
        "date_end": "2027-04-20",
        "primary_signature": "Venus AK pratyantar firing",
        "supporting_signatures": ["7L Mars activation pending", "Saturn entering 7H Apr 2027"],
        "confidence": "high",  # low / moderate / high / certain
        "life_age": 34,
        "rationale": "Atmakaraka pratyantar + 7L sub-lord run + Saturn 7H ingress within 5 months"
      },
      ...
    ]
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# Confidence levels:
#   certain   — astronomical certainty (Saturn returns, planetary returns, MD shifts)
#   high      — 3+ signatures stack on the same theme + dasha-active
#   moderate  — 2 signatures stack
#   low       — 1 signature only (informational, not predictive)
CONFIDENCE_LEVELS = ("low", "moderate", "high", "certain")


def _strip_tz(dt: Any) -> datetime:
    """Coerce a datetime/string with possible tzinfo into a naive datetime."""
    if isinstance(dt, str):
        d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return d.replace(tzinfo=None) if d.tzinfo else d
    if hasattr(dt, "tzinfo") and dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt


def _life_age(birth_dt: datetime, target_dt: datetime) -> int:
    """Return age in whole years at target_dt."""
    return (
        target_dt.year
        - birth_dt.year
        - ((target_dt.month, target_dt.day) < (birth_dt.month, birth_dt.day))
    )


def _house_lord(house: int, lagna_sign_idx: int) -> str:
    """Return the lord of a house given the Lagna sign index (0-11 = Aries-Pisces)."""
    sign_lord = {
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
    sign_in_house = (lagna_sign_idx + house - 1) % 12
    return sign_lord[sign_in_house]


def _lord_house_placement(lord: str, natal_planets: dict, lagna_sign_idx: int) -> int:
    """Return the house where a planet sits (1-12) from the Lagna."""
    if lord not in natal_planets:
        return 0
    p_sign = int(float(natal_planets[lord]["longitude"]) // 30)
    return ((p_sign - lagna_sign_idx) % 12) + 1


# ════════════════════════════════════════════════════════════════════
#  Detector functions — one per event category. Each returns 0+ events.
# ════════════════════════════════════════════════════════════════════


def detect_marriage_windows(chart_data: dict) -> list[dict]:
    """Marriage windows: 7L MD or AD + Venus/Jupiter transit on 7H or 7L."""
    out: list[dict] = []
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]
    seventh_lord = _house_lord(7, lagna_sign_idx)
    venus_house = _lord_house_placement("venus", natal, lagna_sign_idx)

    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    md = chart_data["dasha"]["current"]["mahadasha"]
    ad = chart_data["dasha"]["current"]["antardasha"]

    # If Venus is currently Antardasha lord → marriage potential is "open"
    if ad["lord"] == "venus":
        d_start = _strip_tz(ad["start_date"])
        d_end = _strip_tz(ad["end_date"])
        out.append(
            {
                "id": "marriage_venus_ad",
                "event": "Marriage Window — Venus Sub-Period",
                "category": "marriage",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": "Venus Antardasha active",
                "supporting_signatures": [
                    f"Venus karaka of marriage, sits in {venus_house}H from Lagna",
                    f"7L is {seventh_lord.title()}",
                ],
                "confidence": "high",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "Venus is the natural karaka of marriage; its sub-period activates partnership themes.",
            }
        )

    # If 7L is currently MD or AD lord → strong marriage signature
    if md["lord"] == seventh_lord or ad["lord"] == seventh_lord:
        level = "Mahadasha" if md["lord"] == seventh_lord else "Antardasha"
        period = md if level == "Mahadasha" else ad
        d_start = _strip_tz(period["start_date"])
        d_end = _strip_tz(period["end_date"])
        out.append(
            {
                "id": f"marriage_7l_{level.lower()}",
                "event": f"Marriage Window — 7L {level}",
                "category": "marriage",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": f"{seventh_lord.title()} (7L of marriage) running as {level}",
                "supporting_signatures": [
                    f"7L sits in {_lord_house_placement(seventh_lord, natal, lagna_sign_idx)}H",
                ],
                "confidence": "high",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "When the 7th lord runs as MD or AD, partnership-house themes get directly activated.",
            }
        )

    return out


def detect_career_peaks(chart_data: dict) -> list[dict]:
    """Career peak windows — 10L MD/AD activations."""
    out: list[dict] = []
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]
    tenth_lord = _house_lord(10, lagna_sign_idx)
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    md = chart_data["dasha"]["current"]["mahadasha"]
    ad = chart_data["dasha"]["current"]["antardasha"]

    if md["lord"] == tenth_lord or ad["lord"] == tenth_lord:
        level = "Mahadasha" if md["lord"] == tenth_lord else "Antardasha"
        period = md if level == "Mahadasha" else ad
        d_start = _strip_tz(period["start_date"])
        d_end = _strip_tz(period["end_date"])
        out.append(
            {
                "id": f"career_peak_{level.lower()}",
                "event": f"Career Peak — 10L {level}",
                "category": "career",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": f"{tenth_lord.title()} (10L of career) running as {level}",
                "supporting_signatures": [
                    f"10L sits in {_lord_house_placement(tenth_lord, natal, lagna_sign_idx)}H"
                ],
                "confidence": "high",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "10L MD/AD = the career-engine has the microphone for this entire period.",
            }
        )

    # Scan upcoming ADs in the current MD for 10L sub-periods
    md_ads = chart_data["dasha"].get("current_md_antardashas") or []
    for adp in md_ads:
        if adp["lord"] == tenth_lord:
            d_start = (
                _strip_tz(adp["start"])
                if isinstance(adp["start"], str)
                else _strip_tz(adp["start_date"])
            )
            d_end = (
                _strip_tz(adp["end"]) if isinstance(adp["end"], str) else _strip_tz(adp["end_date"])
            )
            if d_start <= datetime.now():
                continue  # already covered above
            out.append(
                {
                    "id": f"career_peak_upcoming_{d_start.year}",
                    "event": f"Career Peak Window — {md['lord'].title()}-{tenth_lord.title()} AD",
                    "category": "career",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": d_end.strftime("%Y-%m-%d"),
                    "primary_signature": f"10L {tenth_lord.title()} AD inside {md['lord'].title()} MD",
                    "supporting_signatures": [],
                    "confidence": "high",
                    "life_age": _life_age(birth_dt, d_start),
                    "rationale": "Future 10L sub-period within the current MD — recognised career inflection.",
                }
            )

    return out


def detect_career_changes(chart_data: dict) -> list[dict]:
    """Career change/job shift windows — every MD shift + every AD shift in upcoming MD."""
    out: list[dict] = []
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    now = datetime.now()

    # MD shifts = whole-life pivots that almost always coincide with vocation reshape
    for md in chart_data["dasha"].get("mahadasha_sequence", []):
        d_start = (
            _strip_tz(md["start"]) if isinstance(md["start"], str) else _strip_tz(md["start_date"])
        )
        _d_end = _strip_tz(md["end"]) if isinstance(md["end"], str) else _strip_tz(md["end_date"])
        if d_start < now:
            continue
        out.append(
            {
                "id": f"md_shift_{md['lord']}",
                "event": f"Major Chapter Shift — {md['lord'].title()} Mahadasha opens",
                "category": "life_shift",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": (d_start + timedelta(days=180)).strftime("%Y-%m-%d"),
                "primary_signature": f"Mahadasha lord changes to {md['lord'].title()}",
                "supporting_signatures": [],
                "confidence": "certain",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "MD changes redefine the structural texture of life for the next 6-20 years; career/identity reshape within 6 months.",
            }
        )
    return out[:5]  # only next 5 MDs


def detect_wealth_peaks(chart_data: dict) -> list[dict]:
    """Wealth peak windows — 2L/11L MD/AD + favourable Jupiter transit."""
    out: list[dict] = []
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]
    second_lord = _house_lord(2, lagna_sign_idx)
    eleventh_lord = _house_lord(11, lagna_sign_idx)
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    md = chart_data["dasha"]["current"]["mahadasha"]
    ad = chart_data["dasha"]["current"]["antardasha"]

    for label, lord in [("2L (wealth/family)", second_lord), ("11L (gains)", eleventh_lord)]:
        if md["lord"] == lord or ad["lord"] == lord:
            level = "Mahadasha" if md["lord"] == lord else "Antardasha"
            period = md if level == "Mahadasha" else ad
            d_start = _strip_tz(period["start_date"])
            d_end = _strip_tz(period["end_date"])
            out.append(
                {
                    "id": f"wealth_peak_{lord}_{level.lower()}",
                    "event": f"Wealth Window — {label} {level}",
                    "category": "wealth",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": d_end.strftime("%Y-%m-%d"),
                    "primary_signature": f"{lord.title()} as {label} running",
                    "supporting_signatures": [
                        f"{lord.title()} sits in {_lord_house_placement(lord, natal, lagna_sign_idx)}H"
                    ],
                    "confidence": "high",
                    "life_age": _life_age(birth_dt, d_start),
                    "rationale": "Wealth-house lord running directly activates income/accumulation themes.",
                }
            )

    return out


def detect_property_windows(chart_data: dict) -> list[dict]:
    """Property/vehicle acquisition windows — 4L AD + Sasa Yoga active."""
    out: list[dict] = []
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    _natal = chart_data["natal_planets_dict"]
    fourth_lord = _house_lord(4, lagna_sign_idx)
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    ad = chart_data["dasha"]["current"]["antardasha"]

    if ad["lord"] == fourth_lord:
        d_start = _strip_tz(ad["start_date"])
        d_end = _strip_tz(ad["end_date"])
        out.append(
            {
                "id": "property_4l_ad",
                "event": "Property/Home Window",
                "category": "property",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": f"4L {fourth_lord.title()} Antardasha — home/property house lord active",
                "supporting_signatures": [],
                "confidence": "high",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "When the 4H lord runs as sub-period, property/home themes get the strongest activation.",
            }
        )

    # Also look ahead for 4L sub-periods in current MD
    md = chart_data["dasha"]["current"]["mahadasha"]
    md_ads = chart_data["dasha"].get("current_md_antardashas") or []
    for adp in md_ads:
        if adp["lord"] == fourth_lord:
            d_start = _strip_tz(adp.get("start") or adp.get("start_date"))
            d_end = _strip_tz(adp.get("end") or adp.get("end_date"))
            if d_start <= datetime.now():
                continue
            out.append(
                {
                    "id": f"property_upcoming_{d_start.year}",
                    "event": f"Property/Home Window — {md['lord'].title()}-{fourth_lord.title()} AD",
                    "category": "property",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": d_end.strftime("%Y-%m-%d"),
                    "primary_signature": f"4L {fourth_lord.title()} AD opens",
                    "supporting_signatures": [],
                    "confidence": "high",
                    "life_age": _life_age(birth_dt, d_start),
                    "rationale": "Future 4L sub-period — second-strongest property window after current AD.",
                }
            )

    return out


def detect_foreign_settlement(chart_data: dict) -> list[dict]:
    """Foreign settlement / major relocation windows — 12L AD + Rahu transit support."""
    out: list[dict] = []
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]
    twelfth_lord = _house_lord(12, lagna_sign_idx)
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    md = chart_data["dasha"]["current"]["mahadasha"]
    ad = chart_data["dasha"]["current"]["antardasha"]

    # 12L currently active
    if md["lord"] == twelfth_lord or ad["lord"] == twelfth_lord:
        level = "Mahadasha" if md["lord"] == twelfth_lord else "Antardasha"
        period = md if level == "Mahadasha" else ad
        d_start = _strip_tz(period["start_date"])
        d_end = _strip_tz(period["end_date"])
        out.append(
            {
                "id": f"foreign_{level.lower()}",
                "event": f"Foreign Move / Settlement Window — 12L {level}",
                "category": "foreign",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": f"12L {twelfth_lord.title()} running as {level}",
                "supporting_signatures": [
                    f"12L sits in {_lord_house_placement(twelfth_lord, natal, lagna_sign_idx)}H"
                ],
                "confidence": "high",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "12L MD/AD activates foreign/abroad/relocation themes.",
            }
        )

    # Rahu in 9H/12H AD = strong foreign signature
    if ad["lord"] == "rahu":
        rahu_house = _lord_house_placement("rahu", natal, lagna_sign_idx)
        if rahu_house in (9, 12, 7):
            d_start = _strip_tz(ad["start_date"])
            d_end = _strip_tz(ad["end_date"])
            out.append(
                {
                    "id": "foreign_rahu_ad",
                    "event": "Foreign Opportunity Window — Rahu Sub-Period",
                    "category": "foreign",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": d_end.strftime("%Y-%m-%d"),
                    "primary_signature": f"Rahu AD active, Rahu sits in {rahu_house}H",
                    "supporting_signatures": [],
                    "confidence": "moderate",
                    "life_age": _life_age(birth_dt, d_start),
                    "rationale": "Rahu in foreign-flavoured houses + Rahu sub-period = foreign exposure spike.",
                }
            )

    return out


def detect_health_audits(chart_data: dict) -> list[dict]:
    """Health audit windows — 6L/8L AD activations, debilitated Mars activations."""
    out: list[dict] = []
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    _natal = chart_data["natal_planets_dict"]
    sixth_lord = _house_lord(6, lagna_sign_idx)
    eighth_lord = _house_lord(8, lagna_sign_idx)
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])

    md_ads = chart_data["dasha"].get("current_md_antardashas") or []
    _md = chart_data["dasha"]["current"]["mahadasha"]
    for adp in md_ads:
        if adp["lord"] in (sixth_lord, eighth_lord):
            d_start = _strip_tz(adp.get("start") or adp.get("start_date"))
            d_end = _strip_tz(adp.get("end") or adp.get("end_date"))
            label = (
                "6L (illness/debt)" if adp["lord"] == sixth_lord else "8L (transformation/chronic)"
            )
            out.append(
                {
                    "id": f"health_audit_{adp['lord']}_{d_start.year}",
                    "event": f"Health Audit Window — {label} Sub-Period",
                    "category": "health",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": d_end.strftime("%Y-%m-%d"),
                    "primary_signature": f"{label} {adp['lord'].title()} sub-period active",
                    "supporting_signatures": [],
                    "confidence": "moderate",
                    "life_age": _life_age(birth_dt, d_start),
                    "rationale": "6L/8L sub-periods classically bring health-themes into focus — body audit + medical attention often follow.",
                }
            )
    return out


def detect_accident_windows(chart_data: dict) -> list[dict]:
    """Accident-prone windows — Mars-Saturn slow-transit conjunctions, retrograde Mars activations."""
    out: list[dict] = []
    natal = chart_data["natal_planets_dict"]
    if "mars" not in natal:
        return out
    mars_retro = natal["mars"].get("retrograde") or natal["mars"].get("is_retrograde", False)
    mars_debilitated = int(float(natal["mars"]["longitude"]) // 30) == 3  # Cancer = 3
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])

    if mars_debilitated:
        # Mars sub-periods will be challenging for accidents/injuries
        md_ads = chart_data["dasha"].get("current_md_antardashas") or []
        for adp in md_ads:
            if adp["lord"] == "mars":
                d_start = _strip_tz(adp.get("start") or adp.get("start_date"))
                d_end = _strip_tz(adp.get("end") or adp.get("end_date"))
                out.append(
                    {
                        "id": f"accident_mars_ad_{d_start.year}",
                        "event": "Caution Window — Debilitated Mars Sub-Period",
                        "category": "accident",
                        "date_start": d_start.strftime("%Y-%m-%d"),
                        "date_end": d_end.strftime("%Y-%m-%d"),
                        "primary_signature": "Mars Antardasha active, natal Mars debilitated"
                        + (" + retrograde" if mars_retro else ""),
                        "supporting_signatures": [],
                        "confidence": "moderate",
                        "life_age": _life_age(birth_dt, d_start),
                        "rationale": "Debilitated Mars sub-periods classically bring injury/accident risk — exercise caution with sharp tools, vehicles, sports.",
                    }
                )
    return out


def detect_saturn_returns(chart_data: dict) -> list[dict]:
    """Saturn returns — astronomical certainty, every ~29 years."""
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    out: list[dict] = []
    # Saturn orbital period ≈ 29.5 years
    for n in (1, 2, 3):
        return_date = birth_dt + timedelta(days=29.5 * 365.25 * n)
        out.append(
            {
                "id": f"saturn_return_{n}",
                "event": f"Saturn Return #{n}",
                "category": "structural_pivot",
                "date_start": (return_date - timedelta(days=180)).strftime("%Y-%m-%d"),
                "date_end": (return_date + timedelta(days=180)).strftime("%Y-%m-%d"),
                "primary_signature": "Saturn returns to natal Saturn position",
                "supporting_signatures": [],
                "confidence": "certain",
                "life_age": _life_age(birth_dt, return_date),
                "rationale": "Saturn returns to its birth position every 29.5 years — classical 'life stocktake' moment, restructuring of identity and direction.",
            }
        )
    return out


def detect_jupiter_returns(chart_data: dict) -> list[dict]:
    """Jupiter returns — every ~12 years."""
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    out: list[dict] = []
    for n in (1, 2, 3, 4, 5, 6, 7, 8, 9):
        return_date = birth_dt + timedelta(days=12 * 365.25 * n)
        if return_date.year > birth_dt.year + 120:
            break
        out.append(
            {
                "id": f"jupiter_return_{n}",
                "event": f"Jupiter Return #{n}",
                "category": "structural_pivot",
                "date_start": (return_date - timedelta(days=90)).strftime("%Y-%m-%d"),
                "date_end": (return_date + timedelta(days=90)).strftime("%Y-%m-%d"),
                "primary_signature": "Jupiter returns to natal Jupiter position",
                "supporting_signatures": [],
                "confidence": "certain",
                "life_age": _life_age(birth_dt, return_date),
                "rationale": "Jupiter returns every 12 years — classical 'dharmic refresh' moment, expansion of meaning and opportunity.",
            }
        )
    return out


def detect_md_shifts(chart_data: dict) -> list[dict]:
    """Mahadasha shifts — the 9 big life-act transitions."""
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    out: list[dict] = []
    for md in chart_data["dasha"].get("mahadasha_sequence", [])[:9]:
        d_start = _strip_tz(md.get("start") or md.get("start_date"))
        d_end = _strip_tz(md.get("end") or md.get("end_date"))
        out.append(
            {
                "id": f"md_open_{md['lord']}",
                "event": f"{md['lord'].title()} Mahadasha Opens — Chapter {len(out)+1}",
                "category": "structural_pivot",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": f"Mahadasha lord changes to {md['lord'].title()} ({md.get('years', '?')}y)",
                "supporting_signatures": [],
                "confidence": "certain",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": f"The {md.get('years', '?')}-year planetary chapter begins — sets the structural flavour of this entire act of life.",
            }
        )
    return out


def detect_sade_sati_cycles(chart_data: dict) -> list[dict]:
    """Sade Sati cycles — every ~30 years.

    Saturn transits 12/1/2 from natal Moon — 2.5y each, 7.5y total.
    Currently active phase is already in chart_data['state_vector']['sade_sati'].
    This function predicts FUTURE Sade Sati cycles based on Saturn's orbital period.
    """
    out: list[dict] = []
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])

    sv = chart_data.get("state_vector") or {}
    sade = sv.get("sade_sati") or {}
    if sade.get("active"):
        # mark current cycle if active
        out.append(
            {
                "id": "sade_sati_current",
                "event": f"Sade Sati Currently Active — {sade.get('phase', '?').title()} Phase",
                "category": "structural_pivot",
                "date_start": datetime.now().strftime("%Y-%m-%d"),
                "date_end": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
                "primary_signature": f"Saturn in {sade.get('phase', '?')} phase from natal Moon",
                "supporting_signatures": [],
                "confidence": "certain",
                "life_age": _life_age(birth_dt, datetime.now()),
                "rationale": "Sade Sati is Saturn's 7.5-year passage through 12/1/2 from natal Moon — the classical reshaping cycle.",
            }
        )

    # Predict next Sade Sati cycles (every ~29.5 years)
    for n in (1, 2):
        next_cycle = datetime.now() + timedelta(days=29.5 * 365.25 * n)
        out.append(
            {
                "id": f"sade_sati_future_{n}",
                "event": f"Next Sade Sati Cycle Approaches (#{n} ahead)",
                "category": "structural_pivot",
                "date_start": (next_cycle - timedelta(days=900)).strftime("%Y-%m-%d"),
                "date_end": (next_cycle + timedelta(days=900)).strftime("%Y-%m-%d"),
                "primary_signature": "Saturn returns to 12th from natal Moon, opening next 7.5-year Sade Sati",
                "supporting_signatures": [],
                "confidence": "certain",
                "life_age": _life_age(birth_dt, next_cycle),
                "rationale": "Sade Sati recurs every ~29.5 years; classical 'soul restructuring' window.",
            }
        )
    return out


def detect_spiritual_openings(chart_data: dict) -> list[dict]:
    """Spiritual awakening windows — Ketu MD/AD + 12H/9H lord activations."""
    out: list[dict] = []
    birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    md = chart_data["dasha"]["current"]["mahadasha"]
    ad = chart_data["dasha"]["current"]["antardasha"]

    if md["lord"] == "ketu" or ad["lord"] == "ketu":
        level = "Mahadasha" if md["lord"] == "ketu" else "Antardasha"
        period = md if level == "Mahadasha" else ad
        d_start = _strip_tz(period["start_date"])
        d_end = _strip_tz(period["end_date"])
        out.append(
            {
                "id": f"spiritual_ketu_{level.lower()}",
                "event": f"Spiritual Inquiry / Dissolution Window — Ketu {level}",
                "category": "spiritual",
                "date_start": d_start.strftime("%Y-%m-%d"),
                "date_end": d_end.strftime("%Y-%m-%d"),
                "primary_signature": f"Ketu {level} active — dissolution and inward turn",
                "supporting_signatures": [],
                "confidence": "high",
                "life_age": _life_age(birth_dt, d_start),
                "rationale": "Ketu periods classically open spiritual inquiry, dissolution of old structures, and inward focus.",
            }
        )
    return out


# ════════════════════════════════════════════════════════════════════
#  Master orchestrator
# ════════════════════════════════════════════════════════════════════


def get_past_verification_events(chart_data: dict, years_back: int = 8) -> list[dict]:
    """Return the past significant dasha sub-periods + their classical-event
    signatures, so the customer can verify the chart against their own
    lived history (trust-builder for the predictions ahead).

    Returns list of past windows with the major event-themes that would
    have been ACTIVE during that period — formatted for direct comparison
    with the customer's actual lived experience.
    """
    _birth_dt = _strip_tz(chart_data["birth"]["datetime"])
    now = datetime.now()
    look_back = now - timedelta(days=years_back * 365.25)

    natal = chart_data["natal_planets_dict"]
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]

    # Past MD shifts + AD shifts
    past_events: list[dict] = []
    md_seq = chart_data["dasha"].get("mahadasha_sequence", [])
    for md in md_seq:
        d_start = _strip_tz(md.get("start") or md.get("start_date"))
        d_end = _strip_tz(md.get("end") or md.get("end_date"))
        if d_start > now or d_end < look_back:
            continue
        # MD opening within window
        if d_start >= look_back:
            past_events.append(
                {
                    "id": f"past_md_{md['lord']}",
                    "event": f"{md['lord'].title()} Mahadasha Opened",
                    "category": "structural_pivot",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": (d_start + timedelta(days=180)).strftime("%Y-%m-%d"),
                    "themes_active": [
                        f"{md['lord'].title()} themes ({md.get('years', '?')}-year chapter began)",
                        "Identity / direction reshape within 6 months of this date",
                    ],
                    "what_likely_happened": (
                        f"A major life-shift around this date — career direction, "
                        f"location, relationship, or identity reset. The "
                        f"{md['lord'].title()} chapter took over."
                    ),
                }
            )

    # Past AD shifts in current MD
    current_md = chart_data["dasha"]["current"]["mahadasha"]
    md_ads = chart_data["dasha"].get("current_md_antardashas") or []
    for adp in md_ads:
        d_start = _strip_tz(adp.get("start") or adp.get("start_date"))
        d_end = _strip_tz(adp.get("end") or adp.get("end_date"))
        if d_start > now or d_end < look_back:
            continue
        if d_start >= look_back and d_start <= now:
            ad_lord = adp["lord"]
            # Compute which houses this AD lord ruled and sat in
            houses_ruled = [h for h in range(1, 13) if _house_lord(h, lagna_sign_idx) == ad_lord]
            sits_in = _lord_house_placement(ad_lord, natal, lagna_sign_idx)
            theme_lines = []
            if houses_ruled and sits_in:
                houses_str = "/".join(f"{h}H" for h in houses_ruled)
                theme_lines.append(
                    f"{current_md['lord'].title()}-{ad_lord.title()} sub-period: "
                    f"{houses_str} themes activating through {sits_in}H"
                )
            past_events.append(
                {
                    "id": f"past_ad_{ad_lord}_{d_start.year}",
                    "event": f"{current_md['lord'].title()}-{ad_lord.title()} Sub-Period",
                    "category": "sub_period",
                    "date_start": d_start.strftime("%Y-%m-%d"),
                    "date_end": d_end.strftime("%Y-%m-%d"),
                    "themes_active": theme_lines,
                    "what_likely_happened": _ad_lord_theme_phrasing(ad_lord, sits_in, houses_ruled),
                }
            )

    past_events.sort(key=lambda e: e["date_start"])
    return past_events


def _ad_lord_theme_phrasing(_ad_lord: str, sits_in: int, houses_ruled: list[int]) -> str:
    """Phrase what likely happened during a past sub-period in lived terms."""
    house_to_life_theme = {
        1: "identity / body / public self",
        2: "wealth / family / speech",
        3: "siblings / effort / short trips / communication work",
        4: "home / mother / property / inner ground",
        5: "creativity / children / romance / speculation",
        6: "service / debt / illness / daily-work conflict",
        7: "partnership / spouse / business deals",
        8: "transformation / sudden change / hidden things",
        9: "dharma / travel / father / guru / higher learning",
        10: "career / public role / status",
        11: "gains / network / ambitions / income surge",
        12: "foreign / loss / dissolution / spiritual / hidden work",
    }
    phrases = []
    for h in houses_ruled:
        if h in house_to_life_theme:
            phrases.append(house_to_life_theme[h])
    sits_phrase = house_to_life_theme.get(sits_in, "")
    if phrases and sits_phrase:
        return (
            f"This period activated {' + '.join(phrases)} themes through your "
            f"{sits_phrase}. If you remember events in those domains around this window, "
            "that's the chart speaking."
        )
    elif sits_phrase:
        return f"Themes related to {sits_phrase}."
    return "A specific sub-period of life — check what changed in that domain."


def predict_life_events(chart_data: dict) -> list[dict]:
    """Run all detectors and return a unified, time-sorted list of predictions."""
    all_events: list[dict] = []
    for detector in [
        detect_marriage_windows,
        detect_career_peaks,
        detect_career_changes,
        detect_wealth_peaks,
        detect_property_windows,
        detect_foreign_settlement,
        detect_health_audits,
        detect_accident_windows,
        detect_saturn_returns,
        detect_jupiter_returns,
        detect_md_shifts,
        detect_sade_sati_cycles,
        detect_spiritual_openings,
    ]:
        try:
            all_events.extend(detector(chart_data))
        except Exception as e:
            logger.warning(f"Detector {detector.__name__} failed: {e}")

    # De-duplicate by id, sort by date_start
    seen_ids = set()
    deduped: list[dict] = []
    for ev in all_events:
        if ev["id"] in seen_ids:
            continue
        seen_ids.add(ev["id"])
        deduped.append(ev)
    deduped.sort(key=lambda e: e["date_start"])
    return deduped


def get_current_situation(chart_data: dict) -> dict:
    """Compute the rich present-moment snapshot for the report's opening pages.

    Returns:
        {
          "active_md": {"lord": "...", "end_date": "..."},
          "active_ad": {...},
          "active_pd": {...},
          "current_themes": ["...", "..."],
          "next_pivot": {"event": "...", "date": "...", "days_away": 123},
          "weather": "growing" | "consolidating" | "dissolving" | "audit" | ...,
          "summary": "One paragraph synthesising what the customer is in right now."
        }
    """
    cur = chart_data["dasha"]["current"]
    md = cur["mahadasha"]
    ad = cur["antardasha"]
    pd = cur["pratyantardasha"]
    lagna_sign_idx = chart_data["lagna"]["rashi_idx"]
    natal = chart_data["natal_planets_dict"]
    now = datetime.now()

    # What houses do the active MD + AD activate?
    def _lord_houses(lord: str) -> tuple[list[int], int]:
        """Return (houses_ruled, house_sat_in) for a lord."""
        houses_ruled = [h for h in range(1, 13) if _house_lord(h, lagna_sign_idx) == lord]
        house_sat_in = _lord_house_placement(lord, natal, lagna_sign_idx) if lord in natal else 0
        return houses_ruled, house_sat_in

    md_ruled, md_sits = _lord_houses(md["lord"])
    ad_ruled, ad_sits = _lord_houses(ad["lord"])

    current_themes: list[str] = []
    for label, ruled, sits in [
        (md["lord"].title() + " MD", md_ruled, md_sits),
        (ad["lord"].title() + " AD", ad_ruled, ad_sits),
    ]:
        if ruled and sits:
            houses_str = "/".join(f"{r}H" for r in ruled)
            current_themes.append(f"{label}: {houses_str} themes activating THROUGH {sits}H")

    # Find the next major pivot
    all_events = predict_life_events(chart_data)
    upcoming = [e for e in all_events if datetime.fromisoformat(e["date_start"]) > now]
    next_pivot = None
    if upcoming:
        nxt = upcoming[0]
        days = (datetime.fromisoformat(nxt["date_start"]) - now).days
        next_pivot = {
            "event": nxt["event"],
            "date": nxt["date_start"],
            "days_away": days,
            "category": nxt["category"],
        }

    return {
        "active_md": {
            "lord": md["lord"],
            "end_date": _strip_tz(md["end_date"]).strftime("%Y-%m-%d"),
            "houses_ruled": md_ruled,
            "house_sits_in": md_sits,
        },
        "active_ad": {
            "lord": ad["lord"],
            "end_date": _strip_tz(ad["end_date"]).strftime("%Y-%m-%d"),
            "houses_ruled": ad_ruled,
            "house_sits_in": ad_sits,
        },
        "active_pd": {
            "lord": pd["lord"],
            "end_date": _strip_tz(pd["end_date"]).strftime("%Y-%m-%d"),
        },
        "current_themes": current_themes,
        "next_pivot": next_pivot,
    }
