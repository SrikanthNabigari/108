"""Vimshottari Dasha calculations module for 108 Vedic Astrology app.

This module implements the Vimshottari Dasha system, the most widely used
planetary period system in Vedic astrology. It calculates Mahadasha,
Antardasha, and Pratyantardasha periods based on Moon's position at birth.

The Vimshottari Dasha system consists of 9 planetary periods totaling 120 years:
- Ketu: 7 years
- Venus: 20 years
- Sun: 6 years
- Moon: 10 years
- Mars: 7 years
- Rahu: 18 years
- Jupiter: 16 years
- Saturn: 19 years
- Mercury: 17 years
"""

from datetime import datetime, timedelta
from typing import Any

from packages.core.src.knowledge_loader import (
    get_antardasha_effects as get_antardasha_effects_data,
)
from packages.core.src.knowledge_loader import (
    get_dasha_rules,
)
from packages.core.src.knowledge_loader import (
    get_deha_dasha_effects as get_deha_dasha_effects_data,
)
from packages.core.src.knowledge_loader import (
    get_prana_dasha_effects as get_prana_dasha_effects_data,
)
from packages.core.src.knowledge_loader import (
    get_pratyantardasha_effects as get_pratyantardasha_effects_data,
)
from packages.core.src.knowledge_loader import (
    get_sookshma_dasha_effects as get_sookshma_dasha_effects_data,
)


def _normalize_pair(birth_dt: datetime, query_dt: datetime) -> tuple[datetime, datetime]:
    """Return (birth, query) with consistent tz state for comparison.

    Why: callers may pass aware birth + naive query (or vice versa). Direct
    comparison raises TypeError. Per BPHS the dasha clock runs in the native's
    local civil time, so we align both to birth's frame: if birth is aware and
    query is naive, attach birth's tzinfo to query; if birth is naive and query
    is aware, convert query to birth's wall time then drop tz; if mixed-aware,
    convert query into birth's tz. Result: both aware OR both naive.
    """
    if birth_dt.tzinfo is None and query_dt.tzinfo is None:
        return birth_dt, query_dt
    if birth_dt.tzinfo is not None and query_dt.tzinfo is not None:
        return birth_dt, query_dt.astimezone(birth_dt.tzinfo)
    if birth_dt.tzinfo is not None and query_dt.tzinfo is None:
        return birth_dt, query_dt.replace(tzinfo=birth_dt.tzinfo)
    return birth_dt.replace(tzinfo=query_dt.tzinfo), query_dt


# Module-level cache for dasha rules
_dasha_rules_cache: dict[str, Any] | None = None


def _get_dasha_rules() -> dict[str, Any]:
    """Get cached dasha rules from JSON."""
    global _dasha_rules_cache
    if _dasha_rules_cache is None:
        _dasha_rules_cache = get_dasha_rules()
    return _dasha_rules_cache


def _get_dasha_years() -> dict[str, int]:
    """Get dasha years from JSON, with fallback to defaults."""
    rules = _get_dasha_rules()
    vimshottari = rules.get("vimshottari_system", {})
    periods = vimshottari.get("periods", [])

    if periods:
        return {p["planet"]: p["years"] for p in periods}

    # Fallback to defaults if JSON not available
    return {
        "ketu": 7,
        "venus": 20,
        "sun": 6,
        "moon": 10,
        "mars": 7,
        "rahu": 18,
        "jupiter": 16,
        "saturn": 19,
        "mercury": 17,
    }


def _get_dasha_sequence() -> list[str]:
    """Get dasha sequence from JSON, with fallback to defaults."""
    rules = _get_dasha_rules()
    vimshottari = rules.get("vimshottari_system", {})
    periods = vimshottari.get("periods", [])

    if periods:
        return [p["planet"] for p in sorted(periods, key=lambda x: x["order"])]

    # Fallback to defaults
    return ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]


