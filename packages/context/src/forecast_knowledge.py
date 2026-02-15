"""Knowledge-backed text generation for forecast engines.

Uses the centralized knowledge_loader from packages.core to look up
interpretive text for summaries and recommendations.
"""

from __future__ import annotations

from typing import Any

from packages.core.src.knowledge_loader import (
    get_antardasha_effects,
    load_rules,
)
from packages.core.src.knowledge_loader import (
    get_dasha_guide as _get_dasha_guide_raw,
)
from packages.core.src.knowledge_loader import (
    get_nakshatra_transit_rules as _get_nak_transit_raw,
)
from packages.core.src.knowledge_loader import (
    get_tithi_definitions as _get_tithi_raw,
)
from packages.core.src.knowledge_loader import (
    get_transit_aspect_effects as _get_transit_effects_raw,
)
from packages.core.src.knowledge_loader import (
    get_vara_definitions as _get_vara_raw,
)

# ---------------------------------------------------------------------------
# Vara (weekday) guidance
# ---------------------------------------------------------------------------


def get_vara_guidance(weekday_english: str) -> dict[str, Any]:
    """Return good_for / avoid lists for a weekday.

    Args:
        weekday_english: e.g. "Monday", "Tuesday" (case-insensitive)

    Returns:
        {"good_for": [...], "avoid": [...], "lord": "..."}
    """
    data = _get_vara_raw()
    target = weekday_english.strip().title()
    for vara in data.get("varas", []):
        if vara.get("english") == target:
            return {
                "good_for": vara.get("good_for", []),
                "avoid": vara.get("avoid", []),
                "lord": vara.get("lord", ""),
            }
    return {"good_for": [], "avoid": [], "lord": ""}


# ---------------------------------------------------------------------------
# Tithi guidance
# ---------------------------------------------------------------------------


def get_tithi_guidance(tithi_name: str) -> dict[str, Any]:
    """Return good_for / avoid for a tithi.

    Args:
        tithi_name: e.g. "Shukla Saptami", "Pratipada" (matches partial)

    Returns:
        {"good_for": [...], "avoid": [...], "nature": "..."}
    """
    data = _get_tithi_raw()
    target = tithi_name.strip().lower()
    for tithi in data.get("tithis", []):
        name = tithi.get("name", "").lower()
        paksha = tithi.get("paksha", "").lower()
        full = f"{paksha} {name}"
        if name in target or target in full or full in target:
            return {
                "good_for": tithi.get("good_for", []),
                "avoid": tithi.get("avoid", []),
                "nature": tithi.get("nature", ""),
            }
    return {"good_for": [], "avoid": [], "nature": ""}


# ---------------------------------------------------------------------------
# Transit aspect effects
# ---------------------------------------------------------------------------


def get_transit_aspect_effect(transit_planet: str, natal_planet: str, aspect_type: str) -> str:
    """Return the interpretive effect text for a transit aspect.

    Args:
        transit_planet: e.g. "saturn"
        natal_planet: e.g. "moon"
        aspect_type: "conjunction", "opposition", "trine", "square", "sextile"

    Returns:
        Human-readable effect string, or empty string if not found.
    """
    effects = _get_transit_effects_raw()
    return (
        effects.get(transit_planet, {}).get(natal_planet, {}).get(aspect_type, {}).get("effect", "")
    )


# ---------------------------------------------------------------------------
# Nakshatra transit text (Moon transits)
# ---------------------------------------------------------------------------

# Nakshatra name normalization: "Purva Bhadrapada" -> "purva_bhadrapada"
_NAK_NORMALIZE = {
    "ashwini": "ashwini",
    "bharani": "bharani",
    "krittika": "krittika",
    "rohini": "rohini",
    "mrigashira": "mrigashira",
    "mrigashirsha": "mrigashira",
    "ardra": "ardra",
    "punarvasu": "punarvasu",
    "pushya": "pushya",
    "ashlesha": "ashlesha",
    "magha": "magha",
    "purva phalguni": "purva_phalguni",
    "uttara phalguni": "uttara_phalguni",
    "hasta": "hasta",
    "chitra": "chitra",
    "swati": "swati",
    "vishakha": "vishakha",
    "anuradha": "anuradha",
    "jyeshtha": "jyeshtha",
    "mula": "mula",
    "moola": "mula",
    "purva ashadha": "purva_ashadha",
    "uttara ashadha": "uttara_ashadha",
    "shravana": "shravana",
    "dhanishta": "dhanishta",
    "shatabhisha": "shatabhisha",
    "purva bhadrapada": "purva_bhadrapada",
    "uttara bhadrapada": "uttara_bhadrapada",
    "revati": "revati",
}


