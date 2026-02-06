"""Ashtottari Dasha calculations module for 108 Vedic Astrology app.

This module implements the Ashtottari Dasha system, a 108-year planetary period
system used when Rahu is in kendra or trikona from the Lagna lord.

The Ashtottari Dasha uses 8 planets (no Ketu) totaling 108 years:
- Sun: 6 years
- Moon: 15 years
- Mars: 8 years
- Mercury: 17 years
- Saturn: 10 years
- Jupiter: 19 years
- Rahu: 12 years
- Venus: 21 years

Sequence: Sun -> Moon -> Mars -> Mercury -> Saturn -> Jupiter -> Rahu -> Venus

The starting lord is determined by Moon's nakshatra at birth using a specific
mapping of nakshatras to lords.
"""

from datetime import datetime, timedelta

from packages.core.src.constants import NAKSHATRA_SPAN

# Ashtottari sequence with years: (lord, years)
ASHTOTTARI_DATA: list[tuple[str, int]] = [
    ("sun", 6),
    ("moon", 15),
    ("mars", 8),
    ("mercury", 17),
    ("saturn", 10),
    ("jupiter", 19),
    ("rahu", 12),
    ("venus", 21),
]

TOTAL_CYCLE = 108  # years

# Nakshatra-to-starting-lord mapping
# Nakshatra numbers (1-indexed) mapped to starting lord
NAKSHATRA_TO_LORD: dict[str, str] = {
    "ardra": "sun",  # 6
    "punarvasu": "sun",  # 7
    "pushya": "moon",  # 8
    "ashlesha": "moon",  # 9
    "magha": "mars",  # 10
    "purva_phalguni": "mars",  # 11
    "uttara_phalguni": "mercury",  # 12
    "hasta": "mercury",  # 13
    "chitra": "saturn",  # 14
    "swati": "saturn",  # 15
    "vishakha": "jupiter",  # 16
    "anuradha": "jupiter",  # 17
    "jyeshtha": "rahu",  # 18
    "moola": "rahu",  # 19
    "purva_ashadha": "venus",  # 20
    "uttara_ashadha": "venus",  # 21
}

# Also provide a mapping by nakshatra number for convenience
NAKSHATRA_NUM_TO_LORD: dict[int, str] = {
    6: "sun",  # Ardra
    7: "sun",  # Punarvasu
    8: "moon",  # Pushya
    9: "moon",  # Ashlesha
    10: "mars",  # Magha
    11: "mars",  # Purva Phalguni
    12: "mercury",  # Uttara Phalguni
    13: "mercury",  # Hasta
    14: "saturn",  # Chitra
    15: "saturn",  # Swati
    16: "jupiter",  # Vishakha
    17: "jupiter",  # Anuradha
    18: "rahu",  # Jyeshtha
    19: "rahu",  # Moola
    20: "venus",  # Purva Ashadha
    21: "venus",  # Uttara Ashadha
}

# For nakshatras outside 6-21 range, use the cyclic mapping
# The 16 nakshatras repeat in pairs over the 8 lords
# Nakshatras 1-5 and 22-27 map cyclically
_ALL_NAKSHATRA_TO_LORD: dict[int, str] = {}
_lord_sequence = ["sun", "moon", "mars", "mercury", "saturn", "jupiter", "rahu", "venus"]
for _i in range(27):
    # Each pair of nakshatras maps to one lord, starting from Ardra (6)
    # Offset so Ardra (index 5, 0-based) maps to Sun
    _pair_index = ((_i - 5) % 16) // 2
    _ALL_NAKSHATRA_TO_LORD[_i + 1] = _lord_sequence[_pair_index % 8]

# Override with the canonical mapping for nakshatras 6-21
_ALL_NAKSHATRA_TO_LORD.update(NAKSHATRA_NUM_TO_LORD)

# Kendra houses (1, 4, 7, 10) and Trikona houses (1, 5, 9)
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}


