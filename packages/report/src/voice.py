"""Voice-transform helpers — placement → modern human language.

A small library of pattern → modern-translation mappings used by the
narrative synthesizer to keep the report's voice consistent: warm,
direct, modern, no woo-woo. References to ancient sources stay precise
(BPHS chapter, Jaimini sutra) but the descriptions sound like a sharp
friend explaining your chart, not a Sanskrit recitation.
"""

from __future__ import annotations

# ── Lagna lord nature → modern descriptor ──
LAGNA_DESCRIPTORS: dict[str, str] = {
    "aries": "you lead with your body and your bluntness; people feel your presence before your words",
    "taurus": "you move slow on purpose; comfort, beauty, and what's solid matter more than what's exciting",
    "gemini": "you live in your head, your phone, and your ten parallel conversations; ideas are your love language",
    "cancer": "you feel everything everyone else is feeling, then act surprised when you're tired",
    "leo": "you're built to be seen; if no one's watching, you'll perform for yourself",
    "virgo": "you spot what's wrong before what's right; your standards are how you say I love you",
    "libra": "you read the room before you speak; harmony is currency, but it costs you to maintain",
    "scorpio": "you show 30%, hold 70%; intensity scares others before it scares you",
    "sagittarius": "you can't sit still in someone else's small story; meaning beats comfort every time",
    "capricorn": "you'd rather build for ten years than win in one; you trust structure more than people",
    "aquarius": "you observe humans like a curious anthropologist; the future is where you actually live",
    "pisces": "you absorb your surroundings like sponge; boundaries are your hardest course",
}


# ── Moon sign → emotional weather ──
MOON_DESCRIPTORS: dict[str, str] = {
    "aries": "your moods arrive without warning and leave the same way",
    "taurus": "you process slowly; food, sleep, and physical comfort regulate you more than therapy",
    "gemini": "your mind never stops talking to itself; silence feels foreign",
    "cancer": "your mood IS the weather; people learn to read it",
    "leo": "you need to be witnessed to feel real; alone too long and you start to fade",
    "virgo": "you analyze your own emotions in real-time; feeling something raw is almost rude to your system",
    "libra": "you're emotionally diplomatic; you rarely tell yourself what you actually feel",
    "scorpio": "you go all-in or you disappear; there's no middle setting on your emotional dial",
    "sagittarius": "you'd rather feel free than feel understood",
    "capricorn": "you contain feelings until they're useful; the bill comes later",
    "aquarius": "you process emotions intellectually first; sometimes they never make it to feeling",
    "pisces": "you feel things that don't even belong to you; the empath tax is real",
}


# ── Planet placements: planet × house mini-descriptors ──
# Used as building blocks. Format: PLANET_HOUSE[(planet, house)] = phrase
PLANET_HOUSE: dict[tuple[str, int], str] = {
    ("sun", 1): "you are who you are loudly; ego and identity are fused",
    ("sun", 2): "your sense of self is wrapped in family money, voice, and what you can hold",
    ("sun", 7): "you find yourself through partnership; you don't fully exist alone",
    ("sun", 10): "career is identity; without work you don't know who you are",
    ("moon", 1): "you wear your moods on your face; people read you in seconds",
    ("moon", 4): "home is where you actually live, even if you live elsewhere",
    ("moon", 5): "feelings flow into creative expression; emotion is your art",
    ("moon", 6): "your emotional default is service-and-struggle; rest feels suspicious",
    ("mars", 3): "you talk fast, write sharp, fight quick; siblings know your edges",
    ("mars", 10): "career energy is combat-coded; you push hard, sometimes break things",
    ("mercury", 1): "your intelligence is the front door; people meet your mind first",
    ("mercury", 2): "you make money through what you say and how you say it",
    ("jupiter", 1): "you carry teacher energy whether you mean to or not",
    ("jupiter", 5): "wisdom flows through creativity, children, and what you teach",
    ("jupiter", 9): "you're a natural pilgrim; long journeys reveal what cities can't",
    ("jupiter", 12): "you find truth in solitude, foreign places, and behind closed doors",
    ("venus", 3): "your charm shows up in writing, voice, and short trips",
    ("venus", 4): "your home is where beauty lives; aesthetic standards run deep",
    ("venus", 7): "you marry beauty, possibly more than once",
    ("saturn", 4): "home was built with discipline; foundation is your strength",
    ("saturn", 5): "creativity through long-arc work; you build slowly, but it lasts",
    ("saturn", 10): "career is your spiritual practice; recognition arrives late but stays",
    ("rahu", 2): "money is dramatic; speech and family wealth keep changing shape",
    ("rahu", 11): "your network is your fortune, but the rules of it keep shifting",
    (
        "ketu",
        5,
    ): "old creative pursuits dissolve; spiritual restlessness about romance and children",
    (
        "ketu",
        8,
    ): "you survive transformations like you've done it before; the occult feels familiar",
    ("ketu", 9): "the dharma path keeps slipping; pilgrimage is your default coping mode",
}


