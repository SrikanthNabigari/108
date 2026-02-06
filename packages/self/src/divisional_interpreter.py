"""Divisional chart interpretation for 108 Vedic Astrology.

Interprets planet placements in divisional charts (D2 through D60)
using knowledge/rules/divisional_interpretation.json for D9/D10,
and BPHS-based interpretations in code for all other divisional charts.
"""

from typing import Any

from packages.core.src.knowledge_loader import get_divisional_interpretation
from packages.cosmos.src.divisional import DivisionalChart, get_divisional_chart

_interp_cache: dict[str, Any] | None = None


def _get_interp() -> dict[str, Any]:
    """Get cached divisional interpretation rules."""
    global _interp_cache
    if _interp_cache is None:
        _interp_cache = get_divisional_interpretation()
    return _interp_cache


RASHI_NAMES_LOWER = [
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

# Sign element classification
_FIRE_SIGNS = {"aries", "leo", "sagittarius"}
_EARTH_SIGNS = {"taurus", "virgo", "capricorn"}
_AIR_SIGNS = {"gemini", "libra", "aquarius"}
_WATER_SIGNS = {"cancer", "scorpio", "pisces"}

# Planet nature classification
_BENEFIC_PLANETS = {"jupiter", "venus", "moon", "mercury"}
_MALEFIC_PLANETS = {"sun", "mars", "saturn", "rahu", "ketu"}

# Planet exaltation signs
_PLANET_EXALTATION = {
    "sun": "aries",
    "moon": "taurus",
    "mars": "capricorn",
    "mercury": "virgo",
    "jupiter": "cancer",
    "venus": "pisces",
    "saturn": "libra",
}

# Planet debilitation signs
_PLANET_DEBILITATION = {
    "sun": "libra",
    "moon": "scorpio",
    "mars": "cancer",
    "mercury": "pisces",
    "jupiter": "capricorn",
    "venus": "virgo",
    "saturn": "aries",
}

# Planet own signs
_PLANET_OWN_SIGNS = {
    "sun": {"leo"},
    "moon": {"cancer"},
    "mars": {"aries", "scorpio"},
    "mercury": {"gemini", "virgo"},
    "jupiter": {"sagittarius", "pisces"},
    "venus": {"taurus", "libra"},
    "saturn": {"capricorn", "aquarius"},
}


def _get_dignity(planet: str, rashi: str) -> str:
    """Get planet's dignity in a sign."""
    p = planet.lower()
    r = rashi.lower()
    if _PLANET_EXALTATION.get(p) == r:
        return "exalted"
    if _PLANET_DEBILITATION.get(p) == r:
        return "debilitated"
    if r in _PLANET_OWN_SIGNS.get(p, set()):
        return "own_sign"
    return "neutral"


def _get_element(rashi: str) -> str:
    """Get the element of a rashi."""
    r = rashi.lower()
    if r in _FIRE_SIGNS:
        return "fire"
    if r in _EARTH_SIGNS:
        return "earth"
    if r in _AIR_SIGNS:
        return "air"
    if r in _WATER_SIGNS:
        return "water"
    return "unknown"


def interpret_d9_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D9 (Navamsha) chart.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with theme, marriage, dharma, strength, characteristics.
    """
    interp = _get_interp()
    d9 = interp.get("d9_navamsha", {})
    planet_data = d9.get("planet_in_signs", {}).get(planet.lower(), {})
    sign_data = planet_data.get(rashi_name.lower(), {})

    if not sign_data:
        return {
            "planet": planet.lower(),
            "rashi": rashi_name.lower(),
            "found": False,
        }

    return {
        "planet": planet.lower(),
        "rashi": rashi_name.lower(),
        "found": True,
        "theme": sign_data.get("theme", ""),
        "marriage": sign_data.get("marriage", ""),
        "dharma": sign_data.get("dharma", ""),
        "strength": sign_data.get("strength", ""),
        "characteristics": sign_data.get("characteristics", ""),
    }


def interpret_d10_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D10 (Dashamsha) chart.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with theme, career, leadership, strength, characteristics.
    """
    interp = _get_interp()
    d10 = interp.get("d10_dashamsha", {})
    planet_data = d10.get("planet_in_signs", {}).get(planet.lower(), {})
    sign_data = planet_data.get(rashi_name.lower(), {})

    if not sign_data:
        return {
            "planet": planet.lower(),
            "rashi": rashi_name.lower(),
            "found": False,
        }

    return {
        "planet": planet.lower(),
        "rashi": rashi_name.lower(),
        "found": True,
        "theme": sign_data.get("theme", ""),
        "career": sign_data.get("career", ""),
        "leadership": sign_data.get("leadership", ""),
        "strength": sign_data.get("strength", ""),
        "characteristics": sign_data.get("characteristics", ""),
    }


def interpret_d2_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D2 (Hora) chart.

    D2 Hora divides each sign into two halves (Sun/Moon hora).
    It reveals wealth, finances, and material accumulation capacity.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)
    element = _get_element(r)

    # D2 wealth themes per planet
    wealth_themes = {
        "sun": {
            "summary": "Wealth through authority, government, and leadership",
            "key_themes": ["government income", "father's wealth", "authority-based earning"],
            "positive": "Strong capacity for earning through status and power",
            "negative": "Ego-driven spending, losses through pride",
        },
        "moon": {
            "summary": "Wealth through public, nurturing, and emotional intelligence",
            "key_themes": ["public income", "mother's wealth", "emotional investments"],
            "positive": "Good instinct for profitable ventures, public support",
            "negative": "Fluctuating finances, emotional spending",
        },
        "mars": {
            "summary": "Wealth through courage, real estate, and technical skills",
            "key_themes": ["property income", "engineering", "military/police career"],
            "positive": "Ability to acquire property, bold financial moves",
            "negative": "Impulsive spending, losses through aggression",
        },
        "mercury": {
            "summary": "Wealth through intellect, trade, and communication",
            "key_themes": ["business income", "writing", "commerce"],
            "positive": "Smart financial decisions, multiple income sources",
            "negative": "Scattered investments, overthinking finances",
        },
        "jupiter": {
            "summary": "Wealth through wisdom, teaching, and divine grace",
            "key_themes": ["dharmic wealth", "teaching income", "inherited wealth"],
            "positive": "Natural abundance, wealth grows with knowledge",
            "negative": "Over-generosity, losses through misplaced trust",
        },
        "venus": {
            "summary": "Wealth through luxury, arts, and partnerships",
            "key_themes": ["luxury goods", "creative income", "spouse's wealth"],
            "positive": "Attraction to wealth, luxurious lifestyle",
            "negative": "Excessive spending on pleasures, financial indulgence",
        },
        "saturn": {
            "summary": "Wealth through discipline, service, and long-term effort",
            "key_themes": ["slow steady income", "labor-based wealth", "old industries"],
            "positive": "Wealth accumulated through patience and hard work",
            "negative": "Delayed wealth, poverty in early life",
        },
        "rahu": {
            "summary": "Wealth through unconventional means and foreign sources",
            "key_themes": ["foreign income", "technology wealth", "speculation"],
            "positive": "Sudden gains, wealth from foreign or tech sources",
            "negative": "Unstable wealth, deceptive financial dealings",
        },
        "ketu": {
            "summary": "Wealth through spiritual pursuits and detachment",
            "key_themes": ["spiritual income", "research gains", "mystical healing"],
            "positive": "Unexpected gains, wealth from spiritual services",
            "negative": "Disinterest in accumulation, financial losses",
        },
    }

    base = wealth_themes.get(
        p,
        {
            "summary": "Financial patterns indicated by this placement",
            "key_themes": ["general wealth"],
            "positive": "Potential for financial growth",
            "negative": "Need for careful financial management",
        },
    )

    # Modify based on dignity
    specific = f"{p.title()} in {r.title()} in D2 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent wealth potential, strong financial acumen."
    elif dignity == "own_sign":
        specific += "Good wealth retention, comfortable financial position."
    elif dignity == "debilitated":
        specific += "Challenges in wealth accumulation, needs remedial measures."
    else:
        if element == "earth":
            specific += "Material wealth through practical means."
        elif element == "water":
            specific += "Wealth through emotional intelligence and intuition."
        elif element == "fire":
            specific += "Wealth through initiative and leadership."
        else:
            specific += "Wealth through communication and networking."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d3_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D3 (Drekkana) chart.

    D3 Drekkana divides each sign into 3 parts (10 degrees each).
    It reveals siblings, courage, co-borns, and one's initiative.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    sibling_themes = {
        "sun": {
            "summary": "Leadership among siblings, authoritative elder brother",
            "key_themes": ["elder sibling dominance", "father-like role in siblings"],
            "positive": "Protective elder sibling, strong co-born support",
            "negative": "Ego clashes with siblings, domineering tendency",
        },
        "moon": {
            "summary": "Emotional bonds with siblings, nurturing co-borns",
            "key_themes": ["emotional sibling bonds", "mother-like sister"],
            "positive": "Close emotional ties with siblings, caring co-borns",
            "negative": "Emotional dependency on siblings, mood-driven conflicts",
        },
        "mars": {
            "summary": "Courage and valor, competitive siblings",
            "key_themes": ["younger siblings", "courage", "physical prowess"],
            "positive": "Great personal courage, brave siblings, martial ability",
            "negative": "Fights with siblings, accidents, aggressive co-borns",
        },
        "mercury": {
            "summary": "Communicative siblings, intellectual co-borns",
            "key_themes": ["communication with siblings", "intellectual bonds"],
            "positive": "Good rapport with siblings, shared learning",
            "negative": "Gossip among siblings, superficial bonds",
        },
        "jupiter": {
            "summary": "Wise and supportive siblings, spiritual co-borns",
            "key_themes": ["elder siblings as guides", "dharmic brothers"],
            "positive": "Siblings bring good fortune, wise elder brothers",
            "negative": "Over-reliance on siblings for guidance",
        },
        "venus": {
            "summary": "Harmonious sibling relationships, artistic co-borns",
            "key_themes": ["sisters", "artistic siblings", "pleasant bonds"],
            "positive": "Beautiful sibling relationships, artistic sisters",
            "negative": "Jealousy among siblings, luxury-related conflicts",
        },
        "saturn": {
            "summary": "Delayed or distant sibling relationships",
            "key_themes": ["separation from siblings", "elder siblings' hardship"],
            "positive": "Responsible siblings, long-lasting bonds through effort",
            "negative": "Few siblings, separation, delayed support from co-borns",
        },
        "rahu": {
            "summary": "Unconventional siblings, foreign connections",
            "key_themes": ["foreign siblings", "unusual co-borns", "adoptive siblings"],
            "positive": "Unique and helpful co-borns, siblings in foreign lands",
            "negative": "Deception from siblings, broken trust among co-borns",
        },
        "ketu": {
            "summary": "Spiritual siblings, detachment from co-borns",
            "key_themes": ["spiritual brothers", "detachment", "loss of siblings"],
            "positive": "Spiritually inclined siblings, past-life bonds",
            "negative": "Loss of siblings, emotional distance from co-borns",
        },
    }

    base = sibling_themes.get(
        p,
        {
            "summary": "Sibling dynamics indicated by this placement",
            "key_themes": ["siblings", "courage"],
            "positive": "Potential for supportive siblings",
            "negative": "Challenges in sibling relationships",
        },
    )

    specific = f"{p.title()} in {r.title()} in D3 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent courage, strong and supportive siblings."
    elif dignity == "own_sign":
        specific += "Good sibling bonds, natural courage and initiative."
    elif dignity == "debilitated":
        specific += "Challenges with siblings, lack of courage in some areas."
    else:
        specific += "Moderate sibling support and courage levels."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d4_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D4 (Chaturthamsha) chart.

    D4 divides each sign into 4 parts (7.5 degrees each).
    It reveals property, fortune, fixed assets, and happiness from home.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)
    element = _get_element(r)

    property_themes = {
        "sun": {
            "summary": "Government property, ancestral estates from father",
            "key_themes": ["inherited property", "government grants", "father's fortune"],
            "positive": "Gains property through authority, well-built home",
            "negative": "Property disputes with government, tax issues",
        },
        "moon": {
            "summary": "Beautiful home, property near water, mother's fortune",
            "key_themes": ["domestic happiness", "waterside property", "mother's assets"],
            "positive": "Comfortable home, good fortune from mother's side",
            "negative": "Frequent changes of residence, fluctuating property values",
        },
        "mars": {
            "summary": "Land ownership, real estate, construction",
            "key_themes": ["land acquisition", "construction", "rural property"],
            "positive": "Multiple properties, gains through real estate",
            "negative": "Property disputes, damage to property, litigation",
        },
        "mercury": {
            "summary": "Commercial property, urban apartments, multiple residences",
            "key_themes": ["commercial property", "urban dwelling", "rental income"],
            "positive": "Smart property investments, income from rentals",
            "negative": "Documents issues, property fraud, title disputes",
        },
        "jupiter": {
            "summary": "Spacious home, religious property, temple land",
            "key_themes": ["large estates", "religious property", "educational institutions"],
            "positive": "Abundant property, blessed home, spiritual environment",
            "negative": "Over-investment in property, neglecting maintenance",
        },
        "venus": {
            "summary": "Luxurious home, beautiful gardens, artistic property",
            "key_themes": ["luxury home", "gardens", "vehicles"],
            "positive": "Beautiful and comfortable living space, artistic decor",
            "negative": "Excessive spending on home beautification",
        },
        "saturn": {
            "summary": "Old property, delayed acquisition, ancestral land",
            "key_themes": ["old buildings", "delayed property", "inherited land"],
            "positive": "Durable property, long-term real estate gains",
            "negative": "Delayed property acquisition, dilapidated buildings",
        },
        "rahu": {
            "summary": "Foreign property, unconventional living arrangements",
            "key_themes": ["foreign property", "apartment living", "unusual homes"],
            "positive": "Property in foreign lands, modern housing",
            "negative": "Property disputes, haunted or problematic property",
        },
        "ketu": {
            "summary": "Spiritual retreats, detachment from material property",
            "key_themes": ["ashram living", "minimal possessions", "spiritual property"],
            "positive": "Peace at home, spiritual environment",
            "negative": "Loss of property, fire damage, instability",
        },
    }

    base = property_themes.get(
        p,
        {
            "summary": "Property and fortune patterns indicated",
            "key_themes": ["property", "fixed assets"],
            "positive": "Potential for property acquisition",
            "negative": "Challenges related to immovable assets",
        },
    )

    specific = f"{p.title()} in {r.title()} in D4 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent for property acquisition and domestic happiness."
    elif dignity == "own_sign":
        specific += "Comfortable home life, stable property holdings."
    elif dignity == "debilitated":
        specific += "Difficulties with property, domestic unhappiness possible."
    else:
        if element == "earth":
            specific += "Good for land and agricultural property."
        elif element == "water":
            specific += "Property near water bodies, comfortable home."
        else:
            specific += "Moderate property luck."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d7_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D7 (Saptamsha) chart.

    D7 divides each sign into 7 parts. It reveals children,
    progeny, creative output, and one's capacity for procreation.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    children_themes = {
        "sun": {
            "summary": "Authoritative relationship with children, strong firstborn",
            "key_themes": ["firstborn son", "father-child bond", "leadership in children"],
            "positive": "Children achieve authority and fame, strong male progeny",
            "negative": "Ego clashes with children, controlling parenting",
        },
        "moon": {
            "summary": "Nurturing parent, emotional bond with children",
            "key_themes": ["daughters", "emotional parenting", "fertility"],
            "positive": "Many children, strong emotional bonds, fertile",
            "negative": "Over-emotional parenting, worry about children",
        },
        "mars": {
            "summary": "Energetic children, active and athletic offspring",
            "key_themes": ["athletic children", "courage in progeny", "boys"],
            "positive": "Brave and active children, strong male progeny",
            "negative": "Aggressive children, accidents involving children",
        },
        "mercury": {
            "summary": "Intelligent children, academic excellence in progeny",
            "key_themes": ["intelligent children", "academic progeny", "communication"],
            "positive": "Brilliant children, good education for offspring",
            "negative": "Nervous or anxious children, speech issues in progeny",
        },
        "jupiter": {
            "summary": "Blessed progeny, wise and dharmic children",
            "key_themes": ["blessed children", "spiritual progeny", "putra yoga"],
            "positive": "Multiple children, wise and virtuous offspring",
            "negative": "Over-indulgent with children, spoiled progeny",
        },
        "venus": {
            "summary": "Beautiful and artistic children, daughters",
            "key_themes": ["daughters", "artistic children", "beauty in progeny"],
            "positive": "Beautiful children, artistic talents in offspring",
            "negative": "Over-attached to children, spoiled offspring",
        },
        "saturn": {
            "summary": "Delayed children, disciplined but few offspring",
            "key_themes": ["delayed progeny", "few children", "disciplined offspring"],
            "positive": "Responsible children, disciplined offspring",
            "negative": "Delayed childbirth, few children, sorrow from progeny",
        },
        "rahu": {
            "summary": "Unconventional children, adoption possible",
            "key_themes": ["adopted children", "unusual progeny", "foreign-born children"],
            "positive": "Unique and talented children, exceptional offspring",
            "negative": "Misunderstandings with children, unconventional situations",
        },
        "ketu": {
            "summary": "Spiritual children, detachment from progeny",
            "key_themes": ["spiritual offspring", "detachment", "past-life child karma"],
            "positive": "Spiritually inclined children, moksha-oriented progeny",
            "negative": "Separation from children, loss or delay in progeny",
        },
    }

    base = children_themes.get(
        p,
        {
            "summary": "Progeny patterns indicated by this placement",
            "key_themes": ["children", "progeny"],
            "positive": "Potential for blessed children",
            "negative": "Challenges related to progeny",
        },
    )

    specific = f"{p.title()} in {r.title()} in D7 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent for children, blessed progeny."
    elif dignity == "own_sign":
        specific += "Good relationship with children, healthy offspring."
    elif dignity == "debilitated":
        specific += "Challenges with progeny, delayed or difficult childbirth."
    else:
        specific += "Moderate indications for progeny matters."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d12_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D12 (Dwadashamsha) chart.

    D12 divides each sign into 12 parts (2.5 degrees each).
    It reveals parents, ancestry, lineage, and karmic heritage.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    parent_themes = {
        "sun": {
            "summary": "Strong father figure, paternal lineage prominent",
            "key_themes": ["father's health", "paternal ancestry", "father's status"],
            "positive": "Distinguished father, strong paternal lineage",
            "negative": "Conflicts with father, paternal health issues",
        },
        "moon": {
            "summary": "Nurturing mother, maternal lineage supportive",
            "key_themes": ["mother's health", "maternal ancestry", "mother's care"],
            "positive": "Loving mother, strong maternal support",
            "negative": "Emotional dependency on mother, maternal health concerns",
        },
        "mars": {
            "summary": "Energetic parents, warrior ancestry",
            "key_themes": ["military ancestry", "land-owning parents", "parental courage"],
            "positive": "Brave parents, property from ancestors",
            "negative": "Conflicts with parents, ancestral disputes",
        },
        "mercury": {
            "summary": "Intellectual parents, scholarly lineage",
            "key_themes": ["educated parents", "scholarly ancestry", "communication"],
            "positive": "Well-educated parents, intellectual heritage",
            "negative": "Nervous parents, unstable ancestral patterns",
        },
        "jupiter": {
            "summary": "Spiritual parents, dharmic ancestry",
            "key_themes": ["priestly lineage", "dharmic parents", "blessings from ancestors"],
            "positive": "Blessed lineage, wise and spiritual parents",
            "negative": "Over-reliance on ancestral merit",
        },
        "venus": {
            "summary": "Comfortable parents, artistic lineage",
            "key_themes": ["wealthy parents", "artistic ancestry", "comfort"],
            "positive": "Wealthy parents, luxurious upbringing",
            "negative": "Indulgent parents, ancestral debts from luxury",
        },
        "saturn": {
            "summary": "Hardworking parents, humble ancestry",
            "key_themes": ["working-class parents", "difficult ancestry", "longevity"],
            "positive": "Long-lived parents, strong work ethic from ancestry",
            "negative": "Separation from parents, difficult childhood",
        },
        "rahu": {
            "summary": "Unconventional parents, mixed ancestry",
            "key_themes": ["foreign ancestry", "mixed lineage", "adoption"],
            "positive": "Unique heritage, progressive parents",
            "negative": "Unknown ancestry, secrets in family history",
        },
        "ketu": {
            "summary": "Spiritual ancestry, detachment from parents",
            "key_themes": ["spiritual lineage", "past-life parents", "renunciation"],
            "positive": "Spiritually evolved ancestry, past-life merits",
            "negative": "Loss of parents early, emotional distance",
        },
    }

    base = parent_themes.get(
        p,
        {
            "summary": "Parental and ancestral patterns indicated",
            "key_themes": ["parents", "ancestry"],
            "positive": "Positive ancestral influences",
            "negative": "Challenges from ancestral karma",
        },
    )

    specific = f"{p.title()} in {r.title()} in D12 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent parental karma, distinguished lineage."
    elif dignity == "own_sign":
        specific += "Good relationship with parents, stable ancestry."
    elif dignity == "debilitated":
        specific += "Challenges with parents, ancestral karmic debts."
    else:
        specific += "Moderate ancestral influences."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d16_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D16 (Shodashamsha) chart.

    D16 divides each sign into 16 parts. It reveals vehicles,
    comforts, material happiness, and conveyances.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    comfort_themes = {
        "sun": {
            "summary": "Government vehicles, luxury through authority",
            "key_themes": ["official vehicles", "status symbols", "authority comforts"],
            "positive": "Access to luxury vehicles, government perks",
            "negative": "Ego through possessions, vehicle-related authority issues",
        },
        "moon": {
            "summary": "Comfortable lifestyle, water-related vehicles",
            "key_themes": ["domestic comfort", "boats", "emotional satisfaction"],
            "positive": "Comfortable living, good vehicles, mental peace from comforts",
            "negative": "Attachment to comforts, restless about material happiness",
        },
        "mars": {
            "summary": "Sports vehicles, machinery, adventure-related comforts",
            "key_themes": ["sports cars", "machinery", "adventure vehicles"],
            "positive": "Powerful vehicles, mechanical aptitude",
            "negative": "Vehicle accidents, rash driving, mechanical failures",
        },
        "mercury": {
            "summary": "Communication vehicles, technology comforts",
            "key_themes": ["technology", "communication devices", "urban transport"],
            "positive": "Latest technology, multiple vehicles, smart transport",
            "negative": "Vehicle theft, issues with electronic equipment",
        },
        "jupiter": {
            "summary": "Spacious vehicles, spiritual comforts",
            "key_themes": ["large vehicles", "spiritual amenities", "educational comforts"],
            "positive": "Large comfortable vehicles, spiritual happiness",
            "negative": "Excessive comfort-seeking, neglecting simplicity",
        },
        "venus": {
            "summary": "Luxury vehicles, artistic comforts, beauty",
            "key_themes": ["luxury cars", "artistic possessions", "aesthetic comfort"],
            "positive": "Beautiful vehicles, luxurious lifestyle, artistic pleasures",
            "negative": "Over-spending on luxury, attachment to comfort",
        },
        "saturn": {
            "summary": "Delayed vehicles, old but durable comforts",
            "key_themes": ["delayed acquisition", "second-hand vehicles", "durability"],
            "positive": "Durable possessions, eventual comfort through effort",
            "negative": "Delayed comforts, old vehicles, lack of luxury",
        },
        "rahu": {
            "summary": "Foreign vehicles, unconventional comforts",
            "key_themes": ["imported vehicles", "unique possessions", "technology"],
            "positive": "Exotic vehicles, foreign comforts, latest technology",
            "negative": "Vehicle problems, stolen property, illusory comforts",
        },
        "ketu": {
            "summary": "Minimal comforts, spiritual satisfaction over material",
            "key_themes": ["detachment from luxury", "simple living", "spiritual comfort"],
            "positive": "Inner contentment, freedom from material attachment",
            "negative": "Loss of vehicles, damage to property, lack of comfort",
        },
    }

    base = comfort_themes.get(
        p,
        {
            "summary": "Vehicle and comfort patterns indicated",
            "key_themes": ["vehicles", "comforts"],
            "positive": "Good material comforts possible",
            "negative": "Challenges with material pleasures",
        },
    )

    specific = f"{p.title()} in {r.title()} in D16 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent for vehicles and material comforts."
    elif dignity == "own_sign":
        specific += "Good vehicles and comfortable life."
    elif dignity == "debilitated":
        specific += "Vehicle problems, delayed comforts."
    else:
        specific += "Moderate comfort and vehicle indications."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d20_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D20 (Vimshamsha) chart.

    D20 divides each sign into 20 parts. It reveals spiritual progress,
    religious inclinations, and upasana (worship) patterns.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    spiritual_themes = {
        "sun": {
            "summary": "Sun worship, Surya Namaskar, Vedic rituals",
            "key_themes": ["Surya upasana", "Vedic rituals", "self-realization"],
            "positive": "Strong spiritual authority, Vedic knowledge, self-illumination",
            "negative": "Spiritual ego, rigid religious views",
        },
        "moon": {
            "summary": "Devotional bhakti, Moon worship, intuitive spirituality",
            "key_themes": ["bhakti yoga", "Devi worship", "intuitive spirituality"],
            "positive": "Deep devotion, intuitive spiritual path, emotional purity",
            "negative": "Emotional instability in spiritual life, superstition",
        },
        "mars": {
            "summary": "Tantric practices, Hanuman worship, martial discipline",
            "key_themes": ["tantra", "Hanuman bhakti", "tapas (austerity)"],
            "positive": "Intense spiritual discipline, tantric knowledge",
            "negative": "Aggressive spiritual practices, fanaticism",
        },
        "mercury": {
            "summary": "Mantra yoga, Vishnu worship, intellectual spirituality",
            "key_themes": ["mantra sadhana", "jnana yoga", "scriptural study"],
            "positive": "Mastery of mantras, intellectual understanding of dharma",
            "negative": "Over-intellectualizing spirituality, doubt on path",
        },
        "jupiter": {
            "summary": "Guru devotion, Vedantic path, traditional worship",
            "key_themes": ["guru bhakti", "Vedanta", "traditional dharma"],
            "positive": "True guru connection, deep scriptural wisdom, divine grace",
            "negative": "Over-reliance on external guru, spiritual complacency",
        },
        "venus": {
            "summary": "Lakshmi worship, bhakti through beauty and arts",
            "key_themes": ["Lakshmi puja", "devotional music", "aesthetic spirituality"],
            "positive": "Devotion through beauty, sacred arts, tantric balance",
            "negative": "Confusion between material and spiritual pleasure",
        },
        "saturn": {
            "summary": "Karma yoga, Shani worship, ascetic discipline",
            "key_themes": ["karma yoga", "asceticism", "Shani devotion"],
            "positive": "Deep discipline, karmic purification, mature spirituality",
            "negative": "Fear-based spirituality, excessive austerity",
        },
        "rahu": {
            "summary": "Unconventional spirituality, foreign religions",
            "key_themes": ["foreign spiritual paths", "occult", "unconventional meditation"],
            "positive": "Unique spiritual insights, cross-cultural wisdom",
            "negative": "Spiritual confusion, attraction to dark practices",
        },
        "ketu": {
            "summary": "Moksha path, deep meditation, past-life spiritual merit",
            "key_themes": ["moksha", "deep meditation", "Ganesha worship"],
            "positive": "Natural spiritual attainment, past-life sadhana bears fruit",
            "negative": "Spiritual confusion, aimless seeking, escapism",
        },
    }

    base = spiritual_themes.get(
        p,
        {
            "summary": "Spiritual development patterns indicated",
            "key_themes": ["spirituality", "worship"],
            "positive": "Spiritual growth potential",
            "negative": "Challenges on spiritual path",
        },
    )

    specific = f"{p.title()} in {r.title()} in D20 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent spiritual potential, rapid progress on chosen path."
    elif dignity == "own_sign":
        specific += "Natural inclination towards spiritual practices."
    elif dignity == "debilitated":
        specific += "Spiritual challenges, need for guided practice."
    else:
        specific += "Moderate spiritual inclinations."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d24_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D24 (Chaturvimshamsha) chart.

    D24 divides each sign into 24 parts. It reveals education,
    learning capacity, academic achievements, and knowledge.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    education_themes = {
        "sun": {
            "summary": "Education in administration, political science, authority",
            "key_themes": ["political studies", "administration", "leadership education"],
            "positive": "Excellence in administrative studies, government scholarships",
            "negative": "Ego in academic settings, conflicts with teachers",
        },
        "moon": {
            "summary": "Education in arts, psychology, humanities",
            "key_themes": ["arts education", "psychology", "emotional learning"],
            "positive": "Strong intuitive learning, creative education",
            "negative": "Emotional interference in studies, fluctuating focus",
        },
        "mars": {
            "summary": "Education in engineering, medicine, military",
            "key_themes": ["technical education", "surgery", "military academy"],
            "positive": "Excellence in technical subjects, competitive exams",
            "negative": "Aggressive in academic competition, exam anxiety",
        },
        "mercury": {
            "summary": "Education in commerce, languages, communication",
            "key_themes": ["commerce", "languages", "mathematics", "writing"],
            "positive": "Brilliant academic career, multiple degrees, polyglot",
            "negative": "Scattered focus, too many courses, superficial learning",
        },
        "jupiter": {
            "summary": "Education in philosophy, law, theology",
            "key_themes": ["higher education", "philosophy", "teaching", "law"],
            "positive": "Advanced degrees, professor potential, wisdom in learning",
            "negative": "Over-theoretical, impractical knowledge",
        },
        "venus": {
            "summary": "Education in fine arts, music, design",
            "key_themes": ["fine arts", "music education", "fashion design"],
            "positive": "Creative education, artistic mastery, aesthetic sense",
            "negative": "Distraction through romance during studies",
        },
        "saturn": {
            "summary": "Education in engineering, mining, traditional crafts",
            "key_themes": ["hard sciences", "engineering", "traditional learning"],
            "positive": "Deep and thorough learning, expertise through persistence",
            "negative": "Delayed education, struggles in early schooling",
        },
        "rahu": {
            "summary": "Education in technology, foreign institutions, research",
            "key_themes": ["foreign education", "technology", "research"],
            "positive": "Education abroad, cutting-edge knowledge, innovation",
            "negative": "Disrupted education, unconventional learning path",
        },
        "ketu": {
            "summary": "Education in occult, spirituality, ancient languages",
            "key_themes": ["esoteric studies", "sanskrit", "occult sciences"],
            "positive": "Mastery of ancient knowledge, intuitive learning",
            "negative": "Disinterest in formal education, dropout tendency",
        },
    }

    base = education_themes.get(
        p,
        {
            "summary": "Educational patterns indicated",
            "key_themes": ["education", "learning"],
            "positive": "Good academic potential",
            "negative": "Challenges in formal education",
        },
    )

    specific = f"{p.title()} in {r.title()} in D24 ({dignity}). "
    if dignity == "exalted":
        specific += "Excellent educational achievements, scholarly recognition."
    elif dignity == "own_sign":
        specific += "Natural learning ability, good academic performance."
    elif dignity == "debilitated":
        specific += "Educational challenges, may need extra effort."
    else:
        specific += "Moderate educational prospects."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d27_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D27 (Bhamsha/Nakshatramsha) chart.

    D27 divides each sign into 27 parts (one per nakshatra).
    It reveals innate strengths, weaknesses, and inherent abilities.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    strength_themes = {
        "sun": {
            "summary": "Innate leadership ability, willpower strength",
            "key_themes": ["leadership", "willpower", "vitality"],
            "positive": "Natural authority, strong constitution, commanding presence",
            "negative": "Overconfidence, tendency to dominate",
        },
        "moon": {
            "summary": "Emotional intelligence, intuitive strength",
            "key_themes": ["emotional intelligence", "intuition", "adaptability"],
            "positive": "Deep empathy, strong intuition, emotional resilience",
            "negative": "Emotional vulnerability, mood dependency",
        },
        "mars": {
            "summary": "Physical courage, competitive strength",
            "key_themes": ["physical strength", "courage", "competitiveness"],
            "positive": "Exceptional physical endurance, fearlessness",
            "negative": "Uncontrolled aggression, recklessness",
        },
        "mercury": {
            "summary": "Intellectual sharpness, communication strength",
            "key_themes": ["intelligence", "communication", "analytical ability"],
            "positive": "Quick wit, versatile intelligence, articulate expression",
            "negative": "Nervous energy, indecisiveness, overthinking",
        },
        "jupiter": {
            "summary": "Wisdom, teaching ability, moral strength",
            "key_themes": ["wisdom", "teaching", "ethics", "judgment"],
            "positive": "Natural wisdom, strong moral compass, good judgment",
            "negative": "Over-confidence in opinions, preachiness",
        },
        "venus": {
            "summary": "Artistic talent, charm, relationship strength",
            "key_themes": ["artistic ability", "charm", "diplomacy"],
            "positive": "Natural beauty, artistic talent, social grace",
            "negative": "Over-reliance on charm, vanity",
        },
        "saturn": {
            "summary": "Endurance, patience, organizational strength",
            "key_themes": ["endurance", "patience", "discipline"],
            "positive": "Exceptional patience, organizational mastery, perseverance",
            "negative": "Rigidity, pessimism, slow to adapt",
        },
        "rahu": {
            "summary": "Innovation, ambition, unconventional strength",
            "key_themes": ["innovation", "ambition", "unconventional thinking"],
            "positive": "Breakthrough thinking, ambitious drive",
            "negative": "Obsessive ambition, deceptive tendencies",
        },
        "ketu": {
            "summary": "Spiritual insight, intuitive perception, detachment strength",
            "key_themes": ["spiritual insight", "detachment", "psychic ability"],
            "positive": "Deep spiritual perception, liberation tendency",
            "negative": "Disconnection from practical matters, confusion",
        },
    }

    base = strength_themes.get(
        p,
        {
            "summary": "Innate ability patterns indicated",
            "key_themes": ["strengths", "weaknesses"],
            "positive": "Inherent talents present",
            "negative": "Areas needing development",
        },
    )

    specific = f"{p.title()} in {r.title()} in D27 ({dignity}). "
    if dignity == "exalted":
        specific += "Peak expression of innate abilities, exceptional talent."
    elif dignity == "own_sign":
        specific += "Strong and reliable innate abilities."
    elif dignity == "debilitated":
        specific += "Innate weakness in this area, requires conscious effort."
    else:
        specific += "Moderate expression of inherent abilities."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d30_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D30 (Trimshamsha) chart.

    D30 divides each sign into 30 parts. It reveals misfortunes,
    evils, potential calamities, and karmic challenges.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    misfortune_themes = {
        "sun": {
            "summary": "Challenges from authority, government, and ego",
            "key_themes": ["authority conflicts", "health challenges", "ego issues"],
            "positive": "When strong: overcomes adversity through willpower",
            "negative": "When afflicted: government problems, loss of status",
        },
        "moon": {
            "summary": "Emotional suffering, mental health challenges",
            "key_themes": ["mental health", "emotional distress", "mother's suffering"],
            "positive": "When strong: emotional resilience, empathic healing",
            "negative": "When afflicted: depression, anxiety, mental instability",
        },
        "mars": {
            "summary": "Accidents, injuries, surgical interventions",
            "key_themes": ["accidents", "surgery", "violence", "fire"],
            "positive": "When strong: overcomes physical danger, surgical success",
            "negative": "When afflicted: injuries, burns, blood disorders",
        },
        "mercury": {
            "summary": "Nervous disorders, communication mishaps, fraud",
            "key_themes": ["nervous disorders", "fraud", "skin diseases"],
            "positive": "When strong: mental agility avoids problems",
            "negative": "When afflicted: skin diseases, nervous breakdowns, cheating",
        },
        "jupiter": {
            "summary": "Loss of faith, misguided beliefs, excess",
            "key_themes": ["loss of faith", "liver issues", "excess weight"],
            "positive": "When strong: wisdom prevents misfortunes",
            "negative": "When afflicted: liver disease, wrong guru, loss of values",
        },
        "venus": {
            "summary": "Relationship misfortune, reproductive issues",
            "key_themes": ["relationship failures", "reproductive issues", "addiction"],
            "positive": "When strong: transforms suffering through love",
            "negative": "When afflicted: STDs, addiction, marital destruction",
        },
        "saturn": {
            "summary": "Chronic illness, poverty, prolonged suffering",
            "key_themes": ["chronic disease", "poverty", "depression", "longevity issues"],
            "positive": "When strong: endures and transcends suffering",
            "negative": "When afflicted: chronic diseases, extreme poverty, isolation",
        },
        "rahu": {
            "summary": "Sudden calamities, poisoning, mysterious illnesses",
            "key_themes": ["sudden disasters", "poisoning", "phobias", "epidemics"],
            "positive": "When strong: escapes mysterious dangers",
            "negative": "When afflicted: inexplicable diseases, sudden losses",
        },
        "ketu": {
            "summary": "Spiritual crises, accidents, past-life karmic suffering",
            "key_themes": ["spiritual crisis", "past-life karma", "mysterious losses"],
            "positive": "When strong: spiritual transformation through suffering",
            "negative": "When afflicted: mysterious diseases, loss, spiritual darkness",
        },
    }

    base = misfortune_themes.get(
        p,
        {
            "summary": "Karmic challenge patterns indicated",
            "key_themes": ["misfortune", "karma"],
            "positive": "Ability to overcome challenges",
            "negative": "Potential for difficulties",
        },
    )

    specific = f"{p.title()} in {r.title()} in D30 ({dignity}). "
    if dignity == "exalted":
        specific += "Protection from this type of misfortune, karmic shield."
    elif dignity == "own_sign":
        specific += "Manageable challenges, good coping mechanisms."
    elif dignity == "debilitated":
        specific += "Vulnerable to this type of misfortune, remedies recommended."
    else:
        specific += "Moderate susceptibility to challenges."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def interpret_d60_position(planet: str, rashi_name: str) -> dict[str, Any]:
    """Interpret a planet's position in the D60 (Shashtiamsha) chart.

    D60 divides each sign into 60 parts (0.5 degrees each).
    It is considered the most important varga chart, revealing
    past-life karma and the deepest layer of destiny.

    Args:
        planet: Planet name (lowercase)
        rashi_name: Rashi/sign name (lowercase)

    Returns:
        Dictionary with summary, key_themes, positive, negative, specific_effects.
    """
    p = planet.lower()
    r = rashi_name.lower()

    if r not in RASHI_NAMES_LOWER:
        return {"planet": p, "rashi": r, "found": False}

    dignity = _get_dignity(p, r)

    pastlife_themes = {
        "sun": {
            "summary": "Past-life king or authority figure, soul's dharmic karmic seed",
            "key_themes": ["past-life authority", "soul purpose karma", "leadership karma"],
            "positive": "Past-life merit of leadership, strong dharmic foundation",
            "negative": "Past-life abuse of power, karmic debts from authority",
        },
        "moon": {
            "summary": "Past-life emotional bonds, karmic emotional inheritance",
            "key_themes": ["emotional karma", "past-life mother", "karmic relationships"],
            "positive": "Past-life emotional wisdom, carried-over intuition",
            "negative": "Past-life emotional trauma, unresolved grief",
        },
        "mars": {
            "summary": "Past-life warrior, karmic courage or violence",
            "key_themes": ["warrior karma", "past-life battles", "courage inheritance"],
            "positive": "Past-life courage and valor, protector karma",
            "negative": "Past-life violence, karmic debts from aggression",
        },
        "mercury": {
            "summary": "Past-life scholar, karmic intellectual inheritance",
            "key_themes": ["scholar karma", "past-life learning", "knowledge inheritance"],
            "positive": "Past-life wisdom, carried-over intellectual abilities",
            "negative": "Past-life deception, karmic speech debts",
        },
        "jupiter": {
            "summary": "Past-life guru or priest, dharmic karmic merit",
            "key_themes": ["guru karma", "dharmic merit", "past-life teaching"],
            "positive": "Tremendous past-life dharmic merit, guru blessings",
            "negative": "Past-life misuse of spiritual authority",
        },
        "venus": {
            "summary": "Past-life lover or artist, karmic relationship patterns",
            "key_themes": ["love karma", "artistic inheritance", "past-life spouse"],
            "positive": "Past-life artistic mastery, soul-mate connection",
            "negative": "Past-life relationship debts, karmic attraction patterns",
        },
        "saturn": {
            "summary": "Past-life servant or ascetic, karmic duty inheritance",
            "key_themes": ["duty karma", "service inheritance", "past-life austerity"],
            "positive": "Past-life discipline, karmic endurance, service merit",
            "negative": "Past-life suffering, heavy karmic burden",
        },
        "rahu": {
            "summary": "Past-life intense desires, unfulfilled ambitions",
            "key_themes": ["desire karma", "unfulfilled past-life ambitions", "obsession"],
            "positive": "Past-life experience driving current ambition",
            "negative": "Compulsive patterns from past-life obsessions",
        },
        "ketu": {
            "summary": "Past-life spiritual attainment, liberation karma",
            "key_themes": ["spiritual inheritance", "past-life moksha attempts", "detachment"],
            "positive": "Past-life spiritual mastery, natural detachment",
            "negative": "Past-life spiritual confusion, incomplete liberation",
        },
    }

    base = pastlife_themes.get(
        p,
        {
            "summary": "Past-life karmic patterns indicated",
            "key_themes": ["past-life karma", "destiny"],
            "positive": "Positive past-life merit",
            "negative": "Karmic debts from past lives",
        },
    )

    specific = f"{p.title()} in {r.title()} in D60 ({dignity}). "
    if dignity == "exalted":
        specific += "Extremely positive past-life karma, strong destined blessings."
    elif dignity == "own_sign":
        specific += "Good past-life karma, stable karmic foundation."
    elif dignity == "debilitated":
        specific += "Challenging past-life karma, significant karmic debts."
    else:
        specific += "Mixed past-life karma, some debts and some merits."

    return {
        "planet": p,
        "rashi": r,
        "found": True,
        "summary": base["summary"],
        "key_themes": base["key_themes"],
        "positive": base["positive"],
        "negative": base["negative"],
        "specific_effects": specific,
        "dignity": dignity,
    }