def _get_lord_index(lord: str) -> int:
    """Get the index of a lord in the Ashtottari sequence.

    Args:
        lord: Planet name (e.g., "sun", "moon")

    Returns:
        Index (0-7) in ASHTOTTARI_DATA

    Raises:
        ValueError: If lord is not in the Ashtottari sequence
    """
    for i, (name, _) in enumerate(ASHTOTTARI_DATA):
        if name == lord:
            return i
    raise ValueError(
        f"Invalid Ashtottari lord: {lord}. Must be one of: {[d[0] for d in ASHTOTTARI_DATA]}"
    )


def is_ashtottari_applicable(rahu_house: int, lagna_lord_house: int) -> bool:
    """Check if Ashtottari Dasha is applicable based on Rahu's position.

    Ashtottari Dasha is applicable when Rahu is in a kendra or trikona house
    from the house containing the Lagna lord.

    Args:
        rahu_house: House number where Rahu is placed (1-12)
        lagna_lord_house: House number where the Lagna lord is placed (1-12)

    Returns:
        True if Ashtottari is applicable, False otherwise

    Raises:
        ValueError: If house numbers are not 1-12

    Example:
        >>> is_ashtottari_applicable(1, 1)  # Rahu in same house as Lagna lord
        True
        >>> is_ashtottari_applicable(4, 1)  # Rahu 4th from Lagna lord (kendra)
        True
        >>> is_ashtottari_applicable(6, 1)  # Rahu 6th from Lagna lord (neither)
        False
    """
    if not (1 <= rahu_house <= 12):
        raise ValueError(f"Rahu house must be 1-12, got {rahu_house}")
    if not (1 <= lagna_lord_house <= 12):
        raise ValueError(f"Lagna lord house must be 1-12, got {lagna_lord_house}")

    # Calculate the house distance from lagna lord to Rahu
    distance = ((rahu_house - lagna_lord_house) % 12) + 1

    # Check if distance corresponds to kendra or trikona
    return distance in KENDRA_HOUSES or distance in TRIKONA_HOUSES


def get_starting_lord(moon_nakshatra: int) -> str:
    """Get the starting Ashtottari lord from Moon's nakshatra.

    Args:
        moon_nakshatra: Moon's nakshatra number (1-27)

    Returns:
        Starting lord name (e.g., "sun", "moon")

    Raises:
        ValueError: If nakshatra number is not 1-27

    Example:
        >>> get_starting_lord(6)  # Ardra
        'sun'
        >>> get_starting_lord(8)  # Pushya
        'moon'
    """
    if not (1 <= moon_nakshatra <= 27):
        raise ValueError(f"Nakshatra number must be 1-27, got {moon_nakshatra}")

    return _ALL_NAKSHATRA_TO_LORD[moon_nakshatra]


def calculate_ashtottari_balance(moon_nakshatra: int, degree_in_nakshatra: float) -> dict:
    """Calculate remaining balance of the first dasha period at birth.

    The proportion of the nakshatra traversed determines how much of
    the starting lord's period has already elapsed.

    Args:
        moon_nakshatra: Moon's nakshatra number (1-27)
        degree_in_nakshatra: Degrees traversed in current nakshatra (0 to ~13.333)

    Returns:
        Dictionary with:
            - lord: Starting lord name
            - lord_index: Index in ASHTOTTARI_DATA
            - total_years: Full dasha years for this lord
            - elapsed_years: Years already elapsed at birth
            - remaining_years: Years remaining from birth

    Raises:
        ValueError: If inputs are out of range

    Example:
        >>> balance = calculate_ashtottari_balance(8, 6.666)  # Pushya, halfway
        >>> balance['lord']
        'moon'
        >>> abs(balance['remaining_years'] - 7.5) < 0.1
        True
    """
    if not (1 <= moon_nakshatra <= 27):
        raise ValueError(f"Nakshatra number must be 1-27, got {moon_nakshatra}")
    if not (0 <= degree_in_nakshatra < NAKSHATRA_SPAN + 0.001):
        raise ValueError(
            f"Degree in nakshatra must be 0-{NAKSHATRA_SPAN}, got {degree_in_nakshatra}"
        )

    lord = get_starting_lord(moon_nakshatra)
    lord_index = _get_lord_index(lord)
    total_years = ASHTOTTARI_DATA[lord_index][1]

    # Proportion of nakshatra traversed
    proportion_traversed = degree_in_nakshatra / NAKSHATRA_SPAN
    proportion_traversed = min(proportion_traversed, 1.0)

    elapsed_years = total_years * proportion_traversed
    remaining_years = total_years - elapsed_years

    return {
        "lord": lord,
        "lord_index": lord_index,
        "total_years": total_years,
        "elapsed_years": elapsed_years,
        "remaining_years": remaining_years,
    }