def _get_nakshatra_lords() -> dict[int, str]:
    """Get nakshatra lords from JSON, with fallback to defaults."""
    rules = _get_dasha_rules()
    nakshatra_data = rules.get("nakshatra_lords", {})

    if nakshatra_data:
        return {int(k): v["lord"] for k, v in nakshatra_data.items()}

    # Fallback to defaults
    return {
        1: "ketu",  # Ashwini
        2: "venus",  # Bharani
        3: "sun",  # Krittika
        4: "moon",  # Rohini
        5: "mars",  # Mrigashira
        6: "rahu",  # Ardra
        7: "jupiter",  # Punarvasu
        8: "saturn",  # Pushya
        9: "mercury",  # Ashlesha
        10: "ketu",  # Magha
        11: "venus",  # Purva Phalguni
        12: "sun",  # Uttara Phalguni
        13: "moon",  # Hasta
        14: "mars",  # Chitra
        15: "rahu",  # Swati
        16: "jupiter",  # Vishakha
        17: "saturn",  # Anuradha
        18: "mercury",  # Jyeshtha
        19: "ketu",  # Mula
        20: "venus",  # Purva Ashadha
        21: "sun",  # Uttara Ashadha
        22: "moon",  # Shravana
        23: "mars",  # Dhanishtha
        24: "rahu",  # Shatabhisha
        25: "jupiter",  # Purva Bhadrapada
        26: "saturn",  # Uttara Bhadrapada
        27: "mercury",  # Revati
    }


# Each nakshatra spans 13°20' = 13.333...°
NAKSHATRA_SPAN = 13.333333333