def _normalize_nakshatra(name: str) -> str:
    """Normalize nakshatra name to JSON key format."""
    lower = name.strip().lower()
    if lower in _NAK_NORMALIZE:
        return _NAK_NORMALIZE[lower]
    # Try replacing spaces with underscores
    return lower.replace(" ", "_")


def get_nakshatra_transit_text(planet: str, nakshatra: str) -> dict[str, Any]:
    """Return theme/positive/negative/best_for/avoid for a planet in a nakshatra.

    Args:
        planet: e.g. "moon"
        nakshatra: e.g. "Pushya" or "purva_bhadrapada"

    Returns:
        {"theme": "...", "positive": [...], "negative": [...],
         "best_for": [...], "avoid": [...]}
    """
    data = _get_nak_transit_raw()
    transits = data.get("transits", {})
    planet_data = transits.get(planet.lower(), {})
    nak_key = _normalize_nakshatra(nakshatra)
    entry = planet_data.get(nak_key, {})
    return {
        "theme": entry.get("theme", ""),
        "positive": entry.get("positive", []),
        "negative": entry.get("negative", []),
        "best_for": entry.get("best_for", []),
        "avoid": entry.get("avoid", []),
    }


# ---------------------------------------------------------------------------
# Antardasha effects
# ---------------------------------------------------------------------------


def get_antardasha_text(md_planet: str, ad_planet: str) -> dict[str, Any]:
    """Return interpretive text for a Mahadasha-Antardasha combination.

    Returns:
        {"general_effects": [...], "career": "...", "health": "...",
         "relationships": "...", "finances": "...", "positive": [...],
         "negative": [...]}
    """
    effects = get_antardasha_effects()
    entry = effects.get(md_planet.lower(), {}).get(ad_planet.lower(), {})
    return {
        "general_effects": entry.get("general_effects", []),
        "career": entry.get("career", ""),
        "health": entry.get("health", ""),
        "relationships": entry.get("relationships", ""),
        "finances": entry.get("finances", ""),
        "positive": entry.get("positive", []),
        "negative": entry.get("negative", []),
    }


# ---------------------------------------------------------------------------
# Dasha guide (macro themes)
# ---------------------------------------------------------------------------


def get_dasha_guide(planet: str) -> dict[str, Any]:
    """Return the full dasha guide for a planet's Mahadasha.

    Returns:
        {"theme": "...", "focus_areas": [...], "career": "...",
         "health": "...", "relationships": "...", "spiritual": "...",
         "practical_advice": [...], "challenges": "...", "opportunities": "..."}
    """
    data = _get_dasha_guide_raw()
    return data.get("dasha_guide", {}).get(planet.lower(), {})


# ---------------------------------------------------------------------------
# Double transit (Jupiter + Saturn activation)
# ---------------------------------------------------------------------------


def get_double_transit_text(house: int) -> dict[str, Any]:
    """Return theme/effect/typical_events for double transit on a house.

    Args:
        house: 1-12

    Returns:
        {"themes": [...], "effect": "...", "typical_events": [...]}
    """
    data = load_rules("double_transit_rules")
    for rule in data.get("rules", []):
        if rule.get("house") == house:
            return {
                "themes": rule.get("themes", []),
                "effect": rule.get("effect", ""),
                "typical_events": rule.get("typical_events", []),
            }
    return {"themes": [], "effect": "", "typical_events": []}


# ---------------------------------------------------------------------------
# Composite builders for forecast engines
# ---------------------------------------------------------------------------