def calculate_ashtottari_sequence(
    birth_datetime: datetime,
    moon_nakshatra: int,
    degree_in_nakshatra: float,
    years: int = 108,
) -> list[dict]:
    """Generate the full sequence of Ashtottari dasha periods from birth.

    Args:
        birth_datetime: Birth datetime
        moon_nakshatra: Moon's nakshatra number (1-27)
        degree_in_nakshatra: Degrees traversed in nakshatra (0 to ~13.333)
        years: Total years to cover (default 108 = one full cycle)

    Returns:
        List of dicts with: lord, start_date, end_date, years, is_current

    Example:
        >>> from datetime import datetime
        >>> periods = calculate_ashtottari_sequence(
        ...     datetime(1992, 12, 3), 8, 6.0
        ... )
        >>> periods[0]['lord']
        'moon'
    """
    balance = calculate_ashtottari_balance(moon_nakshatra, degree_in_nakshatra)
    starting_index = balance["lord_index"]
    remaining_years = balance["remaining_years"]

    periods = []
    current_date = birth_datetime

    # First period (partial, based on balance at birth)
    lord_name = ASHTOTTARI_DATA[starting_index][0]
    days_in_period = remaining_years * 365.25
    end_date = current_date + timedelta(days=days_in_period)

    periods.append(
        {
            "lord": lord_name,
            "start_date": current_date,
            "end_date": end_date,
            "years": remaining_years,
            "is_current": False,
        }
    )
    current_date = end_date
    total_covered = remaining_years

    # Generate subsequent full periods
    while total_covered < years:
        next_index = (starting_index + len(periods)) % 8
        lord_name, lord_years = ASHTOTTARI_DATA[next_index]

        # Don't exceed total years
        actual_years = min(lord_years, years - total_covered)
        days_in_period = actual_years * 365.25
        end_date = current_date + timedelta(days=days_in_period)

        periods.append(
            {
                "lord": lord_name,
                "start_date": current_date,
                "end_date": end_date,
                "years": actual_years,
                "is_current": False,
            }
        )
        current_date = end_date
        total_covered += actual_years

    return periods


