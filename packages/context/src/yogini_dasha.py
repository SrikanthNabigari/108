"""Yogini Dasha calculations module for 108 Vedic Astrology app.

This module implements the Yogini Dasha system, an ancient 36-year cycle system
based on 8 Yoginis (female deities). Each Yogini rules a specific duration and
is associated with a planetary lord.

The Yogini Dasha system consists of 8 Yoginis totaling 36 years:
- Mangala: 1 year (Moon)
- Pingala: 2 years (Sun)
- Dhanya: 3 years (Jupiter)
- Bhramari: 4 years (Mars)
- Bhadrika: 5 years (Mercury)
- Ulka: 6 years (Saturn)
- Siddha: 7 years (Venus)
- Sankata: 8 years (Rahu)

The starting Yogini is determined by the Moon's nakshatra and pada at birth.
"""

from datetime import datetime, timedelta

from packages.core.src.constants import NAKSHATRA_SPAN, Planet, YoginiName
from packages.core.src.models import YoginiDashaPeriod

# Yogini data: (YoginiName, Planet lord, duration_years)
YOGINI_DATA = [
    (YoginiName.MANGALA, Planet.MOON, 1),
    (YoginiName.PINGALA, Planet.SUN, 2),
    (YoginiName.DHANYA, Planet.JUPITER, 3),
    (YoginiName.BHRAMARI, Planet.MARS, 4),
    (YoginiName.BHADRIKA, Planet.MERCURY, 5),
    (YoginiName.ULKA, Planet.SATURN, 6),
    (YoginiName.SIDDHA, Planet.VENUS, 7),
    (YoginiName.SANKATA, Planet.RAHU, 8),
]

TOTAL_CYCLE = 36  # years