def build_daily_summary(
    *,
    day_rating: int,  # noqa: ARG001
    moon_sign: str,
    moon_nakshatra: str,
    moon_house_from_lagna: int,
    dasha_md: str,
    dasha_ad: str,
    transit_aspects: list[dict[str, Any]],
    is_chandrashtama: bool,
) -> str:
    """Build a rich daily summary from knowledge files.

    Combines: Moon nakshatra theme + top transit aspect effects + dasha context.
    """
    parts: list[str] = []

    # 1. Moon nakshatra theme
    nak_text = get_nakshatra_transit_text("moon", moon_nakshatra)
    if nak_text["theme"]:
        parts.append(
            f"Moon in {moon_nakshatra} ({moon_sign.title()}, house {moon_house_from_lagna}): "
            f"{nak_text['theme']}."
        )
    else:
        parts.append(f"Moon transits {moon_sign.title()} (house {moon_house_from_lagna}).")

    # 2. Top transit aspect effect (tightest orb, slow planets preferred)
    slow = {"saturn", "jupiter", "rahu", "ketu"}
    sorted_aspects = sorted(
        transit_aspects,
        key=lambda a: (a.get("transit", "") not in slow, a.get("orb", 99)),
    )
    for asp in sorted_aspects[:2]:
        effect = get_transit_aspect_effect(
            asp.get("transit", ""),
            asp.get("natal", ""),
            asp.get("aspect", ""),
        )
        if effect:
            parts.append(effect + ".")
            break

    # 3. Dasha context
    ad_text = get_antardasha_text(dasha_md, dasha_ad)
    if ad_text["general_effects"]:
        parts.append(ad_text["general_effects"][0] + ".")

    # 4. Chandrashtama warning in summary
    if is_chandrashtama:
        parts.append("Chandrashtama active — exercise caution with major decisions.")

    return " ".join(parts)


def build_daily_recommendations(
    *,
    weekday: str,
    tithi_name: str,
    moon_nakshatra: str,
    dasha_md: str,
    dasha_ad: str,
    transit_aspects: list[dict[str, Any]],
    is_chandrashtama: bool,
) -> list[str]:
    """Build human-readable recommendation sentences from knowledge files.

    Sources: vara good_for/avoid + tithi + nakshatra best_for + dasha advice.
    Returns: List of 3-6 actionable sentences.
    """
    recs: list[str] = []

    # 0. Chandrashtama (critical warning — insert first so it's never truncated)
    if is_chandrashtama:
        recs.append("Chandrashtama: Postpone important decisions and travel.")

    # 1. Vara guidance
    vara = get_vara_guidance(weekday)
    if vara["good_for"]:
        items = ", ".join(vara["good_for"][:3])
        recs.append(f"{weekday.title()} favors: {items}.")
    if vara["avoid"]:
        items = ", ".join(vara["avoid"][:2])
        recs.append(f"Avoid on {weekday.title()}: {items}.")

    # 2. Tithi guidance
    tithi = get_tithi_guidance(tithi_name)
    if tithi["good_for"]:
        items = ", ".join(tithi["good_for"][:3])
        recs.append(f"{tithi_name}: Good for {items}.")

    # 3. Moon nakshatra best_for
    nak = get_nakshatra_transit_text("moon", moon_nakshatra)
    if nak["best_for"]:
        items = ", ".join(nak["best_for"][:2])
        recs.append(f"Moon in {moon_nakshatra}: {items}.")
    if nak["avoid"]:
        items = ", ".join(nak["avoid"][:2])
        recs.append(f"Avoid during {moon_nakshatra}: {items}.")

    # 4. Dasha-specific career/relationship tip
    ad = get_antardasha_text(dasha_md, dasha_ad)
    if ad["career"]:
        # Take first sentence only
        first_sentence = ad["career"].split(".")[0]
        if first_sentence:
            recs.append(f"Dasha focus: {first_sentence}.")

    # 5. Transit aspect advice (tight aspects only)
    for asp in transit_aspects[:1]:
        if asp.get("orb", 99) <= 3:
            effect = get_transit_aspect_effect(
                asp.get("transit", ""),
                asp.get("natal", ""),
                asp.get("aspect", ""),
            )
            if effect:
                planet = asp.get("transit", "").title()
                recs.append(f"{planet} transit: {effect}.")
                break

    return recs[:6]  # cap at 6