def get_current_ashtottari(
    birth_datetime: datetime,
    moon_nakshatra: int,
    degree_in_nakshatra: float,
    query_datetime: datetime | None = None,
) -> dict:
    """Get current Ashtottari Mahadasha and Antardasha at query time.

    Args:
        birth_datetime: Birth datetime
        moon_nakshatra: Moon's nakshatra number (1-27)
        degree_in_nakshatra: Degrees traversed in nakshatra (0 to ~13.333)
        query_datetime: Datetime to query (defaults to now)

    Returns:
        Dictionary with:
            - mahadasha: dict with lord, start_date, end_date, years
            - antardasha: dict with lord, start_date, end_date, years
            - remaining_days_maha: int
            - remaining_days_antar: int

    Example:
        >>> from datetime import datetime
        >>> result = get_current_ashtottari(
        ...     datetime(1992, 12, 3), 8, 6.0,
        ...     query_datetime=datetime(2025, 1, 1)
        ... )
        >>> result['mahadasha']['lord']
        'mercury'
    """
    if query_datetime is None:
        query_datetime = datetime.now()

    # Ensure timezone consistency: strip tzinfo for comparison
    query_naive = query_datetime.replace(tzinfo=None) if query_datetime.tzinfo else query_datetime

    # Generate enough periods (2 cycles = 216 years should be plenty)
    periods = calculate_ashtottari_sequence(
        birth_datetime, moon_nakshatra, degree_in_nakshatra, years=216
    )

    # Find current Mahadasha
    current_maha = None
    for period in periods:
        start = (
            period["start_date"].replace(tzinfo=None)
            if period["start_date"].tzinfo
            else period["start_date"]
        )
        end = (
            period["end_date"].replace(tzinfo=None)
            if period["end_date"].tzinfo
            else period["end_date"]
        )

        if start <= query_naive < end:
            current_maha = period
            break

    if current_maha is None:
        # Query is beyond all periods, return last
        current_maha = periods[-1]

    # Get antardasha breakdown
    antardashas = get_ashtottari_antardasha(
        current_maha["lord"], current_maha["start_date"], current_maha["end_date"]
    )

    # Find current antardasha
    current_antar = None
    for ad in antardashas:
        ad_start = (
            ad["start_date"].replace(tzinfo=None) if ad["start_date"].tzinfo else ad["start_date"]
        )
        ad_end = ad["end_date"].replace(tzinfo=None) if ad["end_date"].tzinfo else ad["end_date"]

        if ad_start <= query_naive < ad_end:
            current_antar = ad
            break

    if current_antar is None:
        current_antar = antardashas[-1]

    maha_end = (
        current_maha["end_date"].replace(tzinfo=None)
        if current_maha["end_date"].tzinfo
        else current_maha["end_date"]
    )
    antar_end = (
        current_antar["end_date"].replace(tzinfo=None)
        if current_antar["end_date"].tzinfo
        else current_antar["end_date"]
    )

    return {
        "mahadasha": current_maha,
        "antardasha": current_antar,
        "remaining_days_maha": max(0, (maha_end - query_naive).days),
        "remaining_days_antar": max(0, (antar_end - query_naive).days),
    }


def get_ashtottari_antardasha(
    mahadasha_lord: str,
    mahadasha_start: datetime,
    mahadasha_end: datetime,
) -> list[dict]:
    """Calculate Antardasha periods within a Mahadasha.

    The antardasha sequence starts from the Mahadasha lord itself and
    proceeds through the 8-planet sequence. Duration is proportional:
    antardasha_days = (antardasha_lord_years / TOTAL_CYCLE) * mahadasha_days

    Args:
        mahadasha_lord: Lord of the Mahadasha (e.g., "sun", "moon")
        mahadasha_start: Start datetime of the Mahadasha
        mahadasha_end: End datetime of the Mahadasha

    Returns:
        List of 8 dicts with: lord, start_date, end_date, years

    Raises:
        ValueError: If mahadasha_lord is not valid

    Example:
        >>> from datetime import datetime
        >>> ads = get_ashtottari_antardasha("sun",
        ...     datetime(2020, 1, 1), datetime(2026, 1, 1))
        >>> len(ads)
        8
        >>> ads[0]['lord']
        'sun'
    """
    starting_index = _get_lord_index(mahadasha_lord)
    maha_duration_days = (mahadasha_end - mahadasha_start).days

    antardashas = []
    current_date = mahadasha_start

    for i in range(8):
        lord_index = (starting_index + i) % 8
        lord_name, lord_years = ASHTOTTARI_DATA[lord_index]

        # Proportional duration
        antardasha_days = int((lord_years / TOTAL_CYCLE) * maha_duration_days)

        end_date = current_date + timedelta(days=antardasha_days)
        if end_date > mahadasha_end:
            end_date = mahadasha_end

        antardashas.append(
            {
                "lord": lord_name,
                "start_date": current_date,
                "end_date": end_date,
                "years": lord_years,
            }
        )

        current_date = end_date
        if current_date >= mahadasha_end:
            break

    return antardashas