# ── Yoga → modern one-liner ──
YOGA_MODERN: dict[str, str] = {
    "Sasa Yoga": "you're built for long-arc structure work — Saturn in own sign in a kendra",
    "Hamsa Yoga": "exalted Jupiter in a kendra — you carry teacher/guide energy without trying",
    "Malavya Yoga": "Venus in own sign in a kendra — beauty, refinement, and aesthetic command",
    "Gaja Kesari Yoga": "Jupiter and Moon in mutual kendra — wisdom + emotional intelligence combo",
    "Vasumati Yoga": "benefics in upachayas — money grows through compounding effort, not luck",
    "Harsha Yoga (6th Lord Viparita)": "you defeat enemies, illness, and competition by *not fighting them directly*",
    "Sarala Yoga (8th Lord Viparita)": "you survive transformations and crises in ways that look like luck to others",
    "Vimala Yoga (12th Lord Viparita)": "your losses turn into gains; expense becomes investment over time",
    "Adhi Yoga from Lagna": "benefics behind your lagna protect you in ways you don't notice",
    "Daridra Yoga (Lords in Dusthana)": "money has been structurally hard for you; this is a real placement, not your fault",
    "Dhana Yoga (1st Lord in 2nd)": "your wealth lord lives in your wealth house — earnings flow through who you are",
    "Mangal Dosha": "Mars sits in a marriage-friction position; partnerships need care, not avoidance",
    "Surya Grahan Dosha": "Sun + Rahu in same sign — speech and identity carry shadow themes",
}


# ── Dasha lord → modern keyword ──
DASHA_KEYWORD: dict[str, str] = {
    "sun": "authority, recognition, ego, father themes",
    "moon": "emotion, comfort, mother, public reception",
    "mars": "drive, conflict, action, brothers, real estate",
    "mercury": "intellect, communication, business, learning",
    "jupiter": "expansion, wisdom, foreign, teaching, children",
    "venus": "love, beauty, money, aesthetics, partnership",
    "saturn": "discipline, delay, structure, hard-won achievement",
    "rahu": "ambition, foreign, sudden gain, obsession",
    "ketu": "dissolution, mysticism, detachment, sudden loss",
}


# ── Composite score → mood label (reused from state_engine) ──
COMPOSITE_LABEL: dict[float, str] = {
    8.5: "Thriving",
    7.0: "Flowing",
    5.5: "Steady",
    4.0: "Challenged",
    2.5: "Struggling",
    0.0: "Turbulent",
}


def composite_to_label(score: float) -> str:
    """Return the modern label for a composite score 0-10."""
    for threshold in sorted(COMPOSITE_LABEL.keys(), reverse=True):
        if score >= threshold:
            return COMPOSITE_LABEL[threshold]
    return "Turbulent"


def planet_house_phrase(planet: str, house: int) -> str | None:
    """Return the modern descriptor for a planet-house combo, if available."""
    return PLANET_HOUSE.get((planet.lower(), house))


def yoga_phrase(yoga_name: str) -> str | None:
    """Return the modern description for a named yoga, if available."""
    return YOGA_MODERN.get(yoga_name)