# Full interpretation data for each Yogini dasha period
YOGINI_EFFECTS: dict[str, dict] = {
    "mangala": {
        "planet": "moon",
        "years": 1,
        "general": "New beginnings, emotional changes, short travels, fresh starts",
        "positive": [
            "Fresh starts and new opportunities",
            "Emotional clarity and intuition heightened",
            "Good for Moon-related activities (travel, public interaction)",
            "Quick results from efforts",
        ],
        "negative": [
            "Restlessness and emotional turbulence",
            "Short-lived results, lack of permanence",
            "Mood swings and mental instability",
            "Difficulty in long-term planning",
        ],
        "health": "Watch mental health, hydration, sleep patterns, cold-related ailments",
        "career": "Quick changes, new connections, not ideal for long-term planning",
        "relationships": "New emotional bonds, nurturing energy, mother figures prominent",
        "spiritual": "Good for meditation, developing intuition, connecting with inner self",
    },
    "pingala": {
        "planet": "sun",
        "years": 2,
        "general": "Authority, recognition, vitality, leadership opportunities arise",
        "positive": [
            "Government and authority figure favor",
            "Career recognition and promotion",
            "Health vitality increases",
            "Father's support and guidance",
        ],
        "negative": [
            "Ego conflicts with superiors",
            "Eye-related health issues",
            "Excessive pride leading to downfall",
            "Burnout from overwork",
        ],
        "health": "Heart health, eyes, bones, vitality; avoid excessive heat exposure",
        "career": "Leadership roles, government work, authority positions favored",
        "relationships": "Dominant energy in relationships, need for respect and recognition",
        "spiritual": "Self-realization work, connecting with inner light, solar meditations",
    },
    "dhanya": {
        "planet": "jupiter",
        "years": 3,
        "general": "Wisdom, prosperity, children's welfare, spiritual growth, expansion",
        "positive": [
            "Wealth increase and financial stability",
            "Children's welfare and educational success",
            "Spiritual growth and guru's blessings",
            "Marriage prospects improve for eligible",
        ],
        "negative": [
            "Over-expansion and overcommitment",
            "Liver and weight-related health issues",
            "False promises from others",
            "Religious or philosophical conflicts",
        ],
        "health": "Liver, fat metabolism, obesity; maintain moderate diet and exercise",
        "career": "Teaching, counseling, law, finance, religious work favored",
        "relationships": "Harmonious family life, wisdom in partnerships, guru-disciple bonds",
        "spiritual": "Peak period for spiritual practices, pilgrimage, mantra initiation",
    },
    "bhramari": {
        "planet": "mars",
        "years": 4,
        "general": "Energy, courage, competition, property matters, siblings",
        "positive": [
            "Victory in competition and legal matters",
            "Property acquisition or improvement",
            "Courage and initiative increase",
            "Athletic and technical achievements",
        ],
        "negative": [
            "Accident risk and injury potential",
            "Anger management challenges",
            "Blood-related health issues",
            "Conflicts with siblings or neighbors",
        ],
        "health": "Blood pressure, accidents, surgery risk, inflammation; stay active safely",
        "career": "Military, engineering, sports, surgery, real estate favored",
        "relationships": "Passionate but potentially combative; channel energy constructively",
        "spiritual": "Kundalini practices, Hanuman worship, building spiritual discipline",
    },
    "bhadrika": {
        "planet": "mercury",
        "years": 5,
        "general": "Intelligence, communication, business, education, writing",
        "positive": [
            "Business success and trade profits",
            "Communication skills at peak",
            "Educational achievements and certificates",
            "Writing, publishing, media success",
        ],
        "negative": [
            "Nervous disorders and anxiety",
            "Communication mishaps and misunderstandings",
            "Skin problems and allergies",
            "Mental restlessness and overthinking",
        ],
        "health": "Nervous system, skin, respiratory; manage stress and anxiety",
        "career": "Commerce, writing, teaching, IT, accounting, communication roles",
        "relationships": "Intellectual connections, friendships, networking opportunities",
        "spiritual": "Study of scriptures, mantra recitation, intellectual spiritual inquiry",
    },
    "ulka": {
        "planet": "saturn",
        "years": 6,
        "general": "Discipline, karma, delays, hard work, longevity, structure",
        "positive": [
            "Steady progress through discipline",
            "Property gains through patience",
            "Old debts cleared, karma resolved",
            "Mastery through persistent effort",
        ],
        "negative": [
            "Delays in all matters",
            "Chronic health issues surface",
            "Depression and isolation",
            "Career obstacles and slow promotions",
        ],
        "health": "Bones, joints, chronic conditions, teeth; regular health maintenance",
        "career": "Agriculture, mining, labor, judiciary, administration, oil industry",
        "relationships": "Karmic relationships, older partners, duty-bound connections",
        "spiritual": "Deep meditation, austerity, service to elderly, karma yoga",
    },
    "siddha": {
        "planet": "venus",
        "years": 7,
        "general": "Love, marriage, luxury, arts, finances, sensual pleasures",
        "positive": [
            "Marriage and romantic fulfillment",
            "Financial gains and luxury acquisitions",
            "Artistic and creative achievements",
            "Beauty, fashion, entertainment success",
        ],
        "negative": [
            "Excessive indulgence and extravagance",
            "Relationship complications and affairs",
            "Reproductive health issues",
            "Scandal risk from pleasure-seeking",
        ],
        "health": "Reproductive system, kidneys, diabetes; maintain balanced lifestyle",
        "career": "Arts, entertainment, fashion, hospitality, finance, jewellery",
        "relationships": "Peak romance period, marriage, partnerships, social harmony",
        "spiritual": "Bhakti yoga, devotional practices, beauty as spiritual path",
    },
    "sankata": {
        "planet": "rahu",
        "years": 8,
        "general": "Unconventional paths, foreign connections, technology, obsession",
        "positive": [
            "Foreign opportunities and travel",
            "Technology and innovation success",
            "Unconventional gains and breakthroughs",
            "Political and social climbing",
        ],
        "negative": [
            "Deception and betrayal risk",
            "Obsessive behavior and addiction",
            "Mysterious ailments and misdiagnosis",
            "Confusion, scandal, and reputation risk",
        ],
        "health": "Mysterious ailments, poison risk, mental health; seek proper diagnosis",
        "career": "Technology, foreign trade, diplomacy, research, occult sciences",
        "relationships": "Unusual connections, cross-cultural relationships, deception risk",
        "spiritual": "Tantric practices, past-life healing, breaking karmic patterns",
    },
}