# Backwards-compatible exports (use functions internally, but expose as constants)
# These are evaluated at module load time for backwards compatibility
DASHA_YEARS = _get_dasha_years()
DASHA_SEQUENCE = _get_dasha_sequence()
NAKSHATRA_LORDS = _get_nakshatra_lords()


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360 range.

    Args:
        longitude: Longitude in degrees (can be any value)

    Returns:
        Normalized longitude in 0-360 range
    """
    return longitude % 360


def _get_nakshatra_number(moon_longitude: float) -> int:
    """Get the nakshatra number (1-27) for given longitude.

    Args:
        moon_longitude: Moon's longitude in degrees (0-360)

    Returns:
        Nakshatra number (1-27)
    """
    normalized_lon = _normalize_longitude(moon_longitude)
    nakshatra_num = int(normalized_lon / NAKSHATRA_SPAN) + 1

    # Ensure it's in valid range
    if nakshatra_num > 27:
        nakshatra_num = 27

    return nakshatra_num


def get_dasha_balance_at_birth(moon_longitude: float, _birth_datetime: datetime) -> dict[str, Any]:
    """Calculate remaining dasha balance at birth.

    Determines which Mahadasha period the native is born into and how much
    of that dasha period remains. This is calculated based on the Moon's
    position in the zodiac at birth.

    Args:
        moon_longitude: Moon's longitude at birth in degrees (0-360)
        birth_datetime: Birth date and time

    Returns:
        Dictionary containing:
        - lord: The planet ruling the current Mahadasha
        - nakshatra_num: Moon's nakshatra number (1-27)
        - remaining_years: Remaining years in the Mahadasha
        - remaining_days: Remaining days in the Mahadasha
        - traversed_fraction: How much of the nakshatra has been traversed (0-1)

    Example:
        >>> import pytz
        >>> birth_dt = datetime(1992, 12, 3, 3, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
        >>> balance = get_dasha_balance_at_birth(324.0, birth_dt)
        >>> balance['lord']  # Should be 'jupiter' for Purva Bhadrapada
        'jupiter'
    """
    # Get nakshatra number (1-27)
    nakshatra_num = _get_nakshatra_number(moon_longitude)

    # Get nakshatra lord (current dasha lord at birth)
    nakshatra_lords = _get_nakshatra_lords()
    lord = nakshatra_lords[nakshatra_num]

    # Calculate how much of the nakshatra has been traversed
    normalized_lon = _normalize_longitude(moon_longitude)
    degree_in_nakshatra = normalized_lon % NAKSHATRA_SPAN
    traversed_fraction = degree_in_nakshatra / NAKSHATRA_SPAN

    # Calculate remaining dasha
    dasha_years = _get_dasha_years()
    dasha_period_years = dasha_years[lord]
    remaining_years = (1 - traversed_fraction) * dasha_period_years
    remaining_days = remaining_years * 365.25

    return {
        "lord": lord,
        "nakshatra_num": nakshatra_num,
        "remaining_years": remaining_years,
        "remaining_days": remaining_days,
        "traversed_fraction": traversed_fraction,
    }


def get_mahadasha_sequence(
    birth_datetime: datetime, moon_longitude: float, years: int = 120
) -> list[dict[str, Any]]:
    """Generate complete Mahadasha sequence from birth.

    Creates a list of all Mahadasha periods from birth, starting with the
    partial period determined by Moon's position at birth.

    Args:
        birth_datetime: Birth date and time
        moon_longitude: Moon's longitude at birth in degrees (0-360)
        years: Total span of years to generate (default 120 = full cycle)

    Returns:
        List of dictionaries, each containing:
        - lord: Planet ruling the Mahadasha
        - start_date: Start datetime of the period
        - end_date: End datetime of the period
        - years: Duration of the period in years

    Example:
        >>> import pytz
        >>> birth_dt = datetime(1992, 12, 3, 3, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
        >>> sequence = get_mahadasha_sequence(birth_dt, 324.0)
        >>> len(sequence)  # Should be around 9-10 periods
        10
        >>> sequence[0]['lord']
        'jupiter'
    """
    balance = get_dasha_balance_at_birth(moon_longitude, birth_datetime)

    periods = []
    current_date = birth_datetime

    # First period (partial - remaining balance from birth)
    first_lord = balance["lord"]
    first_end = current_date + timedelta(days=balance["remaining_days"])

    periods.append(
        {
            "lord": first_lord,
            "start_date": current_date,
            "end_date": first_end,
            "years": balance["remaining_years"],
        }
    )

    # Find next lord in sequence
    dasha_sequence = _get_dasha_sequence()
    dasha_years = _get_dasha_years()
    lord_idx = dasha_sequence.index(first_lord)
    current_date = first_end
    total_years = balance["remaining_years"]

    # Generate subsequent full periods
    while total_years < years:
        lord_idx = (lord_idx + 1) % 9
        lord = dasha_sequence[lord_idx]
        period_years = dasha_years[lord]

        # Don't exceed the total years limit
        if total_years + period_years > years:
            period_years = years - total_years

        end_date = current_date + timedelta(days=period_years * 365.25)

        periods.append(
            {
                "lord": lord,
                "start_date": current_date,
                "end_date": end_date,
                "years": period_years,
            }
        )

        current_date = end_date
        total_years += period_years

    return periods


def get_antardasha_sequence(
    mahadasha_lord: str, maha_start: datetime, _maha_end: datetime
) -> list[dict[str, Any]]:
    """Calculate Antardasha periods within a Mahadasha.

    The Antardasha sequence repeats the 9-planet cycle within the Mahadasha
    period. The duration of each Antardasha is proportional to both the
    Mahadasha period and the Antardasha planet's dasha period.

    Formula: Antardasha duration = (Maha_years * Antar_years) / 120 * 365.25 days

    Args:
        mahadasha_lord: Planet ruling the Mahadasha (must be valid planet)
        maha_start: Start datetime of the Mahadasha
        maha_end: End datetime of the Mahadasha

    Returns:
        List of dictionaries, each containing:
        - lord: Planet ruling the Antardasha
        - start_date: Start datetime of the period
        - end_date: End datetime of the period
        - years: Duration of the period in years

    Raises:
        ValueError: If mahadasha_lord is not a valid planet

    Example:
        >>> from datetime import datetime, timedelta
        >>> import pytz
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> start = datetime(2010, 1, 1, 0, 0, tzinfo=tz)
        >>> end = datetime(2026, 1, 1, 0, 0, tzinfo=tz)
        >>> antars = get_antardasha_sequence('mercury', start, end)
        >>> len(antars)
        9
    """
    dasha_years = _get_dasha_years()
    dasha_sequence = _get_dasha_sequence()

    if mahadasha_lord not in dasha_years:
        raise ValueError(f"Invalid mahadasha lord: {mahadasha_lord}")

    maha_years = dasha_years[mahadasha_lord]

    # Start sequence from mahadasha lord
    start_idx = dasha_sequence.index(mahadasha_lord)

    periods = []
    current_date = maha_start

    # Generate all 9 antardasha periods
    for i in range(9):
        lord_idx = (start_idx + i) % 9
        antar_lord = dasha_sequence[lord_idx]
        antar_years = dasha_years[antar_lord]

        # Antardasha duration formula: (Maha years * Antar years) / 120
        duration_years = (maha_years * antar_years) / 120
        duration_days = duration_years * 365.25

        end_date = current_date + timedelta(days=duration_days)

        periods.append(
            {
                "lord": antar_lord,
                "start_date": current_date,
                "end_date": end_date,
                "years": duration_years,
            }
        )

        current_date = end_date

    return periods


def _subdivide_dasha_period(
    parent_lord: str, parent_start: datetime, parent_end: datetime
) -> list[dict[str, Any]]:
    """Subdivide a dasha period into 9 sub-periods using Vimshottari proportions.

    This is the universal formula used at every level of the dasha hierarchy:
    Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma -> Prana -> Deha.
    Each sub-period's duration is proportional to its lord's standard years / 120.

    Args:
        parent_lord: Planet ruling the parent period (must be valid planet)
        parent_start: Start datetime of the parent period
        parent_end: End datetime of the parent period

    Returns:
        List of 9 dictionaries, each containing:
        - lord: Planet ruling the sub-period
        - start_date: Start datetime of the sub-period
        - end_date: End datetime of the sub-period
        - years: Duration of the sub-period in years

    Raises:
        ValueError: If parent_lord is not a valid planet
    """
    dasha_years = _get_dasha_years()
    dasha_sequence = _get_dasha_sequence()

    if parent_lord not in dasha_years:
        raise ValueError(f"Invalid dasha lord: {parent_lord}")

    # Use ACTUAL parent duration from dates, not standard planet years.
    actual_parent_days = (parent_end - parent_start).total_seconds() / 86400
    actual_parent_years = actual_parent_days / 365.25

    # Start sequence from parent lord
    start_idx = dasha_sequence.index(parent_lord)

    periods = []
    current_date = parent_start

    # Generate all 9 sub-periods
    for i in range(9):
        lord_idx = (start_idx + i) % 9
        sub_lord = dasha_sequence[lord_idx]
        sub_years = dasha_years[sub_lord]

        # Sub-period gets a proportional share of the actual parent duration
        # proportion = standard_years / 120 (sums to 1.0 across all 9 planets)
        duration_years = (actual_parent_years * sub_years) / 120
        duration_days = duration_years * 365.25

        end_date = current_date + timedelta(days=duration_days)

        periods.append(
            {
                "lord": sub_lord,
                "start_date": current_date,
                "end_date": end_date,
                "years": duration_years,
            }
        )

        current_date = end_date

    return periods


def get_pratyantardasha_sequence(
    antardasha_lord: str, antar_start: datetime, _antar_end: datetime
) -> list[dict[str, Any]]:
    """Calculate Pratyantardasha periods within an Antardasha.

    The Pratyantardasha sequence repeats the 9-planet cycle within the
    Antardasha period. Duration follows the same proportional formula.

    Formula: Pratyantar_duration = (Antar_years * Pratyantar_years) / 120 * 365.25 days

    Args:
        antardasha_lord: Planet ruling the Antardasha (must be valid planet)
        antar_start: Start datetime of the Antardasha
        antar_end: End datetime of the Antardasha

    Returns:
        List of dictionaries, each containing:
        - lord: Planet ruling the Pratyantardasha
        - start_date: Start datetime of the period
        - end_date: End datetime of the period
        - years: Duration of the period in years

    Raises:
        ValueError: If antardasha_lord is not a valid planet
    """
    return _subdivide_dasha_period(antardasha_lord, antar_start, _antar_end)


def get_sookshma_dasha_sequence(
    pratyantardasha_lord: str, pd_start: datetime, pd_end: datetime
) -> list[dict[str, Any]]:
    """Calculate Sookshma Dasha (level 4) periods within a Pratyantardasha.

    Sookshma means 'subtle' -- these are fine subdivisions of the Pratyantardasha
    period. Duration typically ranges from 5-25 days depending on the parent period.

    Args:
        pratyantardasha_lord: Planet ruling the Pratyantardasha
        pd_start: Start datetime of the Pratyantardasha
        pd_end: End datetime of the Pratyantardasha

    Returns:
        List of 9 dictionaries with lord, start_date, end_date, years.

    Raises:
        ValueError: If pratyantardasha_lord is not a valid planet
    """
    return _subdivide_dasha_period(pratyantardasha_lord, pd_start, pd_end)


def get_prana_dasha_sequence(
    sookshma_lord: str, sd_start: datetime, sd_end: datetime
) -> list[dict[str, Any]]:
    """Calculate Prana Dasha (level 5) periods within a Sookshma Dasha.

    Prana means 'life breath' -- these ultra-fine subdivisions typically last
    from a few hours to about 5 days.

    Args:
        sookshma_lord: Planet ruling the Sookshma Dasha
        sd_start: Start datetime of the Sookshma Dasha
        sd_end: End datetime of the Sookshma Dasha

    Returns:
        List of 9 dictionaries with lord, start_date, end_date, years.

    Raises:
        ValueError: If sookshma_lord is not a valid planet
    """
    return _subdivide_dasha_period(sookshma_lord, sd_start, sd_end)


def get_deha_dasha_sequence(
    prana_lord: str, prana_start: datetime, prana_end: datetime
) -> list[dict[str, Any]]:
    """Calculate Deha Dasha (level 6) periods within a Prana Dasha.

    Deha means 'body' -- these are the finest subdivisions in the Vimshottari
    system, typically lasting from about 20 minutes to 14 hours.

    Args:
        prana_lord: Planet ruling the Prana Dasha
        prana_start: Start datetime of the Prana Dasha
        prana_end: End datetime of the Prana Dasha

    Returns:
        List of 9 dictionaries with lord, start_date, end_date, years.

    Raises:
        ValueError: If prana_lord is not a valid planet
    """
    return _subdivide_dasha_period(prana_lord, prana_start, prana_end)


def get_current_dasha(
    birth_datetime: datetime, moon_longitude: float, query_datetime: datetime | None = None
) -> dict[str, Any] | None:
    """Get current Mahadasha, Antardasha, Pratyantardasha, and Sookshma Dasha.

    Determines which dasha periods a native is currently experiencing at
    a given moment. If no query datetime is provided, uses current time.

    Args:
        birth_datetime: Birth date and time
        moon_longitude: Moon's longitude at birth in degrees (0-360)
        query_datetime: Datetime to check (default: current time)

    Returns:
        Dictionary containing:
        - mahadasha: {lord, start_date, end_date, years, days_remaining}
        - antardasha: {lord, start_date, end_date, years, days_remaining}
        - pratyantardasha: {lord, start_date, end_date, years, days_remaining}
        - sookshma_dasha: {lord, start_date, end_date, years, days_remaining}
        - current_datetime: The query datetime used

        Returns None if query_datetime is outside the 120-year cycle from birth

    Example:
        >>> import pytz
        >>> from datetime import datetime
        >>> birth_dt = datetime(1992, 12, 3, 3, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
        >>> query_dt = datetime(2025, 2, 4, tzinfo=pytz.timezone('Asia/Kolkata'))
        >>> dasha = get_current_dasha(birth_dt, 324.0, query_dt)
        >>> dasha['mahadasha']['lord']
        'mercury'
        >>> dasha['antardasha']['lord']
        'ketu'
    """
    if query_datetime is None:
        query_datetime = (
            datetime.now(tz=birth_datetime.tzinfo) if birth_datetime.tzinfo else datetime.now()
        )

    birth_datetime, query_datetime = _normalize_pair(birth_datetime, query_datetime)

    # Get all Mahadashas
    mahadashas = get_mahadasha_sequence(birth_datetime, moon_longitude)

    # Find current Mahadasha
    current_maha = None
    for maha in mahadashas:
        if maha["start_date"] <= query_datetime < maha["end_date"]:
            current_maha = maha
            break

    if not current_maha:
        return None

    # Get Antardashas for current Mahadasha
    antardashas = get_antardasha_sequence(
        current_maha["lord"], current_maha["start_date"], current_maha["end_date"]
    )

    # Find current Antardasha
    current_antar = None
    for antar in antardashas:
        if antar["start_date"] <= query_datetime < antar["end_date"]:
            current_antar = antar
            break

    if not current_antar:
        return None

    # Get Pratyantardashas for current Antardasha
    pratyantardashas = get_pratyantardasha_sequence(
        current_antar["lord"], current_antar["start_date"], current_antar["end_date"]
    )

    # Find current Pratyantardasha
    current_pratyantar = None
    for pratyantar in pratyantardashas:
        if pratyantar["start_date"] <= query_datetime < pratyantar["end_date"]:
            current_pratyantar = pratyantar
            break

    # Calculate remaining time
    days_remaining_maha = (current_maha["end_date"] - query_datetime).total_seconds() / 86400
    days_remaining_antar = (current_antar["end_date"] - query_datetime).total_seconds() / 86400

    pratyantar_data = None
    if current_pratyantar:
        days_remaining_pratyantar = (
            current_pratyantar["end_date"] - query_datetime
        ).total_seconds() / 86400

        pratyantar_data = {
            "lord": current_pratyantar["lord"],
            "start_date": current_pratyantar["start_date"],
            "end_date": current_pratyantar["end_date"],
            "years": current_pratyantar["years"],
            "days_remaining": days_remaining_pratyantar,
        }

    # Get Sookshma Dashas for current Pratyantardasha
    sookshma_data = None
    if current_pratyantar:
        sookshmas = get_sookshma_dasha_sequence(
            current_pratyantar["lord"],
            current_pratyantar["start_date"],
            current_pratyantar["end_date"],
        )
        for sd in sookshmas:
            if sd["start_date"] <= query_datetime < sd["end_date"]:
                days_remaining_sookshma = (sd["end_date"] - query_datetime).total_seconds() / 86400
                sookshma_data = {
                    "lord": sd["lord"],
                    "start_date": sd["start_date"],
                    "end_date": sd["end_date"],
                    "years": sd["years"],
                    "days_remaining": days_remaining_sookshma,
                }
                break

    # Get Prana Dashas for current Sookshma Dasha
    prana_data = None
    if sookshma_data:
        pranas = get_prana_dasha_sequence(
            sookshma_data["lord"],
            sookshma_data["start_date"],
            sookshma_data["end_date"],
        )
        for pr in pranas:
            if pr["start_date"] <= query_datetime < pr["end_date"]:
                days_remaining_prana = (pr["end_date"] - query_datetime).total_seconds() / 86400
                prana_data = {
                    "lord": pr["lord"],
                    "start_date": pr["start_date"],
                    "end_date": pr["end_date"],
                    "years": pr["years"],
                    "days_remaining": days_remaining_prana,
                }
                break

    # Get Deha Dashas for current Prana Dasha
    deha_data = None
    if prana_data:
        dehas = get_deha_dasha_sequence(
            prana_data["lord"],
            prana_data["start_date"],
            prana_data["end_date"],
        )
        for dh in dehas:
            if dh["start_date"] <= query_datetime < dh["end_date"]:
                hours_remaining = (dh["end_date"] - query_datetime).total_seconds() / 3600
                deha_data = {
                    "lord": dh["lord"],
                    "start_date": dh["start_date"],
                    "end_date": dh["end_date"],
                    "years": dh["years"],
                    "hours_remaining": round(hours_remaining, 1),
                }
                break

    return {
        "mahadasha": {
            "lord": current_maha["lord"],
            "start_date": current_maha["start_date"],
            "end_date": current_maha["end_date"],
            "years": current_maha["years"],
            "days_remaining": days_remaining_maha,
        },
        "antardasha": {
            "lord": current_antar["lord"],
            "start_date": current_antar["start_date"],
            "end_date": current_antar["end_date"],
            "years": current_antar["years"],
            "days_remaining": days_remaining_antar,
        },
        "pratyantardasha": pratyantar_data,
        "sookshma_dasha": sookshma_data,
        "prana_dasha": prana_data,
        "deha_dasha": deha_data,
        "current_datetime": query_datetime,
    }


def get_dasha_periods_for_year(
    birth_datetime: datetime, moon_longitude: float, year: int
) -> dict[str, list[dict[str, Any]]]:
    """Get all dasha periods active in a given year.

    Useful for annual horoscope (Varshaphal) analysis.

    Args:
        birth_datetime: Birth date and time
        moon_longitude: Moon's longitude at birth in degrees (0-360)
        year: Year to analyze

    Returns:
        Dictionary with:
        - mahadashas: List of Mahadashas active in the year
        - antardashas: List of Antardashas active in the year (flattened)
    """
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year, 12, 31, 23, 59, 59)

    # Get all mahadashas
    all_mahadashas = get_mahadasha_sequence(birth_datetime, moon_longitude)

    # Filter mahadashas active in this year
    active_mahadashas = [
        m
        for m in all_mahadashas
        if m["start_date"] <= end_of_year and m["end_date"] > start_of_year
    ]

    # Get all antardashas for active mahadashas
    active_antardashas = []
    for maha in active_mahadashas:
        antars = get_antardasha_sequence(maha["lord"], maha["start_date"], maha["end_date"])

        # Filter antardashas active in this year
        for antar in antars:
            if antar["start_date"] <= end_of_year and antar["end_date"] > start_of_year:
                # Include mahadasha lord context
                antar_with_context = antar.copy()
                antar_with_context["mahadasha_lord"] = maha["lord"]
                active_antardashas.append(antar_with_context)

    return {
        "year": year,
        "mahadashas": active_mahadashas,
        "antardashas": active_antardashas,
    }


def validate_dasha_data(birth_datetime: datetime, moon_longitude: float) -> dict[str, Any]:
    """Validate and summarize dasha calculations.

    Useful for debugging and verification of dasha calculations.

    Args:
        birth_datetime: Birth date and time
        moon_longitude: Moon's longitude at birth in degrees (0-360)

    Returns:
        Dictionary containing validation info:
        - is_valid: Whether data is valid
        - balance: Dasha balance at birth
        - first_period: First complete Mahadasha
        - total_span: Total years covered by 120-year cycle
        - message: Status message
    """
    try:
        balance = get_dasha_balance_at_birth(moon_longitude, birth_datetime)
        sequence = get_mahadasha_sequence(birth_datetime, moon_longitude)

        total_years = sum(p["years"] for p in sequence)

        return {
            "is_valid": True,
            "balance": balance,
            "first_period": sequence[0] if sequence else None,
            "total_periods": len(sequence),
            "total_span_years": total_years,
            "message": (
                f"Valid dasha calculation. {len(sequence)} periods "
                f"spanning {total_years:.1f} years."
            ),
        }
    except Exception as e:
        return {
            "is_valid": False,
            "balance": None,
            "first_period": None,
            "total_periods": 0,
            "total_span_years": 0,
            "message": f"Error in dasha calculation: {e}",
        }


# =============================================================================
# Dasha Effects Retrieval Functions
# =============================================================================


def get_antardasha_effect(mahadasha_lord: str, antardasha_lord: str) -> dict[str, Any] | None:
    """Get detailed effects for a specific Antardasha combination.

    Retrieves interpretation and effects for one of 81 possible MD-AD combinations.

    Args:
        mahadasha_lord: Mahadasha planet (sun, moon, mars, mercury, jupiter,
                       venus, saturn, rahu, ketu)
        antardasha_lord: Antardasha planet

    Returns:
        Dictionary with effects including:
        - general_effects: List of general themes
        - positive: Positive outcomes
        - negative: Challenges to watch
        - health: Health-related effects
        - career: Career/profession effects
        - relationships: Relationship dynamics
        - finances: Financial indications
        - spiritual: Spiritual growth aspects

        Returns None if combination not found.

    Example:
        >>> effects = get_antardasha_effect("jupiter", "venus")
        >>> print(effects["general_effects"])
        ['Expansion of pleasures and comforts', ...]
    """
    effects_data = get_antardasha_effects_data()
    md_effects = effects_data.get(mahadasha_lord.lower(), {})
    return md_effects.get(antardasha_lord.lower())


def get_pratyantardasha_effect(
    mahadasha_lord: str, antardasha_lord: str, pratyantardasha_lord: str
) -> dict[str, Any] | None:
    """Get detailed effects for a specific Pratyantardasha combination.

    Retrieves interpretation for one of 729 possible MD-AD-PD combinations
    (9 x 9 x 9 = 729).

    Args:
        mahadasha_lord: Mahadasha planet
        antardasha_lord: Antardasha planet
        pratyantardasha_lord: Pratyantardasha planet

    Returns:
        Dictionary with effects including:
        - theme: Overall theme of this period
        - duration_description: Human-readable duration
        - effects: General effects
        - health: Health indications
        - career: Professional matters
        - relationships: Relationship dynamics
        - finances: Financial outlook
        - timing: Auspicious timing within period
        - recommendations: Suggested actions

        Returns None if combination not found.

    Example:
        >>> effects = get_pratyantardasha_effect("jupiter", "venus", "saturn")
        >>> print(effects["theme"])
        'Balancing expansion with discipline'
    """
    effects_data = get_pratyantardasha_effects_data()
    md_effects = effects_data.get(mahadasha_lord.lower(), {})
    ad_effects = md_effects.get(antardasha_lord.lower(), {})
    return ad_effects.get(pratyantardasha_lord.lower())


def get_sookshma_dasha_effect(
    pratyantardasha_lord: str, sookshma_lord: str
) -> dict[str, Any] | None:
    """Get effects for a specific Sookshma Dasha combination.

    Retrieves interpretation for one of 81 possible PD-SD combinations (9x9).

    Args:
        pratyantardasha_lord: PD planet (parent period)
        sookshma_lord: SD planet (current micro-period)

    Returns:
        Dictionary with effects including theme, effects, health, career,
        relationships, timing_quality. None if not found.
    """
    effects_data = get_sookshma_dasha_effects_data()
    pd_effects = effects_data.get(pratyantardasha_lord.lower(), {})
    return pd_effects.get(sookshma_lord.lower())


def get_prana_dasha_effect(sookshma_lord: str, prana_lord: str) -> dict[str, Any] | None:
    """Get effects for a specific Prana Dasha combination.

    Retrieves interpretation for one of 81 possible SD-Prana combinations (9x9).

    Args:
        sookshma_lord: SD planet (parent period)
        prana_lord: Prana planet (current life-breath period)

    Returns:
        Dictionary with effects including theme, effects, health, career,
        relationships, timing_quality. None if not found.
    """
    effects_data = get_prana_dasha_effects_data()
    sd_effects = effects_data.get(sookshma_lord.lower(), {})
    return sd_effects.get(prana_lord.lower())


def get_deha_dasha_effect(prana_lord: str, deha_lord: str) -> dict[str, Any] | None:
    """Get effects for a specific Deha Dasha combination.

    Retrieves interpretation for one of 81 possible Prana-Deha combinations (9x9).

    Args:
        prana_lord: Prana planet (parent period)
        deha_lord: Deha planet (current body-level period)

    Returns:
        Dictionary with effects including theme, effects, health, career,
        relationships, timing_quality. None if not found.
    """
    effects_data = get_deha_dasha_effects_data()
    prana_effects = effects_data.get(prana_lord.lower(), {})
    return prana_effects.get(deha_lord.lower())