def _get_house_meanings(division_key: str) -> dict[str, Any]:
    """Get house meanings for a divisional chart."""
    interp = _get_interp()
    return interp.get(division_key, {}).get("house_meanings", {})


def _get_special_rules(division_key: str) -> list[dict[str, Any]]:
    """Get special rules for a divisional chart."""
    interp = _get_interp()
    return interp.get(division_key, {}).get("special_rules", [])


def interpret_d9_chart(d9_chart: DivisionalChart) -> dict[str, Any]:
    """Interpret a complete D9 (Navamsha) chart.

    Args:
        d9_chart: DivisionalChart from get_divisional_chart(planets, 9)

    Returns:
        Dictionary with planet interpretations, house meanings, and special rules.
    """
    planet_interpretations: dict[str, Any] = {}

    for planet_name, pos in d9_chart.get("positions", {}).items():
        rashi_name = pos.get("rashi_name", "").lower()
        if rashi_name:
            planet_interpretations[planet_name] = interpret_d9_position(planet_name, rashi_name)

    house_meanings = _get_house_meanings("d9_navamsha")
    special_rules = _get_special_rules("d9_navamsha")

    return {
        "division": 9,
        "division_name": "Navamsha",
        "planets": planet_interpretations,
        "house_meanings": house_meanings,
        "special_rules": special_rules,
    }