def get_starting_yogini(nakshatra_num: int, pada: int) -> int:
    """Calculate the starting Yogini index based on Moon's nakshatra and pada.

    Formula: (nakshatra_pada_number + 3) % 8
    where nakshatra_pada_number = (nakshatra_num - 1) * 4 + pada

    Args:
        nakshatra_num: Nakshatra number (1-27)
        pada: Pada number (1-4)

    Returns:
        Index into YOGINI_DATA (0-7)

    Example:
        >>> get_starting_yogini(1, 1)  # Ashwini pada 1
        4  # Bhadrika
    """
    if not (1 <= nakshatra_num <= 27):
        raise ValueError(f"Nakshatra number must be 1-27, got {nakshatra_num}")
    if not (1 <= pada <= 4):
        raise ValueError(f"Pada must be 1-4, got {pada}")

    # Calculate the nakshatra pada number (1-108)
    nakshatra_pada_number = (nakshatra_num - 1) * 4 + pada

    # Apply formula
    yogini_index = (nakshatra_pada_number + 3) % 8

    return yogini_index


def get_yogini_balance_at_birth(nakshatra_num: int, pada: int, degree_in_nakshatra: float) -> dict:
    """Calculate how much of the starting yogini's period has elapsed at birth.

    Each nakshatra spans 13.333° (13°20'). The proportion of the nakshatra
    traversed determines how much of the starting yogini's period has elapsed.

    Args:
        nakshatra_num: Nakshatra number (1-27)
        pada: Pada number (1-4)
        degree_in_nakshatra: Degrees traversed in current nakshatra (0-13.333)

    Returns:
        Dictionary with:
            - yogini_index: int (0-7)
            - yogini: YoginiName
            - lord: Planet
            - total_years: int
            - elapsed_years: float
            - remaining_years: float

    Example:
        >>> balance = get_yogini_balance_at_birth(25, 3, 10.0)
        >>> balance['yogini']
        'sankata'
    """
    if not (0 <= degree_in_nakshatra < NAKSHATRA_SPAN):
        raise ValueError(
            f"Degree in nakshatra must be 0-{NAKSHATRA_SPAN}, got {degree_in_nakshatra}"
        )

    yogini_index = get_starting_yogini(nakshatra_num, pada)
    yogini_name, planet_lord, total_years = YOGINI_DATA[yogini_index]

    # Calculate proportion of nakshatra traversed
    proportion_traversed = degree_in_nakshatra / NAKSHATRA_SPAN

    # Calculate elapsed and remaining time
    elapsed_years = total_years * proportion_traversed
    remaining_years = total_years * (1 - proportion_traversed)

    return {
        "yogini_index": yogini_index,
        "yogini": yogini_name,
        "lord": planet_lord,
        "total_years": total_years,
        "elapsed_years": elapsed_years,
        "remaining_years": remaining_years,
    }


def calculate_yogini_sequence(
    birth_dt: datetime,
    nakshatra_num: int,
    pada: int,
    degree_in_nakshatra: float,
    cycles: int = 3,
) -> list[YoginiDashaPeriod]:
    """Generate the full sequence of Yogini dasha periods.

    Args:
        birth_dt: Birth datetime
        nakshatra_num: Moon's nakshatra number (1-27)
        pada: Moon's pada (1-4)
        degree_in_nakshatra: Degrees in nakshatra (0-13.333)
        cycles: Number of complete cycles to generate (default 3 = 108 years)

    Returns:
        List of YoginiDashaPeriod objects

    Example:
        >>> from datetime import datetime, UTC
        >>> periods = calculate_yogini_sequence(
        ...     datetime(1992, 12, 3, tzinfo=UTC), 25, 3, 10.0
        ... )
        >>> len(periods)
        24  # 8 yoginis x 3 cycles
    """
    balance = get_yogini_balance_at_birth(nakshatra_num, pada, degree_in_nakshatra)
    starting_index = balance["yogini_index"]
    remaining_years = balance["remaining_years"]

    periods: list[YoginiDashaPeriod] = []
    current_date = birth_dt

    # First period (partial, based on balance)
    yogini_name, planet_lord, total_years = YOGINI_DATA[starting_index]
    days_in_period = int(remaining_years * 365.25)
    end_date = current_date + timedelta(days=days_in_period)

    periods.append(
        YoginiDashaPeriod(
            yogini=yogini_name,
            planet_lord=planet_lord,
            start_date=current_date,
            end_date=end_date,
            duration_years=total_years,
        )
    )
    current_date = end_date

    # Calculate total periods needed (excluding the first partial period)
    total_periods = cycles * 8 - 1

    # Generate subsequent periods
    for i in range(total_periods):
        # Cycle through yoginis starting from the next one after starting_index
        yogini_index = (starting_index + 1 + i) % 8
        yogini_name, planet_lord, duration_years = YOGINI_DATA[yogini_index]

        days_in_period = int(duration_years * 365.25)
        end_date = current_date + timedelta(days=days_in_period)

        periods.append(
            YoginiDashaPeriod(
                yogini=yogini_name,
                planet_lord=planet_lord,
                start_date=current_date,
                end_date=end_date,
                duration_years=duration_years,
            )
        )
        current_date = end_date

    return periods