def build_weekly_summary(
    *,
    overall_rating: float,  # noqa: ARG001
    dasha_md: str,
    dasha_ad: str,
    key_transits: list[dict[str, Any]],
    areas: dict[str, Any],
) -> str:
    """Build a rich weekly summary from knowledge.

    Combines: dasha theme + top area + key transit effects.
    """
    parts: list[str] = []

    # 1. Dasha context
    ad_text = get_antardasha_text(dasha_md, dasha_ad)
    if ad_text["general_effects"]:
        parts.append(ad_text["general_effects"][0] + ".")

    # 2. Top and bottom areas
    sorted_areas = sorted(areas.items(), key=lambda x: x[1].get("rating", 5), reverse=True)
    if sorted_areas:
        top = sorted_areas[0]
        bottom = sorted_areas[-1]
        parts.append(
            f"Strongest area: {top[0].title()} ({top[1].get('rating', '?')}/10). "
            f"Needs attention: {bottom[0].title()} ({bottom[1].get('rating', '?')}/10)."
        )

    # 3. Key transit effect
    for t in key_transits[:1]:
        effect = get_transit_aspect_effect(
            t.get("transit", ""),
            t.get("natal", ""),
            t.get("aspect", ""),
        )
        if effect:
            parts.append(effect + ".")
            break

    return " ".join(parts)


def build_weekly_recommendations(
    *,
    dasha_md: str,
    dasha_ad: str,
    key_transits: list[dict[str, Any]],
) -> list[str]:
    """Build weekly recommendations from knowledge."""
    recs: list[str] = []

    # Dasha advice
    ad = get_antardasha_text(dasha_md, dasha_ad)
    if ad["positive"]:
        recs.append(f"This period supports: {ad['positive'][0]}.")
    if ad["negative"]:
        recs.append(f"Watch for: {ad['negative'][0]}.")
    if ad["career"]:
        first = ad["career"].split(".")[0]
        if first:
            recs.append(f"Career: {first}.")
    if ad["relationships"]:
        first = ad["relationships"].split(".")[0]
        if first:
            recs.append(f"Relationships: {first}.")

    # Key transit recommendations
    for t in key_transits[:2]:
        effect = get_transit_aspect_effect(
            t.get("transit", ""),
            t.get("natal", ""),
            t.get("aspect", ""),
        )
        if effect:
            planet = t.get("transit", "").title()
            recs.append(f"{planet} transit: {effect}.")

    return recs[:5]


def build_monthly_summary(
    *,
    month_rating: float,  # noqa: ARG001
    dasha_md: str,
    dasha_ad: str,
    double_transit_houses: list[int],
    best_area: str | None,
    weakest_area: str | None,
) -> str:
    """Build a rich monthly summary from knowledge.

    Combines: dasha guide theme + double transit effects + area highlights.
    """
    parts: list[str] = []

    # 1. Dasha macro theme
    guide = get_dasha_guide(dasha_md)
    if guide.get("theme"):
        parts.append(f"{dasha_md.title()} Mahadasha: {guide['theme']}.")

    # 2. Antardasha context
    ad = get_antardasha_text(dasha_md, dasha_ad)
    if ad["general_effects"]:
        parts.append(ad["general_effects"][0] + ".")

    # 3. Double transit effects
    for house in double_transit_houses[:2]:
        dt = get_double_transit_text(house)
        if dt["themes"]:
            themes = ", ".join(dt["themes"][:2])
            parts.append(f"Jupiter-Saturn activate house {house}: {themes}.")

    # 4. Best/weakest areas
    if best_area and weakest_area:
        parts.append(f"Strongest: {best_area.title()}. Needs care: {weakest_area.title()}.")

    return " ".join(parts)


def build_monthly_recommendations(
    *,
    dasha_md: str,
    dasha_ad: str,
    double_transit_houses: list[int],
) -> list[str]:
    """Build monthly recommendations from knowledge."""
    recs: list[str] = []

    # Dasha guide practical advice
    guide = get_dasha_guide(dasha_md)
    for advice in guide.get("practical_advice", [])[:2]:
        recs.append(advice)

    # Dasha opportunities
    if guide.get("opportunities"):
        first = guide["opportunities"].split(".")[0]
        if first:
            recs.append(f"Opportunity: {first}.")

    # Double transit typical events
    for house in double_transit_houses[:2]:
        dt = get_double_transit_text(house)
        for event in dt.get("typical_events", [])[:1]:
            recs.append(f"House {house}: {event}.")

    # Antardasha health/relationship tips
    ad = get_antardasha_text(dasha_md, dasha_ad)
    if ad["health"]:
        first = ad["health"].split(".")[0]
        if first:
            recs.append(f"Health: {first}.")

    return recs[:6]