def interpret_d10_chart(d10_chart: DivisionalChart) -> dict[str, Any]:
    """Interpret a complete D10 (Dashamsha) chart.

    Args:
        d10_chart: DivisionalChart from get_divisional_chart(planets, 10)

    Returns:
        Dictionary with planet interpretations, house meanings, and special rules.
    """
    planet_interpretations: dict[str, Any] = {}

    for planet_name, pos in d10_chart.get("positions", {}).items():
        rashi_name = pos.get("rashi_name", "").lower()
        if rashi_name:
            planet_interpretations[planet_name] = interpret_d10_position(planet_name, rashi_name)

    house_meanings = _get_house_meanings("d10_dashamsha")
    special_rules = _get_special_rules("d10_dashamsha")

    return {
        "division": 10,
        "division_name": "Dashamsha",
        "planets": planet_interpretations,
        "house_meanings": house_meanings,
        "special_rules": special_rules,
    }


def _interpret_generic_chart(
    chart: DivisionalChart,
    division: int,
    division_name: str,
    interpret_fn,
) -> dict[str, Any]:
    """Interpret a complete divisional chart using the given interpretation function.

    Args:
        chart: DivisionalChart from get_divisional_chart
        division: Division number (e.g., 2, 3, 4, ...)
        division_name: Human-readable name (e.g., "Hora", "Drekkana")
        interpret_fn: Function to call for each planet position

    Returns:
        Dictionary with planet interpretations.
    """
    planet_interpretations: dict[str, Any] = {}

    for planet_name, pos in chart.get("positions", {}).items():
        rashi_name = pos.get("rashi_name", "").lower()
        if rashi_name:
            planet_interpretations[planet_name] = interpret_fn(planet_name, rashi_name)

    return {
        "division": division,
        "division_name": division_name,
        "planets": planet_interpretations,
    }