def get_current_yogini_dasha(
    birth_dt: datetime,
    nakshatra_num: int,
    pada: int,
    degree_in_nakshatra: float,
    query_dt: datetime | None = None,
) -> dict:
    """Get the current Yogini maha-dasha at a specific date.

    Args:
        birth_dt: Birth datetime
        nakshatra_num: Moon's nakshatra number (1-27)
        pada: Moon's pada (1-4)
        degree_in_nakshatra: Degrees in nakshatra (0-13.333)
        query_dt: Query datetime (defaults to now)

    Returns:
        Dictionary with:
            - yogini: YoginiName
            - lord: Planet
            - start_date: datetime
            - end_date: datetime
            - remaining_days: int

    Example:
        >>> from datetime import datetime, UTC
        >>> current = get_current_yogini_dasha(
        ...     datetime(1992, 12, 3, tzinfo=UTC),
        ...     25, 3, 10.0,
        ...     query_dt=datetime(2025, 1, 1, tzinfo=UTC)
        ... )
        >>> current['yogini']
        'ulka'
    """
    if query_dt is None:
        query_dt = datetime.now()

    # Normalize query_dt to naive for comparison with period dates
    if query_dt.tzinfo is not None:
        query_dt = query_dt.replace(tzinfo=None)

    # Generate enough cycles to cover the query date
    # Assume max lifespan of 120 years (4 cycles)
    periods = calculate_yogini_sequence(
        birth_dt, nakshatra_num, pada, degree_in_nakshatra, cycles=4
    )

    # Find the period that contains the query date
    for period in periods:
        start = (
            period.start_date.replace(tzinfo=None)
            if period.start_date.tzinfo
            else period.start_date
        )
        end = period.end_date.replace(tzinfo=None) if period.end_date.tzinfo else period.end_date

        if start <= query_dt < end:
            remaining_days = (end - query_dt).days
            return {
                "yogini": period.yogini,
                "lord": period.planet_lord,
                "start_date": period.start_date,
                "end_date": period.end_date,
                "remaining_days": remaining_days,
            }

    # If query_dt is beyond all calculated periods, return the last period
    last_period = periods[-1]
    last_end = (
        last_period.end_date.replace(tzinfo=None)
        if last_period.end_date.tzinfo
        else last_period.end_date
    )
    remaining_days = max(0, (last_end - query_dt).days)
    return {
        "yogini": last_period.yogini,
        "lord": last_period.planet_lord,
        "start_date": last_period.start_date,
        "end_date": last_period.end_date,
        "remaining_days": remaining_days,
    }


