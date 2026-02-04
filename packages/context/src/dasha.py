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
    get_pratyantardasha_effects as get_pratyantardasha_effects_data,
)

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
    dasha_years = _get_dasha_years()
    dasha_sequence = _get_dasha_sequence()

    if antardasha_lord not in dasha_years:
        raise ValueError(f"Invalid antardasha lord: {antardasha_lord}")

    antar_years = dasha_years[antardasha_lord]

    # Start sequence from antardasha lord
    start_idx = dasha_sequence.index(antardasha_lord)

    periods = []
    current_date = antar_start

    # Generate all 9 pratyantardasha periods
    for i in range(9):
        lord_idx = (start_idx + i) % 9
        pratyantar_lord = dasha_sequence[lord_idx]
        pratyantar_years = dasha_years[pratyantar_lord]

        # Pratyantardasha duration formula: (Antar years * Pratyantar years) / 120
        duration_years = (antar_years * pratyantar_years) / 120
        duration_days = duration_years * 365.25

        end_date = current_date + timedelta(days=duration_days)

        periods.append(
            {
                "lord": pratyantar_lord,
                "start_date": current_date,
                "end_date": end_date,
                "years": duration_years,
            }
        )

        current_date = end_date

    return periods


def get_current_dasha(
    birth_datetime: datetime, moon_longitude: float, query_datetime: datetime | None = None
) -> dict[str, Any] | None:
    """Get current Mahadasha, Antardasha, and Pratyantardasha.

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
        query_datetime = datetime.now()

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