def get_divisional_analysis(planet_longitudes: dict[str, float]) -> dict[str, Any]:
    """Full divisional chart analysis from planet longitudes.

    Analyzes all major divisional charts: D2, D3, D4, D7, D9, D10,
    D12, D16, D20, D24, D27, D30, D60.

    Args:
        planet_longitudes: Dict mapping planet name -> longitude (0-360)

    Returns:
        Dictionary with interpretations for all divisional charts.
    """
    d9_chart = get_divisional_chart(planet_longitudes, 9)
    d10_chart = get_divisional_chart(planet_longitudes, 10)

    result: dict[str, Any] = {
        "d9_navamsha": interpret_d9_chart(d9_chart),
        "d10_dashamsha": interpret_d10_chart(d10_chart),
    }

    # Add all other divisional chart interpretations
    divisions = {
        2: ("d2_hora", "Hora", interpret_d2_position),
        3: ("d3_drekkana", "Drekkana", interpret_d3_position),
        4: ("d4_chaturthamsha", "Chaturthamsha", interpret_d4_position),
        7: ("d7_saptamsha", "Saptamsha", interpret_d7_position),
        12: ("d12_dwadashamsha", "Dwadashamsha", interpret_d12_position),
        16: ("d16_shodashamsha", "Shodashamsha", interpret_d16_position),
        20: ("d20_vimshamsha", "Vimshamsha", interpret_d20_position),
        24: ("d24_chaturvimshamsha", "Chaturvimshamsha", interpret_d24_position),
        27: ("d27_bhamsha", "Bhamsha", interpret_d27_position),
        30: ("d30_trimshamsha", "Trimshamsha", interpret_d30_position),
        60: ("d60_shashtiamsha", "Shashtiamsha", interpret_d60_position),
    }

    for div_num, (key, name, fn) in divisions.items():
        chart = get_divisional_chart(planet_longitudes, div_num)
        result[key] = _interpret_generic_chart(chart, div_num, name, fn)

    return result