def get_yogini_antardasha(maha: YoginiDashaPeriod) -> list[dict]:
    """Subdivide a maha-dasha into 8 antardashas proportionally.

    The antardasha sequence starts from the maha-dasha yogini itself.
    Each antardasha duration = (antardasha_yogini_years / TOTAL_CYCLE) * maha_duration_days

    Args:
        maha: YoginiDashaPeriod for the maha-dasha

    Returns:
        List of dicts with yogini, lord, start_date, end_date

    Example:
        >>> from datetime import datetime, UTC
        >>> maha = YoginiDashaPeriod(
        ...     yogini=YoginiName.BHADRIKA,
        ...     planet_lord=Planet.MERCURY,
        ...     start_date=datetime(2020, 1, 1, tzinfo=UTC),
        ...     end_date=datetime(2025, 1, 1, tzinfo=UTC),
        ...     duration_years=5
        ... )
        >>> antardashas = get_yogini_antardasha(maha)
        >>> len(antardashas)
        8
    """
    # Find the starting index for this maha-dasha's yogini
    starting_index = None
    for i, (yogini_name, _, _) in enumerate(YOGINI_DATA):
        if yogini_name == maha.yogini:
            starting_index = i
            break

    if starting_index is None:
        raise ValueError(f"Invalid yogini name: {maha.yogini}")

    # Calculate total duration in days
    maha_duration_days = (maha.end_date - maha.start_date).days

    antardashas = []
    current_date = maha.start_date

    # Generate 8 antardashas starting from the maha yogini
    for i in range(8):
        yogini_index = (starting_index + i) % 8
        yogini_name, planet_lord, yogini_years = YOGINI_DATA[yogini_index]

        # Proportional duration
        antardasha_days = int((yogini_years / TOTAL_CYCLE) * maha_duration_days)

        # Ensure we don't exceed the maha end date
        end_date = current_date + timedelta(days=antardasha_days)
        if end_date > maha.end_date:
            end_date = maha.end_date

        antardashas.append(
            {
                "yogini": yogini_name,
                "lord": planet_lord,
                "start_date": current_date,
                "end_date": end_date,
            }
        )

        current_date = end_date

        # Stop if we've reached the maha end date
        if current_date >= maha.end_date:
            break

    return antardashas


def get_yogini_pratyantardasha(antardasha: dict) -> list[dict]:
    """Subdivide an antardasha into 8 pratyantardashas (3rd level).

    The pratyantardasha sequence starts from the antardasha yogini itself.
    Duration formula: (pratyantardasha_years / TOTAL_CYCLE) * antardasha_days

    Args:
        antardasha: Dict with yogini, lord, start_date, end_date (from get_yogini_antardasha)

    Returns:
        List of 8 dicts with yogini, lord, start_date, end_date

    Example:
        >>> ad = {"yogini": YoginiName.BHADRIKA, "lord": Planet.MERCURY,
        ...       "start_date": datetime(2020,1,1), "end_date": datetime(2020,7,1)}
        >>> pads = get_yogini_pratyantardasha(ad)
        >>> len(pads)
        8
    """
    ad_yogini = antardasha["yogini"]
    ad_start = antardasha["start_date"]
    ad_end = antardasha["end_date"]

    # Find starting index
    starting_index = None
    for i, (yogini_name, _, _) in enumerate(YOGINI_DATA):
        if yogini_name == ad_yogini:
            starting_index = i
            break

    if starting_index is None:
        raise ValueError(f"Invalid yogini name: {ad_yogini}")

    ad_duration_days = (ad_end - ad_start).days

    pratyantardashas = []
    current_date = ad_start

    for i in range(8):
        yogini_index = (starting_index + i) % 8
        yogini_name, planet_lord, yogini_years = YOGINI_DATA[yogini_index]

        pad_days = int((yogini_years / TOTAL_CYCLE) * ad_duration_days)
        end_date = current_date + timedelta(days=pad_days)
        if end_date > ad_end:
            end_date = ad_end

        pratyantardashas.append(
            {
                "yogini": yogini_name,
                "lord": planet_lord,
                "start_date": current_date,
                "end_date": end_date,
            }
        )

        current_date = end_date
        if current_date >= ad_end:
            break

    return pratyantardashas


def get_yogini_effects(yogini_name: str) -> dict:
    """Get interpretation effects for a given Yogini dasha period.

    Args:
        yogini_name: Yogini name (e.g., "mangala", "pingala")

    Returns:
        Dictionary with general, positive, negative, health, career, relationships,
        spiritual fields. Returns empty dict if yogini not found.

    Example:
        >>> effects = get_yogini_effects("mangala")
        >>> effects["planet"]
        'moon'
    """
    return YOGINI_EFFECTS.get(yogini_name.lower(), {})
